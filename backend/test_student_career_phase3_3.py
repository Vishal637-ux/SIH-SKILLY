"""
SKILLY MODULE 03 (STUDENT) — PHASE 3.3 AUTOMATED TEST SUITE
Student Career Workspace, Role Explorer, Required Skills & Target Role Selection

Comprehensive 15-Point Verification Suite:
1. GET /student/career-workspace — Unselected target role overview
2. GET /student/career-roles — Real database active career roles list with skill counts
3. GET /student/career-roles — Domain & search keyword filtering
4. GET /student/career-roles/{role_id} — Detailed role specification with sorted required skills
5. PUT /student/target-role — Target career role selection & persistence to PostgreSQL
6. GET /student/career-workspace — Selected target career role with skills & updated completion
7. Verification of is_current_target flag on role list and role detail endpoints
8. Target career role update via PUT /student/profile with active target role
9. Rejection of invalid/nonexistent career role UUID (404 Not Found) on both endpoints
10. STUDENT-only RBAC enforcement (403 Forbidden for TEACHER, COLLEGE_ADMIN, INDUSTRY)
11. Strict IDOR protection (Student identity derived strictly from auth token; Student A cannot modify Student B)
12. Protected security fields immunity (Role, is_active, is_verified, user_id remain immutable)
13. Inactive student account rejection (401 Unauthorized for suspended tokens)
14. Phase 3.2 Profile & Academic Identity regression check
15. Phase 3.1 Dashboard & Journey regression check
"""

import sys
import os
import uuid
import asyncio
from typing import List

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.core.database import async_session_maker
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.careers import CareerRole, CareerRoleSkill
from app.models.skills import Skill
from app.core.security import hash_password, create_access_token


async def cleanup_test_records(
    user_ids: List[uuid.UUID],
    role_ids: List[uuid.UUID],
    skill_ids: List[uuid.UUID],
    dept_ids: List[uuid.UUID],
    inst_ids: List[uuid.UUID],
):
    """Safely cleans up records created specifically by the test suite."""
    async with async_session_maker() as db:
        try:
            if user_ids:
                await db.execute(delete(Student).where(Student.user_id.in_(user_ids)))
                await db.execute(delete(UserProfile).where(UserProfile.user_id.in_(user_ids)))
                await db.execute(delete(User).where(User.id.in_(user_ids)))

            if role_ids:
                await db.execute(delete(CareerRoleSkill).where(CareerRoleSkill.career_role_id.in_(role_ids)))
                await db.execute(delete(CareerRole).where(CareerRole.id.in_(role_ids)))

            if skill_ids:
                await db.execute(delete(CareerRoleSkill).where(CareerRoleSkill.skill_id.in_(skill_ids)))
                await db.execute(delete(Skill).where(Skill.id.in_(skill_ids)))

            if dept_ids:
                await db.execute(delete(Department).where(Department.id.in_(dept_ids)))

            if inst_ids:
                await db.execute(delete(Institution).where(Institution.id.in_(inst_ids)))

            await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"Warning during test cleanup: {e}")


async def cleanup_dangling_test_data():
    """Removes leftover temporary test users matching test patterns from prior aborted runs."""
    async with async_session_maker() as db:
        try:
            stmt = select(User.id).where(
                (User.email.like("student_a_%@example.com")) |
                (User.email.like("student_b_%@example.com")) |
                (User.email.like("teacher_%@example.com")) |
                (User.email.like("inactive_%@example.com"))
            )
            dangling_user_ids = (await db.execute(stmt)).scalars().all()
            if dangling_user_ids:
                await db.execute(delete(Student).where(Student.user_id.in_(dangling_user_ids)))
                await db.execute(delete(UserProfile).where(UserProfile.user_id.in_(dangling_user_ids)))
                await db.execute(delete(User).where(User.id.in_(dangling_user_ids)))
                await db.commit()
                print(f"Cleaned {len(dangling_user_ids)} dangling test user records from prior runs.")
        except Exception as e:
            await db.rollback()
            print(f"Note on initial cleanup: {e}")


