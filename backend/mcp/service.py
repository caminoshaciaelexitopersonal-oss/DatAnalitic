from typing import Dict, Optional
from uuid import UUID
from fastapi import Depends

from backend.mcp.schemas import Session, Job, Step
from backend.core.state_store import StateStore, get_state_store

class McpService:
    """
    Service for the Main Control Plane (MCP).
    Handles the orchestration of sessions, jobs, and steps using the ORM.
    """
    def __init__(self, state_store: StateStore):
        self._store = state_store

    def create_session(self) -> Session:
        """Creates a new analysis session."""
        session_orm = self._store.create_session()
        return Session.model_validate(session_orm.__dict__)

    def get_session(self, session_id: UUID) -> Optional[Session]:
        """Retrieves a session by its ID."""
        session_orm = self._store.get_session(session_id)
        if not session_orm:
            return None
        return Session.model_validate(session_orm.__dict__)

    def create_job(self, session_id: UUID, job_type: str) -> Optional[Job]:
        """Creates a new job within a session."""
        job_orm = self._store.create_job(session_id, job_type)
        if not job_orm:
            return None
        return Job.model_validate(job_orm.__dict__)

    def create_step(self, job_id: UUID, description: str, payload: Optional[Dict] = None) -> Optional[Step]:
        """Creates a new step within a job."""
        step_orm = self._store.create_mcp_step(job_id, description, payload)
        if not step_orm:
            return None
        return Step.model_validate(step_orm.__dict__)

# --- Dependency Injection ---
def get_mcp_service(state_store: StateStore = Depends(get_state_store)) -> McpService:
    """
    Dependency injector for the McpService.
    """
    return McpService(state_store)
