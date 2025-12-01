from typing import Dict, Any, List
from backend.core.state_store import StateStore, get_state_store

class DataGovernanceService:
    """
    MPA service for data governance tasks, including data cataloging and lineage.
    """
    def __init__(self, state_store: StateStore):
        self.state_store = state_store

    def generate_data_catalog(self) -> List[Dict[str, Any]]:
        """
        Generates a catalog of all datasets stored in the system by inspecting
        the persistent storage.
        """
        session_ids = self.state_store.list_all_sessions()

        catalog = []
        for session_id in session_ids:
            df = self.state_store.load_dataframe(session_id)
            if df is not None:
                catalog.append({
                    "session_id": session_id,
                    "columns": df.columns.tolist(),
                    "num_rows": len(df),
                    "num_cols": len(df.columns),
                })
        return catalog

# --- Dependency Injection ---
governance_service = DataGovernanceService(state_store=get_state_store())

def get_governance_service() -> DataGovernanceService:
    return governance_service
