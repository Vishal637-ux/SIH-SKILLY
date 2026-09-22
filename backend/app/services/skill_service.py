import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import selectinload

from app.models.skills import Skill, SkillRelationship, StudentSkill, SkillEvidence
from app.models.careers import CareerRole, CareerRoleSkill, SkillGap
from app.models.institutions import Student

PROFICIENCY_RANKS: Dict[str, int] = {
    "NONE": 0,
    "BEGINNER": 1,
    "INTERMEDIATE": 2,
    "ADVANCED": 3,
    "EXPERT": 4,
}


def get_proficiency_rank(level: Optional[str]) -> int:
    """Return numeric rank for a given proficiency string."""
    if not level:
        return 0
    return PROFICIENCY_RANKS.get(level.strip().upper(), 0)


async def get_all_skills(
    db: AsyncSession,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Skill]:
    """Retrieve active master skills catalog with optional category and search filters."""
    stmt = select(Skill).where(Skill.is_verified.is_(True))

    if category and category.strip():
        stmt = stmt.where(Skill.category.ilike(f"%{category.strip()}%"))
    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(or_(Skill.name.ilike(term), Skill.description.ilike(term)))

    stmt = stmt.order_by(Skill.name)
    res = await db.execute(stmt)
    return res.scalars().all()


async def get_skill_detail(
    db: AsyncSession,
    skill_id: uuid.UUID,
) -> Dict[str, Any]:
    """Retrieve skill detail along with prerequisite and related skills from skill_relationships."""
    stmt = (
        select(Skill)
        .options(
            selectinload(Skill.parent_relationships).selectinload(SkillRelationship.child_skill),
            selectinload(Skill.child_relationships).selectinload(SkillRelationship.parent_skill),
        )
        .where(Skill.id == skill_id)
    )
    res = await db.execute(stmt)
    skill = res.scalar_one_or_none()

    if not skill:
        raise KeyError("Skill not found.")

    prerequisites = []
    related_skills = []

    # Child relationships where this skill is the child -> parent is prerequisite
    for rel in skill.child_relationships or []:
        if rel.relationship_type == "PREREQUISITE" and rel.parent_skill:
            prerequisites.append({
                "id": rel.parent_skill.id,
                "name": rel.parent_skill.name,
                "slug": rel.parent_skill.slug,
                "category": rel.parent_skill.category,
                "relationship_type": rel.relationship_type,
            })
        elif rel.parent_skill:
            related_skills.append({
                "id": rel.parent_skill.id,
                "name": rel.parent_skill.name,
                "slug": rel.parent_skill.slug,
                "category": rel.parent_skill.category,
                "relationship_type": rel.relationship_type,
            })

    # Parent relationships where this skill is the parent
    for rel in skill.parent_relationships or []:
        if rel.child_skill:
            related_skills.append({
                "id": rel.child_skill.id,
                "name": rel.child_skill.name,
                "slug": rel.child_skill.slug,
                "category": rel.child_skill.category,
                "relationship_type": rel.relationship_type,
            })

    return {
        "id": skill.id,
        "name": skill.name,
        "slug": skill.slug,
        "category": skill.category,
        "description": skill.description,
        "is_verified": skill.is_verified,
        "prerequisites": prerequisites,
        "related_skills": related_skills,
    }


async def check_prerequisite_cycle(
    db: AsyncSession,
    parent_skill_id: uuid.UUID,
    child_skill_id: uuid.UUID,
) -> bool:
    """Check if adding a PREREQUISITE edge parent_skill_id -> child_skill_id creates a cycle in the prerequisite graph."""
    if parent_skill_id == child_skill_id:
        return True  # Self loop

    visited = set()
    queue = [child_skill_id]

    while queue:
        curr = queue.pop(0)
        if curr == parent_skill_id:
            return True  # Cycle detected
        if curr in visited:
            continue
        visited.add(curr)

        # Find all skills that have `curr` as a parent in PREREQUISITE relationships
        stmt = select(SkillRelationship.child_skill_id).where(
            SkillRelationship.parent_skill_id == curr,
            SkillRelationship.relationship_type == "PREREQUISITE",
        )
        res = await db.execute(stmt)
        children = res.scalars().all()
        queue.extend(children)

    return False


