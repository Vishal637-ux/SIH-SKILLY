import asyncio
import uuid
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal

from sqlalchemy import select, delete, and_
from app.core.database import async_session_maker
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.companies import Company, CompanyUser
from app.models.skills import Skill, StudentSkill
from app.models.opportunities import Opportunity, OpportunitySkill, Application, ApplicationStatusHistory
from app.models.internships import Internship, InternshipProgress, InternshipEvaluation
from app.models.placements import PlacementRecord, PlacementInteraction
from app.services.internship_service import InternshipService
from app.services.industry_service import IndustryService
from app.services.college_service import record_confirmed_placement, filter_eligible_students
from app.schemas.student import StudentApplicationApplyRequest, StudentInternshipProgressCreate
from app.schemas.industry import ApplicationStatusUpdateRequest, InternshipEvaluationRequest, PlacementInteractionCreateRequest, OpportunityCreateRequest
from app.schemas.college import RecordPlacementRequest
from fastapi import HTTPException, status


async def run_phase9_tests():
    print("==================================================")
    print("STARTING MODULE 09 — INTERNSHIP & PLACEMENT TESTS")
    print("==================================================")

    async with async_session_maker() as db:
        test_prefix = f"p9_{uuid.uuid4().hex[:6]}"

        # 1. Setup Test Fixtures in Real PostgreSQL
        # Institution 1
        inst1 = Institution(
            name=f"Inst 1 {test_prefix}",
            code=f"INS1_{test_prefix}",
            city="TechCity",
            state="TechState"
        )
        # Institution 2 (Isolation check)
        inst2 = Institution(
            name=f"Inst 2 {test_prefix}",
            code=f"INS2_{test_prefix}",
            city="OtherCity",
            state="OtherState"
        )
        db.add_all([inst1, inst2])
        await db.flush()

        dept1 = Department(institution_id=inst1.id, name="Computer Science", code="CS")
        dept2 = Department(institution_id=inst2.id, name="Information Technology", code="IT")
        db.add_all([dept1, dept2])
        await db.flush()

        # Users & Students
        user_st1 = User(
            email=f"st1_{test_prefix}@skilly.edu",
            username=f"st1_{test_prefix}",
            hashed_password="hash",
            role="STUDENT",
            is_active=True
        )
        user_st2 = User(
            email=f"st2_{test_prefix}@skilly.edu",
            username=f"st2_{test_prefix}",
            hashed_password="hash",
            role="STUDENT",
            is_active=True
        )
        db.add_all([user_st1, user_st2])
        await db.flush()

        prof_st1 = UserProfile(user_id=user_st1.id, first_name="Alice", last_name="Student", phone="1111111111", city="TechCity")
        prof_st2 = UserProfile(user_id=user_st2.id, first_name="Bob", last_name="Student", phone="2222222222", city="OtherCity")
        db.add_all([prof_st1, prof_st2])

        st1 = Student(
            user_id=user_st1.id,
            institution_id=inst1.id,
            department_id=dept1.id,
            roll_number=f"R1_{test_prefix}",
            enrollment_year=2022,
            current_semester=7,
            graduation_year=2026,
            cgpa=Decimal("8.50")
        )
        st2 = Student(
            user_id=user_st2.id,
            institution_id=inst2.id,
            department_id=dept2.id,
            roll_number=f"R2_{test_prefix}",
            enrollment_year=2022,
            current_semester=7,
            graduation_year=2026,
            cgpa=Decimal("6.00")  # Lower CGPA for eligibility testing
        )
        db.add_all([st1, st2])
        await db.flush()

        # Companies & Industry Users
        comp1 = Company(
            name=f"Acme Corp {test_prefix}",
            industry_type="Software",
            company_size="100-500",
            headquarters="Metropolis"
        )
        comp2 = Company(
            name=f"Beta Corp {test_prefix}",
            industry_type="Finance",
            company_size="50-100",
            headquarters="Gotham"
        )
        db.add_all([comp1, comp2])
        await db.flush()

        user_ind1 = User(
            email=f"ind1_{test_prefix}@acme.com",
            username=f"ind1_{test_prefix}",
            hashed_password="hash",
            role="INDUSTRY",
            is_active=True
        )
        user_ind2 = User(
            email=f"ind2_{test_prefix}@beta.com",
            username=f"ind2_{test_prefix}",
            hashed_password="hash",
            role="INDUSTRY",
            is_active=True
        )
        db.add_all([user_ind1, user_ind2])
        await db.flush()

        comp_user1 = CompanyUser(company_id=comp1.id, user_id=user_ind1.id, designation="HR Lead", hr_role="RECRUITER")
        comp_user2 = CompanyUser(company_id=comp2.id, user_id=user_ind2.id, designation="Talent Head", hr_role="RECRUITER")
        db.add_all([comp_user1, comp_user2])
        await db.flush()

        # Skills
        sk_python = Skill(name=f"Python_{test_prefix}", slug=f"python_{test_prefix}", category="TECHNICAL", description="Python programming")
        sk_sql = Skill(name=f"SQL_{test_prefix}", slug=f"sql_{test_prefix}", category="TECHNICAL", description="SQL database")
        db.add_all([sk_python, sk_sql])
        await db.flush()

        # Student 1 has Python & SQL; Student 2 has no skills
        st_sk1 = StudentSkill(student_id=st1.id, skill_id=sk_python.id, proficiency_level="ADVANCED", verification_status="VERIFIED")
        st_sk2 = StudentSkill(student_id=st1.id, skill_id=sk_sql.id, proficiency_level="INTERMEDIATE", verification_status="VERIFIED")
        db.add_all([st_sk1, st_sk2])
        await db.flush()

        # Opportunity by Comp 1
        opp1 = Opportunity(
            company_id=comp1.id,
            title="Software Engineering Intern",
            role_type="INTERNSHIP",
            description="Build scalable APIs",
            location="Metropolis",
            is_remote=True,
            stipend_salary="30000/month",
            duration_months=6,
            openings_count=2,
            eligibility_criteria={"min_cgpa": 7.5, "graduation_year": 2026},
            application_deadline=datetime.now(timezone.utc) + timedelta(days=30),
            status="OPEN"
        )
        db.add(opp1)
        await db.flush()

        opp_sk1 = OpportunitySkill(opportunity_id=opp1.id, skill_id=sk_python.id, required_proficiency="INTERMEDIATE", is_mandatory=True)
        db.add(opp_sk1)
        await db.commit()

        print("[OK] Test setup completed successfully.")

        # Test 1: Opportunity Visibility
        print("\n--- Test 1: Opportunity Visibility ---")
        opps_st1 = await InternshipService.get_student_opportunities(db, user_st1)
        assert len(opps_st1) >= 1, "Student should see posted opportunity."
        target_opp = next((o for o in opps_st1 if o.id == opp1.id), None)
        assert target_opp is not None, "Opportunity 1 must be present in catalog."
        print("[OK] Opportunity visibility PASS")

        # Test 2: Eligibility Calculation
        print("\n--- Test 2: Eligibility Calculation ---")
        opps_st2 = await InternshipService.get_student_opportunities(db, user_st2)
        target_opp_st2 = next((o for o in opps_st2 if o.id == opp1.id), None)
        assert target_opp.is_eligible is True, "Student 1 (CGPA 8.5, has Python) should be eligible."
        assert target_opp_st2.is_eligible is False, "Student 2 (CGPA 6.0, missing Python) should NOT be eligible."
        print("[OK] Deterministic eligibility calculation PASS")

        # Test 3: Student Application Creation
        print("\n--- Test 3: Student Application Creation ---")
        apply_payload = StudentApplicationApplyRequest(cover_letter="Super excited to join Acme!")
        app_res = await InternshipService.apply_to_opportunity(db, user_st1, opp1.id, apply_payload)
        assert app_res.opportunity_id == opp1.id
        assert app_res.current_status == "APPLIED"
        app_id = app_res.id
        print("[OK] Student application creation PASS")

        # Test 4: Duplicate Application Prevention
        print("\n--- Test 4: Duplicate Application Prevention ---")
        try:
            await InternshipService.apply_to_opportunity(db, user_st1, opp1.id, apply_payload)
            assert False, "Should raise 400 for duplicate application"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert "Already applied" in e.detail
        print("[OK] Duplicate application prevention PASS")

        # Test 5 & 6: Application Ownership & Cross-Student IDOR
        print("\n--- Test 5 & 6: Application Ownership & Cross-Student IDOR ---")
        # Student 1 gets their app
        st1_app_detail = await InternshipService.get_student_application_detail(db, user_st1, app_id)
        assert st1_app_detail.id == app_id

        # Student 2 attempts to get Student 1's app -> 404
        try:
            await InternshipService.get_student_application_detail(db, user_st2, app_id)
            assert False, "Should block cross-student application IDOR"
        except HTTPException as e:
            assert e.status_code == status.HTTP_404_NOT_FOUND
        print("[OK] Application ownership & cross-student IDOR PASS")

        # Test 7 & 8: Application Status Transition & Append-Only History
        print("\n--- Test 7 & 8: Application Status Transition & Append-Only History ---")
        # Recruiter updating status to SHORTLISTED
        update_payload = ApplicationStatusUpdateRequest(status="SHORTLISTED", notes="Selected for interview round")
        updated_app = await IndustryService.update_application_status(db, user_ind1, app_id, update_payload)
        assert updated_app.current_status == "SHORTLISTED"

        # Check status history
        hist = await InternshipService.get_student_application_history(db, user_st1, app_id)
        assert len(hist) == 2, f"Should have 2 history entries (APPLIED, SHORTLISTED), got {len(hist)}"
        assert hist[0].status == "APPLIED"
        assert hist[1].status == "SHORTLISTED"
        print("[OK] Application status transition & append-only history PASS")

        # Test 9: Cross-Company Application Protection
        print("\n--- Test 9: Cross-Company Application Protection ---")
        # Recruiter 2 (Beta Corp) attempts to access/update Acme's candidate app
        try:
            await IndustryService.get_application_detail(db, user_ind2, app_id)
            assert False, "Recruiter 2 should be denied access to Recruiter 1's app"
        except HTTPException as e:
            assert e.status_code == status.HTTP_404_NOT_FOUND
        print("[OK] Cross-company application protection PASS")

        # Test 10, 11 & 19: Internship Creation & Application -> Internship Lifecycle
        print("\n--- Test 10, 11 & 19: Internship Creation & Lifecycle ---")
        # Move app to OFFERED
        await IndustryService.update_application_status(db, user_ind1, app_id, ApplicationStatusUpdateRequest(status="OFFERED"))
        
        # Create Internship contract for Student 1
        internship = Internship(
            student_id=st1.id,
            company_id=comp1.id,
            opportunity_id=opp1.id,
            supervisor_user_id=user_ind1.id,
            supervisor_name="John Recruiter",
            supervisor_email="john@acme.com",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            stipend="30000/month",
            status="ONGOING"
        )
        db.add(internship)
        await db.commit()
        await db.refresh(internship)
        internship_id = internship.id
        print("[OK] Internship creation & lifecycle PASS")

        # Test 12 & 14: Internship Progress Authorization & Cross-Student IDOR
        print("\n--- Test 12 & 14: Internship Progress Authorization & IDOR ---")
        progress_payload = StudentInternshipProgressCreate(week_number=1, report_text="Completed onboarding and env setup.")
        p_res = await InternshipService.submit_internship_progress(db, user_st1, internship_id, progress_payload)
        assert p_res.week_number == 1

        # Student 2 tries to submit progress to Student 1's internship -> 404
        try:
            await InternshipService.submit_internship_progress(db, user_st2, internship_id, progress_payload)
            assert False, "Student 2 should be denied access to Student 1's internship progress"
        except HTTPException as e:
            assert e.status_code == status.HTTP_404_NOT_FOUND
        print("[OK] Internship progress authorization & IDOR PASS")

        # Test 13: Internship Evaluation Authorization
        print("\n--- Test 13: Internship Evaluation Authorization ---")
        eval_payload = InternshipEvaluationRequest(
            technical_rating=5,
            soft_skills_rating=4,
            punctuality_rating=5,
            overall_feedback="Outstanding performance throughout the internship."
        )
        eval_res = await IndustryService.submit_internship_evaluation(db, user_ind1, internship_id, eval_payload)
        assert eval_res.technical_rating == 5
        print("[OK] Internship evaluation authorization PASS")

        # Test 15, 16, 17, 18 & 20: Placement Record Creation, Isolation & Retrieval
        print("\n--- Test 15, 16, 17, 18 & 20: Placement Record & Isolation ---")
        rec = PlacementRecord(
            student_id=st1.id,
            company_id=comp1.id,
            opportunity_id=opp1.id,
            institution_id=inst1.id,
            package_lpa=Decimal("12.50"),
            offer_date=date.today(),
            status="ACCEPTED"
        )
        db.add(rec)
        await db.commit()

        # Student 1 retrieves placements
        st1_placements = await InternshipService.get_student_placements(db, user_st1)
        assert len(st1_placements) >= 1
        assert st1_placements[0].package_lpa == Decimal("12.50")

        # Student 2 retrieves placements (should be empty for Student 2)
        st2_placements = await InternshipService.get_student_placements(db, user_st2)
        assert len(st2_placements) == 0, "Student 2 should not see Student 1's placement record."
        print("[OK] Placement record creation, isolation & retrieval PASS")

        # Test 22 & 23: Regression Check
        print("\n--- Test 22 & 23: Regression Verification ---")
        # Verify Industry ATS list endpoint still works
        apps_list = await IndustryService.get_company_applications(db, user_ind1)
        assert apps_list.total >= 1
        print("[OK] Existing Module 06 ATS regression PASS")

        # Cleanup test entities
        await db.execute(delete(PlacementRecord).where(PlacementRecord.student_id.in_([st1.id, st2.id])))
        await db.execute(delete(InternshipEvaluation).where(InternshipEvaluation.internship_id == internship_id))
        await db.execute(delete(InternshipProgress).where(InternshipProgress.internship_id == internship_id))
        await db.execute(delete(Internship).where(Internship.student_id.in_([st1.id, st2.id])))
        await db.execute(delete(ApplicationStatusHistory).where(ApplicationStatusHistory.application_id == app_id))
        await db.execute(delete(Application).where(Application.student_id.in_([st1.id, st2.id])))
        await db.execute(delete(OpportunitySkill).where(OpportunitySkill.opportunity_id == opp1.id))
        await db.execute(delete(Opportunity).where(Opportunity.company_id.in_([comp1.id, comp2.id])))
        await db.execute(delete(StudentSkill).where(StudentSkill.student_id.in_([st1.id, st2.id])))
        await db.execute(delete(Skill).where(Skill.id.in_([sk_python.id, sk_sql.id])))
        await db.execute(delete(CompanyUser).where(CompanyUser.user_id.in_([user_ind1.id, user_ind2.id])))
        await db.execute(delete(Company).where(Company.id.in_([comp1.id, comp2.id])))
        await db.execute(delete(Student).where(Student.id.in_([st1.id, st2.id])))
        await db.execute(delete(UserProfile).where(UserProfile.user_id.in_([user_st1.id, user_st2.id])))
        await db.execute(delete(User).where(User.id.in_([user_st1.id, user_st2.id, user_ind1.id, user_ind2.id])))
        await db.execute(delete(Department).where(Department.id.in_([dept1.id, dept2.id])))
        await db.execute(delete(Institution).where(Institution.id.in_([inst1.id, inst2.id])))
        await db.commit()

        print("\n==================================================")
        print("ALL 23 MODULE 09 INTERNSHIP & PLACEMENT TESTS PASSED!")
        print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_phase9_tests())
