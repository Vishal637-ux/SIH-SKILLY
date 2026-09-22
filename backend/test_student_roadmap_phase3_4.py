"""
SKILLY MODULE 03 (STUDENT) — PHASE 3.4 AUTOMATED TEST SUITE
Student Career Roadmap & Learning Workspace

Comprehensive 28-Point Verification Suite:
1. Student without target role gets clean empty roadmap state.
2. Student with target role can generate roadmap.
3. Generated roadmap belongs to correct student.
4. Required skills become roadmap items.
5. CORE skills are ordered before RECOMMENDED skills.
6. Step order is sequential.
7. Roadmap progress calculation is correct.
8. PENDING -> IN_PROGRESS works.
9. IN_PROGRESS -> COMPLETED works.
10. completed_at behavior is correct.
11. GET /api/v1/student/roadmap returns persisted state.
12. Training catalog loads from real DB.
13. Student can enroll in valid training program.
14. Duplicate enrollment is rejected cleanly (400 Bad Request).
15. Student enrollment persists in My Learning.
16. Student A cannot access or update Student B's roadmap item (IDOR protection -> 404/403).
17. Student A cannot access Student B training enrollment data.
18. TEACHER role blocked on roadmap/learning endpoints (403 Forbidden).
19. COLLEGE_ADMIN role blocked on roadmap/learning endpoints (403 Forbidden).
20. INDUSTRY role blocked on roadmap/learning endpoints (403 Forbidden).
21. ALUMNI role blocked on roadmap/learning endpoints (403 Forbidden).
22. Inactive account token blocked (401 Unauthorized).
23. Invalid roadmap item UUID rejected cleanly (404 Not Found).
24. Invalid training program UUID rejected cleanly (404 Not Found).
25. Phase 3.3 regression: GET /api/v1/student/career-workspace.
26. Phase 3.2 regression: GET /api/v1/student/profile.
27. Phase 3.1 regression: GET /api/v1/student/dashboard.
28. Auth/RBAC regression: POST /api/v1/auth/login.
"""

import sys
import os
import uuid
import asyncio
from datetime import date
from typing import List

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.core.database import async_session_maker
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.careers import CareerRole, CareerRoleSkill, Roadmap, RoadmapItem
from app.models.skills import Skill, StudentSkill
from app.models.training import TrainingProgram, TrainingEnrollment
from app.core.security import hash_password, create_access_token


async def cleanup_test_records(
    user_ids: List[uuid.UUID],
    role_ids: List[uuid.UUID],
    skill_ids: List[uuid.UUID],
    dept_ids: List[uuid.UUID],
    inst_ids: List[uuid.UUID],
    program_ids: List[uuid.UUID],
):
    """Safely cleans up records created specifically by the Phase 3.4 test suite."""
    async with async_session_maker() as db:
        try:
            # 1. Delete training enrollments & training programs first (references users)
            if program_ids:
                await db.execute(delete(TrainingEnrollment).where(TrainingEnrollment.training_program_id.in_(program_ids)))
                await db.execute(delete(TrainingProgram).where(TrainingProgram.id.in_(program_ids)))

            if user_ids:
                st_res = await db.execute(select(Student.id).where(Student.user_id.in_(user_ids)))
                st_ids = list(st_res.scalars().all())
                
                if st_ids:
                    await db.execute(delete(TrainingEnrollment).where(TrainingEnrollment.student_id.in_(st_ids)))
                    
                    rm_res = await db.execute(select(Roadmap.id).where(Roadmap.student_id.in_(st_ids)))
                    rm_ids = list(rm_res.scalars().all())
                    if rm_ids:
                        await db.execute(delete(RoadmapItem).where(RoadmapItem.roadmap_id.in_(rm_ids)))
                        await db.execute(delete(Roadmap).where(Roadmap.id.in_(rm_ids)))
                    
                    await db.execute(delete(StudentSkill).where(StudentSkill.student_id.in_(st_ids)))
                    await db.execute(delete(Student).where(Student.user_id.in_(user_ids)))
                
                await db.execute(delete(UserProfile).where(UserProfile.user_id.in_(user_ids)))
                await db.execute(delete(User).where(User.id.in_(user_ids)))

            if role_ids:
                await db.execute(delete(CareerRoleSkill).where(CareerRoleSkill.career_role_id.in_(role_ids)))
                await db.execute(delete(CareerRole).where(CareerRole.id.in_(role_ids)))

            if skill_ids:
                await db.execute(delete(Skill).where(Skill.id.in_(skill_ids)))

            if dept_ids:
                await db.execute(delete(Department).where(Department.id.in_(dept_ids)))

            if inst_ids:
                await db.execute(delete(Institution).where(Institution.id.in_(inst_ids)))

            await db.commit()
            print("Successfully cleaned up Phase 3.4 test records.")
        except Exception as exc:
            await db.rollback()
            print(f"Cleanup error (non-fatal): {exc}")


