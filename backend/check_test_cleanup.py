import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session_maker
from sqlalchemy import text


async def main():
    async with async_session_maker() as s:
        u = (await s.execute(text("SELECT count(id) FROM users WHERE email LIKE '%test_p33%' OR email LIKE '%phase33%'"))).scalar()
        st = (await s.execute(text("SELECT count(s.id) FROM students s JOIN users u ON s.user_id = u.id WHERE u.email LIKE '%test_p33%' OR u.email LIKE '%phase33%'"))).scalar()
        p = (await s.execute(text("SELECT count(p.id) FROM user_profiles p JOIN users u ON p.user_id = u.id WHERE u.email LIKE '%test_p33%' OR u.email LIKE '%phase33%'"))).scalar()
        r = (await s.execute(text("SELECT count(id) FROM career_roles WHERE slug LIKE '%test-p33%' OR title LIKE '%Test Career%'"))).scalar()
        sk = (await s.execute(text("SELECT count(id) FROM skills WHERE name LIKE '%Test Skill%'"))).scalar()
        crs = (await s.execute(text("SELECT count(crs.id) FROM career_role_skills crs JOIN career_roles r ON crs.career_role_id = r.id WHERE r.slug LIKE '%test-p33%'"))).scalar()
        inst = (await s.execute(text("SELECT count(id) FROM institutions WHERE name LIKE '%Test University P33%'"))).scalar()
        dept = (await s.execute(text("SELECT count(id) FROM departments WHERE code LIKE '%P33_TEST%'"))).scalar()
        
        print("================ TEST DATA CLEANUP VERIFICATION ================")
        print(f"Test Users in DB:             {u}")
        print(f"Test Students in DB:          {st}")
        print(f"Test User Profiles in DB:     {p}")
        print(f"Test Career Roles in DB:      {r}")
        print(f"Test Career Role Skills in DB:{crs}")
        print(f"Test Skills in DB:            {sk}")
        print(f"Test Institutions in DB:      {inst}")
        print(f"Test Departments in DB:       {dept}")
        print("================================================================")
        if u == 0 and st == 0 and p == 0 and r == 0 and crs == 0 and sk == 0 and inst == 0 and dept == 0:
            print("CLEANUP STATUS: 100% COMPLETE & VERIFIED (0 ORPHAN TEST RECORDS)")
        else:
            print("CLEANUP STATUS: INCOMPLETE")

if __name__ == "__main__":
    asyncio.run(main())
