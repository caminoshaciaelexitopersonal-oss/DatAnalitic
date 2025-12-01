from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    User,
    create_access_token,
    get_user_from_db,
    verify_password,
    get_db, # Import the new DB dependency
)
from backend.schemas import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/token", response_model=Token, operation_id="loginForAccessToken")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db) # Use the new DB dependency
):
    """
    Provides a JWT token for valid user credentials.
    """
    user = get_user_from_db(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
