import sys
import os
import uuid
import asyncio
from decimal import Decimal
import json
import httpx
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from app.core.config import settings

async def run_phase_3_1_deep_audit():
    print("=" * 80)
    print("SKILLY — MODULE 03 PHASE 3.1 INDEPENDENT DEEP AUDIT")
    print("=" * 80)

    audit_results = {}
    test_uid = uuid.uuid4().hex[:8]
    student_a_email = f"audit_st_a_{test_uid}@skilly.edu"
    student_b_email = f"audit_st_b_{test_uid}@skilly.edu"
    teacher_email = f"audit_teacher_{test_uid}@skilly.edu"
    college_email = f"audit_college_{test_uid}@skilly.edu"
    industry_email = f"audit_industry_{test_uid}@skilly.edu"
    alumni_email = f"audit_alumni_{test_uid}@skilly.edu"
    password = "AuditStudentPass#2026!"

    # -----------------------------------------------------------------
    # 1. Direct PostgreSQL System Catalog & Manual State Audit
    # -----------------------------------------------------------------
    print("\n[LAYER 3] REAL POSTGRESQL MANUAL AUDIT")
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
        # Check Table Count in PostgreSQL
        cur.execute("""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name != 'alembic_version';
        """)
        tbl_count = cur.fetchone()[0]
        assert tbl_count == 47, f"Expected 47 tables, got {tbl_count}"
        print(f"  [PASS] PostgreSQL Catalog verified: {tbl_count}/47 application tables exist.")
        audit_results["table_count"] = tbl_count

        # Seed test institution & department for audit
        cur.execute(
            """
            INSERT INTO institutions (id, name, code, institution_type, city, state, country)
            VALUES (%s, %s, %s, 'COLLEGE', 'Bangalore', 'Karnataka', 'India')
            ON CONFLICT (code) DO NOTHING;
            """,
            (inst_id, f"Audit Institute of Tech {test_uid}", f"AIT_{test_uid}"),
        )
        cur.execute("SELECT id FROM institutions WHERE code = %s;", (f"AIT_{test_uid}",))
        inst_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO departments (id, institution_id, name, code)
            VALUES (%s, %s, 'Information Science & Engineering', %s)
            ON CONFLICT (institution_id, code) DO NOTHING;
            """,
            (dept_id, inst_id, f"ISE_{test_uid}"),
        )
        cur.execute("SELECT id FROM departments WHERE institution_id = %s AND code = %s;", (inst_id, f"ISE_{test_uid}"))
        dept_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO career_roles (id, title, slug, industry_domain, description)
            VALUES (%s, %s, %s, 'Cloud & DevOps', 'Designs and operates scalable cloud infrastructure')
            ON CONFLICT (title) DO NOTHING;
            """,
            (career_role_id, f"Cloud DevOps Engineer {test_uid}", f"cloud-devops-{test_uid}"),
        )
        cur.execute("SELECT id FROM career_roles WHERE title = %s;", (f"Cloud DevOps Engineer {test_uid}",))
        career_role_id = cur.fetchone()[0]

        print(f"  [PASS] Seeded & verified audit fixtures: Institution={inst_id}, Department={dept_id}, CareerRole={career_role_id}")

    # -----------------------------------------------------------------
    # 2. FastAPI Backend Manual Audit & Endpoint Verification
    # -----------------------------------------------------------------
    print("\n[LAYER 4 & 5] BACKEND MANUAL AUDIT & IDOR DATA ISOLATION")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://audit") as client:
        # 2.1 Unauthenticated requests
        unauth_dash = await client.get("/api/v1/student/dashboard")
        assert unauth_dash.status_code == 401
        print("  [PASS] GET /api/v1/student/dashboard without token -> 401 Unauthorized")

        unauth_prof = await client.get("/api/v1/student/profile")
        assert unauth_prof.status_code == 401
        print("  [PASS] GET /api/v1/student/profile without token -> 401 Unauthorized")

        unauth_put = await client.put("/api/v1/student/profile", json={"first_name": "Hacker"})
        assert unauth_put.status_code == 401
        print("  [PASS] PUT /api/v1/student/profile without token -> 401 Unauthorized")

        # 2.2 Register all stakeholder personas
        print("\n  Registering test accounts...")
        await client.post("/api/v1/auth/register", json={"email": student_a_email, "password": password, "role": "student", "fullName": "Alice Auditor"})
        await client.post("/api/v1/auth/register", json={"email": student_b_email, "password": password, "role": "student", "fullName": "Bob Auditor"})
        await client.post("/api/v1/auth/register", json={"email": teacher_email, "password": password, "role": "teacher", "fullName": "Prof Teacher"})
        await client.post("/api/v1/auth/register", json={"email": college_email, "password": password, "role": "college", "fullName": "Dean TPO"})
        await client.post("/api/v1/auth/register", json={"email": industry_email, "password": password, "role": "industry", "fullName": "HR Lead"})
        await client.post("/api/v1/auth/register", json={"email": alumni_email, "password": password, "role": "alumni", "fullName": "Senior Mentor"})

        # Get JWTs
        tok_a = (await client.post("/api/v1/auth/login", json={"email": student_a_email, "password": password})).json()["access_token"]
        tok_b = (await client.post("/api/v1/auth/login", json={"email": student_b_email, "password": password})).json()["access_token"]
        tok_tch = (await client.post("/api/v1/auth/login", json={"email": teacher_email, "password": password})).json()["access_token"]
        tok_col = (await client.post("/api/v1/auth/login", json={"email": college_email, "password": password})).json()["access_token"]
        tok_ind = (await client.post("/api/v1/auth/login", json={"email": industry_email, "password": password})).json()["access_token"]
        tok_alm = (await client.post("/api/v1/auth/login", json={"email": alumni_email, "password": password})).json()["access_token"]

        # -------------------------------------------------------------
        # 3. RBAC Manual Audit (Layer 6)
        # -------------------------------------------------------------
        print("\n[LAYER 6] RBAC MANUAL AUDIT (5 Non-Student Roles vs Student Endpoints)")
        for role_name, token in [
            ("TEACHER", tok_tch),
            ("COLLEGE_ADMIN", tok_col),
            ("INDUSTRY", tok_ind),
            ("ALUMNI", tok_alm),
        ]:
            res_d = await client.get("/api/v1/student/dashboard", headers={"Authorization": f"Bearer {token}"})
            assert res_d.status_code == 403, f"Expected 403 for {role_name} on /student/dashboard, got {res_d.status_code}"
            
            res_p = await client.get("/api/v1/student/profile", headers={"Authorization": f"Bearer {token}"})
            assert res_p.status_code == 403, f"Expected 403 for {role_name} on /student/profile, got {res_p.status_code}"
            
            res_u = await client.put("/api/v1/student/profile", json={"first_name": "Test"}, headers={"Authorization": f"Bearer {token}"})
            assert res_u.status_code == 403, f"Expected 403 for {role_name} on PUT /student/profile, got {res_u.status_code}"
            print(f"  [PASS] Role '{role_name}' correctly denied (403 Forbidden) on all Student endpoints.")

        # -------------------------------------------------------------
        # 4. Student Dashboard & Profile Execution for Student A
        # -------------------------------------------------------------
        print("\n[LAYER 4] Testing Student A Dashboard & Profile Endpoints...")
        # Unlinked initial profile
        res_dash_a = await client.get("/api/v1/student/dashboard", headers={"Authorization": f"Bearer {tok_a}"})
        assert res_dash_a.status_code == 200
        dash_a = res_dash_a.json()
        assert dash_a["user"]["email"] == student_a_email.lower()
        assert dash_a["academic_profile"] is None
        assert dash_a["metrics"]["assessed_skills_count"] == 0
        assert dash_a["metrics"]["active_roadmaps_count"] == 0
        assert dash_a["metrics"]["applications_count"] == 0
        assert dash_a["journey_status"]["profile_completed"] is False
        print("  [PASS] Initial Dashboard: returns 200 OK with real zero metrics and unlinked academic profile.")

        # Profile Lookups
        res_insts = await client.get("/api/v1/student/institutions", headers={"Authorization": f"Bearer {tok_a}"})
        assert res_insts.status_code == 200
        assert any(i["id"] == str(inst_id) for i in res_insts.json())
        print(f"  [PASS] GET /api/v1/student/institutions -> 200 OK ({len(res_insts.json())} institutions)")

        res_depts = await client.get(f"/api/v1/student/departments?institution_id={inst_id}", headers={"Authorization": f"Bearer {tok_a}"})
        assert res_depts.status_code == 200
        assert any(d["id"] == str(dept_id) for d in res_depts.json())
        print(f"  [PASS] GET /api/v1/student/departments?institution_id={inst_id} -> 200 OK ({len(res_depts.json())} departments)")

        res_roles = await client.get("/api/v1/student/career-roles", headers={"Authorization": f"Bearer {tok_a}"})
        assert res_roles.status_code == 200
        assert any(r["id"] == str(career_role_id) for r in res_roles.json())
        print(f"  [PASS] GET /api/v1/student/career-roles -> 200 OK ({len(res_roles.json())} career roles)")

        # Update Student A profile
        put_payload = {
            "first_name": "Alice",
            "last_name": "Auditor",
            "phone": "+91 9988776655",
            "bio": "Cloud and DevOps enthusiast.",
            "city": "Bangalore",
            "state": "Karnataka",
            "country": "India",
            "linkedin_url": "https://linkedin.com/in/aliceauditor",
            "github_url": "https://github.com/aliceauditor",
            "website_url": "https://alice.cloud",
            "institution_id": str(inst_id),
            "department_id": str(dept_id),
            "roll_number": f"AUDIT_ROLL_{test_uid}",
            "enrollment_year": 2023,
            "graduation_year": 2027,
            "current_semester": 5,
            "cgpa": 9.40,
            "target_career_role_id": str(career_role_id),
        }
        res_put_a = await client.put("/api/v1/student/profile", json=put_payload, headers={"Authorization": f"Bearer {tok_a}"})
        assert res_put_a.status_code == 200
        prof_a = res_put_a.json()
        assert prof_a["academic_profile"]["roll_number"] == f"AUDIT_ROLL_{test_uid}"
        assert prof_a["academic_profile"]["institution"]["id"] == str(inst_id)
        assert prof_a["academic_profile"]["department"]["id"] == str(dept_id)
        assert prof_a["academic_profile"]["target_career_role"]["id"] == str(career_role_id)
        assert prof_a["is_profile_complete"] is True
        print(f"  [PASS] PUT /api/v1/student/profile -> 200 OK (Academic profile linked: roll={f'AUDIT_ROLL_{test_uid}'})")

        # -------------------------------------------------------------
        # 5. IDOR & Data Isolation Audit (Layer 5)
        # -------------------------------------------------------------
        print("\n[LAYER 5] REAL STUDENT DATA ISOLATION / IDOR CHECK")
        res_prof_b = await client.get("/api/v1/student/profile", headers={"Authorization": f"Bearer {tok_b}"})
        assert res_prof_b.status_code == 200
        prof_b = res_prof_b.json()
        assert prof_b["user"]["email"] == student_b_email.lower()
        assert prof_b["user"]["profile"]["first_name"] == "Bob"
        assert prof_b["academic_profile"] is None # Student B has not set up profile
        assert prof_b["is_profile_complete"] is False

        res_dash_b = await client.get("/api/v1/student/dashboard", headers={"Authorization": f"Bearer {tok_b}"})
        assert res_dash_b.status_code == 200
        dash_b = res_dash_b.json()
        assert dash_b["academic_profile"] is None
        assert dash_b["journey_status"]["profile_completed"] is False
        print("  [PASS] Student B receives strictly Student B's own records (zero leak of Student A data).")

        # -------------------------------------------------------------
        # 6. Profile Security Audit (Layer 7 - Protected Fields Modification)
        # -------------------------------------------------------------
        print("\n[LAYER 7] PROFILE SECURITY AUDIT (Attempting Protected Fields Modification)")
        # Attempt to inject role, is_active, is_verified, id, password in PUT /student/profile
        malicious_payload = {
            "first_name": "AliceHacked",
            "role": "SUPER_ADMIN",
            "is_active": False,
            "is_verified": True,
            "id": str(uuid.uuid4()),
            "hashed_password": "HackedPasswordHash",
            "password": "HackedPassword",
        }
        res_malicious = await client.put("/api/v1/student/profile", json=malicious_payload, headers={"Authorization": f"Bearer {tok_a}"})
        assert res_malicious.status_code == 200
        
        # Verify directly in PostgreSQL that role, is_active, is_verified, and password were NOT modified!
        with sync_conn.cursor() as cur:
            cur.execute("SELECT role, is_active, is_verified, hashed_password FROM users WHERE email = %s;", (student_a_email.lower(),))
            row = cur.fetchone()
            assert row[0] == "STUDENT", f"Role was tampered! Expected STUDENT, got {row[0]}"
            assert row[1] is True, f"is_active was tampered! Expected True, got {row[1]}"
            assert row[2] is False, f"is_verified was tampered! Expected False, got {row[2]}"
            assert not row[3].startswith("Hacked"), "Password was tampered!"
            print("  [PASS] Protected fields (role, is_active, is_verified, password) are completely immune to tampering via PUT /student/profile.")

        # -------------------------------------------------------------
        # 7. Direct PostgreSQL Record Verification (Layer 3)
        # -------------------------------------------------------------
        print("\n[LAYER 3] DIRECT POSTGRESQL RECORD RELATIONSHIPS CHECK")
        with sync_conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    u.email, u.role, p.first_name, p.phone, s.roll_number, s.cgpa, s.current_semester,
                    i.name, d.name, c.title
                FROM users u
                JOIN user_profiles p ON u.id = p.user_id
                JOIN students s ON u.id = s.user_id
                JOIN institutions i ON s.institution_id = i.id
                JOIN departments d ON s.department_id = d.id
                JOIN career_roles c ON s.target_career_role_id = c.id
                WHERE u.email = %s;
            """, (student_a_email.lower(),))
            row = cur.fetchone()
            assert row is not None, "PostgreSQL query returned no record for Student A!"
            print(f"  [PASS] Database state verified:")
            print(f"         User Email: {row[0]}")
            print(f"         Role: {row[1]}")
            print(f"         First Name: {row[2]}")
            print(f"         Phone: {row[3]}")
            print(f"         Roll Number: {row[4]}")
            print(f"         CGPA: {row[5]}")
            print(f"         Semester: {row[6]}")
            print(f"         Institution: {row[7]}")
            print(f"         Department: {row[8]}")
            print(f"         Target Career Role: {row[9]}")

    sync_conn.close()
    print("\n" + "=" * 80)
    print("ALL AUDIT LAYERS EXECUTED SUCCESSFULLY WITH FULL CONFORMANCE!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_phase_3_1_deep_audit())
