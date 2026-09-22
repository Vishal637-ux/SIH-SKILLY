import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    String, Text, Numeric, Date, ForeignKey, text,
    CheckConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.institutions import Institution, Student
    from app.models.companies import Company
    from app.models.opportunities import Opportunity


class PlacementRecord(Base):
    """Final formal placement offers and institutional hiring records."""
    __tablename__ = "placement_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
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
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    package_lpa: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    offer_letter_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    offer_date: Mapped[date] = mapped_column(Date, nullable=False)
    joining_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="OFFERED",
        server_default=text("'OFFERED'"),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("package_lpa > 0.00", name="chk_placement_package"),
        Index("idx_placement_records_institution", "institution_id"),
        Index("idx_placement_records_student", "student_id"),
    )

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="placement_records")
    company: Mapped["Company"] = relationship("Company", back_populates="placement_records")
    opportunity: Mapped[Optional["Opportunity"]] = relationship("Opportunity", back_populates="placement_records")
    institution: Mapped["Institution"] = relationship("Institution", back_populates="placement_records")


class PlacementInteraction(Base):
    """Scheduled interviews, GDs, tests, and campus drive events."""
    __tablename__ = "placement_interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    institution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=True,
    )
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    meeting_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
        Index("idx_placement_interactions_opp", "opportunity_id"),
        Index("idx_placement_interactions_schedule", "scheduled_at"),
    )

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="placement_interactions")
    institution: Mapped[Optional["Institution"]] = relationship("Institution", back_populates="placement_interactions")
    conducted_by_user: Mapped[Optional["User"]] = relationship("User")
