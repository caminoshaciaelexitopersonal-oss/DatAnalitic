"""
This module contains the Pydantic models (schemas) for the AutoML API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class AutoMLRequest(BaseModel):
    """Payload for the POST /submit endpoint."""
    job_id: str = Field(..., description="The job_id of the main analysis pipeline to link with.")
    target: Optional[str] = Field(None, description="The target variable for supervised learning. If None, it's inferred from the target detection step.")
    models_to_run: Optional[List[str]] = Field(None, description="Optional list of model keys to run. If None, a default selection is used.")
    perform_hpo: bool = Field(False, description="Whether to perform Hyperparameter Optimization.")

class AutoMLSubmitResponse(BaseModel):
    """Response from the POST /submit endpoint."""
    automl_job_id: str
    celery_task_id: str
