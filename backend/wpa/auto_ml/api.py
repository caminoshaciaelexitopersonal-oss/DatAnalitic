from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
from backend.wpa.auto_ml.model_registry import MODEL_REGISTRY
from backend.wpa.auto_ml.tasks import run_full_automl
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
