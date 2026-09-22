import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct
from sqlalchemy.orm import selectinload, joinedload

from app.models.institutions import Institution, Department, InstitutionStaff, Teacher, Student
from app.models.users import User, UserProfile
from app.models.opportunities import Opportunity, Application
from app.models.companies import Company
from app.models.placements import PlacementRecord
from app.models.skills import Skill, StudentSkill
from app.models.careers import SkillGap, CareerRole
from app.schemas.college import (
    CollegeDashboardResponse,
    TopSkillGapItem,
    DepartmentItem,
    FacultyItem,
    StudentRosterItem,
    StudentRosterResponse,
    SkillAnalyticsResponse,
    SkillGapAnalyticsItem,
    CampusDriveItem,
    ShortlistRequest,
    ShortlistResponse,
    ShortlistedStudentItem,
    RecordPlacementRequest,
    PlacementRecordResponse
)


async def get_staff_context(db: AsyncSession, user_id: uuid.UUID) -> Optional[InstitutionStaff]:
    """Retrieve InstitutionStaff context for a COLLEGE_ADMIN user."""
    stmt = (
        select(InstitutionStaff)
        .options(selectinload(InstitutionStaff.institution))
        .where(InstitutionStaff.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_teacher_context(db: AsyncSession, user_id: uuid.UUID) -> Optional[Teacher]:
    """Retrieve Teacher context for a TEACHER user."""
    stmt = (
        select(Teacher)
        .options(selectinload(Teacher.institution), selectinload(Teacher.department))
        .where(Teacher.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_dashboard_metrics(
    db: AsyncSession,
    institution_id: uuid.UUID
) -> CollegeDashboardResponse:
    """Aggregate real-time live database metrics for an institution's dashboard."""
    # 1. Institution Name
    inst_stmt = select(Institution.name).where(Institution.id == institution_id)
    inst_res = await db.execute(inst_stmt)
    inst_name = inst_res.scalar_one_or_none() or "Institution"

    # 2. Total Students
    stud_count_stmt = select(func.count(Student.id)).where(Student.institution_id == institution_id)
    total_students = (await db.execute(stud_count_stmt)).scalar() or 0

    # 3. Total Departments
    dept_count_stmt = select(func.count(Department.id)).where(Department.institution_id == institution_id)
    total_departments = (await db.execute(dept_count_stmt)).scalar() or 0

    # 4. Active Campus Drives (Open Opportunities)
    drives_stmt = select(func.count(Opportunity.id)).where(Opportunity.status == "OPEN")
    active_drives = (await db.execute(drives_stmt)).scalar() or 0

    # 5. Placements (Students with confirmed placement records)
    placements_stmt = (
        select(
            func.count(distinct(PlacementRecord.student_id)),
            func.avg(PlacementRecord.package_lpa),
            func.max(PlacementRecord.package_lpa)
        )
        .join(Student, PlacementRecord.student_id == Student.id)
        .where(Student.institution_id == institution_id)
    )
    placed_res = (await db.execute(placements_stmt)).first()
    total_placements = placed_res[0] if placed_res and placed_res[0] else 0
    avg_package = float(placed_res[1]) if placed_res and placed_res[1] else 0.0
    highest_package = float(placed_res[2]) if placed_res and placed_res[2] else 0.0

    # Placement Rate Percentage
    placement_rate = (total_placements / total_students * 100.0) if total_students > 0 else 0.0

    # 6. Top Skill Gaps in Institution
    skill_gap_stmt = (
        select(
            Skill.id,
            Skill.name,
            func.count(distinct(SkillGap.student_id)).label("gap_count")
        )
        .join(SkillGap, Skill.id == SkillGap.skill_id)
        .join(Student, SkillGap.student_id == Student.id)
        .where(Student.institution_id == institution_id)
        .group_by(Skill.id, Skill.name)
        .order_by(func.count(distinct(SkillGap.student_id)).desc())
        .limit(5)
    )
    gap_res = (await db.execute(skill_gap_stmt)).all()
    top_skill_gaps = [
        TopSkillGapItem(
            skill_id=row[0],
            skill_name=row[1],
            student_count=row[2]
        )
        for row in gap_res
    ]

    return CollegeDashboardResponse(
        institution_id=institution_id,
        institution_name=inst_name,
        total_students=total_students,
        total_departments=total_departments,
        active_drives=active_drives,
        total_placements=total_placements,
        placement_rate_percentage=round(placement_rate, 1),
        average_package_lpa=round(avg_package, 2),
        highest_package_lpa=round(highest_package, 2),
        top_skill_gaps=top_skill_gaps
    )


async def get_departments_list(
    db: AsyncSession,
    institution_id: uuid.UUID
) -> List[DepartmentItem]:
    """Retrieve all academic departments with student and faculty counts."""
    stmt = select(Department).where(Department.institution_id == institution_id).order_by(Department.name)
    departments = (await db.execute(stmt)).scalars().all()

    items = []
    for dept in departments:
        # Count students in department
        s_count = (await db.execute(
            select(func.count(Student.id)).where(
                Student.institution_id == institution_id,
                Student.department_id == dept.id
            )
        )).scalar() or 0

        # Count faculty (teachers) in department
        f_count = (await db.execute(
            select(func.count(Teacher.id)).where(
                Teacher.institution_id == institution_id,
                Teacher.department_id == dept.id
            )
        )).scalar() or 0

        items.append(
            DepartmentItem(
                id=dept.id,
                name=dept.name,
                code=dept.code,
                student_count=s_count,
                faculty_count=f_count,
                created_at=dept.created_at if hasattr(dept, 'created_at') and dept.created_at else datetime.now(timezone.utc)
            )
        )
    return items


async def get_faculty_directory(
    db: AsyncSession,
    institution_id: uuid.UUID
) -> List[FacultyItem]:
    """Retrieve staff and teacher directory for an institution."""
    faculty_list = []

    # 1. Staff Members
    staff_stmt = (
        select(InstitutionStaff)
        .options(
            joinedload(InstitutionStaff.user).joinedload(User.profile)
        )
        .where(InstitutionStaff.institution_id == institution_id)
    )
    staff_members = (await db.execute(staff_stmt)).scalars().all()

    for s in staff_members:
        profile = s.user.profile if s.user else None
        first_name = profile.first_name if profile else "Staff"
        last_name = profile.last_name if profile else "Member"
        email = s.user.email if s.user else ""

        faculty_list.append(
            FacultyItem(
                id=s.id,
                user_id=s.user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                designation="TPO Staff",
                department_name="Placement Office",
                role_type="STAFF",
                staff_role=s.staff_role
            )
        )

    # 2. Teachers
    teacher_stmt = (
        select(Teacher)
        .options(
            joinedload(Teacher.user).joinedload(User.profile),
            joinedload(Teacher.department)
        )
        .where(Teacher.institution_id == institution_id)
    )
    teachers = (await db.execute(teacher_stmt)).scalars().all()

    for t in teachers:
        profile = t.user.profile if t.user else None
        first_name = profile.first_name if profile else "Faculty"
        last_name = profile.last_name if profile else "Member"
        email = t.user.email if t.user else ""
        dept_name = t.department.name if t.department else "Academic"

        faculty_list.append(
            FacultyItem(
                id=t.id,
                user_id=t.user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                designation=t.designation or "Assistant Professor",
                department_name=dept_name,
                role_type="TEACHER",
                staff_role=None
            )
        )

    return faculty_list


async def get_student_roster(
    db: AsyncSession,
    institution_id: uuid.UUID,
    department_id: Optional[uuid.UUID] = None,
    graduation_year: Optional[int] = None,
    min_cgpa: Optional[float] = None,
    current_semester: Optional[int] = None,
    page: int = 1,
    limit: int = 20
) -> StudentRosterResponse:
    """Retrieve filterable, paginated student roster for an institution."""
    limit = max(1, min(100, limit))
    offset = (max(1, page) - 1) * limit

    conditions = [Student.institution_id == institution_id]

    if department_id:
        conditions.append(Student.department_id == department_id)
    if graduation_year:
        conditions.append(Student.graduation_year == graduation_year)
    if min_cgpa is not None:
        conditions.append(Student.cgpa >= min_cgpa)
    if current_semester:
        conditions.append(Student.current_semester == current_semester)

    # Count Total
    count_stmt = select(func.count(Student.id)).where(and_(*conditions))
    total_count = (await db.execute(count_stmt)).scalar() or 0

    # Query Students
    stmt = (
        select(Student)
        .options(
            joinedload(Student.user).joinedload(User.profile),
            joinedload(Student.department),
            joinedload(Student.target_career_role)
        )
        .where(and_(*conditions))
        .order_by(Student.roll_number.asc())
        .offset(offset)
        .limit(limit)
    )
    students = (await db.execute(stmt)).scalars().all()

    student_items = []
    for s in students:
        profile = s.user.profile if s.user else None
        first_name = profile.first_name if profile else "Student"
        last_name = profile.last_name if profile else ""
        email = s.user.email if s.user else ""
        dept_name = s.department.name if s.department else "Unassigned"
        target_role = s.target_career_role.title if s.target_career_role else None

        student_items.append(
            StudentRosterItem(
                id=s.id,
                user_id=s.user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                roll_number=s.roll_number,
                department_id=s.department_id,
                department_name=dept_name,
                enrollment_year=s.enrollment_year,
                graduation_year=s.graduation_year,
                current_semester=s.current_semester,
                cgpa=float(s.cgpa) if s.cgpa else 0.0,
                target_career_role=target_role
            )
        )

    return StudentRosterResponse(
        total_count=total_count,
        page=page,
        limit=limit,
        students=student_items
    )


async def get_skill_analytics(
    db: AsyncSession,
    institution_id: uuid.UUID,
    department_id: Optional[uuid.UUID] = None
) -> SkillAnalyticsResponse:
    """Aggregate batch skill proficiencies and critical skill gaps."""
    conditions = [Student.institution_id == institution_id]
    if department_id:
        conditions.append(Student.department_id == department_id)

    # Assessed Students
    assessed_stmt = (
        select(func.count(distinct(StudentSkill.student_id)))
        .join(Student, StudentSkill.student_id == Student.id)
        .where(and_(*conditions))
    )
    total_assessed = (await db.execute(assessed_stmt)).scalar() or 0

    # Skill Gap Aggregations
    gap_stmt = (
        select(
            Skill.id,
            Skill.name,
            Skill.category,
            func.count(distinct(SkillGap.student_id)).label("affected_students"),
            func.count(distinct(SkillGap.id)).label("total_gaps")
        )
        .join(SkillGap, Skill.id == SkillGap.skill_id)
        .join(Student, SkillGap.student_id == Student.id)
        .where(and_(*conditions))
        .group_by(Skill.id, Skill.name, Skill.category)
        .order_by(func.count(distinct(SkillGap.student_id)).desc())
        .limit(10)
    )
    gap_rows = (await db.execute(gap_stmt)).all()

    gap_items = [
        SkillGapAnalyticsItem(
            skill_id=row[0],
            skill_name=row[1],
            category=row[2],
            affected_students_count=row[3],
            critical_gap_count=row[4]
        )
        for row in gap_rows
    ]

    return SkillAnalyticsResponse(
        institution_id=institution_id,
        department_id=department_id,
        total_assessed_students=total_assessed,
        top_skill_gaps=gap_items
    )


async def get_institution_opportunities(
    db: AsyncSession,
    institution_id: uuid.UUID
) -> List[CampusDriveItem]:
    """Retrieve open placement opportunities available for campus drives."""
    stmt = (
        select(Opportunity)
        .options(joinedload(Opportunity.company))
        .where(Opportunity.status == "OPEN")
        .order_by(Opportunity.created_at.desc())
    )
    opportunities = (await db.execute(stmt)).scalars().all()

    drives = []
    for opp in opportunities:
        # Count applications for this opportunity from current institution
        app_count_stmt = (
            select(func.count(Application.id))
            .join(Student, Application.student_id == Student.id)
            .where(
                Application.opportunity_id == opp.id,
                Student.institution_id == institution_id
            )
        )
        app_count = (await db.execute(app_count_stmt)).scalar() or 0

        drives.append(
            CampusDriveItem(
                id=opp.id,
                company_id=opp.company_id,
                company_name=opp.company.name if opp.company else "Industry Partner",
                company_logo_url=opp.company.logo_url if opp.company else None,
                title=opp.title,
                role_type=opp.role_type,
                description=opp.description,
                location=opp.location,
                is_remote=opp.is_remote,
                stipend_salary=opp.stipend_salary,
                openings_count=opp.openings_count,
                application_deadline=opp.application_deadline,
                status=opp.status,
                total_applications=app_count
            )
        )
    return drives


async def filter_eligible_students(
    db: AsyncSession,
    institution_id: uuid.UUID,
    req: ShortlistRequest
) -> ShortlistResponse:
    """Deterministically filter students based on criteria (CGPA, Batch, Dept, Skills)."""
    # 1. Verify Opportunity Exists
    opp_stmt = select(Opportunity).where(Opportunity.id == req.opportunity_id)
    opp = (await db.execute(opp_stmt)).scalar_one_or_none()
    if not opp:
        raise ValueError("Opportunity not found.")

    # 2. Build Student Filter Conditions
    conditions = [Student.institution_id == institution_id]

    if req.min_cgpa > 0:
        conditions.append(Student.cgpa >= req.min_cgpa)
    if req.graduation_year:
        conditions.append(Student.graduation_year == req.graduation_year)
    if req.department_ids:
        conditions.append(Student.department_id.in_(req.department_ids))

    # Query Candidate Students
    stmt = (
        select(Student)
        .options(
            joinedload(Student.user).joinedload(User.profile),
            joinedload(Student.department)
        )
        .where(and_(*conditions))
    )
    candidates = (await db.execute(stmt)).scalars().all()

    shortlisted = []
    min_prof = req.min_proficiency or 1

    for s in candidates:
        matching_count = 0
        is_eligible = True

        if req.required_skill_ids:
            # Check student's skills
            skill_stmt = select(StudentSkill).where(
                StudentSkill.student_id == s.id,
                StudentSkill.skill_id.in_(req.required_skill_ids)
            )
            matched_skills = (await db.execute(skill_stmt)).scalars().all()
            matching_count = len(matched_skills)

            # If student lacks any required skill, mark ineligible if required skills are mandatory
            if matching_count < len(req.required_skill_ids):
                is_eligible = False

        if is_eligible:
            profile = s.user.profile if s.user else None
            first_name = profile.first_name if profile else "Student"
            last_name = profile.last_name if profile else ""
            email = s.user.email if s.user else ""
            dept_name = s.department.name if s.department else "Department"

            shortlisted.append(
                ShortlistedStudentItem(
                    student_id=s.id,
                    user_id=s.user_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    roll_number=s.roll_number,
                    department_name=dept_name,
                    cgpa=float(s.cgpa) if s.cgpa else 0.0,
                    graduation_year=s.graduation_year,
                    matching_skills_count=matching_count
                )
            )

    return ShortlistResponse(
        opportunity_id=opp.id,
        opportunity_title=opp.title,
        eligible_student_count=len(shortlisted),
        shortlisted_students=shortlisted
    )


async def record_confirmed_placement(
    db: AsyncSession,
    institution_id: uuid.UUID,
    req: RecordPlacementRequest
) -> PlacementRecordResponse:
    """Record a student's confirmed placement in placement_records table."""
    # 1. Verify Student belongs to institution
    stud_stmt = (
        select(Student)
        .options(joinedload(Student.user).joinedload(User.profile))
        .where(
            Student.id == req.student_id,
            Student.institution_id == institution_id
        )
    )
    student = (await db.execute(stud_stmt)).scalar_one_or_none()
    if not student:
        raise ValueError("Student not found in your institution.")

    profile = student.user.profile if student.user else None
    student_name = f"{profile.first_name} {profile.last_name}".strip() if profile else "Student"

    # 2. Query or create Company
    comp_stmt = select(Company).where(Company.name == req.company_name)
    company = (await db.execute(comp_stmt)).scalar_one_or_none()
    if not company:
        company = Company(name=req.company_name, industry_type="Technology")
        db.add(company)
        await db.flush()

    offer_date = req.placement_date.date() if req.placement_date else datetime.now(timezone.utc).date()

    record = PlacementRecord(
        student_id=student.id,
        company_id=company.id,
        institution_id=institution_id,
        package_lpa=req.package_amount,
        offer_date=offer_date,
        status="ACCEPTED"
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return PlacementRecordResponse(
        id=record.id,
        student_id=record.student_id,
        student_name=student_name,
        company_name=company.name,
        job_title=req.job_title,
        package_amount=float(record.package_lpa),
        placement_type=req.placement_type,
        status=record.status,
        placement_date=datetime.combine(record.offer_date, datetime.min.time(), tzinfo=timezone.utc)
    )
