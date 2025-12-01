
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.mcp.schemas import Job
from backend.core.state_store import StateStore, get_state_store
from backend.core.dependencies import get_db
from backend.wpa.tasks import master_pipeline_task

router = APIRouter(tags=["MCP - Main Control Plane"])

@router.post("/job/start", response_model=Job, operation_id="createJobUnified")
async def create_job_unified(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    service: StateStore = Depends(get_state_store),
):
    """
    Unified endpoint to start a new analysis job.
    """
    session = service.create_session(db)
    job = service.create_job(db, session.session_id, job_type="unified_analysis", filename=file.filename)

    if not job:
        raise HTTPException(status_code=500, detail="Failed to create a job record.")

    job_id = str(job.job_id)

    try:
        service.save_raw_file(job_id, file.filename, await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

    master_pipeline_task.delay(job_id)

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
def get_job_results(job_id: str, service: StateStore = Depends(get_state_store)):
    """
    Retrieves a consolidated summary of the job results.
    """
    manifest = service.load_json_artifact(job_id, "manifest.json")
    if not manifest:
        raise HTTPException(status_code=404, detail="Job manifest not found.")

    target_data = service.load_json_artifact(job_id, "target.json")
    target_info = {
        "selected_target": target_data.get("selected_target") if target_data else None,
        "confidence": target_data.get("confidence") if target_data else 0.0,
        "explanation": target_data.get("explanation") if target_data else "Target information not available.",
        "candidates": target_data.get("candidates") if target_data else [],
    }

    report_urls = {}
    if "reports" in manifest:
        for format, rel_path in manifest["reports"].items():
            if format != "generated_at":
                report_urls[format] = f"/unified/v1/wpa/auto-analysis/{job_id}/report/{format}"

    job_status = service.load_job_status(job_id)
    final_status = job_status.get("status", "unknown") if job_status else manifest.get("status", "unknown")

    return {
        "job_id": job_id,
        "status": final_status,
        "dataset_hash": manifest.get("dataset_hash"),
        "target_detection": target_info,
        "reports": report_urls,
        "mlflow_run_id": manifest.get("mlflow_run_id")
    }
