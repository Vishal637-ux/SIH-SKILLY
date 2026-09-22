import uuid
from decimal import Decimal
from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.auth import UserResponse, UserProfileResponse


class InstitutionSimple(BaseModel):
    """Lookup representation of an academic institution."""
    id: uuid.UUID
    name: str
    code: str
    city: str
    state: str

    model_config = ConfigDict(from_attributes=True)


class DepartmentSimple(BaseModel):
    """Lookup representation of an academic department."""
    id: uuid.UUID
    institution_id: uuid.UUID
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class CareerRoleSimple(BaseModel):
    """Lookup representation of a career role objective."""
    id: uuid.UUID
    title: str
    slug: str
    industry_domain: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CareerRoleSkillDetail(BaseModel):
    """Granular skill requirement metadata for a career role."""
    skill_id: uuid.UUID
    skill_name: str
    category: str
    required_level: str  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    importance_level: str  # CORE, RECOMMENDED, OPTIONAL
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CareerRoleDetailRead(BaseModel):
    """Full detail view of a career role including all required skills."""
    id: uuid.UUID
    title: str
    slug: str
    industry_domain: str
    description: Optional[str] = None
    is_active: bool = True
    required_skills: List[CareerRoleSkillDetail] = Field(default_factory=list)
    is_current_target: bool = False

    model_config = ConfigDict(from_attributes=True)


class CareerRoleListItem(BaseModel):
    """Card item representation for the career role explorer catalog."""
    id: uuid.UUID
    title: str
    slug: str
    industry_domain: str
    description: Optional[str] = None
    skills_count: int = 0
    core_skills_count: int = 0
    is_current_target: bool = False

    model_config = ConfigDict(from_attributes=True)


class StudentProfileCompletionDetail(BaseModel):
    """Deterministic profile completion score and breakdown."""
    percentage: int = Field(default=0, ge=0, le=100, description="Overall profile completion percentage")
    is_complete: bool = Field(default=False, description="True if all core academic and career requirements are met")
    personal_percentage: int = Field(default=0, ge=0, le=100)
    academic_percentage: int = Field(default=0, ge=0, le=100)
    career_percentage: int = Field(default=0, ge=0, le=100)
    missing_fields: List[str] = Field(default_factory=list, description="List of uncompleted profile fields")


class TargetCareerRoleUpdate(BaseModel):
    """Payload to update student's target career role."""
    career_role_id: uuid.UUID


class TargetCareerRoleResponse(BaseModel):
    """Response returned upon selecting or updating target career role."""
    message: str
    target_career_role: CareerRoleDetailRead
    completion: StudentProfileCompletionDetail


class StudentCareerWorkspaceResponse(BaseModel):
    """High-level workspace status for the authenticated student."""
    current_target_role: Optional[CareerRoleDetailRead] = None
    available_roles_count: int = 0
    completion: StudentProfileCompletionDetail


class StudentAcademicProfileRead(BaseModel):
    """Detailed academic and institutional profile of a student."""
    id: uuid.UUID
    user_id: uuid.UUID
    institution_id: uuid.UUID
    department_id: uuid.UUID
    roll_number: str
    enrollment_year: int
    graduation_year: int
    current_semester: int
    cgpa: Optional[Decimal] = None
    target_career_role_id: Optional[uuid.UUID] = None
    
    # Nested lookups
    institution: Optional[InstitutionSimple] = None
    department: Optional[DepartmentSimple] = None
    target_career_role: Optional[CareerRoleSimple] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)



class StudentProfileRead(BaseModel):
    """Full student identity, personal bio, contact, academic profile, and completion breakdown."""
    user: UserResponse
    academic_profile: Optional[StudentAcademicProfileRead] = None
    is_profile_complete: bool = Field(
        default=False,
        description="True if student has linked academic institution, department, roll number, and target role.",
    )
    completion: StudentProfileCompletionDetail = Field(
        default_factory=StudentProfileCompletionDetail,
        description="Granular completion breakdown and percentage.",
    )


class StudentProfileUpdate(BaseModel):
    """Payload to update student personal bio, contact links, and academic details."""
    # Personal & Contact Information (updates user_profiles)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=30)
    bio: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default="India", max_length=100)
    linkedin_url: Optional[str] = Field(default=None)
    github_url: Optional[str] = Field(default=None)
    website_url: Optional[str] = Field(default=None)

    # Academic & Career Information (updates students table)
    institution_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    roll_number: Optional[str] = Field(default=None, max_length=50)
    enrollment_year: Optional[int] = Field(default=None, ge=2000, le=2100)
    graduation_year: Optional[int] = Field(default=None, ge=2000, le=2100)
    current_semester: Optional[int] = Field(default=None, ge=1, le=12)
    cgpa: Optional[Decimal] = Field(default=None, ge=0.00, le=10.00)
    target_career_role_id: Optional[uuid.UUID] = None


