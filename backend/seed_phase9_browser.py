import asyncio
import uuid
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal

from sqlalchemy import select, and_
from app.core.database import async_session_maker
from app.core.security import hash_password
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.companies import Company, CompanyUser
from app.models.skills import Skill, StudentSkill
from app.models.opportunities import Opportunity, OpportunitySkill, Application, ApplicationStatusHistory
from app.models.internships import Internship, InternshipProgress, InternshipEvaluation
from app.models.placements import PlacementRecord, PlacementInteraction


async def seed_phase9():
    async with async_session_maker() as db:
        # Check/Create Institution & Department
        stmt_inst = select(Institution).where(Institution.code == "SKILLY_UNI")
        inst = (await db.execute(stmt_inst)).scalar_one_or_none()
        if not inst:
            inst = Institution(
                name="Skilly Tech University",
                code="SKILLY_UNI",
                institution_type="COLLEGE",
                city="Bangalore",
                state="Karnataka",
                country="India",
                is_accredited=True
            )
            db.add(inst)
            await db.flush()

            dept = Department(institution_id=inst.id, name="Computer Science", code="CS")
            db.add(dept)
            await db.flush()
        else:
            dept_stmt = select(Department).where(Department.institution_id == inst.id)
            dept = (await db.execute(dept_stmt)).scalars().first()

        # Check/Create Student User
        stmt_u_st = select(User).where(User.email == "student_p9@skilly.edu")
        u_st = (await db.execute(stmt_u_st)).scalar_one_or_none()
        if not u_st:
            u_st = User(
                email="student_p9@skilly.edu",
                username="student_p9",
                hashed_password=hash_password("Password@123"),
                role="STUDENT",
                is_active=True,
                is_verified=True
            )
            db.add(u_st)
            await db.flush()

            prof_st = UserProfile(user_id=u_st.id, first_name="Aarav", last_name="Sharma", city="Bangalore", phone="+91 9999999999")
            db.add(prof_st)

            st = Student(
                user_id=u_st.id,
                institution_id=inst.id,
                department_id=dept.id,
                roll_number="CS2023001",
                enrollment_year=2023,
                graduation_year=2026,
                current_semester=7,
                cgpa=Decimal("9.10")
            )
            db.add(st)
            await db.flush()
        else:
            st_stmt = select(Student).where(Student.user_id == u_st.id)
            st = (await db.execute(st_stmt)).scalar_one_or_none()

        # Check/Create Industry User & Company
        stmt_comp = select(Company).where(Company.name == "TechCorp Innovations")
        comp = (await db.execute(stmt_comp)).scalar_one_or_none()
        if not comp:
            comp = Company(
                name="TechCorp Innovations",
                industry_type="Software & AI",
                company_size="500+",
                headquarters="Bangalore",
                description="Leading AI and Software engineering firm.",
                is_verified=True
            )
            db.add(comp)
            await db.flush()

            u_ind = User(
                email="recruiter_p9@techcorp.com",
                username="recruiter_p9",
                hashed_password=hash_password("Password@123"),
                role="INDUSTRY",
                is_active=True,
                is_verified=True
            )
            db.add(u_ind)
            await db.flush()

            comp_u = CompanyUser(user_id=u_ind.id, company_id=comp.id, designation="Lead Recruiter", hr_role="RECRUITER")
            db.add(comp_u)
            await db.flush()
        else:
            u_ind_stmt = select(User).where(User.email == "recruiter_p9@techcorp.com")
            u_ind = (await db.execute(u_ind_stmt)).scalar_one_or_none()

        # Check/Create Opportunity
        stmt_opp = select(Opportunity).where(Opportunity.title == "Full Stack Engineer Intern 2026")
        opp = (await db.execute(stmt_opp)).scalar_one_or_none()
        if not opp:
            opp = Opportunity(
                company_id=comp.id,
                title="Full Stack Engineer Intern 2026",
                role_type="INTERNSHIP",
                description="Work on high-scale FastAPI and React applications.",
                location="Bangalore",
                is_remote=True,
                stipend_salary="45,000 / month",
                duration_months=6,
                openings_count=5,
                eligibility_criteria={"min_cgpa": 7.5, "graduation_year": 2026},
                application_deadline=datetime.now(timezone.utc) + timedelta(days=60),
                status="OPEN"
            )
            db.add(opp)
            await db.flush()

        # Check/Create Application
        stmt_app = select(Application).where(and_(Application.opportunity_id == opp.id, Application.student_id == st.id))
        app = (await db.execute(stmt_app)).scalar_one_or_none()
        if not app:
            app = Application(
                opportunity_id=opp.id,
                student_id=st.id,
                cover_letter="I have extensive experience with FastAPI and React.",
                current_status="INTERVIEWING"
            )
            db.add(app)
            await db.flush()

            hist1 = ApplicationStatusHistory(application_id=app.id, status="APPLIED", notes="Applied online", changed_by_user_id=u_st.id)
            hist2 = ApplicationStatusHistory(application_id=app.id, status="SHORTLISTED", notes="Shortlisted for technical test", changed_by_user_id=u_ind.id)
            hist3 = ApplicationStatusHistory(application_id=app.id, status="INTERVIEWING", notes="Scheduled round 1 technical interview", changed_by_user_id=u_ind.id)
            db.add_all([hist1, hist2, hist3])

        # Check/Create Internship
        stmt_intern = select(Internship).where(and_(Internship.student_id == st.id, Internship.company_id == comp.id))
        intern = (await db.execute(stmt_intern)).scalar_one_or_none()
        if not intern:
            intern = Internship(
                student_id=st.id,
                company_id=comp.id,
                opportunity_id=opp.id,
                supervisor_user_id=u_ind.id,
                supervisor_name="Vikram Sethi",
                supervisor_email="vikram@techcorp.com",
                start_date=date.today() - timedelta(days=30),
                end_date=date.today() + timedelta(days=120),
                stipend="45,000 / month",
                status="ONGOING"
            )
            db.add(intern)
            await db.flush()

            prog1 = InternshipProgress(internship_id=intern.id, week_number=1, report_text="Completed dev environment setup and codebase walkthrough.", mentor_feedback="Great start!")
            prog2 = InternshipProgress(internship_id=intern.id, week_number=2, report_text="Built auth middleware and wrote unit tests.", mentor_feedback="Excellent quality code.")
            db.add_all([prog1, prog2])

        # Check/Create Placement Record
        stmt_place = select(PlacementRecord).where(and_(PlacementRecord.student_id == st.id, PlacementRecord.company_id == comp.id))
        place = (await db.execute(stmt_place)).scalar_one_or_none()
        if not place:
            place = PlacementRecord(
                student_id=st.id,
                company_id=comp.id,
                opportunity_id=opp.id,
                institution_id=inst.id,
                package_lpa=Decimal("18.50"),
                offer_date=date.today() - timedelta(days=5),
                status="OFFERED"
            )
            db.add(place)

        await db.commit()
        print("Module 09 Seed completed successfully: student_p9@skilly.edu / recruiter_p9@techcorp.com (Password@123)")

if __name__ == "__main__":
    asyncio.run(seed_phase9())
