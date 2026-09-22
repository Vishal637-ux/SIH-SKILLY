import asyncio
import uuid
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.main import app
from app.core.database import async_session_maker
from app.core.security import hash_password, create_access_token
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.skills import Skill, StudentSkill, SkillEvidence, SkillRelationship
from app.models.careers import CareerRole, CareerRoleSkill, SkillGap, Roadmap, RoadmapItem
from app.models.assessments import Assessment, AssessmentQuestion, AssessmentAttempt
from app.services.skill_service import check_prerequisite_cycle, calculate_student_skill_gaps


async def run_skill_assessment_module_tests():
    print("================================================================================")
    print("STARTING MODULE 08 — SKILL & ASSESSMENT ENGINE AUTOMATED TEST SUITE")
    print("================================================================================")

    async with async_session_maker() as db:
        prefix = f"test_a8_{uuid.uuid4().hex[:6]}"

        # 1. Setup Test Fixtures
        # Student A
        u_student_a = User(
            email=f"student_a_{prefix}@test.com",
            username=f"student_a_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="STUDENT",
            is_active=True,
        )
        db.add(u_student_a)

        # Student B (For IDOR isolation testing)
        u_student_b = User(
            email=f"student_b_{prefix}@test.com",
            username=f"student_b_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="STUDENT",
            is_active=True,
        )
        db.add(u_student_b)

        # Non-STUDENT user (Teacher)
        u_teacher = User(
            email=f"teacher_{prefix}@test.com",
            username=f"teacher_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="TEACHER",
            is_active=True,
        )
        db.add(u_teacher)

        await db.flush()

        # Profiles
        db.add(UserProfile(user_id=u_student_a.id, first_name="Alice", last_name="Student", city="Mumbai", state="MH"))
        db.add(UserProfile(user_id=u_student_b.id, first_name="Bob", last_name="Student", city="Pune", state="MH"))

        # Institution, Department
        inst = Institution(name=f"{prefix} Tech Inst", code=f"INST_{prefix}", institution_type="COLLEGE", city="Mumbai", state="MH")
        db.add(inst)
        await db.flush()

        dept = Department(institution_id=inst.id, name="Computer Science", code=f"CS_{prefix}")
        db.add(dept)
        await db.flush()

        # Master Skills
        skill_python = Skill(name=f"Python Programming_{prefix}", slug=f"python-{prefix}", category="Programming", description="Core Python")
        skill_fastapi = Skill(name=f"FastAPI Web_{prefix}", slug=f"fastapi-{prefix}", category="Backend", description="FastAPI Framework")
        skill_docker = Skill(name=f"Docker Containers_{prefix}", slug=f"docker-{prefix}", category="DevOps", description="Docker Containerization")
        db.add_all([skill_python, skill_fastapi, skill_docker])
        await db.flush()

        # Skill Relationship: Python is prerequisite to FastAPI
        rel_prereq = SkillRelationship(
            parent_skill_id=skill_python.id,
            child_skill_id=skill_fastapi.id,
            relationship_type="PREREQUISITE",
        )
        db.add(rel_prereq)

        # Career Role: Backend Engineer
        role_backend = CareerRole(
            title=f"Backend Engineer_{prefix}",
            slug=f"backend-engineer-{prefix}",
            industry_domain="Software Engineering",
            description="Backend Engineering Role",
        )
        db.add(role_backend)
        await db.flush()

        # Career Role Skill requirements:
        # Python = ADVANCED (Rank 3)
        # FastAPI = INTERMEDIATE (Rank 2)
        # Docker = BEGINNER (Rank 1)
        cr_skill_py = CareerRoleSkill(career_role_id=role_backend.id, skill_id=skill_python.id, required_level="ADVANCED", importance_level="CORE")
        cr_skill_fa = CareerRoleSkill(career_role_id=role_backend.id, skill_id=skill_fastapi.id, required_level="INTERMEDIATE", importance_level="CORE")
        cr_skill_dk = CareerRoleSkill(career_role_id=role_backend.id, skill_id=skill_docker.id, required_level="BEGINNER", importance_level="RECOMMENDED")
        db.add_all([cr_skill_py, cr_skill_fa, cr_skill_dk])

        # Student A record
        student_a_entity = Student(
            user_id=u_student_a.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"ROLL_A_{prefix}",
            enrollment_year=2022,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("9.20"),
            target_career_role_id=role_backend.id,
        )
        db.add(student_a_entity)

        # Student B record
        student_b_entity = Student(
            user_id=u_student_b.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"ROLL_B_{prefix}",
            enrollment_year=2022,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("8.50"),
            target_career_role_id=role_backend.id,
        )
        db.add(student_b_entity)
        await db.flush()

        # Pre-assign Student A Python skill as BEGINNER (Level 1 vs Required ADVANCED Level 3 -> INSUFFICIENT)
        st_skill_py_a = StudentSkill(
            student_id=student_a_entity.id,
            skill_id=skill_python.id,
            proficiency_level="BEGINNER",
            verification_status="SELF_REPORTED",
            score=Decimal("40.00"),
        )
        db.add(st_skill_py_a)

        # Assessment entity on Python
        ass_py = Assessment(
            title=f"Python Advanced Diagnostic_{prefix}",
            assessment_type="QUIZ",
            target_skill_id=skill_python.id,
            created_by_user_id=u_teacher.id,
            total_questions=2,
            duration_minutes=20,
            passing_score=Decimal("70.00"),
            is_active=True,
        )
        db.add(ass_py)
        await db.flush()

        # Questions for Assessment
        q1 = AssessmentQuestion(
            assessment_id=ass_py.id,
            question_text="What is a list comprehension in Python?",
            question_type="SINGLE_CHOICE",
            options=["Syntactic construct to create lists", "Database table", "Variable type", "File format"],
            correct_answer="Syntactic construct to create lists",
            points=1,
            question_order=1,
        )
        q2 = AssessmentQuestion(
            assessment_id=ass_py.id,
            question_text="Which decorator is used to define an async function in Python?",
            question_type="SINGLE_CHOICE",
            options=["async def", "@async", "def async", "thread"],
            correct_answer="async def",
            points=1,
            question_order=2,
        )
        db.add_all([q1, q2])
        await db.commit()

        # Tokens
        token_a = create_access_token(subject=u_student_a.id, role="STUDENT")
        token_b = create_access_token(subject=u_student_b.id, role="STUDENT")
        token_teacher = create_access_token(subject=u_teacher.id, role="TEACHER")

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        # ----------------------------------------------------------------------
        # TEST 1: Unauthenticated Assessment Access -> 401
        # ----------------------------------------------------------------------
        print("\n[TEST 1] Unauthenticated GET /api/v1/student/assessments -> 401")
        res = await ac.get("/api/v1/student/assessments")
        assert res.status_code == 401
        print(" -> PASSED: 401 Unauthorized")

        # ----------------------------------------------------------------------
        # TEST 2: Non-STUDENT Role Rejection -> 403
        # ----------------------------------------------------------------------
        print("\n[TEST 2] Non-STUDENT role (TEACHER) access to student assessment API -> 403")
        res = await ac.get("/api/v1/student/assessments", headers={"Authorization": f"Bearer {token_teacher}"})
        assert res.status_code == 403
        print(" -> PASSED: Non-STUDENT role rejected with 403")

        # ----------------------------------------------------------------------
        # TEST 3: Skill Taxonomy API Listing & Detail
        # ----------------------------------------------------------------------
        print("\n[TEST 3] GET /api/v1/skills catalog & detail")
        res_skills = await ac.get("/api/v1/skills", headers=headers_a)
        assert res_skills.status_code == 200
        skills_data = res_skills.json()
        assert len(skills_data) >= 3

        res_skill_detail = await ac.get(f"/api/v1/skills/{skill_fastapi.id}", headers=headers_a)
        assert res_skill_detail.status_code == 200
        detail_data = res_skill_detail.json()
        assert len(detail_data["prerequisites"]) == 1
        assert detail_data["prerequisites"][0]["id"] == str(skill_python.id)
        print(" -> PASSED: Master skills taxonomy and prerequisite graph retrieved")

        # ----------------------------------------------------------------------
        # TEST 4: Prerequisite Cycle Detection Check
        # ----------------------------------------------------------------------
        print("\n[TEST 4] Prerequisite Cycle Detection (Python -> FastAPI -> Python)")
        async with async_session_maker() as cycle_db:
            has_cycle = await check_prerequisite_cycle(cycle_db, parent_skill_id=skill_fastapi.id, child_skill_id=skill_python.id)
            assert has_cycle is True, "Cycle should be detected if adding edge FastAPI -> Python"
        print(" -> PASSED: Cycle detection logic accurately flagged invalid circular prerequisite")

        # ----------------------------------------------------------------------
        # TEST 5: Assessment Catalog & Detail Visibility
        # ----------------------------------------------------------------------
        print("\n[TEST 5] GET /api/v1/student/assessments & GET /api/v1/student/assessments/{id}")
        res_cat = await ac.get("/api/v1/student/assessments", headers=headers_a)
        assert res_cat.status_code == 200
        cat_items = res_cat.json()
        assert len(cat_items) >= 1

        res_ass_det = await ac.get(f"/api/v1/student/assessments/{ass_py.id}", headers=headers_a)
        assert res_ass_det.status_code == 200
        assert res_ass_det.json()["title"] == f"Python Advanced Diagnostic_{prefix}"
        print(" -> PASSED: Assessment metadata retrieved cleanly")

        # ----------------------------------------------------------------------
        # TEST 6: Start Assessment Attempt & Verify Answer Leak Prevention
        # ----------------------------------------------------------------------
        print("\n[TEST 6] POST /api/v1/student/assessments/{id}/start")
        res_start = await ac.post(f"/api/v1/student/assessments/{ass_py.id}/start", headers=headers_a)
        assert res_start.status_code == 201
        attempt_a_data = res_start.json()
        attempt_a_id = attempt_a_data["id"]

        # Ensure correct_answer is NOT leaked in questions list
        for q in attempt_a_data["questions"]:
            assert "correct_answer" not in q or q.get("correct_answer") is None, "Correct answer must NOT be exposed before submission!"
            assert "explanation" not in q or q.get("explanation") is None, "Explanation must NOT be exposed before submission!"
        print(f" -> PASSED: Attempt initialized (ID: {attempt_a_id}). Answers strictly protected from leak.")

        # ----------------------------------------------------------------------
        # TEST 7: Cross-Student Attempt IDOR Rejection (404)
        # ----------------------------------------------------------------------
        print("\n[TEST 7] Student B GET /api/v1/student/assessment-attempts/{Student A attempt_id} -> 404")
        res_idor = await ac.get(f"/api/v1/student/assessment-attempts/{attempt_a_id}", headers=headers_b)
        assert res_idor.status_code == 404
        print(" -> PASSED: Cross-student attempt IDOR strictly blocked with 404")

        # ----------------------------------------------------------------------
        # TEST 8: Submit Assessment Attempt & Deterministic Evaluation
        # ----------------------------------------------------------------------
        print("\n[TEST 8] POST /api/v1/student/assessment-attempts/{id}/submit (100% Correct)")
        submit_payload = {
            "responses": {
                str(q1.id): "Syntactic construct to create lists",
                str(q2.id): "async def",
            }
        }
        res_sub = await ac.post(
            f"/api/v1/student/assessment-attempts/{attempt_a_id}/submit",
            json=submit_payload,
            headers=headers_a,
        )
        assert res_sub.status_code == 200
        result_data = res_sub.json()
        assert float(result_data["score"]) == 2.0
        assert float(result_data["percentage"]) == 100.0
        assert result_data["is_passed"] is True
        assert result_data["proficiency_level"] == "EXPERT"
        print(" -> PASSED: Attempt evaluated deterministically: Score 100%, Passed, Level EXPERT")

        # ----------------------------------------------------------------------
        # TEST 9: Completed Attempt Immutability
        # ----------------------------------------------------------------------
        print("\n[TEST 9] Re-submitting completed attempt -> 400 Bad Request")
        res_resub = await ac.post(
            f"/api/v1/student/assessment-attempts/{attempt_a_id}/submit",
            json=submit_payload,
            headers=headers_a,
        )
        assert res_resub.status_code == 400
        print(" -> PASSED: Completed attempt immutability enforced")

        # ----------------------------------------------------------------------
        # TEST 10: Verified Skill Evidence & Student Skill Update
        # ----------------------------------------------------------------------
        print("\n[TEST 10] Verify StudentSkill & SkillEvidence updated in database")
        async with async_session_maker() as verify_db:
            st_skill_stmt = (
                select(StudentSkill)
                .options(selectinload(StudentSkill.evidence))
                .where(
                    StudentSkill.student_id == student_a_entity.id,
                    StudentSkill.skill_id == skill_python.id,
                )
            )
            st_skill = (await verify_db.execute(st_skill_stmt)).scalar_one_or_none()
            assert st_skill is not None
            assert st_skill.proficiency_level == "EXPERT"
            assert st_skill.verification_status == "ASSESSED"
            assert st_skill.score == Decimal("100.00")
            assert len(st_skill.evidence) >= 1
            assert st_skill.evidence[0].evidence_type == "ASSESSMENT"
            assert st_skill.evidence[0].reference_id == uuid.UUID(attempt_a_id)
        print(" -> PASSED: StudentSkill updated to EXPERT with digital ASSESSMENT evidence")

        # ----------------------------------------------------------------------
        # TEST 11: GET /api/v1/student/skills Profile
        # ----------------------------------------------------------------------
        print("\n[TEST 11] GET /api/v1/student/skills (Student A skill passport)")
        res_st_skills = await ac.get("/api/v1/student/skills", headers=headers_a)
        assert res_st_skills.status_code == 200
        user_skills = res_st_skills.json()
        assert len(user_skills) >= 1
        assert user_skills[0]["proficiency_level"] == "EXPERT"
        print(" -> PASSED: Student skill profile returned with verified evidence ledger")

        # ----------------------------------------------------------------------
        # TEST 12: Skill Gap Calculation Engine
        # ----------------------------------------------------------------------
        print("\n[TEST 12] GET /api/v1/student/skill-gaps (Student A Gap Analysis)")
        res_gaps = await ac.get("/api/v1/student/skill-gaps", headers=headers_a)
        assert res_gaps.status_code == 200
        gaps_data = res_gaps.json()

        assert gaps_data["has_target_role"] is True
        summary = gaps_data["summary"]
        # Python: Required ADVANCED (3), Student EXPERT (4) -> SATISFIED
        # FastAPI: Required INTERMEDIATE (2), Student NONE (0) -> MISSING
        # Docker: Required BEGINNER (1), Student NONE (0) -> MISSING
        assert summary["satisfied_count"] == 1
        assert summary["missing_count"] == 2
        print(f" -> PASSED: Deterministic Skill Gap Analysis (Satisfied: {summary['satisfied_count']}, Missing: {summary['missing_count']})")

        # ----------------------------------------------------------------------
        # TEST 13: Student B Skill Gap Analysis (All Missing/Insufficient)
        # ----------------------------------------------------------------------
        print("\n[TEST 13] GET /api/v1/student/skill-gaps (Student B Baseline)")
        res_gaps_b = await ac.get("/api/v1/student/skill-gaps", headers=headers_b)
        assert res_gaps_b.status_code == 200
        gaps_data_b = res_gaps_b.json()
        assert gaps_data_b["summary"]["satisfied_count"] == 0
        assert gaps_data_b["summary"]["missing_count"] == 3
        print(" -> PASSED: Baseline student skill gaps correctly calculated (3/3 MISSING)")

        # ----------------------------------------------------------------------
        # TEST 14: Student Assessment History
        # ----------------------------------------------------------------------
        print("\n[TEST 14] GET /api/v1/student/assessment-history (Student A)")
        res_hist = await ac.get("/api/v1/student/assessment-history", headers=headers_a)
        assert res_hist.status_code == 200
        hist_items = res_hist.json()
        assert len(hist_items) >= 1
        assert hist_items[0]["attempt_id"] == attempt_a_id
        print(" -> PASSED: Completed attempt history logged")

    print("\n================================================================================")
    print("MODULE 08 AUTOMATED TEST SUITE PASSED SUCCESSFULLY (14/14 SCENARIOS)")
    print("================================================================================")


if __name__ == "__main__":
    asyncio.run(run_skill_assessment_module_tests())
