from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.wpa.powerbi.services.data_service import DataService
from backend.wpa.powerbi.services.viz_service import VisualizationService
from backend.wpa.powerbi.services.model_service import ModelService
from backend.wpa.powerbi.services.cache_service import CacheService
from backend.wpa.powerbi.schemas.dashboard_config import DashboardConfig, WidgetConfig
from backend.wpa.powerbi.schemas.powerbi_request import DataQueryRequest

router = APIRouter(prefix="/powerbi", tags=["PowerBI-Style"])

data_service = DataService()
viz_service = VisualizationService()
model_service = ModelService()
cache_service = CacheService()


# ---------------------------
# 1. LISTAR DASHBOARDS
# ---------------------------
@router.get("/dashboards", response_model=List[str])
async def list_dashboards():
    """List all available dashboard IDs."""
    dashboards = viz_service.get_available_dashboards()
    return dashboards


# ---------------------------
# 2. OBTENER DASHBOARD COMPLETO
# ---------------------------
@router.get("/dashboard/{dashboard_id}", response_model=DashboardConfig)
async def get_dashboard(dashboard_id: str):
    """
    Returns full dashboard: layout, widgets, filters, metadata.
    """
    dashboard = viz_service.load_dashboard(dashboard_id)

    if dashboard is None:
        raise HTTPException(status_code=404, detail=f"Dashboard '{dashboard_id}' not found")

    return dashboard


# ---------------------------
# 3. EJECUTAR QUERY GENERAL
# ---------------------------
@router.post("/data/query")
async def query_data(req: DataQueryRequest):
    """
    Executes a dataset query (SQL-like, pandas-like, or connector).
    Automatically handles:
      - DBs
      - CSV/Excel/Parquet
      - Google Drive / OneDrive
      - DataLake
      - AutoML enriched data
    """
    try:
        cache_key = f"query:{req.model_dump()}"
        cached = cache_service.get(cache_key)
        if cached:
            return cached

        df = data_service.execute_query(req)
        data = df.to_dict(orient="records")

        cache_service.set(cache_key, data)
        return data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------
# 4. OBTENER DATOS DE UN WIDGET
# ---------------------------
@router.get("/data/widget/{dashboard_id}/{widget_id}")
async def get_widget_data(
    dashboard_id: str,
    widget_id: str,
    filter_values: Optional[str] = Query(default=None, description="JSON string of filters"),
):
    """
    Returns processed widget data (aggregations, group-bys, filters applied).
    """
    dashboard = viz_service.load_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail=f"Dashboard '{dashboard_id}' not found")

    widget = next((w for w in dashboard.layout.widgets if w.id == widget_id), None)

    if widget is None:
        raise HTTPException(status_code=404, detail=f"Widget '{widget_id}' not found")

    try:
        cache_key = f"widget:{dashboard_id}:{widget_id}:{filter_values}"
        cached = cache_service.get(cache_key)
        if cached:
            return cached

        df = data_service.execute_widget_query(widget, filters=filter_values)

        processed = viz_service.process_widget(widget, df)

        cache_service.set(cache_key, processed)
        return processed

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------
# 5. AUTO-RECOMENDACIONES (AI)
# ---------------------------
class RecommendationRequest(BaseModel):
    dataset_name: str
    sample_limit: Optional[int] = 5000


@router.post("/model/recommend")
async def recommend_dashboard(req: RecommendationRequest):
    """
    AutoML suggestions:
      - Best KPIs
      - Best chart types
      - Best variables to analyze
      - Insights (correlations, trends)
      - Feature importance
      - Clusters / segments
    """
    try:
        recommendations = model_service.recommend_dashboard(
            dataset_name=req.dataset_name,
            sample_limit=req.sample_limit,
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------
# 6. REFRESCAR CACHE
# ---------------------------
@router.delete("/cache/clear")
async def clear_cache():
    """
    Deletes all internal cache for dashboards, widgets and datasets.
    """
    cache_service.clear()
    return {"status": "cache cleared"}


# ---------------------------
# 7. HEALTHCHECK / STATUS
# ---------------------------
@router.get("/status")
async def powerbi_status():
    return {
        "status": "OK",
        "dashboards": viz_service.get_available_dashboards(),
        "connectors": data_service.get_available_connectors(),
        "ai_ready": model_service.is_ready()
    }
