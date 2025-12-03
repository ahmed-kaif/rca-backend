from typing import Annotated, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.core.config import settings
from src.models.user import User, UserRole
from src.schemas.auth import TokenData

# Defines where the token comes from (the /login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_db() -> Generator:
    """
    Creates a new database session for each request and closes it afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type shortcuts
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    Validates the JWT token and returns the current user.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = session.query(User).filter(User.email == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """
    Dependency to restrict access to ADMINS only.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
