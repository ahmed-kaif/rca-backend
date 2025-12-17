"""
Management commands for RCA backend.
"""

import typer
from sqlalchemy.orm import Session
from src.db.database import SessionLocal, engine
from src.models.user import User, Profile
from src.models.enums import UserRole
from src.core.security import get_password_hash
from src.db.base import Base

app = typer.Typer(help="RCA Backend Management Commands")


@app.command()
def create_admin(
    email: str = typer.Option(..., prompt=True, help="Admin email address"),
    password: str = typer.Option(
        ...,
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        help="Admin password",
    ),
    full_name: str = typer.Option(..., prompt=True, help="Full name of admin"),
    department: str = typer.Option("CSE", help="Department"),
    series: str = typer.Option("2020", help="Batch/Series"),
):
    """
    Create a new admin user.
    """
    db = SessionLocal()

    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            typer.secho(
                f"❌ User with email '{email}' already exists!", fg=typer.colors.RED
            )
            raise typer.Exit(1)

        # Create user
        admin_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

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

        typer.secho(f"\n✅ Admin user created successfully!", fg=typer.colors.GREEN)
        typer.secho(f"Email: {email}", fg=typer.colors.CYAN)
        typer.secho(f"Role: ADMIN\n", fg=typer.colors.CYAN)

    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        db.rollback()
        raise typer.Exit(1)
    finally:
        db.close()


@app.command()
def init_db():
    """
    Initialize the database (create all tables).
    """
    try:
        Base.metadata.create_all(bind=engine)
        typer.secho("✅ Database initialized successfully!", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def list_users(
    role: str = typer.Option(
        None, help="Filter by role (admin/alumni/student/pending)"
    ),
):
    """
    List all users in the system.
    """
    db = SessionLocal()

    try:
        query = db.query(User)

        if role:
            role_enum = UserRole[role.upper()]
            query = query.filter(User.role == role_enum)

        users = query.all()

        if not users:
            typer.secho("No users found.", fg=typer.colors.YELLOW)
            return

        typer.secho(
            f"\n{'Email':<30} {'Role':<10} {'Active':<8} {'Created'}",
            fg=typer.colors.CYAN,
        )
        typer.secho("-" * 70, fg=typer.colors.CYAN)

        for user in users:
            active = "✓" if user.is_active else "✗"
            created = user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A"
            typer.echo(f"{user.email:<30} {user.role.value:<10} {active:<8} {created}")

        typer.secho(f"\nTotal: {len(users)} users\n", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    app()
