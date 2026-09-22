import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Any, Dict, TYPE_CHECKING
from sqlalchemy import (
    String, Boolean, Text, Integer, Numeric, ForeignKey, text,
    CheckConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.companies import Company
    from app.models.skills import Skill
    from app.models.institutions import Student


class Assessment(Base):
    """Diagnostic tests, technical quizzes, and coding challenges."""
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_skill_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assessment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    passing_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("60.00"),
        server_default=text("60.00"),
        nullable=False,
    )
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("TRUE"),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("passing_score >= 0.00 AND passing_score <= 100.00", name="chk_assessments_passing_score"),
        CheckConstraint("duration_minutes > 0", name="chk_assessments_duration"),
        CheckConstraint("total_questions > 0", name="chk_assessments_total_q"),
        Index("idx_assessments_skill", "target_skill_id"),
        Index("idx_assessments_company", "company_id"),
    )

    # Relationships
    target_skill: Mapped[Optional["Skill"]] = relationship("Skill", back_populates="assessments")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="assessments")
    created_by_user: Mapped["User"] = relationship("User")
    questions: Mapped[List["AssessmentQuestion"]] = relationship(
        "AssessmentQuestion",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
    attempts: Mapped[List["AssessmentAttempt"]] = relationship(
        "AssessmentAttempt",
        back_populates="assessment",
    )


class AssessmentQuestion(Base):
    """Question bank items belonging to an assessment."""
    __tablename__ = "assessment_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)
    options: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    points: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default=text("1"),
        nullable=False,
    )
    question_order: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("points > 0", name="chk_assessment_questions_points"),
        Index("idx_assessment_questions_assessment", "assessment_id"),
    )

    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="questions")


class AssessmentAttempt(Base):
    """Student test session execution and grading record with immutable JSONB responses."""
    __tablename__ = "assessment_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    is_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    responses: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint("score >= 0.00", name="chk_assessment_attempts_score"),
        CheckConstraint("percentage >= 0.00 AND percentage <= 100.00", name="chk_assessment_attempts_pct"),
        Index("idx_assessment_attempts_student", "student_id"),
        Index("idx_assessment_attempts_assessment", "assessment_id"),
    )

    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="attempts")
    student: Mapped["Student"] = relationship("Student", back_populates="assessment_attempts")
