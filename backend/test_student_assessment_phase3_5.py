"""
SKILLY MODULE 03 (STUDENT) — PHASE 3.5 AUTOMATED TEST SUITE
Student Skill Assessment & Diagnostic Benchmarking

Comprehensive 28-Point Verification Suite:
1. Assessment catalog listing (GET /api/v1/student/assessments).
2. Assessment detail retrieval (GET /api/v1/student/assessments/{id}).
3. Start assessment attempt session (POST /api/v1/student/assessments/{id}/start).
4. Attempt question retrieval without correct_answer leakage.
5. Correct answer evaluation & percentage calculation.
6. Passing attempt (percentage >= passing_score) sets is_passed=True.
7. Failing attempt sets is_passed=False.
8. student_skills record created/updated with verification_status="ASSESSED".
9. skill_evidence record created with evidence_type="ASSESSMENT".
10. skill_gaps recomputed after passing assessment.
11. Matching roadmap_items auto-completed upon passing.
12. Attempt completion timestamp (completed_at) set correctly.
13. Completed attempt immutability (subsequent submissions rejected with 400 Bad Request).
14. Assessment history retrieval (GET /api/v1/student/assessment-history).
15. IDOR protection: Student A cannot access Student B's attempt session (404/403).
16. TEACHER role blocked (403 Forbidden).
17. COLLEGE_ADMIN role blocked (403 Forbidden).
18. INDUSTRY role blocked (403 Forbidden).
19. ALUMNI role blocked (403 Forbidden).
20. Inactive account token blocked (401 Unauthorized).
21. Invalid assessment UUID rejected (404 Not Found).
22. Invalid attempt UUID rejected (404 Not Found).
23. EXPERT proficiency threshold (>= 90%).
24. ADVANCED proficiency threshold (>= 75%).
25. INTERMEDIATE proficiency threshold (>= 60%).
26. BEGINNER proficiency threshold (< 60%).
27. Phase 3.4 Roadmap & Learning regression.
28. Phase 3.3/3.2/3.1/Auth regressions.
"""

import sys
import os
import uuid
import asyncio
from decimal import Decimal
from typing import List

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.core.database import async_session_maker
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.careers import CareerRole, CareerRoleSkill, Roadmap, RoadmapItem, SkillGap
from app.models.skills import Skill, StudentSkill, SkillEvidence
from app.models.assessments import Assessment, AssessmentQuestion, AssessmentAttempt
from app.core.security import hash_password, create_access_token


async def cleanup_test_records(
    user_ids: List[uuid.UUID],
    assessment_ids: List[uuid.UUID],
    role_ids: List[uuid.UUID],
    skill_ids: List[uuid.UUID],
    dept_ids: List[uuid.UUID],
    inst_ids: List[uuid.UUID],
):
    """Safely cleans up records created specifically by the Phase 3.5 test suite."""
    async with async_session_maker() as db:
        try:
            # 1. Delete assessment attempts & questions
            if assessment_ids:
                await db.execute(delete(AssessmentAttempt).where(AssessmentAttempt.assessment_id.in_(assessment_ids)))
                await db.execute(delete(AssessmentQuestion).where(AssessmentQuestion.assessment_id.in_(assessment_ids)))
                await db.execute(delete(Assessment).where(Assessment.id.in_(assessment_ids)))

            # 2. Delete student records, evidence, skills, gaps, roadmaps
            if user_ids:
                st_res = await db.execute(select(Student.id).where(Student.user_id.in_(user_ids)))
                st_ids = list(st_res.scalars().all())
                
                if st_ids:
                    # Delete attempts for students
                    await db.execute(delete(AssessmentAttempt).where(AssessmentAttempt.student_id.in_(st_ids)))
                    
                    # Delete skill evidence
                    ss_res = await db.execute(select(StudentSkill.id).where(StudentSkill.student_id.in_(st_ids)))
                    ss_ids = list(ss_res.scalars().all())
                    if ss_ids:
                        await db.execute(delete(SkillEvidence).where(SkillEvidence.student_skill_id.in_(ss_ids)))
                        await db.execute(delete(StudentSkill).where(StudentSkill.id.in_(ss_ids)))

                    # Delete skill gaps
                    await db.execute(delete(SkillGap).where(SkillGap.student_id.in_(st_ids)))

                    # Delete roadmaps & items
                    rm_res = await db.execute(select(Roadmap.id).where(Roadmap.student_id.in_(st_ids)))
                    rm_ids = list(rm_res.scalars().all())
                    if rm_ids:
                        await db.execute(delete(RoadmapItem).where(RoadmapItem.roadmap_id.in_(rm_ids)))
                        await db.execute(delete(Roadmap).where(Roadmap.id.in_(rm_ids)))

                    await db.execute(delete(Student).where(Student.user_id.in_(user_ids)))

                await db.execute(delete(UserProfile).where(UserProfile.user_id.in_(user_ids)))
                await db.execute(delete(User).where(User.id.in_(user_ids)))

            # 3. Delete career roles & skills
            if role_ids:
                await db.execute(delete(CareerRoleSkill).where(CareerRoleSkill.career_role_id.in_(role_ids)))
                await db.execute(delete(SkillGap).where(SkillGap.career_role_id.in_(role_ids)))
                await db.execute(delete(Roadmap).where(Roadmap.career_role_id.in_(role_ids)))
                await db.execute(delete(CareerRole).where(CareerRole.id.in_(role_ids)))

            if skill_ids:
                await db.execute(delete(Skill).where(Skill.id.in_(skill_ids)))

            if dept_ids:
                await db.execute(delete(Department).where(Department.id.in_(dept_ids)))

            if inst_ids:
                await db.execute(delete(Institution).where(Institution.id.in_(inst_ids)))

            await db.commit()
            print("Successfully cleaned up Phase 3.5 test records.")
        except Exception as exc:
            await db.rollback()
            print(f"Cleanup error (non-fatal): {exc}")


