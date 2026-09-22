import uuid
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload

from app.models.users import User, UserProfile
from app.models.companies import Company, CompanyUser
from app.models.opportunities import Opportunity, OpportunitySkill, Application, ApplicationStatusHistory
from app.models.internships import Internship, InternshipProgress, InternshipEvaluation
from app.models.placements import PlacementRecord, PlacementInteraction
from app.models.skills import Skill, StudentSkill
from app.models.institutions import Student, Institution, Department
from app.models.careers import CareerRole

from app.schemas.industry import (
    CompanyProfileResponse,
    CompanyProfileUpdateRequest,
    OpportunityCreateRequest,
    OpportunityUpdateRequest,
    OpportunityItem,
    OpportunityListResponse,
    OpportunitySkillRequirement,
    ApplicationItem,
    ApplicationStudentProfile,
    ApplicationListResponse,
    ApplicationStatusUpdateRequest,
    ApplicationStatusHistoryItem,
    InternshipItem,
    InternshipEvaluationRequest,
    InternshipEvaluationResponse,
    PlacementInteractionCreateRequest,
    PlacementInteractionItem,
    IndustryDashboardResponse,
    RecentApplicationOverview,
    IndustryAnalyticsResponse,
    StatusFunnelItem,
    TopRequiredSkillItem,
)


