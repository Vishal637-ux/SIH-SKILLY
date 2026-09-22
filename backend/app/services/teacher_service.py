import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct
from sqlalchemy.orm import selectinload, joinedload

from app.models.institutions import Institution, Department, Teacher, Student
from app.models.users import User, UserProfile
from app.models.training import TrainingProgram, TrainingEnrollment
from app.models.mentorship import MentorConnection, MentorshipSession
from app.models.community import Activity
from app.models.skills import Skill, StudentSkill
from app.models.careers import SkillGap, CareerRole
from app.models.placements import PlacementRecord
from app.schemas.teacher import (
    TeacherDashboardResponse,
    TopSkillGapItem,
    ActivityOverviewItem,
    TeacherProfileResponse,
    TeacherProfileUpdateRequest,
    DepartmentStudentItem,
    DepartmentStudentRosterResponse,
    TrainingProgramCreateRequest,
    TrainingProgramItem,
    TrainingProgramListResponse,
    EnrollmentStudentItem,
    TrainingProgramEnrollmentsResponse,
    EnrollmentUpdateRequest,
    MentorshipRequestItem,
    MentorshipSessionCreateRequest,
    MentorshipSessionResponse,
    ActivityCreateRequest,
    ActivityItem,
    ActivityListResponse,
    DepartmentAnalyticsResponse,
    CgpaDistribution
)


