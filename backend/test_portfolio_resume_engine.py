import asyncio
import uuid
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal

from sqlalchemy import select, delete, and_
from app.core.database import async_session_maker
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.companies import Company
from app.models.skills import Skill, StudentSkill, SkillEvidence
from app.models.portfolio import PortfolioItem, Recognition, ResumeVersion
from app.models.internships import Internship
from app.models.placements import PlacementRecord
from app.services.portfolio_service import PortfolioService
from app.schemas.student import (
    ProjectCreateRequest,
    RecognitionCreateRequest,
    SkillEvidenceCreateRequest,
    ResumeGenerateRequest,
)
from fastapi import HTTPException, status


async def run_portfolio_resume_tests():
    print("==================================================")
    print("STARTING DIGITAL PORTFOLIO & RESUME ENGINE TESTS")
    print("==================================================")

    async with async_session_maker() as db:
        test_prefix = f"pf_{uuid.uuid4().hex[:6]}"

        # 1. Setup Test Fixtures in Real PostgreSQL
        inst = Institution(
            name=f"Inst {test_prefix}",
            code=f"INS_{test_prefix}",
            city="TechCity",
            state="TechState"
        )
        db.add(inst)
        await db.flush()

        dept = Department(institution_id=inst.id, name="Computer Science", code="CS")
        db.add(dept)
        await db.flush()

        # Student 1
        user_st1 = User(
            email=f"st1_{test_prefix}@skilly.edu",
            username=f"st1_{test_prefix}",
            hashed_password="hash",
            role="STUDENT",
            is_active=True
        )
        # Student 2 (IDOR check)
        user_st2 = User(
            email=f"st2_{test_prefix}@skilly.edu",
            username=f"st2_{test_prefix}",
            hashed_password="hash",
            role="STUDENT",
            is_active=True
        )
        db.add_all([user_st1, user_st2])
        await db.flush()

        prof_st1 = UserProfile(user_id=user_st1.id, first_name="Aarav", last_name="Verma", phone="9998887771", city="TechCity")
        prof_st2 = UserProfile(user_id=user_st2.id, first_name="Rohan", last_name="Sharma", phone="9998887772", city="TechCity")
        db.add_all([prof_st1, prof_st2])

        st1 = Student(
            user_id=user_st1.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"R1_{test_prefix}",
            enrollment_year=2023,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("9.20")
        )
        st2 = Student(
            user_id=user_st2.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"R2_{test_prefix}",
            enrollment_year=2023,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("8.00")
        )
        db.add_all([st1, st2])
        await db.flush()

        # Skill & StudentSkill
        sk_react = Skill(name=f"ReactJS_{test_prefix}", slug=f"react_{test_prefix}", category="FRONTEND", description="React UI Development")
        db.add(sk_react)
        await db.flush()

        st_sk1 = StudentSkill(student_id=st1.id, skill_id=sk_react.id, proficiency_level="ADVANCED", verification_status="SELF_REPORTED")
        db.add(st_sk1)
        await db.flush()

        print("[OK] Test setup completed successfully.")

        # Test 1: Add Project Showcase
        print("\n--- Test 1: Add Project Showcase ---")
        proj_payload = ProjectCreateRequest(
            item_type="PROJECT",
            title="E-Commerce Microservices",
            description="Distributed microservice platform built with FastAPI and React.",
            repository_url="https://github.com/skilly/ecommerce",
            live_url="https://ecommerce.skilly.dev",
            role_in_project="Lead Architect",
            is_featured=True
        )
        proj_res = await PortfolioService.add_project(db, user_st1, proj_payload)
        assert proj_res.title == "E-Commerce Microservices"
        assert proj_res.is_featured is True
        proj_id = proj_res.id
        print("[OK] Add project showcase PASS")

        # Test 2: Add Recognition / Certification
        print("\n--- Test 2: Add Recognition / Certification ---")
        rec_payload = RecognitionCreateRequest(
            title="AWS Certified Solutions Architect",
            issuer_name="Amazon Web Services",
            issuer_type="CERTIFICATION",
            issued_date=date.today() - timedelta(days=60)
        )
        rec_res = await PortfolioService.add_recognition(db, user_st1, rec_payload)
        assert rec_res.title == "AWS Certified Solutions Architect"
        assert rec_res.issuer_name == "Amazon Web Services"
        print("[OK] Add recognition PASS")

        # Test 3: Attach Verified Skill Evidence
        print("\n--- Test 3: Attach Verified Skill Evidence ---")
        ev_payload = SkillEvidenceCreateRequest(
            student_skill_id=st_sk1.id,
            evidence_type="PROJECT",
            title="GitHub Repository Proof & Passing Test Suite",
            url="https://github.com/skilly/ecommerce"
        )
        ev_res = await PortfolioService.add_skill_evidence(db, user_st1, ev_payload)
        assert ev_res.student_skill_id == st_sk1.id
        assert ev_res.title == "GitHub Repository Proof & Passing Test Suite"

        # Verify StudentSkill status updated to VERIFIED
        st_sk_check = (await db.execute(select(StudentSkill).where(StudentSkill.id == st_sk1.id))).scalar_one()
        assert st_sk_check.verification_status == "VERIFIED"
        print("[OK] Attach verified skill evidence PASS")

        # Test 4: Skill Evidence IDOR Protection
        print("\n--- Test 4: Skill Evidence IDOR Protection ---")
        try:
            await PortfolioService.add_skill_evidence(db, user_st2, ev_payload)
            assert False, "Student 2 should not be able to add evidence to Student 1's skill."
        except HTTPException as e:
            assert e.status_code == status.HTTP_404_NOT_FOUND
        print("[OK] Skill evidence IDOR protection PASS")

        # Test 5: Get Aggregated Digital Portfolio
        print("\n--- Test 5: Get Aggregated Digital Portfolio ---")
        portfolio = await PortfolioService.get_digital_portfolio(db, user_st1)
        assert portfolio.student_id == st1.id
        assert len(portfolio.skills) >= 1
        assert len(portfolio.projects) >= 1
        assert len(portfolio.certifications) >= 1
        assert portfolio.verified_evidence_count >= 1
        assert portfolio.portfolio_score > 40
        print("[OK] Get aggregated digital portfolio PASS")

        # Test 6: Generate Structured JSON Resume
        print("\n--- Test 6: Generate Structured JSON Resume ---")
        res_payload = ResumeGenerateRequest(
            title="Senior Fullstack Software Engineer Resume",
            include_projects=True,
            include_certifications=True,
            include_internships=True
        )
        resume_ver = await PortfolioService.generate_structured_resume(db, user_st1, res_payload)
        assert resume_ver.title == "Senior Fullstack Software Engineer Resume"
        assert resume_ver.parsed_content is not None
        assert "header" in resume_ver.parsed_content
        assert resume_ver.parsed_content["header"]["name"] == "Aarav Verma"
        resume_id = resume_ver.id
        print("[OK] Generate structured JSON resume PASS")

        # Test 7: Resume Listing & Retrieval
        print("\n--- Test 7: Resume Listing & Retrieval ---")
        resumes_list = await PortfolioService.get_student_resumes(db, user_st1)
        assert len(resumes_list) >= 1

        resume_detail = await PortfolioService.get_student_resume_detail(db, user_st1, resume_id)
        assert resume_detail.id == resume_id
        print("[OK] Resume listing & retrieval PASS")

        # Test 8: Resume IDOR Protection
        print("\n--- Test 8: Resume IDOR Protection ---")
        try:
            await PortfolioService.get_student_resume_detail(db, user_st2, resume_id)
            assert False, "Student 2 should be blocked from accessing Student 1's resume version."
        except HTTPException as e:
            assert e.status_code == status.HTTP_404_NOT_FOUND
        print("[OK] Resume IDOR protection PASS")

        # Test 9: Project Deletion & Ownership
        print("\n--- Test 9: Project Deletion & Ownership ---")
        # Student 2 attempts to delete Student 1's project -> 404
        try:
            await PortfolioService.delete_project(db, user_st2, proj_id)
            assert False, "Student 2 should not be able to delete Student 1's project."
        except HTTPException as e:
            assert e.status_code == status.HTTP_404_NOT_FOUND

        # Student 1 deletes their project
        await PortfolioService.delete_project(db, user_st1, proj_id)
        print("[OK] Project deletion & ownership PASS")

        # Cleanup test entities
        await db.execute(delete(ResumeVersion).where(ResumeVersion.student_id.in_([st1.id, st2.id])))
        await db.execute(delete(SkillEvidence).where(SkillEvidence.student_skill_id == st_sk1.id))
        await db.execute(delete(Recognition).where(Recognition.student_id.in_([st1.id, st2.id])))
        await db.execute(delete(PortfolioItem).where(PortfolioItem.student_id.in_([st1.id, st2.id])))
        await db.execute(delete(StudentSkill).where(StudentSkill.student_id.in_([st1.id, st2.id])))
        await db.execute(delete(Skill).where(Skill.id == sk_react.id))
        await db.execute(delete(Student).where(Student.id.in_([st1.id, st2.id])))
        await db.execute(delete(UserProfile).where(UserProfile.user_id.in_([user_st1.id, user_st2.id])))
        await db.execute(delete(User).where(User.id.in_([user_st1.id, user_st2.id])))
        await db.execute(delete(Department).where(Department.id == dept.id))
        await db.execute(delete(Institution).where(Institution.id == inst.id))
        await db.commit()

        print("\n==================================================")
        print("ALL DIGITAL PORTFOLIO & RESUME TESTS PASSED!")
        print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_portfolio_resume_tests())
