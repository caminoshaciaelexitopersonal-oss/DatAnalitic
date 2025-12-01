import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Set an environment variable to indicate we are running tests
os.environ['TESTING'] = 'True'

# Import the SQLAlchemy Base from where the models are defined
from backend.core.state_store import Base
from backend.core.dependencies import get_db
from backend.main import app as main_app # Import the main app

# --- Database Fixtures for Testing ---

@pytest.fixture(scope="session")
def engine():
    """
    Creates a new in-memory SQLite engine for the entire test session.
    """
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

@pytest.fixture(scope="session")
def setup_database(engine):
    """
    Creates all database tables once for the test session.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine, setup_database):
    """
    Provides a transactional scope for a test. This is the fixture
    that individual tests should depend on to get a clean DB state.
    """
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    # Begin a transaction
    connection = engine.connect()
    transaction = connection.begin()
    db.begin_nested()

    yield db

    # Rollback the transaction after the test is done to ensure isolation
    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client_with_db(db_session):
    """
    A fixture that provides a TestClient with the database dependency overridden.
    This is the key to solving the session scope issue. The session is yielded
    within the override, ensuring it stays open for the duration of the client request.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            # The session is managed by the db_session fixture's outer transaction
            pass

    main_app.dependency_overrides[get_db] = override_get_db
    with TestClient(main_app) as c:
        yield c
    main_app.dependency_overrides.clear()
