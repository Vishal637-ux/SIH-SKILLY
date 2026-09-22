import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    String, Boolean, Text, Integer, Numeric, ForeignKey, text,
    UniqueConstraint, CheckConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.institutions import Student
    from app.models.skills import Skill
    from app.models.portfolio import ResumeVersion


class CareerRole(Base):
    """Standardized target career benchmark definitions."""
    __tablename__ = "career_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    title: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    industry_domain: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
        Index("idx_career_roles_slug", "slug"),
    )

    # Relationships
    students: Mapped[List["Student"]] = relationship(
        "Student",
        back_populates="target_career_role",
    )
    role_skills: Mapped[List["CareerRoleSkill"]] = relationship(
        "CareerRoleSkill",
        back_populates="career_role",
        cascade="all, delete-orphan",
    )
    skill_gaps: Mapped[List["SkillGap"]] = relationship(
        "SkillGap",
        back_populates="career_role",
        cascade="all, delete-orphan",
    )
    roadmaps: Mapped[List["Roadmap"]] = relationship(
        "Roadmap",
        back_populates="career_role",
    )
    resume_versions: Mapped[List["ResumeVersion"]] = relationship(
        "ResumeVersion",
        back_populates="target_role",
    )


class CareerRoleSkill(Base):
    """Skills required to qualify for a specific career role."""
    __tablename__ = "career_role_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    career_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False,
    )
    required_level: Mapped[str] = mapped_column(String(50), nullable=False)
    importance_level: Mapped[str] = mapped_column(
        String(50),
        default="CORE",
        server_default=text("'CORE'"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("career_role_id", "skill_id", name="uq_career_role_skill"),
        Index("idx_career_role_skills_role", "career_role_id"),
    )

    # Relationships
    career_role: Mapped["CareerRole"] = relationship("CareerRole", back_populates="role_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="career_role_skills")


class SkillGap(Base):
    """Calculated competency gaps between a student and their target career role."""
    __tablename__ = "skill_gaps"

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
    career_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False,
    )
    current_level: Mapped[str] = mapped_column(
        String(50),
        default="NONE",
        server_default=text("'NONE'"),
        nullable=False,
    )
    target_level: Mapped[str] = mapped_column(String(50), nullable=False)
    gap_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    calculated_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("student_id", "career_role_id", "skill_id", name="uq_student_role_skill_gap"),
        Index("idx_skill_gaps_student_role", "student_id", "career_role_id"),
    )

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="skill_gaps")
    career_role: Mapped["CareerRole"] = relationship("CareerRole", back_populates="skill_gaps")
    skill: Mapped["Skill"] = relationship("Skill")


class Roadmap(Base, TimestampMixin):
    """Active personalized career progression roadmap for a student."""
    __tablename__ = "roadmaps"

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
    career_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        server_default=text("'ACTIVE'"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_roadmaps_student", "student_id"),
    )

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="roadmaps")
    career_role: Mapped["CareerRole"] = relationship("CareerRole", back_populates="roadmaps")
    items: Mapped[List["RoadmapItem"]] = relationship(
        "RoadmapItem",
        back_populates="roadmap",
        cascade="all, delete-orphan",
    )


class RoadmapItem(Base):
    """Individual milestone checkpoints within a roadmap."""
    __tablename__ = "roadmap_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resource_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        server_default=text("'PENDING'"),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("roadmap_id", "step_order", name="uq_roadmap_item_order"),
        CheckConstraint("estimated_hours IS NULL OR estimated_hours >= 0", name="chk_roadmap_items_hours"),
        Index("idx_roadmap_items_roadmap", "roadmap_id"),
    )

    # Relationships
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="items")
    skill: Mapped[Optional["Skill"]] = relationship("Skill")