class StudentMetrics(BaseModel):
    """Accurate live metric counts aggregated from database tables."""
    assessed_skills_count: int = Field(default=0, description="Total verified skills assessed")
    active_skill_gaps_count: int = Field(default=0, description="Identified skill gaps against target role")
    active_roadmaps_count: int = Field(default=0, description="Active personalized roadmaps")
    completed_roadmap_steps_count: int = Field(default=0, description="Milestone steps completed in roadmap")
    total_roadmap_steps_count: int = Field(default=0, description="Total steps in roadmap")
    applications_count: int = Field(default=0, description="Total internship/placement applications")
    active_internships_count: int = Field(default=0, description="Currently active internship engagements")
    recognitions_count: int = Field(default=0, description="Achievements & recognitions recorded")
    unread_notifications_count: int = Field(default=0, description="Unread system notifications")


class StudentJourneyStatus(BaseModel):
    """Progress status across the 5 core stages of the Student Journey."""
    profile_completed: bool = False
    target_role_selected: bool = False
    skills_assessed: bool = False
    roadmap_active: bool = False
    internship_active: bool = False


class StudentDashboardResponse(BaseModel):
    """Comprehensive dashboard payload for the authenticated student."""
    user: UserResponse
    academic_profile: Optional[StudentAcademicProfileRead] = None
    metrics: StudentMetrics
    journey_status: StudentJourneyStatus
    completion: StudentProfileCompletionDetail = Field(
        default_factory=StudentProfileCompletionDetail,
        description="Profile completion status and percentage.",
    )
    recent_announcements: List[str] = Field(
        default_factory=list,
        description="System announcements for students",
    )


# =====================================================================
# Phase 3.4 — Roadmap & Learning Workspace DTOs
# =====================================================================

class SkillSimple(BaseModel):
    """Lookup representation of a master skill."""
    id: uuid.UUID
    name: str
    slug: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class RoadmapItemRead(BaseModel):
    """Granular roadmap milestone step DTO."""
    id: uuid.UUID
    roadmap_id: uuid.UUID
    skill_id: Optional[uuid.UUID] = None
    step_order: int
    title: str
    description: Optional[str] = None
    resource_url: Optional[str] = None
    estimated_hours: Optional[int] = None
    status: str = Field(default="PENDING", description="PENDING, IN_PROGRESS, or COMPLETED")
    completed_at: Optional[datetime] = None
    skill: Optional[SkillSimple] = None

    model_config = ConfigDict(from_attributes=True)


class RoadmapItemUpdate(BaseModel):
    """Payload to update roadmap item status."""
    status: str = Field(..., description="Target status: PENDING, IN_PROGRESS, or COMPLETED")


