from datetime import datetime
from pydantic import BaseModel, EmailStr
from src.models.user import UserRole, BloodGroup


# --- Profile Schemas ---
class ProfileBase(BaseModel):
    full_name: str | None = None
    phone_number: str | None = None
    blood_group: BloodGroup | None = None
    bio: str | None = None
    avatar_url: str | None = None

    # Academic
    university_id: str | None = None
    department: str | None = None
    series: str | None = None

    # Work
    is_employed: bool = False
    current_company: str | None = None
    designation: str | None = None
    work_location: str | None = None
    linkedin_profile: str | None = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    # Only Admin can update roles or active status usually
    is_active: bool | None = None
    role: UserRole | None = None


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    profile: ProfileResponse | None = None

    class Config:
        from_attributes = True
