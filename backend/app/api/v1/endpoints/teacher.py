import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.users import User
from app.models.institutions import Teacher
from app.schemas.teacher import (
    TeacherDashboardResponse,
    TeacherProfileResponse,
    TeacherProfileUpdateRequest,
    DepartmentStudentRosterResponse,
    TrainingProgramCreateRequest,
    TrainingProgramItem,
    TrainingProgramListResponse,
    TrainingProgramEnrollmentsResponse,
    EnrollmentStudentItem,
    EnrollmentUpdateRequest,
    MentorshipRequestItem,
    MentorshipStatusUpdateRequest,
    MentorshipSessionCreateRequest,
    MentorshipSessionResponse,
    ActivityCreateRequest,
    ActivityItem,
    ActivityListResponse,
    DepartmentAnalyticsResponse
)
from app.services.teacher_service import (
    get_teacher_context,
    get_teacher_dashboard,
    get_teacher_profile,
    update_teacher_profile,
    get_department_student_roster,
    get_training_programs_list,
    create_training_program,
    get_program_enrollments,
    update_program_enrollment,
    get_mentorship_requests,
    update_mentorship_request_status,
    create_mentorship_session,
    get_activities_list,
    create_activity,
    get_department_analytics
)

router = APIRouter(prefix="/teacher", tags=["Teacher / Academician"])


async def _resolve_teacher(db: AsyncSession, current_user: User) -> Teacher:
    """
    Resolves Teacher identity server-side from PostgreSQL based on current_user.id.
    Never trusts client-supplied teacher_id, institution_id, or department_id!
    """
    teacher = await get_teacher_context(db, current_user.id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher profile not configured for this account."
        )
    return teacher


@router.get("/dashboard", response_model=TeacherDashboardResponse)
async def get_dashboard(
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Fetch aggregated dashboard metrics and overview for authenticated teacher."""
    teacher = await _resolve_teacher(db, current_user)
    return await get_teacher_dashboard(db, teacher)


@router.get("/profile", response_model=TeacherProfileResponse)
async def get_profile(
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Get authenticated teacher's academic identity and profile details."""
    teacher = await _resolve_teacher(db, current_user)
    return await get_teacher_profile(db, teacher)


@router.put("/profile", response_model=TeacherProfileResponse)
async def update_profile(
    update_req: TeacherProfileUpdateRequest,
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Update profile details for authenticated teacher."""
    teacher = await _resolve_teacher(db, current_user)
    return await update_teacher_profile(db, teacher, update_req)


@router.get("/students", response_model=DepartmentStudentRosterResponse)
async def get_students(
    graduation_year: Optional[int] = Query(None, description="Filter by graduation year"),
    current_semester: Optional[int] = Query(None, description="Filter by semester"),
    search: Optional[str] = Query(None, description="Search by roll number or name"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Query department student roster strictly scoped to teacher's institution and department."""
    teacher = await _resolve_teacher(db, current_user)
    return await get_department_student_roster(
        db, teacher,
        graduation_year=graduation_year,
        current_semester=current_semester,
        search=search,
        page=page,
        limit=limit
    )


@router.get("/training-programs", response_model=TrainingProgramListResponse)
async def get_training_programs(
    scope: str = Query("my_programs", description="Filter scope: 'my_programs' or 'institution'"),
    program_type: Optional[str] = Query(None, description="Must be WORKSHOP, BOOTCAMP, or MASTERCLASS"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Fetch training programs and workshops scoped to teacher's institution."""
    teacher = await _resolve_teacher(db, current_user)
    return await get_training_programs_list(
        db, teacher,
        scope=scope,
        program_type=program_type,
        page=page,
        limit=limit
    )


@router.post("/training-programs", response_model=TrainingProgramItem, status_code=status.HTTP_201_CREATED)
async def create_new_training_program(
    req: TrainingProgramCreateRequest,
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new training program / workshop conducted by authenticated teacher."""
    if req.end_date < req.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date cannot be earlier than start_date."
        )

    teacher = await _resolve_teacher(db, current_user)
    return await create_training_program(db, teacher, req)


@router.get("/training-programs/{program_id}/enrollments", response_model=TrainingProgramEnrollmentsResponse)
async def get_program_enrollments_list(
    program_id: uuid.UUID,
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """View student enrollments for a specific program."""
    teacher = await _resolve_teacher(db, current_user)
    res = await get_program_enrollments(db, teacher, program_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training program not found or access denied."
        )
    return res


@router.put(
    "/training-programs/{program_id}/enrollments/{enrollment_id}",
    response_model=EnrollmentStudentItem
)
async def update_student_enrollment(
    program_id: uuid.UUID,
    enrollment_id: uuid.UUID,
    req: EnrollmentUpdateRequest,
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Update student attendance and completion status for a conducted program."""
    teacher = await _resolve_teacher(db, current_user)
    res = await update_program_enrollment(db, teacher, program_id, enrollment_id, req)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment or training program not found or access denied."
        )
    return res


@router.get("/mentorship/requests", response_model=List[MentorshipRequestItem])
async def get_mentorship_connection_requests(
    status_filter: Optional[str] = Query(None, description="Filter by status: PENDING, ACCEPTED, REJECTED, COMPLETED"),
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """View incoming student mentorship requests for the authenticated teacher."""
    teacher = await _resolve_teacher(db, current_user)
    return await get_mentorship_requests(db, teacher, status_filter=status_filter)


@router.put("/mentorship/requests/{connection_id}", response_model=MentorshipRequestItem)
async def update_mentorship_request(
    connection_id: uuid.UUID,
    req: MentorshipStatusUpdateRequest,
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Accept or reject a student mentorship connection request."""
    teacher = await _resolve_teacher(db, current_user)
    res = await update_mentorship_request_status(db, teacher, connection_id, req.status)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentorship request not found or access denied."
        )
    return res


@router.post("/mentorship/sessions", response_model=MentorshipSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_mentorship_session(
    req: MentorshipSessionCreateRequest,
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Schedule a mentorship session with an accepted student mentee."""
    teacher = await _resolve_teacher(db, current_user)
    res = await create_mentorship_session(db, teacher, req)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mentorship connection not found, not owned by teacher, or status is not ACCEPTED."
        )
    return res


@router.get("/activities", response_model=ActivityListResponse)
async def get_activities(
    scope: str = Query("institution", description="'institution' or 'my_activities'"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """List campus activities and guest lectures in teacher's institution."""
    teacher = await _resolve_teacher(db, current_user)
    return await get_activities_list(db, teacher, scope=scope, page=page, limit=limit)


@router.post("/activities", response_model=ActivityItem, status_code=status.HTTP_201_CREATED)
async def create_new_activity(
    req: ActivityCreateRequest,
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Schedule a new department activity or industry guest lecture."""
    if req.end_time < req.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time cannot be earlier than start_time."
        )

    teacher = await _resolve_teacher(db, current_user)
    return await create_activity(db, teacher, req)


@router.get("/analytics/department", response_model=DepartmentAnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Fetch read-only department academic analytics derived deterministically from PostgreSQL."""
    teacher = await _resolve_teacher(db, current_user)
    return await get_department_analytics(db, teacher)
