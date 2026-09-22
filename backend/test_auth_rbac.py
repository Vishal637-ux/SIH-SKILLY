import sys
import uuid
import asyncio
from datetime import timedelta
import httpx
import psycopg2
from fastapi import APIRouter, Depends

from app.main import app
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.dependencies.auth import require_roles
from app.models.users import User

# Temporary RBAC test router isolated to test execution
test_rbac_router = APIRouter(prefix="/test-rbac", tags=["Test RBAC Verification"])

@test_rbac_router.get("/student")
async def _test_st(user: User = Depends(require_roles("STUDENT"))):
    return {"access": "granted", "role": user.role}

@test_rbac_router.get("/college")
async def _test_col(user: User = Depends(require_roles("COLLEGE_ADMIN"))):
    return {"access": "granted", "role": user.role}

@test_rbac_router.get("/teacher")
async def _test_tch(user: User = Depends(require_roles("TEACHER"))):
    return {"access": "granted", "role": user.role}

@test_rbac_router.get("/industry")
async def _test_ind(user: User = Depends(require_roles("INDUSTRY"))):
    return {"access": "granted", "role": user.role}

@test_rbac_router.get("/alumni")
async def _test_alm(user: User = Depends(require_roles("ALUMNI"))):
    return {"access": "granted", "role": user.role}

app.include_router(test_rbac_router)


