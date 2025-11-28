from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from backend.mpa.ethics.service import AIEthicsService, get_ai_ethics_service

router = APIRouter(tags=["MPA - AI Ethics"])

class BiasAuditRequest(BaseModel):
    run_id: str
    sensitive_feature: str
    label_column: str

class ModelCardRequest(BaseModel):
    run_id: str

@router.post("/bias-audit", response_model=Dict[str, Any])
def run_bias_audit(
    request: BiasAuditRequest = Body(...),
    service: AIEthicsService = Depends(get_ai_ethics_service)
):
    """
    Performs a bias audit on a specified model run.
    """
    try:
        audit_results = service.run_bias_audit(
            run_id=request.run_id,
            sensitive_feature=request.sensitive_feature,
            label_column=request.label_column
        )
        return audit_results
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.post("/model-card", response_model=str)
def generate_model_card(
    request: ModelCardRequest = Body(...),
    service: AIEthicsService = Depends(get_ai_ethics_service)
):
    """
    Generates and saves a Model Card for a specified model run.
    """
    try:
        model_card = service.generate_model_card(run_id=request.run_id)
        return model_card
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while generating the model card: {e}")
