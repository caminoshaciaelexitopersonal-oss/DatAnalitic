
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime

class TraceableRequest(BaseModel):
    job_id: UUID = Field(default_factory=uuid4)
    user_id: Optional[str] = None

class EtlStep(BaseModel):
    action: str
    params: Dict[str, Any]

class Session(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session_id: UUID
    created_at: datetime
    status: str = "active"
    jobs: List["Job"] = []

class Step(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    step_id: UUID
    job_id: UUID
    description: str
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime
    status: str = "pending"

class Job(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: UUID
    session_id: UUID
    job_type: str
    created_at: datetime
    status: str = "pending"
    steps: List[Step] = []

Session.update_forward_refs()
Job.update_forward_refs()
