import uuid
from datetime import date
from typing import Optional, Any, Dict, TYPE_CHECKING
from sqlalchemy import (
    String, Boolean, Text, Date, ForeignKey, text, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.institutions import Student
    from app.models.careers import CareerRole


class PortfolioItem(Base):
    """Project showcases, research papers, and technical deliverables on student profile."""
    __tablename__ = "portfolio_items"

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
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    repository_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    live_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role_in_project: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("FALSE"),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_portfolio_items_student", "student_id"),
    )

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="portfolio_items")


class Recognition(Base):
    """Verified digital badges, institutional honors, and hackathon certificates."""
    __tablename__ = "recognitions"

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
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer_type: Mapped[str] = mapped_column(String(50), nullable=False)
    badge_icon: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    verification_hash: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_recognitions_student", "student_id"),
    )

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="recognitions")


class ResumeVersion(Base):
    """Versioned resume uploads and structured JSON resumes for students."""
    __tablename__ = "resume_versions"

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
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_content: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    target_role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_resume_versions_student", "student_id"),
    )

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="resume_versions")
    target_role: Mapped[Optional["CareerRole"]] = relationship("CareerRole", back_populates="resume_versions")
