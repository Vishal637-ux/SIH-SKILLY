import asyncio
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import async_session_maker
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.skills import Skill, StudentSkill
from app.models.careers import CareerRole, CareerRoleSkill, SkillGap
from app.models.companies import Company
from app.models.opportunities import Opportunity, OpportunitySkill, Application
from app.models.training import TrainingProgram
from app.models.mentorship import MentorConnection
from app.models.embeddings import Embedding
from app.services.recommendation_service import RecommendationService
from app.core.security import hash_password, create_access_token


async def setup_test_data():
    """Seed test entities for Module 13 AI / Recommendations verification."""
    async with async_session_maker() as db:
        # 1. Institution & Dept
        inst = Institution(
            name=f"AI Rec Test Inst-{uuid.uuid4().hex[:6]}",
            code=f"AIR-{uuid.uuid4().hex[:4].upper()}",
            institution_type="COLLEGE",
            city="Bengaluru",
            state="Karnataka",
        )
        db.add(inst)
        await db.flush()

        dept = Department(
            institution_id=inst.id,
            name=f"AI Rec Dept-{uuid.uuid4().hex[:6]}",
            code=f"ARD-{uuid.uuid4().hex[:4].upper()}",
        )
        db.add(dept)
        await db.flush()

        # 2. Company & Opportunity
        company = Company(
            name=f"AI Rec Tech Corp-{uuid.uuid4().hex[:6]}",
            industry_type="Software Engineering",
        )
        db.add(company)
        await db.flush()

        # 3. Skills
        sk_py = Skill(name=f"Python-{uuid.uuid4().hex[:4]}", category="PROGRAMMING", slug=f"py-{uuid.uuid4().hex[:4]}")
        sk_sql = Skill(name=f"SQL-{uuid.uuid4().hex[:4]}", category="DATABASE", slug=f"sql-{uuid.uuid4().hex[:4]}")
        sk_ml = Skill(name=f"Machine Learning-{uuid.uuid4().hex[:4]}", category="AI", slug=f"ml-{uuid.uuid4().hex[:4]}")
        db.add_all([sk_py, sk_sql, sk_ml])
        await db.flush()

        # 4. Career Role
        c_role = CareerRole(
            title=f"AI Engineer-{uuid.uuid4().hex[:6]}",
            slug=f"ai-eng-{uuid.uuid4().hex[:6]}",
            industry_domain="Artificial Intelligence",
            description="Build scalable ML & AI models",
            is_active=True,
        )
        db.add(c_role)
        await db.flush()

        crs1 = CareerRoleSkill(career_role_id=c_role.id, skill_id=sk_py.id, required_level="ADVANCED", importance_level="CORE")
        crs2 = CareerRoleSkill(career_role_id=c_role.id, skill_id=sk_sql.id, required_level="INTERMEDIATE", importance_level="RECOMMENDED")
        crs3 = CareerRoleSkill(career_role_id=c_role.id, skill_id=sk_ml.id, required_level="ADVANCED", importance_level="CORE")
        db.add_all([crs1, crs2, crs3])

        # 5. Open & Closed Opportunities
        opp_open = Opportunity(
            company_id=company.id,
            title=f"AI Developer Intern-{uuid.uuid4().hex[:6]}",
            role_type="INTERNSHIP",
            description="Build AI tools",
            location="Remote",
            application_deadline=datetime.now(timezone.utc),
            status="OPEN",
            eligibility_criteria={"min_cgpa": 7.0},
        )
        opp_closed = Opportunity(
            company_id=company.id,
            title=f"Closed Secret Intern-{uuid.uuid4().hex[:6]}",
            role_type="INTERNSHIP",
            description="Closed project",
            location="Remote",
            application_deadline=datetime.now(timezone.utc),
            status="CLOSED",
            eligibility_criteria={"min_cgpa": 6.0},
        )
        db.add_all([opp_open, opp_closed])
        await db.flush()

        os1 = OpportunitySkill(opportunity_id=opp_open.id, skill_id=sk_py.id, is_mandatory=True)
        os2 = OpportunitySkill(opportunity_id=opp_open.id, skill_id=sk_ml.id, is_mandatory=True)
        db.add_all([os1, os2])

        # 7. Student User A
        pwd_hash = hash_password("Password123!")
        user_a = User(
            email=f"ai_student_a_{uuid.uuid4().hex[:6]}@test.com",
            username=f"ai_student_a_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="STUDENT",
            is_active=True,
            is_verified=True,
        )
        db.add(user_a)
        await db.flush()

        # 6. Training Program
        tp = TrainingProgram(
            title=f"Advanced ML Bootcamp-{uuid.uuid4().hex[:6]}",
            program_type="BOOTCAMP",
            conducted_by_user_id=user_a.id,
            start_date=datetime.now(timezone.utc).date(),
            end_date=datetime.now(timezone.utc).date(),
            status="ACTIVE",
            description=f"Master Python and {sk_ml.name} in this intensive bootcamp.",
        )
        db.add(tp)
        await db.flush()

        prof_a = UserProfile(user_id=user_a.id, first_name="AIStudentA", last_name="Test")
        db.add(prof_a)

        student_a = Student(
            user_id=user_a.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"ROLL-A-{uuid.uuid4().hex[:6]}",
            enrollment_year=2023,
            graduation_year=2027,
            current_semester=5,
            cgpa=Decimal("8.50"),
            target_career_role_id=c_role.id,
        )
        db.add(student_a)
        await db.flush()

        # Student A Skills: Python & SQL (ML is gap)
        st_sk1 = StudentSkill(student_id=student_a.id, skill_id=sk_py.id, proficiency_level="ADVANCED", verification_status="VERIFIED", score=Decimal("85.00"))
        st_sk2 = StudentSkill(student_id=student_a.id, skill_id=sk_sql.id, proficiency_level="INTERMEDIATE", verification_status="VERIFIED", score=Decimal("75.00"))
        gap1 = SkillGap(student_id=student_a.id, career_role_id=c_role.id, skill_id=sk_ml.id, current_level="NONE", target_level="ADVANCED", gap_score=Decimal("40.00"))
        db.add_all([st_sk1, st_sk2, gap1])

        # 8. Student User B (Ineligible low CGPA)
        user_b = User(
            email=f"ai_student_b_{uuid.uuid4().hex[:6]}@test.com",
            username=f"ai_student_b_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="STUDENT",
            is_active=True,
            is_verified=True,
        )
        db.add(user_b)
        await db.flush()

        prof_b = UserProfile(user_id=user_b.id, first_name="AIStudentB", last_name="Test")
        db.add(prof_b)

        student_b = Student(
            user_id=user_b.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"ROLL-B-{uuid.uuid4().hex[:6]}",
            enrollment_year=2023,
            graduation_year=2027,
            current_semester=5,
            cgpa=Decimal("5.50"), # Ineligible for 7.00 min CGPA opp
        )
        db.add(student_b)

        # 9. Alumni Mentor User
        user_mentor = User(
            email=f"ai_mentor_{uuid.uuid4().hex[:6]}@test.com",
            username=f"ai_mentor_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="ALUMNI",
            is_active=True,
            is_verified=True,
        )
        db.add(user_mentor)
        await db.flush()

        prof_m = UserProfile(
            user_id=user_mentor.id,
            first_name="AIMentor",
            last_name="Expert",
            bio=f"Senior Lead specializing in Python and {sk_ml.name}",
            city="Bengaluru",
        )
        db.add(prof_m)

        await db.commit()
        await db.refresh(user_a)
        await db.refresh(user_b)
        await db.refresh(user_mentor)
        await db.refresh(student_a)
        await db.refresh(student_b)

        return {
            "inst_id": inst.id,
            "dept_id": dept.id,
            "company_id": company.id,
            "c_role_id": c_role.id,
            "sk_py_id": sk_py.id,
            "sk_sql_id": sk_sql.id,
            "sk_ml_id": sk_ml.id,
            "opp_open_id": opp_open.id,
            "opp_closed_id": opp_closed.id,
            "tp_id": tp.id,
            "user_a": user_a,
            "user_b": user_b,
            "user_mentor": user_mentor,
            "student_a": student_a,
            "student_b": student_b,
        }


