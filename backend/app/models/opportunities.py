import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict, TYPE_CHECKING
from sqlalchemy import (
    String, Boolean, Text, Integer, ForeignKey, text,
    UniqueConstraint, CheckConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.companies import Company
    from app.models.skills import Skill
    from app.models.institutions import Student
    from app.models.portfolio import ResumeVersion
    from app.models.internships import Internship
    from app.models.placements import PlacementRecord, PlacementInteraction


class Opportunity(Base, TimestampMixin):
    """Job, internship, and live project postings created by employers."""
    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    role_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    is_remote: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("FALSE"),
        nullable=False,
    )
    stipend_salary: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    duration_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    openings_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default=text("1"),
        nullable=False,
    )
    eligibility_criteria: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    application_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="OPEN",
        server_default=text("'OPEN'"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("openings_count > 0", name="chk_opportunities_openings"),
        CheckConstraint("duration_months IS NULL OR duration_months > 0", name="chk_opportunities_duration"),
        Index("idx_opportunities_company", "company_id"),
        Index("idx_opportunities_status_deadline", "status", "application_deadline"),
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="opportunities")
    required_skills: Mapped[List["OpportunitySkill"]] = relationship(
        "OpportunitySkill",
        back_populates="opportunity",
        cascade="all, delete-orphan",
    )
    applications: Mapped[List["Application"]] = relationship(
        "Application",
        back_populates="opportunity",
        cascade="all, delete-orphan",
    )
    internships: Mapped[List["Internship"]] = relationship(
        "Internship",
        back_populates="opportunity",
    )
    placement_records: Mapped[List["PlacementRecord"]] = relationship(
        "PlacementRecord",
        back_populates="opportunity",
    )
    placement_interactions: Mapped[List["PlacementInteraction"]] = relationship(
        "PlacementInteraction",
        back_populates="opportunity",
        cascade="all, delete-orphan",
    )


class OpportunitySkill(Base):
    """Mandatory and preferred skills attached to an opportunity."""
    __tablename__ = "opportunity_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False,
    )
    required_proficiency: Mapped[str] = mapped_column(
        String(50),
        default="INTERMEDIATE",
        server_default=text("'INTERMEDIATE'"),
        nullable=False,
    )
    is_mandatory: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("TRUE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("opportunity_id", "skill_id", name="uq_opportunity_skill"),
        Index("idx_opp_skills_opp_id", "opportunity_id"),
    )

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="required_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="opportunity_skills")


class Application(Base, TimestampMixin):
    """Student application submitted to an opportunity."""
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_status: Mapped[str] = mapped_column(
        String(50),
        default="APPLIED",
        server_default=text("'APPLIED'"),
        nullable=False,
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("opportunity_id", "student_id", name="uq_student_opportunity_application"),
        Index("idx_applications_student", "student_id"),
        Index("idx_applications_opportunity_status", "opportunity_id", "current_status"),
    )

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="applications")
    student: Mapped["Student"] = relationship("Student", back_populates="applications")
    resume_version: Mapped[Optional["ResumeVersion"]] = relationship("ResumeVersion")
    status_history: Mapped[List["ApplicationStatusHistory"]] = relationship(
        "ApplicationStatusHistory",
        back_populates="application",
        cascade="all, delete-orphan",
    )


class ApplicationStatusHistory(Base):
    """Append-only immutable audit log of candidate stage movements through ATS."""
    __tablename__ = "application_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_app_status_hist_application", "application_id"),
    )

    # Relationships
    application: Mapped["Application"] = relationship("Application", back_populates="status_history")
    changed_by_user: Mapped["User"] = relationship("User")
