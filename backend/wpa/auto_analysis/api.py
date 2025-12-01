from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import mlflow
from typing import Dict, Any

import json
from backend.celery_worker import celery_app
from backend.core.state_store import StateStore, get_state_store
from backend.core.security import User, require_role
from backend.schemas import Role
from backend.core.config import config


# Existing imports
router = APIRouter(tags=["WPA - Automated Analysis"])


@router.get("/jobs/status", operation_id="getAllJobStatuses")
def get_all_job_statuses(state_store: StateStore = Depends(get_state_store)):
    """
    Returns the status of all jobs.
    """
    statuses = state_store.load_all_job_statuses()
    return statuses


@router.get("/{job_id}/status", operation_id="getJobStatus")
def get_job_status(job_id: str, state_store: StateStore = Depends(get_state_store)):
    status = state_store.load_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found.")
    return status


@router.get("/{job_id}/report/{format}", operation_id="downloadReport")
def download_report(job_id: str, format: str):
    """
    Downloads the specified report (docx, xlsx, or pdf) for a completed job.
    It reads the manifest to find the correct report path.
    """
    if format not in ["docx", "xlsx", "pdf"]:
        raise HTTPException(status_code=400, detail="Format must be one of docx, xlsx, or pdf.")

    # This endpoint is not yet fully implemented as report generation is pending.
    # For now, we will return a placeholder.
    # In the future, this will load the report from the StateStore.
    raise HTTPException(status_code=501, detail="Report generation is not yet implemented.")

    media_types = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf"
    }

    filename = f"report_{job_id}.{format}"
    return FileResponse(report_path, media_type=media_types[format], filename=filename)

import os

@router.get("/{job_id}/target", operation_id="getTargetDetectionResult")
def get_target_detection_result(job_id: str, state_store: StateStore = Depends(get_state_store)):
    """
    Returns the target.json file for the specified job from the StateStore.
    """
    target_data = state_store.load_json_artifact(job_id, "target.json")
    if target_data is None:
        raise HTTPException(status_code=404, detail="Target detection result not found.")
    return target_data

@router.get("/{job_id}/quality-report", operation_id="getQualityReport")
def get_quality_report(job_id: str, state_store: StateStore = Depends(get_state_store)):
    """
    Returns the quality_report.json file for the specified job from the StateStore.
    """
    quality_data = state_store.load_json_artifact(job_id, "quality_report.json")
    if quality_data is None:
        raise HTTPException(status_code=404, detail="Quality report not found.")
    return quality_data
