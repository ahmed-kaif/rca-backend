from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from src.api import deps
from src.core import security
from src.models.user import User, Profile
from src.schemas.user import (
    UserCreate,
    UserResponse,
    ProfileCreate,
    ProfileResponse,
)

router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
def create_user(
    *,
    session: deps.SessionDep,
    user_in: UserCreate,
) -> Any:
    """
    Create new user (Open Registration).
    """
    user = session.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # Create User
    db_user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        role=user_in.role,
        is_active=user_in.is_active,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Create Empty Profile for the user automatically
    db_profile = Profile(user_id=db_user.id, full_name=user_in.email.split("@")[0])
    session.add(db_profile)
    session.commit()

    return db_user


@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: deps.CurrentUser,
) -> Any:
    """
    Get current logged-in user.
    """
    return current_user


@router.put("/me/profile", response_model=ProfileResponse)
def update_user_profile(
    *,
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
    profile_in: ProfileCreate,
) -> Any:
    """
    Update own profile.
    """
    profile = current_user.profile
    if not profile:
        # Should not happen if we create profile on register, but safety check
        profile = Profile(user_id=current_user.id)
        session.add(profile)

    profile_data = profile_in.model_dump(exclude_unset=True)
    for field, value in profile_data.items():
        setattr(profile, field, value)

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.get(
    "/",
    response_model=List[UserResponse],
    dependencies=[Depends(deps.get_current_active_superuser)],
)
def read_users(
    session: deps.SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users. (Admin Only)
    """
    users = session.query(User).offset(skip).limit(limit).all()
    return users
