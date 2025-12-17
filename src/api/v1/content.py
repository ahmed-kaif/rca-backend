from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException

from src.api import deps
from src.models.content import Event, Notice
from src.models.enums import UserRole
from src.schemas.content import EventCreate, EventResponse, NoticeCreate, NoticeResponse

router = APIRouter()


# --- Events ---
@router.get("/events", response_model=List[EventResponse])
def read_events(
    session: deps.SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all events.
    """
    return (
        session.query(Event)
        .order_by(Event.event_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post(
    "/events",
    response_model=EventResponse,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
def create_event(
    *,
    session: deps.SessionDep,
    event_in: EventCreate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Create an event.
    """
    db_obj = Event(**event_in.model_dump())
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.get("/events/{event_id}", response_model=EventResponse)
def read_event(
    event_id: int,
    session: deps.SessionDep,
) -> Any:
    """
    Get event by ID.
    """
    return session.query(Event).filter(Event.id == event_id).first()


# --- Notices ---
@router.get("/notices", response_model=List[NoticeResponse])
def read_notices(
    session: deps.SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get public notices.
    """
    return (
        session.query(Notice)
        .filter(Notice.is_published)
        .order_by(Notice.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/notices", response_model=NoticeResponse)
def create_notice(
    *,
    session: deps.SessionDep,
    notice_in: NoticeCreate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Create a notice.
    """
    db_obj = Notice(**notice_in.model_dump(), author_id=current_user.id)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.put("/notices/{notice_id}", response_model=NoticeResponse)
def update_notice(
    *,
    session: deps.SessionDep,
    notice_id: int,
    notice_in: NoticeCreate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Update a notice.
    """
    db_obj = session.query(Notice).filter(Notice.id == notice_id).first()
    if current_user.id != db_obj.author_id or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this notice."
        )
    for field, value in notice_in.model_dump().items():
        setattr(db_obj, field, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
