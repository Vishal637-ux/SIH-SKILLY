import uuid
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, get_optional_user, require_roles
from app.models.users import User, UserProfile
from app.models.institutions import Student, Institution, Department
from app.models.careers import CareerRole, CareerRoleSkill, SkillGap, Roadmap, RoadmapItem
from app.models.skills import Skill, StudentSkill
from app.models.opportunities import Application
from app.models.internships import Internship
from app.models.portfolio import Recognition
from app.models.notifications import Notification

from app.schemas.student import (
    InstitutionSimple,
    DepartmentSimple,
    CareerRoleSimple,
    CareerRoleSkillDetail,
    CareerRoleDetailRead,
    CareerRoleListItem,
    TargetCareerRoleUpdate,
    TargetCareerRoleResponse,
    StudentCareerWorkspaceResponse,
    StudentAcademicProfileRead,
    StudentProfileCompletionDetail,
    StudentProfileRead,
    StudentProfileUpdate,
    StudentMetrics,
    StudentJourneyStatus,
    StudentDashboardResponse,
    RoadmapItemRead,
    RoadmapItemUpdate,
    RoadmapRead,
    RoadmapOverviewResponse,
    TrainingProgramRead,
    TrainingEnrollmentRead,
    TrainingEnrollmentCreate,
    StudentLearningWorkspaceResponse,
    AssessmentCatalogItem,
    AssessmentDetail,
    AssessmentQuestionPublic,
    AssessmentAttemptRead,
    AssessmentSubmitRequest,
    AssessmentResult,
    AssessmentHistoryItem,
    OpportunityStudentRead,
    StudentApplicationApplyRequest,
    StudentApplicationRead,
    StudentApplicationStatusHistoryRead,
    StudentInternshipRead,
    StudentInternshipProgressCreate,
    StudentInternshipProgressRead,
    StudentPlacementRecordRead,
    ProjectCreateRequest,
    ProjectRead,
    RecognitionCreateRequest,
    RecognitionRead,
    SkillEvidenceCreateRequest,
    SkillEvidenceRead,
    DigitalPortfolioRead,
    ResumeGenerateRequest,
    ResumeVersionRead,
)
from app.services.internship_service import InternshipService
from app.services.portfolio_service import PortfolioService
from app.services.roadmap_service import (
    get_student_active_roadmap,
    generate_or_sync_student_roadmap,
    update_roadmap_item_status,
    get_student_learning_workspace,
    enroll_student_in_training,
)
from app.services.assessment_service import (
    get_assessment_catalog,
    get_assessment_detail,
    start_assessment_attempt,
    get_assessment_attempt,
    submit_assessment_attempt,
    get_student_assessment_history,
)
from app.services.skill_service import (
    get_student_skills_profile,
    calculate_student_skill_gaps,
)

router = APIRouter(prefix="/student", tags=["Student Module"])



def calculate_profile_completion(
    user_profile: Optional[UserProfile],
    student: Optional[Student],
) -> StudentProfileCompletionDetail:
    """Calculates deterministic profile completion percentages, scores, and missing fields."""
    missing_fields: List[str] = []

    # 1. Personal Info (30 points total: 7.5 points each across 4 fields)
    personal_score = 0.0
    if user_profile is not None and user_profile.first_name and user_profile.first_name.strip():
        personal_score += 7.5
    else:
        missing_fields.append("First Name")

    if user_profile is not None and user_profile.phone and user_profile.phone.strip():
        personal_score += 7.5
    else:
        missing_fields.append("Phone Number")

    if user_profile is not None and user_profile.city and user_profile.city.strip():
        personal_score += 7.5
    else:
        missing_fields.append("City")

    if user_profile is not None and user_profile.state and user_profile.state.strip():
        personal_score += 7.5
    else:
        missing_fields.append("State")

    # 2. Academic Info (50 points total: 10 points each across 5 fields)
    academic_score = 0.0
    if student is not None and student.institution_id:
        academic_score += 10.0
    else:
        missing_fields.append("Institution")

    if student is not None and student.department_id:
        academic_score += 10.0
    else:
        missing_fields.append("Department")

    if student is not None and student.roll_number and student.roll_number.strip():
        academic_score += 10.0
    else:
        missing_fields.append("Roll Number")

    if student is not None and student.current_semester is not None and student.current_semester > 0:
        academic_score += 10.0
    else:
        missing_fields.append("Current Semester")

    if student is not None and student.cgpa is not None:
        academic_score += 10.0
    else:
        missing_fields.append("CGPA")

    # 3. Career Goal (20 points total: 20 points for target role)
    career_score = 0.0
    if student is not None and student.target_career_role_id:
        career_score += 20.0
    else:
        missing_fields.append("Target Career Role")

    total_percentage = int(round(personal_score + academic_score + career_score))
    personal_pct = int(round((personal_score / 30.0) * 100))
    academic_pct = int(round((academic_score / 50.0) * 100))
    career_pct = int(round((career_score / 20.0) * 100))

    is_complete = bool(
        user_profile is not None and user_profile.first_name and user_profile.first_name.strip() and
        student is not None and student.institution_id and student.department_id and
        student.roll_number and student.roll_number.strip() and student.target_career_role_id
    )

    return StudentProfileCompletionDetail(
        percentage=min(100, max(0, total_percentage)),
        is_complete=is_complete,
        personal_percentage=min(100, max(0, personal_pct)),
        academic_percentage=min(100, max(0, academic_pct)),
        career_percentage=min(100, max(0, career_pct)),
        missing_fields=missing_fields,
    )


