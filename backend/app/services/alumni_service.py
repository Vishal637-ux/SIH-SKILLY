import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload

from app.models.users import User, UserProfile
from app.models.institutions import Student, Institution, Department
from app.models.mentorship import MentorConnection, MentorshipSession
from app.models.notifications import Notification
from app.models.skills import Skill, StudentSkill
from app.models.careers import CareerRole

from app.schemas.alumni import (
    AlumniProfileResponse,
    AlumniProfileUpdateRequest,
    MentorshipStudentProfile,
    MentorshipRequestItem,
    MentorshipRequestListResponse,
    MentorshipRequestActionRequest,
    MentorConnectionItem,
    MentorConnectionListResponse,
    MentorshipSessionCreateRequest,
    MentorshipSessionUpdateRequest,
    MentorshipSessionItem,
    MentorshipSessionListResponse,
    AlumniDashboardResponse,
)


class AlumniService:

    @staticmethod
    async def get_alumni_profile(db: AsyncSession, user: User) -> AlumniProfileResponse:
        stmt_prof = select(UserProfile).where(UserProfile.user_id == user.id)
        res = await db.execute(stmt_prof)
        prof = res.scalar_one_or_none()

        if not prof:
            prof = UserProfile(
                user_id=user.id,
                first_name=user.username,
                last_name="",
                country="India",
            )
            db.add(prof)
            await db.commit()
            await db.refresh(prof)

        return AlumniProfileResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=prof.first_name,
            last_name=prof.last_name,
            avatar_url=prof.avatar_url,
            phone=prof.phone,
            bio=prof.bio,
            city=prof.city,
            state=prof.state,
            country=prof.country,
            linkedin_url=prof.linkedin_url,
            github_url=prof.github_url,
            website_url=prof.website_url,
        )

    @staticmethod
    async def update_alumni_profile(
        db: AsyncSession, user: User, payload: AlumniProfileUpdateRequest
    ) -> AlumniProfileResponse:
        stmt_prof = select(UserProfile).where(UserProfile.user_id == user.id)
        res = await db.execute(stmt_prof)
        prof = res.scalar_one_or_none()

        if not prof:
            prof = UserProfile(user_id=user.id)
            db.add(prof)

        prof.first_name = payload.first_name.strip()
        prof.last_name = payload.last_name.strip()
        prof.avatar_url = payload.avatar_url.strip() if payload.avatar_url else None
        prof.phone = payload.phone.strip() if payload.phone else None
        prof.bio = payload.bio.strip() if payload.bio else None
        prof.city = payload.city.strip() if payload.city else None
        prof.state = payload.state.strip() if payload.state else None
        prof.country = payload.country.strip() if payload.country else "India"
        prof.linkedin_url = payload.linkedin_url.strip() if payload.linkedin_url else None
        prof.github_url = payload.github_url.strip() if payload.github_url else None
        prof.website_url = payload.website_url.strip() if payload.website_url else None

        await db.commit()
        await db.refresh(prof)

        return await AlumniService.get_alumni_profile(db, user)

    @staticmethod
    async def _build_student_dto(db: AsyncSession, student: Student) -> MentorshipStudentProfile:
        u_prof = student.user.profile if (student and student.user) else None
        first_name = u_prof.first_name if u_prof else "Student"
        last_name = u_prof.last_name if u_prof else ""

        inst_name = student.institution.name if (student and student.institution) else "Institution"
        dept_name = student.department.name if (student and student.department) else "Department"
        role_title = student.target_career_role.title if (student and student.target_career_role) else None

        stmt_skills = (
            select(Skill.name)
            .join(StudentSkill, Skill.id == StudentSkill.skill_id)
            .where(StudentSkill.student_id == student.id)
        )
        skill_names = (await db.execute(stmt_skills)).scalars().all()

        return MentorshipStudentProfile(
            student_id=student.id,
            user_id=student.user_id,
            first_name=first_name,
            last_name=last_name,
            roll_number=student.roll_number,
            institution_name=inst_name,
            department_name=dept_name,
            current_semester=student.current_semester,
            graduation_year=student.graduation_year,
            cgpa=student.cgpa,
            target_career_role=role_title,
            skills=list(skill_names),
        )

    @staticmethod
    async def get_alumni_dashboard(db: AsyncSession, user: User) -> AlumniDashboardResponse:
        u_id = user.id

        # Fetch mentor name
        stmt_prof = select(UserProfile).where(UserProfile.user_id == u_id)
        prof_res = await db.execute(stmt_prof)
        prof = prof_res.scalar_one_or_none()
        mentor_name = f"{prof.first_name} {prof.last_name}".strip() if prof else user.username

        # 1. Total Requests
        stmt_req_tot = select(func.count(MentorConnection.id)).where(
            MentorConnection.mentor_user_id == u_id
        )
        total_requests = (await db.execute(stmt_req_tot)).scalar() or 0

        # 2. Pending Requests
        stmt_req_pend = select(func.count(MentorConnection.id)).where(
            and_(MentorConnection.mentor_user_id == u_id, MentorConnection.status == "PENDING")
        )
        pending_requests = (await db.execute(stmt_req_pend)).scalar() or 0

        # 3. Active Connections
        stmt_conn_act = select(func.count(MentorConnection.id)).where(
            and_(MentorConnection.mentor_user_id == u_id, MentorConnection.status == "ACCEPTED")
        )
        active_connections = (await db.execute(stmt_conn_act)).scalar() or 0

        # 4. Total Sessions
        stmt_sess_tot = select(func.count(MentorshipSession.id)).join(MentorConnection).where(
            MentorConnection.mentor_user_id == u_id
        )
        total_sessions = (await db.execute(stmt_sess_tot)).scalar() or 0

        # 5. Upcoming Sessions
        now_utc = datetime.now(timezone.utc)
        stmt_sess_up = select(func.count(MentorshipSession.id)).join(MentorConnection).where(
            and_(
                MentorConnection.mentor_user_id == u_id,
                MentorshipSession.status == "SCHEDULED",
                MentorshipSession.scheduled_at >= now_utc,
            )
        )
        upcoming_sessions = (await db.execute(stmt_sess_up)).scalar() or 0

        # 6. Completed Sessions
        stmt_sess_comp = select(func.count(MentorshipSession.id)).join(MentorConnection).where(
            and_(
                MentorConnection.mentor_user_id == u_id,
                MentorshipSession.status == "COMPLETED",
            )
        )
        completed_sessions = (await db.execute(stmt_sess_comp)).scalar() or 0

        # 7. Recent Requests (Top 5)
        stmt_recent = (
            select(MentorConnection)
            .options(
                joinedload(MentorConnection.student).joinedload(Student.user).joinedload(User.profile),
                joinedload(MentorConnection.student).joinedload(Student.institution),
                joinedload(MentorConnection.student).joinedload(Student.department),
                joinedload(MentorConnection.student).joinedload(Student.target_career_role),
            )
            .where(MentorConnection.mentor_user_id == u_id)
            .order_by(desc(MentorConnection.created_at))
            .limit(5)
        )
        recent_res = await db.execute(stmt_recent)
        recent_conns = recent_res.scalars().unique().all()

        recent_items = []
        for mc in recent_conns:
            student_dto = await AlumniService._build_student_dto(db, mc.student)
            recent_items.append(
                MentorshipRequestItem(
                    connection_id=mc.id,
                    student=student_dto,
                    status=mc.status,
                    request_note=mc.request_note,
                    connected_at=mc.connected_at,
                    created_at=mc.created_at,
                )
            )

        return AlumniDashboardResponse(
            user_id=u_id,
            mentor_name=mentor_name,
            total_requests_count=total_requests,
            pending_requests_count=pending_requests,
            active_connections_count=active_connections,
            total_sessions_count=total_sessions,
            upcoming_sessions_count=upcoming_sessions,
            completed_sessions_count=completed_sessions,
            recent_requests=recent_items,
        )

    @staticmethod
    async def get_mentorship_requests(
        db: AsyncSession, user: User, status_filter: Optional[str] = None
    ) -> MentorshipRequestListResponse:
        stmt = (
            select(MentorConnection)
            .options(
                joinedload(MentorConnection.student).joinedload(Student.user).joinedload(User.profile),
                joinedload(MentorConnection.student).joinedload(Student.institution),
                joinedload(MentorConnection.student).joinedload(Student.department),
                joinedload(MentorConnection.student).joinedload(Student.target_career_role),
            )
            .where(MentorConnection.mentor_user_id == user.id)
        )

        if status_filter:
            stmt = stmt.where(MentorConnection.status == status_filter.upper().strip())

        stmt = stmt.order_by(desc(MentorConnection.created_at))
        res = await db.execute(stmt)
        connections = res.scalars().unique().all()

        items = []
        for mc in connections:
            student_dto = await AlumniService._build_student_dto(db, mc.student)
            items.append(
                MentorshipRequestItem(
                    connection_id=mc.id,
                    student=student_dto,
                    status=mc.status,
                    request_note=mc.request_note,
                    connected_at=mc.connected_at,
                    created_at=mc.created_at,
                )
            )

        return MentorshipRequestListResponse(
            total=len(items),
            requests=items,
        )

    @staticmethod
    async def respond_to_mentorship_request(
        db: AsyncSession,
        user: User,
        connection_id: uuid.UUID,
        payload: MentorshipRequestActionRequest,
    ) -> MentorshipRequestItem:
        # IDOR check: Verify mentor_user_id == user.id
        stmt = (
            select(MentorConnection)
            .options(
                joinedload(MentorConnection.student).joinedload(Student.user).joinedload(User.profile),
                joinedload(MentorConnection.student).joinedload(Student.institution),
                joinedload(MentorConnection.student).joinedload(Student.department),
                joinedload(MentorConnection.student).joinedload(Student.target_career_role),
            )
            .where(
                and_(
                    MentorConnection.id == connection_id,
                    MentorConnection.mentor_user_id == user.id,
                )
            )
        )
        res = await db.execute(stmt)
        mc = res.scalar_one_or_none()

        if not mc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mentorship connection request not found or access denied.",
            )

        new_status = payload.status.upper().strip()
        mc.status = new_status

        if new_status == "ACCEPTED":
            mc.connected_at = datetime.now(timezone.utc)

            # Trigger notification for student
            stmt_prof = select(UserProfile).where(UserProfile.user_id == user.id)
            p_res = await db.execute(stmt_prof)
            m_prof = p_res.scalar_one_or_none()
            m_name = f"{m_prof.first_name} {m_prof.last_name}".strip() if m_prof else user.username

            notification = Notification(
                user_id=mc.student.user_id,
                title="Mentorship Request Accepted",
                message=f"Mentor {m_name} accepted your mentorship request!",
                notification_type="MENTORSHIP",
                reference_id=mc.id,
                reference_type="MENTOR_CONNECTION",
            )
            db.add(notification)

        await db.commit()
        await db.refresh(mc)

        student_dto = await AlumniService._build_student_dto(db, mc.student)
        return MentorshipRequestItem(
            connection_id=mc.id,
            student=student_dto,
            status=mc.status,
            request_note=mc.request_note,
            connected_at=mc.connected_at,
            created_at=mc.created_at,
        )

    @staticmethod
    async def get_active_connections(db: AsyncSession, user: User) -> MentorConnectionListResponse:
        stmt = (
            select(MentorConnection)
            .options(
                joinedload(MentorConnection.student).joinedload(Student.user).joinedload(User.profile),
                joinedload(MentorConnection.student).joinedload(Student.institution),
                joinedload(MentorConnection.student).joinedload(Student.department),
                joinedload(MentorConnection.student).joinedload(Student.target_career_role),
                selectinload(MentorConnection.sessions),
            )
            .where(
                and_(
                    MentorConnection.mentor_user_id == user.id,
                    MentorConnection.status == "ACCEPTED",
                )
            )
            .order_by(desc(MentorConnection.connected_at))
        )
        res = await db.execute(stmt)
        connections = res.scalars().unique().all()

        items = []
        for mc in connections:
            student_dto = await AlumniService._build_student_dto(db, mc.student)
            sess_cnt = len(mc.sessions or [])
            items.append(
                MentorConnectionItem(
                    connection_id=mc.id,
                    student=student_dto,
                    status=mc.status,
                    connected_at=mc.connected_at,
                    sessions_count=sess_cnt,
                    created_at=mc.created_at,
                )
            )

        return MentorConnectionListResponse(
            total=len(items),
            connections=items,
        )

    @staticmethod
    async def get_connection_detail(
        db: AsyncSession, user: User, connection_id: uuid.UUID
    ) -> MentorConnectionItem:
        stmt = (
            select(MentorConnection)
            .options(
                joinedload(MentorConnection.student).joinedload(Student.user).joinedload(User.profile),
                joinedload(MentorConnection.student).joinedload(Student.institution),
                joinedload(MentorConnection.student).joinedload(Student.department),
                joinedload(MentorConnection.student).joinedload(Student.target_career_role),
                selectinload(MentorConnection.sessions),
            )
            .where(
                and_(
                    MentorConnection.id == connection_id,
                    MentorConnection.mentor_user_id == user.id,
                )
            )
        )
        res = await db.execute(stmt)
        mc = res.scalar_one_or_none()

        if not mc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mentor connection not found or access denied.",
            )

        student_dto = await AlumniService._build_student_dto(db, mc.student)
        return MentorConnectionItem(
            connection_id=mc.id,
            student=student_dto,
            status=mc.status,
            connected_at=mc.connected_at,
            sessions_count=len(mc.sessions or []),
            created_at=mc.created_at,
        )

    @staticmethod
    async def get_mentorship_sessions(
        db: AsyncSession, user: User, status_filter: Optional[str] = None
    ) -> MentorshipSessionListResponse:
        stmt = (
            select(MentorshipSession)
            .options(
                joinedload(MentorshipSession.connection)
                .joinedload(MentorConnection.student)
                .joinedload(Student.user)
                .joinedload(User.profile)
            )
            .join(MentorConnection)
            .where(MentorConnection.mentor_user_id == user.id)
        )

        if status_filter:
            stmt = stmt.where(MentorshipSession.status == status_filter.upper().strip())

        stmt = stmt.order_by(desc(MentorshipSession.scheduled_at))
        res = await db.execute(stmt)
        sessions = res.scalars().all()

        items = []
        for ms in sessions:
            stu = ms.connection.student if ms.connection else None
            p = stu.user.profile if (stu and stu.user and stu.user.profile) else None
            stu_name = f"{p.first_name} {p.last_name}".strip() if p else "Student"

            items.append(
                MentorshipSessionItem(
                    id=ms.id,
                    connection_id=ms.connection_id,
                    student_name=stu_name,
                    topic=ms.topic,
                    scheduled_at=ms.scheduled_at,
                    duration_minutes=ms.duration_minutes,
                    meeting_link=ms.meeting_link,
                    session_notes=ms.session_notes,
                    feedback_rating=ms.feedback_rating,
                    status=ms.status,
                    created_at=ms.created_at,
                )
            )

        return MentorshipSessionListResponse(
            total=len(items),
            sessions=items,
        )

    @staticmethod
    async def create_mentorship_session(
        db: AsyncSession, user: User, payload: MentorshipSessionCreateRequest
    ) -> MentorshipSessionItem:
        # IDOR & ACCEPTED status check: Verify connection belongs to mentor and is ACCEPTED
        stmt_conn = (
            select(MentorConnection)
            .options(
                joinedload(MentorConnection.student).joinedload(Student.user).joinedload(User.profile)
            )
            .where(
                and_(
                    MentorConnection.id == payload.connection_id,
                    MentorConnection.mentor_user_id == user.id,
                )
            )
        )
        res_conn = await db.execute(stmt_conn)
        conn = res_conn.scalar_one_or_none()

        if not conn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mentor connection not found or cross-mentor access denied.",
            )

        if conn.status != "ACCEPTED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mentorship session can only be created for accepted mentor connections.",
            )

        new_session = MentorshipSession(
            connection_id=conn.id,
            topic=payload.topic.strip(),
            scheduled_at=payload.scheduled_at,
            duration_minutes=payload.duration_minutes,
            meeting_link=payload.meeting_link.strip() if payload.meeting_link else None,
            session_notes=payload.session_notes.strip() if payload.session_notes else None,
            status="SCHEDULED",
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)

        stu = conn.student
        p = stu.user.profile if (stu and stu.user and stu.user.profile) else None
        stu_name = f"{p.first_name} {p.last_name}".strip() if p else "Student"

        return MentorshipSessionItem(
            id=new_session.id,
            connection_id=new_session.connection_id,
            student_name=stu_name,
            topic=new_session.topic,
            scheduled_at=new_session.scheduled_at,
            duration_minutes=new_session.duration_minutes,
            meeting_link=new_session.meeting_link,
            session_notes=new_session.session_notes,
            feedback_rating=new_session.feedback_rating,
            status=new_session.status,
            created_at=new_session.created_at,
        )

    @staticmethod
    async def get_session_detail(
        db: AsyncSession, user: User, session_id: uuid.UUID
    ) -> MentorshipSessionItem:
        stmt = (
            select(MentorshipSession)
            .options(
                joinedload(MentorshipSession.connection)
                .joinedload(MentorConnection.student)
                .joinedload(Student.user)
                .joinedload(User.profile)
            )
            .join(MentorConnection)
            .where(
                and_(
                    MentorshipSession.id == session_id,
                    MentorConnection.mentor_user_id == user.id,
                )
            )
        )
        res = await db.execute(stmt)
        ms = res.scalar_one_or_none()

        if not ms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mentorship session not found or cross-mentor access denied.",
            )

        stu = ms.connection.student if ms.connection else None
        p = stu.user.profile if (stu and stu.user and stu.user.profile) else None
        stu_name = f"{p.first_name} {p.last_name}".strip() if p else "Student"

        return MentorshipSessionItem(
            id=ms.id,
            connection_id=ms.connection_id,
            student_name=stu_name,
            topic=ms.topic,
            scheduled_at=ms.scheduled_at,
            duration_minutes=ms.duration_minutes,
            meeting_link=ms.meeting_link,
            session_notes=ms.session_notes,
            feedback_rating=ms.feedback_rating,
            status=ms.status,
            created_at=ms.created_at,
        )

    @staticmethod
    async def update_mentorship_session(
        db: AsyncSession,
        user: User,
        session_id: uuid.UUID,
        payload: MentorshipSessionUpdateRequest,
    ) -> MentorshipSessionItem:
        stmt = (
            select(MentorshipSession)
            .options(
                joinedload(MentorshipSession.connection)
                .joinedload(MentorConnection.student)
                .joinedload(Student.user)
                .joinedload(User.profile)
            )
            .join(MentorConnection)
            .where(
                and_(
                    MentorshipSession.id == session_id,
                    MentorConnection.mentor_user_id == user.id,
                )
            )
        )
        res = await db.execute(stmt)
        ms = res.scalar_one_or_none()

        if not ms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mentorship session not found or cross-mentor access denied.",
            )

        if payload.topic is not None:
            ms.topic = payload.topic.strip()
        if payload.scheduled_at is not None:
            ms.scheduled_at = payload.scheduled_at
        if payload.duration_minutes is not None:
            ms.duration_minutes = payload.duration_minutes
        if payload.meeting_link is not None:
            ms.meeting_link = payload.meeting_link.strip() if payload.meeting_link else None
        if payload.session_notes is not None:
            ms.session_notes = payload.session_notes.strip() if payload.session_notes else None
        if payload.status is not None:
            ms.status = payload.status.upper().strip()

        await db.commit()
        await db.refresh(ms)

        stu = ms.connection.student if ms.connection else None
        p = stu.user.profile if (stu and stu.user and stu.user.profile) else None
        stu_name = f"{p.first_name} {p.last_name}".strip() if p else "Student"

        return MentorshipSessionItem(
            id=ms.id,
            connection_id=ms.connection_id,
            student_name=stu_name,
            topic=ms.topic,
            scheduled_at=ms.scheduled_at,
            duration_minutes=ms.duration_minutes,
            meeting_link=ms.meeting_link,
            session_notes=ms.session_notes,
            feedback_rating=ms.feedback_rating,
            status=ms.status,
            created_at=ms.created_at,
        )
