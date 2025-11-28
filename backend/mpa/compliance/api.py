from fastapi import APIRouter, Depends, Body, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from backend.mpa.compliance.service import ComplianceService, get_compliance_service
from backend.core.state_store import StateStore, get_state_store

router = APIRouter(tags=["MPA - Compliance"])

class AnonymizeRequest(BaseModel):
    session_id: str
    columns: Optional[List[str]] = None

@router.post("/anonymize")
def anonymize_data(
    request: AnonymizeRequest = Body(...),
    service: ComplianceService = Depends(get_compliance_service),
    state_store: StateStore = Depends(get_state_store)
):
    """
    Anonymizes PII data for a given session.
    """
    df = state_store.load_dataframe(request.session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="No data found for the given session ID.")

    anonymized_df = service.anonymize_dataframe(df, request.columns)

    # Overwrite the existing dataframe with the anonymized version
    state_store.save_dataframe(request.session_id, anonymized_df)

    return {
        "message": "Data anonymization complete.",
        "anonymized_columns": service.find_pii_columns(df) if not request.columns else request.columns
    }
