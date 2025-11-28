import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.schemas import User, TokenData, Role
from backend.core.state_store import StateStore, get_state_store, DATABASE_URL # Import db components
from sqlalchemy import create_engine, text

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set. Application cannot start securely.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Database Setup for Users ---
engine = create_engine(DATABASE_URL)

def initialize_user_table():
    with engine.connect() as connection:
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            hashed_password TEXT,
            role TEXT,
            disabled BOOLEAN DEFAULT FALSE
        )
        """))
        # Add a default admin user if it doesn't exist
        result = connection.execute(text("SELECT * FROM users WHERE username = :username"), {"username": "admin"}).fetchone()
        if not result:
            default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin_password_placeholder")
            if default_password == "admin_password_placeholder" or not default_password:
                print("WARNING: DEFAULT_ADMIN_PASSWORD not set. Skipping default admin creation.")
                return

            hashed_password = pwd_context.hash(default_password)
            connection.execute(
                text("""
                INSERT INTO users (username, full_name, email, hashed_password, role, disabled)
                VALUES (:username, :full_name, :email, :hashed_password, :role, :disabled)
                """),
                {
                    "username": "admin",
                    "full_name": "Admin User",
                    "email": "admin@example.com",
                    "hashed_password": hashed_password,
                    "role": "admin",
                    "disabled": False,
                }
            )
            print("Default admin user created.")

initialize_user_table()


# --- Utility Functions ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # ... (same as before)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_from_db(db: Session, username: str) -> Optional[User]:
    """Retrieves a user from the database."""
    query = text("SELECT * FROM users WHERE username = :username")
    user_data = db.execute(query, {"username": username}).fetchone()
    if not user_data:
        return None
    return User(**user_data._asdict())


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
