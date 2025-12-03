from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Enum,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from src.db.base import Base
from src.models.enums import UserRole, BloodGroup


class User(Base):
    """
    Handles Authentication (Login/Password).
    Minimal info here. All details go into 'Profile'.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(Enum(UserRole), default=UserRole.PENDING)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationship to Profile (One-to-One)
    profile = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class Profile(Base):
    """
    Handles User Details (Alumni/Student info).
    """

    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # --- Common Info ---
    full_name = Column(String, index=True)
    phone_number = Column(String, nullable=True)
    blood_group = Column(Enum(BloodGroup), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)

    # --- Academic Info (University) ---
    university_id = Column(String, nullable=False)  # ID card number
    department = Column(String, nullable=False)
    series = Column(String, nullable=False)  # e.g., "2018"

    # --- Alumni Specific Info (Nullable for Students) ---
    is_employed = Column(Boolean, default=False)
    current_company = Column(String, nullable=True)
    designation = Column(String, nullable=True)  # Job Title
    work_location = Column(String, nullable=True)  # City/Country of work
    linkedin_profile = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")