async def test_auth_and_rbac_suite():
    print("\n=======================================================")
    print("STARTING SKILLY PHASE 2.3 AUTHENTICATION & RBAC TEST SUITE")
    print("=======================================================")

    test_uid = uuid.uuid4().hex[:8]
    student_email = f"student_{test_uid}@example.com"
    college_email = f"college_{test_uid}@example.com"
    teacher_email = f"teacher_{test_uid}@example.com"
    industry_email = f"industry_{test_uid}@example.com"
    alumni_email = f"alumni_{test_uid}@example.com"
    password = "SecurePassword123!"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # -------------------------------------------------------------
        # 1. Registration Tests
        # -------------------------------------------------------------
        print("\n[TEST 1] Register valid STUDENT user...")
        res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": student_email,
                "password": password,
                "role": "student",
                "fullName": "Student TestUser",
            },
        )
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        student_data = res.json()
        assert student_data["email"] == student_email.lower()
        assert student_data["role"] == "STUDENT", f"Expected canonical STUDENT, got {student_data['role']}"
        assert student_data["is_active"] is True
        assert "password" not in student_data
        assert "hashed_password" not in student_data
        assert student_data["profile"]["first_name"] == "Student"
        assert student_data["profile"]["last_name"] == "TestUser"
        print(" -> PASS: Student registered with canonical role STUDENT and profile created.")

        # -------------------------------------------------------------
        # 2. Duplicate Email Registration Rejection
        # -------------------------------------------------------------
        print("\n[TEST 2] Duplicate email registration rejection...")
        res_dup = await client.post(
            "/api/v1/auth/register",
            json={
                "email": student_email,
                "password": password,
                "role": "student",
                "fullName": "Duplicate User",
            },
        )
        assert res_dup.status_code == 400, f"Expected 400 Bad Request, got {res_dup.status_code}: {res_dup.text}"
        assert "already exists" in res_dup.json()["detail"]
        print(" -> PASS: Duplicate registration rejected with 400 Bad Request.")

        # -------------------------------------------------------------
        # 3. Registration of other canonical roles via aliases
        # -------------------------------------------------------------
        print("\n[TEST 3] Registering users with role aliases (tpo, trainer, company, mentor)...")
        # College Admin via 'tpo'
        res_col = await client.post("/api/v1/auth/register", json={"email": college_email, "password": password, "role": "tpo", "fullName": "Dean TPO"})
        assert res_col.status_code == 201
        assert res_col.json()["role"] == "COLLEGE_ADMIN"
        print(" -> PASS: Role alias 'tpo' normalized to canonical 'COLLEGE_ADMIN'")

        # Teacher via 'trainer'
        res_teach = await client.post("/api/v1/auth/register", json={"email": teacher_email, "password": password, "role": "trainer", "fullName": "Prof Trainer"})
        assert res_teach.status_code == 201
        assert res_teach.json()["role"] == "TEACHER"
        print(" -> PASS: Role alias 'trainer' normalized to canonical 'TEACHER'")

        # Industry via 'company'
        res_ind = await client.post("/api/v1/auth/register", json={"email": industry_email, "password": password, "role": "company", "fullName": "HR Leader"})
        assert res_ind.status_code == 201
        assert res_ind.json()["role"] == "INDUSTRY"
        print(" -> PASS: Role alias 'company' normalized to canonical 'INDUSTRY'")

        # Alumni via 'mentor'
        res_alum = await client.post("/api/v1/auth/register", json={"email": alumni_email, "password": password, "role": "mentor", "fullName": "Senior Alumni"})
        assert res_alum.status_code == 201
        assert res_alum.json()["role"] == "ALUMNI"
        print(" -> PASS: Role alias 'mentor' normalized to canonical 'ALUMNI'")

        # -------------------------------------------------------------
        # 4. Validation Rejection (Invalid Role, Short Password)
        # -------------------------------------------------------------
        print("\n[TEST 4] Invalid role & short password validation rejection...")
        res_bad_role = await client.post("/api/v1/auth/register", json={"email": f"bad_role_{test_uid}@example.com", "password": password, "role": "SUPER_ADMIN_HACK", "fullName": "Hacker"})
        assert res_bad_role.status_code == 422
        print(" -> PASS: Invalid role rejected with 422 Unprocessable Entity.")

        res_short_pw = await client.post("/api/v1/auth/register", json={"email": f"short_pw_{test_uid}@example.com", "password": "123", "role": "student", "fullName": "Short Pass"})
        assert res_short_pw.status_code == 422
        print(" -> PASS: Short password rejected with 422 Unprocessable Entity.")

        # -------------------------------------------------------------
        # 5. Password Hashing Verification (Argon2)
        # -------------------------------------------------------------
        print("\n[TEST 5] Verifying Argon2 password hash in database...")
        sync_conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname=settings.POSTGRES_DB,
        )
        with sync_conn.cursor() as cur:
            cur.execute("SELECT hashed_password FROM users WHERE email = %s;", (student_email.lower(),))
            row = cur.fetchone()
            assert row is not None
            stored_hash = row[0]
            assert stored_hash.startswith("$argon2id$"), f"Expected Argon2id hash, got: {stored_hash}"
            assert stored_hash != password
            assert verify_password(password, stored_hash) is True
            assert verify_password("WrongPassword!", stored_hash) is False
        print(" -> PASS: Argon2id hash verified directly in database ($argon2id$ prefix, non-plaintext, verified).")

        # -------------------------------------------------------------
        # 6. Login Verification
        # -------------------------------------------------------------
        print("\n[TEST 6] Login with correct & incorrect credentials...")
        # Success
        res_login = await client.post("/api/v1/auth/login", json={"email": student_email, "password": password})
        assert res_login.status_code == 200, f"Login failed: {res_login.text}"
        token_data = res_login.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["expires_in"] == 3600
        assert token_data["user"]["email"] == student_email.lower()
        assert token_data["user"]["role"] == "STUDENT"
        student_token = token_data["access_token"]
        print(" -> PASS: Login successful, returned valid JWT Bearer token and user details.")

        # Wrong password
        res_wrong_pw = await client.post("/api/v1/auth/login", json={"email": student_email, "password": "WrongPassword123!"})
        assert res_wrong_pw.status_code == 401
        print(" -> PASS: Wrong password rejected with 401 Unauthorized.")

        # Unknown user
        res_unknown = await client.post("/api/v1/auth/login", json={"email": f"nonexistent_{test_uid}@example.com", "password": password})
        assert res_unknown.status_code == 401
        print(" -> PASS: Non-existent user rejected with 401 Unauthorized.")

        # -------------------------------------------------------------
        # 7. JWT Claims & Expiration Handling
        # -------------------------------------------------------------
        print("\n[TEST 7] JWT Claims & Expiration validation...")
        payload = decode_access_token(student_token)
        assert "sub" in payload
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
        assert "password" not in payload
        assert "hashed_password" not in payload
        print(" -> PASS: JWT payload contains minimal claims without sensitive data.")

        # Test expired token
        expired_token = create_access_token(
            subject=student_data["id"],
            role="STUDENT",
            expires_delta=timedelta(minutes=-30),
        )
        res_exp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert res_exp.status_code == 401
        assert "expired" in res_exp.json()["detail"].lower()
        print(" -> PASS: Expired token rejected with 401 Unauthorized.")

        # Test invalid token
        res_inv = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.garbage.token"})
        assert res_inv.status_code == 401
        print(" -> PASS: Malformed/invalid token rejected with 401 Unauthorized.")

        # Test missing token
        res_missing = await client.get("/api/v1/auth/me")
        assert res_missing.status_code == 401
        print(" -> PASS: Missing token rejected with 401 Unauthorized.")

        # Test valid token on /me
        res_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {student_token}"})
        assert res_me.status_code == 200
        assert res_me.json()["email"] == student_email.lower()
        assert res_me.json()["profile"]["first_name"] == "Student"
        print(" -> PASS: GET /api/v1/auth/me with valid Bearer token returned current user.")

        # -------------------------------------------------------------
        # 8. Role-Based Access Control (RBAC) Verification
        # -------------------------------------------------------------
        print("\n[TEST 8] Role-Based Access Control (RBAC) backend enforcement...")
        # Obtain tokens for all roles
        col_res = await client.post("/api/v1/auth/login", json={"email": college_email, "password": password})
        col_tok = col_res.json()["access_token"]
        
        teach_res = await client.post("/api/v1/auth/login", json={"email": teacher_email, "password": password})
        teach_tok = teach_res.json()["access_token"]
        
        ind_res = await client.post("/api/v1/auth/login", json={"email": industry_email, "password": password})
        ind_tok = ind_res.json()["access_token"]
        
        alum_res = await client.post("/api/v1/auth/login", json={"email": alumni_email, "password": password})
        alum_tok = alum_res.json()["access_token"]

        # Student accessing endpoints
        res_st_on_st = await client.get("/test-rbac/student", headers={"Authorization": f"Bearer {student_token}"})
        assert res_st_on_st.status_code == 200
        
        res_st_on_col = await client.get("/test-rbac/college", headers={"Authorization": f"Bearer {student_token}"})
        assert res_st_on_col.status_code == 403
        
        res_st_on_tch = await client.get("/test-rbac/teacher", headers={"Authorization": f"Bearer {student_token}"})
        assert res_st_on_tch.status_code == 403
        
        res_st_on_ind = await client.get("/test-rbac/industry", headers={"Authorization": f"Bearer {student_token}"})
        assert res_st_on_ind.status_code == 403
        
        res_st_on_alm = await client.get("/test-rbac/alumni", headers={"Authorization": f"Bearer {student_token}"})
        assert res_st_on_alm.status_code == 403
        print(" -> PASS: STUDENT permitted on student route (200), forbidden on all other role routes (403).")

        # College Admin accessing endpoints
        res_col_on_col = await client.get("/test-rbac/college", headers={"Authorization": f"Bearer {col_tok}"})
        assert res_col_on_col.status_code == 200
        
        res_col_on_st = await client.get("/test-rbac/student", headers={"Authorization": f"Bearer {col_tok}"})
        assert res_col_on_st.status_code == 403
        print(" -> PASS: COLLEGE_ADMIN permitted on college route (200), forbidden on student route (403).")

        # Teacher accessing endpoints
        res_tch_on_tch = await client.get("/test-rbac/teacher", headers={"Authorization": f"Bearer {teach_tok}"})
        assert res_tch_on_tch.status_code == 200
        
        res_tch_on_ind = await client.get("/test-rbac/industry", headers={"Authorization": f"Bearer {teach_tok}"})
        assert res_tch_on_ind.status_code == 403
        print(" -> PASS: TEACHER permitted on teacher route (200), forbidden on industry route (403).")

        # Industry accessing endpoints
        res_ind_on_ind = await client.get("/test-rbac/industry", headers={"Authorization": f"Bearer {ind_tok}"})
        assert res_ind_on_ind.status_code == 200
        
        res_ind_on_tch = await client.get("/test-rbac/teacher", headers={"Authorization": f"Bearer {ind_tok}"})
        assert res_ind_on_tch.status_code == 403
        print(" -> PASS: INDUSTRY permitted on industry route (200), forbidden on teacher route (403).")

        # Alumni accessing endpoints
        res_alm_on_alm = await client.get("/test-rbac/alumni", headers={"Authorization": f"Bearer {alum_tok}"})
        assert res_alm_on_alm.status_code == 200
        
        res_alm_on_st = await client.get("/test-rbac/student", headers={"Authorization": f"Bearer {alum_tok}"})
        assert res_alm_on_st.status_code == 403
        print(" -> PASS: ALUMNI permitted on alumni route (200), forbidden on student route (403).")

        # -------------------------------------------------------------
        # 9. Inactive / Suspended Account Enforcement
        # -------------------------------------------------------------
        print("\n[TEST 9] Inactive / Suspended account enforcement...")
        with sync_conn.cursor() as cur:
            cur.execute("UPDATE users SET is_active = FALSE WHERE email = %s;", (student_email.lower(),))
        sync_conn.commit()

        # Try login
        res_inactive_login = await client.post("/api/v1/auth/login", json={"email": student_email, "password": password})
        assert res_inactive_login.status_code == 401
        assert "inactive" in res_inactive_login.json()["detail"].lower()
        print(" -> PASS: Inactive user login blocked with 401 Unauthorized.")

        # Try accessing /me with previously issued token
        res_inactive_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {student_token}"})
        assert res_inactive_me.status_code == 401
        assert "inactive" in res_inactive_me.json()["detail"].lower()
        print(" -> PASS: Inactive user Bearer token blocked with 401 Unauthorized.")

        # Restore active state for cleanup
        with sync_conn.cursor() as cur:
            cur.execute("UPDATE users SET is_active = TRUE WHERE email = %s;", (student_email.lower(),))
        sync_conn.commit()

        # -------------------------------------------------------------
        # 10. Logout Endpoint
        # -------------------------------------------------------------
        print("\n[TEST 10] Logout endpoint...")
        res_logout = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {student_token}"})
        assert res_logout.status_code == 200
        assert res_logout.json()["status"] == "ok"
        print(" -> PASS: Logout endpoint returned successful client acknowledgement.")

        # -------------------------------------------------------------
        # 11. Database Regression Test (47/47 tables preserved)
        # -------------------------------------------------------------
        print("\n[TEST 11] Database regression check (47/47 tables & extensions)...")
        with sync_conn.cursor() as cur:
            cur.execute("""
                SELECT count(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name != 'alembic_version';
            """)
            table_count = cur.fetchone()[0]
            assert table_count == 47, f"Expected 47 tables, got {table_count}"

            cur.execute("SELECT extname FROM pg_extension WHERE extname = 'pgcrypto';")
            exts = {r[0] for r in cur.fetchall()}
            assert "pgcrypto" in exts, "pgcrypto extension missing"

            cur.execute("SELECT 1 FROM pg_type WHERE typname = 'vector';")
            assert cur.fetchone() is not None, "vector type missing in PostgreSQL"

        sync_conn.close()
        print(" -> PASS: All 47 tables, pgcrypto, vector type verified intact.")

    print("\n=======================================================")
    print("ALL 11 AUTHENTICATION & RBAC TESTS PASSED SUCCESSFULLY!")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(test_auth_and_rbac_suite())
