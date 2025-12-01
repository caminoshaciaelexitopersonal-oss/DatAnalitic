from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
import uuid
import mlflow
from typing import Dict, Any

import json
from backend.celery_worker import celery_app
from backend.core.state_store import StateStore, get_state_store
from backend.wpa.auto_analysis.report_service import ReportService
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
def download_report(job_id: str, format: str, state_store: StateStore = Depends(get_state_store)):
    """
    Generates and downloads the specified report for a completed job.
    Currently, only PDF format is supported.
    """
    if format != "pdf":
        raise HTTPException(status_code=400, detail="Format must be pdf.")

    report_filename = f"executive_report_{job_id}.pdf"

    try:
        # Check if the report already exists in the StateStore (caching)
        report_bytes = state_store.load_artifact_as_bytes(job_id, f"reports/{report_filename}")

        if report_bytes is None:
            # If not, generate it, save it, and then load it
            print(f"Report for job {job_id} not found. Generating...")
            report_service = ReportService(job_id, state_store)
            report_bytes = report_service.generate_report()

            # Save the newly generated report for future requests
            state_store.save_report_artifact(job_id, report_filename, report_bytes)
            print(f"Report for job {job_id} saved to StateStore.")

        media_type = "application/pdf"
        headers = {
            'Content-Disposition': f'attachment; filename="{report_filename}"'
        }

        return Response(content=report_bytes, media_type=media_type, headers=headers)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Could not generate report: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

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
