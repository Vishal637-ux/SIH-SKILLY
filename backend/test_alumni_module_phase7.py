import asyncio
import uuid
import sys
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport

from sqlalchemy import select, and_

from app.main import app
from app.core.database import async_session_maker
from app.core.security import hash_password, create_access_token
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.mentorship import MentorConnection, MentorshipSession
from app.models.notifications import Notification
from app.models.skills import Skill, StudentSkill
from app.models.careers import CareerRole


async def run_alumni_module_tests():
    print("================================================================================")
    print("STARTING MODULE 07 — ALUMNI / MENTOR AUTOMATED TEST SUITE")
    print("================================================================================")

    async with async_session_maker() as db:
        prefix = f"test_a7_{uuid.uuid4().hex[:6]}"

        # 1. Setup Test Fixture Entities in PostgreSQL
        # Alumni User A (Primary Mentor)
        u_alumni_a = User(
            email=f"alumni_a_{prefix}@test.com",
            username=f"alumni_a_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="ALUMNI",
            is_active=True,
            is_verified=True,
        )
        db.add(u_alumni_a)

        # Alumni User B (Foreign Mentor for IDOR testing)
        u_alumni_b = User(
            email=f"alumni_b_{prefix}@test.com",
            username=f"alumni_b_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="ALUMNI",
            is_active=True,
            is_verified=True,
        )
        db.add(u_alumni_b)

        # Inactive Alumni User
        u_alumni_inact = User(
            email=f"alumni_inact_{prefix}@test.com",
            username=f"alumni_inact_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="ALUMNI",
            is_active=False,
            is_verified=True,
        )
        db.add(u_alumni_inact)

        # Non-ALUMNI Users (Student, Teacher, College Admin, Industry)
        u_student = User(
            email=f"student_{prefix}@test.com",
            username=f"student_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="STUDENT",
            is_active=True,
        )
        db.add(u_student)

        u_student_2 = User(
            email=f"student2_{prefix}@test.com",
            username=f"student2_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="STUDENT",
            is_active=True,
        )
        db.add(u_student_2)

        u_teacher = User(
            email=f"teacher_{prefix}@test.com",
            username=f"teacher_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="TEACHER",
            is_active=True,
        )
        db.add(u_teacher)

        u_college = User(
            email=f"college_{prefix}@test.com",
            username=f"college_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="COLLEGE_ADMIN",
            is_active=True,
        )
        db.add(u_college)

        u_industry = User(
            email=f"industry_{prefix}@test.com",
            username=f"industry_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="INDUSTRY",
            is_active=True,
        )
        db.add(u_industry)

        await db.flush()

        # User Profiles
        db.add(UserProfile(user_id=u_alumni_a.id, first_name="Alex", last_name="Mentor", bio="Senior Staff Architect", city="San Jose", state="CA", country="USA"))
        db.add(UserProfile(user_id=u_alumni_b.id, first_name="Beth", last_name="Mentor", bio="Lead Data Scientist", city="London", state="UK", country="UK"))
        db.add(UserProfile(user_id=u_student.id, first_name="Daniel", last_name="Student", city="Mumbai", state="Maharashtra"))
        db.add(UserProfile(user_id=u_student_2.id, first_name="Emily", last_name="Student", city="Pune", state="Maharashtra"))

        # Institution, Department, Student
        inst = Institution(name=f"{prefix} University", code=f"UNI_{prefix}", institution_type="UNIVERSITY", city="Mumbai", state="Maharashtra")
        db.add(inst)
        await db.flush()

        dept = Department(institution_id=inst.id, name="Computer Science", code=f"CS_{prefix}")
        db.add(dept)
        await db.flush()

        career_role = CareerRole(title=f"Cloud Architect_{prefix}", slug=f"cloud-architect-{prefix}", industry_domain="Engineering", description="Cloud Infra")
        db.add(career_role)
        await db.flush()

        student_entity = Student(
            user_id=u_student.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"ROLL_{prefix}",
            enrollment_year=2022,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("9.10"),
            target_career_role_id=career_role.id,
        )
        db.add(student_entity)

        student_entity_2 = Student(
            user_id=u_student_2.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"ROLL2_{prefix}",
            enrollment_year=2022,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("8.80"),
            target_career_role_id=career_role.id,
        )
        db.add(student_entity_2)
        await db.flush()

        # Skills
        skill_python = Skill(name=f"Python_{prefix}", slug=f"python-{prefix}", category="Programming", description="Python")
        db.add(skill_python)
        await db.flush()
        db.add(StudentSkill(student_id=student_entity.id, skill_id=skill_python.id, proficiency_level="ADVANCED"))

        # Mentor Connection 1: Student -> Mentor A (PENDING)
        conn_pending_a = MentorConnection(
            student_id=student_entity.id,
            mentor_user_id=u_alumni_a.id,
            status="PENDING",
            request_note="Hi Alex, I would love guidance on Distributed Systems!",
        )
        db.add(conn_pending_a)

        # Mentor Connection 2: Student 2 -> Mentor A (ACCEPTED)
        conn_accepted_a = MentorConnection(
            student_id=student_entity_2.id,
            mentor_user_id=u_alumni_a.id,
            status="ACCEPTED",
            request_note="Accepted connection for career mentorship.",
            connected_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
        db.add(conn_accepted_a)

        # Mentor Connection 3: Student -> Mentor B (Foreign for IDOR)
        conn_b = MentorConnection(
            student_id=student_entity.id,
            mentor_user_id=u_alumni_b.id,
            status="PENDING",
            request_note="Hi Beth, requesting mentorship on Data Science!",
        )
        db.add(conn_b)
        await db.flush()

        # Mentorship Session 1 under Connection Accepted A
        sess_a1 = MentorshipSession(
            connection_id=conn_accepted_a.id,
            topic="Cloud Systems & Design Review",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
            duration_minutes=45,
            meeting_link="https://meet.example.com/session-a1",
            session_notes="Focus on microservices design.",
            status="SCHEDULED",
        )
        db.add(sess_a1)

        # Mentorship Session 2 under Connection B (Foreign for IDOR)
        sess_b1 = MentorshipSession(
            connection_id=conn_b.id,
            topic="Data Pipelines & Spark Overview",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=4),
            duration_minutes=60,
            meeting_link="https://meet.example.com/session-b1",
            status="SCHEDULED",
        )
        db.add(sess_b1)

        await db.commit()

        # Generate JWT tokens
        token_alumni_a = create_access_token(subject=u_alumni_a.id, role="ALUMNI")
        token_alumni_b = create_access_token(subject=u_alumni_b.id, role="ALUMNI")
        token_alumni_inact = create_access_token(subject=u_alumni_inact.id, role="ALUMNI")
        token_student = create_access_token(subject=u_student.id, role="STUDENT")
        token_teacher = create_access_token(subject=u_teacher.id, role="TEACHER")
        token_college = create_access_token(subject=u_college.id, role="COLLEGE_ADMIN")
        token_industry = create_access_token(subject=u_industry.id, role="INDUSTRY")

        headers_a = {"Authorization": f"Bearer {token_alumni_a}"}
        headers_b = {"Authorization": f"Bearer {token_alumni_b}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        # ----------------------------------------------------------------------
        # TEST 1: Unauthenticated Access (401)
        # ----------------------------------------------------------------------
        print("\n[TEST 1] Unauthenticated request to /api/v1/alumni/profile -> 401")
        res = await ac.get("/api/v1/alumni/profile")
        assert res.status_code == 401, f"Expected 401, got {res.status_code}"
        print(" -> PASSED: 401 Unauthorized")

        # ----------------------------------------------------------------------
        # TEST 2: Non-ALUMNI RBAC (403)
        # ----------------------------------------------------------------------
        print("\n[TEST 2] Non-ALUMNI roles access to /api/v1/alumni/dashboard -> 403")
        for role_name, tok in [
            ("STUDENT", token_student),
            ("TEACHER", token_teacher),
            ("COLLEGE_ADMIN", token_college),
            ("INDUSTRY", token_industry),
        ]:
            res = await ac.get("/api/v1/alumni/dashboard", headers={"Authorization": f"Bearer {tok}"})
            assert res.status_code == 403, f"Expected 403 for {role_name}, got {res.status_code}"
        print(" -> PASSED: All non-ALUMNI roles rejected with 403 Forbidden")

        # ----------------------------------------------------------------------
        # TEST 3: Inactive ALUMNI user rejection (401)
        # ----------------------------------------------------------------------
        print("\n[TEST 3] Inactive ALUMNI user access -> 401")
        res = await ac.get("/api/v1/alumni/profile", headers={"Authorization": f"Bearer {token_alumni_inact}"})
        assert res.status_code == 401, f"Expected 401 for inactive user, got {res.status_code}"
        print(" -> PASSED: Inactive account blocked")

        # ----------------------------------------------------------------------
        # TEST 4: Alumni Profile GET
        # ----------------------------------------------------------------------
        print("\n[TEST 4] GET /api/v1/alumni/profile (Mentor A)")
        res = await ac.get("/api/v1/alumni/profile", headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["first_name"] == "Alex"
        assert data["email"] == f"alumni_a_{prefix}@test.com"
        print(f" -> PASSED: Profile loaded for {data['first_name']} {data['last_name']}")

        # ----------------------------------------------------------------------
        # TEST 5: Alumni Profile PUT
        # ----------------------------------------------------------------------
        print("\n[TEST 5] PUT /api/v1/alumni/profile (Update Mentor A)")
        upd_payload = {
            "first_name": "Alexander",
            "last_name": "Mentor Principal",
            "bio": "Principal Cloud & Distributed Systems Architect",
            "city": "Seattle",
            "state": "WA",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/alexander-mentor",
        }
        res = await ac.put("/api/v1/alumni/profile", json=upd_payload, headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["first_name"] == "Alexander"
        assert data["city"] == "Seattle"
        print(" -> PASSED: Profile updated successfully")

        # ----------------------------------------------------------------------
        # TEST 6: Mentorship Requests GET
        # ----------------------------------------------------------------------
        print("\n[TEST 6] GET /api/v1/alumni/requests (Mentor A requests)")
        res = await ac.get("/api/v1/alumni/requests", headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        req_data = res.json()
        assert req_data["total"] >= 2
        print(f" -> PASSED: Retrieved {req_data['total']} mentorship requests for Mentor A")

        # ----------------------------------------------------------------------
        # TEST 7: Accept Mentorship Request & Notification Trigger
        # ----------------------------------------------------------------------
        print("\n[TEST 7] PUT /api/v1/alumni/requests/{connection_id} (Accept Pending Request)")
        res = await ac.put(
            f"/api/v1/alumni/requests/{conn_pending_a.id}",
            json={"status": "ACCEPTED"},
            headers=headers_a,
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        assert res.json()["status"] == "ACCEPTED"
        assert res.json()["connected_at"] is not None
        print(" -> PASSED: Request accepted and connected_at set")

        # Verify notification was generated for student
        async with async_session_maker() as verify_db:
            stmt_notif = select(Notification).where(
                and_(Notification.user_id == u_student.id, Notification.notification_type == "MENTORSHIP")
            )
            notif_res = await verify_db.execute(stmt_notif)
            notif = notif_res.scalar_one_or_none()
            assert notif is not None, "Notification should be generated on acceptance"
            print(" -> PASSED: Student notification generated on acceptance")

        # ----------------------------------------------------------------------
        # TEST 8: Reject Mentorship Request
        # ----------------------------------------------------------------------
        print("\n[TEST 8] PUT /api/v1/alumni/requests/{connection_id} (Reject Request)")
        res = await ac.put(
            f"/api/v1/alumni/requests/{conn_b.id}",
            json={"status": "REJECTED"},
            headers=headers_b,
        )
        assert res.status_code == 200
        assert res.json()["status"] == "REJECTED"
        print(" -> PASSED: Request rejected successfully")

        # ----------------------------------------------------------------------
        # TEST 9: Cross-Mentor Connection IDOR Rejection (404)
        # ----------------------------------------------------------------------
        print("\n[TEST 9] Cross-Mentor Connection IDOR (Mentor B -> Mentor A Connection)")
        res_idor = await ac.put(
            f"/api/v1/alumni/requests/{conn_pending_a.id}",
            json={"status": "REJECTED"},
            headers=headers_b,
        )
        assert res_idor.status_code == 404, f"Expected 404, got {res_idor.status_code}"
        print(" -> PASSED: Cross-Mentor connection IDOR blocked with 404 Not Found")

        # ----------------------------------------------------------------------
        # TEST 10: Active Connections GET
        # ----------------------------------------------------------------------
        print("\n[TEST 10] GET /api/v1/alumni/connections (Mentor A active connections)")
        res = await ac.get("/api/v1/alumni/connections", headers=headers_a)
        assert res.status_code == 200
        conns_data = res.json()
        assert conns_data["total"] >= 2
        print(f" -> PASSED: Retrived {conns_data['total']} active connections")

        # ----------------------------------------------------------------------
        # TEST 11: Connection Detail GET
        # ----------------------------------------------------------------------
        print("\n[TEST 11] GET /api/v1/alumni/connections/{connection_id}")
        res = await ac.get(f"/api/v1/alumni/connections/{conn_accepted_a.id}", headers=headers_a)
        assert res.status_code == 200
        conn_detail = res.json()
        assert conn_detail["student"]["first_name"] == "Emily"
        print(" -> PASSED: Connection detail loaded with student context")

        # ----------------------------------------------------------------------
        # TEST 12: Session Creation under Accepted Connection
        # ----------------------------------------------------------------------
        print("\n[TEST 12] POST /api/v1/alumni/sessions (Create Session under Accepted Connection)")
        session_payload = {
            "connection_id": str(conn_accepted_a.id),
            "topic": "System Architecture & Scalability",
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
            "duration_minutes": 60,
            "meeting_link": "https://meet.example.com/architecture-101",
            "session_notes": "Review student system design diagram.",
        }
        res = await ac.post("/api/v1/alumni/sessions", json=session_payload, headers=headers_a)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        new_sess_data = res.json()
        new_sess_id = new_sess_data["id"]
        assert new_sess_data["topic"] == "System Architecture & Scalability"
        print(f" -> PASSED: Mentorship session created with ID {new_sess_id}")

        # ----------------------------------------------------------------------
        # TEST 13: Session Creation Rejection under Unaccepted Connection
        # ----------------------------------------------------------------------
        print("\n[TEST 13] POST /api/v1/alumni/sessions under Rejected Connection -> 400")
        bad_sess_payload = {
            "connection_id": str(conn_b.id),  # conn_b was REJECTED above
            "topic": "Invalid Session",
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "duration_minutes": 45,
        }
        res_bad = await ac.post("/api/v1/alumni/sessions", json=bad_sess_payload, headers=headers_b)
        assert res_bad.status_code == 400, f"Expected 400, got {res_bad.status_code}"
        print(" -> PASSED: Session creation under unaccepted connection rejected with 400")

        # ----------------------------------------------------------------------
        # TEST 14: Cross-Mentor Session IDOR Rejection (404)
        # ----------------------------------------------------------------------
        print("\n[TEST 14] Cross-Mentor Session IDOR (Mentor B -> Mentor A Session)")
        res_sess_idor = await ac.get(f"/api/v1/alumni/sessions/{sess_a1.id}", headers=headers_b)
        assert res_sess_idor.status_code == 404, f"Expected 404, got {res_sess_idor.status_code}"

        res_sess_upd_idor = await ac.put(
            f"/api/v1/alumni/sessions/{sess_a1.id}",
            json={"status": "CANCELLED"},
            headers=headers_b,
        )
        assert res_sess_upd_idor.status_code == 404, f"Expected 404, got {res_sess_upd_idor.status_code}"
        print(" -> PASSED: Cross-Mentor session IDOR strictly blocked with 404")

        # ----------------------------------------------------------------------
        # TEST 15: Session Status Update
        # ----------------------------------------------------------------------
        print("\n[TEST 15] PUT /api/v1/alumni/sessions/{session_id} (Update Status to COMPLETED)")
        res_upd_sess = await ac.put(
            f"/api/v1/alumni/sessions/{sess_a1.id}",
            json={"status": "COMPLETED", "session_notes": "Completed system architecture review."},
            headers=headers_a,
        )
        assert res_upd_sess.status_code == 200
        assert res_upd_sess.json()["status"] == "COMPLETED"
        print(" -> PASSED: Session status updated to COMPLETED")

        # ----------------------------------------------------------------------
        # TEST 16: Alumni Dashboard GET Aggregations
        # ----------------------------------------------------------------------
        print("\n[TEST 16] GET /api/v1/alumni/dashboard (Mentor A)")
        res = await ac.get("/api/v1/alumni/dashboard", headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        dash = res.json()
        assert dash["total_requests_count"] >= 2
        assert dash["active_connections_count"] >= 2
        assert dash["total_sessions_count"] >= 2
        print(f" -> PASSED: Alumni dashboard aggregated (Requests: {dash['total_requests_count']}, Active Connections: {dash['active_connections_count']}, Sessions: {dash['total_sessions_count']})")

    print("\n================================================================================")
    print("MODULE 07 AUTOMATED TEST SUITE PASSED SUCCESSFULLY (16/16 SCENARIOS)")
    print("================================================================================")


if __name__ == "__main__":
    asyncio.run(run_alumni_module_tests())
