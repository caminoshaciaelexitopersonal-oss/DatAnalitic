"""
This module contains the Pydantic models (schemas) for the AutoML API,
defining the data structures for requests and responses as per the "Plan Científico".
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AutoMLSubmitRequest(BaseModel):
    """Payload for the POST /submit endpoint."""
    input_csv_path: str
    task_type: str = "auto"
    target: Optional[str] = None
    params: Dict[str, Any] = {}

class AutoMLSubmitResponse(BaseModel):
    """Response from the POST /submit endpoint."""
    job_id: str
    task_id: str