async def get_teacher_context(db: AsyncSession, user_id: uuid.UUID) -> Optional[Teacher]:
    """Retrieve Teacher context for a TEACHER user."""
    stmt = (
        select(Teacher)
        .options(
            selectinload(Teacher.institution),
            selectinload(Teacher.department),
            selectinload(Teacher.user).selectinload(User.profile)
        )
        .where(Teacher.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_teacher_dashboard(db: AsyncSession, teacher: Teacher) -> TeacherDashboardResponse:
    """Aggregate dashboard statistics for the authenticated teacher."""
    # 1. Total department students count
    stmt_students = (
        select(func.count(Student.id))
        .where(
            and_(
                Student.institution_id == teacher.institution_id,
                Student.department_id == teacher.department_id
            )
        )
    )
    total_students = (await db.execute(stmt_students)).scalar() or 0

    # 2. Programs conducted count
    stmt_programs = (
        select(func.count(TrainingProgram.id))
        .where(TrainingProgram.conducted_by_user_id == teacher.user_id)
    )
    programs_count = (await db.execute(stmt_programs)).scalar() or 0

    # 3. Active mentorships count
    stmt_mentorships = (
        select(func.count(MentorConnection.id))
        .where(
            and_(
                MentorConnection.mentor_user_id == teacher.user_id,
                MentorConnection.status == "ACCEPTED"
            )
        )
    )
    active_mentorships = (await db.execute(stmt_mentorships)).scalar() or 0

    # 4. Department top skill gaps
    stmt_gaps = (
        select(
            Skill.id.label("skill_id"),
            Skill.name.label("skill_name"),
            func.count(distinct(Student.id)).label("student_count")
        )
        .select_from(SkillGap)
        .join(Student, Student.id == SkillGap.student_id)
        .join(Skill, Skill.id == SkillGap.skill_id)
        .where(
            and_(
                Student.institution_id == teacher.institution_id,
                Student.department_id == teacher.department_id
            )
        )
        .group_by(Skill.id, Skill.name)
        .order_by(func.count(distinct(Student.id)).desc())
        .limit(5)
    )
    gaps_result = await db.execute(stmt_gaps)
    top_gaps = [
        TopSkillGapItem(
            skill_id=row.skill_id,
            skill_name=row.skill_name,
            student_count=row.student_count
        )
        for row in gaps_result.all()
    ]

    # 5. Recent activities
    stmt_activities = (
        select(Activity)
        .where(Activity.institution_id == teacher.institution_id)
        .order_by(Activity.start_time.desc())
        .limit(5)
    )
    activities_result = await db.execute(stmt_activities)
    recent_activities = [
        ActivityOverviewItem(
            id=act.id,
            title=act.title,
            activity_type=act.activity_type,
            start_time=act.start_time
        )
        for act in activities_result.scalars().all()
    ]

    return TeacherDashboardResponse(
        teacher_id=teacher.id,
        designation=teacher.designation,
        department_id=teacher.department_id,
        department_name=teacher.department.name if teacher.department else "Department",
        institution_id=teacher.institution_id,
        institution_name=teacher.institution.name if teacher.institution else "Institution",
        total_department_students=total_students,
        programs_conducted_count=programs_count,
        active_mentorships_count=active_mentorships,
        department_top_skill_gaps=top_gaps,
        recent_activities=recent_activities
    )


async def get_teacher_profile(db: AsyncSession, teacher: Teacher) -> TeacherProfileResponse:
    """Retrieve profile object for authenticated teacher."""
    user = teacher.user
    profile = user.profile if user else None

    return TeacherProfileResponse(
        id=teacher.id,
        user_id=teacher.user_id,
        email=user.email if user else "",
        username=user.username if user else "",
        first_name=profile.first_name if profile else "",
        last_name=profile.last_name if profile else "",
        phone=profile.phone if profile else None,
        avatar_url=profile.avatar_url if profile else None,
        bio=profile.bio if profile else None,
        city=profile.city if profile else None,
        state=profile.state if profile else None,
        country=profile.country if profile else None,
        linkedin_url=profile.linkedin_url if profile else None,
        github_url=profile.github_url if profile else None,
        website_url=profile.website_url if profile else None,
        designation=teacher.designation,
        employee_id=teacher.employee_id,
        specialization=teacher.specialization,
        is_trainer=teacher.is_trainer,
        institution_id=teacher.institution_id,
        institution_name=teacher.institution.name if teacher.institution else "",
        department_id=teacher.department_id,
        department_name=teacher.department.name if teacher.department else ""
    )


async def update_teacher_profile(
    db: AsyncSession,
    teacher: Teacher,
    update_req: TeacherProfileUpdateRequest
) -> TeacherProfileResponse:
    """Update profile and identity attributes for authenticated teacher."""
    user = teacher.user
    profile = user.profile if user else None

    if not profile:
        profile = UserProfile(user_id=user.id, first_name=update_req.first_name, last_name=update_req.last_name)
        db.add(profile)
        await db.flush()

    # Update profile fields
    profile.first_name = update_req.first_name
    profile.last_name = update_req.last_name
    profile.phone = update_req.phone
    profile.bio = update_req.bio
    profile.city = update_req.city
    profile.state = update_req.state
    profile.country = update_req.country or "India"
    profile.linkedin_url = update_req.linkedin_url
    profile.github_url = update_req.github_url
    profile.website_url = update_req.website_url

    # Update teacher fields
    teacher.designation = update_req.designation
    teacher.employee_id = update_req.employee_id
    teacher.specialization = update_req.specialization
    if update_req.is_trainer is not None:
        teacher.is_trainer = update_req.is_trainer

    await db.commit()
    await db.refresh(teacher)
    return await get_teacher_profile(db, teacher)


async def get_department_student_roster(
    db: AsyncSession,
    teacher: Teacher,
    graduation_year: Optional[int] = None,
    current_semester: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> DepartmentStudentRosterResponse:
    """Fetch paginated student roster strictly scoped to teacher's department."""
    conditions = [
        Student.institution_id == teacher.institution_id,
        Student.department_id == teacher.department_id
    ]

    if graduation_year is not None:
        conditions.append(Student.graduation_year == graduation_year)

    if current_semester is not None:
        conditions.append(Student.current_semester == current_semester)

    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                Student.roll_number.ilike(search_pattern),
                UserProfile.first_name.ilike(search_pattern),
                UserProfile.last_name.ilike(search_pattern)
            )
        )

    stmt_count = (
        select(func.count(Student.id))
        .select_from(Student)
        .join(User, User.id == Student.user_id)
        .join(UserProfile, UserProfile.user_id == User.id)
        .where(and_(*conditions))
    )
    total = (await db.execute(stmt_count)).scalar() or 0

    offset = (page - 1) * limit
    stmt_students = (
        select(Student)
        .options(
            selectinload(Student.user).selectinload(User.profile),
            selectinload(Student.target_career_role)
        )
        .join(User, User.id == Student.user_id)
        .join(UserProfile, UserProfile.user_id == User.id)
        .where(and_(*conditions))
        .order_by(Student.roll_number.asc())
        .offset(offset)
        .limit(limit)
    )

    students_result = await db.execute(stmt_students)
    student_records = students_result.scalars().all()

    items = []
    for s in student_records:
        prof = s.user.profile if s.user else None
        items.append(
            DepartmentStudentItem(
                student_id=s.id,
                user_id=s.user_id,
                first_name=prof.first_name if prof else "",
                last_name=prof.last_name if prof else "",
                roll_number=s.roll_number,
                enrollment_year=s.enrollment_year,
                graduation_year=s.graduation_year,
                current_semester=s.current_semester,
                cgpa=s.cgpa,
                target_career_role=s.target_career_role.title if s.target_career_role else None
            )
        )

    return DepartmentStudentRosterResponse(total=total, page=page, limit=limit, students=items)


async def get_training_programs_list(
    db: AsyncSession,
    teacher: Teacher,
    scope: str = "my_programs",
    program_type: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> TrainingProgramListResponse:
    """Fetch training programs scoped to teacher's institution or private conducted list."""
    conditions = [TrainingProgram.institution_id == teacher.institution_id]

    if scope == "my_programs":
        conditions.append(TrainingProgram.conducted_by_user_id == teacher.user_id)

    if program_type:
        conditions.append(TrainingProgram.program_type == program_type.upper())

    stmt_count = select(func.count(TrainingProgram.id)).where(and_(*conditions))
    total = (await db.execute(stmt_count)).scalar() or 0

    offset = (page - 1) * limit
    stmt_programs = (
        select(
            TrainingProgram,
            func.count(TrainingEnrollment.id).label("enrolled_count"),
            UserProfile.first_name,
            UserProfile.last_name
        )
        .select_from(TrainingProgram)
        .outerjoin(TrainingEnrollment, TrainingEnrollment.training_program_id == TrainingProgram.id)
        .join(User, User.id == TrainingProgram.conducted_by_user_id)
        .outerjoin(UserProfile, UserProfile.user_id == User.id)
        .where(and_(*conditions))
        .group_by(TrainingProgram.id, UserProfile.first_name, UserProfile.last_name)
        .order_by(TrainingProgram.start_date.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt_programs)
    rows = result.all()

    items = []
    for prog, count, f_name, l_name in rows:
        cond_name = f"{f_name or ''} {l_name or ''}".strip() or "Instructor"
        items.append(
            TrainingProgramItem(
                id=prog.id,
                title=prog.title,
                description=prog.description,
                program_type=prog.program_type,
                institution_id=prog.institution_id,
                company_id=prog.company_id,
                conducted_by_user_id=prog.conducted_by_user_id,
                conducted_by_name=cond_name,
                start_date=prog.start_date,
                end_date=prog.end_date,
                capacity=prog.capacity,
                status=prog.status,
                enrolled_count=count
            )
        )

    return TrainingProgramListResponse(total=total, page=page, limit=limit, programs=items)


async def create_training_program(
    db: AsyncSession,
    teacher: Teacher,
    req: TrainingProgramCreateRequest
) -> TrainingProgramItem:
    """Create a new training program / workshop conducted by authenticated teacher."""
    program = TrainingProgram(
        title=req.title,
        description=req.description,
        program_type=req.program_type.upper(),
        institution_id=teacher.institution_id,
        conducted_by_user_id=teacher.user_id,
        start_date=req.start_date,
        end_date=req.end_date,
        capacity=req.capacity,
        status="UPCOMING"
    )
    db.add(program)
    await db.commit()
    await db.refresh(program)

    prof = teacher.user.profile if teacher.user else None
    cond_name = f"{prof.first_name} {prof.last_name}" if prof else "Instructor"

    return TrainingProgramItem(
        id=program.id,
        title=program.title,
        description=program.description,
        program_type=program.program_type,
        institution_id=program.institution_id,
        company_id=program.company_id,
        conducted_by_user_id=program.conducted_by_user_id,
        conducted_by_name=cond_name,
        start_date=program.start_date,
        end_date=program.end_date,
        capacity=program.capacity,
        status=program.status,
        enrolled_count=0
    )


async def get_program_enrollments(
    db: AsyncSession,
    teacher: Teacher,
    program_id: uuid.UUID
) -> Optional[TrainingProgramEnrollmentsResponse]:
    """Fetch student enrollments for a specific program conducted by the teacher."""
    # Verify program belongs to teacher's institution AND is conducted by the teacher
    stmt_prog = select(TrainingProgram).where(
        and_(
            TrainingProgram.id == program_id,
            TrainingProgram.institution_id == teacher.institution_id,
            TrainingProgram.conducted_by_user_id == teacher.user_id
        )
    )
    prog = (await db.execute(stmt_prog)).scalar_one_or_none()
    if not prog:
        return None

    stmt_enroll = (
        select(TrainingEnrollment)
        .options(
            selectinload(TrainingEnrollment.student).selectinload(Student.user).selectinload(User.profile)
        )
        .where(TrainingEnrollment.training_program_id == program_id)
        .order_by(TrainingEnrollment.enrollment_date.asc())
    )
    enrollments_result = await db.execute(stmt_enroll)
    enroll_records = enrollments_result.scalars().all()

    items = []
    for en in enroll_records:
        st = en.student
        prof = st.user.profile if st and st.user else None
        st_name = f"{prof.first_name} {prof.last_name}" if prof else "Student"
        items.append(
            EnrollmentStudentItem(
                enrollment_id=en.id,
                student_id=en.student_id,
                student_name=st_name,
                roll_number=st.roll_number if st else "",
                enrollment_date=en.enrollment_date,
                attendance_percentage=en.attendance_percentage,
                completion_status=en.completion_status,
                certificate_url=en.certificate_url
            )
        )

    return TrainingProgramEnrollmentsResponse(
        program_id=prog.id,
        program_title=prog.title,
        total_enrolled=len(items),
        enrollments=items
    )


async def update_program_enrollment(
    db: AsyncSession,
    teacher: Teacher,
    program_id: uuid.UUID,
    enrollment_id: uuid.UUID,
    req: EnrollmentUpdateRequest
) -> Optional[EnrollmentStudentItem]:
    """Update student attendance & completion status for a conducted program."""
    # Check program ownership (both institution and teacher-conducted)
    stmt_prog = select(TrainingProgram).where(
        and_(
            TrainingProgram.id == program_id,
            TrainingProgram.institution_id == teacher.institution_id,
            TrainingProgram.conducted_by_user_id == teacher.user_id
        )
    )
    prog = (await db.execute(stmt_prog)).scalar_one_or_none()
    if not prog:
        return None

    stmt_enroll = (
        select(TrainingEnrollment)
        .options(
            selectinload(TrainingEnrollment.student).selectinload(Student.user).selectinload(User.profile)
        )
        .where(
            and_(
                TrainingEnrollment.id == enrollment_id,
                TrainingEnrollment.training_program_id == program_id
            )
        )
    )
    enrollment = (await db.execute(stmt_enroll)).scalar_one_or_none()
    if not enrollment:
        return None

    enrollment.attendance_percentage = req.attendance_percentage
    enrollment.completion_status = req.completion_status.upper()
    if req.certificate_url is not None:
        enrollment.certificate_url = req.certificate_url

    await db.commit()
    await db.refresh(enrollment)

    st = enrollment.student
    prof = st.user.profile if st and st.user else None
    st_name = f"{prof.first_name} {prof.last_name}" if prof else "Student"

    return EnrollmentStudentItem(
        enrollment_id=enrollment.id,
        student_id=enrollment.student_id,
        student_name=st_name,
        roll_number=st.roll_number if st else "",
        enrollment_date=enrollment.enrollment_date,
        attendance_percentage=enrollment.attendance_percentage,
        completion_status=enrollment.completion_status,
        certificate_url=enrollment.certificate_url
    )


async def get_mentorship_requests(
    db: AsyncSession,
    teacher: Teacher,
    status_filter: Optional[str] = None
) -> List[MentorshipRequestItem]:
    """List student mentorship connection requests for the authenticated teacher."""
    conditions = [MentorConnection.mentor_user_id == teacher.user_id]
    if status_filter:
        conditions.append(MentorConnection.status == status_filter.upper())

    stmt = (
        select(MentorConnection)
        .options(
            selectinload(MentorConnection.student).selectinload(Student.user).selectinload(User.profile),
            selectinload(MentorConnection.student).selectinload(Student.department)
        )
        .where(and_(*conditions))
        .order_by(MentorConnection.created_at.desc())
    )
    result = await db.execute(stmt)
    connections = result.scalars().all()

    items = []
    for conn in connections:
        st = conn.student
        prof = st.user.profile if st and st.user else None
        st_name = f"{prof.first_name} {prof.last_name}" if prof else "Student"
        dept_name = st.department.name if st and st.department else "Department"

        items.append(
            MentorshipRequestItem(
                connection_id=conn.id,
                student_id=conn.student_id,
                student_name=st_name,
                student_roll_number=st.roll_number if st else "",
                student_department=dept_name,
                status=conn.status,
                request_note=conn.request_note,
                connected_at=conn.connected_at,
                created_at=conn.created_at
            )
        )

    return items


async def update_mentorship_request_status(
    db: AsyncSession,
    teacher: Teacher,
    connection_id: uuid.UUID,
    new_status: str
) -> Optional[MentorshipRequestItem]:
    """Accept or reject a student mentorship connection request."""
    stmt = (
        select(MentorConnection)
        .options(
            selectinload(MentorConnection.student).selectinload(Student.user).selectinload(User.profile),
            selectinload(MentorConnection.student).selectinload(Student.department)
        )
        .where(
            and_(
                MentorConnection.id == connection_id,
                MentorConnection.mentor_user_id == teacher.user_id
            )
        )
    )
    conn = (await db.execute(stmt)).scalar_one_or_none()
    if not conn:
        return None

    conn.status = new_status.upper()
    if new_status.upper() == "ACCEPTED" and not conn.connected_at:
        conn.connected_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(conn)

    st = conn.student
    prof = st.user.profile if st and st.user else None
    st_name = f"{prof.first_name} {prof.last_name}" if prof else "Student"
    dept_name = st.department.name if st and st.department else "Department"

    return MentorshipRequestItem(
        connection_id=conn.id,
        student_id=conn.student_id,
        student_name=st_name,
        student_roll_number=st.roll_number if st else "",
        student_department=dept_name,
        status=conn.status,
        request_note=conn.request_note,
        connected_at=conn.connected_at,
        created_at=conn.created_at
    )


async def create_mentorship_session(
    db: AsyncSession,
    teacher: Teacher,
    req: MentorshipSessionCreateRequest
) -> Optional[MentorshipSessionResponse]:
    """Schedule a mentorship session under an ACCEPTED connection."""
    stmt_conn = select(MentorConnection).where(
        and_(
            MentorConnection.id == req.connection_id,
            MentorConnection.mentor_user_id == teacher.user_id
        )
    )
    conn = (await db.execute(stmt_conn)).scalar_one_or_none()
    if not conn or conn.status != "ACCEPTED":
        return None

    session = MentorshipSession(
        connection_id=req.connection_id,
        topic=req.topic,
        scheduled_at=req.scheduled_at,
        duration_minutes=req.duration_minutes,
        meeting_link=req.meeting_link,
        session_notes=req.session_notes,
        status="SCHEDULED"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return MentorshipSessionResponse(
        id=session.id,
        connection_id=session.connection_id,
        topic=session.topic,
        scheduled_at=session.scheduled_at,
        duration_minutes=session.duration_minutes,
        meeting_link=session.meeting_link,
        session_notes=session.session_notes,
        status=session.status,
        created_at=session.created_at
    )


async def get_activities_list(
    db: AsyncSession,
    teacher: Teacher,
    scope: str = "institution",
    page: int = 1,
    limit: int = 20
) -> ActivityListResponse:
    """Fetch campus activities and guest lectures."""
    conditions = [Activity.institution_id == teacher.institution_id]
    if scope == "my_activities":
        conditions.append(Activity.conducted_by_user_id == teacher.user_id)

    stmt_count = select(func.count(Activity.id)).where(and_(*conditions))
    total = (await db.execute(stmt_count)).scalar() or 0

    offset = (page - 1) * limit
    stmt_activities = (
        select(Activity)
        .options(selectinload(Activity.conducted_by_user).selectinload(User.profile))
        .where(and_(*conditions))
        .order_by(Activity.start_time.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt_activities)
    activities = result.scalars().all()

    items = []
    for act in activities:
        user = act.conducted_by_user
        prof = user.profile if user else None
        cond_name = f"{prof.first_name} {prof.last_name}" if prof else None

        items.append(
            ActivityItem(
                id=act.id,
                title=act.title,
                description=act.description,
                activity_type=act.activity_type,
                start_time=act.start_time,
                end_time=act.end_time,
                location_or_url=act.location_or_url,
                conducted_by_user_id=act.conducted_by_user_id,
                conducted_by_name=cond_name
            )
        )

    return ActivityListResponse(total=total, page=page, limit=limit, activities=items)


async def create_activity(
    db: AsyncSession,
    teacher: Teacher,
    req: ActivityCreateRequest
) -> ActivityItem:
    """Schedule a new department/campus activity or guest lecture."""
    activity = Activity(
        title=req.title,
        description=req.description,
        activity_type=req.activity_type.upper(),
        institution_id=teacher.institution_id,
        conducted_by_user_id=teacher.user_id,
        start_time=req.start_time,
        end_time=req.end_time,
        location_or_url=req.location_or_url
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    user = teacher.user
    prof = user.profile if user else None
    cond_name = f"{prof.first_name} {prof.last_name}" if prof else "Instructor"

    return ActivityItem(
        id=activity.id,
        title=activity.title,
        description=activity.description,
        activity_type=activity.activity_type,
        start_time=activity.start_time,
        end_time=activity.end_time,
        location_or_url=activity.location_or_url,
        conducted_by_user_id=activity.conducted_by_user_id,
        conducted_by_name=cond_name
    )


async def get_department_analytics(
    db: AsyncSession,
    teacher: Teacher
) -> DepartmentAnalyticsResponse:
    """Calculate read-only department academic metrics derived strictly from existing data."""
    # Total department students
    stmt_total = select(func.count(Student.id)).where(
        and_(
            Student.institution_id == teacher.institution_id,
            Student.department_id == teacher.department_id
        )
    )
    total_students = (await db.execute(stmt_total)).scalar() or 0

    # CGPA Distribution
    stmt_above_8 = select(func.count(Student.id)).where(
        and_(
            Student.institution_id == teacher.institution_id,
            Student.department_id == teacher.department_id,
            Student.cgpa >= Decimal("8.00")
        )
    )
    above_8 = (await db.execute(stmt_above_8)).scalar() or 0

    stmt_between = select(func.count(Student.id)).where(
        and_(
            Student.institution_id == teacher.institution_id,
            Student.department_id == teacher.department_id,
            Student.cgpa >= Decimal("6.00"),
            Student.cgpa < Decimal("8.00")
        )
    )
    between_6_and_8 = (await db.execute(stmt_between)).scalar() or 0

    stmt_below_6 = select(func.count(Student.id)).where(
        and_(
            Student.institution_id == teacher.institution_id,
            Student.department_id == teacher.department_id,
            Student.cgpa < Decimal("6.00")
        )
    )
    below_6 = (await db.execute(stmt_below_6)).scalar() or 0

    # Top skill gaps
    stmt_gaps = (
        select(
            Skill.id.label("skill_id"),
            Skill.name.label("skill_name"),
            func.count(distinct(Student.id)).label("student_count")
        )
        .select_from(SkillGap)
        .join(Student, Student.id == SkillGap.student_id)
        .join(Skill, Skill.id == SkillGap.skill_id)
        .where(
            and_(
                Student.institution_id == teacher.institution_id,
                Student.department_id == teacher.department_id
            )
        )
        .group_by(Skill.id, Skill.name)
        .order_by(func.count(distinct(Student.id)).desc())
        .limit(5)
    )
    gaps_result = await db.execute(stmt_gaps)
    top_gaps = [
        TopSkillGapItem(
            skill_id=row.skill_id,
            skill_name=row.skill_name,
            student_count=row.student_count
        )
        for row in gaps_result.all()
    ]

    # Placements summary (Read-only aggregation)
    stmt_placed = (
        select(func.count(distinct(PlacementRecord.student_id)))
        .select_from(PlacementRecord)
        .join(Student, Student.id == PlacementRecord.student_id)
        .where(
            and_(
                Student.institution_id == teacher.institution_id,
                Student.department_id == teacher.department_id
            )
        )
    )
    placed_count = (await db.execute(stmt_placed)).scalar() or 0
    placement_pct = round((placed_count / total_students * 100.0), 2) if total_students > 0 else 0.0

    return DepartmentAnalyticsResponse(
        department_id=teacher.department_id,
        department_name=teacher.department.name if teacher.department else "Department",
        total_students=total_students,
        cgpa_distribution=CgpaDistribution(
            above_8=above_8,
            between_6_and_8=between_6_and_8,
            below_6=below_6
        ),
        top_skill_gaps=top_gaps,
        placed_students_count=placed_count,
        placement_percentage=placement_pct
    )
