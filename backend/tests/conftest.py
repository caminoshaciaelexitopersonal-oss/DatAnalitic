import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set an environment variable to indicate we are running tests
os.environ['TESTING'] = 'True'

# Import the SQLAlchemy Base from where the models are defined
from backend.core.state_store import Base
from backend.main import app

@pytest.fixture(scope="function")
def test_db():
    """
    Pytest fixture to provide a transactional in-memory SQLite database session.
    """
    # Use in-memory SQLite for tests.
    # `check_same_thread` is required for multi-threaded test runners.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create a new session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = TestingSessionLocal()

    try:
        yield db_session
    finally:
        db_session.close()
        # Drop all tables after the test finishes
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_app():
    """
    Provides the FastAPI app instance for testing.
    """
    return app

@pytest.fixture(scope="module")
def client(test_app):
    """
    Creates a TestClient for the FastAPI app.
    """
    with TestClient(test_app) as c:
        yield c
