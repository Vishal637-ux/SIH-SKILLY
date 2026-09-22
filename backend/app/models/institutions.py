import uuid
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    String, Boolean, Text, Integer, Numeric, ForeignKey, text,
    UniqueConstraint, ForeignKeyConstraint, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.careers import CareerRole, SkillGap, Roadmap
    from app.models.skills import StudentSkill
    from app.models.assessments import AssessmentAttempt
    from app.models.training import TrainingProgram, TrainingEnrollment
    from app.models.opportunities import Application
    from app.models.internships import Internship
    from app.models.placements import PlacementRecord, PlacementInteraction
    from app.models.portfolio import PortfolioItem, Recognition, ResumeVersion
    from app.models.mentorship import MentorConnection
    from app.models.community import PeerSkillRequest, Activity
    from app.models.competitions import Competition, CompetitionParticipant, CompetitionTeam, CompetitionTeamMember


class Institution(Base):
    """Master catalog of partner colleges, universities, and academic institutions."""
    __tablename__ = "institutions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    institution_type: Mapped[str] = mapped_column(
        String(50),
        default="COLLEGE",
        server_default=text("'COLLEGE'"),
        nullable=False,
    )
    website: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(
        String(100),
        default="India",
        server_default=text("'India'"),
        nullable=False,
    )
    is_accredited: Mapped[bool] = mapped_column(
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
        Index("idx_institutions_code", "code"),
        Index("idx_institutions_state_city", "state", "city"),
    )

    # Relationships
    departments: Mapped[List["Department"]] = relationship(
        "Department",
        back_populates="institution",
        cascade="all, delete-orphan",
    )
    students: Mapped[List["Student"]] = relationship(
        "Student",
        back_populates="institution",
        foreign_keys="[Student.institution_id]",
    )
    teachers: Mapped[List["Teacher"]] = relationship(
        "Teacher",
        back_populates="institution",
        foreign_keys="[Teacher.institution_id]",
    )
    staff_members: Mapped[List["InstitutionStaff"]] = relationship(
        "InstitutionStaff",
        back_populates="institution",
        cascade="all, delete-orphan",
    )
    training_programs: Mapped[List["TrainingProgram"]] = relationship(
        "TrainingProgram",
        back_populates="institution",
    )
    placement_records: Mapped[List["PlacementRecord"]] = relationship(
        "PlacementRecord",
        back_populates="institution",
    )
    placement_interactions: Mapped[List["PlacementInteraction"]] = relationship(
        "PlacementInteraction",
        back_populates="institution",
    )
    activities: Mapped[List["Activity"]] = relationship(
        "Activity",
        back_populates="institution",
        cascade="all, delete-orphan",
    )
    competitions: Mapped[List["Competition"]] = relationship(
        "Competition",
        back_populates="institution",
    )


class Department(Base):
    """Academic departments within an institution."""
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("institution_id", "code", name="uq_institution_department_code"),
        UniqueConstraint("institution_id", "id", name="uq_institution_department_id"),
        Index("idx_departments_institution_id", "institution_id"),
    )

    # Relationships
    institution: Mapped["Institution"] = relationship("Institution", back_populates="departments")
    students: Mapped[List["Student"]] = relationship(
        "Student",
        back_populates="department",
        foreign_keys="[Student.institution_id, Student.department_id]",
    )
    teachers: Mapped[List["Teacher"]] = relationship(
        "Teacher",
        back_populates="department",
        foreign_keys="[Teacher.institution_id, Teacher.department_id]",
    )


