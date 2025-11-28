import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict

import os
import json
from backend.mcp.schemas import Job
from backend.core.state_store import StateStore, get_state_store
from backend.core.config import config
# Import the master pipeline task
from backend.wpa.tasks import master_pipeline_task

router = APIRouter(tags=["MCP - Main Control Plane"])

@router.post("/job/start", response_model=Job, operation_id="createJobUnified")
async def create_job_unified(
    file: UploadFile = File(...),
    service: StateStore = Depends(get_state_store),
):
    """
    Unified endpoint to start a new analysis job.
    1. Creates a Session and a Job.
    2. Uploads the data file to object storage (MinIO).
    3. Triggers the master asynchronous pipeline.
    """
    # 1. Create session and job records in the database
    session = service.create_session()
    job = service.create_job(session.session_id, job_type="unified_analysis", filename=file.filename)

    if not job:
        raise HTTPException(status_code=500, detail="Failed to create a job record.")

    job_id = str(job.job_id)

    # 2. Upload the file to MinIO, associating it with the job_id
    try:
        # We use job_id as the "folder" in MinIO for all related artifacts
        service.save_raw_file(job_id, file.filename, await file.read())
    except Exception as e:
        # TODO: Add logic to mark the job as failed
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

    # 3. Trigger the master pipeline
    master_pipeline_task.delay(job_id)

    # 4. Set initial job status
    initial_status = {"status": "queued", "stage": "Starting"}
    service.save_job_status(job_id, initial_status)

    return job

@router.get("/job/{job_id}/status", operation_id="getJobStatusUnified")
def get_job_status_unified(job_id: str, service: StateStore = Depends(get_state_store)):
    """Retrieves the current status of a job."""
    status = service.load_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found.")
    return status

@router.get("/job/{job_id}/results", operation_id="getJobResults")
def get_job_results(job_id: str):
    """
    Retrieves a consolidated summary of the job results for the frontend.
    """
    job_dir = os.path.join(config.PROCESSED_DATA_DIR, job_id)
    manifest_path = os.path.join(job_dir, "manifest.json")

    if not os.path.exists(manifest_path):
        raise HTTPException(status_code=404, detail="Job manifest not found.")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # Extract key information for the frontend
    target_info_path = os.path.join(job_dir, "target.json")
    target_info = {}
    if os.path.exists(target_info_path):
        with open(target_info_path, "r") as f:
            target_data = json.load(f)
            target_info = {
                "selected_target": target_data.get("selected_target"),
                "confidence": target_data.get("confidence"),
                "explanation": target_data.get("explanation"),
                "candidates": target_data.get("candidates")
            }

    # Construct download URLs for reports
    report_urls = {}
    if "reports" in manifest:
        for format, rel_path in manifest["reports"].items():
            if format != "generated_at":
                report_urls[format] = f"/unified/v1/wpa/auto-analysis/{job_id}/report/{format}"

    return {
        "job_id": job_id,
        "status": manifest.get("status", "unknown"),
        "dataset_hash": manifest.get("dataset_hash"),
        "target_detection": target_info,
        "reports": report_urls,
        "mlflow_run_id": manifest.get("mlflow_run_id") # Assuming this will be added to manifest
    }
