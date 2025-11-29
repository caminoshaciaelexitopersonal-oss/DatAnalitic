import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from jose import jwt
from unittest.mock import patch
from sqlalchemy.orm import Session

from backend.core.security import (
    verify_password,
    create_access_token,
    get_current_user,
    require_role,
    get_db,
    initialize_default_admin,
    ALGORITHM,
    pwd_context,
)
from backend.schemas import User, Role, UserBase
from backend.core.auth.api import router as auth_router

# --- Test Data ---
TEST_PASSWORD = "testpassword"
ADMIN_PASSWORD = "adminpassword"

@pytest.fixture
def test_user_in_db(test_db: Session):
    user = User(
        username="testuser",
        full_name="Test User",
        email="test@example.com",
        hashed_password=pwd_context.hash(TEST_PASSWORD),
        role=Role.DATA_SCIENTIST,
        disabled=False,
    )
    test_db.add(user)
    test_db.commit()
    return user

@pytest.fixture(autouse=True)
def setup_default_admin(test_db: Session):
    # This fixture automatically runs for every test, ensuring the admin exists
    with patch.dict('os.environ', {'DEFAULT_ADMIN_PASSWORD': ADMIN_PASSWORD}):
        initialize_default_admin(test_db)

# --- App setup with dependency override ---
app = FastAPI()
app.include_router(auth_router)

# This is the key part: override the get_db dependency for tests
@pytest.fixture
def client(test_db: Session):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # Clear the override after the test
    app.dependency_overrides.clear()

# --- Unit Tests for Security Utils ---
def test_verify_password(test_user_in_db):
    assert verify_password(TEST_PASSWORD, test_user_in_db.hashed_password)
    assert not verify_password("wrongpassword", test_user_in_db.hashed_password)

def test_create_and_decode_token(test_user_in_db):
    token = create_access_token(data={"sub": test_user_in_db.username})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == test_user_in_db.username

# --- Tests for Dependencies (no longer need mocks) ---
def test_get_current_user_valid_token(client: TestClient, test_user_in_db):
    token = create_access_token(data={"sub": test_user_in_db.username})

    # We need a temporary endpoint to test the dependency
    @app.get("/test_users/me")
    async def read_users_me(current_user: User = Depends(get_current_user)):
        return current_user

    response = client.get("/test_users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == test_user_in_db.username

# --- Integration Tests for Auth Router (now enabled) ---
def test_login_for_access_token(client: TestClient):
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_login_for_access_token_failure(client: TestClient):
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401
