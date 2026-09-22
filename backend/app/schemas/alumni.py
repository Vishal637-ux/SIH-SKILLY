import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

ALLOWED_REQUEST_STATUSES = {"PENDING", "ACCEPTED", "REJECTED"}
ALLOWED_SESSION_STATUSES = {"SCHEDULED", "COMPLETED", "CANCELLED"}


# Alumni Profile Schemas
class AlumniProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None


class AlumniProfileUpdateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=30)
    bio: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field("India", max_length=100)
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None


# Student Context inside Mentorship
class MentorshipStudentProfile(BaseModel):
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


# Mentorship Request Schemas
class MentorshipRequestItem(BaseModel):
    connection_id: uuid.UUID
    student: MentorshipStudentProfile
    status: str
    request_note: Optional[str] = None
    connected_at: Optional[datetime] = None
    created_at: datetime


class MentorshipRequestListResponse(BaseModel):
    total: int
    requests: List[MentorshipRequestItem]


class MentorshipRequestActionRequest(BaseModel):
    status: str = Field(..., description="Must be ACCEPTED or REJECTED")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        upper_v = v.upper().strip()
        if upper_v not in {"ACCEPTED", "REJECTED"}:
            raise ValueError("status must be ACCEPTED or REJECTED")
        return upper_v


# Connection Schemas
class MentorConnectionItem(BaseModel):
    connection_id: uuid.UUID
    student: MentorshipStudentProfile
    status: str
    connected_at: Optional[datetime] = None
    sessions_count: int = 0
    created_at: datetime


class MentorConnectionListResponse(BaseModel):
    total: int
    connections: List[MentorConnectionItem]


# Session Schemas
class MentorshipSessionCreateRequest(BaseModel):
    connection_id: uuid.UUID
    topic: str = Field(..., min_length=3, max_length=255)
    scheduled_at: datetime
    duration_minutes: int = Field(45, ge=15, le=240)
    meeting_link: Optional[str] = None
    session_notes: Optional[str] = None


class MentorshipSessionUpdateRequest(BaseModel):
    topic: Optional[str] = Field(None, min_length=3, max_length=255)
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=240)
    meeting_link: Optional[str] = None
    session_notes: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        upper_v = v.upper().strip()
        if upper_v not in ALLOWED_SESSION_STATUSES:
            raise ValueError(f"status must be one of {sorted(list(ALLOWED_SESSION_STATUSES))}")
        return upper_v


class MentorshipSessionItem(BaseModel):
    id: uuid.UUID
    connection_id: uuid.UUID
    student_name: str
    topic: str
    scheduled_at: datetime
    duration_minutes: int
    meeting_link: Optional[str] = None
    session_notes: Optional[str] = None
    feedback_rating: Optional[int] = None
    status: str
    created_at: datetime


class MentorshipSessionListResponse(BaseModel):
    total: int
    sessions: List[MentorshipSessionItem]


# Alumni Dashboard Response
class AlumniDashboardResponse(BaseModel):
    user_id: uuid.UUID
    mentor_name: str
    total_requests_count: int
    pending_requests_count: int
    active_connections_count: int
    total_sessions_count: int
    upcoming_sessions_count: int
    completed_sessions_count: int
    recent_requests: List[MentorshipRequestItem] = Field(default_factory=list)
