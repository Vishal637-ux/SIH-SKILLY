import uuid
from datetime import datetime
from typing import Optional, List, Any, TYPE_CHECKING
from sqlalchemy import (
    String, Text, Integer, ForeignKey, text,
    CheckConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.institutions import Institution, Student
    from app.models.skills import Skill


class CommunityPost(Base, TimestampMixin):
    """Discussion threads, technical queries, resource links, and showcases."""
    __tablename__ = "community_posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    author_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    post_type: Mapped[str] = mapped_column(
        String(50),
        default="GENERAL",
        server_default=text("'GENERAL'"),
        nullable=False,
    )
    tags: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    upvotes_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_community_posts_author", "author_user_id"),
        Index("idx_community_posts_created", text("created_at DESC")),
    )

    # Relationships
    author_user: Mapped["User"] = relationship("User")
    comments: Mapped[List["CommunityComment"]] = relationship(
        "CommunityComment",
        back_populates="post",
        cascade="all, delete-orphan",
    )


class CommunityComment(Base):
    """Threaded comments and nested replies on community posts."""
    __tablename__ = "community_comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community_comments.id", ondelete="CASCADE"),
        nullable=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_community_comments_post", "post_id"),
    )

    # Relationships
    post: Mapped["CommunityPost"] = relationship("CommunityPost", back_populates="comments")
    author_user: Mapped["User"] = relationship("User")
    parent_comment: Mapped[Optional["CommunityComment"]] = relationship(
        "CommunityComment",
        remote_side=[id],
        back_populates="replies",
    )
    replies: Mapped[List["CommunityComment"]] = relationship(
        "CommunityComment",
        back_populates="parent_comment",
        cascade="all, delete-orphan",
    )


class PeerSkillRequest(Base):
    """Peer skill exchange marketplace ("I can help with X" / "I want to learn Y")."""
    __tablename__ = "peer_skill_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    requester_student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )
    helper_student_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="OPEN",
        server_default=text("'OPEN'"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_peer_skill_req_skill", "skill_id"),
        Index("idx_peer_skill_req_status", "status"),
    )

    # Relationships
    requester_student: Mapped["Student"] = relationship(
        "Student",
        back_populates="peer_skill_requests",
        foreign_keys=[requester_student_id],
    )
    helper_student: Mapped[Optional["Student"]] = relationship("Student", foreign_keys=[helper_student_id])
    skill: Mapped["Skill"] = relationship("Skill", back_populates="peer_skill_requests")


class Activity(Base):
    """Campus events, webinars, guest lectures, and departmental schedules."""
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location_or_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    conducted_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("end_time >= start_time", name="chk_activities_times"),
        Index("idx_activities_institution", "institution_id"),
        Index("idx_activities_start_time", "start_time"),
    )

    # Relationships
    institution: Mapped["Institution"] = relationship("Institution", back_populates="activities")
    conducted_by_user: Mapped[Optional["User"]] = relationship("User")