class RoadmapRead(BaseModel):
    """Personalized career progression roadmap DTO."""
    id: uuid.UUID
    student_id: uuid.UUID
    career_role_id: uuid.UUID
    title: str
    status: str = Field(default="ACTIVE", description="ACTIVE, COMPLETED, or ARCHIVED")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[RoadmapItemRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RoadmapOverviewResponse(BaseModel):
    """Comprehensive roadmap workspace summary response."""
    has_target_role: bool = False
    has_active_roadmap: bool = False
    target_career_role: Optional[CareerRoleSimple] = None
    roadmap: Optional[RoadmapRead] = None
    total_steps: int = 0
    completed_steps: int = 0
    total_estimated_hours: int = 0
    completion_percentage: int = Field(default=0, ge=0, le=100)


class TrainingProgramRead(BaseModel):
    """Catalog representation of an institutional/industry training program."""
    id: uuid.UUID
    title: str
    description: str
    program_type: str
    institution_id: Optional[uuid.UUID] = None
    company_id: Optional[uuid.UUID] = None
    conducted_by_user_id: uuid.UUID
    start_date: Optional[datetime | str] = None
    end_date: Optional[datetime | str] = None
    capacity: Optional[int] = None
    status: str = Field(default="UPCOMING")
    created_at: Optional[datetime | str] = None
    is_enrolled: bool = False

    model_config = ConfigDict(from_attributes=True)


class TrainingEnrollmentRead(BaseModel):
    """Student training program enrollment DTO."""
    id: uuid.UUID
    training_program_id: uuid.UUID
    student_id: uuid.UUID
    enrollment_date: Optional[datetime] = None
    attendance_percentage: Decimal = Decimal("0.00")
    completion_status: str = Field(default="ENROLLED", description="ENROLLED, IN_PROGRESS, COMPLETED, DROPPED")
    certificate_url: Optional[str] = None
    training_program: Optional[TrainingProgramRead] = None

    model_config = ConfigDict(from_attributes=True)


class TrainingEnrollmentCreate(BaseModel):
    """Payload to enroll in a training program."""
    training_program_id: uuid.UUID


class StudentLearningWorkspaceResponse(BaseModel):
    """Comprehensive student learning & training workspace payload."""
    available_programs: List[TrainingProgramRead] = Field(default_factory=list)
    current_enrollments: List[TrainingEnrollmentRead] = Field(default_factory=list)
    enrolled_count: int = 0
    completed_count: int = 0


# =====================================================================
# Phase 3.5 — Skill Assessment & Diagnostic Benchmarking DTOs
# =====================================================================

class AssessmentQuestionPublic(BaseModel):
    """Public representation of an assessment question strictly excluding correct_answer."""
    id: uuid.UUID
    assessment_id: uuid.UUID
    question_text: str
    question_type: str
    options: Optional[Any] = None
    points: int = 1
    question_order: int

    model_config = ConfigDict(from_attributes=True)


class AssessmentCatalogItem(BaseModel):
    """Catalog summary of an active assessment for student browsing."""
    id: uuid.UUID
    title: str
    assessment_type: str
    target_skill_id: Optional[uuid.UUID] = None
    target_skill: Optional[SkillSimple] = None
    total_questions: int
    duration_minutes: int
    passing_score: Decimal
    is_active: bool = True
    attempts_count: int = 0
    best_score: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


class AssessmentDetail(BaseModel):
    """Detailed overview of an assessment prior to test start."""
    id: uuid.UUID
    title: str
    assessment_type: str
    target_skill_id: Optional[uuid.UUID] = None
    target_skill: Optional[SkillSimple] = None
    total_questions: int
    duration_minutes: int
    passing_score: Decimal
    is_active: bool = True
    questions_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class AssessmentAttemptRead(BaseModel):
    """Active or completed test execution session DTO."""
    id: uuid.UUID
    assessment_id: uuid.UUID
    student_id: uuid.UUID
    score: Decimal = Decimal("0.00")
    percentage: Decimal = Decimal("0.00")
    is_passed: bool = False
    responses: Any = Field(default_factory=dict)
    started_at: datetime
    completed_at: Optional[datetime] = None
    assessment: Optional[AssessmentDetail] = None
    questions: List[AssessmentQuestionPublic] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AssessmentSubmitRequest(BaseModel):
    """Student submission payload containing answers mapping question_id -> answer_choice."""
    responses: Dict[str, str] = Field(..., description="Dictionary mapping question_id to selected answer choice")


class AssessmentResult(BaseModel):
    """Graded result outcome payload for a submitted attempt."""
    attempt_id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_title: str
    target_skill_name: Optional[str] = None
    score: Decimal
    percentage: Decimal
    passing_score: Decimal
    is_passed: bool
    proficiency_level: str  # EXPERT, ADVANCED, INTERMEDIATE, BEGINNER
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssessmentHistoryItem(BaseModel):
    """Completed assessment session item for student history ledger."""
    attempt_id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_title: str
    target_skill_name: Optional[str] = None
    score: Decimal
    percentage: Decimal
    passing_score: Decimal
    is_passed: bool
    proficiency_level: str
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# Phase 9 — Internship & Placement Lifecycle DTOs
# =====================================================================

class OpportunitySkillRead(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    required_proficiency: str
    is_mandatory: bool

    model_config = ConfigDict(from_attributes=True)


class OpportunityStudentRead(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    company_name: str
    company_logo_url: Optional[str] = None
    title: str
    role_type: str
    description: str
    location: str
    is_remote: bool
    stipend_salary: Optional[str] = None
    duration_months: Optional[int] = None
    openings_count: int
    eligibility_criteria: Optional[Dict[str, Any]] = None
    application_deadline: datetime
    status: str
    required_skills: List[OpportunitySkillRead] = Field(default_factory=list)
    is_eligible: bool = True
    eligibility_reasons: List[str] = Field(default_factory=list)
    skill_match_percentage: float = 100.0
    has_applied: bool = False
    application_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class StudentApplicationApplyRequest(BaseModel):
    cover_letter: Optional[str] = None
    resume_version_id: Optional[uuid.UUID] = None


class StudentApplicationRead(BaseModel):
    id: uuid.UUID
    opportunity_id: uuid.UUID
    opportunity_title: str
    company_name: str
    current_status: str
    applied_at: datetime
    cover_letter: Optional[str] = None
    resume_version_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class StudentApplicationStatusHistoryRead(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    status: str
    notes: Optional[str] = None
    changed_by_user_id: uuid.UUID
    created_at: Any

    model_config = ConfigDict(from_attributes=True)


class StudentInternshipProgressCreate(BaseModel):
    week_number: int = Field(..., ge=1)
    report_text: str = Field(..., min_length=5)


class StudentInternshipProgressRead(BaseModel):
    id: uuid.UUID
    internship_id: uuid.UUID
    week_number: int
    report_text: str
    mentor_feedback: Optional[str] = None
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentInternshipEvaluationRead(BaseModel):
    id: uuid.UUID
    internship_id: uuid.UUID
    technical_rating: int
    soft_skills_rating: int
    punctuality_rating: int
    overall_feedback: str
    evaluated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentInternshipRead(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    company_id: uuid.UUID
    company_name: str
    opportunity_id: Optional[uuid.UUID] = None
    opportunity_title: Optional[str] = None
    supervisor_name: str
    supervisor_email: str
    start_date: Any
    end_date: Any
    stipend: Optional[str] = None
    status: str
    created_at: Any
    progress_reports: List[StudentInternshipProgressRead] = Field(default_factory=list)
    evaluation: Optional[StudentInternshipEvaluationRead] = None

    model_config = ConfigDict(from_attributes=True)


class StudentPlacementRecordRead(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    company_id: uuid.UUID
    company_name: str
    opportunity_id: Optional[uuid.UUID] = None
    opportunity_title: Optional[str] = None
    institution_id: uuid.UUID
    institution_name: str
    package_lpa: Decimal
    offer_letter_url: Optional[str] = None
    offer_date: Any
    joining_date: Optional[Any] = None
    status: str
    created_at: Any

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# Digital Portfolio & Structured Resume DTOs
# =====================================================================

class ProjectCreateRequest(BaseModel):
    item_type: str = Field(default="PROJECT", description="PROJECT, RESEARCH_PAPER, TECHNICAL_DELIVERABLE")
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=5)
    repository_url: Optional[str] = None
    live_url: Optional[str] = None
    role_in_project: Optional[str] = None
    start_date: Optional[Any] = None
    end_date: Optional[Any] = None
    is_featured: bool = False


class ProjectRead(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    item_type: str
    title: str
    description: str
    repository_url: Optional[str] = None
    live_url: Optional[str] = None
    role_in_project: Optional[str] = None
    start_date: Optional[Any] = None
    end_date: Optional[Any] = None
    is_featured: bool
    created_at: Any

    model_config = ConfigDict(from_attributes=True)


class RecognitionCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    issuer_name: str = Field(..., min_length=2, max_length=255)
    issuer_type: str = Field(default="CERTIFICATION", description="CERTIFICATION, HONOR, HACKATHON, BADGE")
    badge_icon: Optional[str] = None
    issued_date: Any
    verification_hash: Optional[str] = None


class RecognitionRead(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    title: str
    issuer_name: str
    issuer_type: str
    badge_icon: Optional[str] = None
    issued_date: Any
    verification_hash: Optional[str] = None
    created_at: Any

    model_config = ConfigDict(from_attributes=True)


class SkillEvidenceCreateRequest(BaseModel):
    student_skill_id: uuid.UUID
    evidence_type: str = Field(default="PROJECT", description="ASSESSMENT, PROJECT, INTERNSHIP, CERTIFICATION")
    title: str = Field(..., min_length=2, max_length=255)
    url: Optional[str] = None
    reference_id: Optional[uuid.UUID] = None


class SkillEvidenceRead(BaseModel):
    id: uuid.UUID
    student_skill_id: uuid.UUID
    evidence_type: str
    reference_id: Optional[uuid.UUID] = None
    title: str
    url: Optional[str] = None
    verified_by_user_id: Optional[uuid.UUID] = None
    verified_at: Optional[datetime] = None
    created_at: Any

    model_config = ConfigDict(from_attributes=True)


class DigitalPortfolioRead(BaseModel):
    student_id: uuid.UUID
    profile: StudentAcademicProfileRead
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[ProjectRead] = Field(default_factory=list)
    certifications: List[RecognitionRead] = Field(default_factory=list)
    internships: List[StudentInternshipRead] = Field(default_factory=list)
    placements: List[StudentPlacementRecordRead] = Field(default_factory=list)
    verified_evidence_count: int = 0
    portfolio_score: int = Field(default=0, ge=0, le=100)


class ResumeGenerateRequest(BaseModel):
    title: str = Field(default="Canonical Software Resume", min_length=2, max_length=150)
    target_role_id: Optional[uuid.UUID] = None
    include_projects: bool = True
    include_certifications: bool = True
    include_internships: bool = True


class ResumeVersionRead(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    title: str
    file_url: str
    target_role_id: Optional[uuid.UUID] = None
    target_role_title: Optional[str] = None
    parsed_content: Optional[Dict[str, Any]] = None
    created_at: Any

    model_config = ConfigDict(from_attributes=True)




