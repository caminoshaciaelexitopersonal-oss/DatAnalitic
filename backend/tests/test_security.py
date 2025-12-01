import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.orm import Session

from backend.core.security import (
    verify_password,
    create_access_token,
    hash_password,
    ALGORITHM,
    SECRET_KEY,
)
from backend.schemas import User, Role
from backend.core.state_store import UserModel

# --- Test Data ---
TEST_PASSWORD = "testpassword"
ADMIN_PASSWORD = "adminpassword"

# --- Test Fixtures ---
@pytest.fixture
def test_user_in_db(db_session: Session):
    user = UserModel(
        username="testuser",
        full_name="Test User",
        email="test@example.com",
        hashed_password=hash_password(TEST_PASSWORD),
        role=Role.DATA_SCIENTIST.value,
        disabled=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user_in_db(db_session: Session):
    admin_user = UserModel(
        username="admin",
        full_name="Admin User",
        email="admin@example.com",
        hashed_password=hash_password(ADMIN_PASSWORD),
        role=Role.ADMIN.value,
        disabled=False,
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    return admin_user

# --- Unit Tests for Security Utils ---
def test_verify_password(test_user_in_db):
    assert verify_password(TEST_PASSWORD, test_user_in_db.hashed_password)
    assert not verify_password("wrongpassword", test_user_in_db.hashed_password)

def test_create_and_decode_token(test_user_in_db):
    token = create_access_token(data={"sub": test_user_in_db.username})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == test_user_in_db.username

# --- Integration Tests for Auth Router ---
# Note: These tests now use the 'client_with_db' fixture from conftest.py
def test_login_for_access_token(client_with_db: TestClient, admin_user_in_db):
    # ACT
    response = client_with_db.post(
        "/auth/token",
        data={"username": admin_user_in_db.username, "password": ADMIN_PASSWORD}
    )

    # ASSERT
    assert response.status_code == 200, response.text
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_login_for_access_token_failure(client_with_db: TestClient, admin_user_in_db):
    # ACT
    response = client_with_db.post(
        "/auth/token",
        data={"username": admin_user_in_db.username, "password": "wrongpassword"}
    )

    # ASSERT
    assert response.status_code == 401, response.text