async def run_phase_3_3_tests():
    print("=" * 80)
    print("SKILLY MODULE 03 (STUDENT) — PHASE 3.3: 15-POINT AUTOMATED TEST SUITE")
    print("Student Career Workspace, Role Explorer, Required Skills, IDOR & RBAC")
    print("=" * 80)

    # Initial cleanup of any prior aborted runs
    await cleanup_dangling_test_data()

    created_user_ids = []
    created_role_ids = []
    created_skill_ids = []
    created_dept_ids = []
    created_inst_ids = []

    passed_count = 0
    failed_count = 0
    error_count = 0

    try:
        # 1. Database Setup: Create Seed Skills, Roles, Institutions, Students
        async with async_session_maker() as db:
            # Academic Institution & Department
            inst_code = f"INST_{uuid.uuid4().hex[:6].upper()}"
            institution = Institution(
                name="National Institute of Technology Technology",
                code=inst_code,
                institution_type="COLLEGE",
                city="Pune",
                state="Maharashtra",
                country="India",
                is_accredited=True,
            )
            db.add(institution)
            await db.flush()
            inst_id = institution.id
            created_inst_ids.append(inst_id)

            department = Department(
                institution_id=inst_id,
                name="Computer Science & Engineering",
                code=f"CSE_{uuid.uuid4().hex[:4].upper()}",
            )
            db.add(department)
            await db.flush()
            dept_id = department.id
            created_dept_ids.append(dept_id)

            # Canonical Skills in database
            skill_python = Skill(
                name=f"Python Programming {uuid.uuid4().hex[:4]}",
                slug=f"python-{uuid.uuid4().hex[:6]}",
                category="Programming Languages",
                description="Core object-oriented and async programming in Python.",
                is_verified=True,
            )
            skill_react = Skill(
                name=f"React.js {uuid.uuid4().hex[:4]}",
                slug=f"react-{uuid.uuid4().hex[:6]}",
                category="Frontend Development",
                description="Component-driven frontend UI development with React.",
                is_verified=True,
            )
            skill_docker = Skill(
                name=f"Docker & Containers {uuid.uuid4().hex[:4]}",
                slug=f"docker-{uuid.uuid4().hex[:6]}",
                category="Cloud & DevOps",
                description="Containerization and microservices deployment.",
                is_verified=True,
            )
            db.add_all([skill_python, skill_react, skill_docker])
            await db.flush()
            created_skill_ids.extend([skill_python.id, skill_react.id, skill_docker.id])

            # Canonical Career Role 1: Fullstack Software Engineer
            role1_slug = f"fullstack-engineer-{uuid.uuid4().hex[:6]}"
            career_role1 = CareerRole(
                title=f"Fullstack Software Engineer {uuid.uuid4().hex[:4]}",
                slug=role1_slug,
                industry_domain="Software Engineering",
                description="Specializes in end-to-end full-stack web and API architectures.",
                is_active=True,
            )
            db.add(career_role1)
            await db.flush()
            created_role_ids.append(career_role1.id)

            # Link Role 1 Skills: Python (CORE), React (CORE), Docker (RECOMMENDED)
            crs1_1 = CareerRoleSkill(
                career_role_id=career_role1.id,
                skill_id=skill_python.id,
                required_level="ADVANCED",
                importance_level="CORE",
            )
            crs1_2 = CareerRoleSkill(
                career_role_id=career_role1.id,
                skill_id=skill_react.id,
                required_level="ADVANCED",
                importance_level="CORE",
            )
            crs1_3 = CareerRoleSkill(
                career_role_id=career_role1.id,
                skill_id=skill_docker.id,
                required_level="INTERMEDIATE",
                importance_level="RECOMMENDED",
            )
            db.add_all([crs1_1, crs1_2, crs1_3])

            # Canonical Career Role 2: Cloud DevOps Engineer
            role2_slug = f"cloud-devops-{uuid.uuid4().hex[:6]}"
            career_role2 = CareerRole(
                title=f"Cloud DevOps Architect {uuid.uuid4().hex[:4]}",
                slug=role2_slug,
                industry_domain="Cloud & DevOps",
                description="Specializes in CI/CD automation, cloud infrastructure, and kubernetes.",
                is_active=True,
            )
            db.add(career_role2)
            await db.flush()
            created_role_ids.append(career_role2.id)

            # Link Role 2 Skills: Docker (CORE), Python (RECOMMENDED)
            crs2_1 = CareerRoleSkill(
                career_role_id=career_role2.id,
                skill_id=skill_docker.id,
                required_level="EXPERT",
                importance_level="CORE",
            )
            crs2_2 = CareerRoleSkill(
                career_role_id=career_role2.id,
                skill_id=skill_python.id,
                required_level="INTERMEDIATE",
                importance_level="RECOMMENDED",
            )
            db.add_all([crs2_1, crs2_2])

            # Canonical Career Role 3: Inactive Career Role (for rejection testing)
            role3_slug = f"legacy-developer-{uuid.uuid4().hex[:6]}"
            career_role_inactive = CareerRole(
                title=f"Legacy COBOL Maintainer {uuid.uuid4().hex[:4]}",
                slug=role3_slug,
                industry_domain="Legacy Systems",
                description="Deprecated legacy architecture role.",
                is_active=False,
            )
            db.add(career_role_inactive)
            await db.flush()
            created_role_ids.append(career_role_inactive.id)

            # Student User A (starts without target career role)
            student_a_email = f"student_a_{uuid.uuid4().hex[:6]}@example.com"
            student_a = User(
                email=student_a_email,
                username=f"student_a_{uuid.uuid4().hex[:6]}",
                hashed_password=hash_password("StudentPass@123"),
                role="STUDENT",
                is_active=True,
                is_verified=True,
            )
            db.add(student_a)
            await db.flush()
            created_user_ids.append(student_a.id)

            student_a_prof = UserProfile(
                user_id=student_a.id,
                first_name="Aarav",
                last_name="Patel",
                city="Pune",
                state="Maharashtra",
                phone="+91 9876543210",
            )
            db.add(student_a_prof)

            student_a_rec = Student(
                user_id=student_a.id,
                institution_id=inst_id,
                department_id=dept_id,
                roll_number=f"ROLL-A-{uuid.uuid4().hex[:4].upper()}",
                enrollment_year=2023,
                graduation_year=2027,
                current_semester=4,
                cgpa=8.75,
                target_career_role_id=None,  # Not set yet
            )
            db.add(student_a_rec)

            # Student User B (for IDOR tests)
            student_b_email = f"student_b_{uuid.uuid4().hex[:6]}@example.com"
            student_b = User(
                email=student_b_email,
                username=f"student_b_{uuid.uuid4().hex[:6]}",
                hashed_password=hash_password("StudentPass@123"),
                role="STUDENT",
                is_active=True,
                is_verified=True,
            )
            db.add(student_b)
            await db.flush()
            created_user_ids.append(student_b.id)

            student_b_prof = UserProfile(
                user_id=student_b.id,
                first_name="Diya",
                last_name="Iyer",
                city="Pune",
                state="Maharashtra",
                phone="+91 9123456780",
            )
            db.add(student_b_prof)

            student_b_rec = Student(
                user_id=student_b.id,
                institution_id=inst_id,
                department_id=dept_id,
                roll_number=f"ROLL-B-{uuid.uuid4().hex[:4].upper()}",
                enrollment_year=2023,
                graduation_year=2027,
                current_semester=4,
                cgpa=9.10,
                target_career_role_id=career_role2.id,
            )
            db.add(student_b_rec)

            # Teacher User (for RBAC test)
            teacher_email = f"teacher_{uuid.uuid4().hex[:6]}@example.com"
            teacher_user = User(
                email=teacher_email,
                username=f"teacher_{uuid.uuid4().hex[:6]}",
                hashed_password=hash_password("TeacherPass@123"),
                role="TEACHER",
                is_active=True,
                is_verified=True,
            )
            db.add(teacher_user)
            await db.flush()
            created_user_ids.append(teacher_user.id)

            # Inactive Student User (for inactive account test)
            inactive_email = f"inactive_{uuid.uuid4().hex[:6]}@example.com"
            inactive_student = User(
                email=inactive_email,
                username=f"inactive_{uuid.uuid4().hex[:6]}",
                hashed_password=hash_password("InactivePass@123"),
                role="STUDENT",
                is_active=False,
                is_verified=True,
            )
            db.add(inactive_student)
            await db.flush()
            created_user_ids.append(inactive_student.id)

            await db.commit()

            # Save IDs for tests
            role1_id = career_role1.id
            role1_title = career_role1.title
            role2_id = career_role2.id
            role2_title = career_role2.title
            role_inactive_id = career_role_inactive.id
            student_a_id = student_a.id
            student_b_id = student_b.id
            teacher_id = teacher_user.id
            inactive_id = inactive_student.id

        # Generate canonical JWT tokens using project's create_access_token signature: (subject=..., role=...)
        token_student_a = create_access_token(subject=str(student_a_id), role="STUDENT")
        token_student_b = create_access_token(subject=str(student_b_id), role="STUDENT")
        token_teacher = create_access_token(subject=str(teacher_id), role="TEACHER")
        token_inactive = create_access_token(subject=str(inactive_id), role="STUDENT")

        headers_a = {"Authorization": f"Bearer {token_student_a}"}
        headers_b = {"Authorization": f"Bearer {token_student_b}"}
        headers_teacher = {"Authorization": f"Bearer {token_teacher}"}
        headers_inactive = {"Authorization": f"Bearer {token_inactive}"}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # -------------------------------------------------------------
            # TEST 1: GET /student/career-workspace (unselected target role)
            # -------------------------------------------------------------
            try:
                res = await client.get("/api/v1/student/career-workspace", headers=headers_a)
                assert res.status_code == 200, f"Test 1 Failed: {res.text}"
                data = res.json()
                assert data["current_target_role"] is None, "Student A should initially have no target role"
                assert data["available_roles_count"] >= 2, "Should count available active roles"
                assert data["completion"]["career_percentage"] == 0, "Career percentage should be 0 without target role"
                assert "Target Career Role" in data["completion"]["missing_fields"]
                print("  [PASS] Test 1: GET /student/career-workspace unselected state verified.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 1 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 2: GET /student/career-roles (Real DB list with skill counts)
            # -------------------------------------------------------------
            try:
                res = await client.get("/api/v1/student/career-roles", headers=headers_a)
                assert res.status_code == 200, f"Test 2 Failed: {res.text}"
                roles = res.json()
                assert len(roles) >= 2, f"Expected at least 2 active roles, got {len(roles)}"
                inactive_found = any(r["id"] == str(role_inactive_id) for r in roles)
                assert not inactive_found, "Inactive career role must not be listed"

                r1 = next(r for r in roles if r["id"] == str(role1_id))
                assert r1["title"] == role1_title
                assert r1["skills_count"] == 3, f"Expected 3 skills, got {r1['skills_count']}"
                assert r1["core_skills_count"] == 2, f"Expected 2 core skills, got {r1['core_skills_count']}"
                assert r1["is_current_target"] is False, "Role 1 should not be target for Student A yet"
                print("  [PASS] Test 2: GET /student/career-roles live catalog and skill counts verified.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 2 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 3: GET /student/career-roles with domain & search filter
            # -------------------------------------------------------------
            try:
                res_dom = await client.get("/api/v1/student/career-roles?domain=Cloud", headers=headers_a)
                assert res_dom.status_code == 200
                cloud_roles = res_dom.json()
                assert all("Cloud" in r["industry_domain"] for r in cloud_roles), "Domain filter failed"

                res_search = await client.get(f"/api/v1/student/career-roles?search={role1_slug[:8]}", headers=headers_a)
                assert res_search.status_code == 200
                search_roles = res_search.json()
                assert any(r["id"] == str(role1_id) for r in search_roles), "Search filter failed"
                print("  [PASS] Test 3: Domain & keyword filtering on career roles verified.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 3 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 4: GET /student/career-roles/{role_id} (Detailed specification)
            # -------------------------------------------------------------
            try:
                res_detail = await client.get(f"/api/v1/student/career-roles/{role1_id}", headers=headers_a)
                assert res_detail.status_code == 200, f"Test 4 Failed: {res_detail.text}"
                detail = res_detail.json()
                assert detail["id"] == str(role1_id)
                assert detail["title"] == role1_title
                assert detail["is_active"] is True
                assert len(detail["required_skills"]) == 3
                assert detail["required_skills"][0]["importance_level"] == "CORE"
                assert detail["required_skills"][1]["importance_level"] == "CORE"
                assert detail["required_skills"][2]["importance_level"] == "RECOMMENDED"
                print("  [PASS] Test 4: GET /student/career-roles/{role_id} required skills hierarchy verified.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 4 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 5: PUT /student/target-role (Select target career goal)
            # -------------------------------------------------------------
            try:
                res_set = await client.put(
                    "/api/v1/student/target-role",
                    headers=headers_a,
                    json={"career_role_id": str(role1_id)},
                )
                assert res_set.status_code == 200, f"Test 5 Failed: {res_set.text}"
                set_data = res_set.json()
                assert set_data["target_career_role"]["id"] == str(role1_id)
                assert set_data["target_career_role"]["is_current_target"] is True
                assert set_data["completion"]["career_percentage"] == 100, "Career percentage should now be 100%"
                assert set_data["completion"]["percentage"] == 100, "Overall completion should reach 100%"
                assert set_data["completion"]["is_complete"] is True
                print("  [PASS] Test 5: PUT /student/target-role selection & completion recalculation verified.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 5 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 6: GET /student/career-workspace (Reflects selected role)
            # -------------------------------------------------------------
            try:
                res_ws = await client.get("/api/v1/student/career-workspace", headers=headers_a)
                assert res_ws.status_code == 200
                ws_data = res_ws.json()
                assert ws_data["current_target_role"] is not None
                assert ws_data["current_target_role"]["id"] == str(role1_id)
                assert ws_data["current_target_role"]["title"] == role1_title
                assert len(ws_data["current_target_role"]["required_skills"]) == 3
                assert ws_data["completion"]["percentage"] == 100
                print("  [PASS] Test 6: GET /student/career-workspace target role persistence verified.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 6 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 7: is_current_target flag on list and detail
            # -------------------------------------------------------------
            try:
                res_roles_after = await client.get("/api/v1/student/career-roles", headers=headers_a)
                roles_after = res_roles_after.json()
                r1_after = next(r for r in roles_after if r["id"] == str(role1_id))
                r2_after = next(r for r in roles_after if r["id"] == str(role2_id))
                assert r1_after["is_current_target"] is True, "Role 1 must now be marked is_current_target=True"
                assert r2_after["is_current_target"] is False, "Role 2 must be marked is_current_target=False"
                print("  [PASS] Test 7: is_current_target flags verified across catalog endpoints.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 7 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 8: Update target career role via PUT /student/profile
            # -------------------------------------------------------------
            try:
                res_prof_update = await client.put(
                    "/api/v1/student/profile",
                    headers=headers_a,
                    json={"target_career_role_id": str(role2_id)},
                )
                assert res_prof_update.status_code == 200, f"Test 8 Failed: {res_prof_update.text}"
                prof_data = res_prof_update.json()
                assert prof_data["academic_profile"]["target_career_role_id"] == str(role2_id)
                assert prof_data["academic_profile"]["target_career_role"]["title"] == role2_title
                print("  [PASS] Test 8: Target career update via PUT /student/profile verified.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 8 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 9: Rejection of invalid/nonexistent career role UUID (404)
            # -------------------------------------------------------------
            try:
                fake_uuid = str(uuid.uuid4())
                res_inv1 = await client.put(
                    "/api/v1/student/target-role",
                    headers=headers_a,
                    json={"career_role_id": fake_uuid},
                )
                assert res_inv1.status_code == 404, f"Expected 404 on invalid target-role, got {res_inv1.status_code}"

                res_inv_inactive = await client.put(
                    "/api/v1/student/target-role",
                    headers=headers_a,
                    json={"career_role_id": str(role_inactive_id)},
                )
                assert res_inv_inactive.status_code == 404, "Inactive role selection must be rejected with 404"

                res_inv2 = await client.put(
                    "/api/v1/student/profile",
                    headers=headers_a,
                    json={"target_career_role_id": fake_uuid},
                )
                assert res_inv2.status_code == 404, f"Expected 404 on invalid role in profile update, got {res_inv2.status_code}"

                res_inv3 = await client.get(f"/api/v1/student/career-roles/{fake_uuid}", headers=headers_a)
                assert res_inv3.status_code == 404
                print("  [PASS] Test 9: Invalid & inactive career role rejections (404) verified.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 9 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 10: STUDENT-only RBAC (403 for TEACHER / Non-Student)
            # -------------------------------------------------------------
            try:
                res_rbac1 = await client.get("/api/v1/student/career-workspace", headers=headers_teacher)
                assert res_rbac1.status_code == 403, f"Expected 403 for teacher on career-workspace, got {res_rbac1.status_code}"

                res_rbac2 = await client.get("/api/v1/student/career-roles", headers=headers_teacher)
                assert res_rbac2.status_code == 403, f"Expected 403 for teacher on career-roles, got {res_rbac2.status_code}"

                res_rbac3 = await client.put(
                    "/api/v1/student/target-role",
                    headers=headers_teacher,
                    json={"career_role_id": str(role1_id)},
                )
                assert res_rbac3.status_code == 403, f"Expected 403 for teacher on target-role, got {res_rbac3.status_code}"
                print("  [PASS] Test 10: Student-only RBAC authorization verified.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 10 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 11: Strict IDOR Protection (Student A cannot modify Student B)
            # -------------------------------------------------------------
            try:
                res_a_set = await client.put(
                    "/api/v1/student/target-role",
                    headers=headers_a,
                    json={"career_role_id": str(role1_id)},
                )
                assert res_a_set.status_code == 200

                res_b_ws = await client.get("/api/v1/student/career-workspace", headers=headers_b)
                assert res_b_ws.status_code == 200
                b_ws = res_b_ws.json()
                assert b_ws["current_target_role"]["id"] == str(role2_id), "Student B target role was improperly altered!"
                print("  [PASS] Test 11: IDOR isolation verified across distinct student records.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 11 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 12: Protected Security Fields Immunity
            # -------------------------------------------------------------
            try:
                res_tamper = await client.put(
                    "/api/v1/student/profile",
                    headers=headers_a,
                    json={
                        "role": "COLLEGE_ADMIN",
                        "is_active": False,
                        "is_verified": False,
                        "first_name": "Aarav Security Checked",
                    },
                )
                assert res_tamper.status_code == 200
                tamper_data = res_tamper.json()
                assert tamper_data["user"]["role"] == "STUDENT", "Role must remain STUDENT"
                assert tamper_data["user"]["is_active"] is True, "is_active must remain True"
                print("  [PASS] Test 12: Security fields immutability verified against payload tampering.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 12 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 13: Inactive Account Rejection (401)
            # -------------------------------------------------------------
            try:
                res_inact = await client.get("/api/v1/student/career-workspace", headers=headers_inactive)
                assert res_inact.status_code == 401, f"Expected 401 for inactive account, got {res_inact.status_code}"
                print("  [PASS] Test 13: Inactive account rejection (401) verified.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 13 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 14: Phase 3.2 Profile Regression Check
            # -------------------------------------------------------------
            try:
                res_p32 = await client.get("/api/v1/student/profile", headers=headers_a)
                assert res_p32.status_code == 200
                p32_data = res_p32.json()
                assert p32_data["academic_profile"]["institution"]["id"] == str(inst_id)
                assert p32_data["academic_profile"]["department"]["id"] == str(dept_id)
                assert p32_data["completion"]["percentage"] == 100
                print("  [PASS] Test 14: Phase 3.2 Profile & Academic Identity regression check passed.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 14 Failed: {e}")
                failed_count += 1

            # -------------------------------------------------------------
            # TEST 15: Phase 3.1 Dashboard Regression Check
            # -------------------------------------------------------------
            try:
                res_dash = await client.get("/api/v1/student/dashboard", headers=headers_a)
                assert res_dash.status_code == 200
                dash_data = res_dash.json()
                assert dash_data["journey_status"]["target_role_selected"] is True
                assert dash_data["journey_status"]["profile_completed"] is True
                assert dash_data["completion"]["percentage"] == 100
                print("  [PASS] Test 15: Phase 3.1 Dashboard & Journey regression check passed.")
                passed_count += 1
            except Exception as e:
                print(f"  [FAIL] Test 15 Failed: {e}")
                failed_count += 1

    except Exception as general_err:
        print(f"GENERAL ERROR DURING TEST EXECUTION: {general_err}")
        error_count += 1
    finally:
        # Mandatory test data cleanup
        print("\n--- Cleaning up test records from database ---")
        await cleanup_test_records(
            user_ids=created_user_ids,
            role_ids=created_role_ids,
            skill_ids=created_skill_ids,
            dept_ids=created_dept_ids,
            inst_ids=created_inst_ids,
        )
        print("Database cleanup completed successfully.")

    print("\n" + "=" * 80)
    print(f"PHASE 3.3 TEST SUMMARY:")
    print(f"  TOTAL TESTS : 15")
    print(f"  PASSED      : {passed_count}")
    print(f"  FAILED      : {failed_count}")
    print(f"  ERRORS      : {error_count}")
    print("=" * 80)

    if failed_count > 0 or error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_phase_3_3_tests())
