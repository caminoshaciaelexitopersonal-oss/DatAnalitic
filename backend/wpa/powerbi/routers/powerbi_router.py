from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from starlette.responses import FileResponse
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db
from backend.wpa.powerbi.models import Widget
from backend.wpa.powerbi.services.data_service import DataService
from backend.wpa.powerbi.services.viz_service import VisualizationService
from backend.wpa.powerbi.services.model_service import ModelService
from backend.wpa.powerbi.services.cache_service import CacheService
from backend.wpa.powerbi.schemas.powerbi_request import DataQueryRequest

router = APIRouter(prefix="/powerbi", tags=["PowerBI-Style"])

# Services that don't depend on DB session can be instantiated once
data_service = DataService()
model_service = ModelService()
cache_service = CacheService()

# Pydantic Schemas for request bodies
class DashboardCreate(BaseModel):
    name: str
    description: Optional[str] = None

class WidgetCreate(BaseModel):
    title: str
    type: str
    config: Dict[str, Any]
    layout: Dict[str, Any]

# ---------------------------
# 1. DASHBOARD CRUD
# ---------------------------
@router.get("/dashboards", response_model=List[Dict[str, Any]])
async def list_dashboards(db: Session = Depends(get_db)):
    viz_service = VisualizationService(db)
    return viz_service.get_dashboards()

@router.post("/dashboards", status_code=201)
async def create_dashboard(dashboard: DashboardCreate, db: Session = Depends(get_db)):
    viz_service = VisualizationService(db)
    return viz_service.create_dashboard(name=dashboard.name, description=dashboard.description)

@router.get("/dashboard/{dashboard_id}")
async def get_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    viz_service = VisualizationService(db)
    dashboard_details = viz_service.get_dashboard_details(dashboard_id)
    if not dashboard_details:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard_details

# ---------------------------
# 2. WIDGET CRUD
# ---------------------------
@router.post("/dashboard/{dashboard_id}/widgets", status_code=201)
async def add_widget_to_dashboard(dashboard_id: int, widget: WidgetCreate, db: Session = Depends(get_db)):
    viz_service = VisualizationService(db)
    return viz_service.add_widget(
        dashboard_id=dashboard_id,
        title=widget.title,
        type=widget.type,
        config=widget.config,
        layout=widget.layout
    )

@router.delete("/widgets/{widget_id}", status_code=204)
async def delete_widget(widget_id: int, db: Session = Depends(get_db)):
    viz_service = VisualizationService(db)
    viz_service.delete_widget(widget_id)
    return {"ok": True}

# ---------------------------
# 3. WIDGET DATA & EXPORT
# ---------------------------
@router.get("/widget/{widget_id}/data")
async def get_widget_data(
    widget_id: int,
    filter_values: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    viz_service = VisualizationService(db)
    try:
        # Note: Caching would need to be re-implemented here if desired
        processed_data = viz_service.process_widget_from_db(widget_id, filters=filter_values)
        return processed_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Widget '{widget_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widget/{widget_id}/export")
async def get_widget_export(
    widget_id: int,
    format: str = Query(..., description="Export format: png, svg, pdf, csv, json"),
    filter_values: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    viz_service = VisualizationService(db)
    widget_model = db.query(Widget).filter(Widget.id == widget_id).first()
    if not widget_model:
        raise HTTPException(status_code=404, detail=f"Widget '{widget_id}' not found")

    widget_config = {
        "id": widget_model.id,
        "title": widget_model.title,
        "type": widget_model.type,
        **widget_model.config
    }

    try:
        df = data_service.execute_widget_query(widget_config, filters=filter_values)
        file_path = viz_service.export_widget(widget_config, df, format)
        return FileResponse(file_path, media_type=f"application/{format}", filename=f"{widget_model.title}.{format}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export widget: {e}")

# ---------------------------
# OTHERS (Unchanged for now)
# ---------------------------
@router.post("/data/query")
async def query_data(req: DataQueryRequest):
    try:
        df = data_service.execute_query(req)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/cache/clear")
async def clear_cache():
    cache_service.clear()
    return {"status": "cache cleared"}

@router.get("/status")
async def powerbi_status():
    # This might need adjustment based on the new DB-driven approach
    return {
        "status": "OK",
        "connectors": data_service.get_available_connectors(),
        "ai_ready": model_service.is_ready()
    }