@router.get(
    "/dashboard",
    response_model=StudentDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated student's dashboard summary",
    description="Aggregates live profile status, real metric counts, and career journey milestones from PostgreSQL.",
)
async def get_student_dashboard(
    current_user: User = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    # 1. Load Student academic record with related institution, department, target role
    stmt_student = (
        select(Student)
        .options(
            selectinload(Student.institution),
            selectinload(Student.department),
            selectinload(Student.target_career_role),
        )
        .where(Student.user_id == current_user.id)
    )
    res_student = await db.execute(stmt_student)
    student = res_student.scalar_one_or_none()

    # 2. Query real live counts from database
    assessed_skills_count = 0
    active_skill_gaps_count = 0
    active_roadmaps_count = 0
    completed_roadmap_steps_count = 0
    total_roadmap_steps_count = 0
    applications_count = 0
    active_internships_count = 0
    recognitions_count = 0

    if student is not None:
        # Assessed skills count
        stmt_skills = select(func.count(StudentSkill.id)).where(StudentSkill.student_id == student.id)
        assessed_skills_count = (await db.execute(stmt_skills)).scalar() or 0

        # Skill gaps count
        stmt_gaps = select(func.count(SkillGap.id)).where(SkillGap.student_id == student.id)
        active_skill_gaps_count = (await db.execute(stmt_gaps)).scalar() or 0

        # Active roadmaps count
        stmt_roadmaps = select(func.count(Roadmap.id)).where(
            Roadmap.student_id == student.id,
            Roadmap.status == "ACTIVE",
        )
        active_roadmaps_count = (await db.execute(stmt_roadmaps)).scalar() or 0

        # Completed roadmap steps
        stmt_comp_steps = (
            select(func.count(RoadmapItem.id))
            .join(Roadmap, RoadmapItem.roadmap_id == Roadmap.id)
            .where(Roadmap.student_id == student.id, RoadmapItem.status == "COMPLETED")
        )
        completed_roadmap_steps_count = (await db.execute(stmt_comp_steps)).scalar() or 0

        # Total roadmap steps
        stmt_tot_steps = (
            select(func.count(RoadmapItem.id))
            .join(Roadmap, RoadmapItem.roadmap_id == Roadmap.id)
            .where(Roadmap.student_id == student.id)
        )
        total_roadmap_steps_count = (await db.execute(stmt_tot_steps)).scalar() or 0

        # Applications count
        stmt_apps = select(func.count(Application.id)).where(Application.student_id == student.id)
        applications_count = (await db.execute(stmt_apps)).scalar() or 0

        # Active internships count
        stmt_internships = select(func.count(Internship.id)).where(
            Internship.student_id == student.id,
            Internship.status == "ACTIVE",
        )
        active_internships_count = (await db.execute(stmt_internships)).scalar() or 0

        # Recognitions count
        stmt_rec = select(func.count(Recognition.id)).where(Recognition.student_id == student.id)
        recognitions_count = (await db.execute(stmt_rec)).scalar() or 0

    # Unread notifications count
    stmt_notif = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False),
    )
    unread_notifications_count = (await db.execute(stmt_notif)).scalar() or 0

    metrics = StudentMetrics(
        assessed_skills_count=assessed_skills_count,
        active_skill_gaps_count=active_skill_gaps_count,
        active_roadmaps_count=active_roadmaps_count,
        completed_roadmap_steps_count=completed_roadmap_steps_count,
        total_roadmap_steps_count=total_roadmap_steps_count,
        applications_count=applications_count,
        active_internships_count=active_internships_count,
        recognitions_count=recognitions_count,
        unread_notifications_count=unread_notifications_count,
    )

    # 3. Compute completion breakdown
    completion_detail = calculate_profile_completion(current_user.profile, student)

    # 4. Compute Journey status
    has_academic = student is not None and bool(student.institution_id and student.department_id and student.roll_number)
    has_target = student is not None and student.target_career_role_id is not None
    journey_status = StudentJourneyStatus(
        profile_completed=completion_detail.is_complete,
        target_role_selected=has_target,
        skills_assessed=assessed_skills_count > 0,
        roadmap_active=active_roadmaps_count > 0,
        internship_active=(active_internships_count > 0 or applications_count > 0),
    )

    announcements = [
        "Welcome to the SKILLY Student Portal. Complete your academic profile to unlock personalized roadmaps.",
        "Diagnostic skill benchmarking and industry internship drives are being scheduled for your batch.",
    ]

    return StudentDashboardResponse(
        user=current_user,
        academic_profile=student,
        metrics=metrics,
        journey_status=journey_status,
        completion=completion_detail,
        recent_announcements=announcements,
    )