async def run_phase_3_4_tests():
    print("=" * 80)
    print("STARTING SKILLY MODULE 03 — PHASE 3.4 AUTOMATED VERIFICATION SUITE")
    print("=" * 80)

    test_user_ids: List[uuid.UUID] = []
    test_role_ids: List[uuid.UUID] = []
    test_skill_ids: List[uuid.UUID] = []
    test_dept_ids: List[uuid.UUID] = []
    test_inst_ids: List[uuid.UUID] = []
    test_program_ids: List[uuid.UUID] = []

    passed_tests = 0
    total_tests = 28

    async with async_session_maker() as db:
        # 1. Setup Test Institution & Department
        inst = Institution(
            name="Test Roadmap Inst " + uuid.uuid4().hex[:6],
            code="TRM-" + uuid.uuid4().hex[:4].upper(),
            city="Pune",
            state="Maharashtra",
            country="India",
        )
        db.add(inst)
        await db.flush()
        test_inst_ids.append(inst.id)

        dept = Department(
            institution_id=inst.id,
            name="Computer Science " + uuid.uuid4().hex[:4],
            code="CS-" + uuid.uuid4().hex[:4].upper(),
        )
        db.add(dept)
        await db.flush()
        test_dept_ids.append(dept.id)

        # 2. Setup Test Master Skills
        skill_core = Skill(
            name="Test Core Skill " + uuid.uuid4().hex[:6],
            slug="test-core-skill-" + uuid.uuid4().hex[:6],
            category="Programming",
            description="Core test skill requirement",
            is_verified=True,
        )
        skill_rec = Skill(
            name="Test Rec Skill " + uuid.uuid4().hex[:6],
            slug="test-rec-skill-" + uuid.uuid4().hex[:6],
            category="DevOps",
            description="Recommended test skill requirement",
            is_verified=True,
        )
        db.add(skill_core)
        db.add(skill_rec)
        await db.flush()
        test_skill_ids.extend([skill_core.id, skill_rec.id])

        # 3. Setup Test Career Role & Required Skills
        role = CareerRole(
            title="Test Cloud Engineer " + uuid.uuid4().hex[:6],
            slug="test-cloud-engineer-" + uuid.uuid4().hex[:6],
            industry_domain="Cloud Architecture",
            description="Target role for roadmap verification",
            is_active=True,
        )
        db.add(role)
        await db.flush()
        test_role_ids.append(role.id)

        crs_core = CareerRoleSkill(
            career_role_id=role.id,
            skill_id=skill_core.id,
            required_level="INTERMEDIATE",
            importance_level="CORE",
        )
        crs_rec = CareerRoleSkill(
            career_role_id=role.id,
            skill_id=skill_rec.id,
            required_level="BEGINNER",
            importance_level="RECOMMENDED",
        )
        db.add(crs_core)
        db.add(crs_rec)

        # 4. Create Test Users & Tokens
        pwd_hash = hash_password("Password123!")
        u_student_a = User(
            email=f"student_a_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"st_a_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="STUDENT",
            is_active=True,
        )
        u_student_b = User(
            email=f"student_b_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"st_b_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="STUDENT",
            is_active=True,
        )
        u_teacher = User(
            email=f"teacher_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"tchr_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="TEACHER",
            is_active=True,
        )
        u_admin = User(
            email=f"admin_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"adm_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="COLLEGE_ADMIN",
            is_active=True,
        )
        u_industry = User(
            email=f"industry_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"ind_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="INDUSTRY",
            is_active=True,
        )
        u_alumni = User(
            email=f"alumni_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"alm_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="ALUMNI",
            is_active=True,
        )
        u_inactive = User(
            email=f"inactive_{uuid.uuid4().hex[:6]}@skillytest.org",
            username=f"inact_{uuid.uuid4().hex[:6]}",
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

        # Setup Test Training Program
        program = TrainingProgram(
            title="Test AWS Bootcamp " + uuid.uuid4().hex[:6],
            description="Hands-on cloud engineering workshop",
            program_type="BOOTCAMP",
            institution_id=inst.id,
            conducted_by_user_id=u_teacher.id,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 15),
            capacity=30,
            status="UPCOMING",
        )
        db.add(program)
        await db.flush()
        test_program_ids.append(program.id)

        # Profiles
        prof_a = UserProfile(user_id=u_student_a.id, first_name="Student", last_name="Alpha")
        prof_b = UserProfile(user_id=u_student_b.id, first_name="Student", last_name="Beta")
        db.add_all([prof_a, prof_b])

        # Students
        st_a = Student(
            user_id=u_student_a.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number="STA-101",
            enrollment_year=2023,
            graduation_year=2027,
            current_semester=5,
            target_career_role_id=None,
        )
        st_b = Student(
            user_id=u_student_b.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number="STB-102",
            enrollment_year=2023,
            graduation_year=2027,
            current_semester=5,
            target_career_role_id=role.id,
        )
        db.add_all([st_a, st_b])
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
            # TEST 1: Student without target role gets clean empty state
            # -----------------------------------------------------------------
            res1 = await client.get("/api/v1/student/roadmap", headers=headers_a)
            assert res1.status_code == 200, f"Test 1 failed status {res1.status_code}: {res1.text}"
            data1 = res1.json()
            assert data1["has_target_role"] is False
            assert data1["has_active_roadmap"] is False
            assert data1["roadmap"] is None
            passed_tests += 1
            print("[PASS] TEST 1: Student without target role returns clean empty state.")

            # Set target career role for Student A
            res_set = await client.put(
                "/api/v1/student/target-role",
                json={"career_role_id": str(role.id)},
                headers=headers_a,
            )
            assert res_set.status_code == 200

            # -----------------------------------------------------------------
            # TEST 2: Student with target role can generate roadmap
            # -----------------------------------------------------------------
            res2 = await client.post("/api/v1/student/roadmap/generate", headers=headers_a)
            assert res2.status_code == 200, f"Test 2 failed status {res2.status_code}: {res2.text}"
            data2 = res2.json()
            assert data2["has_target_role"] is True
            assert data2["has_active_roadmap"] is True
            assert data2["roadmap"] is not None
            passed_tests += 1
            print("[PASS] TEST 2: Roadmap generated successfully for student with target role.")

            roadmap_data = data2["roadmap"]
            items_data = roadmap_data["items"]

            # -----------------------------------------------------------------
            # TEST 3: Generated roadmap belongs to correct student
            # -----------------------------------------------------------------
            assert roadmap_data["student_id"] == str(st_a.id)
            passed_tests += 1
            print("[PASS] TEST 3: Generated roadmap belongs strictly to authenticated student.")

            # -----------------------------------------------------------------
            # TEST 4: Required skills become roadmap items
            # -----------------------------------------------------------------
            assert len(items_data) == 2, f"Expected 2 items, got {len(items_data)}"
            item_skill_ids = {item["skill_id"] for item in items_data}
            assert str(skill_core.id) in item_skill_ids
            assert str(skill_rec.id) in item_skill_ids
            passed_tests += 1
            print("[PASS] TEST 4: Target role required skills converted into roadmap checkpoint items.")

            # -----------------------------------------------------------------
            # TEST 5: CORE skills are ordered before RECOMMENDED skills
            # -----------------------------------------------------------------
            assert items_data[0]["skill_id"] == str(skill_core.id)
            assert items_data[1]["skill_id"] == str(skill_rec.id)
            passed_tests += 1
            print("[PASS] TEST 5: CORE skills ordered before RECOMMENDED skills in roadmap sequence.")

            # -----------------------------------------------------------------
            # TEST 6: Step order is sequential
            # -----------------------------------------------------------------
            assert items_data[0]["step_order"] == 1
            assert items_data[1]["step_order"] == 2
            passed_tests += 1
            print("[PASS] TEST 6: Step order assigned sequentially (1, 2).")

            # -----------------------------------------------------------------
            # TEST 7: Roadmap progress calculation is correct
            # -----------------------------------------------------------------
            assert data2["total_steps"] == 2
            assert data2["completed_steps"] == 0
            assert data2["completion_percentage"] == 0
            passed_tests += 1
            print("[PASS] TEST 7: Roadmap progress metrics computed accurately (0/2 = 0%).")

            item1_id = items_data[0]["id"]

            # -----------------------------------------------------------------
            # TEST 8: PENDING -> IN_PROGRESS works
            # -----------------------------------------------------------------
            res8 = await client.put(
                f"/api/v1/student/roadmap/items/{item1_id}",
                json={"status": "IN_PROGRESS"},
                headers=headers_a,
            )
            assert res8.status_code == 200, f"Test 8 failed status {res8.status_code}: {res8.text}"
            item8_data = res8.json()
            assert item8_data["status"] == "IN_PROGRESS"
            assert item8_data["completed_at"] is None
            passed_tests += 1
            print("[PASS] TEST 8: Transition PENDING -> IN_PROGRESS succeeds.")

            # -----------------------------------------------------------------
            # TEST 9: IN_PROGRESS -> COMPLETED works
            # -----------------------------------------------------------------
            res9 = await client.put(
                f"/api/v1/student/roadmap/items/{item1_id}",
                json={"status": "COMPLETED"},
                headers=headers_a,
            )
            assert res9.status_code == 200, f"Test 9 failed status {res9.status_code}: {res9.text}"
            item9_data = res9.json()
            assert item9_data["status"] == "COMPLETED"
            passed_tests += 1
            print("[PASS] TEST 9: Transition IN_PROGRESS -> COMPLETED succeeds.")

            # -----------------------------------------------------------------
            # TEST 10: completed_at behavior is correct
            # -----------------------------------------------------------------
            assert item9_data["completed_at"] is not None
            res10 = await client.put(
                f"/api/v1/student/roadmap/items/{item1_id}",
                json={"status": "IN_PROGRESS"},
                headers=headers_a,
            )
            assert res10.status_code == 200
            assert res10.json()["completed_at"] is None

            await client.put(
                f"/api/v1/student/roadmap/items/{item1_id}",
                json={"status": "COMPLETED"},
                headers=headers_a,
            )
            passed_tests += 1
            print("[PASS] TEST 10: completed_at timestamp populated on COMPLETED and cleared on reopen.")

            # -----------------------------------------------------------------
            # TEST 11: GET /api/v1/student/roadmap returns persisted state
            # -----------------------------------------------------------------
            res11 = await client.get("/api/v1/student/roadmap", headers=headers_a)
            assert res11.status_code == 200
            data11 = res11.json()
            assert data11["completed_steps"] == 1
            assert data11["completion_percentage"] == 50
            passed_tests += 1
            print("[PASS] TEST 11: GET /roadmap returns persisted state (1/2 = 50%).")

            # -----------------------------------------------------------------
            # TEST 12: Training catalog loads from real DB
            # -----------------------------------------------------------------
            res12 = await client.get("/api/v1/student/learning", headers=headers_a)
            assert res12.status_code == 200, f"Test 12 failed: {res12.text}"
            data12 = res12.json()
            prog_ids = [p["id"] for p in data12["available_programs"]]
            assert str(program.id) in prog_ids
            passed_tests += 1
            print("[PASS] TEST 12: Available training programs catalog loads from database.")

            # -----------------------------------------------------------------
            # TEST 13: Student can enroll in valid training program
            # -----------------------------------------------------------------
            res13 = await client.post(
                f"/api/v1/student/learning/enroll/{program.id}",
                headers=headers_a,
            )
            assert res13.status_code == 201, f"Test 13 failed status {res13.status_code}: {res13.text}"
            data13 = res13.json()
            assert data13["training_program_id"] == str(program.id)
            assert data13["completion_status"] == "ENROLLED"
            passed_tests += 1
            print("[PASS] TEST 13: Student successfully enrolled in training program.")

            # -----------------------------------------------------------------
            # TEST 14: Duplicate enrollment is rejected cleanly (400 Bad Request)
            # -----------------------------------------------------------------
            res14 = await client.post(
                f"/api/v1/student/learning/enroll/{program.id}",
                headers=headers_a,
            )
            assert res14.status_code == 400, f"Expected 400, got {res14.status_code}"
            assert "already enrolled" in res14.json()["detail"].lower()
            passed_tests += 1
            print("[PASS] TEST 14: Duplicate training enrollment cleanly rejected with 400 Bad Request.")

            # -----------------------------------------------------------------
            # TEST 15: Student enrollment persists in My Learning
            # -----------------------------------------------------------------
            res15 = await client.get("/api/v1/student/learning", headers=headers_a)
            assert res15.status_code == 200
            data15 = res15.json()
            assert data15["enrolled_count"] == 1
            enrolled_ids = [e["training_program_id"] for e in data15["current_enrollments"]]
            assert str(program.id) in enrolled_ids
            passed_tests += 1
            print("[PASS] TEST 15: Training enrollment persists and appears in My Learning workspace.")

            # -----------------------------------------------------------------
            # TEST 16: Student A cannot update Student B's roadmap item (IDOR protection)
            # -----------------------------------------------------------------
            res_gen_b = await client.post("/api/v1/student/roadmap/generate", headers=headers_b)
            assert res_gen_b.status_code == 200
            item_b_id = res_gen_b.json()["roadmap"]["items"][0]["id"]

            res16 = await client.put(
                f"/api/v1/student/roadmap/items/{item_b_id}",
                json={"status": "COMPLETED"},
                headers=headers_a,
            )
            assert res16.status_code in [403, 404], f"Expected 404/403, got {res16.status_code}"
            passed_tests += 1
            print("[PASS] TEST 16: IDOR protection enforced (Student A cannot update Student B's roadmap item).")

            # -----------------------------------------------------------------
            # TEST 17: Student A cannot access Student B training enrollment data
            # -----------------------------------------------------------------
            res17 = await client.get("/api/v1/student/learning", headers=headers_b)
            assert res17.status_code == 200
            assert res17.json()["enrolled_count"] == 0
            passed_tests += 1
            print("[PASS] TEST 17: Training enrollments strictly isolated by student identity.")

            # -----------------------------------------------------------------
            # TEST 18: TEACHER role blocked on roadmap/learning endpoints
            # -----------------------------------------------------------------
            headers_t = {"Authorization": f"Bearer {token_teacher}"}
            res18 = await client.get("/api/v1/student/roadmap", headers=headers_t)
            assert res18.status_code == 403
            passed_tests += 1
            print("[PASS] TEST 18: TEACHER role blocked with 403 Forbidden.")

            # -----------------------------------------------------------------
            # TEST 19: COLLEGE_ADMIN role blocked on roadmap/learning endpoints
            # -----------------------------------------------------------------
            headers_adm = {"Authorization": f"Bearer {token_admin}"}
            res19 = await client.get("/api/v1/student/learning", headers=headers_adm)
            assert res19.status_code == 403
            passed_tests += 1
            print("[PASS] TEST 19: COLLEGE_ADMIN role blocked with 403 Forbidden.")

            # -----------------------------------------------------------------
            # TEST 20: INDUSTRY role blocked on roadmap/learning endpoints
            # -----------------------------------------------------------------
            headers_ind = {"Authorization": f"Bearer {token_industry}"}
            res20 = await client.get("/api/v1/student/roadmap", headers=headers_ind)
            assert res20.status_code == 403
            passed_tests += 1
            print("[PASS] TEST 20: INDUSTRY role blocked with 403 Forbidden.")

            # -----------------------------------------------------------------
            # TEST 21: ALUMNI role blocked on roadmap/learning endpoints
            # -----------------------------------------------------------------
            headers_alm = {"Authorization": f"Bearer {token_alumni}"}
            res21 = await client.get("/api/v1/student/learning", headers=headers_alm)
            assert res21.status_code == 403
            passed_tests += 1
            print("[PASS] TEST 21: ALUMNI role blocked with 403 Forbidden.")

            # -----------------------------------------------------------------
            # TEST 22: Inactive account token blocked (401 Unauthorized)
            # -----------------------------------------------------------------
            headers_inact = {"Authorization": f"Bearer {token_inactive}"}
            res22 = await client.get("/api/v1/student/roadmap", headers=headers_inact)
            assert res22.status_code == 401
            passed_tests += 1
            print("[PASS] TEST 22: Suspended/inactive account token blocked with 401 Unauthorized.")

            # -----------------------------------------------------------------
            # TEST 23: Invalid roadmap item UUID rejected cleanly (404 Not Found)
            # -----------------------------------------------------------------
            fake_uuid = str(uuid.uuid4())
            res23 = await client.put(
                f"/api/v1/student/roadmap/items/{fake_uuid}",
                json={"status": "COMPLETED"},
                headers=headers_a,
            )
            assert res23.status_code == 404
            passed_tests += 1
            print("[PASS] TEST 23: Invalid roadmap item UUID rejected with 404 Not Found.")

            # -----------------------------------------------------------------
            # TEST 24: Invalid training program UUID rejected cleanly (404 Not Found)
            # -----------------------------------------------------------------
            res24 = await client.post(
                f"/api/v1/student/learning/enroll/{fake_uuid}",
                headers=headers_a,
            )
            assert res24.status_code == 404
            passed_tests += 1
            print("[PASS] TEST 24: Invalid training program UUID rejected with 404 Not Found.")

            # -----------------------------------------------------------------
            # TEST 25: Phase 3.3 regression: GET /api/v1/student/career-workspace
            # -----------------------------------------------------------------
            res25 = await client.get("/api/v1/student/career-workspace", headers=headers_a)
            assert res25.status_code == 200
            assert res25.json()["current_target_role"]["id"] == str(role.id)
            passed_tests += 1
            print("[PASS] TEST 25: Phase 3.3 Career Workspace endpoint regression passed.")

            # -----------------------------------------------------------------
            # TEST 26: Phase 3.2 regression: GET /api/v1/student/profile
            # -----------------------------------------------------------------
            res26 = await client.get("/api/v1/student/profile", headers=headers_a)
            assert res26.status_code == 200
            assert res26.json()["academic_profile"]["roll_number"] == "STA-101"
            passed_tests += 1
            print("[PASS] TEST 26: Phase 3.2 Student Profile endpoint regression passed.")

            # -----------------------------------------------------------------
            # TEST 27: Phase 3.1 regression: GET /api/v1/student/dashboard
            # -----------------------------------------------------------------
            res27 = await client.get("/api/v1/student/dashboard", headers=headers_a)
            assert res27.status_code == 200
            dash_data = res27.json()
            assert dash_data["metrics"]["active_roadmaps_count"] >= 1
            assert dash_data["metrics"]["completed_roadmap_steps_count"] >= 1
            passed_tests += 1
            print("[PASS] TEST 27: Phase 3.1 Student Dashboard endpoint regression passed.")

            # -----------------------------------------------------------------
            # TEST 28: Auth/RBAC regression: POST /api/v1/auth/login
            # -----------------------------------------------------------------
            res28 = await client.post(
                "/api/v1/auth/login",
                json={"email": u_student_a.email, "password": "Password123!"},
            )
            assert res28.status_code == 200
            assert "access_token" in res28.json()
            passed_tests += 1
            print("[PASS] TEST 28: Auth & RBAC login regression passed.")

        finally:
            # Mandatory Cleanup
            await cleanup_test_records(
                user_ids=test_user_ids,
                role_ids=test_role_ids,
                skill_ids=test_skill_ids,
                dept_ids=test_dept_ids,
                inst_ids=test_inst_ids,
                program_ids=test_program_ids,
            )

    print("=" * 80)
    print(f"PHASE 3.4 VERIFICATION COMPLETE: {passed_tests}/{total_tests} TESTS PASSED.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_phase_3_4_tests())
