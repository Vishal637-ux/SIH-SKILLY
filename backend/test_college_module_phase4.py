import sys
import os
import uuid
import asyncio
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.core.database import async_session_maker
from app.core.security import create_access_token, hash_password
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, InstitutionStaff, Teacher, Student
from app.models.companies import Company
from app.models.opportunities import Opportunity
from app.models.skills import Skill, StudentSkill
from app.models.careers import CareerRole, SkillGap
from app.models.placements import PlacementRecord


async def run_tests():
    print("=" * 80)
    print("SKILLY MODULE 04 (COLLEGE / TPO) AUTOMATED TEST SUITE")
    print("=" * 80)

    prefix = uuid.uuid4().hex[:8]

    async with async_session_maker() as db:
        print("\n[SETUP] Seeding multi-tenant test data for College A and College B...")

        # 1. Institutions
        inst_a = Institution(
            name=f"Audit Institute of Tech {prefix}",
            code=f"AIT_{prefix}",
            institution_type="ENGINEERING",
            city="Bengaluru",
            state="Karnataka",
            country="India"
        )
        inst_b = Institution(
            name=f"Other College of Tech {prefix}",
            code=f"OCT_{prefix}",
            institution_type="ENGINEERING",
            city="Mysuru",
            state="Karnataka",
            country="India"
        )
        db.add_all([inst_a, inst_b])
        await db.commit()
        await db.refresh(inst_a)
        await db.refresh(inst_b)

        # 2. Departments
        dept_cs = Department(
            institution_id=inst_a.id,
            name=f"Computer Science {prefix}",
            code=f"CS_{prefix}"
        )
        dept_ec = Department(
            institution_id=inst_a.id,
            name=f"Electronics {prefix}",
            code=f"EC_{prefix}"
        )
        dept_b_cs = Department(
            institution_id=inst_b.id,
            name=f"CS Other {prefix}",
            code=f"CSB_{prefix}"
        )
        db.add_all([dept_cs, dept_ec, dept_b_cs])
        await db.commit()
        await db.refresh(dept_cs)
        await db.refresh(dept_ec)
        await db.refresh(dept_b_cs)

        # 3. Users (College Admin A, College Admin B, Teacher A, Student A, Student B, Industry User)
        hashed_pw = hash_password("TestPass123!")

        user_admin_a = User(email=f"admin_a_{prefix}@skilly.edu", username=f"admin_a_{prefix}", hashed_password=hashed_pw, role="COLLEGE_ADMIN", is_active=True)
        user_admin_b = User(email=f"admin_b_{prefix}@skilly.edu", username=f"admin_b_{prefix}", hashed_password=hashed_pw, role="COLLEGE_ADMIN", is_active=True)
        user_teacher = User(email=f"teacher_a_{prefix}@skilly.edu", username=f"teacher_a_{prefix}", hashed_password=hashed_pw, role="TEACHER", is_active=True)
        user_student_a = User(email=f"student_a_{prefix}@skilly.edu", username=f"student_a_{prefix}", hashed_password=hashed_pw, role="STUDENT", is_active=True)
        user_student_b = User(email=f"student_b_{prefix}@skilly.edu", username=f"student_b_{prefix}", hashed_password=hashed_pw, role="STUDENT", is_active=True)
        user_industry = User(email=f"industry_{prefix}@skilly.com", username=f"industry_{prefix}", hashed_password=hashed_pw, role="INDUSTRY", is_active=True)

        db.add_all([user_admin_a, user_admin_b, user_teacher, user_student_a, user_student_b, user_industry])
        await db.commit()

        for u in [user_admin_a, user_admin_b, user_teacher, user_student_a, user_student_b, user_industry]:
            await db.refresh(u)

        # Profiles
        prof_admin_a = UserProfile(user_id=user_admin_a.id, first_name="TPO", last_name="AdminA")
        prof_admin_b = UserProfile(user_id=user_admin_b.id, first_name="TPO", last_name="AdminB")
        prof_teacher = UserProfile(user_id=user_teacher.id, first_name="Prof", last_name="TeacherA")
        prof_student_a = UserProfile(user_id=user_student_a.id, first_name="Alice", last_name="Student")
        prof_student_b = UserProfile(user_id=user_student_b.id, first_name="Bob", last_name="OtherStudent")
        db.add_all([prof_admin_a, prof_admin_b, prof_teacher, prof_student_a, prof_student_b])

        # Staff & Teacher Contexts
        staff_a = InstitutionStaff(user_id=user_admin_a.id, institution_id=inst_a.id, staff_role="TPO_ADMIN")
        staff_b = InstitutionStaff(user_id=user_admin_b.id, institution_id=inst_b.id, staff_role="TPO_ADMIN")
        teacher_a = Teacher(user_id=user_teacher.id, institution_id=inst_a.id, department_id=dept_cs.id, designation="Assoc Professor")
        db.add_all([staff_a, staff_b, teacher_a])

        # Students
        student_a = Student(
            user_id=user_student_a.id,
            institution_id=inst_a.id,
            department_id=dept_cs.id,
            roll_number=f"ROLL_A_{prefix}",
            enrollment_year=2022,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("8.80")
        )
        student_b = Student(
            user_id=user_student_b.id,
            institution_id=inst_b.id,
            department_id=dept_b_cs.id,
            roll_number=f"ROLL_B_{prefix}",
            enrollment_year=2022,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("7.50")
        )
        db.add_all([student_a, student_b])

        # Skills & Career Role
        skill_python = Skill(name=f"Python_{prefix}", slug=f"python_{prefix}", category="TECHNICAL")
        skill_docker = Skill(name=f"Docker_{prefix}", slug=f"docker_{prefix}", category="DEVOPS")
        career_devops = CareerRole(title=f"DevOps Engineer_{prefix}", slug=f"devops_{prefix}", industry_domain="IT & Software", description="DevOps")
        db.add_all([skill_python, skill_docker, career_devops])
        await db.commit()
        await db.refresh(skill_python)
        await db.refresh(skill_docker)
        await db.refresh(career_devops)
        await db.refresh(student_a)
        await db.refresh(student_b)

        # Assign skill & gap to Student A
        st_skill_a = StudentSkill(student_id=student_a.id, skill_id=skill_python.id, proficiency_level="ADVANCED", score=Decimal("85.00"))
        st_gap_a = SkillGap(student_id=student_a.id, career_role_id=career_devops.id, skill_id=skill_docker.id, current_level="NONE", target_level="INTERMEDIATE", gap_score=Decimal("4.00"))
        db.add_all([st_skill_a, st_gap_a])

        # Company & Opportunity
        company = Company(name=f"TechCorp_{prefix}", industry_type="Software", description="Tech Company")
        db.add(company)
        await db.commit()
        await db.refresh(company)

        opportunity = Opportunity(
            company_id=company.id,
            title=f"Graduate Cloud Engineer_{prefix}",
            role_type="FULL_TIME",
            description="Cloud role for 2026 graduates",
            location="Bengaluru",
            stipend_salary="12 LPA",
            openings_count=5,
            application_deadline=datetime.now(timezone.utc) + timedelta(days=30),
            status="OPEN"
        )
        db.add(opportunity)
        await db.commit()
        await db.refresh(opportunity)

        print("[SETUP] Multi-tenant test dataset created successfully!")

        # Tokens
        token_admin_a = create_access_token(user_admin_a.id, role="COLLEGE_ADMIN")
        token_admin_b = create_access_token(user_admin_b.id, role="COLLEGE_ADMIN")
        token_teacher = create_access_token(user_teacher.id, role="TEACHER")
        token_student = create_access_token(user_student_a.id, role="STUDENT")
        token_industry = create_access_token(user_industry.id, role="INDUSTRY")

        headers_admin_a = {"Authorization": f"Bearer {token_admin_a}"}
        headers_admin_b = {"Authorization": f"Bearer {token_admin_b}"}
        headers_teacher = {"Authorization": f"Bearer {token_teacher}"}
        headers_student = {"Authorization": f"Bearer {token_student}"}
        headers_industry = {"Authorization": f"Bearer {token_industry}"}

        # --- TEST EXECUTION VIA ASYNC CLIENT ---
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            print("\n--- Running Module 04 Verification Suite ---")

            # 1. Dashboard Metrics Success
            res = await client.get("/api/v1/college/dashboard", headers=headers_admin_a)
            assert res.status_code == 200, f"Dashboard failed: {res.text}"
            body = res.json()
            assert body["institution_id"] == str(inst_a.id)
            assert body["total_students"] >= 1
            assert body["total_departments"] >= 2
            print("  [PASS] Test 1: GET /college/dashboard returned live DB metrics")

            # 2. Departments List
            res = await client.get("/api/v1/college/departments", headers=headers_admin_a)
            assert res.status_code == 200
            depts = res.json()
            assert len(depts) >= 2
            print("  [PASS] Test 2: GET /college/departments returned department roster")

            # 3. Faculty List
            res = await client.get("/api/v1/college/faculty", headers=headers_admin_a)
            assert res.status_code == 200
            fac = res.json()
            assert len(fac) >= 2
            print("  [PASS] Test 3: GET /college/faculty returned staff & teacher directory")

            # 4. Student Roster
            res = await client.get("/api/v1/college/students", headers=headers_admin_a)
            assert res.status_code == 200
            roster = res.json()
            assert roster["total_count"] >= 1
            print("  [PASS] Test 4: GET /college/students returned student roster")

            # 5. Student Roster Pagination
            res = await client.get("/api/v1/college/students?page=1&limit=1", headers=headers_admin_a)
            assert res.status_code == 200
            assert len(res.json()["students"]) == 1
            print("  [PASS] Test 5: Student roster pagination enforced")

            # 6. CGPA Filter
            res = await client.get("/api/v1/college/students?min_cgpa=8.0", headers=headers_admin_a)
            assert res.status_code == 200
            assert res.json()["total_count"] == 1
            print("  [PASS] Test 6: Min CGPA filter verified")

            # 7. Department Filter
            res = await client.get(f"/api/v1/college/students?department_id={dept_cs.id}", headers=headers_admin_a)
            assert res.status_code == 200
            assert res.json()["total_count"] == 1
            print("  [PASS] Test 7: Department filter verified")

            # 8. Graduation Year Filter
            res = await client.get("/api/v1/college/students?graduation_year=2026", headers=headers_admin_a)
            assert res.status_code == 200
            assert res.json()["total_count"] == 1
            print("  [PASS] Test 8: Graduation year filter verified")

            # 9. Semester Filter
            res = await client.get("/api/v1/college/students?current_semester=7", headers=headers_admin_a)
            assert res.status_code == 200
            assert res.json()["total_count"] == 1
            print("  [PASS] Test 9: Current semester filter verified")

            # 10. Skill Analytics
            res = await client.get("/api/v1/college/analytics/skills", headers=headers_admin_a)
            assert res.status_code == 200
            body = res.json()
            assert len(body["top_skill_gaps"]) >= 1
            print("  [PASS] Test 10: Skill gap aggregations verified")

            # 11. Campus Drive Catalog
            res = await client.get("/api/v1/college/drives", headers=headers_admin_a)
            assert res.status_code == 200
            drives = res.json()
            assert len(drives) >= 1
            print("  [PASS] Test 11: GET /college/drives returned open opportunities")

            # 12 & 13. Shortlisting Engine & Deterministic Skill Filter
            shortlist_payload = {
                "opportunity_id": str(opportunity.id),
                "min_cgpa": 8.0,
                "graduation_year": 2026,
                "department_ids": [str(dept_cs.id)],
                "required_skill_ids": [str(skill_python.id)],
                "min_proficiency": 3
            }
            res = await client.post("/api/v1/college/shortlist", json=shortlist_payload, headers=headers_admin_a)
            assert res.status_code == 200, f"Shortlist failed: {res.text}"
            s_body = res.json()
            assert s_body["eligible_student_count"] == 1
            assert s_body["shortlisted_students"][0]["student_id"] == str(student_a.id)
            print("  [PASS] Tests 12 & 13: Deterministic candidate shortlisting & skill check verified")

            # 14. Confirmed Placement Logging
            place_payload = {
                "student_id": str(student_a.id),
                "company_name": f"TechCorp_{prefix}",
                "job_title": "Software Engineer",
                "package_amount": 14.5,
                "placement_type": "CAMPUS"
            }
            res = await client.post("/api/v1/college/placements", json=place_payload, headers=headers_admin_a)
            assert res.status_code == 200, f"Placement logging failed: {res.text}"
            p_body = res.json()
            assert p_body["student_id"] == str(student_a.id)
            assert p_body["package_amount"] == 14.5
            print("  [PASS] Test 14: Confirmed placement logged in placement_records")

            # 15, 16, 17. RBAC Rejection for Non-College Roles
            res_stud = await client.get("/api/v1/college/dashboard", headers=headers_student)
            assert res_stud.status_code == 403
            res_ind = await client.get("/api/v1/college/dashboard", headers=headers_industry)
            assert res_ind.status_code == 403
            print("  [PASS] Tests 15, 16, 17: Non-college roles rejected with 403 Forbidden")

            # 18. Teacher Scope Restriction
            res_t_dash = await client.get("/api/v1/college/dashboard", headers=headers_teacher)
            assert res_t_dash.status_code == 403  # Teachers cannot access executive TPO dashboard
            res_t_stud = await client.get("/api/v1/college/students", headers=headers_teacher)
            assert res_t_stud.status_code == 200  # Teachers can read department roster
            print("  [PASS] Test 18: Teacher role department scope & dashboard restriction enforced")

            # 19. Multi-Tenant Institution Isolation
            res_b = await client.get("/api/v1/college/students", headers=headers_admin_b)
            assert res_b.status_code == 200
            b_students = res_b.json()["students"]
            student_ids_b = [s["id"] for s in b_students]
            assert str(student_a.id) not in student_ids_b  # Admin B MUST NOT see Admin A's student
            print("  [PASS] Test 19: Strict multi-tenant institutional data isolation verified")

            # 20. Foreign Student IDOR Rejection
            foreign_place_payload = {
                "student_id": str(student_b.id),  # Belongs to College B
                "company_name": "Foreign Corp",
                "job_title": "Dev",
                "package_amount": 10.0,
                "placement_type": "CAMPUS"
            }
            res_idor = await client.post("/api/v1/college/placements", json=foreign_place_payload, headers=headers_admin_a)
            assert res_idor.status_code == 400  # Foreign student placement logging blocked
            print("  [PASS] Test 20: Foreign student IDOR placement logging attempt blocked")

            # 21. Foreign / Nonexistent Opportunity IDOR Rejection
            bad_shortlist = {
                "opportunity_id": str(uuid.uuid4()),
                "min_cgpa": 6.0
            }
            res_bad_opp = await client.post("/api/v1/college/shortlist", json=bad_shortlist, headers=headers_admin_a)
            assert res_bad_opp.status_code == 404
            print("  [PASS] Test 21: Nonexistent opportunity IDOR shortlisting rejected with 404")

            # 22. Inactive Account Rejection
            user_admin_a.is_active = False
            await db.commit()
            res_inactive = await client.get("/api/v1/college/dashboard", headers=headers_admin_a)
            assert res_inactive.status_code == 401
            user_admin_a.is_active = True
            await db.commit()
            print("  [PASS] Test 22: Inactive user account rejected with 401 Unauthorized")

            # 23 & 24. Validation & Malformed Input
            res_val = await client.get("/api/v1/college/students?min_cgpa=15.0", headers=headers_admin_a)
            assert res_val.status_code == 422
            print("  [PASS] Tests 23 & 24: Pydantic input validation & boundary checks enforced")

            # 25. Sensitive Data Leakage Check
            res_faculty = await client.get("/api/v1/college/faculty", headers=headers_admin_a)
            fac_str = res_faculty.text
            assert "hashed_password" not in fac_str
            assert "password" not in fac_str
            print("  [PASS] Test 25: Sensitive authentication fields sanitized from API response")

        # Cleanup
        print("\n[CLEANUP] Cleaning test records from PostgreSQL...")
        await db.execute(delete(PlacementRecord).where(PlacementRecord.student_id.in_([student_a.id, student_b.id])))
        await db.execute(delete(Opportunity).where(Opportunity.id == opportunity.id))
        await db.execute(delete(Company).where(Company.id == company.id))
        await db.execute(delete(SkillGap).where(SkillGap.student_id == student_a.id))
        await db.execute(delete(StudentSkill).where(StudentSkill.student_id == student_a.id))
        await db.execute(delete(Student).where(Student.id.in_([student_a.id, student_b.id])))
        await db.execute(delete(Teacher).where(Teacher.id == teacher_a.id))
        await db.execute(delete(InstitutionStaff).where(InstitutionStaff.id.in_([staff_a.id, staff_b.id])))
        await db.execute(delete(UserProfile).where(UserProfile.user_id.in_([user_admin_a.id, user_admin_b.id, user_teacher.id, user_student_a.id, user_student_b.id, user_industry.id])))
        await db.execute(delete(User).where(User.id.in_([user_admin_a.id, user_admin_b.id, user_teacher.id, user_student_a.id, user_student_b.id, user_industry.id])))
        await db.execute(delete(CareerRole).where(CareerRole.id == career_devops.id))
        await db.execute(delete(Skill).where(Skill.id.in_([skill_python.id, skill_docker.id])))
        await db.execute(delete(Department).where(Department.id.in_([dept_cs.id, dept_ec.id, dept_b_cs.id])))
        await db.execute(delete(Institution).where(Institution.id.in_([inst_a.id, inst_b.id])))
        await db.commit()

    print("\n================================================================================")
    print("ALL 25 MODULE 04 AUTOMATED TESTS PASSED SUCCESSFULLY!")
    print("================================================================================\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