@router.get(
    "/profile",
    response_model=StudentProfileRead,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated student's full profile",
    description="Returns personal biographical info, academic details, and deterministic completion breakdown.",
)
async def get_student_profile(
    current_user: User = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Student)
        .options(
            selectinload(Student.institution),
            selectinload(Student.department),
            selectinload(Student.target_career_role),
        )
        .where(Student.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()

    completion_detail = calculate_profile_completion(current_user.profile, student)

    return StudentProfileRead(
        user=current_user,
        academic_profile=student,
        is_profile_complete=completion_detail.is_complete,
        completion=completion_detail,
    )


@router.put(
    "/profile",
    response_model=StudentProfileRead,
    status_code=status.HTTP_200_OK,
    summary="Update authenticated student's profile & academic information",
    description="Updates biographical details and creates or updates the student's institutional and career goal record.",
)
async def update_student_profile(
    payload: StudentProfileUpdate,
    current_user: User = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    # 1. Update personal UserProfile entity
    stmt_prof = select(UserProfile).where(UserProfile.user_id == current_user.id)
    res_prof = await db.execute(stmt_prof)
    user_profile = res_prof.scalar_one_or_none()

    if user_profile is None:
        user_profile = UserProfile(
            user_id=current_user.id,
            first_name=payload.first_name or "User",
            last_name=payload.last_name or "",
            country="India",
        )
        db.add(user_profile)
        await db.flush()

    if payload.first_name is not None:
        user_profile.first_name = payload.first_name
    if payload.last_name is not None:
        user_profile.last_name = payload.last_name
    if payload.phone is not None:
        user_profile.phone = payload.phone
    if payload.bio is not None:
        user_profile.bio = payload.bio
    if payload.city is not None:
        user_profile.city = payload.city
    if payload.state is not None:
        user_profile.state = payload.state
    if payload.country is not None:
        user_profile.country = payload.country
    if payload.linkedin_url is not None:
        user_profile.linkedin_url = payload.linkedin_url
    if payload.github_url is not None:
        user_profile.github_url = payload.github_url
    if payload.website_url is not None:
        user_profile.website_url = payload.website_url

    # 2. Update or Create Student entity
    stmt_st = select(Student).where(Student.user_id == current_user.id)
    res_st = await db.execute(stmt_st)
    student = res_st.scalar_one_or_none()

    # Check graduation_year >= enrollment_year
    current_year = datetime.now().year
    effective_enrollment = (
        payload.enrollment_year
        if payload.enrollment_year is not None
        else (student.enrollment_year if student else (current_year - 1))
    )
    effective_graduation = (
        payload.graduation_year
        if payload.graduation_year is not None
        else (student.graduation_year if student else (current_year + 3))
    )

    if effective_graduation < effective_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Graduation year cannot be earlier than enrollment year.",
        )

    # If any academic field or target role is passed
    academic_fields_provided = any([
        payload.institution_id is not None,
        payload.department_id is not None,
        payload.roll_number is not None,
        payload.enrollment_year is not None,
        payload.graduation_year is not None,
        payload.current_semester is not None,
        payload.cgpa is not None,
        payload.target_career_role_id is not None,
    ])

    if academic_fields_provided:
        # If target career role is specified, validate it exists and is active
        if payload.target_career_role_id is not None:
            stmt_cr = select(CareerRole).where(
                CareerRole.id == payload.target_career_role_id,
                CareerRole.is_active.is_(True),
            )
            cr_res = await db.execute(stmt_cr)
            if cr_res.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="The selected target career role does not exist or is inactive.",
                )

        if student is None:
            # Validate required fields for student creation
            if not payload.institution_id or not payload.department_id or not payload.roll_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Institution, Department, and Roll Number are required to initialize your academic profile.",
                )

            # Validate department belongs to institution
            stmt_dept = select(Department).where(
                Department.id == payload.department_id,
                Department.institution_id == payload.institution_id,
            )
            dept_res = await db.execute(stmt_dept)
            if dept_res.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The selected Department does not belong to the selected Institution.",
                )

            student = Student(
                user_id=current_user.id,
                institution_id=payload.institution_id,
                department_id=payload.department_id,
                roll_number=payload.roll_number,
                enrollment_year=effective_enrollment,
                graduation_year=effective_graduation,
                current_semester=payload.current_semester or 1,
                cgpa=payload.cgpa,
                target_career_role_id=payload.target_career_role_id,
            )
            db.add(student)
        else:
            # Update existing student record
            target_inst_id = payload.institution_id or student.institution_id
            target_dept_id = payload.department_id or student.department_id

            if payload.institution_id is not None or payload.department_id is not None:
                # Validate department belongs to institution
                stmt_dept = select(Department).where(
                    Department.id == target_dept_id,
                    Department.institution_id == target_inst_id,
                )
                dept_res = await db.execute(stmt_dept)
                if dept_res.scalar_one_or_none() is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="The selected Department does not belong to the selected Institution.",
                    )
                student.institution_id = target_inst_id
                student.department_id = target_dept_id

            if payload.roll_number is not None:
                student.roll_number = payload.roll_number
            if payload.enrollment_year is not None:
                student.enrollment_year = payload.enrollment_year
            if payload.graduation_year is not None:
                student.graduation_year = payload.graduation_year
            if payload.current_semester is not None:
                student.current_semester = payload.current_semester
            if payload.cgpa is not None:
                student.cgpa = payload.cgpa
            if payload.target_career_role_id is not None:
                student.target_career_role_id = payload.target_career_role_id


    await db.commit()

    # Reload fresh user and student profile
    stmt_user = select(User).options(selectinload(User.profile)).where(User.id == current_user.id)
    fresh_user = (await db.execute(stmt_user)).scalar_one()

    stmt_reloaded_st = (
        select(Student)
        .options(
            selectinload(Student.institution),
            selectinload(Student.department),
            selectinload(Student.target_career_role),
        )
        .where(Student.user_id == current_user.id)
    )
    reloaded_st = (await db.execute(stmt_reloaded_st)).scalar_one_or_none()

    completion_detail = calculate_profile_completion(fresh_user.profile, reloaded_st)

    return StudentProfileRead(
        user=fresh_user,
        academic_profile=reloaded_st,
        is_profile_complete=completion_detail.is_complete,
        completion=completion_detail,
    )


