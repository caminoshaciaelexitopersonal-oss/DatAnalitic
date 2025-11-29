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

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # safe backend for servers without display
import matplotlib.pyplot as plt
import seaborn as sns

from backend.wpa.powerbi.services.cache_service import CacheService
from backend.wpa.powerbi.schemas.powerbi_dashboard import DashboardConfig, WidgetConfig
from backend.wpa.powerbi.services.data_service import DataService

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))

CACHE = CacheService()
DATA_SERVICE = DataService()

DASHBOARD_FOLDER = Path(os.environ.get("SADI_POWERBI_DASHBOARDS", "backend/wpa/powerbi/dashboards"))


class VisualizationService:
    def __init__(self):
        self._dash_cache = {}
        self._dash_folder = DASHBOARD_FOLDER

    # ---------------------------
    # Dashboard load / list
    # ---------------------------
    def get_available_dashboards(self) -> List[str]:
        """List dashboard filenames (without extension) in dashboards folder."""
        files = []
        if not self._dash_folder.exists():
            return files
        for p in sorted(self._dash_folder.iterdir()):
            if p.suffix.lower() in (".json", ".yaml", ".yml"):
                files.append(p.stem)
        return files

    def load_dashboard(self, dashboard_id: str) -> Optional[DashboardConfig]:
        """
        Load dashboard configuration from disk (JSON or YAML).
        Returns DashboardConfig dataclass/dict or None if not found.
        """
        # cache hit
        if dashboard_id in self._dash_cache:
            return self._dash_cache[dashboard_id]

        # try json then yaml
        jpath = self._dash_folder / f"{dashboard_id}.json"
        ypath = self._dash_folder / f"{dashboard_id}.yaml"
        if jpath.exists():
            try:
                with open(jpath, "r", encoding="utf8") as fh:
                    cfg = json.load(fh)
                self._dash_cache[dashboard_id] = cfg
                return cfg
            except Exception as e:
                logger.exception("Failed loading dashboard JSON %s: %s", jpath, e)
                return None
        if ypath.exists():
            try:
                import yaml
                with open(ypath, "r", encoding="utf8") as fh:
                    cfg = yaml.safe_load(fh)
                self._dash_cache[dashboard_id] = cfg
                return cfg
            except Exception as e:
                logger.exception("Failed loading dashboard YAML %s: %s", ypath, e)
                return None
        return None

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

            # fallback: return sample rows
            return {"data": df_proc.head(500).to_dict(orient="records"), "meta": {"type": "sample"}}

        except Exception as e:
            logger.exception("process_widget failed: %s", e)
            raise

    # ---------------------------
    # server-side image generation (small preview)
    # ---------------------------
    def render_widget_preview_png(self, widget: Dict[str, Any], df: pd.DataFrame, out_path: Optional[str] = None) -> str:
        """
        Render a small PNG preview for a widget. Returns path to PNG.
        If out_path not provided, create tmp file in /tmp.
        NOTE: keep previews small to avoid memory pressure.
        """
        try:
            wtype = widget.get("type", "table")
            if out_path is None:
                out_path = f"/tmp/pbi_preview_{widget.get('id','widget')}.png"

            plt.figure(figsize=(6, 4))
            sns.set_style("whitegrid")

            if wtype in ("bar", "column"):
                x = widget.get("xField") or df.columns[0]
                series = widget.get("series") or [c for c in df.select_dtypes(include=["number"]).columns if c != x][:1]
                # simple bar of first series
                agg = df.groupby(x)[series[0]].sum().reset_index()
                sns.barplot(data=agg, x=x, y=series[0])
            elif wtype == "line":
                x = widget.get("xField") or df.columns[0]
                series = widget.get("series") or [c for c in df.select_dtypes(include=["number"]).columns if c != x][:1]
                df_sorted = df.sort_values(by=x)
                plt.plot(df_sorted[x], df_sorted[series[0]])
            elif wtype in ("pie", "donut"):
                x = widget.get("xField") or df.columns[0]
                agg = df.groupby(x).size().reset_index(name="count").sort_values("count", ascending=False).head(10)
                plt.pie(agg["count"], labels=agg[x], autopct="%1.1f%%")
            elif wtype == "scatter":
                x = widget.get("xField") or df.columns[0]
                y = widget.get("yField") or df.select_dtypes(include=["number"]).columns[0]
                plt.scatter(df[x], df[y], s=10, alpha=0.6)
            else:
                # fallback table preview
                table = df.head(10)
                plt.axis("off")
                plt.table(cellText=table.values, colLabels=table.columns, loc="center")

            plt.tight_layout()
            plt.savefig(out_path, dpi=150)
            plt.close()
            return out_path
        except Exception as e:
            logger.exception("render_widget_preview_png failed: %s", e)
            raise

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

    def process_widget_from_config(self, dashboard_id: str, widget_id: str, filters: Optional[str] = None) -> Dict[str, Any]:
        """
        Convenience: load dashboard, get widget config, fetch data via DataService and process.
        """
        dashboard = self.load_dashboard(dashboard_id)
        if not dashboard:
            raise FileNotFoundError(f"Dashboard {dashboard_id} not found")
        widget = next((w for w in dashboard.get("layout", {}).get("widgets", []) if w.get("id") == widget_id), None)
        if widget is None:
            raise FileNotFoundError(f"Widget {widget_id} not found in {dashboard_id}")
        # fetch data using DataService - delegate to DataService.execute_widget_query
        df = DATA_SERVICE.execute_widget_query(widget, filters=filters)
        return self.process_widget(widget, df)
