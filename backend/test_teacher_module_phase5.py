import asyncio
import uuid
import sys
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import async_session_maker
from app.core.security import hash_password, create_access_token
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Teacher, Student
from app.models.training import TrainingProgram, TrainingEnrollment
from app.models.mentorship import MentorConnection, MentorshipSession
from app.models.community import Activity
from app.models.careers import CareerRole, SkillGap
from app.models.skills import Skill
from app.models.placements import PlacementRecord

# Test execution runner
async def run_teacher_module_tests():
    print("================================================================================")
    print("STARTING MODULE 05 — TEACHER / ACADEMICIAN AUTOMATED TEST SUITE")
    print("================================================================================")

    async with async_session_maker() as db:
        # 1. Setup Test Fixture Entities in PostgreSQL
        prefix = f"test_t5_{uuid.uuid4().hex[:6]}"

        # Create Institution A
        inst_a = Institution(
            name=f"{prefix} Institution Alpha",
            code=f"INST_{prefix}_A",
            institution_type="AUTONOMOUS_COLLEGE",
            city="Tech City",
            state="Tech State",
            country="India"
        )
        db.add(inst_a)

        # Create Institution B (Foreign)
        inst_b = Institution(
            name=f"{prefix} Institution Beta Foreign",
            code=f"INST_{prefix}_B",
            institution_type="UNIVERSITY",
            city="Foreign City",
            state="Foreign State",
            country="India"
        )
        db.add(inst_b)
        await db.flush()

        # Create Department A1 (Dept A under Inst A)
        dept_a1 = Department(
            institution_id=inst_a.id,
            name="Computer Engineering",
            code=f"DEPT_{prefix}_CS"
        )
        db.add(dept_a1)

        # Create Department A2 (Dept B under Inst A)
        dept_a2 = Department(
            institution_id=inst_a.id,
            name="Electrical Engineering",
            code=f"DEPT_{prefix}_EE"
        )
        db.add(dept_a2)

        # Create Department B1 (Dept under Inst B)
        dept_b1 = Department(
            institution_id=inst_b.id,
            name="Mechanical Engineering",
            code=f"DEPT_{prefix}_ME"
        )
        db.add(dept_b1)
        await db.flush()

        # Create User & Teacher A (Dept A1)
        u_teacher_a = User(
            email=f"teacher_a_{prefix}@test.com",
            username=f"teacher_a_{prefix}",
            hashed_password=hash_password("Password123!"),
            role="TEACHER",
            is_active=True,
            is_verified=True
        )
        db.add(u_teacher_a)
        await db.flush()

        p_teacher_a = UserProfile(
            user_id=u_teacher_a.id,
            first_name="Teacher",
            last_name="Alpha",
            bio="CS Professor"
        )
        db.add(p_teacher_a)

        t_teacher_a = Teacher(
            user_id=u_teacher_a.id,
            institution_id=inst_a.id,
            department_id=dept_a1.id,
            designation="Associate Professor",
            employee_id=f"EMP_{prefix}_A",
            specialization="Algorithms, AI",
            is_trainer=True
        )
        db.add(t_teacher_a)

        # Create User & Teacher B (Dept A2)
        u_teacher_b = User(
            email=f"teacher_b_{prefix}@test.com",
            username=f"teacher_b_{prefix}",
            hashed_password=hash_password("Password123!"),
            role="TEACHER",
            is_active=True,
            is_verified=True
        )
        db.add(u_teacher_b)
        await db.flush()

        p_teacher_b = UserProfile(
            user_id=u_teacher_b.id,
            first_name="Teacher",
            last_name="Beta",
            bio="EE Professor"
        )
        db.add(p_teacher_b)

        t_teacher_b = Teacher(
            user_id=u_teacher_b.id,
            institution_id=inst_a.id,
            department_id=dept_a2.id,
            designation="Assistant Professor",
            employee_id=f"EMP_{prefix}_B",
            specialization="Circuits",
            is_trainer=False
        )
        db.add(t_teacher_b)

        # Create Inactive Teacher
        u_teacher_inactive = User(
            email=f"teacher_inact_{prefix}@test.com",
            username=f"teacher_inact_{prefix}",
            hashed_password=hash_password("Password123!"),
            role="TEACHER",
            is_active=False,
            is_verified=True
        )
        db.add(u_teacher_inactive)

        # Create Student A1 (Dept A1)
        u_student_a1 = User(
            email=f"student_a1_{prefix}@test.com",
            username=f"student_a1_{prefix}",
            hashed_password=hash_password("Password123!"),
            role="STUDENT",
            is_active=True
        )
        db.add(u_student_a1)
        await db.flush()
        db.add(UserProfile(user_id=u_student_a1.id, first_name="Student", last_name="A1"))

        s_student_a1 = Student(
            user_id=u_student_a1.id,
            institution_id=inst_a.id,
            department_id=dept_a1.id,
            roll_number=f"ROLL_{prefix}_A1",
            enrollment_year=2022,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("8.50")
        )
        db.add(s_student_a1)

        # Create Student A2 (Dept A2)
        u_student_a2 = User(
            email=f"student_a2_{prefix}@test.com",
            username=f"student_a2_{prefix}",
            hashed_password=hash_password("Password123!"),
            role="STUDENT",
            is_active=True
        )
        db.add(u_student_a2)
        await db.flush()
        db.add(UserProfile(user_id=u_student_a2.id, first_name="Student", last_name="A2"))

        s_student_a2 = Student(
            user_id=u_student_a2.id,
            institution_id=inst_a.id,
            department_id=dept_a2.id,
            roll_number=f"ROLL_{prefix}_A2",
            enrollment_year=2022,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("7.20")
        )
        db.add(s_student_a2)

        # Create Other Role Users
        u_admin = User(email=f"admin_{prefix}@test.com", username=f"admin_{prefix}", hashed_password=hash_password("P!"), role="COLLEGE_ADMIN", is_active=True)
        u_industry = User(email=f"ind_{prefix}@test.com", username=f"ind_{prefix}", hashed_password=hash_password("P!"), role="INDUSTRY", is_active=True)
        u_alumni = User(email=f"alum_{prefix}@test.com", username=f"alum_{prefix}", hashed_password=hash_password("P!"), role="ALUMNI", is_active=True)
        db.add_all([u_admin, u_industry, u_alumni])

        await db.commit()

        # Generate Tokens
        token_teacher_a = create_access_token(u_teacher_a.id, "TEACHER")
        token_teacher_b = create_access_token(u_teacher_b.id, "TEACHER")
        token_inactive = create_access_token(u_teacher_inactive.id, "TEACHER")
        token_student = create_access_token(u_student_a1.id, "STUDENT")
        token_admin = create_access_token(u_admin.id, "COLLEGE_ADMIN")
        token_industry = create_access_token(u_industry.id, "INDUSTRY")
        token_alumni = create_access_token(u_alumni.id, "ALUMNI")

        headers_teacher_a = {"Authorization": f"Bearer {token_teacher_a}"}
        headers_teacher_b = {"Authorization": f"Bearer {token_teacher_b}"}
        headers_inactive = {"Authorization": f"Bearer {token_inactive}"}
        headers_student = {"Authorization": f"Bearer {token_student}"}
        headers_admin = {"Authorization": f"Bearer {token_admin}"}
        headers_industry = {"Authorization": f"Bearer {token_industry}"}
        headers_alumni = {"Authorization": f"Bearer {token_alumni}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test 1: GET /api/v1/teacher/dashboard
        print("\n--- Test 1: Teacher Dashboard ---")
        res = await client.get("/api/v1/teacher/dashboard", headers=headers_teacher_a)
        assert res.status_code == 200, f"Dashboard failed: {res.text}"
        data = res.json()
        assert data["designation"] == "Associate Professor"
        assert data["department_name"] == "Computer Engineering"
        assert data["total_department_students"] >= 1
        print("-> PASS: Teacher Dashboard returns 200 OK with correct metrics.")

        # Test 2: GET /api/v1/teacher/profile
        print("\n--- Test 2: Get Teacher Profile ---")
        res = await client.get("/api/v1/teacher/profile", headers=headers_teacher_a)
        assert res.status_code == 200
        data = res.json()
        assert data["first_name"] == "Teacher"
        assert data["employee_id"] == f"EMP_{prefix}_A"
        print("-> PASS: Get Teacher Profile returns 200 OK.")

        # Test 3: PUT /api/v1/teacher/profile
        print("\n--- Test 3: Update Teacher Profile ---")
        update_payload = {
            "first_name": "TeacherUpdated",
            "last_name": "AlphaUpdated",
            "phone": "+919999988888",
            "bio": "Updated CS Bio",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "designation": "Professor & HOD",
            "employee_id": f"EMP_{prefix}_A",
            "specialization": "Distributed Systems",
            "is_trainer": True
        }
        res = await client.put("/api/v1/teacher/profile", headers=headers_teacher_a, json=update_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["first_name"] == "TeacherUpdated"
        assert data["designation"] == "Professor & HOD"
        # Ensure security fields were not modified
        assert data["user_id"] == str(u_teacher_a.id)
        assert data["institution_id"] == str(inst_a.id)
        print("-> PASS: Update Teacher Profile returns 200 OK & respects immutability.")

        # Test 4: GET /api/v1/teacher/students (Department Scoping & Isolation)
        print("\n--- Test 4: Department Student Roster Isolation ---")
        res = await client.get("/api/v1/teacher/students", headers=headers_teacher_a)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["students"][0]["roll_number"] == f"ROLL_{prefix}_A1"
        # Ensure Dept A2 student (Student A2) is NOT present in Dept A1 teacher's roster
        student_rolls = [s["roll_number"] for s in data["students"]]
        assert f"ROLL_{prefix}_A2" not in student_rolls
        print("-> PASS: Department student roster is strictly scoped to teacher's department.")

        # Test 5: POST /api/v1/teacher/training-programs (Valid Workshop Creation)
        print("\n--- Test 5: Create Training Program (Valid Program Type) ---")
        program_payload = {
            "title": f"Workshop on Microservices {prefix}",
            "description": "3-day hands-on workshop on Docker and Kubernetes",
            "program_type": "WORKSHOP",
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=3)),
            "capacity": 25
        }
        res = await client.post("/api/v1/teacher/training-programs", headers=headers_teacher_a, json=program_payload)
        assert res.status_code == 201, f"Failed: {res.text}"
        prog_data = res.json()
        program_id = prog_data["id"]
        assert prog_data["program_type"] == "WORKSHOP"
        assert prog_data["conducted_by_user_id"] == str(u_teacher_a.id)
        print("-> PASS: Create training program (WORKSHOP) returns 201 Created.")

        # Test 6: POST /api/v1/teacher/training-programs (Invalid Program Type Rejection)
        print("\n--- Test 6: Create Training Program (Invalid Program Type) ---")
        bad_type_payload = {
            "title": "Unsupported FDP Course",
            "description": "FDP course",
            "program_type": "FDP_INVALID",
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=3))
        }
        res = await client.post("/api/v1/teacher/training-programs", headers=headers_teacher_a, json=bad_type_payload)
        assert res.status_code == 422
        print("-> PASS: Unsupported program_type rejected with 422 Validation Error.")

        # Test 7: GET /api/v1/teacher/training-programs
        print("\n--- Test 7: List Training Programs ---")
        res = await client.get("/api/v1/teacher/training-programs?scope=my_programs", headers=headers_teacher_a)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1
        print("-> PASS: List training programs returns 200 OK.")

        # Test 8 & 9: Enrollments & Update Student Attendance
        print("\n--- Test 8 & 9: Student Enrollment & Attendance Update ---")
        async with async_session_maker() as db:
            enrollment = TrainingEnrollment(
                training_program_id=uuid.UUID(program_id),
                student_id=s_student_a1.id,
                attendance_percentage=Decimal("0.00"),
                completion_status="ENROLLED"
            )
            db.add(enrollment)
            await db.commit()
            enrollment_id = str(enrollment.id)

        res_enroll = await client.get(f"/api/v1/teacher/training-programs/{program_id}/enrollments", headers=headers_teacher_a)
        assert res_enroll.status_code == 200
        enroll_data = res_enroll.json()
        assert enroll_data["total_enrolled"] == 1

        update_enroll_payload = {
            "attendance_percentage": 90.50,
            "completion_status": "COMPLETED",
            "certificate_url": "https://storage.skilly.edu/certs/cert_1.pdf"
        }
        res_update = await client.put(
            f"/api/v1/teacher/training-programs/{program_id}/enrollments/{enrollment_id}",
            headers=headers_teacher_a,
            json=update_enroll_payload
        )
        assert res_update.status_code == 200
        updated_data = res_update.json()
        assert float(updated_data["attendance_percentage"]) == 90.50
        assert updated_data["completion_status"] == "COMPLETED"
        print("-> PASS: Query enrollments & update attendance returns 200 OK.")

        # Test 10: Same-Institution Cross-Teacher IDOR Protection
        print("\n--- Test 10: Same-Institution Cross-Teacher IDOR Protection ---")
        # GET enrollments by Teacher B (same institution, non-owner) -> 404
        res_idor_get = await client.get(
            f"/api/v1/teacher/training-programs/{program_id}/enrollments",
            headers=headers_teacher_b
        )
        assert res_idor_get.status_code == 404, f"Expected 404 for same-institution non-owner GET, got {res_idor_get.status_code}"

        # PUT enrollment update by Teacher B (same institution, non-owner) -> 404
        res_idor_put = await client.put(
            f"/api/v1/teacher/training-programs/{program_id}/enrollments/{enrollment_id}",
            headers=headers_teacher_b,
            json=update_enroll_payload
        )
        assert res_idor_put.status_code == 404, f"Expected 404 for same-institution non-owner PUT, got {res_idor_put.status_code}"
        print("-> PASS: Same-institution non-owner GET and PUT on program enrollments strictly rejected with 404 Not Found.")

        # Test 11, 12, 13, 14: Mentorship Requests & Session Scheduling
        print("\n--- Test 11, 12, 13, 14: Mentorship Workflow ---")
        async with async_session_maker() as db:
            m_conn = MentorConnection(
                student_id=s_student_a1.id,
                mentor_user_id=u_teacher_a.id,
                status="PENDING",
                request_note="Need academic research guidance"
            )
            db.add(m_conn)
            await db.commit()
            conn_id = str(m_conn.id)

        # GET mentorship requests
        res_m = await client.get("/api/v1/teacher/mentorship/requests", headers=headers_teacher_a)
        assert res_m.status_code == 200
        m_list = res_m.json()
        assert len(m_list) >= 1

        # Teacher B attempts to accept Teacher A's connection -> IDOR 404
        res_m_idor = await client.put(
            f"/api/v1/teacher/mentorship/requests/{conn_id}",
            headers=headers_teacher_b,
            json={"status": "ACCEPTED"}
        )
        assert res_m_idor.status_code == 404
        print("-> PASS: Foreign teacher accepting mentorship request rejected with 404 Not Found (IDOR Protection).")

        # Teacher A accepts connection
        res_m_accept = await client.put(
            f"/api/v1/teacher/mentorship/requests/{conn_id}",
            headers=headers_teacher_a,
            json={"status": "ACCEPTED"}
        )
        assert res_m_accept.status_code == 200
        assert res_m_accept.json()["status"] == "ACCEPTED"

        # Schedule mentorship session
        session_payload = {
            "connection_id": conn_id,
            "topic": "Career Roadmap & Research Paper",
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "duration_minutes": 45,
            "meeting_link": "https://meet.google.com/test-link",
            "session_notes": "Initial discussion"
        }
        res_session = await client.post("/api/v1/teacher/mentorship/sessions", headers=headers_teacher_a, json=session_payload)
        assert res_session.status_code == 201
        assert res_session.json()["topic"] == "Career Roadmap & Research Paper"
        print("-> PASS: Mentorship request accept & session schedule workflow succeeded.")

        # Test 15 & 16: Activity Creation & Listing
        print("\n--- Test 15 & 16: Activities Management ---")
        act_payload = {
            "title": f"DevOps Industry Guest Lecture {prefix}",
            "description": "Guest session by senior DevOps engineer",
            "activity_type": "GUEST_LECTURE",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=5, hours=2)).isoformat(),
            "location_or_url": "Seminar Hall A"
        }
        res_act_create = await client.post("/api/v1/teacher/activities", headers=headers_teacher_a, json=act_payload)
        assert res_act_create.status_code == 201
        assert res_act_create.json()["activity_type"] == "GUEST_LECTURE"

        res_act_list = await client.get("/api/v1/teacher/activities", headers=headers_teacher_a)
        assert res_act_list.status_code == 200
        assert res_act_list.json()["total"] >= 1
        print("-> PASS: Activity creation (GUEST_LECTURE) & listing returns 200 OK.")

        # Test 17: Department Analytics
        print("\n--- Test 17: Department Analytics ---")
        res_analytics = await client.get("/api/v1/teacher/analytics/department", headers=headers_teacher_a)
        assert res_analytics.status_code == 200
        an_data = res_analytics.json()
        assert "cgpa_distribution" in an_data
        assert "placed_students_count" in an_data
        print("-> PASS: Department analytics returns 200 OK.")

        # Test 18: Unauthenticated Access Rejection (401)
        print("\n--- Test 18: Unauthenticated Access Rejection ---")
        res_unauth = await client.get("/api/v1/teacher/dashboard")
        assert res_unauth.status_code == 401
        print("-> PASS: Unauthenticated access rejected with 401 Unauthorized.")

        # Test 19: Non-Teacher RBAC Rejections (403)
        print("\n--- Test 19: Non-Teacher RBAC Rejections ---")
        for h, r_name in [(headers_student, "Student"), (headers_admin, "College Admin"), (headers_industry, "Industry"), (headers_alumni, "Alumni")]:
            res_rbac = await client.get("/api/v1/teacher/dashboard", headers=h)
            assert res_rbac.status_code == 403, f"Role {r_name} was not blocked with 403! Status: {res_rbac.status_code}"
        print("-> PASS: All non-TEACHER roles (Student, Admin, Industry, Alumni) rejected with 403 Forbidden.")

        # Test 20: Inactive Account Rejection
        print("\n--- Test 20: Inactive Account Rejection ---")
        res_inact = await client.get("/api/v1/teacher/dashboard", headers=headers_inactive)
        assert res_inact.status_code in (401, 403)
        print("-> PASS: Inactive teacher account rejected with 401/403.")

        # Test 21: Malformed Payload & Date Rejection (400 / 422)
        print("\n--- Test 21: Payload Validation Rejections ---")
        bad_dates_payload = {
            "title": "Bad Dates Program",
            "description": "Invalid dates",
            "program_type": "WORKSHOP",
            "start_date": "2026-10-10",
            "end_date": "2026-10-05"  # end_date before start_date
        }
        res_bad_dates = await client.post("/api/v1/teacher/training-programs", headers=headers_teacher_a, json=bad_dates_payload)
        assert res_bad_dates.status_code == 400
        print("-> PASS: Invalid date range rejected with 400 Bad Request.")

    print("\n================================================================================")
    print("ALL MODULE 05 AUTOMATED TESTS PASSED SUCCESSFULLY!")
    print("================================================================================")

if __name__ == "__main__":
    asyncio.run(run_teacher_module_tests())
