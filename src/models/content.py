from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from src.db.database import Base


class Event(Base):
    """
    Events like 'Freshers Reception', 'Farewell', 'Iftar Mahfil'
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)  # events/iftar-2024
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    event_date = Column(DateTime, nullable=True)
    cover_image = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )


class Notice(Base):
    """
    Admin announcements
    """

    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Who posted this?
    author_id = Column(Integer, ForeignKey("users.id"))
