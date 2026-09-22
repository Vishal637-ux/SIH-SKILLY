import asyncio
from app.core.database import async_session_maker
from app.core.security import hash_password
from app.models.users import User, UserProfile
from app.models.companies import Company, CompanyUser
from sqlalchemy import select

async def seed():
    async with async_session_maker() as db:
        stmt = select(User).where(User.email == "industry@test.com")
        res = await db.execute(stmt)
        u = res.scalar_one_or_none()
        if not u:
            u = User(
                email="industry@test.com",
                username="industry_demo",
                hashed_password=hash_password("Password123!"),
                role="INDUSTRY",
                is_active=True,
                is_verified=True,
            )
            db.add(u)
            await db.flush()
            db.add(UserProfile(user_id=u.id, first_name="Acme", last_name="Recruiter"))
            comp = Company(
                name="Acme Global Corporation",
                industry_type="Technology",
                company_size="50-200 employees",
                headquarters="San Francisco, CA",
                description="Leading technological innovations",
                is_verified=True,
            )
            db.add(comp)
            await db.flush()
            db.add(CompanyUser(user_id=u.id, company_id=comp.id, designation="VP of Talent", hr_role="RECRUITER"))
            await db.commit()
            print("Seeded industry@test.com / Password123!")
        else:
            print("User industry@test.com already exists.")

if __name__ == "__main__":
    asyncio.run(seed())
