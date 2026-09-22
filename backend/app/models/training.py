import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    String, Text, Integer, Numeric, Date, ForeignKey, text,
    UniqueConstraint, CheckConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.institutions import Institution, Student
    from app.models.companies import Company


class TrainingProgram(Base):
    """Structured training bootcamps, workshops, and faculty development programs."""
    __tablename__ = "training_programs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    program_type: Mapped[str] = mapped_column(String(50), nullable=False)
    institution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
    )
    conducted_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="UPCOMING",
        server_default=text("'UPCOMING'"),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_training_programs_dates"),
        CheckConstraint("capacity IS NULL OR capacity > 0", name="chk_training_programs_capacity"),
        Index("idx_training_programs_institution", "institution_id"),
        Index("idx_training_programs_dates", "start_date", "end_date"),
    )

    # Relationships
    institution: Mapped[Optional["Institution"]] = relationship("Institution", back_populates="training_programs")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="training_programs")
    conducted_by_user: Mapped["User"] = relationship("User")
    enrollments: Mapped[List["TrainingEnrollment"]] = relationship(
        "TrainingEnrollment",
        back_populates="training_program",
        cascade="all, delete-orphan",
    )


class TrainingEnrollment(Base):
    """Student participation and completion tracking in training programs."""
    __tablename__ = "training_enrollments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    training_program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_programs.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enrollment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )
    attendance_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        server_default=text("0.00"),
        nullable=False,
    )
    completion_status: Mapped[str] = mapped_column(
        String(50),
        default="ENROLLED",
        server_default=text("'ENROLLED'"),
        nullable=False,
    )
    certificate_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("training_program_id", "student_id", name="uq_training_enrollment"),
        CheckConstraint("attendance_percentage >= 0.00 AND attendance_percentage <= 100.00", name="chk_training_enrollments_att"),
        Index("idx_training_enrollments_student", "student_id"),
    )

    # Relationships
    training_program: Mapped["TrainingProgram"] = relationship("TrainingProgram", back_populates="enrollments")
    student: Mapped["Student"] = relationship("Student", back_populates="training_enrollments")