# -------------------------------------------------------------
# Lookup Endpoints for Dropdown Selectors
# -------------------------------------------------------------

@router.get(
    "/institutions",
    response_model=List[InstitutionSimple],
    status_code=status.HTTP_200_OK,
    summary="List partner academic institutions",
    description="Returns available institutions for student affiliation selection.",
)
async def list_institutions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt = select(Institution).order_by(Institution.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/departments",
    response_model=List[DepartmentSimple],
    status_code=status.HTTP_200_OK,
    summary="List departments for an institution",
    description="Returns departments associated with the specified institution ID.",
)
async def list_departments(
    institution_id: uuid.UUID = Query(..., description="ID of the institution"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt = select(Department).where(Department.institution_id == institution_id).order_by(Department.name)
    result = await db.execute(stmt)
    return result.scalars().all()


# -------------------------------------------------------------
# Career Workspace & Role Catalog Endpoints (Module 03 — Phase 3.3)
# -------------------------------------------------------------

def format_career_role_detail(
    role: CareerRole,
    is_current_target: bool = False,
) -> CareerRoleDetailRead:
    """Canonical formatter for career role specification and required skills breakdown."""
    order_map = {"CORE": 1, "RECOMMENDED": 2, "OPTIONAL": 3}
    sorted_skills = sorted(
        role.role_skills or [],
        key=lambda rs: (
            order_map.get(rs.importance_level, 99),
            rs.skill.name if rs.skill else "",
        ),
    )

    skills_list = []
    for rs in sorted_skills:
        if rs.skill:
            skills_list.append(
                CareerRoleSkillDetail(
                    skill_id=rs.skill_id,
                    skill_name=rs.skill.name,
                    category=rs.skill.category,
                    required_level=rs.required_level,
                    importance_level=rs.importance_level,
                    description=rs.skill.description,
                )
            )

    return CareerRoleDetailRead(
        id=role.id,
        title=role.title,
        slug=role.slug,
        industry_domain=role.industry_domain,
        description=role.description,
        is_active=role.is_active,
        required_skills=skills_list,
        is_current_target=is_current_target,
    )


@router.get(
    "/career-workspace",
    response_model=StudentCareerWorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get student career workspace overview",
    description="Returns current target career goal details with required skills, total role counts, and profile completion status.",
)
async def get_student_career_workspace(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    # 1. Fetch Student profile
    stmt_student = (
        select(Student)
        .options(selectinload(Student.target_career_role))
        .where(Student.user_id == current_user.id)
    )
    student = (await db.execute(stmt_student)).scalar_one_or_none()

    # 2. Total active roles count
    stmt_count = select(func.count(CareerRole.id)).where(CareerRole.is_active.is_(True))
    available_roles_count = (await db.execute(stmt_count)).scalar() or 0

    # 3. Load target role with role_skills and skills if present
    current_target_role = None
    if student and student.target_career_role_id:
        stmt_role = (
            select(CareerRole)
            .options(
                selectinload(CareerRole.role_skills).selectinload(CareerRoleSkill.skill)
            )
            .where(CareerRole.id == student.target_career_role_id, CareerRole.is_active.is_(True))
        )
        target_role_entity = (await db.execute(stmt_role)).scalar_one_or_none()
        if target_role_entity:
            current_target_role = format_career_role_detail(target_role_entity, is_current_target=True)

    # 4. Profile completion
    completion_detail = calculate_profile_completion(current_user.profile, student)

    return StudentCareerWorkspaceResponse(
        current_target_role=current_target_role,
        available_roles_count=available_roles_count,
        completion=completion_detail,
    )


@router.get(
    "/career-roles",
    response_model=List[CareerRoleListItem],
    status_code=status.HTTP_200_OK,
    summary="List active career roles",
    description="Returns active career roles with domain filtering, search, and skill requirement counts.",
)
async def list_career_roles(
    domain: Optional[str] = Query(None, description="Filter by industry domain"),
    search: Optional[str] = Query(None, description="Search keyword in title, description, or domain"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    # Find current student target role id
    stmt_st = select(Student.target_career_role_id).where(Student.user_id == current_user.id)
    target_role_id = (await db.execute(stmt_st)).scalar_one_or_none()

    stmt = (
        select(CareerRole)
        .options(selectinload(CareerRole.role_skills))
        .where(CareerRole.is_active.is_(True))
    )

    if domain and domain.strip():
        stmt = stmt.where(CareerRole.industry_domain.ilike(f"%{domain.strip()}%"))
    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            (CareerRole.title.ilike(term)) |
            (CareerRole.description.ilike(term)) |
            (CareerRole.industry_domain.ilike(term))
        )

    stmt = stmt.order_by(CareerRole.title)
    result = await db.execute(stmt)
    roles = result.scalars().all()

    items = []
    for r in roles:
        skills = r.role_skills or []
        core_count = sum(1 for s in skills if s.importance_level == "CORE")
        items.append(
            CareerRoleListItem(
                id=r.id,
                title=r.title,
                slug=r.slug,
                industry_domain=r.industry_domain,
                description=r.description,
                skills_count=len(skills),
                core_skills_count=core_count,
                is_current_target=bool(target_role_id and target_role_id == r.id),
            )
        )
    return items


@router.get(
    "/career-roles/{role_id}",
    response_model=CareerRoleDetailRead,
    status_code=status.HTTP_200_OK,
    summary="Get detailed career role specification",
    description="Returns comprehensive details of a career role with its required skills hierarchy.",
)
async def get_career_role_detail(
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    # Find current student target role id
    stmt_st = select(Student.target_career_role_id).where(Student.user_id == current_user.id)
    target_role_id = (await db.execute(stmt_st)).scalar_one_or_none()

    stmt = (
        select(CareerRole)
        .options(
            selectinload(CareerRole.role_skills).selectinload(CareerRoleSkill.skill)
        )
        .where(CareerRole.id == role_id, CareerRole.is_active.is_(True))
    )
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career role not found or is currently inactive.",
        )

    is_current = bool(target_role_id and target_role_id == role.id)
    return format_career_role_detail(role, is_current_target=is_current)


@router.put(
    "/target-role",
    response_model=TargetCareerRoleResponse,
    status_code=status.HTTP_200_OK,
    summary="Set or update student target career role",
    description="Updates the authenticated student's target career role and returns recomputed profile completion.",
)
async def set_target_career_role(
    payload: TargetCareerRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    # 1. Validate target career role exists and is active
    stmt_role = (
        select(CareerRole)
        .options(
            selectinload(CareerRole.role_skills).selectinload(CareerRoleSkill.skill)
        )
        .where(CareerRole.id == payload.career_role_id, CareerRole.is_active.is_(True))
    )
    role_res = await db.execute(stmt_role)
    target_role = role_res.scalar_one_or_none()
    if target_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested career role does not exist or is inactive.",
        )

    # 2. Load or create student entity
    stmt_st = select(Student).where(Student.user_id == current_user.id)
    student = (await db.execute(stmt_st)).scalar_one_or_none()

    if student is None:
        # Check if an institution/dept exists to initialize student record
        inst_dept = (
            await db.execute(
                select(Department.institution_id, Department.id).limit(1)
            )
        ).first()
        if inst_dept:
            curr_year = datetime.now().year
            student = Student(
                user_id=current_user.id,
                institution_id=inst_dept.institution_id,
                department_id=inst_dept.id,
                roll_number=f"TEMP-{current_user.id.hex[:6].upper()}",
                enrollment_year=curr_year - 1,
                graduation_year=curr_year + 3,
                current_semester=1,
                target_career_role_id=payload.career_role_id,
            )
            db.add(student)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please complete your academic profile with an institution and department first.",
            )
    else:
        student.target_career_role_id = payload.career_role_id

    await db.commit()

    # 3. Reload fresh user and completion
    stmt_user = select(User).options(selectinload(User.profile)).where(User.id == current_user.id)
    fresh_user = (await db.execute(stmt_user)).scalar_one()
    completion_detail = calculate_profile_completion(fresh_user.profile, student)

    role_detail = format_career_role_detail(target_role, is_current_target=True)

    return TargetCareerRoleResponse(
        message=f"Successfully set '{target_role.title}' as your target career goal.",
        target_career_role=role_detail,
        completion=completion_detail,
    )


# -------------------------------------------------------------
# Phase 3.4 — Milestone Career Roadmap & Learning APIs
# -------------------------------------------------------------

@router.get(
    "/roadmap",
    response_model=RoadmapOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated student's active career roadmap",
    description="Returns active roadmap details, milestone checkpoints, total study hours, and completion percentage.",
)
async def get_student_roadmap(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    # 1. Fetch Student profile
    stmt_st = (
        select(Student)
        .options(selectinload(Student.target_career_role))
        .where(Student.user_id == current_user.id)
    )
    student = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student or not student.target_career_role_id:
        return RoadmapOverviewResponse(
            has_target_role=False,
            has_active_roadmap=False,
        )

    target_role_simple = CareerRoleSimple(
        id=student.target_career_role.id,
        title=student.target_career_role.title,
        slug=student.target_career_role.slug,
        industry_domain=student.target_career_role.industry_domain,
        description=student.target_career_role.description,
    )

    # 2. Get active roadmap or auto-sync if missing
    roadmap = await get_student_active_roadmap(db, student.id)
    if not roadmap:
        # Auto-generate roadmap on first access if target role is set
        try:
            roadmap = await generate_or_sync_student_roadmap(db, student, force_regenerate=False)
        except Exception:
            roadmap = None

    if not roadmap:
        return RoadmapOverviewResponse(
            has_target_role=True,
            has_active_roadmap=False,
            target_career_role=target_role_simple,
        )

    items = roadmap.items or []
    total_steps = len(items)
    completed_steps = sum(1 for item in items if item.status == "COMPLETED")
    total_estimated_hours = sum(item.estimated_hours or 0 for item in items)
    pct = int(round((completed_steps / total_steps) * 100)) if total_steps > 0 else 0

    return RoadmapOverviewResponse(
        has_target_role=True,
        has_active_roadmap=True,
        target_career_role=target_role_simple,
        roadmap=roadmap,
        total_steps=total_steps,
        completed_steps=completed_steps,
        total_estimated_hours=total_estimated_hours,
        completion_percentage=pct,
    )


@router.post(
    "/roadmap/generate",
    response_model=RoadmapOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate or synchronize student career roadmap",
    description="Deterministically builds or synchronizes roadmap steps based on target role required skills.",
)
async def generate_student_roadmap_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student).where(Student.user_id == current_user.id)
    student = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student or not student.target_career_role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select a target career role before generating a roadmap.",
        )

    try:
        await generate_or_sync_student_roadmap(db, student, force_regenerate=True)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    return await get_student_roadmap(db=db, current_user=current_user)


@router.put(
    "/roadmap/items/{item_id}",
    response_model=RoadmapItemRead,
    status_code=status.HTTP_200_OK,
    summary="Update roadmap step status",
    description="Updates status (PENDING, IN_PROGRESS, COMPLETED) of a specific roadmap checkpoint step with IDOR validation.",
)
async def update_roadmap_item_status_endpoint(
    item_id: uuid.UUID,
    payload: RoadmapItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student.id).where(Student.user_id == current_user.id)
    student_id = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    try:
        updated_item = await update_roadmap_item_status(db, student_id, item_id, payload.status)
        return updated_item
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap item not found or unauthorized.",
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )


@router.get(
    "/learning",
    response_model=StudentLearningWorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get student learning and training programs workspace",
    description="Returns available training bootcamps/workshops and current student batch enrollments.",
)
async def get_student_learning_workspace_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student.id).where(Student.user_id == current_user.id)
    student_id = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student_id:
        return StudentLearningWorkspaceResponse()

    data = await get_student_learning_workspace(db, student_id)
    return StudentLearningWorkspaceResponse(**data)


