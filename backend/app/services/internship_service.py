import uuid
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload

from app.models.users import User, UserProfile
from app.models.institutions import Student, Institution
from app.models.companies import Company
from app.models.opportunities import Opportunity, OpportunitySkill, Application, ApplicationStatusHistory
from app.models.internships import Internship, InternshipProgress, InternshipEvaluation
from app.models.placements import PlacementRecord
from app.models.skills import Skill, StudentSkill

from app.schemas.student import (
    OpportunityStudentRead,
    OpportunitySkillRead,
    StudentApplicationApplyRequest,
    StudentApplicationRead,
    StudentApplicationStatusHistoryRead,
    StudentInternshipRead,
    StudentInternshipProgressCreate,
    StudentInternshipProgressRead,
    StudentInternshipEvaluationRead,
    StudentPlacementRecordRead,
)


class InternshipService:

    @staticmethod
    async def get_student_context(db: AsyncSession, user: User) -> Student:
        """Resolves Student model for current authenticated user."""
        stmt = (
            select(Student)
            .options(
                joinedload(Student.user).joinedload(User.profile),
                joinedload(Student.institution),
                joinedload(Student.department),
            )
            .where(Student.user_id == user.id)
        )
        res = await db.execute(stmt)
        student = res.scalar_one_or_none()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found for this user account.",
            )
        return student

    @staticmethod
    def _evaluate_eligibility(
        student: Student,
        opp: Opportunity,
        student_skills_map: Dict[uuid.UUID, str]
    ) -> Tuple[bool, List[str], float]:
        """Calculates deterministic eligibility and skill match percentage."""
        is_eligible = True
        reasons = []

        criteria = opp.eligibility_criteria or {}
        min_cgpa = criteria.get("min_cgpa")
        required_grad_year = criteria.get("graduation_year")

        if min_cgpa is not None and student.cgpa is not None:
            if float(student.cgpa) < float(min_cgpa):
                is_eligible = False
                reasons.append(f"CGPA ({student.cgpa}) is below required minimum ({min_cgpa}).")
            else:
                reasons.append(f"CGPA requirement satisfied ({student.cgpa} >= {min_cgpa}).")
        elif min_cgpa is not None and student.cgpa is None:
            is_eligible = False
            reasons.append("CGPA is missing from student profile.")

        if required_grad_year is not None and student.graduation_year is not None:
            if student.graduation_year != required_grad_year:
                is_eligible = False
                reasons.append(f"Graduation year ({student.graduation_year}) does not match required ({required_grad_year}).")
            else:
                reasons.append(f"Graduation year requirement satisfied ({student.graduation_year}).")

        # Skill matching
        opp_skills = opp.required_skills or []
        if not opp_skills:
            skill_match_pct = 100.0
        else:
            matched_count = 0
            for opp_sk in opp_skills:
                if opp_sk.skill_id in student_skills_map:
                    matched_count += 1
                elif opp_sk.is_mandatory:
                    is_eligible = False
                    reasons.append(f"Missing mandatory skill: {opp_sk.skill.name if opp_sk.skill else 'Required Skill'}.")

            skill_match_pct = round((matched_count / len(opp_skills)) * 100.0, 1)

        if is_eligible and not reasons:
            reasons.append("All eligibility criteria met.")

        return is_eligible, reasons, skill_match_pct

    @classmethod
    async def get_student_opportunities(
        cls,
        db: AsyncSession,
        user: User,
        status_filter: Optional[str] = "OPEN"
    ) -> List[OpportunityStudentRead]:
        student = await cls.get_student_context(db, user)

        # Fetch student skills
        st_skills_stmt = select(StudentSkill).where(StudentSkill.student_id == student.id)
        st_skills_res = await db.execute(st_skills_stmt)
        student_skills_map = {s.skill_id: s.proficiency_level for s in st_skills_res.scalars().all()}

        # Fetch existing applications by student
        apps_stmt = select(Application).where(Application.student_id == student.id)
        apps_res = await db.execute(apps_stmt)
        apps_map = {a.opportunity_id: a for a in apps_res.scalars().all()}

        # Fetch opportunities
        opp_stmt = (
            select(Opportunity)
            .options(
                joinedload(Opportunity.company),
                selectinload(Opportunity.required_skills).joinedload(OpportunitySkill.skill)
            )
        )
        if status_filter:
            opp_stmt = opp_stmt.where(Opportunity.status == status_filter.upper())

        opp_stmt = opp_stmt.order_by(desc(Opportunity.created_at))
        opp_res = await db.execute(opp_stmt)
        opportunities = opp_res.scalars().unique().all()

        results = []
        for opp in opportunities:
            is_eligible, reasons, pct = cls._evaluate_eligibility(student, opp, student_skills_map)
            existing_app = apps_map.get(opp.id)

            req_skills_dto = [
                OpportunitySkillRead(
                    skill_id=s.skill_id,
                    skill_name=s.skill.name if s.skill else "Skill",
                    required_proficiency=s.required_proficiency,
                    is_mandatory=s.is_mandatory
                ) for s in opp.required_skills
            ]

            results.append(
                OpportunityStudentRead(
                    id=opp.id,
                    company_id=opp.company_id,
                    company_name=opp.company.name if opp.company else "Company",
                    company_logo_url=opp.company.logo_url if opp.company else None,
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
                    required_skills=req_skills_dto,
                    is_eligible=is_eligible,
                    eligibility_reasons=reasons,
                    skill_match_percentage=pct,
                    has_applied=existing_app is not None,
                    application_id=existing_app.id if existing_app else None
                )
            )

        return results

    @classmethod
    async def get_opportunity_detail(
        cls,
        db: AsyncSession,
        user: User,
        opportunity_id: uuid.UUID
    ) -> OpportunityStudentRead:
        student = await cls.get_student_context(db, user)

        st_skills_stmt = select(StudentSkill).where(StudentSkill.student_id == student.id)
        st_skills_res = await db.execute(st_skills_stmt)
        student_skills_map = {s.skill_id: s.proficiency_level for s in st_skills_res.scalars().all()}

        app_stmt = select(Application).where(
            and_(Application.student_id == student.id, Application.opportunity_id == opportunity_id)
        )
        existing_app = (await db.execute(app_stmt)).scalar_one_or_none()

        opp_stmt = (
            select(Opportunity)
            .options(
                joinedload(Opportunity.company),
                selectinload(Opportunity.required_skills).joinedload(OpportunitySkill.skill)
            )
            .where(Opportunity.id == opportunity_id)
        )
        opp = (await db.execute(opp_stmt)).scalar_one_or_none()
        if not opp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found.",
            )

        is_eligible, reasons, pct = cls._evaluate_eligibility(student, opp, student_skills_map)

        req_skills_dto = [
            OpportunitySkillRead(
                skill_id=s.skill_id,
                skill_name=s.skill.name if s.skill else "Skill",
                required_proficiency=s.required_proficiency,
                is_mandatory=s.is_mandatory
            ) for s in opp.required_skills
        ]

        return OpportunityStudentRead(
            id=opp.id,
            company_id=opp.company_id,
            company_name=opp.company.name if opp.company else "Company",
            company_logo_url=opp.company.logo_url if opp.company else None,
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
            required_skills=req_skills_dto,
            is_eligible=is_eligible,
            eligibility_reasons=reasons,
            skill_match_percentage=pct,
            has_applied=existing_app is not None,
            application_id=existing_app.id if existing_app else None
        )

    @classmethod
    async def apply_to_opportunity(
        cls,
        db: AsyncSession,
        user: User,
        opportunity_id: uuid.UUID,
        payload: StudentApplicationApplyRequest
    ) -> StudentApplicationRead:
        student = await cls.get_student_context(db, user)

        # Check opportunity existence
        opp_stmt = select(Opportunity).options(joinedload(Opportunity.company)).where(Opportunity.id == opportunity_id)
        opp = (await db.execute(opp_stmt)).scalar_one_or_none()
        if not opp or opp.status != "OPEN":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Opportunity is not open for application.",
            )

        # Check duplicate application
        existing_stmt = select(Application).where(
            and_(Application.opportunity_id == opportunity_id, Application.student_id == student.id)
        )
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already applied to this opportunity.",
            )

        # Atomic creation
        new_app = Application(
            opportunity_id=opportunity_id,
            student_id=student.id,
            cover_letter=payload.cover_letter,
            resume_version_id=payload.resume_version_id,
            current_status="APPLIED"
        )
        db.add(new_app)
        await db.flush()

        history_entry = ApplicationStatusHistory(
            application_id=new_app.id,
            status="APPLIED",
            notes="Application submitted by student.",
            changed_by_user_id=user.id
        )
        db.add(history_entry)

        await db.commit()
        await db.refresh(new_app)

        return StudentApplicationRead(
            id=new_app.id,
            opportunity_id=opp.id,
            opportunity_title=opp.title,
            company_name=opp.company.name if opp.company else "Company",
            current_status=new_app.current_status,
            applied_at=new_app.applied_at,
            cover_letter=new_app.cover_letter,
            resume_version_id=new_app.resume_version_id
        )

    @classmethod
    async def get_student_applications(
        cls,
        db: AsyncSession,
        user: User
    ) -> List[StudentApplicationRead]:
        student = await cls.get_student_context(db, user)

        stmt = (
            select(Application)
            .options(
                joinedload(Application.opportunity).joinedload(Opportunity.company)
            )
            .where(Application.student_id == student.id)
            .order_by(desc(Application.applied_at))
        )
        apps = (await db.execute(stmt)).scalars().all()

        return [
            StudentApplicationRead(
                id=a.id,
                opportunity_id=a.opportunity_id,
                opportunity_title=a.opportunity.title if a.opportunity else "Opportunity",
                company_name=a.opportunity.company.name if (a.opportunity and a.opportunity.company) else "Company",
                current_status=a.current_status,
                applied_at=a.applied_at,
                cover_letter=a.cover_letter,
                resume_version_id=a.resume_version_id
            )
            for a in apps
        ]

    @classmethod
    async def get_student_application_detail(
        cls,
        db: AsyncSession,
        user: User,
        application_id: uuid.UUID
    ) -> StudentApplicationRead:
        student = await cls.get_student_context(db, user)

        stmt = (
            select(Application)
            .options(
                joinedload(Application.opportunity).joinedload(Opportunity.company)
            )
            .where(and_(Application.id == application_id, Application.student_id == student.id))
        )
        app = (await db.execute(stmt)).scalar_one_or_none()
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found or cross-student access denied.",
            )

        return StudentApplicationRead(
            id=app.id,
            opportunity_id=app.opportunity_id,
            opportunity_title=app.opportunity.title if app.opportunity else "Opportunity",
            company_name=app.opportunity.company.name if (app.opportunity and app.opportunity.company) else "Company",
            current_status=app.current_status,
            applied_at=app.applied_at,
            cover_letter=app.cover_letter,
            resume_version_id=app.resume_version_id
        )

    @classmethod
    async def get_student_application_history(
        cls,
        db: AsyncSession,
        user: User,
        application_id: uuid.UUID
    ) -> List[StudentApplicationStatusHistoryRead]:
        student = await cls.get_student_context(db, user)

        # IDOR check
        app_stmt = select(Application).where(
            and_(Application.id == application_id, Application.student_id == student.id)
        )
        app = (await db.execute(app_stmt)).scalar_one_or_none()
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found or cross-student access denied.",
            )

        history_stmt = (
            select(ApplicationStatusHistory)
            .where(ApplicationStatusHistory.application_id == application_id)
            .order_by(ApplicationStatusHistory.created_at.asc())
        )
        history = (await db.execute(history_stmt)).scalars().all()

        return [
            StudentApplicationStatusHistoryRead(
                id=h.id,
                application_id=h.application_id,
                status=h.status,
                notes=h.notes,
                changed_by_user_id=h.changed_by_user_id,
                created_at=h.created_at
            )
            for h in history
        ]

    @classmethod
    async def get_student_internships(
        cls,
        db: AsyncSession,
        user: User
    ) -> List[StudentInternshipRead]:
        student = await cls.get_student_context(db, user)

        stmt = (
            select(Internship)
            .options(
                joinedload(Internship.company),
                joinedload(Internship.opportunity),
                selectinload(Internship.progress_reports),
                selectinload(Internship.evaluation),
            )
            .where(Internship.student_id == student.id)
            .order_by(desc(Internship.created_at))
        )
        internships = (await db.execute(stmt)).scalars().unique().all()

        return [cls._build_internship_read(i) for i in internships]

    @classmethod
    async def get_student_internship_detail(
        cls,
        db: AsyncSession,
        user: User,
        internship_id: uuid.UUID
    ) -> StudentInternshipRead:
        student = await cls.get_student_context(db, user)

        stmt = (
            select(Internship)
            .options(
                joinedload(Internship.company),
                joinedload(Internship.opportunity),
                selectinload(Internship.progress_reports),
                selectinload(Internship.evaluation),
            )
            .where(and_(Internship.id == internship_id, Internship.student_id == student.id))
        )
        internship = (await db.execute(stmt)).scalar_one_or_none()
        if not internship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Internship record not found or access denied.",
            )

        return cls._build_internship_read(internship)

    @classmethod
    async def submit_internship_progress(
        cls,
        db: AsyncSession,
        user: User,
        internship_id: uuid.UUID,
        payload: StudentInternshipProgressCreate
    ) -> StudentInternshipProgressRead:
        student = await cls.get_student_context(db, user)

        # IDOR check
        stmt = select(Internship).where(
            and_(Internship.id == internship_id, Internship.student_id == student.id)
        )
        internship = (await db.execute(stmt)).scalar_one_or_none()
        if not internship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Internship record not found or access denied.",
            )

        # Check existing report for week
        existing_stmt = select(InternshipProgress).where(
            and_(InternshipProgress.internship_id == internship_id, InternshipProgress.week_number == payload.week_number)
        )
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            existing.report_text = payload.report_text
            await db.commit()
            await db.refresh(existing)
            return StudentInternshipProgressRead(
                id=existing.id,
                internship_id=existing.internship_id,
                week_number=existing.week_number,
                report_text=existing.report_text,
                mentor_feedback=existing.mentor_feedback,
                submitted_at=existing.submitted_at
            )

        progress = InternshipProgress(
            internship_id=internship_id,
            week_number=payload.week_number,
            report_text=payload.report_text
        )
        db.add(progress)
        await db.commit()
        await db.refresh(progress)

        return StudentInternshipProgressRead(
            id=progress.id,
            internship_id=progress.internship_id,
            week_number=progress.week_number,
            report_text=progress.report_text,
            mentor_feedback=progress.mentor_feedback,
            submitted_at=progress.submitted_at
        )

    @classmethod
    async def get_student_placements(
        cls,
        db: AsyncSession,
        user: User
    ) -> List[StudentPlacementRecordRead]:
        student = await cls.get_student_context(db, user)

        stmt = (
            select(PlacementRecord)
            .options(
                joinedload(PlacementRecord.company),
                joinedload(PlacementRecord.opportunity),
                joinedload(PlacementRecord.institution)
            )
            .where(PlacementRecord.student_id == student.id)
            .order_by(desc(PlacementRecord.created_at))
        )
        placements = (await db.execute(stmt)).scalars().all()

        return [
            StudentPlacementRecordRead(
                id=p.id,
                student_id=p.student_id,
                company_id=p.company_id,
                company_name=p.company.name if p.company else "Company",
                opportunity_id=p.opportunity_id,
                opportunity_title=p.opportunity.title if p.opportunity else None,
                institution_id=p.institution_id,
                institution_name=p.institution.name if p.institution else "Institution",
                package_lpa=p.package_lpa,
                offer_letter_url=p.offer_letter_url,
                offer_date=p.offer_date,
                joining_date=p.joining_date,
                status=p.status,
                created_at=p.created_at
            )
            for p in placements
        ]

    @staticmethod
    def _build_internship_read(internship: Internship) -> StudentInternshipRead:
        reports_dto = [
            StudentInternshipProgressRead(
                id=r.id,
                internship_id=r.internship_id,
                week_number=r.week_number,
                report_text=r.report_text,
                mentor_feedback=r.mentor_feedback,
                submitted_at=r.submitted_at
            ) for r in (internship.progress_reports or [])
        ]

        eval_dto = None
        if internship.evaluation:
            e = internship.evaluation
            eval_dto = StudentInternshipEvaluationRead(
                id=e.id,
                internship_id=e.internship_id,
                technical_rating=e.technical_rating,
                soft_skills_rating=e.soft_skills_rating,
                punctuality_rating=e.punctuality_rating,
                overall_feedback=e.overall_feedback,
                evaluated_at=e.evaluated_at
            )

        return StudentInternshipRead(
            id=internship.id,
            student_id=internship.student_id,
            company_id=internship.company_id,
            company_name=internship.company.name if internship.company else "Company",
            opportunity_id=internship.opportunity_id,
            opportunity_title=internship.opportunity.title if internship.opportunity else None,
            supervisor_name=internship.supervisor_name,
            supervisor_email=internship.supervisor_email,
            start_date=internship.start_date,
            end_date=internship.end_date,
            stipend=internship.stipend,
            status=internship.status,
            created_at=internship.created_at,
            progress_reports=reports_dto,
            evaluation=eval_dto
        )
