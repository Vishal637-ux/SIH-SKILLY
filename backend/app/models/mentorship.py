import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    String, Text, Integer, ForeignKey, text,
    UniqueConstraint, CheckConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.institutions import Student


class MentorConnection(Base):
    """Established 1-on-1 mentorship link between a student and an alumnus/mentor."""
    __tablename__ = "mentor_connections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mentor_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        server_default=text("'PENDING'"),
        nullable=False,
    )
    request_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("student_id", "mentor_user_id", name="uq_student_mentor_connection"),
        Index("idx_mentor_conn_student", "student_id"),
        Index("idx_mentor_conn_mentor", "mentor_user_id"),
    )

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="mentor_connections")
    mentor_user: Mapped["User"] = relationship("User", foreign_keys=[mentor_user_id])
    sessions: Mapped[List["MentorshipSession"]] = relationship(
        "MentorshipSession",
        back_populates="connection",
        cascade="all, delete-orphan",
    )


class MentorshipSession(Base):
    """Individual scheduled interaction sessions under a mentor connection."""
    __tablename__ = "mentorship_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mentor_connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=45,
        server_default=text("45"),
        nullable=False,
    )
    meeting_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="SCHEDULED",
        server_default=text("'SCHEDULED'"),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("feedback_rating IS NULL OR (feedback_rating >= 1 AND feedback_rating <= 5)", name="chk_session_feedback"),
        CheckConstraint("duration_minutes > 0", name="chk_session_duration"),
        Index("idx_mentorship_sessions_conn", "connection_id"),
        Index("idx_mentorship_sessions_time", "scheduled_at"),
    )

    # Relationships
    connection: Mapped["MentorConnection"] = relationship("MentorConnection", back_populates="sessions")