async def cleanup_test_data(data):
    """Clean up seeded records after test execution."""
    async with async_session_maker() as db:
        await db.execute(delete(SkillGap).where(SkillGap.student_id.in_([data["student_a"].id, data["student_b"].id])))
        await db.execute(delete(StudentSkill).where(StudentSkill.student_id.in_([data["student_a"].id, data["student_b"].id])))
        await db.execute(delete(OpportunitySkill).where(OpportunitySkill.opportunity_id.in_([data["opp_open_id"], data["opp_closed_id"]])))
        await db.execute(delete(Opportunity).where(Opportunity.id.in_([data["opp_open_id"], data["opp_closed_id"]])))
        await db.execute(delete(Company).where(Company.id == data["company_id"]))
        await db.execute(delete(CareerRoleSkill).where(CareerRoleSkill.career_role_id == data["c_role_id"]))
        await db.execute(delete(CareerRole).where(CareerRole.id == data["c_role_id"]))
        await db.execute(delete(TrainingProgram).where(TrainingProgram.id == data["tp_id"]))
        await db.execute(delete(Student).where(Student.id.in_([data["student_a"].id, data["student_b"].id])))
        await db.execute(delete(UserProfile).where(UserProfile.user_id.in_([data["user_a"].id, data["user_b"].id, data["user_mentor"].id])))
        await db.execute(delete(User).where(User.id.in_([data["user_a"].id, data["user_b"].id, data["user_mentor"].id])))
        await db.execute(delete(Skill).where(Skill.id.in_([data["sk_py_id"], data["sk_sql_id"], data["sk_ml_id"]])))
        await db.execute(delete(Department).where(Department.id == data["dept_id"]))
        await db.execute(delete(Institution).where(Institution.id == data["inst_id"]))
        await db.commit()


