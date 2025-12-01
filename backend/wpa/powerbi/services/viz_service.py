"""
viz_service.py

Visualization service used by powerbi_router:
- loads dashboard definitions (JSON/YAML) from dashboards/
- processes widget configs and returns processed data for the frontend
- can render server-side small preview PNGs for heavy widgets (optional)
- provides helper methods for the router and tests

Dependencies:
  pandas, matplotlib, seaborn, plotly (optional)
  For server-side rendering of images: matplotlib + agg backend or plotly + orca/weasyprint (env dependent)

Design notes:
  - This service should NOT assume the presence of a DB; it works with DataService to fetch DataFrames.
  - For heavy visualizations or export to PDF, generate images in /tmp or /data/processed/<job_id>/visuals/
"""

import os
import io
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # safe backend for servers without display
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF  # fpdf2 library is installed as fpdf2, but imported as fpdf

from backend.wpa.powerbi.services.cache_service import CacheService
from sqlalchemy.orm import Session
from backend.wpa.powerbi.models import Dashboard, Widget
from backend.wpa.powerbi.schemas.powerbi_dashboard import DashboardConfig, WidgetConfig
from backend.wpa.powerbi.services.data_service import DataService

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))

CACHE = CacheService()
DATA_SERVICE = DataService()

class VisualizationService:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------
    # Dashboard CRUD
    # ---------------------------
    def get_dashboards(self) -> List[Dict[str, Any]]:
        dashboards = self.db.query(Dashboard).all()
        return [{"id": d.id, "name": d.name, "description": d.description} for d in dashboards]

    def get_dashboard_details(self, dashboard_id: int) -> Optional[Dict[str, Any]]:
        dashboard = self.db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
        if not dashboard:
            return None

        widgets_data = []
        for w in dashboard.widgets:
            widgets_data.append({
                "id": w.id,
                "title": w.title,
                "type": w.type,
                **w.config,  # Unpack config JSON
                **w.layout   # Unpack layout JSON
            })

        return {
            "id": dashboard.id,
            "name": dashboard.name,
            "layout": {"widgets": widgets_data}
        }

    def create_dashboard(self, name: str, description: str) -> Dashboard:
        db_dashboard = Dashboard(name=name, description=description)
        self.db.add(db_dashboard)
        self.db.commit()
        self.db.refresh(db_dashboard)
        return db_dashboard

    def add_widget(self, dashboard_id: int, title: str, type: str, config: Dict, layout: Dict) -> Widget:
        db_widget = Widget(
            dashboard_id=dashboard_id,
            title=title,
            type=type,
            config=config,
            layout=layout
        )
        self.db.add(db_widget)
        self.db.commit()
        self.db.refresh(db_widget)
        return db_widget

    def delete_widget(self, widget_id: int):
        db_widget = self.db.query(Widget).filter(Widget.id == widget_id).first()
        if db_widget:
            self.db.delete(db_widget)
            self.db.commit()

    # ---------------------------
    # Widget processing pipeline
    # ---------------------------
    def process_widget(self, widget: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """
        Given a widget config and a DataFrame, produce processed data ready for frontend.
        Returns a dict with keys: {data: [rows], meta: {...}, preview_image: optional base64}
        """
        try:
            wtype = widget.get("type", "table")
            # apply basic filters if in widget
            filters = widget.get("filters")
            if filters:
                df = self._apply_filters(df, filters)

            # perform aggregation if requested
            if widget.get("group_by") and widget.get("agg"):
                df = df.groupby(widget["group_by"]).agg(widget["agg"]).reset_index()

            # limit rows for performance
            max_rows = int(widget.get("max_rows", 2000))
            if len(df) > max_rows:
                df_proc = df.head(max_rows)
            else:
                df_proc = df

            # For certain chart types, compute aggregated series
            if wtype in ("kpi", "single_value"):
                value_field = widget.get("yField") or widget.get("value") or df_proc.columns[0]
                val = df_proc[value_field].sum() if widget.get("agg_func", "sum") == "sum" else df_proc[value_field].mean()
                return {"data": [{"value": float(val)}], "meta": {"type": wtype, "value_field": value_field}}

            if wtype in ("bar", "line", "area", "pie", "donut", "radar"):
                # expect dataframe with xField and one or more series
                x = widget.get("xField")
                series = widget.get("series")
                if not x and wtype != "pie":
                    # try to infer
                    x = df_proc.columns[0]
                if not series and wtype != "pie":
                    # infer numeric columns as series
                    series = df_proc.select_dtypes(include=["number"]).columns.tolist()
                    # remove x if in series
                    series = [s for s in series if s != x]
                # convert to records suitable for recharts
                records = df_proc[[x] + series].to_dict(orient="records")
                return {"data": records, "meta": {"type": wtype, "xField": x, "series": series}}

            if wtype == "table":
                # return first N rows as records
                records = df_proc.to_dict(orient="records")
                return {"data": records, "meta": {"cols": list(df_proc.columns)}}

            if wtype == "scatter":
                x = widget.get("xField") or df_proc.columns[0]
                y = widget.get("yField") or (df_proc.select_dtypes(include=["number"]).columns[0] if len(df_proc.select_dtypes(include=["number"]).columns)>0 else None)
                records = df_proc[[x, y]].dropna().to_dict(orient="records")
                return {"data": records, "meta": {"type": "scatter", "x": x, "y": y}}

            if wtype == "histogram":
                x = widget.get("xField") or df_proc.select_dtypes(include=["number"]).columns[0]
                bins = widget.get("bins", 20)
                counts, bin_edges = np.histogram(df_proc[x].dropna(), bins=bins)
                records = [{"name": f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}", "value": int(counts[i])} for i in range(len(counts))]
                return {"data": records, "meta": {"type": "histogram", "xField": "name", "series": ["value"]}}

            if wtype == "boxplot":
                series = widget.get("series") or df_proc.select_dtypes(include=["number"]).columns.tolist()
                summary = df_proc[series].describe().to_dict()
                records = [{"name": col, "q1": data["25%"], "q3": data["75%"], "median": data["50%"], "min": data["min"], "max": data["max"]} for col, data in summary.items()]
                return {"data": records, "meta": {"type": "boxplot"}}

            if wtype == "heatmap":
                x = widget.get("xField")
                y = widget.get("yField")
                z = widget.get("zField")
                if not all([x, y, z]):
                    raise ValueError("Heatmap requires xField, yField, and zField")
                pivot_df = df_proc.pivot_table(index=y, columns=x, values=z, aggfunc='mean').fillna(0)
                records = []
                for yi in pivot_df.index:
                    for xi in pivot_df.columns:
                        records.append({"x": xi, "y": yi, "value": pivot_df.loc[yi, xi]})
                return {"data": records, "meta": {"type": "heatmap", "x": pivot_df.columns.tolist(), "y": pivot_df.index.tolist()}}

            # fallback: return sample rows
            return {"data": df_proc.head(500).to_dict(orient="records"), "meta": {"type": "sample"}}

        except Exception as e:
            logger.exception("process_widget failed: %s", e)
            raise

    # ---------------------------
    # Exporting
    # ---------------------------
    def export_widget(self, widget: Dict[str, Any], df: pd.DataFrame, format: str, out_path: Optional[str] = None) -> str:
        """
        Export a widget's data or visualization to a specified format.
        Returns the path to the generated file.
        """
        if out_path is None:
            out_path = f"/tmp/{widget.get('id', 'export')}.{format}"

        if format == "csv":
            df.to_csv(out_path, index=False)
            return out_path
        elif format == "json":
            df.to_json(out_path, orient="records", indent=2)
            return out_path
        elif format in ("png", "svg", "pdf"):
            # Use the matplotlib renderer
            self._render_matplotlib_chart(widget, df, out_path, format=format)
            return out_path
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _render_matplotlib_chart(self, widget: Dict[str, Any], df: pd.DataFrame, out_path: str, format: str = "png"):
        """
        Internal method to render a matplotlib chart and save it.
        Can save as png, svg, or pdf.
        """
        wtype = widget.get("type", "table")

        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")
        plt.title(widget.get("title", "Chart"))

        if wtype in ("bar", "column", "histogram"):
            x = widget.get("xField") or df.columns[0]
            series = widget.get("series") or [c for c in df.select_dtypes(include=["number"]).columns if c != x]
            df.plot(kind='bar', x=x, y=series, ax=plt.gca())
        elif wtype == "line":
            x = widget.get("xField") or df.columns[0]
            series = widget.get("series") or [c for c in df.select_dtypes(include=["number"]).columns if c != x]
            df.sort_values(by=x).plot(kind='line', x=x, y=series, ax=plt.gca())
        elif wtype in ("pie", "donut"):
            x = widget.get("xField") or df.columns[0]
            y = widget.get("series")[0] if widget.get("series") else df.select_dtypes(include=["number"]).columns[0]
            df.set_index(x)[y].plot(kind='pie', autopct='%1.1f%%', ax=plt.gca())
        elif wtype == "scatter":
            x = widget.get("xField") or df.columns[0]
            y = widget.get("yField") or df.select_dtypes(include=["number"]).columns[0]
            sns.scatterplot(data=df, x=x, y=y, ax=plt.gca())
        else: # Fallback for table or unknown
            table_df = df.head(20)
            plt.axis('off')
            plt.table(cellText=table_df.values, colLabels=table_df.columns, loc='center', cellLoc='left')

        plt.tight_layout()

        if format == 'pdf':
            img_path = out_path.replace('.pdf', '.png')
            plt.savefig(img_path, dpi=300)
            pdf = FPDF()
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=190)
            pdf.output(out_path)
            os.remove(img_path)
        else:
            plt.savefig(out_path, format=format, dpi=300)

        plt.close()

    # ---------------------------
    # helpers
    # ---------------------------
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply simple equality filters. Filters can be a dict of column->value or nested.
        """
        df2 = df
        try:
            for k, v in (filters or {}).items():
                if k in df2.columns:
                    if isinstance(v, list):
                        df2 = df2[df2[k].isin(v)]
                    else:
                        df2 = df2[df2[k] == v]
        except Exception:
            logger.exception("Failed to apply filters %s", filters)
        return df2

    def process_widget_from_db(self, widget_id: int, filters: Optional[str] = None) -> Dict[str, Any]:
        """
        Load widget config from DB, fetch data, and process for visualization.
        """
        widget_model = self.db.query(Widget).filter(Widget.id == widget_id).first()
        if not widget_model:
            raise FileNotFoundError(f"Widget {widget_id} not found in DB")

        # The widget config is now a combination of multiple fields in the model
        widget_config = {
            "id": widget_model.id,
            "title": widget_model.title,
            "type": widget_model.type,
            **widget_model.config,
            **widget_model.layout
        }

        df = DATA_SERVICE.execute_widget_query(widget_config, filters=filters)
        return self.process_widget(widget_config, df)
