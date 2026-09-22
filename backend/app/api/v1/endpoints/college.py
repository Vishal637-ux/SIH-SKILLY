import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, require_role, require_roles
from app.models.users import User
from app.schemas.college import (
    CollegeDashboardResponse,
    DepartmentItem,
    FacultyItem,
    StudentRosterResponse,
    SkillAnalyticsResponse,
    CampusDriveItem,
    ShortlistRequest,
    ShortlistResponse,
    RecordPlacementRequest,
    PlacementRecordResponse
)
from app.services.college_service import (
    get_staff_context,
    get_teacher_context,
    get_dashboard_metrics,
    get_departments_list,
    get_faculty_directory,
    get_student_roster,
    get_skill_analytics,
    get_institution_opportunities,
    filter_eligible_students,
    record_confirmed_placement
)

router = APIRouter(prefix="/college", tags=["College Portal & TPO"])


async def _resolve_institution_id(
    db: AsyncSession,
    current_user: User,
    allowed_for_teacher: bool = False
) -> tuple[uuid.UUID, Optional[uuid.UUID]]:
    """
    Resolves institution_id (and optional department_id) server-side from PostgreSQL.
    Never trusts client-supplied institution_id!
    """
    user_role = current_user.role.upper() if current_user.role else ""

    if user_role == "COLLEGE_ADMIN":
        staff = await get_staff_context(db, current_user.id)
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="College Admin staff profile not configured for this account."
            )
        return staff.institution_id, None

    elif user_role == "TEACHER" and allowed_for_teacher:
        teacher = await get_teacher_context(db, current_user.id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teacher profile not configured for this account."
            )
        return teacher.institution_id, teacher.department_id

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied for current user role."
    )


@router.get("/dashboard", response_model=CollegeDashboardResponse)
async def get_dashboard(
    current_user: User = Depends(require_role("COLLEGE_ADMIN")),
    db: AsyncSession = Depends(get_db)
):
    """Fetch live database overview metrics for College / TPO dashboard."""
    inst_id, _ = await _resolve_institution_id(db, current_user)
    return await get_dashboard_metrics(db, inst_id)


@router.get("/departments", response_model=List[DepartmentItem])
async def get_departments(
    current_user: User = Depends(require_roles("COLLEGE_ADMIN", "TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """List academic departments under the authenticated user's institution."""
    inst_id, _ = await _resolve_institution_id(db, current_user, allowed_for_teacher=True)
    return await get_departments_list(db, inst_id)


@router.get("/faculty", response_model=List[FacultyItem])
async def get_faculty(
    current_user: User = Depends(require_roles("COLLEGE_ADMIN", "TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """List staff and faculty directory under the authenticated user's institution."""
    inst_id, _ = await _resolve_institution_id(db, current_user, allowed_for_teacher=True)
    return await get_faculty_directory(db, inst_id)


@router.get("/students", response_model=StudentRosterResponse)
async def get_students(
    department_id: Optional[uuid.UUID] = Query(None),
    graduation_year: Optional[int] = Query(None, ge=2000, le=2100),
    min_cgpa: Optional[float] = Query(None, ge=0.0, le=10.0),
    current_semester: Optional[int] = Query(None, ge=1, le=12),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_roles("COLLEGE_ADMIN", "TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Filterable, paginated student roster for an institution."""
    inst_id, teacher_dept_id = await _resolve_institution_id(db, current_user, allowed_for_teacher=True)

    # For TEACHER role, force query to their assigned department scope
    effective_dept_id = teacher_dept_id if teacher_dept_id else department_id

    return await get_student_roster(
        db=db,
        institution_id=inst_id,
        department_id=effective_dept_id,
        graduation_year=graduation_year,
        min_cgpa=min_cgpa,
        current_semester=current_semester,
        page=page,
        limit=limit
    )


@router.get("/analytics/skills", response_model=SkillAnalyticsResponse)
async def get_skill_gap_analytics(
    department_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(require_roles("COLLEGE_ADMIN", "TEACHER")),
    db: AsyncSession = Depends(get_db)
):
    """Aggregate batch skill proficiencies and identify critical skill gaps."""
    inst_id, teacher_dept_id = await _resolve_institution_id(db, current_user, allowed_for_teacher=True)
    effective_dept_id = teacher_dept_id if teacher_dept_id else department_id

    return await get_skill_analytics(db, inst_id, effective_dept_id)


@router.get("/drives", response_model=List[CampusDriveItem])
async def get_campus_drives(
    current_user: User = Depends(require_role("COLLEGE_ADMIN")),
    db: AsyncSession = Depends(get_db)
):
    """Fetch open campus placement drives (Industry opportunities)."""
    inst_id, _ = await _resolve_institution_id(db, current_user)
    return await get_institution_opportunities(db, inst_id)


@router.post("/shortlist", response_model=ShortlistResponse)
async def shortlist_candidates(
    req: ShortlistRequest,
    current_user: User = Depends(require_role("COLLEGE_ADMIN")),
    db: AsyncSession = Depends(get_db)
):
    """Run deterministic student shortlisting for a placement drive."""
    inst_id, _ = await _resolve_institution_id(db, current_user)
    try:
        return await filter_eligible_students(db, inst_id, req)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        )


@router.post("/placements", response_model=PlacementRecordResponse)
async def log_confirmed_placement(
    req: RecordPlacementRequest,
    current_user: User = Depends(require_role("COLLEGE_ADMIN")),
    db: AsyncSession = Depends(get_db)
):
    """Log confirmed student placement into placement_records."""
    inst_id, _ = await _resolve_institution_id(db, current_user)
    try:
        return await record_confirmed_placement(db, inst_id, req)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err)
        )
