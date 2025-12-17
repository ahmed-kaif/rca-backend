"""
Script to create an admin user for the RCA backend.
Run this script to create the first admin user.
"""

from sqlalchemy.orm import Session
from src.db.database import SessionLocal, engine
from src.models.user import User, Profile
from src.models.enums import UserRole
from src.core.security import get_password_hash
from src.db.base import Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


def create_admin_user(
    email: str,
    password: str,
    full_name: str,
    department: str = "CSE",
    series: str = "2020",
):
    """
    Create an admin user with profile.
    """
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email '{email}' already exists!")
            return

        # Create admin user
        admin_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"✅ Admin user created with email: {email}")

        # Create profile
        admin_profile = Profile(
            user_id=admin_user.id,
            full_name=full_name,
            university_id="ADMIN001",
            department=department,
            series=series,
        )
        db.add(admin_profile)
        db.commit()
        db.refresh(admin_profile)
        print(f"✅ Profile created for: {full_name}")

        print("\n" + "=" * 50)
        print("Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Role: ADMIN")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 50)
    print("RCA Backend - Admin User Creation")
    print("=" * 50 + "\n")

    # Get input from user
    if len(sys.argv) > 1:
        email = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
        full_name = sys.argv[3] if len(sys.argv) > 3 else "Admin User"
    else:
        email = (
            input("Enter admin email (default: admin@rca.com): ").strip()
            or "admin@rca.com"
        )
        password = (
            input("Enter admin password (default: admin123): ").strip() or "admin123"
        )
        full_name = (
            input("Enter full name (default: Admin User): ").strip() or "Admin User"
        )

    # Create admin user
    create_admin_user(
        email=email,
        password=password,
        full_name=full_name,
    )
