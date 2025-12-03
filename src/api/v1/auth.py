from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from src.api import deps
from src.core import security, settings
from src.models.user import User
from src.schemas.auth import Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
    session: deps.SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # 1. Check if user exists
    user = session.query(User).filter(User.email == form_data.username).first()

    # 2. Check password
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 3. Generate Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