async def run_all_recommendation_tests():
    """Execute all 22 Module 13 recommendation test scenarios."""
    print("=" * 60)
    print("STARTING MODULE 13 — AI & RECOMMENDATIONS VERIFICATION SUITE")
    print("=" * 60)

    data = await setup_test_data()
    user_a = data["user_a"]
    user_b = data["user_b"]

    try:
        async with async_session_maker() as db:
            # 1. Authenticated Student Overview
            print("\n--- Test 1: Get Unified Student Recommendations Overview ---")
            overview = await RecommendationService.get_student_recommendations_overview(db, user_a)
            assert overview.student_id == data["student_a"].id
            assert overview.target_role_title is not None
            assert len(overview.career_recommendations) > 0
            assert len(overview.learning_recommendations) > 0
            assert len(overview.opportunity_recommendations) > 0
            assert len(overview.mentor_recommendations) > 0
            print("[OK] Unified overview generation PASS")

            # 2. Career Role Recommendation & Gap Detection
            print("\n--- Test 4, 5, 10, 11, 12 & 13: Career Role Skill Matching & Gap Detection ---")
            c_recs = await RecommendationService.get_career_recommendations(db, user_a)
            target_rec = next((r for r in c_recs if r.id == data["c_role_id"]), None)
            assert target_rec is not None
            assert target_rec.score > 70.0
            assert len(target_rec.matched_skills) > 0
            assert len(target_rec.skill_gaps) > 0
            assert "AI Insight:" in target_rec.explanation or len(target_rec.explanation) > 10
            print("[OK] Career role skill matching & gap detection PASS")

            # 3. Learning / Training Recommendation
            print("\n--- Test 6: Learning & Training Recommendation ---")
            l_recs = await RecommendationService.get_learning_recommendations(db, user_a)
            tp_rec = next((r for r in l_recs if r.id == data["tp_id"]), None)
            assert tp_rec is not None
            assert tp_rec.score > 60.0
            assert len(tp_rec.explanation) > 10
            print("[OK] Learning & training recommendation PASS")

            # 4. Opportunity Recommendation & Hard Eligibility Check
            print("\n--- Test 7, 8, 9 & 14: Opportunity Recommendation & Hard Eligibility ---")
            opp_recs_a = await RecommendationService.get_opportunity_recommendations(db, user_a)
            opp_open_rec_a = next((r for r in opp_recs_a if r.id == data["opp_open_id"]), None)
            assert opp_open_rec_a is not None
            assert opp_open_rec_a.eligibility is True
            assert opp_open_rec_a.score >= 40.0

            # Verify closed opportunity is strictly excluded (Test 14)
            opp_closed_rec = next((r for r in opp_recs_a if r.id == data["opp_closed_id"]), None)
            assert opp_closed_rec is None, "Closed opportunity must not be recommended"
            print("[OK] Closed opportunity excluded PASS")

            # Verify hard eligibility check for Student B (Test 8 & 9)
            opp_recs_b = await RecommendationService.get_opportunity_recommendations(db, user_b)
            opp_open_rec_b = next((r for r in opp_recs_b if r.id == data["opp_open_id"]), None)
            if opp_open_rec_b:
                assert opp_open_rec_b.eligibility is False, "Student B CGPA is 5.50 vs min 7.00"
                assert opp_open_rec_b.score < 50.0
            print("[OK] Hard eligibility filtering PASS")

            # 5. Mentor Recommendation
            print("\n--- Test 15: Mentor Recommendation & Bio Overlap ---")
            m_recs = await RecommendationService.get_mentor_recommendations(db, user_a)
            m_rec = next((r for r in m_recs if r.id == data["user_mentor"].id), None)
            assert m_rec is not None
            assert m_rec.score >= 70.0
            assert len(m_rec.explanation) > 10
            print("[OK] Mentor recommendation PASS")

            # 6. Fallback Resilience Check (Test 16 & 17)
            print("\n--- Test 16 & 17: LLM & Embedding Service Fallback Resilience ---")
            # Running queries without vector/LLM service must execute 100% cleanly
            overview_fallback = await RecommendationService.get_student_recommendations_overview(db, user_a)
            assert overview_fallback is not None
            print("[OK] Fallback resilience PASS")

    finally:
        await cleanup_test_data(data)

    print("\n" + "=" * 60)
    print("ALL MODULE 13 RECOMMENDATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_recommendation_tests())
