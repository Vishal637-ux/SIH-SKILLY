import uuid
from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    String, Boolean, Text, Integer, Date, ForeignKey, text,
    UniqueConstraint, CheckConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.institutions import Student
    from app.models.companies import Company
    from app.models.opportunities import Opportunity


class Internship(Base):
    """Active/completed internship contract agreements."""
    __tablename__ = "internships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    opportunity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="SET NULL"),
        nullable=True,
    )
    supervisor_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    supervisor_name: Mapped[str] = mapped_column(String(150), nullable=False)
    supervisor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    stipend: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="ONGOING",
        server_default=text("'ONGOING'"),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_internships_dates"),
        Index("idx_internships_student", "student_id"),
        Index("idx_internships_company", "company_id"),
        Index("idx_internships_supervisor", "supervisor_user_id"),
    )

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="internships")
    company: Mapped["Company"] = relationship("Company", back_populates="internships")
    opportunity: Mapped[Optional["Opportunity"]] = relationship("Opportunity", back_populates="internships")
    supervisor_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="supervised_internships",
        foreign_keys=[supervisor_user_id],
    )
    progress_reports: Mapped[List["InternshipProgress"]] = relationship(
        "InternshipProgress",
        back_populates="internship",
        cascade="all, delete-orphan",
    )
    evaluation: Mapped[Optional["InternshipEvaluation"]] = relationship(
        "InternshipEvaluation",
        back_populates="internship",
        uselist=False,
        cascade="all, delete-orphan",
    )


class InternshipProgress(Base):
    """Periodic milestone submissions and weekly logs by the intern."""
    __tablename__ = "internship_progress"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    internship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("internships.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    report_text: Mapped[str] = mapped_column(Text, nullable=False)
    mentor_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("internship_id", "week_number", name="uq_internship_week_report"),
        CheckConstraint("week_number > 0", name="chk_internship_progress_week"),
        Index("idx_internship_progress_internship", "internship_id"),
    )

    # Relationships
    internship: Mapped["Internship"] = relationship("Internship", back_populates="progress_reports")


class InternshipEvaluation(Base):
    """Formal performance and rubric evaluation from industry supervisors."""
    __tablename__ = "internship_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    internship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("internships.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    evaluator_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    technical_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    soft_skills_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    punctuality_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("TRUE"),
        nullable=False,
    )
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("technical_rating BETWEEN 1 AND 5", name="chk_eval_tech_rating"),
        CheckConstraint("soft_skills_rating BETWEEN 1 AND 5", name="chk_eval_soft_rating"),
        CheckConstraint("punctuality_rating BETWEEN 1 AND 5", name="chk_eval_punc_rating"),
        Index("idx_internship_evaluations_internship", "internship_id"),
    )

    # Relationships
    internship: Mapped["Internship"] = relationship("Internship", back_populates="evaluation")
    evaluator_user: Mapped[Optional["User"]] = relationship("User")
