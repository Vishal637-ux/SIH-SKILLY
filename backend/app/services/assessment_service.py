import uuid
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from sqlalchemy.orm import selectinload

from app.models.assessments import Assessment, AssessmentQuestion, AssessmentAttempt
from app.models.skills import Skill, StudentSkill, SkillEvidence
from app.models.careers import SkillGap, Roadmap, RoadmapItem, CareerRoleSkill
from app.models.institutions import Student
from app.schemas.student import (
    AssessmentQuestionPublic,
    AssessmentCatalogItem,
    AssessmentDetail,
    AssessmentAttemptRead,
    AssessmentResult,
    AssessmentHistoryItem,
    SkillSimple,
)


def calculate_proficiency_level(percentage: Decimal) -> str:
    """Canonical rule mapping score percentage to proficiency level."""
    if percentage >= Decimal("90.00"):
        return "EXPERT"
    elif percentage >= Decimal("75.00"):
        return "ADVANCED"
    elif percentage >= Decimal("60.00"):
        return "INTERMEDIATE"
    else:
        return "BEGINNER"


async def get_assessment_catalog(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> List[AssessmentCatalogItem]:
    """Retrieve all active assessments with student's personal attempt statistics."""
    stmt = (
        select(Assessment)
        .options(selectinload(Assessment.target_skill))
        .where(Assessment.is_active.is_(True))
        .order_by(Assessment.created_at.desc())
    )
    result = await db.execute(stmt)
    assessments = result.scalars().all()

    # Query student attempts for statistics
    attempts_stmt = select(AssessmentAttempt).where(AssessmentAttempt.student_id == student_id)
    attempts_res = await db.execute(attempts_stmt)
    user_attempts = attempts_res.scalars().all()

    attempts_by_assessment: Dict[uuid.UUID, List[AssessmentAttempt]] = {}
    for att in user_attempts:
        attempts_by_assessment.setdefault(att.assessment_id, []).append(att)

    catalog_items = []
    for ass in assessments:
        att_list = attempts_by_assessment.get(ass.id, [])
        attempts_count = len(att_list)
        best_score = max([a.percentage for a in att_list], default=None)

        skill_simple = None
        if ass.target_skill:
            skill_simple = SkillSimple(
                id=ass.target_skill.id,
                name=ass.target_skill.name,
                slug=ass.target_skill.slug,
                category=ass.target_skill.category,
            )

        catalog_items.append(
            AssessmentCatalogItem(
                id=ass.id,
                title=ass.title,
                assessment_type=ass.assessment_type,
                target_skill_id=ass.target_skill_id,
                target_skill=skill_simple,
                total_questions=ass.total_questions,
                duration_minutes=ass.duration_minutes,
                passing_score=ass.passing_score,
                is_active=ass.is_active,
                attempts_count=attempts_count,
                best_score=best_score,
            )
        )

    return catalog_items


async def get_assessment_detail(
    db: AsyncSession,
    assessment_id: uuid.UUID,
) -> AssessmentDetail:
    """Get metadata for a specific assessment."""
    stmt = (
        select(Assessment)
        .options(
            selectinload(Assessment.target_skill),
            selectinload(Assessment.questions),
        )
        .where(Assessment.id == assessment_id, Assessment.is_active.is_(True))
    )
    res = await db.execute(stmt)
    ass = res.scalar_one_or_none()
    if not ass:
        raise KeyError("Assessment not found or is currently inactive.")

    skill_simple = None
    if ass.target_skill:
        skill_simple = SkillSimple(
            id=ass.target_skill.id,
            name=ass.target_skill.name,
            slug=ass.target_skill.slug,
            category=ass.target_skill.category,
        )

    return AssessmentDetail(
        id=ass.id,
        title=ass.title,
        assessment_type=ass.assessment_type,
        target_skill_id=ass.target_skill_id,
        target_skill=skill_simple,
        total_questions=ass.total_questions,
        duration_minutes=ass.duration_minutes,
        passing_score=ass.passing_score,
        is_active=ass.is_active,
        questions_count=len(ass.questions or []),
    )


async def start_assessment_attempt(
    db: AsyncSession,
    student_id: uuid.UUID,
    assessment_id: uuid.UUID,
) -> AssessmentAttemptRead:
    """Initialize a new assessment attempt session and return questions (without correct_answer)."""
    # 1. Fetch assessment
    stmt = (
        select(Assessment)
        .options(
            selectinload(Assessment.target_skill),
            selectinload(Assessment.questions),
        )
        .where(Assessment.id == assessment_id, Assessment.is_active.is_(True))
    )
    res = await db.execute(stmt)
    ass = res.scalar_one_or_none()
    if not ass:
        raise KeyError("Assessment not found or is currently inactive.")

    # 2. Create AssessmentAttempt
    now = datetime.now(timezone.utc)
    attempt = AssessmentAttempt(
        assessment_id=ass.id,
        student_id=student_id,
        score=Decimal("0.00"),
        percentage=Decimal("0.00"),
        is_passed=False,
        responses={},
        started_at=now,
        completed_at=now,
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    # 3. Format questions (STRICTLY EXCLUDING correct_answer)
    sorted_questions = sorted(ass.questions or [], key=lambda q: q.question_order)
    public_questions = [
        AssessmentQuestionPublic(
            id=q.id,
            assessment_id=q.assessment_id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            points=q.points,
            question_order=q.question_order,
        )
        for q in sorted_questions
    ]

    skill_simple = None
    if ass.target_skill:
        skill_simple = SkillSimple(
            id=ass.target_skill.id,
            name=ass.target_skill.name,
            slug=ass.target_skill.slug,
            category=ass.target_skill.category,
        )

    detail = AssessmentDetail(
        id=ass.id,
        title=ass.title,
        assessment_type=ass.assessment_type,
        target_skill_id=ass.target_skill_id,
        target_skill=skill_simple,
        total_questions=ass.total_questions,
        duration_minutes=ass.duration_minutes,
        passing_score=ass.passing_score,
        is_active=ass.is_active,
        questions_count=len(sorted_questions),
    )

    return AssessmentAttemptRead(
        id=attempt.id,
        assessment_id=attempt.assessment_id,
        student_id=attempt.student_id,
        score=attempt.score,
        percentage=attempt.percentage,
        is_passed=attempt.is_passed,
        responses=attempt.responses,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        assessment=detail,
        questions=public_questions,
    )


async def get_assessment_attempt(
    db: AsyncSession,
    student_id: uuid.UUID,
    attempt_id: uuid.UUID,
) -> AssessmentAttemptRead:
    """Retrieve attempt session details with strict IDOR verification."""
    stmt = (
        select(AssessmentAttempt)
        .options(
            selectinload(AssessmentAttempt.assessment).selectinload(Assessment.target_skill),
            selectinload(AssessmentAttempt.assessment).selectinload(Assessment.questions),
        )
        .where(AssessmentAttempt.id == attempt_id)
    )
    res = await db.execute(stmt)
    attempt = res.scalar_one_or_none()

    if not attempt or attempt.student_id != student_id:
        raise KeyError("Assessment attempt not found or unauthorized.")

    ass = attempt.assessment
    sorted_questions = sorted(ass.questions or [], key=lambda q: q.question_order)
    public_questions = [
        AssessmentQuestionPublic(
            id=q.id,
            assessment_id=q.assessment_id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            points=q.points,
            question_order=q.question_order,
        )
        for q in sorted_questions
    ]

    skill_simple = None
    if ass.target_skill:
        skill_simple = SkillSimple(
            id=ass.target_skill.id,
            name=ass.target_skill.name,
            slug=ass.target_skill.slug,
            category=ass.target_skill.category,
        )

    detail = AssessmentDetail(
        id=ass.id,
        title=ass.title,
        assessment_type=ass.assessment_type,
        target_skill_id=ass.target_skill_id,
        target_skill=skill_simple,
        total_questions=ass.total_questions,
        duration_minutes=ass.duration_minutes,
        passing_score=ass.passing_score,
        is_active=ass.is_active,
        questions_count=len(sorted_questions),
    )

    return AssessmentAttemptRead(
        id=attempt.id,
        assessment_id=attempt.assessment_id,
        student_id=attempt.student_id,
        score=attempt.score,
        percentage=attempt.percentage,
        is_passed=attempt.is_passed,
        responses=attempt.responses,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        assessment=detail,
        questions=public_questions,
    )


async def submit_assessment_attempt(
    db: AsyncSession,
    student_id: uuid.UUID,
    attempt_id: uuid.UUID,
    responses: Dict[str, str],
) -> AssessmentResult:
    """Submit responses, execute deterministic grading, upsert skill passport & evidence, sync gaps & roadmaps."""
    # 1. Fetch attempt with assessment and questions
    stmt = (
        select(AssessmentAttempt)
        .options(
            selectinload(AssessmentAttempt.assessment).selectinload(Assessment.target_skill),
            selectinload(AssessmentAttempt.assessment).selectinload(Assessment.questions),
        )
        .where(AssessmentAttempt.id == attempt_id)
    )
    res = await db.execute(stmt)
    attempt = res.scalar_one_or_none()

    if not attempt or attempt.student_id != student_id:
        raise KeyError("Assessment attempt not found or unauthorized.")

    # Check immutability
    if bool(attempt.responses) or attempt.completed_at > attempt.started_at:
        raise ValueError("This assessment attempt has already been submitted and completed.")

    ass = attempt.assessment
    questions = ass.questions or []

    # 2. Deterministic Grading
    total_points = sum(q.points for q in questions)
    earned_points = 0

    for q in questions:
        q_id_str = str(q.id)
        student_ans = responses.get(q_id_str)
        if student_ans and str(student_ans).strip().lower() == str(q.correct_answer).strip().lower():
            earned_points += q.points

    pct = (Decimal(earned_points) / Decimal(total_points) * Decimal("100.00")) if total_points > 0 else Decimal("0.00")
    pct = min(Decimal("100.00"), max(Decimal("0.00"), round(pct, 2)))
    is_passed = bool(pct >= ass.passing_score)
    prof_level = calculate_proficiency_level(pct)

    submit_now = datetime.now(timezone.utc)
    if submit_now <= attempt.started_at:
        submit_now = attempt.started_at + timedelta(seconds=1)
    completed_time = submit_now

    attempt.score = Decimal(earned_points)
    attempt.percentage = pct
    attempt.is_passed = is_passed
    attempt.responses = responses
    attempt.completed_at = completed_time

    # 3. Upsert Student Skill Passport & Evidence
    if ass.target_skill_id:
        st_skill_stmt = select(StudentSkill).where(
            StudentSkill.student_id == student_id,
            StudentSkill.skill_id == ass.target_skill_id,
        )
        st_skill_res = await db.execute(st_skill_stmt)
        st_skill = st_skill_res.scalar_one_or_none()

        if st_skill:
            st_skill.proficiency_level = prof_level
            st_skill.verification_status = "ASSESSED"
            st_skill.score = pct
            st_skill.last_assessed_at = completed_time
        else:
            st_skill = StudentSkill(
                student_id=student_id,
                skill_id=ass.target_skill_id,
                proficiency_level=prof_level,
                verification_status="ASSESSED",
                score=pct,
                last_assessed_at=completed_time,
            )
            db.add(st_skill)
            await db.flush()

        # Add Skill Evidence
        evidence = SkillEvidence(
            student_skill_id=st_skill.id,
            evidence_type="ASSESSMENT",
            reference_id=attempt.id,
            title=f"Assessment: {ass.title} ({prof_level})",
            created_at=completed_time.isoformat(),
        )
        db.add(evidence)

        # 4. Synchronize Skill Gaps & Roadmap Items if Passed
        if is_passed:
            st_obj = (await db.execute(select(Student).where(Student.id == student_id))).scalar_one_or_none()
            if st_obj and st_obj.target_career_role_id:
                # Update matching skill gap
                gap_stmt = select(SkillGap).where(
                    SkillGap.student_id == student_id,
                    SkillGap.career_role_id == st_obj.target_career_role_id,
                    SkillGap.skill_id == ass.target_skill_id,
                )
                gap_res = await db.execute(gap_stmt)
                gap = gap_res.scalar_one_or_none()
                if gap:
                    gap.current_level = prof_level
                    gap.gap_score = Decimal("0.00")

                # Sync active roadmap item
                rm_stmt = (
                    select(RoadmapItem)
                    .join(Roadmap, RoadmapItem.roadmap_id == Roadmap.id)
                    .where(
                        Roadmap.student_id == student_id,
                        Roadmap.status == "ACTIVE",
                        RoadmapItem.skill_id == ass.target_skill_id,
                    )
                )
                rm_items = (await db.execute(rm_stmt)).scalars().all()
                for item in rm_items:
                    item.status = "COMPLETED"
                    item.completed_at = completed_time

    await db.commit()

    target_skill_name = ass.target_skill.name if ass.target_skill else None

    return AssessmentResult(
        attempt_id=attempt.id,
        assessment_id=ass.id,
        assessment_title=ass.title,
        target_skill_name=target_skill_name,
        score=attempt.score,
        percentage=attempt.percentage,
        passing_score=ass.passing_score,
        is_passed=attempt.is_passed,
        proficiency_level=prof_level,
        completed_at=attempt.completed_at,
    )


async def get_student_assessment_history(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> List[AssessmentHistoryItem]:
    """Retrieve history of completed assessment attempts for the authenticated student."""
    stmt = (
        select(AssessmentAttempt)
        .options(
            selectinload(AssessmentAttempt.assessment).selectinload(Assessment.target_skill),
        )
        .where(
            AssessmentAttempt.student_id == student_id,
            AssessmentAttempt.completed_at.isnot(None),
        )
        .order_by(AssessmentAttempt.completed_at.desc())
    )
    res = await db.execute(stmt)
    attempts = res.scalars().all()

    history = []
    for att in attempts:
        ass = att.assessment
        target_skill_name = ass.target_skill.name if ass and ass.target_skill else None
        prof_level = calculate_proficiency_level(att.percentage)

        history.append(
            AssessmentHistoryItem(
                attempt_id=att.id,
                assessment_id=ass.id,
                assessment_title=ass.title,
                target_skill_name=target_skill_name,
                score=att.score,
                percentage=att.percentage,
                passing_score=ass.passing_score,
                is_passed=att.is_passed,
                proficiency_level=prof_level,
                completed_at=att.completed_at,
            )
        )
    return history
