import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload

from app.models.careers import CareerRole, CareerRoleSkill, Roadmap, RoadmapItem, SkillGap
from app.models.skills import Skill, StudentSkill
from app.models.training import TrainingProgram, TrainingEnrollment
from app.models.institutions import Student


async def get_student_active_roadmap(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> Optional[Roadmap]:
    """Retrieve the student's current active career roadmap with items and skills loaded."""
    stmt = (
        select(Roadmap)
        .options(
            selectinload(Roadmap.items).selectinload(RoadmapItem.skill),
            selectinload(Roadmap.career_role),
        )
        .where(
            Roadmap.student_id == student_id,
            Roadmap.status == "ACTIVE",
        )
    )
    result = await db.execute(stmt)
    roadmap = result.scalar_one_or_none()
    
    if roadmap and roadmap.items:
        # Sort items sequentially by step_order
        roadmap.items.sort(key=lambda item: item.step_order)
        
    return roadmap


async def generate_or_sync_student_roadmap(
    db: AsyncSession,
    student: Student,
    force_regenerate: bool = False,
) -> Roadmap:
    """Deterministically generate or synchronize a career roadmap based on target role requirements."""
    if not student.target_career_role_id:
        raise ValueError("Student must select a target career role before generating a roadmap.")

    # 1. Fetch target career role details and required skills
    role_stmt = (
        select(CareerRole)
        .options(
            selectinload(CareerRole.role_skills).selectinload(CareerRoleSkill.skill)
        )
        .where(CareerRole.id == student.target_career_role_id)
    )
    role_res = await db.execute(role_stmt)
    career_role = role_res.scalar_one_or_none()
    if not career_role:
        raise ValueError("Target career role does not exist.")

    # 2. Fetch existing student skills for proficiency comparison
    student_skills_stmt = select(StudentSkill).where(StudentSkill.student_id == student.id)
    student_skills_res = await db.execute(student_skills_stmt)
    student_skills_map = {ss.skill_id: ss for ss in student_skills_res.scalars().all()}

    # 3. Archive any existing active roadmaps for different roles
    archive_stmt = (
        update(Roadmap)
        .where(
            Roadmap.student_id == student.id,
            Roadmap.career_role_id != student.target_career_role_id,
            Roadmap.status == "ACTIVE",
        )
        .values(status="ARCHIVED")
    )
    await db.execute(archive_stmt)

    # 4. Check if an active roadmap for this target role already exists
    active_roadmap = await get_student_active_roadmap(db, student.id)

    if active_roadmap and not force_regenerate:
        # Synchronize existing roadmap with role skills
        existing_skill_ids = {item.skill_id for item in active_roadmap.items if item.skill_id}
        max_step = max([item.step_order for item in active_roadmap.items], default=0)

        # Sort role skills: CORE first, then RECOMMENDED
        sorted_role_skills = sorted(
            career_role.role_skills,
            key=lambda rs: (0 if rs.importance_level == "CORE" else (1 if rs.importance_level == "RECOMMENDED" else 2)),
        )

        added = False
        for rs in sorted_role_skills:
            if rs.skill_id not in existing_skill_ids:
                max_step += 1
                new_item = RoadmapItem(
                    roadmap_id=active_roadmap.id,
                    skill_id=rs.skill_id,
                    step_order=max_step,
                    title=f"Master {rs.skill.name}",
                    description=f"Attain {rs.required_level} proficiency in {rs.skill.name} ({rs.importance_level} requirement for {career_role.title}).",
                    resource_url=f"https://documentation.skilly.org/skills/{rs.skill.slug}",
                    estimated_hours=15 if rs.importance_level == "CORE" else 10,
                    status="PENDING",
                    completed_at=None,
                )
                db.add(new_item)
                added = True
        if added:
            await db.commit()
            active_roadmap = await get_student_active_roadmap(db, student.id)
        return active_roadmap

    # 5. Create new roadmap if none exists or force_regenerate is True
    if active_roadmap and force_regenerate:
        active_roadmap.status = "ARCHIVED"
        await db.flush()

    new_roadmap = Roadmap(
        student_id=student.id,
        career_role_id=career_role.id,
        title=f"Career Roadmap: {career_role.title}",
        status="ACTIVE",
    )
    db.add(new_roadmap)
    await db.flush()

    # Sort role skills: CORE first, then RECOMMENDED, then OPTIONAL
    sorted_role_skills = sorted(
        career_role.role_skills,
        key=lambda rs: (0 if rs.importance_level == "CORE" else (1 if rs.importance_level == "RECOMMENDED" else 2)),
    )

    step_order = 1
    for rs in sorted_role_skills:
        skill = rs.skill
        st_skill = student_skills_map.get(rs.skill_id)
        
        # Check if already completed based on existing skill score or proficiency
        is_completed = False
        if st_skill and st_skill.proficiency_level in ["INTERMEDIATE", "ADVANCED", "EXPERT"]:
            if rs.required_level in ["BEGINNER", "INTERMEDIATE"]:
                is_completed = True

        item = RoadmapItem(
            roadmap_id=new_roadmap.id,
            skill_id=skill.id,
            step_order=step_order,
            title=f"Master {skill.name}",
            description=f"Attain {rs.required_level} proficiency in {skill.name} ({rs.importance_level} requirement for {career_role.title}).",
            resource_url=f"https://documentation.skilly.org/skills/{skill.slug}",
            estimated_hours=15 if rs.importance_level == "CORE" else 10,
            status="COMPLETED" if is_completed else "PENDING",
            completed_at=datetime.now(timezone.utc) if is_completed else None,
        )
        db.add(item)
        step_order += 1

    await db.commit()
    return await get_student_active_roadmap(db, student.id)


async def update_roadmap_item_status(
    db: AsyncSession,
    student_id: uuid.UUID,
    item_id: uuid.UUID,
    new_status: str,
) -> RoadmapItem:
    """Update roadmap item status with strict IDOR verification and timestamp handling."""
    if new_status not in ["PENDING", "IN_PROGRESS", "COMPLETED"]:
        raise ValueError("Invalid status. Must be PENDING, IN_PROGRESS, or COMPLETED.")

    # Load item and verify roadmap ownership
    stmt = (
        select(RoadmapItem)
        .options(
            selectinload(RoadmapItem.roadmap),
            selectinload(RoadmapItem.skill),
        )
        .where(RoadmapItem.id == item_id)
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()

    if not item or item.roadmap.student_id != student_id:
        raise KeyError("Roadmap item not found or unauthorized.")

    # Status transition logic
    item.status = new_status
    if new_status == "COMPLETED":
        if not item.completed_at:
            item.completed_at = datetime.now(timezone.utc)
    else:
        item.completed_at = None

    await db.commit()
    await db.refresh(item)
    return item


async def get_student_learning_workspace(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> Dict[str, Any]:
    """Retrieve available training programs and student's active enrollments."""
    # 1. Fetch student's enrollments with training program loaded
    enroll_stmt = (
        select(TrainingEnrollment)
        .options(selectinload(TrainingEnrollment.training_program))
        .where(TrainingEnrollment.student_id == student_id)
    )
    enroll_res = await db.execute(enroll_stmt)
    current_enrollments = list(enroll_res.scalars().all())
    enrolled_program_ids = {e.training_program_id for e in current_enrollments}

    # 2. Fetch available training programs
    prog_stmt = select(TrainingProgram).where(TrainingProgram.status.in_(["UPCOMING", "ONGOING"]))
    prog_res = await db.execute(prog_stmt)
    available_programs = list(prog_res.scalars().all())

    # Attach is_enrolled flag for display
    for prog in available_programs:
        prog.is_enrolled = prog.id in enrolled_program_ids

    enrolled_count = len(current_enrollments)
    completed_count = sum(1 for e in current_enrollments if e.completion_status == "COMPLETED")

    return {
        "available_programs": available_programs,
        "current_enrollments": current_enrollments,
        "enrolled_count": enrolled_count,
        "completed_count": completed_count,
    }


async def enroll_student_in_training(
    db: AsyncSession,
    student_id: uuid.UUID,
    program_id: uuid.UUID,
) -> TrainingEnrollment:
    """Enroll student in an available training program with duplicate protection."""
    # 1. Verify program exists
    prog_stmt = select(TrainingProgram).where(TrainingProgram.id == program_id)
    prog_res = await db.execute(prog_stmt)
    program = prog_res.scalar_one_or_none()
    if not program:
        raise KeyError("Training program not found.")

    # 2. Check for duplicate enrollment
    existing_stmt = select(TrainingEnrollment).where(
        TrainingEnrollment.student_id == student_id,
        TrainingEnrollment.training_program_id == program_id,
    )
    existing_res = await db.execute(existing_stmt)
    if existing_res.scalar_one_or_none():
        raise ValueError("Student is already enrolled in this training program.")

    # 3. Create enrollment
    enrollment = TrainingEnrollment(
        student_id=student_id,
        training_program_id=program_id,
        completion_status="ENROLLED",
        attendance_percentage=Decimal("0.00"),
    )
    db.add(enrollment)
    await db.commit()

    # Re-query with training_program loaded
    res_stmt = (
        select(TrainingEnrollment)
        .options(selectinload(TrainingEnrollment.training_program))
        .where(TrainingEnrollment.id == enrollment.id)
    )
    res = await db.execute(res_stmt)
    return res.scalar_one()
