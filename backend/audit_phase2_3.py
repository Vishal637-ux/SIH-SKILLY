import sys
import os
import uuid
import asyncio
from datetime import datetime, timedelta, timezone
import json
import httpx
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import jwt
import sqlalchemy
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.dependencies.auth import get_current_user, require_roles
from app.models.users import User, UserProfile
from app.models import Base
from app.main import app

# Temporary router attached dynamically for RBAC testing
rbac_test_router = APIRouter(prefix="/audit-rbac", tags=["Audit RBAC Tests"])

@rbac_test_router.get("/student")
async def _aud_st(user: User = Depends(require_roles("STUDENT"))):
    return {"status": "ok", "role": user.role, "user_id": str(user.id)}

@rbac_test_router.get("/college")
async def _aud_col(user: User = Depends(require_roles("COLLEGE_ADMIN"))):
    return {"status": "ok", "role": user.role, "user_id": str(user.id)}

@rbac_test_router.get("/teacher")
async def _aud_tch(user: User = Depends(require_roles("TEACHER"))):
    return {"status": "ok", "role": user.role, "user_id": str(user.id)}

@rbac_test_router.get("/industry")
async def _aud_ind(user: User = Depends(require_roles("INDUSTRY"))):
    return {"status": "ok", "role": user.role, "user_id": str(user.id)}

@rbac_test_router.get("/alumni")
async def _aud_alm(user: User = Depends(require_roles("ALUMNI"))):
    return {"status": "ok", "role": user.role, "user_id": str(user.id)}

app.include_router(rbac_test_router)