async def get_student_skills_profile(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> List[Dict[str, Any]]:
    """Retrieve authenticated student's assessed skill passport and attached digital evidence."""
    stmt = (
        select(StudentSkill)
        .options(
            selectinload(StudentSkill.skill),
            selectinload(StudentSkill.evidence),
        )
        .where(StudentSkill.student_id == student_id)
        .order_by(StudentSkill.updated_at.desc())
    )
    res = await db.execute(stmt)
    st_skills = res.scalars().all()

    result = []
    for ss in st_skills:
        evidence_items = [
            {
                "id": ev.id,
                "evidence_type": ev.evidence_type,
                "reference_id": ev.reference_id,
                "title": ev.title,
                "url": ev.url,
                "created_at": ev.created_at,
            }
            for ev in (ss.evidence or [])
        ]

        result.append({
            "id": ss.id,
            "skill_id": ss.skill_id,
            "skill_name": ss.skill.name if ss.skill else "Unknown",
            "skill_category": ss.skill.category if ss.skill else "General",
            "proficiency_level": ss.proficiency_level,
            "verification_status": ss.verification_status,
            "score": ss.score,
            "last_assessed_at": ss.last_assessed_at,
            "evidence": evidence_items,
        })

    return result


async def calculate_student_skill_gaps(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> Dict[str, Any]:
    """Deterministically calculate skill gaps for a student against their target career role."""
    # 1. Fetch Student profile & target career role
    stmt_st = select(Student).where(Student.id == student_id)
    student = (await db.execute(stmt_st)).scalar_one_or_none()

    if not student or not student.target_career_role_id:
        return {
            "has_target_role": False,
            "target_career_role": None,
            "summary": {"satisfied_count": 0, "insufficient_count": 0, "missing_count": 0, "total_required": 0},
            "gaps": [],
        }

    # 2. Fetch Target Career Role metadata & required skills
    stmt_role = (
        select(CareerRole)
        .options(selectinload(CareerRole.role_skills).selectinload(CareerRoleSkill.skill))
        .where(CareerRole.id == student.target_career_role_id)
    )
    role = (await db.execute(stmt_role)).scalar_one_or_none()
    if not role:
        return {
            "has_target_role": False,
            "target_career_role": None,
            "summary": {"satisfied_count": 0, "insufficient_count": 0, "missing_count": 0, "total_required": 0},
            "gaps": [],
        }

    # 3. Fetch student's current skills
    stmt_st_skills = select(StudentSkill).where(StudentSkill.student_id == student_id)
    st_skills_res = await db.execute(stmt_st_skills)
    student_skills_map = {ss.skill_id: ss for ss in st_skills_res.scalars().all()}

    # 4. Compare required skills against student skills
    gaps_list = []
    satisfied_count = 0
    insufficient_count = 0
    missing_count = 0

    for cr_skill in role.role_skills or []:
        skill_id = cr_skill.skill_id
        skill_name = cr_skill.skill.name if cr_skill.skill else "Skill"
        required_level = cr_skill.required_level
        required_rank = get_proficiency_rank(required_level)

        st_skill = student_skills_map.get(skill_id)
        current_level = st_skill.proficiency_level if st_skill else "NONE"
        current_rank = get_proficiency_rank(current_level)

        if current_rank >= required_rank and current_rank > 0:
            status = "SATISFIED"
            gap_score = Decimal("0.00")
            satisfied_count += 1
        elif current_rank > 0:
            status = "INSUFFICIENT"
            gap_score = Decimal(str(required_rank - current_rank))
            insufficient_count += 1
        else:
            status = "MISSING"
            gap_score = Decimal(str(required_rank))
            missing_count += 1

        # Upsert SkillGap in PostgreSQL
        stmt_existing_gap = select(SkillGap).where(
            SkillGap.student_id == student_id,
            SkillGap.career_role_id == role.id,
            SkillGap.skill_id == skill_id,
        )
        existing_gap = (await db.execute(stmt_existing_gap)).scalar_one_or_none()

        if existing_gap:
            existing_gap.current_level = current_level
            existing_gap.target_level = required_level
            existing_gap.gap_score = gap_score
        else:
            new_gap = SkillGap(
                student_id=student_id,
                career_role_id=role.id,
                skill_id=skill_id,
                current_level=current_level,
                target_level=required_level,
                gap_score=gap_score,
            )
            db.add(new_gap)

        gaps_list.append({
            "skill_id": skill_id,
            "skill_name": skill_name,
            "category": cr_skill.skill.category if cr_skill.skill else "General",
            "importance_level": cr_skill.importance_level,
            "current_level": current_level,
            "target_level": required_level,
            "gap_status": status,
            "gap_score": gap_score,
        })

    await db.commit()

    return {
        "has_target_role": True,
        "target_career_role": {
            "id": role.id,
            "title": role.title,
            "slug": role.slug,
            "industry_domain": role.industry_domain,
        },
        "summary": {
            "satisfied_count": satisfied_count,
            "insufficient_count": insufficient_count,
            "missing_count": missing_count,
            "total_required": len(role.role_skills or []),
        },
        "gaps": gaps_list,
    }
