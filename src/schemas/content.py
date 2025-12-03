from datetime import datetime
from pydantic import BaseModel


# --- Event Schemas ---
class EventBase(BaseModel):
    title: str
    slug: str
    description: str | None = None
    location: str | None = None
    event_date: datetime | None = None
    cover_image: str | None = None


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    title: str | None = None
    slug: str | None = None


class EventResponse(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Notice Schemas ---
class NoticeBase(BaseModel):
    title: str
    content: str
    is_published: bool = True


class NoticeCreate(NoticeBase):
    pass


class NoticeUpdate(NoticeBase):
    title: str | None = None
    content: str | None = None


class NoticeResponse(NoticeBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
