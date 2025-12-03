from typing import Any, List
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import joinedload

from src.api import deps
from src.models.committee import CommitteeSession, CommitteeMember
from src.schemas.committee import (
    CommitteeSessionCreate,
    CommitteeSessionResponse,
    CommitteeSessionDetail,
    CommitteeMemberCreate,
    CommitteeMemberResponse,
)

router = APIRouter()


@router.get("/active", response_model=CommitteeSessionDetail)
def get_active_committee(
    session: deps.SessionDep,
) -> Any:
    """
    Get the currently active committee and its members.
    """
    committee = (
        session.query(CommitteeSession)
        .filter(CommitteeSession.is_active)
        .options(joinedload(CommitteeSession.members))
        .first()
    )
    if not committee:
        raise HTTPException(status_code=404, detail="No active committee found")
    return committee


@router.post("/sessions", response_model=CommitteeSessionResponse)
def create_committee_session(
    *,
    session: deps.SessionDep,
    committee_in: CommitteeSessionCreate,
    current_user: deps.CurrentUser,  # Protected: Logged in users only
) -> Any:
    """
    Create a new committee year (e.g. "2024-25").
    Only Admins should arguably do this, but keeping it simple for now.
    """
    # If admin check is needed: deps.get_current_active_superuser

    # If setting to active, deactivate others
    if committee_in.is_active:
        session.query(CommitteeSession).update({CommitteeSession.is_active: False})
        session.commit()

    db_obj = CommitteeSession(**committee_in.model_dump())
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.post("/members", response_model=CommitteeMemberResponse)
def add_committee_member(
    *,
    session: deps.SessionDep,
    member_in: CommitteeMemberCreate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Add a member to a committee session.
    """
    db_obj = CommitteeMember(**member_in.model_dump())
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.get("/history", response_model=List[CommitteeSessionResponse])
def get_committee_history(
    session: deps.SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get list of past committees.
    """
    return (
        session.query(CommitteeSession)
        .order_by(CommitteeSession.start_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
