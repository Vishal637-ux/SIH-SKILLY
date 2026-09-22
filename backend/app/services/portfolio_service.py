import uuid
import json
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, and_, desc
from sqlalchemy.orm import selectinload, joinedload

from app.models.users import User, UserProfile
from app.models.institutions import Student, Institution, Department
from app.models.careers import CareerRole
from app.models.skills import Skill, StudentSkill, SkillEvidence
from app.models.portfolio import PortfolioItem, Recognition, ResumeVersion
from app.models.internships import Internship
from app.models.placements import PlacementRecord

from app.services.internship_service import InternshipService
from app.schemas.student import (
    StudentAcademicProfileRead,
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


class PortfolioService:

    @staticmethod
    async def get_student_context(db: AsyncSession, user: User) -> Student:
        """Resolves Student model for current authenticated user."""
        stmt = (
            select(Student)
            .options(
                joinedload(Student.user).joinedload(User.profile),
                joinedload(Student.institution),
                joinedload(Student.department),
                joinedload(Student.target_career_role),
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

    @classmethod
    async def get_digital_portfolio(cls, db: AsyncSession, user: User) -> DigitalPortfolioRead:
        student = await cls.get_student_context(db, user)

        # 1. Profile snapshot
        profile_dto = StudentAcademicProfileRead.model_validate(student)

        # 2. Skills with evidence
        skills_stmt = (
            select(StudentSkill)
            .options(
                joinedload(StudentSkill.skill),
                selectinload(StudentSkill.evidence)
            )
            .where(StudentSkill.student_id == student.id)
        )
        st_skills = (await db.execute(skills_stmt)).scalars().all()

        skills_list = []
        verified_evidence_count = 0
        for s in st_skills:
            evidence_dtos = []
            for ev in (s.evidence or []):
                verified_evidence_count += 1
                evidence_dtos.append({
                    "id": str(ev.id),
                    "evidence_type": ev.evidence_type,
                    "title": ev.title,
                    "url": ev.url,
                    "verified_at": ev.verified_at.isoformat() if ev.verified_at else None
                })
            skills_list.append({
                "skill_id": str(s.skill_id),
                "skill_name": s.skill.name if s.skill else "Skill",
                "category": s.skill.category if s.skill else "TECHNICAL",
                "proficiency_level": s.proficiency_level,
                "verification_status": s.verification_status,
                "evidence": evidence_dtos
            })

        # 3. Projects (Portfolio Items)
        proj_stmt = select(PortfolioItem).where(PortfolioItem.student_id == student.id).order_by(desc(PortfolioItem.created_at))
        projects = (await db.execute(proj_stmt)).scalars().all()
        projects_dto = [
            ProjectRead(
                id=p.id,
                student_id=p.student_id,
                item_type=p.item_type,
                title=p.title,
                description=p.description,
                repository_url=p.repository_url,
                live_url=p.live_url,
                role_in_project=p.role_in_project,
                start_date=p.start_date,
                end_date=p.end_date,
                is_featured=p.is_featured,
                created_at=p.created_at
            ) for p in projects
        ]

        # 4. Certifications & Recognitions
        rec_stmt = select(Recognition).where(Recognition.student_id == student.id).order_by(desc(Recognition.issued_date))
        recognitions = (await db.execute(rec_stmt)).scalars().all()
        recognitions_dto = [
            RecognitionRead(
                id=r.id,
                student_id=r.student_id,
                title=r.title,
                issuer_name=r.issuer_name,
                issuer_type=r.issuer_type,
                badge_icon=r.badge_icon,
                issued_date=r.issued_date,
                verification_hash=r.verification_hash,
                created_at=r.created_at
            ) for r in recognitions
        ]

        # 5. Internships & Placements
        internships_dto = await InternshipService.get_student_internships(db, user)
        placements_dto = await InternshipService.get_student_placements(db, user)

        # Calculate deterministic portfolio completion score (0-100)
        score = 20  # Base profile score
        if student.cgpa is not None:
            score += 10
        if student.target_career_role_id is not None:
            score += 10
        if len(skills_list) > 0:
            score += min(20, len(skills_list) * 5)
        if len(projects_dto) > 0:
            score += min(15, len(projects_dto) * 7.5)
        if len(recognitions_dto) > 0:
            score += min(10, len(recognitions_dto) * 5)
        if len(internships_dto) > 0:
            score += 15

        portfolio_score = int(min(100, score))

        return DigitalPortfolioRead(
            student_id=student.id,
            profile=profile_dto,
            skills=skills_list,
            projects=projects_dto,
            certifications=recognitions_dto,
            internships=internships_dto,
            placements=placements_dto,
            verified_evidence_count=verified_evidence_count,
            portfolio_score=portfolio_score
        )

    @classmethod
    async def add_project(cls, db: AsyncSession, user: User, payload: ProjectCreateRequest) -> ProjectRead:
        student = await cls.get_student_context(db, user)

        item = PortfolioItem(
            student_id=student.id,
            item_type=payload.item_type.upper().strip(),
            title=payload.title.strip(),
            description=payload.description.strip(),
            repository_url=payload.repository_url.strip() if payload.repository_url else None,
            live_url=payload.live_url.strip() if payload.live_url else None,
            role_in_project=payload.role_in_project.strip() if payload.role_in_project else None,
            start_date=payload.start_date,
            end_date=payload.end_date,
            is_featured=payload.is_featured
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)

        return ProjectRead(
            id=item.id,
            student_id=item.student_id,
            item_type=item.item_type,
            title=item.title,
            description=item.description,
            repository_url=item.repository_url,
            live_url=item.live_url,
            role_in_project=item.role_in_project,
            start_date=item.start_date,
            end_date=item.end_date,
            is_featured=item.is_featured,
            created_at=item.created_at
        )

    @classmethod
    async def delete_project(cls, db: AsyncSession, user: User, project_id: uuid.UUID) -> None:
        student = await cls.get_student_context(db, user)

        stmt = select(PortfolioItem).where(
            and_(PortfolioItem.id == project_id, PortfolioItem.student_id == student.id)
        )
        item = (await db.execute(stmt)).scalar_one_or_none()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio project not found or access denied.",
            )

        await db.delete(item)
        await db.commit()

    @classmethod
    async def add_recognition(cls, db: AsyncSession, user: User, payload: RecognitionCreateRequest) -> RecognitionRead:
        student = await cls.get_student_context(db, user)

        v_hash = payload.verification_hash.strip() if payload.verification_hash else f"VER_{uuid.uuid4().hex[:12].upper()}"

        rec = Recognition(
            student_id=student.id,
            title=payload.title.strip(),
            issuer_name=payload.issuer_name.strip(),
            issuer_type=payload.issuer_type.upper().strip(),
            badge_icon=payload.badge_icon.strip() if payload.badge_icon else None,
            issued_date=payload.issued_date if payload.issued_date else date.today(),
            verification_hash=v_hash
        )
        db.add(rec)
        await db.commit()
        await db.refresh(rec)

        return RecognitionRead(
            id=rec.id,
            student_id=rec.student_id,
            title=rec.title,
            issuer_name=rec.issuer_name,
            issuer_type=rec.issuer_type,
            badge_icon=rec.badge_icon,
            issued_date=rec.issued_date,
            verification_hash=rec.verification_hash,
            created_at=rec.created_at
        )

    @classmethod
    async def add_skill_evidence(cls, db: AsyncSession, user: User, payload: SkillEvidenceCreateRequest) -> SkillEvidenceRead:
        student = await cls.get_student_context(db, user)

        # IDOR check: verify student owns student_skill_id
        st_sk_stmt = select(StudentSkill).where(
            and_(StudentSkill.id == payload.student_skill_id, StudentSkill.student_id == student.id)
        )
        st_sk = (await db.execute(st_sk_stmt)).scalar_one_or_none()
        if not st_sk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student skill record not found or access denied.",
            )

        ev = SkillEvidence(
            student_skill_id=payload.student_skill_id,
            evidence_type=payload.evidence_type.upper().strip(),
            reference_id=payload.reference_id,
            title=payload.title.strip(),
            url=payload.url.strip() if payload.url else None,
            verified_by_user_id=user.id,
            verified_at=datetime.now(timezone.utc)
        )
        db.add(ev)
        
        # Update student_skill verification_status to VERIFIED
        st_sk.verification_status = "VERIFIED"

        await db.commit()
        await db.refresh(ev)

        return SkillEvidenceRead(
            id=ev.id,
            student_skill_id=ev.student_skill_id,
            evidence_type=ev.evidence_type,
            reference_id=ev.reference_id,
            title=ev.title,
            url=ev.url,
            verified_by_user_id=ev.verified_by_user_id,
            verified_at=ev.verified_at,
            created_at=ev.created_at
        )

    @classmethod
    async def generate_structured_resume(cls, db: AsyncSession, user: User, payload: ResumeGenerateRequest) -> ResumeVersionRead:
        student = await cls.get_student_context(db, user)
        portfolio = await cls.get_digital_portfolio(db, user)

        # Resolve target role title if provided
        target_role_title = None
        target_role_id = payload.target_role_id or student.target_career_role_id
        if target_role_id:
            role_stmt = select(CareerRole).where(CareerRole.id == target_role_id)
            r_obj = (await db.execute(role_stmt)).scalar_one_or_none()
            if r_obj:
                target_role_title = r_obj.title

        prof = student.user.profile if (student.user and student.user.profile) else None
        first_name = prof.first_name if prof else "Student"
        last_name = prof.last_name if prof else ""

        # Build structured JSON resume representation
        parsed_resume = {
            "header": {
                "name": f"{first_name} {last_name}".strip(),
                "email": student.user.email if student.user else "",
                "phone": prof.phone if prof else None,
                "city": prof.city if prof else None,
                "roll_number": student.roll_number,
                "institution": student.institution.name if student.institution else "Institution",
                "department": student.department.name if student.department else "Department",
                "graduation_year": student.graduation_year,
                "cgpa": float(student.cgpa) if student.cgpa else None,
                "target_role": target_role_title or (student.target_career_role.title if student.target_career_role else None)
            },
            "summary": f"Graduating student in {student.department.name if student.department else 'Computer Science'} with target specialization in {target_role_title or 'Software Engineering'}. Backed by verified digital skill evidence and practical project experience.",
            "skills": portfolio.skills,
            "projects": [json.loads(p.model_dump_json()) for p in portfolio.projects] if payload.include_projects else [],
            "certifications": [json.loads(c.model_dump_json()) for c in portfolio.certifications] if payload.include_certifications else [],
            "internships": [json.loads(i.model_dump_json()) for i in portfolio.internships] if payload.include_internships else [],
            "placements": [json.loads(pl.model_dump_json()) for pl in portfolio.placements],
            "verified_evidence_summary": {
                "total_evidence_count": portfolio.verified_evidence_count,
                "portfolio_score": portfolio.portfolio_score
            }
        }

        file_url = f"/api/v1/student/resumes/export/{uuid.uuid4().hex[:8]}.pdf"

        resume_ver = ResumeVersion(
            student_id=student.id,
            title=payload.title.strip(),
            file_url=file_url,
            parsed_content=parsed_resume,
            target_role_id=target_role_id
        )
        db.add(resume_ver)
        await db.commit()
        await db.refresh(resume_ver)

        return ResumeVersionRead(
            id=resume_ver.id,
            student_id=resume_ver.student_id,
            title=resume_ver.title,
            file_url=resume_ver.file_url,
            target_role_id=resume_ver.target_role_id,
            target_role_title=target_role_title,
            parsed_content=resume_ver.parsed_content,
            created_at=resume_ver.created_at
        )

    @classmethod
    async def get_student_resumes(cls, db: AsyncSession, user: User) -> List[ResumeVersionRead]:
        student = await cls.get_student_context(db, user)

        stmt = (
            select(ResumeVersion)
            .options(joinedload(ResumeVersion.target_role))
            .where(ResumeVersion.student_id == student.id)
            .order_by(desc(ResumeVersion.created_at))
        )
        resumes = (await db.execute(stmt)).scalars().all()

        return [
            ResumeVersionRead(
                id=r.id,
                student_id=r.student_id,
                title=r.title,
                file_url=r.file_url,
                target_role_id=r.target_role_id,
                target_role_title=r.target_role.title if r.target_role else None,
                parsed_content=r.parsed_content,
                created_at=r.created_at
            ) for r in resumes
        ]

    @classmethod
    async def get_student_resume_detail(cls, db: AsyncSession, user: User, resume_id: uuid.UUID) -> ResumeVersionRead:
        student = await cls.get_student_context(db, user)

        stmt = (
            select(ResumeVersion)
            .options(joinedload(ResumeVersion.target_role))
            .where(and_(ResumeVersion.id == resume_id, ResumeVersion.student_id == student.id))
        )
        resume = (await db.execute(stmt)).scalar_one_or_none()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume version not found or access denied.",
            )

        return ResumeVersionRead(
            id=resume.id,
            student_id=resume.student_id,
            title=resume.title,
            file_url=resume.file_url,
            target_role_id=resume.target_role_id,
            target_role_title=resume.target_role.title if resume.target_role else None,
            parsed_content=resume.parsed_content,
            created_at=resume.created_at
        )
