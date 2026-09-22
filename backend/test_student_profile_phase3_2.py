"""
SKILLY MODULE 03 (STUDENT) — PHASE 3.2 AUTOMATED TEST SUITE
Student Profile & Academic Identity Verification

Comprehensive 15-Point Verification Suite:
1. GET student profile — unlinked
2. GET student profile — linked
3. Completion calculation (deterministic formula: 30% Personal, 50% Academic, 20% Career)
4. Personal profile update (Biographical & Contact)
5. Academic profile creation (First-time initialization)
6. Academic profile update (Modifying existing academic details)
7. Institution/Department mismatch rejection (Composite FK constraint)
8. Career role selection
9. Graduation year earlier than enrollment year rejection (chk_students_graduation)
10. Invalid CGPA rejection (chk_students_cgpa / Pydantic validation)
11. Invalid semester rejection (chk_students_semester / Pydantic validation)
12. STUDENT-only RBAC (Rejection for non-student roles)
13. Strict IDOR protection (Student A cannot modify Student B)
14. Protected security fields immunity (Role / Active / Verified cannot be altered)
15. Inactive account rejection (Suspended token enforcement)
"""

import sys
import os
import uuid
import asyncio

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.core.database import async_session_maker
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.careers import CareerRole
from app.core.security import hash_password, create_access_token


