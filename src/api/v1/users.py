from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from io import BytesIO
import csv
import secrets
import string
from src.api import deps
from src.core import security
from src.models.user import User, Profile
from src.models.enums import UserRole, BloodGroup
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

    # Create Empty Profile for the user automatically with required fields
    db_profile = Profile(
        user_id=db_user.id,
        full_name=user_in.email.split("@")[0],
        university_id="",  # Will be updated by user later
        department="",  # Will be updated by user later
        series="",  # Will be updated by user later
    )
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)

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
    # Query profile directly from database to avoid stale data
    profile = session.query(Profile).filter(Profile.user_id == current_user.id).first()

    if not profile:
        # Create profile if it doesn't exist (safety check)
        profile = Profile(
            user_id=current_user.id,
            full_name=current_user.email.split("@")[0],
            university_id="",
            department="",
            series="",
        )
        session.add(profile)
        session.flush()

    # Update profile fields
    profile_data = profile_in.model_dump(exclude_unset=True)
    for field, value in profile_data.items():
        setattr(profile, field, value)

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
def delete_user(
    *,
    session: deps.SessionDep,
    user_id: int,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Delete a user by ID.
    Admin only endpoint.
    """
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.query(Profile).filter(Profile.user_id == user.id).delete()
    session.commit()
    session.delete(user)
    session.commit()
    return user


@router.get("/", response_model=List[UserResponse])
def read_users(
    session: deps.SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    users = session.query(User).offset(skip).limit(limit).all()
    return users


@router.post(
    "/bulk-upload-alumni", dependencies=[Depends(deps.get_current_active_superuser)]
)
async def bulk_upload_alumni(
    session: deps.SessionDep,
    file: UploadFile = File(...),
) -> Any:
    """
    Bulk upload alumni from CSV or Excel file.
    Admin only endpoint.

    Required columns:
    - full_name (required)
    - series (required - graduation year/batch)

    Auto-generated if missing:
    - email (generated from name and series if missing)
    - password (random password generated if missing)

    Optional columns:
    - phone_number, blood_group, department, university_id
    - is_employed, current_company, designation
    - work_location, linkedin_profile

    Note: Auto-generated credentials will be returned in the response
    """
    # Check file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = file.filename.lower().split(".")[-1]
    if file_ext not in ["csv", "xlsx", "xls"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload CSV or Excel file.",
        )

    # Read file content
    content = await file.read()

    results = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "errors": [],
        "created_users": [],
        "auto_generated_credentials": [],
    }

    def generate_email(full_name: str, series: str, university_id: str = "") -> str:
        """Generate email from name and series"""
        # Use university_id if available, otherwise use name
        if university_id:
            base = university_id.lower()
        else:
            # Take first name and last name
            name_parts = full_name.lower().strip().split()
            if len(name_parts) >= 2:
                base = f"{name_parts[0]}.{name_parts[-1]}"
            else:
                base = name_parts[0] if name_parts else "alumni"

        email = f"{base}.{series}@alumni.rca.com"

        # Check if email exists, add number if needed
        counter = 1
        original_email = email
        while session.query(User).filter(User.email == email).first():
            email = f"{base}.{series}.{counter}@alumni.rca.com"
            counter += 1
            if counter > 100:  # Safety limit
                email = f"{base}.{secrets.token_hex(4)}@alumni.rca.com"
                break

        return email

    def generate_password(length: int = 12) -> str:
        """Generate a random secure password"""
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        return password

    try:
        if file_ext == "csv":
            # Parse CSV
            csv_content = content.decode("utf-8")
            csv_reader = csv.DictReader(csv_content.splitlines())
            rows = list(csv_reader)
        else:
            # Parse Excel
            try:
                import openpyxl
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="Excel support not installed. Please use CSV or install openpyxl.",
                )

            workbook = openpyxl.load_workbook(BytesIO(content))
            sheet = workbook.active

            # Get headers from first row
            headers = [cell.value for cell in sheet[1]]

            # Convert to list of dicts
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if any(row):  # Skip empty rows
                    row_dict = {
                        headers[i]: row[i] for i in range(len(headers)) if i < len(row)
                    }
                    rows.append(row_dict)

        results["total"] = len(rows)

        # Process each row
        for idx, row in enumerate(rows, start=1):
            try:
                # Get values with defaults
                full_name = str(row.get("full_name", "")).strip()
                series = str(row.get("series", "")).strip()
                university_id = str(row.get("university_id", "")).strip()

                # Validate minimum required fields
                if not full_name or not series:
                    results["errors"].append(
                        {
                            "row": idx,
                            "error": "Missing required fields: full_name and series are mandatory",
                            "data": {"full_name": full_name, "series": series},
                        }
                    )
                    results["failed"] += 1
                    continue

                # Get or generate email
                email = str(row.get("email", "")).strip()
                email_generated = False
                if not email:
                    email = generate_email(full_name, series, university_id)
                    email_generated = True

                # Check if user already exists
                existing = session.query(User).filter(User.email == email).first()
                if existing:
                    results["errors"].append(
                        {"row": idx, "email": email, "error": "User already exists"}
                    )
                    results["failed"] += 1
                    continue

                # Get or generate password
                password = str(row.get("password", "")).strip()
                password_generated = False
                if not password:
                    password = generate_password()
                    password_generated = True

                # Parse blood group if provided
                blood_group = None
                blood_group_str = str(row.get("blood_group", "")).strip()
                if blood_group_str:
                    try:
                        # Convert A+ to A_POS format
                        bg_map = {
                            "A+": "A_POS",
                            "A-": "A_NEG",
                            "B+": "B_POS",
                            "B-": "B_NEG",
                            "O+": "O_POS",
                            "O-": "O_NEG",
                            "AB+": "AB_POS",
                            "AB-": "AB_NEG",
                        }
                        blood_group = BloodGroup[
                            bg_map.get(blood_group_str, blood_group_str.upper())
                        ]
                    except (KeyError, ValueError):
                        pass  # Ignore invalid blood group

                # Parse is_employed
                is_employed_str = str(row.get("is_employed", "false")).strip().lower()
                is_employed = is_employed_str in ["true", "yes", "1", "t", "y"]

                # Create User
                new_user = User(
                    email=email,
                    hashed_password=security.get_password_hash(password),
                    role=UserRole.ALUMNI,
                    is_active=True,
                )
                session.add(new_user)
                session.flush()

                # Create Profile
                new_profile = Profile(
                    user_id=new_user.id,
                    full_name=full_name,
                    phone_number=str(row.get("phone_number", "")).strip() or None,
                    blood_group=blood_group,
                    university_id=university_id or "",
                    department=str(row.get("department", "")).strip() or "",
                    series=series,
                    is_employed=is_employed,
                    current_company=str(row.get("current_company", "")).strip() or None,
                    designation=str(row.get("designation", "")).strip() or None,
                    work_location=str(row.get("work_location", "")).strip() or None,
                    linkedin_profile=str(row.get("linkedin_profile", "")).strip()
                    or None,
                )
                session.add(new_profile)
                session.flush()

                results["success"] += 1
                user_info = {"email": email, "full_name": full_name, "series": series}
                results["created_users"].append(user_info)

                # Track auto-generated credentials
                if email_generated or password_generated:
                    cred_info = {
                        "row": idx,
                        "email": email,
                        "full_name": full_name,
                    }
                    if email_generated:
                        cred_info["email_generated"] = True
                    if password_generated:
                        cred_info["password"] = password  # Include generated password
                        cred_info["password_generated"] = True
                    results["auto_generated_credentials"].append(cred_info)

            except Exception as e:
                results["errors"].append(
                    {"row": idx, "email": row.get("email", "N/A"), "error": str(e)}
                )
                results["failed"] += 1

        # Commit all changes
        if results["success"] > 0:
            session.commit()

        return results

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