class IndustryService:

    @staticmethod
    async def get_company_context(db: AsyncSession, user: User) -> Tuple[CompanyUser, Company]:
        """Resolves the company context for the authenticated Industry user.

        Enforces strict resolution: JWT sub -> users.id -> company_users -> companies.
        Raises 404 NOT FOUND if company association is missing.
        """
        stmt = (
            select(CompanyUser)
            .options(selectinload(CompanyUser.company))
            .where(CompanyUser.user_id == user.id)
        )
        res = await db.execute(stmt)
        company_user = res.scalar_one_or_none()

        if not company_user or not company_user.company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No company profile associated with this user account.",
            )

        return company_user, company_user.company

    @staticmethod
    async def get_company_profile(db: AsyncSession, user: User) -> CompanyProfileResponse:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt_prof = select(UserProfile).where(UserProfile.user_id == user.id)
        prof_res = await db.execute(stmt_prof)
        user_prof = prof_res.scalar_one_or_none()
        user_name = f"{user_prof.first_name} {user_prof.last_name}".strip() if user_prof else user.username

        return CompanyProfileResponse(
            id=company.id,
            name=company.name,
            industry_type=company.industry_type,
            company_size=company.company_size,
            website=company.website,
            logo_url=company.logo_url,
            headquarters=company.headquarters,
            description=company.description,
            is_verified=company.is_verified,
            user_designation=company_user.designation,
            user_hr_role=company_user.hr_role,
            user_email=user.email,
            user_name=user_name,
        )

    @staticmethod
    async def update_company_profile(
        db: AsyncSession, user: User, payload: CompanyProfileUpdateRequest
    ) -> CompanyProfileResponse:
        company_user, company = await IndustryService.get_company_context(db, user)

        # Update allowed Company fields
        company.name = payload.name.strip()
        company.industry_type = payload.industry_type.strip()
        company.company_size = payload.company_size.strip() if payload.company_size else None
        company.website = payload.website.strip() if payload.website else None
        company.logo_url = payload.logo_url.strip() if payload.logo_url else None
        company.headquarters = payload.headquarters.strip() if payload.headquarters else None
        company.description = payload.description.strip() if payload.description else None

        # Update CompanyUser designation
        company_user.designation = payload.designation.strip()

        await db.commit()
        await db.refresh(company)
        await db.refresh(company_user)

        return await IndustryService.get_company_profile(db, user)

    @staticmethod
    async def get_company_dashboard(db: AsyncSession, user: User) -> IndustryDashboardResponse:
        company_user, company = await IndustryService.get_company_context(db, user)
        c_id = company.id

        # 1. Active Opportunities
        stmt_opps = select(func.count(Opportunity.id)).where(
            and_(Opportunity.company_id == c_id, Opportunity.status == "OPEN")
        )
        active_opps = (await db.execute(stmt_opps)).scalar() or 0

        # 2. Total Applications
        stmt_apps = select(func.count(Application.id)).join(Opportunity).where(
            Opportunity.company_id == c_id
        )
        total_apps = (await db.execute(stmt_apps)).scalar() or 0

        # 3. Shortlisted Count
        stmt_shortlisted = select(func.count(Application.id)).join(Opportunity).where(
            and_(Opportunity.company_id == c_id, Application.current_status == "SHORTLISTED")
        )
        shortlisted_cnt = (await db.execute(stmt_shortlisted)).scalar() or 0

        # 4. Selected / Offered Count
        stmt_selected = select(func.count(Application.id)).join(Opportunity).where(
            and_(
                Opportunity.company_id == c_id,
                Application.current_status.in_(["OFFERED", "ACCEPTED"])
            )
        )
        selected_cnt = (await db.execute(stmt_selected)).scalar() or 0

        # 5. Active Internships
        stmt_internships = select(func.count(Internship.id)).where(
            and_(Internship.company_id == c_id, Internship.status == "ONGOING")
        )
        active_internships = (await db.execute(stmt_internships)).scalar() or 0

        # 6. Upcoming Interactions
        now_utc = datetime.now(timezone.utc)
        stmt_interactions = select(func.count(PlacementInteraction.id)).join(Opportunity).where(
            and_(Opportunity.company_id == c_id, PlacementInteraction.scheduled_at >= now_utc)
        )
        upcoming_interactions = (await db.execute(stmt_interactions)).scalar() or 0

        # 7. Recent Applications (Top 5)
        stmt_recent = (
            select(Application)
            .options(
                joinedload(Application.opportunity),
                joinedload(Application.student).joinedload(Student.user).joinedload(User.profile),
            )
            .join(Opportunity)
            .where(Opportunity.company_id == c_id)
            .order_by(desc(Application.applied_at))
            .limit(5)
        )
        recent_apps_res = await db.execute(stmt_recent)
        recent_apps_entities = recent_apps_res.scalars().all()

        recent_list = []
        for app in recent_apps_entities:
            stu_name = "Student"
            if app.student and app.student.user and app.student.user.profile:
                p = app.student.user.profile
                stu_name = f"{p.first_name} {p.last_name}".strip()
            recent_list.append(
                RecentApplicationOverview(
                    id=app.id,
                    opportunity_title=app.opportunity.title if app.opportunity else "Opportunity",
                    student_name=stu_name,
                    status=app.current_status,
                    applied_at=app.applied_at,
                )
            )

        return IndustryDashboardResponse(
            company_id=c_id,
            company_name=company.name,
            is_verified=company.is_verified,
            active_opportunities_count=active_opps,
            total_applications_count=total_apps,
            shortlisted_count=shortlisted_cnt,
            selected_count=selected_cnt,
            active_internships_count=active_internships,
            upcoming_interactions_count=upcoming_interactions,
            recent_applications=recent_list,
        )

    @staticmethod
    async def _build_opportunity_item(db: AsyncSession, opp: Opportunity) -> OpportunityItem:
        # Load required skills with skill details
        stmt_skills = (
            select(OpportunitySkill)
            .options(selectinload(OpportunitySkill.skill))
            .where(OpportunitySkill.opportunity_id == opp.id)
        )
        skills_res = await db.execute(stmt_skills)
        opp_skills = skills_res.scalars().all()

        skills_list = [
            OpportunitySkillRequirement(
                skill_id=os.skill_id,
                skill_name=os.skill.name if os.skill else None,
                required_proficiency=os.required_proficiency,
                is_mandatory=os.is_mandatory,
            )
            for os in opp_skills
        ]

        # App count
        stmt_count = select(func.count(Application.id)).where(Application.opportunity_id == opp.id)
        app_count = (await db.execute(stmt_count)).scalar() or 0

        company_name = opp.company.name if opp.company else "Company"

        return OpportunityItem(
            id=opp.id,
            company_id=opp.company_id,
            company_name=company_name,
            title=opp.title,
            role_type=opp.role_type,
            description=opp.description,
            location=opp.location,
            is_remote=opp.is_remote,
            stipend_salary=opp.stipend_salary,
            duration_months=opp.duration_months,
            openings_count=opp.openings_count,
            eligibility_criteria=opp.eligibility_criteria,
            application_deadline=opp.application_deadline,
            status=opp.status,
            created_at=opp.created_at,
            required_skills=skills_list,
            applications_count=app_count,
        )

    @staticmethod
    async def get_company_opportunities(
        db: AsyncSession, user: User, status_filter: Optional[str] = None
    ) -> OpportunityListResponse:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt = (
            select(Opportunity)
            .options(selectinload(Opportunity.company))
            .where(Opportunity.company_id == company.id)
        )
        if status_filter:
            stmt = stmt.where(Opportunity.status == status_filter.upper())

        stmt = stmt.order_by(desc(Opportunity.created_at))
        res = await db.execute(stmt)
        opps = res.scalars().all()

        items = []
        for opp in opps:
            items.append(await IndustryService._build_opportunity_item(db, opp))

        return OpportunityListResponse(
            total=len(items),
            page=1,
            limit=len(items) or 10,
            opportunities=items,
        )

    @staticmethod
    async def create_opportunity(
        db: AsyncSession, user: User, payload: OpportunityCreateRequest
    ) -> OpportunityItem:
        company_user, company = await IndustryService.get_company_context(db, user)

        new_opp = Opportunity(
            company_id=company.id,
            title=payload.title.strip(),
            role_type=payload.role_type.upper().strip(),
            description=payload.description.strip(),
            location=payload.location.strip(),
            is_remote=payload.is_remote,
            stipend_salary=payload.stipend_salary.strip() if payload.stipend_salary else None,
            duration_months=payload.duration_months,
            openings_count=payload.openings_count,
            eligibility_criteria=payload.eligibility_criteria,
            application_deadline=payload.application_deadline,
            status="OPEN",
        )
        db.add(new_opp)
        await db.flush()

        # Attach skills
        for sk in payload.skills:
            stmt_s = select(Skill).where(Skill.id == sk.skill_id)
            s_res = await db.execute(stmt_s)
            if s_res.scalar_one_or_none():
                opp_skill = OpportunitySkill(
                    opportunity_id=new_opp.id,
                    skill_id=sk.skill_id,
                    required_proficiency=sk.required_proficiency,
                    is_mandatory=sk.is_mandatory,
                )
                db.add(opp_skill)

        await db.commit()

        # Reload with company
        stmt_load = select(Opportunity).options(selectinload(Opportunity.company)).where(Opportunity.id == new_opp.id)
        loaded_opp = (await db.execute(stmt_load)).scalar_one()

        return await IndustryService._build_opportunity_item(db, loaded_opp)

    @staticmethod
    async def get_opportunity_detail(
        db: AsyncSession, user: User, opportunity_id: uuid.UUID
    ) -> OpportunityItem:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt = (
            select(Opportunity)
            .options(selectinload(Opportunity.company))
            .where(Opportunity.id == opportunity_id)
        )
        res = await db.execute(stmt)
        opp = res.scalar_one_or_none()

        if not opp or opp.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found or access denied.",
            )

        return await IndustryService._build_opportunity_item(db, opp)

    @staticmethod
    async def update_opportunity(
        db: AsyncSession, user: User, opportunity_id: uuid.UUID, payload: OpportunityUpdateRequest
    ) -> OpportunityItem:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt = select(Opportunity).options(selectinload(Opportunity.company)).where(Opportunity.id == opportunity_id)
        res = await db.execute(stmt)
        opp = res.scalar_one_or_none()

        if not opp or opp.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found or access denied.",
            )

        if payload.title is not None:
            opp.title = payload.title.strip()
        if payload.role_type is not None:
            opp.role_type = payload.role_type.upper().strip()
        if payload.description is not None:
            opp.description = payload.description.strip()
        if payload.location is not None:
            opp.location = payload.location.strip()
        if payload.is_remote is not None:
            opp.is_remote = payload.is_remote
        if payload.stipend_salary is not None:
            opp.stipend_salary = payload.stipend_salary.strip()
        if payload.duration_months is not None:
            opp.duration_months = payload.duration_months
        if payload.openings_count is not None:
            opp.openings_count = payload.openings_count
        if payload.eligibility_criteria is not None:
            opp.eligibility_criteria = payload.eligibility_criteria
        if payload.application_deadline is not None:
            opp.application_deadline = payload.application_deadline
        if payload.status is not None:
            opp.status = payload.status.upper().strip()

        if payload.skills is not None:
            await db.execute(delete(OpportunitySkill).where(OpportunitySkill.opportunity_id == opp.id))
            for sk in payload.skills:
                opp_skill = OpportunitySkill(
                    opportunity_id=opp.id,
                    skill_id=sk.skill_id,
                    required_proficiency=sk.required_proficiency,
                    is_mandatory=sk.is_mandatory,
                )
                db.add(opp_skill)

        await db.commit()
        await db.refresh(opp)

        return await IndustryService._build_opportunity_item(db, opp)

    @staticmethod
    async def delete_opportunity(
        db: AsyncSession, user: User, opportunity_id: uuid.UUID
    ) -> None:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        res = await db.execute(stmt)
        opp = res.scalar_one_or_none()

        if not opp or opp.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found or access denied.",
            )

        opp.status = "CLOSED"
        await db.commit()

    @staticmethod
    async def get_company_applications(
        db: AsyncSession,
        user: User,
        opportunity_id: Optional[uuid.UUID] = None,
        status_filter: Optional[str] = None,
        min_cgpa: Optional[float] = None,
        graduation_year: Optional[int] = None,
        skill_id: Optional[uuid.UUID] = None,
    ) -> ApplicationListResponse:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt = (
            select(Application)
            .options(
                joinedload(Application.opportunity),
                joinedload(Application.student).joinedload(Student.user).joinedload(User.profile),
                joinedload(Application.student).joinedload(Student.institution),
                joinedload(Application.student).joinedload(Student.department),
                joinedload(Application.student).joinedload(Student.target_career_role),
            )
            .join(Opportunity)
            .where(Opportunity.company_id == company.id)
        )

        if opportunity_id:
            stmt = stmt.where(Application.opportunity_id == opportunity_id)

        if status_filter:
            stmt = stmt.where(Application.current_status == status_filter.upper())

        if min_cgpa is not None:
            stmt = stmt.join(Student, Application.student_id == Student.id).where(
                Student.cgpa >= Decimal(str(min_cgpa))
            )

        if graduation_year is not None:
            stmt = stmt.join(Student, Application.student_id == Student.id).where(
                Student.graduation_year == graduation_year
            )

        if skill_id is not None:
            stmt = stmt.join(StudentSkill, Application.student_id == StudentSkill.student_id).where(
                StudentSkill.skill_id == skill_id
            )

        stmt = stmt.order_by(desc(Application.applied_at))
        res = await db.execute(stmt)
        applications = res.scalars().unique().all()

        items = []
        for app in applications:
            stu = app.student
            user_prof = stu.user.profile if (stu and stu.user) else None

            first_name = user_prof.first_name if user_prof else "Student"
            last_name = user_prof.last_name if user_prof else ""
            user_id = stu.user_id if stu else uuid.uuid4()

            inst_name = stu.institution.name if (stu and stu.institution) else "Institution"
            dept_name = stu.department.name if (stu and stu.department) else "Department"
            role_title = stu.target_career_role.title if (stu and stu.target_career_role) else None

            stmt_st_skills = (
                select(Skill.name)
                .join(StudentSkill, Skill.id == StudentSkill.skill_id)
                .where(StudentSkill.student_id == stu.id)
            )
            st_skills_res = await db.execute(stmt_st_skills)
            student_skill_names = st_skills_res.scalars().all()

            student_profile_dto = ApplicationStudentProfile(
                student_id=stu.id if stu else uuid.uuid4(),
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                roll_number=stu.roll_number if stu else "N/A",
                institution_name=inst_name,
                department_name=dept_name,
                current_semester=stu.current_semester if stu else 1,
                graduation_year=stu.graduation_year if stu else 2026,
                cgpa=stu.cgpa if stu else None,
                target_career_role=role_title,
                skills=list(student_skill_names),
            )

            items.append(
                ApplicationItem(
                    id=app.id,
                    opportunity_id=app.opportunity_id,
                    opportunity_title=app.opportunity.title if app.opportunity else "Opportunity",
                    student=student_profile_dto,
                    resume_version_id=app.resume_version_id,
                    cover_letter=app.cover_letter,
                    current_status=app.current_status,
                    applied_at=app.applied_at,
                    skill_match_percentage=85.0,
                )
            )

        return ApplicationListResponse(
            total=len(items),
            page=1,
            limit=len(items) or 10,
            applications=items,
        )

    @staticmethod
    async def get_application_detail(
        db: AsyncSession, user: User, application_id: uuid.UUID
    ) -> ApplicationItem:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt = (
            select(Application)
            .options(
                joinedload(Application.opportunity),
                joinedload(Application.student).joinedload(Student.user).joinedload(User.profile),
                joinedload(Application.student).joinedload(Student.institution),
                joinedload(Application.student).joinedload(Student.department),
                joinedload(Application.student).joinedload(Student.target_career_role),
            )
            .join(Opportunity)
            .where(and_(Application.id == application_id, Opportunity.company_id == company.id))
        )
        res = await db.execute(stmt)
        app = res.scalar_one_or_none()

        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found or cross-company access denied.",
            )

        stu = app.student
        user_prof = stu.user.profile if (stu and stu.user) else None
        inst_name = stu.institution.name if (stu and stu.institution) else "Institution"
        dept_name = stu.department.name if (stu and stu.department) else "Department"
        role_title = stu.target_career_role.title if (stu and stu.target_career_role) else None

        stmt_st_skills = (
            select(Skill.name)
            .join(StudentSkill, Skill.id == StudentSkill.skill_id)
            .where(StudentSkill.student_id == stu.id)
        )
        student_skill_names = (await db.execute(stmt_st_skills)).scalars().all()

        student_dto = ApplicationStudentProfile(
            student_id=stu.id,
            user_id=stu.user_id,
            first_name=user_prof.first_name if user_prof else "Student",
            last_name=user_prof.last_name if user_prof else "",
            roll_number=stu.roll_number,
            institution_name=inst_name,
            department_name=dept_name,
            current_semester=stu.current_semester,
            graduation_year=stu.graduation_year,
            cgpa=stu.cgpa,
            target_career_role=role_title,
            skills=list(student_skill_names),
        )

        return ApplicationItem(
            id=app.id,
            opportunity_id=app.opportunity_id,
            opportunity_title=app.opportunity.title if app.opportunity else "Opportunity",
            student=student_dto,
            resume_version_id=app.resume_version_id,
            cover_letter=app.cover_letter,
            current_status=app.current_status,
            applied_at=app.applied_at,
            skill_match_percentage=85.0,
        )

    @staticmethod
    async def update_application_status(
        db: AsyncSession,
        user: User,
        application_id: uuid.UUID,
        payload: ApplicationStatusUpdateRequest,
    ) -> ApplicationItem:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt = (
            select(Application)
            .join(Opportunity)
            .where(and_(Application.id == application_id, Opportunity.company_id == company.id))
        )
        res = await db.execute(stmt)
        app = res.scalar_one_or_none()

        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found or cross-company access denied.",
            )

        new_status = payload.status.upper().strip()

        app.current_status = new_status

        history_entry = ApplicationStatusHistory(
            application_id=app.id,
            status=new_status,
            notes=payload.notes.strip() if payload.notes else f"Status updated to {new_status}",
            changed_by_user_id=user.id,
        )
        db.add(history_entry)
        await db.commit()

        return await IndustryService.get_application_detail(db, user, application_id)

    @staticmethod
    async def get_application_status_history(
        db: AsyncSession, user: User, application_id: uuid.UUID
    ) -> List[ApplicationStatusHistoryItem]:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt_app = (
            select(Application)
            .join(Opportunity)
            .where(and_(Application.id == application_id, Opportunity.company_id == company.id))
        )
        app_res = await db.execute(stmt_app)
        if not app_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found or cross-company access denied.",
            )

        stmt_hist = (
            select(ApplicationStatusHistory)
            .options(joinedload(ApplicationStatusHistory.changed_by_user).joinedload(User.profile))
            .where(ApplicationStatusHistory.application_id == application_id)
            .order_by(desc(ApplicationStatusHistory.created_at))
        )
        res = await db.execute(stmt_hist)
        records = res.scalars().all()

        items = []
        for r in records:
            u = r.changed_by_user
            p = u.profile if (u and u.profile) else None
            c_name = f"{p.first_name} {p.last_name}".strip() if p else (u.username if u else "System")

            items.append(
                ApplicationStatusHistoryItem(
                    id=r.id,
                    status=r.status,
                    notes=r.notes,
                    changed_by_name=c_name,
                    created_at=r.created_at,
                )
            )

        return items

    @staticmethod
    async def get_company_internships(db: AsyncSession, user: User) -> List[InternshipItem]:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt = (
            select(Internship)
            .options(
                joinedload(Internship.student).joinedload(Student.user).joinedload(User.profile),
                joinedload(Internship.opportunity),
                selectinload(Internship.progress_reports),
                selectinload(Internship.evaluation),
            )
            .where(Internship.company_id == company.id)
            .order_by(desc(Internship.start_date))
        )
        res = await db.execute(stmt)
        internships = res.scalars().unique().all()

        items = []
        for i in internships:
            stu = i.student
            p = stu.user.profile if (stu and stu.user and stu.user.profile) else None
            stu_name = f"{p.first_name} {p.last_name}".strip() if p else "Student"

            items.append(
                InternshipItem(
                    id=i.id,
                    student_id=i.student_id,
                    student_name=stu_name,
                    roll_number=stu.roll_number if stu else "N/A",
                    opportunity_title=i.opportunity.title if i.opportunity else "Internship Opportunity",
                    supervisor_name=i.supervisor_name,
                    supervisor_email=i.supervisor_email,
                    start_date=i.start_date,
                    end_date=i.end_date,
                    stipend=i.stipend,
                    status=i.status,
                    weekly_reports_count=len(i.progress_reports or []),
                    has_evaluation=i.evaluation is not None,
                )
            )

        return items

    @staticmethod
    async def submit_internship_evaluation(
        db: AsyncSession,
        user: User,
        internship_id: uuid.UUID,
        payload: InternshipEvaluationRequest,
    ) -> InternshipEvaluationResponse:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt = (
            select(Internship)
            .options(selectinload(Internship.evaluation))
            .where(and_(Internship.id == internship_id, Internship.company_id == company.id))
        )
        res = await db.execute(stmt)
        internship = res.scalar_one_or_none()

        if not internship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Internship contract not found or access denied.",
            )

        if internship.evaluation:
            eval_entity = internship.evaluation
            eval_entity.technical_rating = payload.technical_rating
            eval_entity.soft_skills_rating = payload.soft_skills_rating
            eval_entity.punctuality_rating = payload.punctuality_rating
            eval_entity.overall_feedback = payload.overall_feedback
            eval_entity.evaluator_user_id = user.id
        else:
            eval_entity = InternshipEvaluation(
                internship_id=internship.id,
                evaluator_user_id=user.id,
                technical_rating=payload.technical_rating,
                soft_skills_rating=payload.soft_skills_rating,
                punctuality_rating=payload.punctuality_rating,
                overall_feedback=payload.overall_feedback,
                is_verified=True,
            )
            db.add(eval_entity)

        await db.commit()
        await db.refresh(eval_entity)

        return InternshipEvaluationResponse(
            id=eval_entity.id,
            internship_id=eval_entity.internship_id,
            technical_rating=eval_entity.technical_rating,
            soft_skills_rating=eval_entity.soft_skills_rating,
            punctuality_rating=eval_entity.punctuality_rating,
            overall_feedback=eval_entity.overall_feedback,
            evaluated_at=eval_entity.evaluated_at,
        )

    @staticmethod
    async def get_company_interactions(db: AsyncSession, user: User) -> List[PlacementInteractionItem]:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt = (
            select(PlacementInteraction)
            .options(
                joinedload(PlacementInteraction.opportunity),
                joinedload(PlacementInteraction.conducted_by_user).joinedload(User.profile),
            )
            .join(Opportunity)
            .where(Opportunity.company_id == company.id)
            .order_by(desc(PlacementInteraction.scheduled_at))
        )
        res = await db.execute(stmt)
        interactions = res.scalars().all()

        items = []
        for pi in interactions:
            u = pi.conducted_by_user
            p = u.profile if (u and u.profile) else None
            cond_name = f"{p.first_name} {p.last_name}".strip() if p else (u.username if u else None)

            items.append(
                PlacementInteractionItem(
                    id=pi.id,
                    opportunity_id=pi.opportunity_id,
                    opportunity_title=pi.opportunity.title if pi.opportunity else "Opportunity",
                    interaction_type=pi.interaction_type,
                    title=pi.title,
                    scheduled_at=pi.scheduled_at,
                    meeting_link=pi.meeting_link,
                    conducted_by_name=cond_name,
                    created_at=pi.created_at,
                )
            )

        return items

    @staticmethod
    async def create_company_interaction(
        db: AsyncSession, user: User, payload: PlacementInteractionCreateRequest
    ) -> PlacementInteractionItem:
        company_user, company = await IndustryService.get_company_context(db, user)

        stmt_opp = select(Opportunity).where(
            and_(Opportunity.id == payload.opportunity_id, Opportunity.company_id == company.id)
        )
        opp_res = await db.execute(stmt_opp)
        opp = opp_res.scalar_one_or_none()

        if not opp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found or access denied.",
            )

        new_interaction = PlacementInteraction(
            opportunity_id=opp.id,
            interaction_type=payload.interaction_type.upper().strip(),
            title=payload.title.strip(),
            scheduled_at=payload.scheduled_at,
            meeting_link=payload.meeting_link.strip() if payload.meeting_link else None,
            conducted_by_user_id=user.id,
        )
        db.add(new_interaction)
        await db.commit()

        stmt_load = (
            select(PlacementInteraction)
            .options(
                joinedload(PlacementInteraction.opportunity),
                joinedload(PlacementInteraction.conducted_by_user).joinedload(User.profile),
            )
            .where(PlacementInteraction.id == new_interaction.id)
        )
        loaded = (await db.execute(stmt_load)).scalar_one()

        u = loaded.conducted_by_user
        p = u.profile if (u and u.profile) else None
        cond_name = f"{p.first_name} {p.last_name}".strip() if p else (u.username if u else None)

        return PlacementInteractionItem(
            id=loaded.id,
            opportunity_id=loaded.opportunity_id,
            opportunity_title=loaded.opportunity.title if loaded.opportunity else "Opportunity",
            interaction_type=loaded.interaction_type,
            title=loaded.title,
            scheduled_at=loaded.scheduled_at,
            meeting_link=loaded.meeting_link,
            conducted_by_name=cond_name,
            created_at=loaded.created_at,
        )

    @staticmethod
    async def get_company_analytics(db: AsyncSession, user: User) -> IndustryAnalyticsResponse:
        company_user, company = await IndustryService.get_company_context(db, user)
        c_id = company.id

        stmt_postings = select(func.count(Opportunity.id)).where(Opportunity.company_id == c_id)
        total_postings = (await db.execute(stmt_postings)).scalar() or 0

        stmt_apps = select(func.count(Application.id)).join(Opportunity).where(
            Opportunity.company_id == c_id
        )
        total_apps = (await db.execute(stmt_apps)).scalar() or 0

        stmt_funnel = (
            select(Application.current_status, func.count(Application.id))
            .join(Opportunity)
            .where(Opportunity.company_id == c_id)
            .group_by(Application.current_status)
        )
        funnel_res = await db.execute(stmt_funnel)
        funnel_dict = dict(funnel_res.all())

        statuses = ["APPLIED", "SHORTLISTED", "INTERVIEWING", "OFFERED", "REJECTED", "ACCEPTED"]
        funnel_items = [
            StatusFunnelItem(status=st, count=funnel_dict.get(st, 0)) for st in statuses
        ]

        stmt_skills = (
            select(Skill.id, Skill.name, func.count(OpportunitySkill.opportunity_id))
            .join(OpportunitySkill, Skill.id == OpportunitySkill.skill_id)
            .join(Opportunity, OpportunitySkill.opportunity_id == Opportunity.id)
            .where(Opportunity.company_id == c_id)
            .group_by(Skill.id, Skill.name)
            .order_by(desc(func.count(OpportunitySkill.opportunity_id)))
            .limit(5)
        )
        skills_res = await db.execute(stmt_skills)
        top_skills = [
            TopRequiredSkillItem(skill_id=s_id, skill_name=s_name, postings_count=cnt)
            for s_id, s_name, cnt in skills_res.all()
        ]

        stmt_internships_tot = select(func.count(Internship.id)).where(Internship.company_id == c_id)
        tot_int = (await db.execute(stmt_internships_tot)).scalar() or 0

        stmt_internships_comp = select(func.count(Internship.id)).where(
            and_(Internship.company_id == c_id, Internship.status == "COMPLETED")
        )
        comp_int = (await db.execute(stmt_internships_comp)).scalar() or 0

        completion_rate = (float(comp_int) / float(tot_int) * 100.0) if tot_int > 0 else 100.0

        return IndustryAnalyticsResponse(
            company_id=c_id,
            company_name=company.name,
            total_postings=total_postings,
            total_applications=total_apps,
            hiring_funnel=funnel_items,
            top_demanded_skills=top_skills,
            internship_completion_rate=round(completion_rate, 1),
        )
