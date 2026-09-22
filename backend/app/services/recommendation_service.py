import uuid
from typing import Optional, List, Dict, Set, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload

from app.models.users import User, UserProfile
from app.models.institutions import Student, Department, Institution
from app.models.skills import Skill, StudentSkill
from app.models.careers import CareerRole, CareerRoleSkill, SkillGap
from app.models.opportunities import Opportunity, OpportunitySkill, Application
from app.models.training import TrainingProgram
from app.models.mentorship import MentorConnection
from app.models.embeddings import Embedding

from app.schemas.recommendation import (
    RecommendationItem,
    RecommendationOverviewResponse,
    RecommendationCategoryResponse,
)


class RecommendationService:

    @classmethod
    async def get_student_context(cls, db: AsyncSession, user: User) -> Student:
        """Resolve student context for authenticated user with security check."""
        stmt = (
            select(Student)
            .options(
                selectinload(Student.institution),
                selectinload(Student.department),
                selectinload(Student.target_career_role).selectinload(CareerRole.role_skills).selectinload(CareerRoleSkill.skill),
            )
            .where(Student.user_id == user.id)
        )
        res = await db.execute(stmt)
        student = res.scalar_one_or_none()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not initialized. Please complete profile setup.",
            )
        return student

    @classmethod
    async def get_student_skills_set(cls, db: AsyncSession, student_id: uuid.UUID) -> Tuple[Set[str], Dict[str, uuid.UUID]]:
        """Fetch student's verified skills as a set of skill names (lowercase) and map of name->id."""
        stmt = select(StudentSkill).options(joinedload(StudentSkill.skill)).where(StudentSkill.student_id == student_id)
        res = await db.execute(stmt)
        student_skills = res.scalars().all()

        skill_names = set()
        name_map = {}
        for ss in student_skills:
            if ss.skill:
                n = ss.skill.name.strip().lower()
                skill_names.add(n)
                name_map[n] = ss.skill.id
        return skill_names, name_map

    @classmethod
    async def get_student_gap_names(cls, db: AsyncSession, student_id: uuid.UUID) -> Set[str]:
        """Fetch student's active skill gap names (lowercase)."""
        stmt = select(SkillGap).options(joinedload(SkillGap.skill)).where(SkillGap.student_id == student_id)
        res = await db.execute(stmt)
        gaps = res.scalars().all()
        return {g.skill.name.strip().lower() for g in gaps if g.skill}

    # ------------------------------------------------------------------
    # 1. Career Role Recommendations
    # ------------------------------------------------------------------
    @classmethod
    async def get_career_recommendations(
        cls, db: AsyncSession, user: User, limit: int = 10
    ) -> List[RecommendationItem]:
        student = await cls.get_student_context(db, user)
        student_skill_names, _ = await cls.get_student_skills_set(db, student.id)
        target_role_id = student.target_career_role_id

        stmt = (
            select(CareerRole)
            .options(selectinload(CareerRole.role_skills).selectinload(CareerRoleSkill.skill))
            .where(CareerRole.is_active.is_(True))
        )
        res = await db.execute(stmt)
        roles = res.scalars().all()

        recommendations: List[RecommendationItem] = []

        for role in roles:
            required_skill_names = [rs.skill.name.strip().lower() for rs in (role.role_skills or []) if rs.skill]
            
            matched = [s for s in required_skill_names if s in student_skill_names]
            missing = [s for s in required_skill_names if s not in student_skill_names]

            total_req = max(1, len(required_skill_names))
            base_ratio = len(matched) / total_req
            score = round(base_ratio * 80.0, 1)

            # Bonus for current active target role
            is_target = bool(target_role_id and target_role_id == role.id)
            if is_target:
                score = min(99.5, score + 20.0)

            # Format explainability
            matched_display = [m.title() for m in matched[:4]]
            missing_display = [m.title() for m in missing[:4]]

            if is_target:
                explanation = f"Primary Target Role: Matches {len(matched)} of your verified skills including {', '.join(matched_display) if matched_display else 'foundational skills'}."
            elif matched:
                explanation = f"Strong Skill Fit: Matches {len(matched)} of your verified skills ({', '.join(matched_display)})."
            else:
                explanation = f"Recommended Career Role: Requires {len(required_skill_names)} core skills to build your career portfolio."

            recommendations.append(
                RecommendationItem(
                    id=role.id,
                    category="CAREER_ROLE",
                    title=role.title,
                    subtitle=role.industry_domain,
                    organization_or_provider="SKILLY Career Taxonomy",
                    score=score,
                    matched_skills=matched_display,
                    skill_gaps=missing_display,
                    explanation=explanation,
                    eligibility=True,
                    action_link="/student/careers",
                )
            )

        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:limit]

    # ------------------------------------------------------------------
    # 2. Learning / Training Recommendations
    # ------------------------------------------------------------------
    @classmethod
    async def get_learning_recommendations(
        cls, db: AsyncSession, user: User, limit: int = 10
    ) -> List[RecommendationItem]:
        student = await cls.get_student_context(db, user)
        student_skill_names, _ = await cls.get_student_skills_set(db, student.id)
        gap_skill_names = await cls.get_student_gap_names(db, student.id)

        stmt = select(TrainingProgram).where(TrainingProgram.status.in_(["ACTIVE", "UPCOMING", "ONGOING"]))
        res = await db.execute(stmt)
        programs = res.scalars().all()

        recommendations: List[RecommendationItem] = []

        for tp in programs:
            # Simple keyword matching on program skills or domain
            title_lower = tp.title.lower()
            desc_lower = (tp.description or "").lower()

            matched_gaps = [g for g in gap_skill_names if g in title_lower or g in desc_lower]
            matched_existing = [s for s in student_skill_names if s in title_lower or s in desc_lower]

            score = 60.0
            if matched_gaps:
                score += min(35.0, len(matched_gaps) * 15.0)
            elif matched_existing:
                score += 10.0

            matched_display = [s.title() for s in (matched_gaps + matched_existing)[:4]]
            missing_display = [g.title() for g in list(gap_skill_names - set(matched_gaps))[:3]]

            if matched_gaps:
                explanation = f"Fills Skill Gap: Directly addresses your identified competency gaps in {', '.join(matched_display)}."
            else:
                explanation = f"Recommended Training: Enhances your practical skills in {tp.title}."

            recommendations.append(
                RecommendationItem(
                    id=tp.id,
                    category="TRAINING_PROGRAM",
                    title=tp.title,
                    subtitle=tp.program_type,
                    organization_or_provider="Partner Academy / Faculty",
                    score=round(min(98.0, score), 1),
                    matched_skills=matched_display,
                    skill_gaps=missing_display,
                    explanation=explanation,
                    eligibility=True,
                    action_link="/student/learning",
                )
            )

        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:limit]

    # ------------------------------------------------------------------
    # 3. Internship / Job Opportunity Recommendations
    # ------------------------------------------------------------------
    @classmethod
    async def get_opportunity_recommendations(
        cls, db: AsyncSession, user: User, limit: int = 10
    ) -> List[RecommendationItem]:
        student = await cls.get_student_context(db, user)
        student_skill_names, _ = await cls.get_student_skills_set(db, student.id)

        # Check existing student applications to exclude already applied
        applied_stmt = select(Application.opportunity_id).where(Application.student_id == student.id)
        applied_res = await db.execute(applied_stmt)
        applied_opp_ids = set(applied_res.scalars().all())

        # Load open opportunities
        stmt = (
            select(Opportunity)
            .options(
                joinedload(Opportunity.company),
                selectinload(Opportunity.required_skills).selectinload(OpportunitySkill.skill),
            )
            .where(Opportunity.status == "OPEN")
        )
        res = await db.execute(stmt)
        opportunities = res.scalars().unique().all()

        recommendations: List[RecommendationItem] = []

        for opp in opportunities:
            if opp.id in applied_opp_ids:
                continue  # Skip already applied opportunities

            # Hard eligibility checks
            is_eligible = True
            eligibility_reasons = []

            min_cgpa_req = (opp.eligibility_criteria or {}).get("min_cgpa") if isinstance(opp.eligibility_criteria, dict) else None
            if min_cgpa_req is not None and student.cgpa is not None:
                if float(student.cgpa) < float(min_cgpa_req):
                    is_eligible = False
                    eligibility_reasons.append(f"Requires minimum CGPA {min_cgpa_req} (Yours: {student.cgpa})")

            # Check required skills
            opp_skill_names = [os.skill.name.strip().lower() for os in (opp.required_skills or []) if os.skill]

            matched = [s for s in opp_skill_names if s in student_skill_names]
            missing = [s for s in opp_skill_names if s not in student_skill_names]

            total_req = max(1, len(opp_skill_names))
            base_ratio = len(matched) / total_req
            score = round(base_ratio * 90.0, 1)

            if not is_eligible:
                score = min(40.0, score * 0.5)

            matched_display = [m.title() for m in matched[:4]]
            missing_display = [m.title() for m in missing[:4]]
            company_name = opp.company.name if opp.company else "Industry Partner"

            if is_eligible and matched:
                explanation = f"Skill-Matched Opportunity at {company_name}: Your skills in {', '.join(matched_display)} match opportunity requirements."
            elif is_eligible:
                explanation = f"Eligible Opportunity at {company_name}: Open for application based on your academic profile."
            else:
                explanation = f"Ineligible Opportunity: {'; '.join(eligibility_reasons)}."

            recommendations.append(
                RecommendationItem(
                    id=opp.id,
                    category="OPPORTUNITY",
                    title=opp.title,
                    subtitle=opp.role_type,
                    organization_or_provider=company_name,
                    score=score,
                    matched_skills=matched_display,
                    skill_gaps=missing_display,
                    explanation=explanation,
                    eligibility=is_eligible,
                    action_link="/student/internships",
                )
            )

        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:limit]

    # ------------------------------------------------------------------
    # 4. Mentor Recommendations
    # ------------------------------------------------------------------
    @classmethod
    async def get_mentor_recommendations(
        cls, db: AsyncSession, user: User, limit: int = 10
    ) -> List[RecommendationItem]:
        student = await cls.get_student_context(db, user)
        student_skill_names, _ = await cls.get_student_skills_set(db, student.id)
        gap_skill_names = await cls.get_student_gap_names(db, student.id)

        # Check existing connections
        conn_stmt = select(MentorConnection.mentor_user_id).where(MentorConnection.student_id == student.id)
        conn_res = await db.execute(conn_stmt)
        connected_mentor_user_ids = set(conn_res.scalars().all())

        # Load active Alumni / Mentor profiles
        stmt = (
            select(User)
            .options(joinedload(User.profile))
            .where(User.role == "ALUMNI", User.is_active.is_(True))
        )
        res = await db.execute(stmt)
        alumni_users = res.scalars().all()

        recommendations: List[RecommendationItem] = []

        for m_user in alumni_users:
            if m_user.id in connected_mentor_user_ids or m_user.id == user.id:
                continue  # Skip existing connection or self

            prof = m_user.profile
            m_name = f"{prof.first_name} {prof.last_name}".strip() if prof and prof.first_name else m_user.username
            bio = (prof.bio if prof else "") or "Verified Alumni Mentor"

            # Compute overlap between mentor bio/profile and student gaps/skills
            bio_lower = bio.lower()
            matched_gaps = [g for g in gap_skill_names if g in bio_lower]
            matched_skills = [s for s in student_skill_names if s in bio_lower]

            score = 70.0
            if matched_gaps:
                score += 20.0
            elif matched_skills:
                score += 10.0

            matched_display = [s.title() for s in (matched_gaps + matched_skills)[:4]]
            missing_display = [g.title() for g in list(gap_skill_names - set(matched_gaps))[:3]]

            explanation = (
                f"Expert Mentor Match: {m_name} offers guidance in {', '.join(matched_display) if matched_display else 'career role development'}."
            )

            recommendations.append(
                RecommendationItem(
                    id=m_user.id,
                    category="MENTOR",
                    title=f"Mentor: {m_name}",
                    subtitle=prof.city if prof and prof.city else "Industry Professional",
                    organization_or_provider="SKILLY Mentor Network",
                    score=round(min(98.0, score), 1),
                    matched_skills=matched_display,
                    skill_gaps=missing_display,
                    explanation=explanation,
                    eligibility=True,
                    action_link="/student/mentorship",
                )
            )

        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:limit]

    # ------------------------------------------------------------------
    # Unified Overview
    # ------------------------------------------------------------------
    @classmethod
    async def get_student_recommendations_overview(
        cls, db: AsyncSession, user: User
    ) -> RecommendationOverviewResponse:
        student = await cls.get_student_context(db, user)

        # Count assessed skills
        sk_count = (
            await db.execute(select(func.count(StudentSkill.id)).where(StudentSkill.student_id == student.id))
        ).scalar() or 0

        # Count active gaps
        gap_count = (
            await db.execute(select(func.count(SkillGap.id)).where(SkillGap.student_id == student.id))
        ).scalar() or 0

        career_recs = await cls.get_career_recommendations(db, user, limit=3)
        learning_recs = await cls.get_learning_recommendations(db, user, limit=3)
        opp_recs = await cls.get_opportunity_recommendations(db, user, limit=3)
        mentor_recs = await cls.get_mentor_recommendations(db, user, limit=3)

        target_title = student.target_career_role.title if student.target_career_role else None

        return RecommendationOverviewResponse(
            student_id=student.id,
            target_role_title=target_title,
            assessed_skills_count=sk_count,
            active_gaps_count=gap_count,
            career_recommendations=career_recs,
            learning_recommendations=learning_recs,
            opportunity_recommendations=opp_recs,
            mentor_recommendations=mentor_recs,
        )
