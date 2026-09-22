import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    String, Boolean, Text, ForeignKey, text, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.opportunities import Opportunity
    from app.models.training import TrainingProgram
    from app.models.internships import Internship
    from app.models.placements import PlacementRecord
    from app.models.assessments import Assessment
    from app.models.competitions import Competition


class Company(Base):
    """Master corporate and employer profile."""
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    industry_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    headquarters: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(
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
        Index("idx_companies_name", "name"),
        Index("idx_companies_industry_type", "industry_type"),
    )

    # Relationships
    company_users: Mapped[List["CompanyUser"]] = relationship(
        "CompanyUser",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    opportunities: Mapped[List["Opportunity"]] = relationship(
        "Opportunity",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    training_programs: Mapped[List["TrainingProgram"]] = relationship(
        "TrainingProgram",
        back_populates="company",
    )
    internships: Mapped[List["Internship"]] = relationship(
        "Internship",
        back_populates="company",
    )
    placement_records: Mapped[List["PlacementRecord"]] = relationship(
        "PlacementRecord",
        back_populates="company",
    )
    assessments: Mapped[List["Assessment"]] = relationship(
        "Assessment",
        back_populates="company",
    )
    competitions: Mapped[List["Competition"]] = relationship(
        "Competition",
        back_populates="company",
    )


class CompanyUser(Base):
    """Recruiter, hiring manager, and interviewer staff associated with a company."""
    __tablename__ = "company_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    hr_role: Mapped[str] = mapped_column(
        String(50),
        default="RECRUITER",
        server_default=text("'RECRUITER'"),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_company_users_company_id", "company_id"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="company_user_profile")
    company: Mapped["Company"] = relationship("Company", back_populates="company_users")
