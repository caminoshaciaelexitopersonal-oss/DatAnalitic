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

# New imports for code inspection and report generation
from backend.wpa.code_inspector.recorder import CodeRecorder
from backend.wpa.code_inspector.exporter import CodeExporter
from backend.wpa.report_generator.docx_generator import create_docx_report
from backend.wpa.report_generator.excel_generator import create_excel_report
from backend.wpa.report_generator.pdf_generator import create_pdf_report

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

@router.get("/{job_id}/code", operation_id="getGeneratedCode")
def get_generated_code(job_id: str, format: str = "python"):
    """
    Returns the code generated during the analysis in the specified format.
    """
    exporter = CodeExporter(job_id)
    if format == "python":
        path = exporter.export_to_python()
        media_type = "application/x-python"
    elif format == "json":
        path = exporter.export_to_json()
        media_type = "application/json"
    elif format == "text":
        path = exporter.export_to_text()
        media_type = "text/plain"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Must be 'python', 'json', or 'text'.")

    return FileResponse(path, media_type=media_type, filename=f"code_{job_id}.{format}")

def _get_artifacts_for_report(job_id: str) -> Dict[str, Any]:
    """Helper to load all necessary artifacts for report generation."""
    job_dir = os.path.join(config.PROCESSED_DATA_DIR, job_id)
    return {
        "summary": "This is an auto-generated executive summary.",
        "eda": {"overview": {"num_rows": 100, "num_cols": 10}},
        "model": {"metrics": {"accuracy": 0.95, "f1_score": 0.92}},
        "explainability_path": os.path.join(job_dir, "explainability"),
        "code": CodeExporter(job_id).prepare_for_report()
    }

@router.get("/{job_id}/report/{format}", operation_id="downloadReport")
def download_report(job_id: str, format: str):
    """
    Downloads the specified report (docx, xlsx, or pdf) for a completed job.
    It reads the manifest to find the correct report path.
    """
    if format not in ["docx", "xlsx", "pdf"]:
        raise HTTPException(status_code=400, detail="Format must be one of docx, xlsx, or pdf.")

    job_dir = os.path.join(config.PROCESSED_DATA_DIR, job_id)
    manifest_path = os.path.join(job_dir, "manifest.json")

    if not os.path.exists(manifest_path):
        raise HTTPException(status_code=404, detail="Job manifest not found.")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    report_info = manifest.get("reports")
    if not report_info or format not in report_info:
        raise HTTPException(status_code=404, detail=f"Report in format '{format}' not found for this job.")

    # Construct full path from base and relative path in manifest
    report_path = os.path.join(job_dir, report_info[format])

    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report file is missing from artifacts.")

    media_types = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf"
    }

    filename = f"report_{job_id}.{format}"
    return FileResponse(report_path, media_type=media_types[format], filename=filename)

import os

@router.get("/{job_id}/target", operation_id="getTargetDetectionResult")
def get_target_detection_result(job_id: str):
    """
    Returns the target.json file for the specified job.
    """
    job_dir = os.path.join(config.PROCESSED_DATA_DIR, job_id)
    target_path = os.path.join(job_dir, "target.json")
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Target detection result not found.")
    return FileResponse(target_path, media_type="application/json")
