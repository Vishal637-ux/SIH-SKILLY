import sys
import os
import uuid
import asyncio
from decimal import Decimal
import httpx
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from app.core.config import settings

async def run_student_module_tests():
    print("=" * 75)
    print("SKILLY MODULE 03 — STUDENT MODULE FOUNDATION (PHASE 3.1) TEST SUITE")
    print("=" * 75)

    test_uid = uuid.uuid4().hex[:8]
    student_a_email = f"student_a_{test_uid}@skilly.edu"
    student_b_email = f"student_b_{test_uid}@skilly.edu"
    teacher_email = f"teacher_{test_uid}@skilly.edu"
    password = "StudentSecurePass#2026!"

    # 1. Direct DB Setup for Test Institution, Department, Career Role
    sync_conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB,
    )
    sync_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    inst_id = str(uuid.uuid4())
    dept_id = str(uuid.uuid4())
    career_role_id = str(uuid.uuid4())

    with sync_conn.cursor() as cur:
        # Seed test institution
        cur.execute(
            """
            INSERT INTO institutions (id, name, code, institution_type, city, state, country)
            VALUES (%s, %s, %s, 'COLLEGE', 'Bangalore', 'Karnataka', 'India')
            ON CONFLICT (code) DO NOTHING;
            """,
            (inst_id, f"Test Institute of Tech {test_uid}", f"TIT_{test_uid}"),
        )
        # Fetch actual inst_id if collided
        cur.execute("SELECT id FROM institutions WHERE code = %s;", (f"TIT_{test_uid}",))
        inst_id = cur.fetchone()[0]

        # Seed test department
        cur.execute(
            """
            INSERT INTO departments (id, institution_id, name, code)
            VALUES (%s, %s, 'Computer Science & Engineering', %s)
            ON CONFLICT (institution_id, code) DO NOTHING;
            """,
            (dept_id, inst_id, f"CSE_{test_uid}"),
        )
        cur.execute("SELECT id FROM departments WHERE institution_id = %s AND code = %s;", (inst_id, f"CSE_{test_uid}"))
        dept_id = cur.fetchone()[0]

        # Seed test career role
        cur.execute(
            """
            INSERT INTO career_roles (id, title, slug, industry_domain, description)
            VALUES (%s, %s, %s, 'Software Engineering', 'Full-stack web application development')
            ON CONFLICT (title) DO NOTHING;
            """,
            (career_role_id, f"Fullstack Developer {test_uid}", f"fullstack-dev-{test_uid}"),
        )
        cur.execute("SELECT id FROM career_roles WHERE title = %s;", (f"Fullstack Developer {test_uid}",))
        career_role_id = cur.fetchone()[0]

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        
        # -------------------------------------------------------------
        # 1. Unauthenticated Requests Rejection
        # -------------------------------------------------------------
        print("\n[TEST 1] Unauthenticated request rejection...")
        res_unauth_dash = await client.get("/api/v1/student/dashboard")
        assert res_unauth_dash.status_code == 401, f"Expected 401, got {res_unauth_dash.status_code}"
        
        res_unauth_prof = await client.get("/api/v1/student/profile")
        assert res_unauth_prof.status_code == 401, f"Expected 401, got {res_unauth_prof.status_code}"
        
        res_unauth_put = await client.put("/api/v1/student/profile", json={"first_name": "Test"})
        assert res_unauth_put.status_code == 401, f"Expected 401, got {res_unauth_put.status_code}"
        print(" -> PASS: Unauthenticated requests correctly rejected with 401 Unauthorized.")

        # -------------------------------------------------------------
        # 2. Register Student A, Student B, and Teacher
        # -------------------------------------------------------------
        print("\n[TEST 2] Registering test users (Student A, Student B, Teacher)...")
        res_st_a = await client.post(
            "/api/v1/auth/register",
            json={"email": student_a_email, "password": password, "role": "student", "fullName": "Alice Student"},
        )
        assert res_st_a.status_code == 201
        
        res_st_b = await client.post(
            "/api/v1/auth/register",
            json={"email": student_b_email, "password": password, "role": "student", "fullName": "Bob Student"},
        )
        assert res_st_b.status_code == 201

        res_tch = await client.post(
            "/api/v1/auth/register",
            json={"email": teacher_email, "password": password, "role": "teacher", "fullName": "Dr Teacher"},
        )
        assert res_tch.status_code == 201

        # Obtain tokens
        res_login_a = await client.post("/api/v1/auth/login", json={"email": student_a_email, "password": password})
        assert res_login_a.status_code == 200
        token_a = res_login_a.json()["access_token"]

        res_login_b = await client.post("/api/v1/auth/login", json={"email": student_b_email, "password": password})
        assert res_login_b.status_code == 200
        token_b = res_login_b.json()["access_token"]

        res_login_tch = await client.post("/api/v1/auth/login", json={"email": teacher_email, "password": password})
        assert res_login_tch.status_code == 200
        token_tch = res_login_tch.json()["access_token"]
        print(" -> PASS: Test users created and JWT tokens obtained.")

        # -------------------------------------------------------------
        # 3. RBAC Enforcement: Non-Student Access Denied
        # -------------------------------------------------------------
        print("\n[TEST 3] RBAC Enforcement: Teacher role attempting Student API...")
        res_tch_dash = await client.get("/api/v1/student/dashboard", headers={"Authorization": f"Bearer {token_tch}"})
        assert res_tch_dash.status_code == 403, f"Expected 403, got {res_tch_dash.status_code}"
        
        res_tch_prof = await client.get("/api/v1/student/profile", headers={"Authorization": f"Bearer {token_tch}"})
        assert res_tch_prof.status_code == 403, f"Expected 403, got {res_tch_prof.status_code}"
        print(" -> PASS: Non-student role blocked with 403 Forbidden.")

        # -------------------------------------------------------------
        # 4. Student Dashboard Real Metrics Verification (Zero Fake Data)
        # -------------------------------------------------------------
        print("\n[TEST 4] Student A Dashboard data aggregation...")
        res_dash = await client.get("/api/v1/student/dashboard", headers={"Authorization": f"Bearer {token_a}"})
        assert res_dash.status_code == 200, f"Expected 200, got {res_dash.status_code}: {res_dash.text}"
        dash_data = res_dash.json()
        assert dash_data["user"]["email"] == student_a_email.lower()
        assert dash_data["user"]["role"] == "STUDENT"
        assert dash_data["academic_profile"] is None # Fresh user has not linked academic profile yet
        assert dash_data["metrics"]["assessed_skills_count"] == 0 # Zero fake numbers!
        assert dash_data["metrics"]["active_roadmaps_count"] == 0
        assert dash_data["metrics"]["applications_count"] == 0
        assert dash_data["journey_status"]["profile_completed"] is False
        assert dash_data["journey_status"]["target_role_selected"] is False
        print(" -> PASS: Student Dashboard queried live database with accurate zero-counts.")

        # -------------------------------------------------------------
        # 5. Lookups Verification (Institutions, Departments, Career Roles)
        # -------------------------------------------------------------
        print("\n[TEST 5] Lookups endpoints...")
        res_insts = await client.get("/api/v1/student/institutions", headers={"Authorization": f"Bearer {token_a}"})
        assert res_insts.status_code == 200
        inst_list = res_insts.json()
        assert any(i["id"] == str(inst_id) for i in inst_list), "Seeded institution missing from lookup"

        res_depts = await client.get(f"/api/v1/student/departments?institution_id={inst_id}", headers={"Authorization": f"Bearer {token_a}"})
        assert res_depts.status_code == 200
        dept_list = res_depts.json()
        assert any(d["id"] == str(dept_id) for d in dept_list), "Seeded department missing from lookup"

        res_roles = await client.get("/api/v1/student/career-roles", headers={"Authorization": f"Bearer {token_a}"})
        assert res_roles.status_code == 200
        role_list = res_roles.json()
        assert any(r["id"] == str(career_role_id) for r in role_list), "Seeded career role missing from lookup"
        print(" -> PASS: All lookup endpoints returned active records.")

        # -------------------------------------------------------------
        # 6. Student Profile Update (Personal & Academic Profile Creation)
        # -------------------------------------------------------------
        print("\n[TEST 6] Student A Profile Update (Personal + Academic Linkage)...")
        update_payload = {
            "first_name": "Alice",
            "last_name": "Wonderland",
            "phone": "+91 9876543210",
            "bio": "Aspiring Fullstack Engineer specializing in React & Python.",
            "city": "Bangalore",
            "state": "Karnataka",
            "country": "India",
            "linkedin_url": "https://linkedin.com/in/alicestudent",
            "github_url": "https://github.com/alicestudent",
            "website_url": "https://alicestudent.dev",
            "institution_id": str(inst_id),
            "department_id": str(dept_id),
            "roll_number": f"ROLL_{test_uid}",
            "enrollment_year": 2023,
            "graduation_year": 2027,
            "current_semester": 5,
            "cgpa": 9.15,
            "target_career_role_id": str(career_role_id),
        }
        res_put = await client.put("/api/v1/student/profile", json=update_payload, headers={"Authorization": f"Bearer {token_a}"})
        assert res_put.status_code == 200, f"Expected 200, got {res_put.status_code}: {res_put.text}"
        prof_data = res_put.json()
        assert prof_data["user"]["profile"]["first_name"] == "Alice"
        assert prof_data["user"]["profile"]["phone"] == "+91 9876543210"
        assert prof_data["academic_profile"]["roll_number"] == f"ROLL_{test_uid}"
        assert prof_data["academic_profile"]["institution"]["id"] == str(inst_id)
        assert prof_data["academic_profile"]["department"]["id"] == str(dept_id)
        assert prof_data["academic_profile"]["target_career_role"]["id"] == str(career_role_id)
        assert prof_data["is_profile_complete"] is True
        print(" -> PASS: Profile updated successfully with institutional and career role linkage.")

        # -------------------------------------------------------------
        # 7. Dashboard Reflection after Profile Setup
        # -------------------------------------------------------------
        print("\n[TEST 7] Dashboard reflection after profile update...")
        res_dash_updated = await client.get("/api/v1/student/dashboard", headers={"Authorization": f"Bearer {token_a}"})
        assert res_dash_updated.status_code == 200
        dash_updated = res_dash_updated.json()
        assert dash_updated["academic_profile"]["roll_number"] == f"ROLL_{test_uid}"
        assert dash_updated["journey_status"]["profile_completed"] is True
        assert dash_updated["journey_status"]["target_role_selected"] is True
        print(" -> PASS: Student Dashboard reflects completed profile and selected target role.")

        # -------------------------------------------------------------
        # 8. Data Isolation & IDOR Check (Student A vs Student B)
        # -------------------------------------------------------------
        print("\n[TEST 8] Data Isolation Check (Student B cannot access Student A data)...")
        # Student B reads own profile
        res_prof_b = await client.get("/api/v1/student/profile", headers={"Authorization": f"Bearer {token_b}"})
        assert res_prof_b.status_code == 200
        prof_b_data = res_prof_b.json()
        assert prof_b_data["user"]["email"] == student_b_email.lower()
        assert prof_b_data["user"]["profile"]["first_name"] == "Bob"
        assert prof_b_data["academic_profile"] is None # Student B's academic profile is unlinked
        assert prof_b_data["is_profile_complete"] is False

        # Verify Student B's dashboard does NOT show Student A's roll number or affiliation
        res_dash_b = await client.get("/api/v1/student/dashboard", headers={"Authorization": f"Bearer {token_b}"})
        assert res_dash_b.status_code == 200
        dash_b_data = res_dash_b.json()
        assert dash_b_data["user"]["email"] == student_b_email.lower()
        assert dash_b_data["academic_profile"] is None
        assert dash_b_data["journey_status"]["profile_completed"] is False
        print(" -> PASS: Strict data isolation verified. Student B receives only Student B's records.")

        # -------------------------------------------------------------
        # 9. Validation Rejections (Invalid Department / Out of Bounds Metrics)
        # -------------------------------------------------------------
        print("\n[TEST 9] Input Validation rejection...")
        # Invalid semester (<1)
        bad_sem_payload = {
            "current_semester": 0,
        }
        res_bad_sem = await client.put("/api/v1/student/profile", json=bad_sem_payload, headers={"Authorization": f"Bearer {token_a}"})
        assert res_bad_sem.status_code == 422
        print(" -> PASS: Invalid current_semester (<1) rejected with 422 Unprocessable Entity.")

        # Invalid CGPA (>10.00)
        bad_cgpa_payload = {
            "cgpa": 11.50,
        }
        res_bad_cgpa = await client.put("/api/v1/student/profile", json=bad_cgpa_payload, headers={"Authorization": f"Bearer {token_a}"})
        assert res_bad_cgpa.status_code == 422
        print(" -> PASS: Invalid CGPA (>10.00) rejected with 422 Unprocessable Entity.")

    sync_conn.close()
    print("\n" + "=" * 75)
    print("ALL 9 STUDENT MODULE TESTS PASSED SUCCESSFULLY!")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    asyncio.run(run_student_module_tests())
