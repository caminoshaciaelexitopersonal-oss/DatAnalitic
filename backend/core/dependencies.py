
from typing import Generator
from backend.core.state_store import get_state_store

def get_db() -> Generator:
    """
    FastAPI dependency that provides a transactional scope around a series of
    database operations.
    """
    db = None
    try:
        state_store = get_state_store()
        db = state_store.SessionLocal()
        yield db
    finally:
        if db:
            db.close()
