from datetime import date, datetime
from pydantic import BaseModel


# --- Member Schemas ---
class CommitteeMemberBase(BaseModel):
    name: str
    position: str
    rank: int = 100
    image_url: str | None = None
    facebook_link: str | None = None
    email: str | None = None
    user_id: int | None = None


class CommitteeMemberCreate(CommitteeMemberBase):
    pass


class CommitteeMemberUpdate(CommitteeMemberBase):
    name: str | None = None
    position: str | None = None


class CommitteeMemberResponse(CommitteeMemberBase):
    id: int
    session_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Session Schemas ---
class CommitteeSessionBase(BaseModel):
    name: str
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool = False


class CommitteeSessionCreate(CommitteeSessionBase):
    pass


class CommitteeSessionUpdate(CommitteeSessionBase):
    name: str | None = None
    is_active: bool | None = None


class CommitteeSessionResponse(CommitteeSessionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Special schema to return a session WITH all its members
class CommitteeSessionDetail(CommitteeSessionResponse):
    members: list[CommitteeMemberResponse] = []