class Student(Base, TimestampMixin):
    """Student domain profile storing academic metrics and career objectives."""
    __tablename__ = "students"

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
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    roll_number: Mapped[str] = mapped_column(String(50), nullable=False)
    enrollment_year: Mapped[int] = mapped_column(Integer, nullable=False)
    graduation_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    current_semester: Mapped[int] = mapped_column(Integer, nullable=False)
    cgpa: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    target_career_role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        UniqueConstraint("institution_id", "roll_number", name="uq_institution_student_roll"),
        ForeignKeyConstraint(
            ["institution_id", "department_id"],
            ["departments.institution_id", "departments.id"],
            name="fk_student_institution_dept",
            ondelete="RESTRICT",
        ),
        CheckConstraint("current_semester > 0", name="chk_students_semester"),
        CheckConstraint("cgpa IS NULL OR (cgpa >= 0.00 AND cgpa <= 10.00)", name="chk_students_cgpa"),
        CheckConstraint("graduation_year >= enrollment_year", name="chk_students_graduation"),
        Index("idx_students_institution_dept", "institution_id", "department_id"),
        Index("idx_students_graduation_year", "graduation_year"),
        Index("idx_students_target_role", "target_career_role_id"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="student_profile")
    institution: Mapped["Institution"] = relationship(
        "Institution",
        back_populates="students",
        foreign_keys=[institution_id],
    )
    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="students",
        foreign_keys=[institution_id, department_id],
        primaryjoin="and_(Student.institution_id == Department.institution_id, Student.department_id == Department.id)",
    )
    target_career_role: Mapped[Optional["CareerRole"]] = relationship("CareerRole", back_populates="students")
    skills: Mapped[List["StudentSkill"]] = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    skill_gaps: Mapped[List["SkillGap"]] = relationship("SkillGap", back_populates="student", cascade="all, delete-orphan")
    roadmaps: Mapped[List["Roadmap"]] = relationship("Roadmap", back_populates="student", cascade="all, delete-orphan")
    assessment_attempts: Mapped[List["AssessmentAttempt"]] = relationship("AssessmentAttempt", back_populates="student", cascade="all, delete-orphan")
    training_enrollments: Mapped[List["TrainingEnrollment"]] = relationship("TrainingEnrollment", back_populates="student", cascade="all, delete-orphan")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="student", cascade="all, delete-orphan")
    internships: Mapped[List["Internship"]] = relationship("Internship", back_populates="student", cascade="all, delete-orphan")
    placement_records: Mapped[List["PlacementRecord"]] = relationship("PlacementRecord", back_populates="student")
    portfolio_items: Mapped[List["PortfolioItem"]] = relationship("PortfolioItem", back_populates="student", cascade="all, delete-orphan")
    recognitions: Mapped[List["Recognition"]] = relationship("Recognition", back_populates="student", cascade="all, delete-orphan")
    resume_versions: Mapped[List["ResumeVersion"]] = relationship("ResumeVersion", back_populates="student", cascade="all, delete-orphan")
    mentor_connections: Mapped[List["MentorConnection"]] = relationship("MentorConnection", back_populates="student", cascade="all, delete-orphan")
    peer_skill_requests: Mapped[List["PeerSkillRequest"]] = relationship(
        "PeerSkillRequest",
        back_populates="requester_student",
        foreign_keys="[PeerSkillRequest.requester_student_id]",
        cascade="all, delete-orphan",
    )
    competition_participants: Mapped[List["CompetitionParticipant"]] = relationship("CompetitionParticipant", back_populates="student", cascade="all, delete-orphan")
    competition_team_memberships: Mapped[List["CompetitionTeamMember"]] = relationship("CompetitionTeamMember", back_populates="student", cascade="all, delete-orphan")


class Teacher(Base):
    """Faculty and trainer domain profile."""
    __tablename__ = "teachers"

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
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    employee_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    specialization: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_trainer: Mapped[bool] = mapped_column(
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
        ForeignKeyConstraint(
            ["institution_id", "department_id"],
            ["departments.institution_id", "departments.id"],
            name="fk_teacher_institution_dept",
            ondelete="RESTRICT",
        ),
        Index("idx_teachers_institution_dept", "institution_id", "department_id"),
        Index("idx_teachers_is_trainer", "is_trainer"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="teacher_profile")
    institution: Mapped["Institution"] = relationship(
        "Institution",
        back_populates="teachers",
        foreign_keys=[institution_id],
    )
    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="teachers",
        foreign_keys=[institution_id, department_id],
        primaryjoin="and_(Teacher.institution_id == Department.institution_id, Teacher.department_id == Department.id)",
    )


class InstitutionStaff(Base):
    """Operational management staff for colleges (TPOs, Deans, Placement Officers)."""
    __tablename__ = "institution_staff"

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
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    staff_role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    employee_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_institution_staff_inst_role", "institution_id", "staff_role"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="staff_profile")
    institution: Mapped["Institution"] = relationship("Institution", back_populates="staff_members")