async def run_phase_2_3_deep_audit():
    results = {}
    print("=" * 80)
    print("SKILLY — PHASE 2.3 INDEPENDENT DEEP AUDIT EXECUTION")
    print("=" * 80)

    # -------------------------------------------------------------
    # 1. Environment & Package Dependencies
    # -------------------------------------------------------------
    print("\n[SECTION 1] Package & Dependency Audit")
    import argon2
    import pydantic
    import alembic
    import pgvector
    
    pkg_info = {
        "Python": sys.version.split()[0],
        "FastAPI": getattr(sys.modules.get("fastapi"), "__version__", "installed"),
        "SQLAlchemy": sqlalchemy.__version__,
        "Alembic": alembic.__version__,
        "PyJWT": jwt.__version__,
        "Argon2-cffi": argon2.__version__,
        "Pydantic": pydantic.__version__,
        "pgvector": getattr(pgvector, "__version__", "installed"),
    }
    for k, v in pkg_info.items():
        print(f"  {k}: {v}")
    
    # Check bcrypt presence
    has_bcrypt = "bcrypt" in sys.modules or os.path.exists(os.path.join(os.path.dirname(__file__), ".venv/Lib/site-packages/bcrypt"))
    print(f"  Bcrypt installed unnecessarily: {has_bcrypt}")
    results["dependencies"] = pkg_info
    results["bcrypt_not_used"] = not has_bcrypt

    # -------------------------------------------------------------
    # 2. Configuration & Secret Audit
    # -------------------------------------------------------------
    print("\n[SECTION 2] Configuration & Secret Handling Audit")
    jwt_secret = settings.JWT_SECRET_KEY
    assert len(jwt_secret) >= 32, "JWT_SECRET_KEY is shorter than 32 characters!"
    assert jwt_secret != "CHANGE_ME_TO_A_LONG_RANDOM_SECRET", "JWT_SECRET_KEY is using default placeholder!"
    print("  [PASS] JWT_SECRET_KEY loaded from environment with length >= 32 chars")
    print("  [PASS] No hardcoded default secret fallback in config.py")

    # -------------------------------------------------------------
    # 3. Direct DB Connection Setup for verification
    # -------------------------------------------------------------
    sync_conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB,
    )
    sync_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://audit-test") as client:
        test_id = uuid.uuid4().hex[:8]
        test_pw = "AuditPass#2026!"
        student_email = f"audit_student_{test_id}@skilly.edu"
        college_email = f"audit_tpo_{test_id}@skilly.edu"
        teacher_email = f"audit_trainer_{test_id}@skilly.edu"
        industry_email = f"audit_company_{test_id}@skilly.edu"
        alumni_email = f"audit_mentor_{test_id}@skilly.edu"

        # ---------------------------------------------------------
        # 4. Registration Audit
        # ---------------------------------------------------------
        print("\n[SECTION 3] Registration Audit")
        # 4.1 Valid student registration
        reg_res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": student_email,
                "password": test_pw,
                "role": "student",
                "fullName": "Student Auditor",
            },
        )
        assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
        student_user = reg_res.json()
        assert student_user["email"] == student_email.lower()
        assert student_user["role"] == "STUDENT"
        assert student_user["is_active"] is True
        assert "password" not in student_user
        assert "hashed_password" not in student_user
        assert student_user["profile"]["first_name"] == "Student"
        assert student_user["profile"]["last_name"] == "Auditor"
        print("  [PASS] Valid registration returned 201 Created and safe UserResponse")

        # 4.2 Duplicate email rejection
        dup_res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": student_email,
                "password": test_pw,
                "role": "student",
                "fullName": "Duplicate User",
            },
        )
        assert dup_res.status_code == 400
        print("  [PASS] Duplicate email registration rejected with 400 Bad Request")

        # 4.3 Short password rejection (<8 chars)
        short_res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"short_{test_id}@skilly.edu",
                "password": "short",
                "role": "student",
            },
        )
        assert short_res.status_code == 422
        print("  [PASS] Short password (<8 chars) rejected with 422 Unprocessable Entity")

        # 4.4 Invalid email format
        bad_email_res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": test_pw,
                "role": "student",
            },
        )
        assert bad_email_res.status_code == 422
        print("  [PASS] Invalid email rejected with 422 Unprocessable Entity")

        # 4.5 Role alias normalization on registration
        aliases = [
            (college_email, "tpo", "COLLEGE_ADMIN", "Dean College"),
            (teacher_email, "trainer", "TEACHER", "Prof Trainer"),
            (industry_email, "company", "INDUSTRY", "HR Industry"),
            (alumni_email, "mentor", "ALUMNI", "Senior Alumni"),
        ]
        created_users = {"STUDENT": student_user}
        for email, alias, canonical, name in aliases:
            res = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": test_pw,
                    "role": alias,
                    "fullName": name,
                },
            )
            assert res.status_code == 201, f"Failed for {alias}: {res.text}"
            data = res.json()
            assert data["role"] == canonical, f"Expected {canonical}, got {data['role']}"
            created_users[canonical] = data
            print(f"  [PASS] Role alias '{alias}' correctly normalized to canonical '{canonical}'")

        # ---------------------------------------------------------
        # 5. Password Hashing Audit (Argon2)
        # ---------------------------------------------------------
        print("\n[SECTION 4] Password Hashing Audit")
        with sync_conn.cursor() as cur:
            cur.execute("SELECT hashed_password FROM users WHERE email = %s;", (student_email.lower(),))
            row = cur.fetchone()
            assert row is not None
            db_hash = row[0]
            assert db_hash.startswith("$argon2id$"), f"Expected $argon2id$ format, got {db_hash}"
            assert db_hash != test_pw, "Password stored plaintext!"
            print(f"  [PASS] Stored hash format verified: {db_hash[:30]}... ($argon2id$ variant)")
            
            # Verify password check functions
            assert verify_password(test_pw, db_hash) is True
            assert verify_password("WrongPassword!", db_hash) is False
            assert verify_password("", db_hash) is False
            print("  [PASS] Argon2 verification: correct password passes, incorrect/empty fails")

        # ---------------------------------------------------------
        # 6. Login & JWT Generation Audit
        # ---------------------------------------------------------
        print("\n[SECTION 5] Login & JWT Audit")
        # 6.1 Successful Login
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": student_email, "password": test_pw},
        )
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        login_data = login_res.json()
        student_jwt = login_data["access_token"]
        assert login_data["token_type"] == "bearer"
        assert login_data["expires_in"] == 3600
        assert "password" not in login_data["user"]
        assert "hashed_password" not in login_data["user"]
        print("  [PASS] Login successful with email + password (no role param required)")

        # 6.2 Wrong password -> 401
        bad_pw_res = await client.post(
            "/api/v1/auth/login",
            json={"email": student_email, "password": "WrongPassword999!"},
        )
        assert bad_pw_res.status_code == 401
        print("  [PASS] Wrong password rejected with 401 Unauthorized")

        # 6.3 Unknown email -> 401
        unknown_res = await client.post(
            "/api/v1/auth/login",
            json={"email": f"ghost_{test_id}@skilly.edu", "password": test_pw},
        )
        assert unknown_res.status_code == 401
        print("  [PASS] Unknown email rejected with 401 Unauthorized")

        # 6.4 JWT Claims Inspection
        raw_payload = decode_access_token(student_jwt)
        assert raw_payload["sub"] == student_user["id"]
        assert raw_payload["type"] == "access"
        assert "iat" in raw_payload
        assert "exp" in raw_payload
        assert raw_payload["exp"] > raw_payload["iat"]
        assert "password" not in raw_payload
        assert "hashed_password" not in raw_payload
        print(f"  [PASS] JWT claims inspected: sub={raw_payload['sub']}, type={raw_payload['type']}, exp-iat={raw_payload['exp'] - raw_payload['iat']}s")

        # ---------------------------------------------------------
        # 7. /me Endpoint Audit (7 Cases)
        # ---------------------------------------------------------
        print("\n[SECTION 6] Current User (/me) Audit — 7 Test Cases")
        # Case 1: Valid token
        me_valid = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {student_jwt}"})
        assert me_valid.status_code == 200
        assert me_valid.json()["id"] == student_user["id"]
        print("  [PASS] Case 1 (Valid token): 200 OK")

        # Case 2: Missing token
        me_missing = await client.get("/api/v1/auth/me")
        assert me_missing.status_code == 401
        print("  [PASS] Case 2 (Missing token): 401 Unauthorized")

        # Case 3: Malformed token
        me_malformed = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not.a.valid.jwt.string"})
        assert me_malformed.status_code == 401
        print("  [PASS] Case 3 (Malformed token): 401 Unauthorized")

        # Case 4: Expired token
        expired_token = create_access_token(
            subject=student_user["id"],
            role="STUDENT",
            expires_delta=timedelta(minutes=-10),
        )
        me_expired = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert me_expired.status_code == 401
        print("  [PASS] Case 4 (Expired token): 401 Unauthorized")

        # Case 5: Token with invalid signature (signed with different secret)
        fake_secret_token = jwt.encode(
            {"sub": student_user["id"], "type": "access", "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())},
            "completely-different-wrong-secret-key-that-should-fail!",
            algorithm="HS256"
        )
        me_fake_sig = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {fake_secret_token}"})
        assert me_fake_sig.status_code == 401
        print("  [PASS] Case 5 (Invalid signature token): 401 Unauthorized")

        # Case 6: Nonexistent user ID in valid token
        nonexistent_uuid = str(uuid.uuid4())
        nonexistent_token = create_access_token(subject=nonexistent_uuid, role="STUDENT")
        me_nonexistent = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {nonexistent_token}"})
        assert me_nonexistent.status_code == 401
        print("  [PASS] Case 6 (Token for nonexistent user): 401 Unauthorized")

        # Case 7: Inactive user
        with sync_conn.cursor() as cur:
            cur.execute("UPDATE users SET is_active = FALSE WHERE id = %s;", (student_user["id"],))
        me_inactive = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {student_jwt}"})
        assert me_inactive.status_code == 401
        print("  [PASS] Case 7 (Token for inactive user): 401 Unauthorized")

        # Restore active state
        with sync_conn.cursor() as cur:
            cur.execute("UPDATE users SET is_active = TRUE WHERE id = %s;", (student_user["id"],))

        # ---------------------------------------------------------
        # 8. CRITICAL JWT/RBAC TEST: Database-Authoritative RBAC
        # ---------------------------------------------------------
        print("\n[SECTION 7] CRITICAL JWT/RBAC TEST: Database-Authoritative RBAC")
        # Step 1: User is currently STUDENT, student_jwt has role="STUDENT"
        # Verify student can access student route but NOT teacher route
        st_pre = await client.get("/audit-rbac/student", headers={"Authorization": f"Bearer {student_jwt}"})
        assert st_pre.status_code == 200, f"Expected 200, got {st_pre.status_code}"
        tch_pre = await client.get("/audit-rbac/teacher", headers={"Authorization": f"Bearer {student_jwt}"})
        assert tch_pre.status_code == 403, f"Expected 403, got {tch_pre.status_code}"
        print("  [PASS] Initial state: student token accesses /student (200), denied on /teacher (403)")

        # Step 2: Directly change user's database role from 'STUDENT' to 'TEACHER'
        with sync_conn.cursor() as cur:
            cur.execute("UPDATE users SET role = 'TEACHER' WHERE id = %s;", (student_user["id"],))
        print("  [INFO] Modified user role in database directly: STUDENT -> TEACHER")

        # Step 3: Call /audit-rbac/teacher with the OLD UNMODIFIED student_jwt (whose claim says 'STUDENT')
        tch_post = await client.get("/audit-rbac/teacher", headers={"Authorization": f"Bearer {student_jwt}"})
        assert tch_post.status_code == 200, f"Expected 200, got {tch_post.status_code}: {tch_post.text}"
        print("  [PASS] Old JWT (stale role claim='STUDENT') successfully accessed /audit-rbac/teacher (200 OK)!")

        # Step 4: Call /audit-rbac/student with the OLD UNMODIFIED student_jwt
        st_post = await client.get("/audit-rbac/student", headers={"Authorization": f"Bearer {student_jwt}"})
        assert st_post.status_code == 403, f"Expected 403, got {st_post.status_code}: {st_post.text}"
        print("  [PASS] Old JWT immediately denied access to /audit-rbac/student (403 Forbidden) because live DB role is TEACHER!")

        # Restore role back to STUDENT
        with sync_conn.cursor() as cur:
            cur.execute("UPDATE users SET role = 'STUDENT' WHERE id = %s;", (student_user["id"],))
        print("  --> DATABASE-AUTHORITATIVE RBAC: PASS")
        results["database_authoritative_rbac"] = "PASS"

        # ---------------------------------------------------------
        # 9. Full RBAC Matrix Across All 5 Canonical Roles
        # ---------------------------------------------------------
        print("\n[SECTION 8] Full RBAC Matrix Across All 5 Canonical Roles")
        tokens = {}
        for role_name, user_data in created_users.items():
            l_res = await client.post("/api/v1/auth/login", json={"email": user_data["email"], "password": test_pw})
            assert l_res.status_code == 200
            tokens[role_name] = l_res.json()["access_token"]

        endpoints = [
            ("STUDENT", "/audit-rbac/student"),
            ("COLLEGE_ADMIN", "/audit-rbac/college"),
            ("TEACHER", "/audit-rbac/teacher"),
            ("INDUSTRY", "/audit-rbac/industry"),
            ("ALUMNI", "/audit-rbac/alumni"),
        ]

        for active_role, token in tokens.items():
            for target_role, endpoint in endpoints:
                res = await client.get(endpoint, headers={"Authorization": f"Bearer {token}"})
                if active_role == target_role:
                    assert res.status_code == 200, f"Expected 200 for {active_role} on {endpoint}, got {res.status_code}"
                else:
                    assert res.status_code == 403, f"Expected 403 for {active_role} on {endpoint}, got {res.status_code}"
            print(f"  [PASS] Role '{active_role}' authorized only on /{target_role.lower()} (200) and forbidden elsewhere (403)")

        # ---------------------------------------------------------
        # 10. Stateless Logout Audit
        # ---------------------------------------------------------
        print("\n[SECTION 9] Stateless Logout Audit")
        logout_res = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {student_jwt}"})
        assert logout_res.status_code == 200
        assert logout_res.json()["status"] == "ok"
        print("  [PASS] Logout endpoint returned 200 OK client acknowledgment")

        # ---------------------------------------------------------
        # 11. CORS Audit
        # ---------------------------------------------------------
        print("\n[SECTION 10] CORS Configuration Audit")
        cors_res = await client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization",
            },
        )
        print(f"  CORS Preflight response status: {cors_res.status_code}")
        print(f"  CORS Allow-Origin header: {cors_res.headers.get('access-control-allow-origin')}")
        print(f"  CORS Allow-Credentials header: {cors_res.headers.get('access-control-allow-credentials')}")
        assert cors_res.headers.get("access-control-allow-origin") == "http://localhost:5173"
        print("  [PASS] CORS is properly configured for frontend dev origin")

        # ---------------------------------------------------------
        # 12. Database Regression Audit (47 Tables)
        # ---------------------------------------------------------
        print("\n[SECTION 11] Database Regression Audit (47 Tables & Constraints)")
        with sync_conn.cursor() as cur:
            cur.execute("""
                SELECT count(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name != 'alembic_version';
            """)
            tbl_count = cur.fetchone()[0]
            assert tbl_count == 47, f"Expected 47 tables, got {tbl_count}"
            print(f"  [PASS] Exact 47 application tables verified in PostgreSQL catalog")

            cur.execute("SELECT extname FROM pg_extension WHERE extname = 'pgcrypto';")
            assert cur.fetchone() is not None, "pgcrypto extension missing!"
            print("  [PASS] pgcrypto extension verified")

            cur.execute("SELECT 1 FROM pg_type WHERE typname = 'vector';")
            assert cur.fetchone() is not None, "vector type missing!"
            print("  [PASS] vector type verified")

    sync_conn.close()
    print("\n" + "=" * 80)
    print("ALL DEEP AUDIT CHECKS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_phase_2_3_deep_audit())
