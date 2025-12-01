import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from backend.schemas import User, TokenData, Role
from backend.core.state_store import StateStore, get_state_store, UserModel

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set. Application cannot start securely.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against a hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# --- Database Initialization Logic ---
def initialize_default_admin(db: Session):
    """
    Checks for and creates a default admin user if one doesn't exist.
    This function should be called during application startup.
    Credentials are read from environment variables for security.
    """
    try:
        admin_username = os.getenv("DEFAULT_ADMIN_USER", "admin")
        admin_user = db.query(UserModel).filter(UserModel.username == admin_username).first()

        if not admin_user:
            default_password = os.getenv("DEFAULT_ADMIN_PASSWORD")
            if not default_password:
                print("WARNING: DEFAULT_ADMIN_PASSWORD not set. Skipping default admin creation.")
                return

            hashed_password = hash_password(default_password)
            new_admin = UserModel(
                username=admin_username,
                full_name="Admin User",
                email=f"{admin_username}@example.com",
                hashed_password=hashed_password,
                role="admin",
                disabled=False
            )
            db.add(new_admin)
            db.commit()
            print("Default admin user created.")
    except Exception as e:
        print(f"DEBUG: Could not connect to DB during admin initialization: {e}")


# --- Utility Functions ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_from_db(db: Session, username: str) -> Optional[UserModel]:
    """Retrieves a user from the database using the ORM."""
    return db.query(UserModel).filter(UserModel.username == username).first()


# --- FastAPI Dependencies ---
def get_db(state_store: StateStore = Depends(get_state_store)) -> Session:
    """Dependency to get a DB session."""
    return state_store.SessionLocal()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # ... (logic is similar, but uses DB)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user_from_db(db, username=token_data.username)
    if user is None or user.disabled:
        raise credentials_exception
    return user

def require_role(required_role: Role):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role",
            )
        return current_user
    return role_checker
