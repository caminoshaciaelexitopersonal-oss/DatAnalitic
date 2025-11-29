from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from backend.wpa.auto_ml.model_registry import MODEL_REGISTRY
from backend.wpa.auto_ml.tasks import run_full_automl
 
from backend.wpa.auto_ml.hpo import run_hpo_study
from backend.wpa.auto_ml.schemas import AutoMLRequest, AutoMLSubmitResponse, HPORequest, HPOSubmitResponse
 
from backend.core.state_store import get_state_store, StateStore
import uuid

router = APIRouter()

@router.get("/status", operation_id="getAutoMLStatus")
async def get_automl_status():
    """
    Returns the status of the AutoML module, including the number of registered models.
    """
    return {
        "status": "running",
        "registered_models": len(MODEL_REGISTRY),
        "models": list(MODEL_REGISTRY.keys())
    }

@router.get("/models", operation_id="getAutoMLModels")
async def get_automl_models():
    """
    Returns a list of all registered models.
    """
    return list(MODEL_REGISTRY.keys())

@router.get("/download/{job_id}/{model_name}", operation_id="downloadAutoMLModel")
async def download_automl_model(job_id: str, model_name: str):
    """
    Downloads a trained model.
    """
    file_path = f"/tmp/{job_id}_{model_name}.joblib"
    return FileResponse(file_path, media_type="application/octet-stream", filename=f"{model_name}.joblib")

@router.post("/submit", response_model=AutoMLSubmitResponse, operation_id="submitAutoMLJob")
async def submit_automl_job(
    request: AutoMLRequest,
    state_store: StateStore = Depends(get_state_store),
):
    """
    Submits a new AutoML job.
    This enqueues a Celery task to run the full AutoML pipeline.
    """
    # Verify that the main job_id exists
    job = state_store.get_job(uuid.UUID(request.job_id))
    if not job:
        raise HTTPException(status_code=404, detail=f"Main job_id '{request.job_id}' not found.")
 
    # Enqueue the Celery task
    task = run_full_automl.delay(request.job_id, request.dict())

    return AutoMLSubmitResponse(automl_job_id=request.job_id, celery_task_id=task.id)

@router.post("/hpo/submit", response_model=HPOSubmitResponse, operation_id="submitHPOJob")
async def submit_hpo_job(
    request: HPORequest,
    state_store: StateStore = Depends(get_state_store),
):
    """
    Submits a new HPO job.
    """
    # Verify that the main job_id exists
    job = state_store.get_job(uuid.UUID(request.job_id))
    if not job:
        raise HTTPException(status_code=404, detail=f"Main job_id '{request.job_id}' not found.")

    # Enqueue the Celery task
    task = run_hpo_study.delay(request.job_id, request.dict())

    return HPOSubmitResponse(hpo_job_id=request.job_id, celery_task_id=task.id)
 
