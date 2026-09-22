import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

ALLOWED_ROLE_TYPES = {"FULL_TIME", "INTERNSHIP", "PART_TIME", "PROJECT", "CONTRACT"}
ALLOWED_PROFICIENCIES = {"BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"}
ALLOWED_APP_STATUSES = {"APPLIED", "SHORTLISTED", "INTERVIEWING", "OFFERED", "REJECTED", "ACCEPTED"}
ALLOWED_INTERACTION_TYPES = {"INTERVIEW", "GD", "TEST", "CAMPUS_DRIVE", "WORKSHOP", "GUEST_LECTURE"}


# Company Profile Schemas
class CompanyProfileResponse(BaseModel):
    id: uuid.UUID
    name: str
    industry_type: str
    company_size: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    headquarters: Optional[str] = None
    description: Optional[str] = None
    is_verified: bool
    user_designation: str
    user_hr_role: str
    user_email: str
    user_name: str


class CompanyProfileUpdateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    industry_type: str = Field(..., min_length=2, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = None
    logo_url: Optional[str] = None
    headquarters: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None
    designation: str = Field(..., min_length=2, max_length=100)


# Opportunity Schemas
class OpportunitySkillRequirement(BaseModel):
    skill_id: uuid.UUID
    skill_name: Optional[str] = None
    required_proficiency: str = "INTERMEDIATE"
    is_mandatory: bool = True

    @field_validator("required_proficiency")
    @classmethod
    def validate_proficiency(cls, v: str) -> str:
        upper_v = v.upper().strip()
        if upper_v not in ALLOWED_PROFICIENCIES:
            raise ValueError(f"required_proficiency must be one of {sorted(list(ALLOWED_PROFICIENCIES))}")
        return upper_v


class OpportunityCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    role_type: str = Field(..., description="Must be FULL_TIME, INTERNSHIP, PART_TIME, PROJECT, or CONTRACT")
    description: str = Field(..., min_length=10)
    location: str = Field(..., min_length=2, max_length=150)
    is_remote: bool = False
    stipend_salary: Optional[str] = Field(None, max_length=100)
    duration_months: Optional[int] = Field(None, ge=1)
    openings_count: int = Field(1, ge=1)
    eligibility_criteria: Optional[Dict[str, Any]] = None
    application_deadline: datetime
    skills: List[OpportunitySkillRequirement] = Field(default_factory=list)

    @field_validator("role_type")
    @classmethod
    def validate_role_type(cls, v: str) -> str:
        upper_v = v.upper().strip()
        if upper_v not in ALLOWED_ROLE_TYPES:
            raise ValueError(f"role_type must be one of {sorted(list(ALLOWED_ROLE_TYPES))}")
        return upper_v


class OpportunityUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    role_type: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, min_length=2, max_length=150)
    is_remote: Optional[bool] = None
    stipend_salary: Optional[str] = None
    duration_months: Optional[int] = Field(None, ge=1)
    openings_count: Optional[int] = Field(None, ge=1)
    eligibility_criteria: Optional[Dict[str, Any]] = None
    application_deadline: Optional[datetime] = None
    status: Optional[str] = None
    skills: Optional[List[OpportunitySkillRequirement]] = None


