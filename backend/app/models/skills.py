import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    String, Boolean, Text, Numeric, ForeignKey, text,
    UniqueConstraint, CheckConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.institutions import Student
    from app.models.users import User
    from app.models.careers import CareerRoleSkill, SkillGap, RoadmapItem
    from app.models.assessments import Assessment
    from app.models.opportunities import OpportunitySkill
    from app.models.community import PeerSkillRequest


class Skill(Base):
    """Authoritative master dictionary of all technical and soft skills."""
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(
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
        Index("idx_skills_slug", "slug"),
        Index("idx_skills_category", "category"),
    )

    # Relationships
    parent_relationships: Mapped[List["SkillRelationship"]] = relationship(
        "SkillRelationship",
        back_populates="parent_skill",
        foreign_keys="[SkillRelationship.parent_skill_id]",
        cascade="all, delete-orphan",
    )
    child_relationships: Mapped[List["SkillRelationship"]] = relationship(
        "SkillRelationship",
        back_populates="child_skill",
        foreign_keys="[SkillRelationship.child_skill_id]",
        cascade="all, delete-orphan",
    )
    student_skills: Mapped[List["StudentSkill"]] = relationship(
        "StudentSkill",
        back_populates="skill",
    )
    career_role_skills: Mapped[List["CareerRoleSkill"]] = relationship(
        "CareerRoleSkill",
        back_populates="skill",
    )
    opportunity_skills: Mapped[List["OpportunitySkill"]] = relationship(
        "OpportunitySkill",
        back_populates="skill",
    )
    assessments: Mapped[List["Assessment"]] = relationship(
        "Assessment",
        back_populates="target_skill",
    )
    peer_skill_requests: Mapped[List["PeerSkillRequest"]] = relationship(
        "PeerSkillRequest",
        back_populates="skill",
    )


class SkillRelationship(Base):
    """Directed Skill Relationship Graph linking prerequisite, related, and specialized skills."""
    __tablename__ = "skill_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    parent_skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
    )
    child_skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("parent_skill_id", "child_skill_id", "relationship_type", name="uq_skill_relationship"),
        CheckConstraint("parent_skill_id != child_skill_id", name="chk_no_self_relationship"),
        Index("idx_skill_rel_parent", "parent_skill_id"),
        Index("idx_skill_rel_child", "child_skill_id"),
    )

    # Relationships
    parent_skill: Mapped["Skill"] = relationship(
        "Skill",
        back_populates="parent_relationships",
        foreign_keys=[parent_skill_id],
    )
    child_skill: Mapped["Skill"] = relationship(
        "Skill",
        back_populates="child_relationships",
        foreign_keys=[child_skill_id],
    )


class StudentSkill(Base, TimestampMixin):
    """Current assessed and self-reported competencies for individual students."""
    __tablename__ = "student_skills"

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
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False,
    )
    proficiency_level: Mapped[str] = mapped_column(
        String(50),
        default="BEGINNER",
        server_default=text("'BEGINNER'"),
        nullable=False,
    )
    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="SELF_REPORTED",
        server_default=text("'SELF_REPORTED'"),
        nullable=False,
    )
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    last_assessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("student_id", "skill_id", name="uq_student_skill"),
        CheckConstraint("score IS NULL OR (score >= 0.00 AND score <= 100.00)", name="chk_student_skills_score"),
        CheckConstraint("confidence_score IS NULL OR (confidence_score >= 0.00 AND confidence_score <= 1.00)", name="chk_student_skills_conf"),
        Index("idx_student_skills_lookup", "student_id", "skill_id"),
        Index("idx_student_skills_status", "verification_status"),
    )

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="student_skills")
    evidence: Mapped[List["SkillEvidence"]] = relationship(
        "SkillEvidence",
        back_populates="student_skill",
        cascade="all, delete-orphan",
    )


class SkillEvidence(Base):
    """Verified digital evidence backing evaluated student skills."""
    __tablename__ = "skill_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    student_skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_skills.id", ondelete="CASCADE"),
        nullable=False,
    )
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_skill_evidence_student_skill", "student_skill_id"),
        Index("idx_skill_evidence_ref", "evidence_type", "reference_id"),
    )

    # Relationships
    student_skill: Mapped["StudentSkill"] = relationship("StudentSkill", back_populates="evidence")
    verified_by_user: Mapped[Optional["User"]] = relationship("User")