async def run_phase_3_2_tests():
    print("=" * 80)
    print("SKILLY MODULE 03 (STUDENT) — PHASE 3.2: 15-POINT AUTOMATED TEST SUITE")
    print("Student Profile, Academic Identity, Composite FK, IDOR & RBAC Protection")
    print("=" * 80)

    # 1. Database Setup: Create Seed Records
    async with async_session_maker() as db:
        inst_code = f"INST_{uuid.uuid4().hex[:6].upper()}"
        institution = Institution(
            name="Indian Institute of Technology Excellence",
            code=inst_code,
            institution_type="COLLEGE",
            city="Bangalore",
            state="Karnataka",
            country="India",
            is_accredited=True,
        )
        db.add(institution)
        await db.flush()
        inst_id = institution.id
        inst_name = institution.name

        department = Department(
            institution_id=inst_id,
            name="Computer Science and Engineering",
            code=f"CSE_{uuid.uuid4().hex[:4].upper()}",
        )
        db.add(department)
        await db.flush()
        dept_id = department.id
        dept_name = department.name

        # Second institution to test cross-institution department rejection
        inst2_code = f"INST2_{uuid.uuid4().hex[:6].upper()}"
        institution2 = Institution(
            name="National Institute of Technology",
            code=inst2_code,
            institution_type="COLLEGE",
            city="Surathkal",
            state="Karnataka",
            country="India",
            is_accredited=True,
        )
        db.add(institution2)
        await db.flush()
        inst2_id = institution2.id

        department2 = Department(
            institution_id=inst2_id,
            name="Mechanical Engineering",
            code=f"MECH_{uuid.uuid4().hex[:4].upper()}",
        )
        db.add(department2)
        await db.flush()
        dept2_id = department2.id

        # Career role
        role_slug = f"fullstack-dev-{uuid.uuid4().hex[:6]}"
        career_role = CareerRole(
            title=f"Fullstack Developer {uuid.uuid4().hex[:4]}",
            slug=role_slug,
            industry_domain="Software Engineering",
            description="Designs and implements end-to-end web applications.",
            is_active=True,
        )
        db.add(career_role)
        await db.flush()
        career_role_id = career_role.id
        career_role_title = career_role.title

        # Student A (starts unlinked)
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
        student_a_id = student_a.id

        profile_a = UserProfile(
            user_id=student_a_id,
            first_name="Jordan",
            last_name="Lee",
            country="India",
        )
        db.add(profile_a)

        # Student B (for IDOR tests)
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
        student_b_id = student_b.id

        profile_b = UserProfile(
            user_id=student_b_id,
            first_name="Alex",
            last_name="Morgan",
            country="India",
        )
        db.add(profile_b)

        # Non-student roles for RBAC test
        teacher_email = f"teacher_{uuid.uuid4().hex[:6]}@example.com"
        teacher = User(
            email=teacher_email,
            username=f"teacher_{uuid.uuid4().hex[:6]}",
            hashed_password=hash_password("TeacherPass@123"),
            role="TEACHER",
            is_active=True,
            is_verified=True,
        )
        db.add(teacher)
        await db.flush()
        teacher_id = teacher.id

        admin_email = f"admin_{uuid.uuid4().hex[:6]}@example.com"
        college_admin = User(
            email=admin_email,
            username=f"admin_{uuid.uuid4().hex[:6]}",
            hashed_password=hash_password("AdminPass@123"),
            role="COLLEGE_ADMIN",
            is_active=True,
            is_verified=True,
        )
        db.add(college_admin)
        await db.flush()
        admin_id = college_admin.id

        industry_user = User(
            email=f"industry_{uuid.uuid4().hex[:6]}@example.com",
            username=f"ind_{uuid.uuid4().hex[:6]}",
            hashed_password=hash_password("IndPass@123"),
            role="INDUSTRY",
            is_active=True,
            is_verified=True,
        )
        db.add(industry_user)
        await db.flush()
        industry_id = industry_user.id

        await db.commit()

    # Generate JWT tokens
    token_a = create_access_token(subject=str(student_a_id), role="STUDENT")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b = create_access_token(subject=str(student_b_id), role="STUDENT")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    token_teacher = create_access_token(subject=str(teacher_id), role="TEACHER")
    headers_teacher = {"Authorization": f"Bearer {token_teacher}"}

    token_admin = create_access_token(subject=str(admin_id), role="COLLEGE_ADMIN")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    token_industry = create_access_token(subject=str(industry_id), role="INDUSTRY")
    headers_industry = {"Authorization": f"Bearer {token_industry}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        # -------------------------------------------------------------
        # TEST 1: GET student profile — unlinked
        # -------------------------------------------------------------
        print("\n[TEST 1] GET student profile — unlinked...")
        res = await client.get("/api/v1/student/profile", headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["user"]["email"] == student_a_email
        assert data["user"]["role"] == "STUDENT"
        assert data["academic_profile"] is None
        assert data["is_profile_complete"] is False
        assert "Institution" in data["completion"]["missing_fields"]
        print(" -> PASS: Unlinked profile returned correctly with is_profile_complete=False.")

        # -------------------------------------------------------------
        # TEST 2: Personal profile update (Biographical & Contact)
        # -------------------------------------------------------------
        print("\n[TEST 2] Personal profile update (Biographical & Contact)...")
        personal_payload = {
            "first_name": "Jordan",
            "last_name": "Lee-Smith",
            "phone": "+91 9876543210",
            "bio": "Fullstack developer passionate about high performance systems.",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India",
            "linkedin_url": "https://linkedin.com/in/jordanlee",
            "github_url": "https://github.com/jordanlee",
            "website_url": "https://jordanlee.dev",
        }
        res = await client.put("/api/v1/student/profile", json=personal_payload, headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["user"]["profile"]["first_name"] == "Jordan"
        assert data["user"]["profile"]["last_name"] == "Lee-Smith"
        assert data["user"]["profile"]["phone"] == "+91 9876543210"
        assert data["user"]["profile"]["city"] == "Bengaluru"
        assert data["user"]["profile"]["state"] == "Karnataka"
        print(" -> PASS: Personal profile successfully updated and persisted in user_profiles.")

        # -------------------------------------------------------------
        # TEST 3: Completion calculation (Personal sub-score check)
        # -------------------------------------------------------------
        print("\n[TEST 3] Completion calculation (Formula: 30% Personal, 50% Academic, 20% Career)...")
        # With 4 personal fields completed (7.5% each = 30%), personal_percentage is 100%, total percentage is 30%
        assert data["completion"]["personal_percentage"] == 100
        assert data["completion"]["percentage"] == 30
        assert data["completion"]["academic_percentage"] == 0
        assert data["completion"]["career_percentage"] == 0
        assert data["completion"]["is_complete"] is False
        print(" -> PASS: Deterministic completion calculation matches exact weighted scoring formula.")

        # -------------------------------------------------------------
        # TEST 4: Academic profile creation (First-time initialization)
        # -------------------------------------------------------------
        print("\n[TEST 4] Academic profile creation (First-time initialization)...")
        academic_create_payload = {
            "institution_id": str(inst_id),
            "department_id": str(dept_id),
            "roll_number": "2024CS1099",
            "enrollment_year": 2023,
            "graduation_year": 2027,
            "current_semester": 4,
            "cgpa": 8.95,
        }
        res = await client.put("/api/v1/student/profile", json=academic_create_payload, headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["academic_profile"] is not None
        assert data["academic_profile"]["roll_number"] == "2024CS1099"
        assert data["academic_profile"]["institution_id"] == str(inst_id)
        assert data["academic_profile"]["department_id"] == str(dept_id)
        assert data["completion"]["academic_percentage"] == 100
        assert data["completion"]["percentage"] == 80  # 30% personal + 50% academic = 80%
        print(" -> PASS: Student academic record created with composite foreign key intact.")

        # -------------------------------------------------------------
        # TEST 5: GET student profile — linked
        # -------------------------------------------------------------
        print("\n[TEST 5] GET student profile — linked...")
        res = await client.get("/api/v1/student/profile", headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["academic_profile"] is not None
        assert data["academic_profile"]["institution"]["name"] == inst_name
        assert data["academic_profile"]["department"]["name"] == dept_name
        assert data["academic_profile"]["current_semester"] == 4
        print(" -> PASS: Linked student profile returns nested institution and department models.")

        # -------------------------------------------------------------
        # TEST 6: Academic profile update (Modifying existing details)
        # -------------------------------------------------------------
        print("\n[TEST 6] Academic profile update (Modifying semester & CGPA)...")
        academic_update_payload = {
            "current_semester": 5,
            "cgpa": 9.15,
            "roll_number": "2024CS1099-HONORS",
        }
        res = await client.put("/api/v1/student/profile", json=academic_update_payload, headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["academic_profile"]["current_semester"] == 5
        assert float(data["academic_profile"]["cgpa"]) == 9.15
        assert data["academic_profile"]["roll_number"] == "2024CS1099-HONORS"
        print(" -> PASS: Existing academic profile successfully updated.")

        # -------------------------------------------------------------
        # TEST 7: Institution/Department mismatch rejection (Composite FK)
        # -------------------------------------------------------------
        print("\n[TEST 7] Institution/Department mismatch rejection (Composite relationship)...")
        mismatch_payload = {
            "institution_id": str(inst_id),
            "department_id": str(dept2_id),  # Belongs to institution 2!
        }
        res = await client.put("/api/v1/student/profile", json=mismatch_payload, headers=headers_a)
        assert res.status_code == 400, f"Expected 400 Bad Request, got {res.status_code}: {res.text}"
        assert "Department does not belong to the selected Institution" in res.json()["detail"]
        print(" -> PASS: Mismatched department belonging to another institution rejected with 400 Bad Request.")

        # -------------------------------------------------------------
        # TEST 8: Career role selection
        # -------------------------------------------------------------
        print("\n[TEST 8] Career role selection & 100% completion verification...")
        career_payload = {
            "target_career_role_id": str(career_role_id),
        }
        res = await client.put("/api/v1/student/profile", json=career_payload, headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["academic_profile"]["target_career_role_id"] == str(career_role_id)
        assert data["academic_profile"]["target_career_role"]["title"] == career_role_title
        assert data["is_profile_complete"] is True
        assert data["completion"]["percentage"] == 100
        assert data["completion"]["is_complete"] is True
        assert len(data["completion"]["missing_fields"]) == 0
        print(" -> PASS: Target career role selected; profile reached 100% complete.")

        # -------------------------------------------------------------
        # TEST 9: Graduation year < Enrollment year rejection
        # -------------------------------------------------------------
        print("\n[TEST 9] Graduation year < Enrollment year rejection...")
        invalid_years_payload = {
            "enrollment_year": 2026,
            "graduation_year": 2024,
        }
        res = await client.put("/api/v1/student/profile", json=invalid_years_payload, headers=headers_a)
        assert res.status_code in (400, 422), f"Expected 400 or 422, got {res.status_code}: {res.text}"
        print(" -> PASS: graduation_year < enrollment_year rejected with validation error.")

        # -------------------------------------------------------------
        # TEST 10: Invalid CGPA rejection (>10.00 / <0.00)
        # -------------------------------------------------------------
        print("\n[TEST 10] Invalid CGPA rejection (>10.00 / <0.00)...")
        res_cgpa_high = await client.put("/api/v1/student/profile", json={"cgpa": 11.00}, headers=headers_a)
        assert res_cgpa_high.status_code == 422, f"Expected 422, got {res_cgpa_high.status_code}"

        res_cgpa_low = await client.put("/api/v1/student/profile", json={"cgpa": -1.50}, headers=headers_a)
        assert res_cgpa_low.status_code == 422, f"Expected 422, got {res_cgpa_low.status_code}"
        print(" -> PASS: Out-of-range CGPA rejected with 422 Unprocessable Entity.")

        # -------------------------------------------------------------
        # TEST 11: Invalid semester rejection (<1 / >12)
        # -------------------------------------------------------------
        print("\n[TEST 11] Invalid semester rejection (<1 / >12)...")
        res_sem_low = await client.put("/api/v1/student/profile", json={"current_semester": 0}, headers=headers_a)
        assert res_sem_low.status_code == 422, f"Expected 422, got {res_sem_low.status_code}"

        res_sem_high = await client.put("/api/v1/student/profile", json={"current_semester": 13}, headers=headers_a)
        assert res_sem_high.status_code == 422, f"Expected 422, got {res_sem_high.status_code}"
        print(" -> PASS: Out-of-range semester rejected with 422 Unprocessable Entity.")

        # -------------------------------------------------------------
        # TEST 12: STUDENT-only RBAC (Non-student role rejection)
        # -------------------------------------------------------------
        print("\n[TEST 12] STUDENT-only RBAC (Non-student role rejection)...")
        res_t_get = await client.get("/api/v1/student/profile", headers=headers_teacher)
        assert res_t_get.status_code == 403, f"Expected 403 for TEACHER, got {res_t_get.status_code}"

        res_a_get = await client.get("/api/v1/student/profile", headers=headers_admin)
        assert res_a_get.status_code == 403, f"Expected 403 for COLLEGE_ADMIN, got {res_a_get.status_code}"

        res_i_get = await client.get("/api/v1/student/profile", headers=headers_industry)
        assert res_i_get.status_code == 403, f"Expected 403 for INDUSTRY, got {res_i_get.status_code}"
        print(" -> PASS: TEACHER, COLLEGE_ADMIN, and INDUSTRY rejected with 403 Forbidden.")

        # -------------------------------------------------------------
        # TEST 13: Strict IDOR protection (Student A cannot modify Student B)
        # -------------------------------------------------------------
        print("\n[TEST 13] Strict IDOR protection (Cross-student modification attempt)...")
        idor_payload = {
            "user_id": str(student_b_id),
            "student_id": str(uuid.uuid4()),
            "first_name": "JordanRenamed",
            "roll_number": "ROLL_JORDAN_SECURE",
        }
        res_idor = await client.put("/api/v1/student/profile", json=idor_payload, headers=headers_a)
        assert res_idor.status_code == 200

        # Verify in DB that Student B was NOT modified
        async with async_session_maker() as check_db:
            stmt_b_check = select(UserProfile).where(UserProfile.user_id == student_b_id)
            profile_b_fresh = (await check_db.execute(stmt_b_check)).scalar_one()
            assert profile_b_fresh.first_name == "Alex", f"Student B first_name altered to {profile_b_fresh.first_name}!"

            # Verify that only Student A was updated
            stmt_a_check = select(UserProfile).where(UserProfile.user_id == student_a_id)
            profile_a_fresh = (await check_db.execute(stmt_a_check)).scalar_one()
            assert profile_a_fresh.first_name == "JordanRenamed"
        print(" -> PASS: Strict IDOR protection verified: Student B remains completely untouched.")

        # -------------------------------------------------------------
        # TEST 14: Protected security fields immunity
        # -------------------------------------------------------------
        print("\n[TEST 14] Protected security fields immunity (Role/Active/Verified tampering)...")
        security_payload = {
            "role": "COLLEGE_ADMIN",
            "is_active": False,
            "is_verified": False,
            "first_name": "JordanTamperProof",
        }
        res_sec = await client.put("/api/v1/student/profile", json=security_payload, headers=headers_a)
        assert res_sec.status_code == 200

        async with async_session_maker() as check_db:
            stmt_sec = select(User).where(User.id == student_a_id)
            user_a_fresh = (await check_db.execute(stmt_sec)).scalar_one()
            assert user_a_fresh.role == "STUDENT", f"Role was illegally escalated to {user_a_fresh.role}!"
            assert user_a_fresh.is_active is True
            assert user_a_fresh.is_verified is True
        print(" -> PASS: Protected fields immune to tampering; role and security flags unchanged.")

        # -------------------------------------------------------------
        # TEST 15: Inactive account rejection (Suspended token enforcement)
        # -------------------------------------------------------------
        print("\n[TEST 15] Inactive account rejection (Suspended token enforcement)...")
        async with async_session_maker() as update_db:
            stmt_update = select(User).where(User.id == student_a_id)
            user_a_to_deactivate = (await update_db.execute(stmt_update)).scalar_one()
            user_a_to_deactivate.is_active = False
            await update_db.commit()

        res_inact = await client.get("/api/v1/student/profile", headers=headers_a)
        assert res_inact.status_code == 401, f"Expected 401 for inactive user, got {res_inact.status_code}"
        print(" -> PASS: Inactive student token rejected with 401 Unauthorized.")

        # Re-activate for clean state
        async with async_session_maker() as update_db:
            stmt_update = select(User).where(User.id == student_a_id)
            user_a_to_reactivate = (await update_db.execute(stmt_update)).scalar_one()
            user_a_to_reactivate.is_active = True
            await update_db.commit()

    print("\n" + "=" * 80)
    print("ALL 15 PHASE 3.2 AUTOMATED TESTS PASSED SUCCESSFULLY (15/15)!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_phase_3_2_tests())
