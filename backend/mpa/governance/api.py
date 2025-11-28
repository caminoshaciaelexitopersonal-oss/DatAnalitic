from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from backend.mpa.governance.service import DataGovernanceService, get_governance_service

router = APIRouter(tags=["MPA - Data Governance"])

@router.get("/catalog", response_model=List[Dict[str, Any]])
def get_data_catalog(
    service: DataGovernanceService = Depends(get_governance_service)
):
    """
    Retrieves the data catalog, showing metadata for all datasets in the system.
    """
    return service.generate_data_catalog()