@router.post(
    "/learning/enroll/{program_id}",
    response_model=TrainingEnrollmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll student in a training program",
    description="Enrolls authenticated student in an upcoming or ongoing training program with duplicate protection.",
)
async def enroll_in_training_program_endpoint(
    program_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student.id).where(Student.user_id == current_user.id)
    student_id = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    try:
        enrollment = await enroll_student_in_training(db, student_id, program_id)
        return enrollment
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


# -------------------------------------------------------------
# Phase 3.5 — Skill Assessment & Diagnostic Benchmarking APIs
# -------------------------------------------------------------

@router.get(
    "/assessments",
    response_model=List[AssessmentCatalogItem],
    status_code=status.HTTP_200_OK,
    summary="List active diagnostic assessments",
    description="Returns available skill assessments catalog with student's best score and attempt counts.",
)
async def list_student_assessments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student.id).where(Student.user_id == current_user.id)
    student_id = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student_id:
        return []

    return await get_assessment_catalog(db, student_id)


@router.get(
    "/assessments/{assessment_id}",
    response_model=AssessmentDetail,
    status_code=status.HTTP_200_OK,
    summary="Get assessment detail & instructions",
    description="Returns metadata, target skill, duration, and question count prior to test start.",
)
async def get_student_assessment_detail(
    assessment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    try:
        return await get_assessment_detail(db, assessment_id)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.post(
    "/assessments/{assessment_id}/start",
    response_model=AssessmentAttemptRead,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new assessment attempt session",
    description="Initializes test attempt record and returns public questions (without correct_answer).",
)
async def start_student_assessment(
    assessment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student.id).where(Student.user_id == current_user.id)
    student_id = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    try:
        return await start_assessment_attempt(db, student_id, assessment_id)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.get(
    "/assessment-attempts/{attempt_id}",
    response_model=AssessmentAttemptRead,
    status_code=status.HTTP_200_OK,
    summary="Get active or completed attempt session",
    description="Returns session state and questions (without correct_answer) with strict IDOR verification.",
)
async def get_student_assessment_attempt(
    attempt_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student.id).where(Student.user_id == current_user.id)
    student_id = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    try:
        return await get_assessment_attempt(db, student_id, attempt_id)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.post(
    "/assessment-attempts/{attempt_id}/submit",
    response_model=AssessmentResult,
    status_code=status.HTTP_200_OK,
    summary="Submit answers and grade assessment attempt",
    description="Grades answers deterministically, updates skill passport & evidence, syncs gaps and roadmap.",
)
async def submit_student_assessment_attempt(
    attempt_id: uuid.UUID,
    payload: AssessmentSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student.id).where(Student.user_id == current_user.id)
    student_id = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    try:
        result = await submit_assessment_attempt(db, student_id, attempt_id, payload.responses)
        return result
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get(
    "/assessment-history",
    response_model=List[AssessmentHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get student assessment history",
    description="Returns completed assessment attempts history for the authenticated student.",
)
async def get_student_assessment_history_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student.id).where(Student.user_id == current_user.id)
    student_id = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student_id:
        return []

    return await get_student_assessment_history(db, student_id)


# -------------------------------------------------------------
# Module 08 — Canonical Student Skills & Skill Gap Endpoints
# -------------------------------------------------------------

@router.get(
    "/skills",
    status_code=status.HTTP_200_OK,
    summary="Get authenticated student's assessed skill profile",
    description="Returns student's assessed skills taxonomy and attached digital evidence.",
)
async def get_student_skills_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student.id).where(Student.user_id == current_user.id)
    student_id = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student_id:
        return []

    return await get_student_skills_profile(db, student_id)


