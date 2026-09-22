import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Any, Dict, TYPE_CHECKING
from sqlalchemy import (
    String, Text, Integer, Numeric, ForeignKey, text,
    UniqueConstraint, CheckConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.institutions import Institution, Student
    from app.models.companies import Company


class Competition(Base):
    """Hackathons, algorithm tournaments, and collegiate competitions."""
    __tablename__ = "competitions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    organizer_type: Mapped[str] = mapped_column(String(50), nullable=False)
    institution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="SET NULL"),
        nullable=True,
    )
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    banner_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    track_type: Mapped[str] = mapped_column(
        String(50),
        default="BOTH",
        server_default=text("'BOTH'"),
        nullable=False,
    )
    max_team_size: Mapped[int] = mapped_column(
        Integer,
        default=4,
        server_default=text("4"),
        nullable=False,
    )
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rules: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prizes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="UPCOMING",
        server_default=text("'UPCOMING'"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("max_team_size > 0", name="chk_competitions_team_size"),
        CheckConstraint("end_date >= start_date AND start_date >= registration_deadline", name="chk_competitions_dates"),
        Index("idx_competitions_slug", "slug"),
        Index("idx_competitions_status", "status"),
    )

    # Relationships
    institution: Mapped[Optional["Institution"]] = relationship("Institution", back_populates="competitions")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="competitions")
    participants: Mapped[List["CompetitionParticipant"]] = relationship(
        "CompetitionParticipant",
        back_populates="competition",
        cascade="all, delete-orphan",
    )
    teams: Mapped[List["CompetitionTeam"]] = relationship(
        "CompetitionTeam",
        back_populates="competition",
        cascade="all, delete-orphan",
    )


class CompetitionParticipant(Base):
    """Registered individual participants in a competition."""
    __tablename__ = "competition_participants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    competition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )
    registration_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )
    submission_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    award_title: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    certificate_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("competition_id", "student_id", name="uq_comp_participant"),
        Index("idx_comp_participants_comp", "competition_id"),
        Index("idx_comp_participants_student", "student_id"),
    )

    # Relationships
    competition: Mapped["Competition"] = relationship("Competition", back_populates="participants")
    student: Mapped["Student"] = relationship("Student", back_populates="competition_participants")


class CompetitionTeam(Base):
    """Multi-student teams participating in collegiate hackathons."""
    __tablename__ = "competition_teams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    competition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    team_name: Mapped[str] = mapped_column(String(150), nullable=False)
    team_leader_student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
    )
    submission_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submission_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    award_title: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("competition_id", "team_name", name="uq_comp_team_name"),
        Index("idx_comp_teams_competition", "competition_id"),
    )

    # Relationships
    competition: Mapped["Competition"] = relationship("Competition", back_populates="teams")
    team_leader: Mapped["Student"] = relationship("Student", foreign_keys=[team_leader_student_id])
    members: Mapped[List["CompetitionTeamMember"]] = relationship(
        "CompetitionTeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
    )


class CompetitionTeamMember(Base):
    """Junction mapping student members to a competition team."""
    __tablename__ = "competition_team_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competition_teams.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )
    member_role: Mapped[str] = mapped_column(
        String(50),
        default="DEVELOPER",
        server_default=text("'DEVELOPER'"),
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("team_id", "student_id", name="uq_team_student_member"),
        Index("idx_comp_team_members_team", "team_id"),
        Index("idx_comp_team_members_student", "student_id"),
    )

    # Relationships
    team: Mapped["CompetitionTeam"] = relationship("CompetitionTeam", back_populates="members")
    student: Mapped["Student"] = relationship("Student", back_populates="competition_team_memberships")