class OpportunityItem(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    company_name: str
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
    created_at: datetime
    required_skills: List[OpportunitySkillRequirement] = Field(default_factory=list)
    applications_count: int = 0


class OpportunityListResponse(BaseModel):
    total: int
    page: int
    limit: int
    opportunities: List[OpportunityItem]


# Application Schemas
class ApplicationStudentProfile(BaseModel):
    student_id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    roll_number: str
    institution_name: str
    department_name: str
    current_semester: int
    graduation_year: int
    cgpa: Optional[Decimal] = None
    target_career_role: Optional[str] = None
    skills: List[str] = Field(default_factory=list)


class ApplicationItem(BaseModel):
    id: uuid.UUID
    opportunity_id: uuid.UUID
    opportunity_title: str
    student: ApplicationStudentProfile
    resume_version_id: Optional[uuid.UUID] = None
    cover_letter: Optional[str] = None
    current_status: str
    applied_at: datetime
    skill_match_percentage: float = 0.0


class ApplicationListResponse(BaseModel):
    total: int
    page: int
    limit: int
    applications: List[ApplicationItem]


class ApplicationStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="Must be APPLIED, SHORTLISTED, INTERVIEWING, OFFERED, REJECTED, or ACCEPTED")
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        upper_v = v.upper().strip()
        if upper_v not in ALLOWED_APP_STATUSES:
            raise ValueError(f"status must be one of {sorted(list(ALLOWED_APP_STATUSES))}")
        return upper_v


class ApplicationStatusHistoryItem(BaseModel):
    id: uuid.UUID
    status: str
    notes: Optional[str] = None
    changed_by_name: str
    created_at: datetime


# Internship Schemas
class InternshipItem(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    roll_number: str
    opportunity_title: Optional[str] = None
    supervisor_name: str
    supervisor_email: str
    start_date: date
    end_date: date
    stipend: Optional[str] = None
    status: str
    weekly_reports_count: int = 0
    has_evaluation: bool = False


class InternshipEvaluationRequest(BaseModel):
    technical_rating: int = Field(..., ge=1, le=5)
    soft_skills_rating: int = Field(..., ge=1, le=5)
    punctuality_rating: int = Field(..., ge=1, le=5)
    overall_feedback: str = Field(..., min_length=5)


class InternshipEvaluationResponse(BaseModel):
    id: uuid.UUID
    internship_id: uuid.UUID
    technical_rating: int
    soft_skills_rating: int
    punctuality_rating: int
    overall_feedback: str
    evaluated_at: datetime


# Interaction Schemas
class PlacementInteractionCreateRequest(BaseModel):
    opportunity_id: uuid.UUID
    interaction_type: str = Field(..., description="Must be INTERVIEW, GD, TEST, CAMPUS_DRIVE, WORKSHOP, or GUEST_LECTURE")
    title: str = Field(..., min_length=3, max_length=255)
    scheduled_at: datetime
    meeting_link: Optional[str] = None

    @field_validator("interaction_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        upper_v = v.upper().strip()
        if upper_v not in ALLOWED_INTERACTION_TYPES:
            raise ValueError(f"interaction_type must be one of {sorted(list(ALLOWED_INTERACTION_TYPES))}")
        return upper_v


class PlacementInteractionItem(BaseModel):
    id: uuid.UUID
    opportunity_id: uuid.UUID
    opportunity_title: str
    interaction_type: str
    title: str
    scheduled_at: datetime
    meeting_link: Optional[str] = None
    conducted_by_name: Optional[str] = None
    created_at: datetime


# Dashboard & Analytics Schemas
class RecentApplicationOverview(BaseModel):
    id: uuid.UUID
    opportunity_title: str
    student_name: str
    status: str
    applied_at: datetime


class IndustryDashboardResponse(BaseModel):
    company_id: uuid.UUID
    company_name: str
    is_verified: bool
    active_opportunities_count: int
    total_applications_count: int
    shortlisted_count: int
    selected_count: int
    active_internships_count: int
    upcoming_interactions_count: int
    recent_applications: List[RecentApplicationOverview] = Field(default_factory=list)


class StatusFunnelItem(BaseModel):
    status: str
    count: int


class TopRequiredSkillItem(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    postings_count: int


class IndustryAnalyticsResponse(BaseModel):
    company_id: uuid.UUID
    company_name: str
    total_postings: int
    total_applications: int
    hiring_funnel: List[StatusFunnelItem] = Field(default_factory=list)
    top_demanded_skills: List[TopRequiredSkillItem] = Field(default_factory=list)
    internship_completion_rate: float = 0.0
