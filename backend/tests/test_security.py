import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from jose import jwt
from unittest.mock import patch

from backend.core.security import (
    verify_password,
    create_access_token,
    get_current_user,
    require_role,
    SECRET_KEY,
    ALGORITHM,
    pwd_context,
)
from backend.schemas import User, Role
from backend.app.api.auth_router import router as auth_router

# --- Test Data ---
@pytest.fixture
def test_user():
    return User(
        username="testuser",
        full_name="Test User",
        email="test@example.com",
        hashed_password=pwd_context.hash("testpass"),
        role=Role.DATA_SCIENTIST,
        disabled=False,
    )

# --- Unit Tests for Security Utils ---
def test_verify_password():
    hashed_pass = pwd_context.hash("mypassword")
    assert verify_password("mypassword", hashed_pass)
    assert not verify_password("wrongpassword", hashed_pass)

def test_create_and_decode_token(test_user):
    token = create_access_token(data={"sub": test_user.username})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == test_user.username

# --- Setup for Dependency Tests ---
app = FastAPI()

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/items/scientist")
async def read_scientist_items(current_user: User = Depends(require_role(Role.DATA_SCIENTIST))):
    return {"item": "scientist_data", "owner": current_user.username}

# Include the auth router for integration tests
app.include_router(auth_router)
client = TestClient(app)

# --- Tests for Dependencies ---
@patch("backend.core.security.get_user")
def test_get_current_user_valid_token(mock_get_user, test_user):
    mock_get_user.return_value = test_user
    token = create_access_token(data={"sub": test_user.username})
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == test_user.username

def test_get_current_user_invalid_token():
    # This token is structurally invalid and will raise JWTError
    response = client.get("/users/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401

@patch("backend.core.security.get_user")
def test_require_role_success(mock_get_user, test_user):
    test_user.role = Role.DATA_SCIENTIST
    mock_get_user.return_value = test_user
    token = create_access_token(data={"sub": test_user.username})
    response = client.get("/items/scientist", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["owner"] == test_user.username

@patch("backend.core.security.get_user")
def test_require_role_failure(mock_get_user, test_user):
    test_user.role = Role.ADMIN # Assign a different role
    mock_get_user.return_value = test_user
    token = create_access_token(data={"sub": test_user.username})
    response = client.get("/items/scientist", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

# --- Integration Test for Auth Router ---
def test_login_for_access_token():
    response = client.post("/auth/token", data={"username": "admin", "password": "adminpass"})
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_login_for_access_token_failure():
    response = client.post("/auth/token", data={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401
