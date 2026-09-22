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
from app.models.companies import Company, CompanyUser
from app.models.opportunities import Opportunity, OpportunitySkill, Application, ApplicationStatusHistory
from app.models.internships import Internship, InternshipProgress, InternshipEvaluation
from app.models.placements import PlacementRecord, PlacementInteraction
from app.models.skills import Skill, StudentSkill
from app.models.institutions import Institution, Department, Student


async def run_industry_module_tests():
    print("================================================================================")
    print("STARTING MODULE 06 — INDUSTRY / COMPANY AUTOMATED TEST SUITE")
    print("================================================================================")

    async with async_session_maker() as db:
        prefix = f"test_i6_{uuid.uuid4().hex[:6]}"

        # 1. Setup Test Fixture Entities in PostgreSQL
        # Create Company A
        comp_a = Company(
            name=f"{prefix} Enterprise Alpha",
            industry_type="Software Engineering",
            company_size="100-500",
            website="https://alpha.example.com",
            headquarters="San Francisco, CA",
            description="Alpha Enterprise Corporation",
            is_verified=True,
        )
        db.add(comp_a)

        # Create Company B (Foreign for IDOR testing)
        comp_b = Company(
            name=f"{prefix} Enterprise Beta Foreign",
            industry_type="Finance & Fintech",
            company_size="50-100",
            website="https://beta.example.com",
            headquarters="London, UK",
            description="Beta Fintech Corporation",
            is_verified=True,
        )
        db.add(comp_b)
        await db.flush()

        # Create Users
        # User Industry A (Company A)
        u_ind_a = User(
            email=f"ind_a_{prefix}@test.com",
            username=f"ind_a_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="INDUSTRY",
            is_active=True,
            is_verified=True,
        )
        db.add(u_ind_a)

        # User Industry B (Company B)
        u_ind_b = User(
            email=f"ind_b_{prefix}@test.com",
            username=f"ind_b_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="INDUSTRY",
            is_active=True,
            is_verified=True,
        )
        db.add(u_ind_b)

        # Inactive Industry User
        u_ind_inactive = User(
            email=f"ind_inact_{prefix}@test.com",
            username=f"ind_inact_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="INDUSTRY",
            is_active=False,
            is_verified=True,
        )
        db.add(u_ind_inactive)

        # Unassociated Industry User (No CompanyUser record)
        u_ind_unassoc = User(
            email=f"ind_unassoc_{prefix}@test.com",
            username=f"ind_unassoc_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="INDUSTRY",
            is_active=True,
            is_verified=True,
        )
        db.add(u_ind_unassoc)

        # Non-Industry Users (Student, College Admin, Teacher, Alumni)
        u_student = User(
            email=f"student_{prefix}@test.com",
            username=f"student_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="STUDENT",
            is_active=True,
        )
        db.add(u_student)

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

        u_alumni = User(
            email=f"alumni_{prefix}@test.com",
            username=f"alumni_{prefix}",
            hashed_password=hash_password("Pass123!"),
            role="ALUMNI",
            is_active=True,
        )
        db.add(u_alumni)

        await db.flush()

        # Profiles
        db.add(UserProfile(user_id=u_ind_a.id, first_name="Alice", last_name="Recruiter"))
        db.add(UserProfile(user_id=u_ind_b.id, first_name="Bob", last_name="Recruiter"))
        db.add(UserProfile(user_id=u_student.id, first_name="Charlie", last_name="Student"))

        # Company Users
        cu_a = CompanyUser(
            user_id=u_ind_a.id,
            company_id=comp_a.id,
            designation="Senior Recruiter",
            hr_role="RECRUITER",
        )
        db.add(cu_a)

        cu_b = CompanyUser(
            user_id=u_ind_b.id,
            company_id=comp_b.id,
            designation="HR Director",
            hr_role="RECRUITER",
        )
        db.add(cu_b)

        # Institution, Department, Student
        inst = Institution(name=f"{prefix} College", code=f"COL_{prefix}", institution_type="COLLEGE", city="Mumbai", state="Maharashtra")
        db.add(inst)
        await db.flush()

        dept = Department(institution_id=inst.id, name="Computer Science", code=f"CS_{prefix}")
        db.add(dept)
        await db.flush()

        student_entity = Student(
            user_id=u_student.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"ROLL_{prefix}",
            enrollment_year=2022,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("8.75"),
        )
        db.add(student_entity)
        await db.flush()

        # Skills
        skill_python = Skill(name=f"Python_{prefix}", slug=f"python-{prefix}", category="Programming", description="Python lang")
        skill_react = Skill(name=f"React_{prefix}", slug=f"react-{prefix}", category="Web Dev", description="React JS")
        db.add_all([skill_python, skill_react])
        await db.flush()

        # Add skill to student
        db.add(StudentSkill(student_id=student_entity.id, skill_id=skill_python.id, proficiency_level="ADVANCED"))

        # Opportunities
        opp_a = Opportunity(
            company_id=comp_a.id,
            title="Backend Engineer",
            role_type="FULL_TIME",
            description="Build scalable APIs in Python and FastAPI",
            location="Remote",
            is_remote=True,
            stipend_salary="12 LPA",
            openings_count=3,
            application_deadline=datetime.now(timezone.utc) + timedelta(days=30),
            status="OPEN",
        )
        db.add(opp_a)

        opp_b = Opportunity(
            company_id=comp_b.id,
            title="Fintech Analyst",
            role_type="FULL_TIME",
            description="Financial analysis in London",
            location="London",
            is_remote=False,
            stipend_salary="15 LPA",
            openings_count=2,
            application_deadline=datetime.now(timezone.utc) + timedelta(days=30),
            status="OPEN",
        )
        db.add(opp_b)
        await db.flush()

        # Opportunity Skill
        db.add(OpportunitySkill(opportunity_id=opp_a.id, skill_id=skill_python.id, required_proficiency="ADVANCED"))

        # Application from Charlie to Opp A
        app_a = Application(
            opportunity_id=opp_a.id,
            student_id=student_entity.id,
            cover_letter="I am excited to apply for Backend Engineer.",
            current_status="APPLIED",
        )
        db.add(app_a)

        # Application from Charlie to Opp B
        app_b = Application(
            opportunity_id=opp_b.id,
            student_id=student_entity.id,
            cover_letter="I am excited to apply for Fintech Analyst.",
            current_status="APPLIED",
        )
        db.add(app_b)
        await db.flush()

        # Internship under Company A
        internship_a = Internship(
            student_id=student_entity.id,
            company_id=comp_a.id,
            opportunity_id=opp_a.id,
            supervisor_name="Alice Recruiter",
            supervisor_email=u_ind_a.email,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            stipend="25000/mo",
            status="ONGOING",
        )
        db.add(internship_a)

        # Internship under Company B
        internship_b = Internship(
            student_id=student_entity.id,
            company_id=comp_b.id,
            opportunity_id=opp_b.id,
            supervisor_name="Bob Recruiter",
            supervisor_email=u_ind_b.email,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            stipend="30000/mo",
            status="ONGOING",
        )
        db.add(internship_b)
        await db.flush()

        # Placement Interaction under Company A
        interaction_a = PlacementInteraction(
            opportunity_id=opp_a.id,
            interaction_type="INTERVIEW",
            title="Technical Interview Round 1",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=2),
            meeting_link="https://meet.example.com/interview-1",
            conducted_by_user_id=u_ind_a.id,
        )
        db.add(interaction_a)

        # Placement Interaction under Company B
        interaction_b = PlacementInteraction(
            opportunity_id=opp_b.id,
            interaction_type="INTERVIEW",
            title="Fintech Interview Round 1",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
            meeting_link="https://meet.example.com/interview-b",
            conducted_by_user_id=u_ind_b.id,
        )
        db.add(interaction_b)

        await db.commit()

        # Tokens
        token_ind_a = create_access_token(subject=u_ind_a.id, role="INDUSTRY")
        token_ind_b = create_access_token(subject=u_ind_b.id, role="INDUSTRY")
        token_ind_inact = create_access_token(subject=u_ind_inactive.id, role="INDUSTRY")
        token_student = create_access_token(subject=u_student.id, role="STUDENT")
        token_teacher = create_access_token(subject=u_teacher.id, role="TEACHER")
        token_college = create_access_token(subject=u_college.id, role="COLLEGE_ADMIN")
        token_alumni = create_access_token(subject=u_alumni.id, role="ALUMNI")

        headers_a = {"Authorization": f"Bearer {token_ind_a}"}
        headers_b = {"Authorization": f"Bearer {token_ind_b}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        # ----------------------------------------------------------------------
        # TEST 1: Unauthenticated RBAC (401)
        # ----------------------------------------------------------------------
        print("\n[TEST 1] Unauthenticated request to /api/v1/industry/profile -> 401")
        res = await ac.get("/api/v1/industry/profile")
        assert res.status_code == 401, f"Expected 401, got {res.status_code}"
        print(" -> PASSED: 401 Unauthorized")

        # ----------------------------------------------------------------------
        # TEST 2: Non-Industry RBAC (403)
        # ----------------------------------------------------------------------
        print("\n[TEST 2] Non-Industry roles access to /api/v1/industry/dashboard -> 403")
        for role_name, tok in [
            ("STUDENT", token_student),
            ("TEACHER", token_teacher),
            ("COLLEGE_ADMIN", token_college),
            ("ALUMNI", token_alumni),
        ]:
            res = await ac.get("/api/v1/industry/dashboard", headers={"Authorization": f"Bearer {tok}"})
            assert res.status_code == 403, f"Expected 403 for {role_name}, got {res.status_code}"
        print(" -> PASSED: All non-Industry roles rejected with 403 Forbidden")

        # ----------------------------------------------------------------------
        # TEST 3: Inactive Industry user rejection (401)
        # ----------------------------------------------------------------------
        print("\n[TEST 3] Inactive Industry user access -> 401")
        res = await ac.get("/api/v1/industry/profile", headers={"Authorization": f"Bearer {token_ind_inact}"})
        assert res.status_code == 401, f"Expected 401 for inactive user, got {res.status_code}"
        print(" -> PASSED: Inactive account blocked")

        # ----------------------------------------------------------------------
        # TEST 3.5: Unassociated Industry User (No CompanyUser -> Company) -> 404
        # ----------------------------------------------------------------------
        print("\n[TEST 3.5] Unassociated Industry user access -> 404 Not Found")
        token_unassoc = create_access_token(subject=u_ind_unassoc.id, role="INDUSTRY")
        res_unassoc = await ac.get("/api/v1/industry/profile", headers={"Authorization": f"Bearer {token_unassoc}"})
        assert res_unassoc.status_code == 404, f"Expected 404, got {res_unassoc.status_code}"
        print(" -> PASSED: Unassociated Industry user without company context safely rejected with 404")

        # ----------------------------------------------------------------------
        # TEST 4: Company Profile GET & Server-Side Identity Resolution
        # ----------------------------------------------------------------------
        print("\n[TEST 4] GET /api/v1/industry/profile (Company A)")
        res = await ac.get("/api/v1/industry/profile", headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["name"] == f"{prefix} Enterprise Alpha"
        assert data["user_designation"] == "Senior Recruiter"
        print(f" -> PASSED: Company identity resolved: {data['name']} (ID: {data['id']})")

        # ----------------------------------------------------------------------
        # TEST 5: Company Profile PUT
        # ----------------------------------------------------------------------
        print("\n[TEST 5] PUT /api/v1/industry/profile (Update Company A)")
        update_payload = {
            "name": f"{prefix} Enterprise Alpha Updated",
            "industry_type": "Software & AI",
            "company_size": "200-500 employees",
            "website": "https://alpha-updated.example.com",
            "headquarters": "San Jose, CA",
            "description": "Leading AI & Software Enterprise",
            "designation": "Head of Global Talent",
        }
        res = await ac.put("/api/v1/industry/profile", json=update_payload, headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["name"] == f"{prefix} Enterprise Alpha Updated"
        assert data["user_designation"] == "Head of Global Talent"
        print(" -> PASSED: Company profile updated successfully")

        # ----------------------------------------------------------------------
        # TEST 6: Industry Dashboard GET
        # ----------------------------------------------------------------------
        print("\n[TEST 6] GET /api/v1/industry/dashboard (Company A)")
        res = await ac.get("/api/v1/industry/dashboard", headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        dash = res.json()
        assert dash["active_opportunities_count"] >= 1
        assert dash["total_applications_count"] >= 1
        print(f" -> PASSED: Dashboard metrics retrieved (Active Opps: {dash['active_opportunities_count']}, Apps: {dash['total_applications_count']})")

        # ----------------------------------------------------------------------
        # TEST 7: Opportunity Creation & Required Skills
        # ----------------------------------------------------------------------
        print("\n[TEST 7] POST /api/v1/industry/opportunities (Create Opp + Skill)")
        opp_payload = {
            "title": "Frontend React Specialist",
            "role_type": "FULL_TIME",
            "description": "Develop high performance React UI applications on SKILLY platform.",
            "location": "Remote / Hyderabad",
            "is_remote": True,
            "stipend_salary": "10 LPA",
            "duration_months": 12,
            "openings_count": 2,
            "application_deadline": (datetime.now(timezone.utc) + timedelta(days=15)).isoformat(),
            "skills": [
                {
                    "skill_id": str(skill_react.id),
                    "required_proficiency": "INTERMEDIATE",
                    "is_mandatory": True,
                }
            ],
        }
        res = await ac.post("/api/v1/industry/opportunities", json=opp_payload, headers=headers_a)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        new_opp_data = res.json()
        new_opp_id = new_opp_data["id"]
        assert new_opp_data["title"] == "Frontend React Specialist"
        assert len(new_opp_data["required_skills"]) == 1
        print(f" -> PASSED: Opportunity created with ID {new_opp_id}")

        # ----------------------------------------------------------------------
        # TEST 8: Opportunity List GET
        # ----------------------------------------------------------------------
        print("\n[TEST 8] GET /api/v1/industry/opportunities (Company A list)")
        res = await ac.get("/api/v1/industry/opportunities", headers=headers_a)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        opp_list = res.json()
        assert opp_list["total"] >= 2
        print(f" -> PASSED: Retrived {opp_list['total']} opportunities for Company A")

        # ----------------------------------------------------------------------
        # TEST 9: Opportunity Detail GET & Update PUT
        # ----------------------------------------------------------------------
        print("\n[TEST 9] GET & PUT /api/v1/industry/opportunities/{id}")
        res = await ac.get(f"/api/v1/industry/opportunities/{new_opp_id}", headers=headers_a)
        assert res.status_code == 200
        
        upd_opp_payload = {"title": "Frontend React Specialist (Lead)"}
        res_upd = await ac.put(f"/api/v1/industry/opportunities/{new_opp_id}", json=upd_opp_payload, headers=headers_a)
        assert res_upd.status_code == 200
        assert res_upd.json()["title"] == "Frontend React Specialist (Lead)"
        print(" -> PASSED: Opportunity updated successfully")

        # ----------------------------------------------------------------------
        # TEST 10: Cross-Company Opportunity IDOR Rejection
        # ----------------------------------------------------------------------
        print("\n[TEST 10] Cross-Company Opportunity IDOR (Company B -> Company A Opp)")
        res_idor = await ac.get(f"/api/v1/industry/opportunities/{opp_a.id}", headers=headers_b)
        assert res_idor.status_code == 404, f"Expected 404/403, got {res_idor.status_code}"
        
        res_upd_idor = await ac.put(
            f"/api/v1/industry/opportunities/{opp_a.id}",
            json={"title": "Hacked Title"},
            headers=headers_b,
        )
        assert res_upd_idor.status_code == 404, f"Expected 404/403, got {res_upd_idor.status_code}"
        print(" -> PASSED: Cross-Company Opportunity IDOR strictly blocked with 404")

        # ----------------------------------------------------------------------
        # TEST 11: Applications Roster GET & Filtering
        # ----------------------------------------------------------------------
        print("\n[TEST 11] GET /api/v1/industry/applications (Company A apps)")
        res = await ac.get("/api/v1/industry/applications", headers=headers_a)
        assert res.status_code == 200
        apps_data = res.json()
        assert apps_data["total"] >= 1
        app_item_id = apps_data["applications"][0]["id"]
        print(f" -> PASSED: Applications roster retrieved (Count: {apps_data['total']})")

        # ----------------------------------------------------------------------
        # TEST 12: Application Status Update & Append-Only History
        # ----------------------------------------------------------------------
        print("\n[TEST 12] PUT /api/v1/industry/applications/{id}/status & GET /history")
        st_payload = {"status": "SHORTLISTED", "notes": "Candidate profile matched Python requirement."}
        res_st = await ac.put(f"/api/v1/industry/applications/{app_a.id}/status", json=st_payload, headers=headers_a)
        assert res_st.status_code == 200, f"Expected 200, got {res_st.status_code}: {res_st.text}"
        assert res_st.json()["current_status"] == "SHORTLISTED"

        # Check status history
        res_hist = await ac.get(f"/api/v1/industry/applications/{app_a.id}/history", headers=headers_a)
        assert res_hist.status_code == 200
        hist_records = res_hist.json()
        assert len(hist_records) >= 1
        assert hist_records[0]["status"] == "SHORTLISTED"
        print(" -> PASSED: Application status updated and history audit record appended")

        # ----------------------------------------------------------------------
        # TEST 13: Cross-Company Application IDOR Rejection
        # ----------------------------------------------------------------------
        print("\n[TEST 13] Cross-Company Application IDOR (Company B -> Company A Application)")
        res_app_idor = await ac.get(f"/api/v1/industry/applications/{app_a.id}", headers=headers_b)
        assert res_app_idor.status_code == 404, f"Expected 404, got {res_app_idor.status_code}"

        res_app_upd_idor = await ac.put(
            f"/api/v1/industry/applications/{app_a.id}/status",
            json={"status": "REJECTED"},
            headers=headers_b,
        )
        assert res_app_upd_idor.status_code == 404, f"Expected 404, got {res_app_upd_idor.status_code}"
        print(" -> PASSED: Cross-Company Application IDOR strictly blocked")

        # ----------------------------------------------------------------------
        # TEST 14: Internship Supervision & Evaluation
        # ----------------------------------------------------------------------
        print("\n[TEST 14] GET /api/v1/industry/internships & POST evaluation")
        res_int = await ac.get("/api/v1/industry/internships", headers=headers_a)
        assert res_int.status_code == 200
        ints = res_int.json()
        assert len(ints) >= 1

        eval_payload = {
            "technical_rating": 5,
            "soft_skills_rating": 4,
            "punctuality_rating": 5,
            "overall_feedback": "Exceptional intern performance on backend architecture.",
        }
        res_eval = await ac.post(
            f"/api/v1/industry/internships/{internship_a.id}/evaluations",
            json=eval_payload,
            headers=headers_a,
        )
        assert res_eval.status_code == 200, f"Expected 200, got {res_eval.status_code}: {res_eval.text}"
        assert res_eval.json()["technical_rating"] == 5
        print(" -> PASSED: Internship list & evaluation submitted successfully")

        # ----------------------------------------------------------------------
        # TEST 15: Cross-Company Internship IDOR Rejection
        # ----------------------------------------------------------------------
        print("\n[TEST 15] Cross-Company Internship IDOR (Company B -> Company A Internship Eval)")
        res_int_idor = await ac.post(
            f"/api/v1/industry/internships/{internship_a.id}/evaluations",
            json=eval_payload,
            headers=headers_b,
        )
        assert res_int_idor.status_code == 404, f"Expected 404, got {res_int_idor.status_code}"
        print(" -> PASSED: Cross-Company Internship IDOR strictly blocked")

        # ----------------------------------------------------------------------
        # TEST 16: Placement Interaction Creation & Ownership
        # ----------------------------------------------------------------------
        print("\n[TEST 16] POST /api/v1/industry/interactions & GET interactions")
        interaction_payload = {
            "opportunity_id": str(opp_a.id),
            "interaction_type": "INTERVIEW",
            "title": "Technical Round 2 System Design",
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
            "meeting_link": "https://meet.example.com/tech-2",
        }
        res_pi = await ac.post("/api/v1/industry/interactions", json=interaction_payload, headers=headers_a)
        assert res_pi.status_code == 201, f"Expected 201, got {res_pi.status_code}: {res_pi.text}"
        assert res_pi.json()["title"] == "Technical Round 2 System Design"

        res_pi_list = await ac.get("/api/v1/industry/interactions", headers=headers_a)
        assert res_pi_list.status_code == 200
        assert len(res_pi_list.json()) >= 2
        print(" -> PASSED: Recruitment interaction created & retrieved successfully")

        # ----------------------------------------------------------------------
        # TEST 17: Industry Analytics GET
        # ----------------------------------------------------------------------
        print("\n[TEST 17] GET /api/v1/industry/analytics (Company A)")
        res_an = await ac.get("/api/v1/industry/analytics", headers=headers_a)
        assert res_an.status_code == 200, f"Expected 200, got {res_an.status_code}: {res_an.text}"
        an_data = res_an.json()
        assert an_data["total_postings"] >= 2
        assert len(an_data["hiring_funnel"]) >= 5
        print(f" -> PASSED: Industry analytics calculated (Postings: {an_data['total_postings']}, Apps: {an_data['total_applications']})")

    print("\n================================================================================")
    print("MODULE 06 AUTOMATED TEST SUITE PASSED SUCCESSFULLY (17/17 SCENARIOS)")
    print("================================================================================")


if __name__ == "__main__":
    asyncio.run(run_industry_module_tests())
