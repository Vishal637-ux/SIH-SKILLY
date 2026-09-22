import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

# --- Dashboard Schemas ---
class TopSkillGapItem(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    student_count: int

class CollegeDashboardResponse(BaseModel):
    institution_id: uuid.UUID
    institution_name: str
    total_students: int
    total_departments: int
    active_drives: int
    total_placements: int
    placement_rate_percentage: float
    average_package_lpa: float
    highest_package_lpa: float
    top_skill_gaps: List[TopSkillGapItem]

# --- Department & Faculty Schemas ---
class DepartmentItem(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    student_count: int
    faculty_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FacultyItem(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    designation: Optional[str] = None
    department_name: Optional[str] = None
    role_type: str  # "STAFF" or "TEACHER"
    staff_role: Optional[str] = None  # "TPO_ADMIN", "TPO_COORDINATOR", "DEPT_HEAD"

# --- Student Roster Schemas ---
class StudentRosterItem(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    roll_number: str
    department_id: uuid.UUID
    department_name: str
    enrollment_year: int
    graduation_year: int
    current_semester: int
    cgpa: float
    target_career_role: Optional[str] = None

class StudentRosterResponse(BaseModel):
    total_count: int
    page: int
    limit: int
    students: List[StudentRosterItem]

# --- Skill Analytics Schemas ---
class SkillGapAnalyticsItem(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    category: str
    affected_students_count: int
    critical_gap_count: int

class SkillAnalyticsResponse(BaseModel):
    institution_id: uuid.UUID
    department_id: Optional[uuid.UUID] = None
    total_assessed_students: int
    top_skill_gaps: List[SkillGapAnalyticsItem]

# --- Campus Drive & Shortlisting Schemas ---
class CampusDriveItem(BaseModel):
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
    openings_count: int
    application_deadline: datetime
    status: str
    total_applications: int

class ShortlistRequest(BaseModel):
    opportunity_id: uuid.UUID
    min_cgpa: float = Field(ge=0.0, le=10.0, default=0.0)
    graduation_year: Optional[int] = Field(default=None, ge=2000, le=2100)
    department_ids: Optional[List[uuid.UUID]] = None
    required_skill_ids: Optional[List[uuid.UUID]] = None
    min_proficiency: Optional[int] = Field(default=1, ge=1, le=5)

class ShortlistedStudentItem(BaseModel):
    student_id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    roll_number: str
    department_name: str
    cgpa: float
    graduation_year: int
    matching_skills_count: int

class ShortlistResponse(BaseModel):
    opportunity_id: uuid.UUID
    opportunity_title: str
    eligible_student_count: int
    shortlisted_students: List[ShortlistedStudentItem]

# --- Placement Record Logging Schemas ---
class RecordPlacementRequest(BaseModel):
    student_id: uuid.UUID
    company_name: str = Field(min_length=2, max_length=200)
    job_title: str = Field(min_length=2, max_length=200)
    package_amount: float = Field(gt=0.0)
    placement_type: str = Field(default="CAMPUS", pattern="^(CAMPUS|OFF_CAMPUS)$")
    placement_date: Optional[datetime] = None

class PlacementRecordResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    company_name: str
    job_title: str
    package_amount: float
    placement_type: str
    status: str
    placement_date: datetime
