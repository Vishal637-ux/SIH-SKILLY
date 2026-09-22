import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- Dashboard Schemas ---
class TopSkillGapItem(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    student_count: int


class ActivityOverviewItem(BaseModel):
    id: uuid.UUID
    title: str
    activity_type: str
    start_time: datetime


class TeacherDashboardResponse(BaseModel):
    teacher_id: uuid.UUID
    designation: str
    department_id: uuid.UUID
    department_name: str
    institution_id: uuid.UUID
    institution_name: str
    total_department_students: int
    programs_conducted_count: int
    active_mentorships_count: int
    department_top_skill_gaps: List[TopSkillGapItem]
    recent_activities: List[ActivityOverviewItem]


# --- Profile Schemas ---
class TeacherProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email: str
    username: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    designation: str
    employee_id: Optional[str] = None
    specialization: Optional[str] = None
    is_trainer: bool = False
    institution_id: uuid.UUID
    institution_name: str
    department_id: uuid.UUID
    department_name: str

    model_config = ConfigDict(from_attributes=True)


class TeacherProfileUpdateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)
    bio: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    designation: str = Field(..., min_length=1, max_length=100)
    employee_id: Optional[str] = Field(None, max_length=50)
    specialization: Optional[str] = None
    is_trainer: Optional[bool] = False


# --- Department Roster Schemas ---
class DepartmentStudentItem(BaseModel):
    student_id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    roll_number: str
    enrollment_year: int
    graduation_year: int
    current_semester: int
    cgpa: Optional[Decimal] = None
    target_career_role: Optional[str] = None


class DepartmentStudentRosterResponse(BaseModel):
    total: int
    page: int
    limit: int
    students: List[DepartmentStudentItem]


# --- Training Program Schemas ---
ALLOWED_PROGRAM_TYPES = {"WORKSHOP", "BOOTCAMP", "MASTERCLASS"}


class TrainingProgramCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    program_type: str = Field(..., description="Must be one of WORKSHOP, BOOTCAMP, MASTERCLASS")
    start_date: date
    end_date: date
    capacity: Optional[int] = Field(None, ge=1)

    @field_validator("program_type")
    @classmethod
    def validate_program_type(cls, v: str) -> str:
        upper_v = v.upper().strip()
        if upper_v not in ALLOWED_PROGRAM_TYPES:
            raise ValueError(f"program_type must be one of {sorted(list(ALLOWED_PROGRAM_TYPES))}")
        return upper_v


class TrainingProgramItem(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    program_type: str
    institution_id: Optional[uuid.UUID] = None
    company_id: Optional[uuid.UUID] = None
    conducted_by_user_id: uuid.UUID
    conducted_by_name: str
    start_date: date
    end_date: date
    capacity: Optional[int] = None
    status: str
    enrolled_count: int


class TrainingProgramListResponse(BaseModel):
    total: int
    page: int
    limit: int
    programs: List[TrainingProgramItem]


class EnrollmentStudentItem(BaseModel):
    enrollment_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    roll_number: str
    enrollment_date: datetime
    attendance_percentage: Decimal
    completion_status: str
    certificate_url: Optional[str] = None


class TrainingProgramEnrollmentsResponse(BaseModel):
    program_id: uuid.UUID
    program_title: str
    total_enrolled: int
    enrollments: List[EnrollmentStudentItem]


class EnrollmentUpdateRequest(BaseModel):
    attendance_percentage: Decimal = Field(..., ge=Decimal("0.00"), le=Decimal("100.00"))
    completion_status: str = Field(..., min_length=1, max_length=50)
    certificate_url: Optional[str] = None

    @field_validator("completion_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = {"ENROLLED", "ATTENDING", "COMPLETED", "DROPPED"}
        upper_v = v.upper().strip()
        if upper_v not in valid_statuses:
            raise ValueError(f"completion_status must be one of {sorted(list(valid_statuses))}")
        return upper_v


# --- Mentorship Schemas ---
class MentorshipRequestItem(BaseModel):
    connection_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    student_roll_number: str
    student_department: str
    status: str
    request_note: Optional[str] = None
    connected_at: Optional[datetime] = None
    created_at: datetime


class MentorshipStatusUpdateRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_mentorship_status(cls, v: str) -> str:
        valid_statuses = {"ACCEPTED", "REJECTED", "COMPLETED"}
        upper_v = v.upper().strip()
        if upper_v not in valid_statuses:
            raise ValueError(f"status must be one of {sorted(list(valid_statuses))}")
        return upper_v


class MentorshipSessionCreateRequest(BaseModel):
    connection_id: uuid.UUID
    topic: str = Field(..., min_length=1, max_length=255)
    scheduled_at: datetime
    duration_minutes: int = Field(45, ge=1)
    meeting_link: Optional[str] = None
    session_notes: Optional[str] = None


class MentorshipSessionResponse(BaseModel):
    id: uuid.UUID
    connection_id: uuid.UUID
    topic: str
    scheduled_at: datetime
    duration_minutes: int
    meeting_link: Optional[str] = None
    session_notes: Optional[str] = None
    status: str
    created_at: datetime


# --- Activity Schemas ---
ALLOWED_ACTIVITY_TYPES = {"GUEST_LECTURE", "WEBINAR", "WORKSHOP", "CAMPUS_EVENT"}


class ActivityCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    activity_type: str = Field(..., description="Must be GUEST_LECTURE, WEBINAR, WORKSHOP, or CAMPUS_EVENT")
    start_time: datetime
    end_time: datetime
    location_or_url: Optional[str] = None

    @field_validator("activity_type")
    @classmethod
    def validate_activity_type(cls, v: str) -> str:
        upper_v = v.upper().strip()
        if upper_v not in ALLOWED_ACTIVITY_TYPES:
            raise ValueError(f"activity_type must be one of {sorted(list(ALLOWED_ACTIVITY_TYPES))}")
        return upper_v


class ActivityItem(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    activity_type: str
    start_time: datetime
    end_time: datetime
    location_or_url: Optional[str] = None
    conducted_by_user_id: Optional[uuid.UUID] = None
    conducted_by_name: Optional[str] = None


class ActivityListResponse(BaseModel):
    total: int
    page: int
    limit: int
    activities: List[ActivityItem]


# --- Analytics Schemas ---
class CgpaDistribution(BaseModel):
    above_8: int
    between_6_and_8: int
    below_6: int


class DepartmentAnalyticsResponse(BaseModel):
    department_id: uuid.UUID
    department_name: str
    total_students: int
    cgpa_distribution: CgpaDistribution
    top_skill_gaps: List[TopSkillGapItem]
    placed_students_count: int
    placement_percentage: float
