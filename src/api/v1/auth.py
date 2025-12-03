from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from src.api import deps
from src.core import security, settings
from src.models.enums import UserRole
from src.models.user import Profile, User
from src.schemas.auth import Token
from src.schemas.user import AlumniRegister, StudentRegister, UserResponse

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


@router.post("/register/student", response_model=UserResponse)
def register_student(
    *,
    session: deps.SessionDep,
    user_in: StudentRegister,
) -> Any:
    """
    Register a new STUDENT.
    """
    # 1. Check if email exists
    if session.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists.",
        )

    # 2. Create User (Force Role = STUDENT)
    db_user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        role=UserRole.STUDENT,
        is_active=True,
    )

    # 3. Create Profile with Student Data
    db_profile = Profile(
        user_id=db_user.id,
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
        blood_group=user_in.blood_group,
        university_id=user_in.university_id,
        department=user_in.department,
        series=user_in.series,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    session.add(db_profile)
    session.commit()

    return db_user


@router.post("/register/alumni", response_model=UserResponse)
def register_alumni(
    *,
    session: deps.SessionDep,
    user_in: AlumniRegister,
) -> Any:
    """
    Register a new ALUMNI.
    """
    if session.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    # 1. Create User (Force Role = PENDING or ALUMNI)
    # Usually, Alumni need verification, so we might set Role=PENDING initially.
    # But for now, let's set them as ALUMNI.
    db_user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        role=UserRole.ALUMNI,
        is_active=True,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # 2. Create Profile with Alumni Data
    db_profile = Profile(
        user_id=db_user.id,
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
        blood_group=user_in.blood_group,
        series=user_in.series,  # Batch
        is_employed=user_in.is_employed,
        current_company=user_in.current_company,
        designation=user_in.designation,
        linkedin_profile=user_in.linkedin_profile,
    )
    session.add(db_profile)
    session.commit()

    return db_user
