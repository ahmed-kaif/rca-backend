from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from src.db.database import Base


class CommitteeSession(Base):
    """
    Represents a term/year. e.g., "Executive Committee 2024-25"
    """

    __tablename__ = "committee_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g. "EC 2024-25"
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_active = Column(
        Boolean, default=False
    )  # Admin sets this to True for the current one

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationship to members
    members = relationship("CommitteeMember", back_populates="session")


class CommitteeMember(Base):
    """
    Individual members in a specific session.
    """

    __tablename__ = "committee_members"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("committee_sessions.id"))

    # We store basic info here directly.
    # Why? Because sometimes a committee member might not have a website account
    # (especially for very old committees from history).
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)  # e.g. "President", "General Secretary"

    # Rank is used for sorting on the frontend (e.g., President=1, GS=2, Member=10)
    rank = Column(Integer, default=100)

    image_url = Column(String, nullable=True)
    facebook_link = Column(String, nullable=True)
    email = Column(String, nullable=True)

    # Optional: Link to a registered user if they exist
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    session = relationship("CommitteeSession", back_populates="members")