@router.get(
    "/skill-gaps",
    status_code=status.HTTP_200_OK,
    summary="Get authenticated student's deterministic skill gap analysis",
    description="Calculates competency gaps between student's assessed skills and target career role requirements.",
)
async def get_student_skill_gaps_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    stmt_st = select(Student.id).where(Student.user_id == current_user.id)
    student_id = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student_id:
        return {
            "has_target_role": False,
            "target_career_role": None,
            "summary": {"satisfied_count": 0, "insufficient_count": 0, "missing_count": 0, "total_required": 0},
            "gaps": [],
        }

    return await calculate_student_skill_gaps(db, student_id)


# =====================================================================
# Phase 9 — Internship & Placement Lifecycle Endpoints
# =====================================================================

@router.get(
    "/opportunities",
    response_model=List[OpportunityStudentRead],
    status_code=status.HTTP_200_OK,
    summary="Get open industry opportunities with eligibility & skill matching",
)
async def get_student_opportunities(
    status: Optional[str] = Query("OPEN"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    return await InternshipService.get_student_opportunities(db, current_user, status_filter=status)


@router.get(
    "/opportunities/{id}",
    response_model=OpportunityStudentRead,
    status_code=status.HTTP_200_OK,
    summary="Get detailed opportunity view with eligibility and skill match",
)
async def get_student_opportunity_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await InternshipService.get_opportunity_detail(db, current_user, id)


@router.post(
    "/opportunities/{id}/apply",
    response_model=StudentApplicationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit application to an industry opportunity",
)
async def apply_to_opportunity(
    id: uuid.UUID,
    payload: StudentApplicationApplyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await InternshipService.apply_to_opportunity(db, current_user, id, payload)


@router.get(
    "/applications",
    response_model=List[StudentApplicationRead],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated student's submitted applications",
)
async def get_student_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await InternshipService.get_student_applications(db, current_user)


@router.get(
    "/applications/{id}",
    response_model=StudentApplicationRead,
    status_code=status.HTTP_200_OK,
    summary="Get application detail for student",
)
async def get_student_application_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await InternshipService.get_student_application_detail(db, current_user, id)


@router.get(
    "/applications/{id}/history",
    response_model=List[StudentApplicationStatusHistoryRead],
    status_code=status.HTTP_200_OK,
    summary="Get application status transition history timeline",
)
async def get_student_application_history(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await InternshipService.get_student_application_history(db, current_user, id)


@router.get(
    "/internships",
    response_model=List[StudentInternshipRead],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated student's active and completed internships",
)
async def get_student_internships(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await InternshipService.get_student_internships(db, current_user)


@router.get(
    "/internships/{id}",
    response_model=StudentInternshipRead,
    status_code=status.HTTP_200_OK,
    summary="Get detailed view of a student internship including progress & evaluation",
)
async def get_student_internship_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await InternshipService.get_student_internship_detail(db, current_user, id)


@router.get(
    "/internships/{id}/progress",
    response_model=List[StudentInternshipProgressRead],
    status_code=status.HTTP_200_OK,
    summary="Get progress report logs for an internship",
)
async def get_student_internship_progress(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    internship = await InternshipService.get_student_internship_detail(db, current_user, id)
    return internship.progress_reports


@router.post(
    "/internships/{id}/progress",
    response_model=StudentInternshipProgressRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit weekly internship progress log",
)
async def submit_student_internship_progress(
    id: uuid.UUID,
    payload: StudentInternshipProgressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await InternshipService.submit_internship_progress(db, current_user, id, payload)


@router.get(
    "/placements",
    response_model=List[StudentPlacementRecordRead],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated student's confirmed placement records",
)
async def get_student_placements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await InternshipService.get_student_placements(db, current_user)


# =====================================================================
# Digital Portfolio & Structured Resume Endpoints
# =====================================================================

@router.get(
    "/portfolio",
    response_model=DigitalPortfolioRead,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated student's aggregated Digital Portfolio & Skill Passport",
)
async def get_digital_portfolio(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await PortfolioService.get_digital_portfolio(db, current_user)


@router.post(
    "/portfolio/projects",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add project / technical deliverable to portfolio",
)
async def add_portfolio_project(
    payload: ProjectCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await PortfolioService.add_project(db, current_user, payload)


@router.delete(
    "/portfolio/projects/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete portfolio project",
)
async def delete_portfolio_project(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    await PortfolioService.delete_project(db, current_user, id)


@router.post(
    "/portfolio/recognitions",
    response_model=RecognitionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add certification, badge, or achievement recognition to portfolio",
)
async def add_portfolio_recognition(
    payload: RecognitionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await PortfolioService.add_recognition(db, current_user, payload)


@router.post(
    "/portfolio/evidence",
    response_model=SkillEvidenceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Attach verified digital evidence to a student skill",
)
async def add_skill_evidence(
    payload: SkillEvidenceCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await PortfolioService.add_skill_evidence(db, current_user, payload)


@router.post(
    "/resumes/generate",
    response_model=ResumeVersionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate structured JSON resume & version from digital portfolio",
)
async def generate_structured_resume(
    payload: ResumeGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await PortfolioService.generate_structured_resume(db, current_user, payload)


@router.get(
    "/resumes",
    response_model=List[ResumeVersionRead],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated student's saved resume versions",
)
async def get_student_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await PortfolioService.get_student_resumes(db, current_user)


@router.get(
    "/resumes/{id}",
    response_model=ResumeVersionRead,
    status_code=status.HTTP_200_OK,
    summary="Get detailed saved resume version with structured JSON content",
)
async def get_student_resume_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
):
    return await PortfolioService.get_student_resume_detail(db, current_user, id)






