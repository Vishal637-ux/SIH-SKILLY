import asyncio
import uuid
from app.core.database import async_session_maker
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.careers import CareerRole, CareerRoleSkill
from app.models.skills import Skill
from app.core.security import hash_password
from sqlalchemy import select

async def seed():
    async with async_session_maker() as db:
        # Check institution
        stmt_inst = select(Institution).where(Institution.code == 'IITB_DEMO')
        inst = (await db.execute(stmt_inst)).scalar_one_or_none()
        if not inst:
            inst = Institution(
                name='IIT Bangalore (Demonstration Campus)',
                code='IITB_DEMO',
                institution_type='COLLEGE',
                city='Bangalore',
                state='Karnataka',
                country='India',
                is_accredited=True
            )
            db.add(inst)
            await db.flush()
            
            dept1 = Department(institution_id=inst.id, name='Computer Science & Engineering', code='CSE')
            dept2 = Department(institution_id=inst.id, name='Information Technology & AI', code='ITAI')
            db.add_all([dept1, dept2])
            await db.flush()
        else:
            dept1 = (await db.execute(select(Department).where(Department.institution_id == inst.id))).scalars().first()

        # Seed Skills
        skills_data = [
            ("React.js", "react-js", "Frontend Development", "Component-driven frontend UI development."),
            ("FastAPI & Async Python", "fastapi-async-python", "Backend Development", "High-performance asynchronous RESTful APIs with Python."),
            ("PostgreSQL Database", "postgresql-database", "Databases", "Relational database design, ACID transactions, and indexing."),
            ("Docker & Containerization", "docker-containers", "Cloud & DevOps", "Container orchestration and image creation."),
            ("Kubernetes & Cloud Infra", "kubernetes-cloud-infra", "Cloud & DevOps", "Container management and scalable cluster deployment."),
            ("Machine Learning & PyTorch", "ml-pytorch", "Artificial Intelligence", "Deep learning model design and neural networks."),
            ("Network Security & Auditing", "network-security", "Cybersecurity", "Network protocols, vulnerability scanning, and hardening."),
        ]

        skills_dict = {}
        for s_name, s_slug, s_cat, s_desc in skills_data:
            stmt_s = select(Skill).where(Skill.slug == s_slug)
            s_obj = (await db.execute(stmt_s)).scalar_one_or_none()
            if not s_obj:
                s_obj = Skill(name=s_name, slug=s_slug, category=s_cat, description=s_desc, is_verified=True)
                db.add(s_obj)
                await db.flush()
            skills_dict[s_slug] = s_obj

        # Seed Career Roles
        roles_data = [
            (
                "Full Stack Software Engineer",
                "full-stack-engineer-demo",
                "Software Development",
                "Designs and delivers complete end-to-end web applications with modern frontend and backend architectures.",
                [
                    ("react-js", "ADVANCED", "CORE"),
                    ("fastapi-async-python", "ADVANCED", "CORE"),
                    ("postgresql-database", "INTERMEDIATE", "CORE"),
                    ("docker-containers", "INTERMEDIATE", "RECOMMENDED"),
                ]
            ),
            (
                "Cloud DevOps Architect",
                "cloud-devops-architect-demo",
                "Cloud & DevOps",
                "Automates cloud infrastructure, manages CI/CD deployment pipelines, and ensures high system resilience.",
                [
                    ("docker-containers", "ADVANCED", "CORE"),
                    ("kubernetes-cloud-infra", "ADVANCED", "CORE"),
                    ("fastapi-async-python", "INTERMEDIATE", "RECOMMENDED"),
                ]
            ),
            (
                "AI & Machine Learning Engineer",
                "ai-ml-engineer-demo",
                "Artificial Intelligence",
                "Builds generative AI systems, deep neural networks, and scalable data intelligence pipelines.",
                [
                    ("ml-pytorch", "ADVANCED", "CORE"),
                    ("fastapi-async-python", "INTERMEDIATE", "CORE"),
                    ("postgresql-database", "BEGINNER", "RECOMMENDED"),
                ]
            ),
            (
                "Cybersecurity Specialist",
                "cybersecurity-specialist-demo",
                "Cybersecurity",
                "Protects enterprise networks, conducts ethical vulnerability assessments, and enforces zero-trust security.",
                [
                    ("network-security", "ADVANCED", "CORE"),
                    ("docker-containers", "INTERMEDIATE", "RECOMMENDED"),
                ]
            ),
        ]

        for r_title, r_slug, r_domain, r_desc, r_skills in roles_data:
            stmt_r = select(CareerRole).where(CareerRole.slug == r_slug)
            r_obj = (await db.execute(stmt_r)).scalar_one_or_none()
            if not r_obj:
                r_obj = CareerRole(
                    title=r_title,
                    slug=r_slug,
                    industry_domain=r_domain,
                    description=r_desc,
                    is_active=True,
                )
                db.add(r_obj)
                await db.flush()

                for skill_slug, req_lvl, imp_lvl in r_skills:
                    if skill_slug in skills_dict:
                        crs = CareerRoleSkill(
                            career_role_id=r_obj.id,
                            skill_id=skills_dict[skill_slug].id,
                            required_level=req_lvl,
                            importance_level=imp_lvl,
                        )
                        db.add(crs)

        # Student User
        stmt_u = select(User).where(User.email == 'student_browser@skilly.edu')
        user = (await db.execute(stmt_u)).scalar_one_or_none()
        if not user:
            user = User(
                email='student_browser@skilly.edu',
                username='student_browser',
                hashed_password=hash_password('Password@123'),
                role='STUDENT',
                is_active=True,
                is_verified=True
            )
            db.add(user)
            await db.flush()

            prof = UserProfile(
                user_id=user.id,
                first_name='Kavya',
                last_name='Sharma',
                city='Bangalore',
                state='Karnataka',
                country='India',
                phone='+91 9876543210',
                bio='Aspiring cloud and fullstack software engineer.'
            )
            db.add(prof)

            # Link Student record
            st_rec = Student(
                user_id=user.id,
                institution_id=inst.id,
                department_id=dept1.id,
                roll_number='IITB-2023-CS042',
                enrollment_year=2023,
                graduation_year=2027,
                current_semester=4,
                cgpa=9.15,
                target_career_role_id=None,
            )
            db.add(st_rec)

        await db.commit()
        print('Seed complete: 4 canonical career roles, skills, and student_browser@skilly.edu / Password@123 ready.')

if __name__ == '__main__':
    asyncio.run(seed())

