
from fastapi import APIRouter, Depends, HTTPException
from backend.core.state_store import StateStore, get_state_store
from sqlalchemy.orm import Session
from backend.core.dependencies import get_db

router = APIRouter(tags=["MPA - DTL"])

@router.get("/job/{job_id}/quality")
def get_quality_report(job_id: str, service: StateStore = Depends(get_state_store)):
    """
    Retrieves the data quality report for a given job.
    """
    report = service.load_json_artifact(job_id, "quality_report.json")
    if not report:
        raise HTTPException(status_code=404, detail="Data quality report not found.")
    return report

@router.get("/job/{job_id}/schema")
def get_schema_metadata(job_id: str, service: StateStore = Depends(get_state_store)):
    """
    Retrieves the schema validation metadata for a given job.
    """
    schema = service.load_json_artifact(job_id, "metadata.json")
    if not schema:
        raise HTTPException(status_code=404, detail="Schema metadata not found.")
    return schema