async def run_phase_3_5_tests():
    print("=" * 80)
    print("STARTING SKILLY MODULE 03 — PHASE 3.5 AUTOMATED VERIFICATION SUITE")
    print("=" * 80)

    test_user_ids: List[uuid.UUID] = []
    test_assessment_ids: List[uuid.UUID] = []
    test_role_ids: List[uuid.UUID] = []
    test_skill_ids: List[uuid.UUID] = []
    test_dept_ids: List[uuid.UUID] = []
    test_inst_ids: List[uuid.UUID] = []

    passed_tests = 0
    total_tests = 28

    async with async_session_maker() as db:
        # 1. Setup Test Institution & Department
        inst = Institution(
            name="Test Assessment Inst " + uuid.uuid4().hex[:6],
            code="TAI-" + uuid.uuid4().hex[:4].upper(),
            city="Pune",
            state="Maharashtra",
            country="India",
        )
        db.add(inst)
        await db.flush()
        test_inst_ids.append(inst.id)

        dept = Department(
            institution_id=inst.id,
            name="Computer Engineering " + uuid.uuid4().hex[:4],
            code="CE-" + uuid.uuid4().hex[:4].upper(),
        )
        db.add(dept)
        await db.flush()
        test_dept_ids.append(dept.id)

        # 2. Setup Test Master Skill & Career Role
        skill = Skill(
            name="Test Python Mastery " + uuid.uuid4().hex[:6],
            slug="test-python-mastery-" + uuid.uuid4().hex[:6],
            category="Programming",
            description="Python diagnostic testing skill",
            is_verified=True,
        )
        db.add(skill)
        await db.flush()
        test_skill_ids.append(skill.id)

        role = CareerRole(
            title="Test Backend Engineer " + uuid.uuid4().hex[:6],
            slug="test-backend-engineer-" + uuid.uuid4().hex[:6],
            industry_domain="Software Engineering",
            description="Target career role for assessment benchmarking",
            is_active=True,
        )
        db.add(role)
        await db.flush()
        test_role_ids.append(role.id)

        crs = CareerRoleSkill(
            career_role_id=role.id,
            skill_id=skill.id,
            required_level="INTERMEDIATE",
            importance_level="CORE",
        )
        db.add(crs)
        await db.flush()

        # 3. Setup Test Users
        pwd_hash = hash_password("Password123!")
        u_student_a = User(
            email=f"ast_a_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"ast_a_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="STUDENT",
            is_active=True,
        )
        u_student_b = User(
            email=f"ast_b_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"ast_b_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="STUDENT",
            is_active=True,
        )
        u_teacher = User(
            email=f"ateacher_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"atchr_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="TEACHER",
            is_active=True,
        )
        u_admin = User(
            email=f"aadmin_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"aadm_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="COLLEGE_ADMIN",
            is_active=True,
        )
        u_industry = User(
            email=f"aindustry_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"aind_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="INDUSTRY",
            is_active=True,
        )
        u_alumni = User(
            email=f"aalumni_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"aalm_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="ALUMNI",
            is_active=True,
        )
        u_inactive = User(
            email=f"ainactive_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"ainact_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="STUDENT",
            is_active=False,
        )
        db.add_all([u_student_a, u_student_b, u_teacher, u_admin, u_industry, u_alumni, u_inactive])
        await db.flush()

        test_user_ids.extend([
            u_student_a.id, u_student_b.id, u_teacher.id, u_admin.id,
            u_industry.id, u_alumni.id, u_inactive.id
        ])

        # Setup Profiles & Student Entities
        prof_a = UserProfile(user_id=u_student_a.id, first_name="Student", last_name="Alpha")
        prof_b = UserProfile(user_id=u_student_b.id, first_name="Student", last_name="Beta")
        db.add_all([prof_a, prof_b])

        st_a = Student(
            user_id=u_student_a.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number="AST-101",
            enrollment_year=2023,
            graduation_year=2027,
            current_semester=5,
            target_career_role_id=role.id,
        )
        st_b = Student(
            user_id=u_student_b.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number="AST-102",
            enrollment_year=2023,
            graduation_year=2027,
            current_semester=5,
            target_career_role_id=role.id,
        )
        db.add_all([st_a, st_b])
        await db.flush()

        # Create Roadmap for Student A
        roadmap_a = Roadmap(
            student_id=st_a.id,
            career_role_id=role.id,
            title=f"Career Roadmap: {role.title}",
            status="ACTIVE",
        )
        db.add(roadmap_a)
        await db.flush()

        rm_item = RoadmapItem(
            roadmap_id=roadmap_a.id,
            skill_id=skill.id,
            step_order=1,
            title=f"Master {skill.name}",
            description="Attain INTERMEDIATE proficiency",
            status="PENDING",
        )
        db.add(rm_item)

        # Create SkillGap for Student A
        gap_a = SkillGap(
            student_id=st_a.id,
            career_role_id=role.id,
            skill_id=skill.id,
            current_level="NONE",
            target_level="INTERMEDIATE",
            gap_score=Decimal("2.00"),
        )
        db.add(gap_a)

        # 4. Setup Test Assessment & Questions
        ass = Assessment(
            title="Python Fundamentals Diagnostic " + uuid.uuid4().hex[:6],
            target_skill_id=skill.id,
            assessment_type="MCQ",
            total_questions=2,
            duration_minutes=15,
            passing_score=Decimal("60.00"),
            created_by_user_id=u_teacher.id,
            is_active=True,
        )
        db.add(ass)
        await db.flush()
        test_assessment_ids.append(ass.id)

        q1 = AssessmentQuestion(
            assessment_id=ass.id,
            question_text="What is the output of print(2 ** 3)?",
            question_type="MCQ",
            options=[
                {"id": "A", "text": "6"},
                {"id": "B", "text": "8"},
                {"id": "C", "text": "9"},
            ],
            correct_answer="B",
            points=1,
            question_order=1,
        )
        q2 = AssessmentQuestion(
            assessment_id=ass.id,
            question_text="Which keyword is used to define a function in Python?",
            question_type="MCQ",
            options=[
                {"id": "A", "text": "func"},
                {"id": "B", "text": "define"},
                {"id": "C", "text": "def"},
            ],
            correct_answer="C",
            points=1,
            question_order=2,
        )
        db.add_all([q1, q2])
        await db.commit()

        # Tokens
        token_a = create_access_token(subject=u_student_a.id, role="STUDENT")
        token_b = create_access_token(subject=u_student_b.id, role="STUDENT")
        token_teacher = create_access_token(subject=u_teacher.id, role="TEACHER")
        token_admin = create_access_token(subject=u_admin.id, role="COLLEGE_ADMIN")
        token_industry = create_access_token(subject=u_industry.id, role="INDUSTRY")
        token_alumni = create_access_token(subject=u_alumni.id, role="ALUMNI")
        token_inactive = create_access_token(subject=u_inactive.id, role="STUDENT")

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

    # Execute HTTP Async Verification
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            # -----------------------------------------------------------------
            # TEST 1: Assessment catalog listing (GET /api/v1/student/assessments)
            # -----------------------------------------------------------------
            res1 = await client.get("/api/v1/student/assessments", headers=headers_a)
            assert res1.status_code == 200, f"Test 1 failed status {res1.status_code}: {res1.text}"
            data1 = res1.json()
            ass_ids = [item["id"] for item in data1]
            assert str(ass.id) in ass_ids
            passed_tests += 1
            print("[PASS] TEST 1: Active assessments catalog loaded successfully.")

            # -----------------------------------------------------------------
            # TEST 2: Assessment detail retrieval (GET /api/v1/student/assessments/{id})
            # -----------------------------------------------------------------
            res2 = await client.get(f"/api/v1/student/assessments/{ass.id}", headers=headers_a)
            assert res2.status_code == 200, f"Test 2 failed status {res2.status_code}: {res2.text}"
            data2 = res2.json()
            assert data2["id"] == str(ass.id)
            assert data2["total_questions"] == 2
            assert float(data2["passing_score"]) == 60.0
            passed_tests += 1
            print("[PASS] TEST 2: Assessment detail and instructions loaded successfully.")

            # -----------------------------------------------------------------
            # TEST 3: Start assessment attempt session (POST /api/v1/student/assessments/{id}/start)
            # -----------------------------------------------------------------
            res3 = await client.post(f"/api/v1/student/assessments/{ass.id}/start", headers=headers_a)
            assert res3.status_code == 201, f"Test 3 failed status {res3.status_code}: {res3.text}"
            data3 = res3.json()
            attempt_a_id = data3["id"]
            assert data3["student_id"] == str(st_a.id)
            assert data3["assessment_id"] == str(ass.id)
            passed_tests += 1
            print("[PASS] TEST 3: Assessment attempt session initialized.")

            # -----------------------------------------------------------------
            # TEST 4: Attempt question retrieval without correct_answer leakage
            # -----------------------------------------------------------------
            questions_received = data3["questions"]
            assert len(questions_received) == 2
            for q in questions_received:
                assert "correct_answer" not in q, "SECURITY FAILURE: correct_answer exposed in public schema!"
            passed_tests += 1
            print("[PASS] TEST 4: Question list retrieved strictly WITHOUT correct_answer leakage.")

            # -----------------------------------------------------------------
            # TEST 5 & 6: Correct answer evaluation & percentage calculation (Passing attempt)
            # -----------------------------------------------------------------
            res_sub = await client.post(
                f"/api/v1/student/assessment-attempts/{attempt_a_id}/submit",
                json={"responses": {str(q1.id): "B", str(q2.id): "C"}},  # Both correct = 100%
                headers=headers_a,
            )
            assert res_sub.status_code == 200, f"Test 5/6 failed status {res_sub.status_code}: {res_sub.text}"
            sub_data = res_sub.json()
            assert float(sub_data["score"]) == 2.0
            assert float(sub_data["percentage"]) == 100.0
            assert sub_data["is_passed"] is True
            passed_tests += 2
            print("[PASS] TEST 5 & 6: Answers graded deterministically (2/2 = 100%, is_passed=True).")

            # -----------------------------------------------------------------
            # TEST 7: Failing attempt sets is_passed=False
            # -----------------------------------------------------------------
            # Start a second attempt for student A to test failing score
            res_start_fail = await client.post(f"/api/v1/student/assessments/{ass.id}/start", headers=headers_a)
            attempt_fail_id = res_start_fail.json()["id"]

            res_sub_fail = await client.post(
                f"/api/v1/student/assessment-attempts/{attempt_fail_id}/submit",
                json={"responses": {str(q1.id): "A", str(q2.id): "A"}},  # Both wrong = 0%
                headers=headers_a,
            )
            assert res_sub_fail.status_code == 200
            fail_data = res_sub_fail.json()
            assert float(fail_data["percentage"]) == 0.0
            assert fail_data["is_passed"] is False
            passed_tests += 1
            print("[PASS] TEST 7: Failing attempt sets is_passed=False correctly.")

            # -----------------------------------------------------------------
            # TEST 8: student_skills record created/updated with verification_status="ASSESSED"
            # -----------------------------------------------------------------
            async with async_session_maker() as db_check:
                st_skill_res = await db_check.execute(
                    select(StudentSkill).where(
                        StudentSkill.student_id == st_a.id,
                        StudentSkill.skill_id == skill.id,
                    )
                )
                st_skill_obj = st_skill_res.scalar_one_or_none()
                assert st_skill_obj is not None
                assert st_skill_obj.verification_status == "ASSESSED"
                assert st_skill_obj.score == Decimal("0.00") or st_skill_obj.score == Decimal("100.00")
            passed_tests += 1
            print("[PASS] TEST 8: student_skills passport updated with verification_status='ASSESSED'.")

            # -----------------------------------------------------------------
            # TEST 9: skill_evidence record created with evidence_type="ASSESSMENT"
            # -----------------------------------------------------------------
            async with async_session_maker() as db_check:
                ev_res = await db_check.execute(
                    select(SkillEvidence).where(
                        SkillEvidence.reference_id == uuid.UUID(attempt_a_id)
                    )
                )
                ev_obj = ev_res.scalar_one_or_none()
                assert ev_obj is not None
                assert ev_obj.evidence_type == "ASSESSMENT"
            passed_tests += 1
            print("[PASS] TEST 9: skill_evidence record created with evidence_type='ASSESSMENT'.")

            # -----------------------------------------------------------------
            # TEST 10: skill_gaps recomputed after passing assessment
            # -----------------------------------------------------------------
            async with async_session_maker() as db_check:
                gap_res = await db_check.execute(
                    select(SkillGap).where(
                        SkillGap.student_id == st_a.id,
                        SkillGap.career_role_id == role.id,
                        SkillGap.skill_id == skill.id,
                    )
                )
                gap_obj = gap_res.scalar_one_or_none()
                assert gap_obj is not None
                assert gap_obj.gap_score == Decimal("0.00")
            passed_tests += 1
            print("[PASS] TEST 10: skill_gaps variance recomputed to 0.00 after passing assessment.")

            # -----------------------------------------------------------------
            # TEST 11: Matching roadmap_items auto-completed upon passing
            # -----------------------------------------------------------------
            async with async_session_maker() as db_check:
                item_res = await db_check.execute(
                    select(RoadmapItem).where(RoadmapItem.id == rm_item.id)
                )
                item_obj = item_res.scalar_one()
                assert item_obj.status == "COMPLETED"
                assert item_obj.completed_at is not None
            passed_tests += 1
            print("[PASS] TEST 11: Matching roadmap checkpoint item auto-completed upon passing.")

            # -----------------------------------------------------------------
            # TEST 12: Attempt completion timestamp (completed_at) set correctly
            # -----------------------------------------------------------------
            assert sub_data["completed_at"] is not None
            passed_tests += 1
            print("[PASS] TEST 12: Attempt completed_at timestamp set correctly.")

            # -----------------------------------------------------------------
            # TEST 13: Completed attempt immutability (re-submission rejected with 400 Bad Request)
            # -----------------------------------------------------------------
            res13 = await client.post(
                f"/api/v1/student/assessment-attempts/{attempt_a_id}/submit",
                json={"responses": {str(q1.id): "C"}},
                headers=headers_a,
            )
            assert res13.status_code == 400, f"Expected 400, got {res13.status_code}"
            assert "already been submitted" in res13.json()["detail"].lower()
            passed_tests += 1
            print("[PASS] TEST 13: Completed attempt immutability enforced (re-submission rejected).")

            # -----------------------------------------------------------------
            # TEST 14: Assessment history retrieval (GET /api/v1/student/assessment-history)
            # -----------------------------------------------------------------
            res14 = await client.get("/api/v1/student/assessment-history", headers=headers_a)
            assert res14.status_code == 200
            hist_data = res14.json()
            assert len(hist_data) >= 2
            passed_tests += 1
            print("[PASS] TEST 14: Completed assessment attempt history retrieved successfully.")

            # -----------------------------------------------------------------
            # TEST 15: IDOR protection: Student A cannot access Student B's attempt session
            # -----------------------------------------------------------------
            res_start_b = await client.post(f"/api/v1/student/assessments/{ass.id}/start", headers=headers_b)
            attempt_b_id = res_start_b.json()["id"]

            res15 = await client.get(f"/api/v1/student/assessment-attempts/{attempt_b_id}", headers=headers_a)
            assert res15.status_code in [403, 404], f"Expected 404/403, got {res15.status_code}"
            passed_tests += 1
            print("[PASS] TEST 15: IDOR protection enforced (Student A cannot access Student B's attempt).")

            # -----------------------------------------------------------------
            # TEST 18-21: Role-based access control (403 Forbidden for non-STUDENT roles)
            # -----------------------------------------------------------------
            for r_token, r_name in [
                (token_teacher, "TEACHER"),
                (token_admin, "COLLEGE_ADMIN"),
                (token_industry, "INDUSTRY"),
                (token_alumni, "ALUMNI"),
            ]:
                hdr = {"Authorization": f"Bearer {r_token}"}
                res_rb = await client.get("/api/v1/student/assessments", headers=hdr)
                assert res_rb.status_code == 403, f"{r_name} should be blocked with 403"
            passed_tests += 4
            print("[PASS] TEST 16-19: RBAC enforced (403 Forbidden for TEACHER, COLLEGE_ADMIN, INDUSTRY, ALUMNI).")

            # -----------------------------------------------------------------
            # TEST 22: Inactive account token blocked (401 Unauthorized)
            # -----------------------------------------------------------------
            hdr_inact = {"Authorization": f"Bearer {token_inactive}"}
            res22 = await client.get("/api/v1/student/assessments", headers=hdr_inact)
            assert res22.status_code == 401
            passed_tests += 1
            print("[PASS] TEST 20: Suspended/inactive account token blocked with 401 Unauthorized.")

            # -----------------------------------------------------------------
            # TEST 23 & 24: Invalid assessment & attempt UUIDs (404 Not Found)
            # -----------------------------------------------------------------
            fake_uuid = str(uuid.uuid4())
            res23 = await client.get(f"/api/v1/student/assessments/{fake_uuid}", headers=headers_a)
            assert res23.status_code == 404
            res24 = await client.get(f"/api/v1/student/assessment-attempts/{fake_uuid}", headers=headers_a)
            assert res24.status_code == 404
            passed_tests += 2
            print("[PASS] TEST 21 & 22: Invalid assessment and attempt UUIDs rejected with 404 Not Found.")

            # -----------------------------------------------------------------
            # TEST 23-26: Proficiency Level Thresholds (EXPERT, ADVANCED, INTERMEDIATE, BEGINNER)
            # -----------------------------------------------------------------
            from app.services.assessment_service import calculate_proficiency_level
            assert calculate_proficiency_level(Decimal("95.00")) == "EXPERT"
            assert calculate_proficiency_level(Decimal("80.00")) == "ADVANCED"
            assert calculate_proficiency_level(Decimal("65.00")) == "INTERMEDIATE"
            assert calculate_proficiency_level(Decimal("45.00")) == "BEGINNER"
            passed_tests += 4
            print("[PASS] TEST 23-26: Proficiency level thresholds verified (EXPERT, ADVANCED, INTERMEDIATE, BEGINNER).")

            # -----------------------------------------------------------------
            # TEST 27 & 28: Regressions (Phase 3.4 Roadmap & Phase 3.3 Workspace)
            # -----------------------------------------------------------------
            res27 = await client.get("/api/v1/student/roadmap", headers=headers_a)
            assert res27.status_code == 200
            res28 = await client.get("/api/v1/student/career-workspace", headers=headers_a)
            assert res28.status_code == 200
            passed_tests += 2
            print("[PASS] TEST 27 & 28: Regressions passed (Phase 3.4 Roadmap & Phase 3.3 Workspace).")

        finally:
            # Mandatory Cleanup
            await cleanup_test_records(
                user_ids=test_user_ids,
                assessment_ids=test_assessment_ids,
                role_ids=test_role_ids,
                skill_ids=test_skill_ids,
                dept_ids=test_dept_ids,
                inst_ids=test_inst_ids,
            )

    print("=" * 80)
    print(f"PHASE 3.5 VERIFICATION COMPLETE: {passed_tests}/{total_tests} TESTS PASSED.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_phase_3_5_tests())
