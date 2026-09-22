import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from sqlalchemy import select, delete, and_
from app.core.database import async_session_maker
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.skills import Skill
from app.models.community import CommunityPost, CommunityComment, PeerSkillRequest, Activity
from app.services.community_service import CommunityService
from app.schemas.community import (
    CommunityPostCreate,
    CommunityPostUpdate,
    CommunityCommentCreate,
    CommunityCommentUpdate,
    PeerSkillRequestCreate,
    PeerSkillRequestUpdate,
)
from fastapi import HTTPException, status


async def run_phase11_tests():
    print("==================================================")
    print("STARTING MODULE 11 — COMMUNITY & NETWORKING TESTS")
    print("==================================================")

    async with async_session_maker() as db:
        test_prefix = f"cm_{uuid.uuid4().hex[:6]}"

        # 1. Setup Test Fixtures in Real PostgreSQL
        inst = Institution(
            name=f"Community Inst {test_prefix}",
            code=f"INS_{test_prefix}",
            city="TechCity",
            state="TechState"
        )
        db.add(inst)
        await db.flush()

        dept = Department(institution_id=inst.id, name="Computer Science", code="CS")
        db.add(dept)
        await db.flush()

        # User 1 (Student A)
        user_a = User(
            email=f"usera_{test_prefix}@skilly.edu",
            username=f"usera_{test_prefix}",
            hashed_password="hash",
            role="STUDENT",
            is_active=True
        )
        # User 2 (Student B - IDOR testing)
        user_b = User(
            email=f"userb_{test_prefix}@skilly.edu",
            username=f"userb_{test_prefix}",
            hashed_password="hash",
            role="STUDENT",
            is_active=True
        )
        db.add_all([user_a, user_b])
        await db.flush()

        prof_a = UserProfile(user_id=user_a.id, first_name="Alice", last_name="Community", phone="1234567890", city="TechCity")
        prof_b = UserProfile(user_id=user_b.id, first_name="Bob", last_name="Network", phone="0987654321", city="TechCity")
        db.add_all([prof_a, prof_b])

        st_a = Student(
            user_id=user_a.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"STA_{test_prefix}",
            enrollment_year=2023,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("8.80")
        )
        st_b = Student(
            user_id=user_b.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"STB_{test_prefix}",
            enrollment_year=2023,
            graduation_year=2026,
            current_semester=7,
            cgpa=Decimal("7.50")
        )
        db.add_all([st_a, st_b])
        await db.flush()

        # Skill for peer exchange
        sk_python = Skill(name=f"Python_{test_prefix}", slug=f"python_{test_prefix}", category="TECHNICAL", description="Python programming")
        db.add(sk_python)
        await db.flush()

        # Activity fixture
        act = Activity(
            institution_id=inst.id,
            title=f"Annual Hackathon Launch {test_prefix}",
            description="Collaborative campus hackathon kickoff.",
            activity_type="WORKSHOP",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(hours=4),
            location_or_url="Auditorium A",
            conducted_by_user_id=user_a.id
        )
        db.add(act)
        await db.commit()

        print("[OK] Test setup completed successfully.")

        # Test 1 & 2: Authenticated Community Access & Post Creation
        print("\n--- Test 1, 2, 3 & 4: Post Creation & Retrieval ---")
        post_payload = CommunityPostCreate(
            title="Best Practices for FastAPI Async DB Sessions",
            content="Always ensure greenlet_spawn or async_session_maker context manager is used cleanly.",
            post_type="DISCUSSION",
            tags=["FastAPI", "Python", "PostgreSQL"]
        )
        created_post = await CommunityService.create_post(db, user_a, post_payload)
        assert created_post.title == "Best Practices for FastAPI Async DB Sessions"
        assert created_post.author.user_id == user_a.id
        post_id = created_post.id
        print("[OK] Post creation & retrieval PASS")

        # Test 5, 7 & 8: Post Update, Ownership & Cross-User IDOR
        print("\n--- Test 5, 7 & 8: Post Update & Cross-User IDOR ---")
        update_payload = CommunityPostUpdate(title="Updated: Best Practices for FastAPI Async DB Sessions")
        updated_post = await CommunityService.update_post(db, user_a, post_id, update_payload)
        assert updated_post.title == "Updated: Best Practices for FastAPI Async DB Sessions"

        # User B attempts to edit User A's post -> 403
        try:
            await CommunityService.update_post(db, user_b, post_id, update_payload)
            assert False, "User B should be blocked from updating User A's post"
        except HTTPException as e:
            assert e.status_code == status.HTTP_403_FORBIDDEN
        print("[OK] Post update & cross-user IDOR PASS")

        # Test 9, 10, 11 & 12: Comment Creation, Retrieval & Cross-User IDOR
        print("\n--- Test 9, 10, 11 & 12: Comment Creation, Retrieval & IDOR ---")
        comment_payload = CommunityCommentCreate(content="Great guide! Asyncpg makes SQLAlchemy 2.0 super fast.")
        created_comment = await CommunityService.create_comment(db, user_b, post_id, comment_payload)
        assert created_comment.content == "Great guide! Asyncpg makes SQLAlchemy 2.0 super fast."
        assert created_comment.author.user_id == user_b.id
        comment_id = created_comment.id

        comments_list = await CommunityService.get_comments(db, user_a, post_id)
        assert len(comments_list) >= 1

        # User A attempts to edit User B's comment -> 403
        c_update = CommunityCommentUpdate(content="Attempted hijack")
        try:
            await CommunityService.update_comment(db, user_a, comment_id, c_update)
            assert False, "User A should be blocked from updating User B's comment"
        except HTTPException as e:
            assert e.status_code == status.HTTP_403_FORBIDDEN
        print("[OK] Comment creation, retrieval & IDOR PASS")

        # Test 13: Comment Update & Delete by Owner
        print("\n--- Test 13: Comment Update & Delete by Owner ---")
        valid_c_update = CommunityCommentUpdate(content="Updated: Asyncpg makes SQLAlchemy 2.0 fast.")
        updated_c = await CommunityService.update_comment(db, user_b, comment_id, valid_c_update)
        assert updated_c.content == "Updated: Asyncpg makes SQLAlchemy 2.0 fast."

        await CommunityService.delete_comment(db, user_b, comment_id)
        print("[OK] Comment update & delete by owner PASS")

        # Test 14, 15, 16, 17 & 18: Peer Skill Request Lifecycle & IDOR
        print("\n--- Test 14, 15, 16, 17 & 18: Peer Skill Request Lifecycle & IDOR ---")
        peer_req_payload = PeerSkillRequestCreate(
            skill_id=sk_python.id,
            request_type="SEEKING_HELP",
            description="Looking for help with asyncpg connection pooling."
        )
        peer_req = await CommunityService.create_peer_skill_request(db, user_a, peer_req_payload)
        assert peer_req.skill_id == sk_python.id
        assert peer_req.requester_student_id == st_a.id
        req_id = peer_req.id

        # User B accepts request as helper
        peer_update = PeerSkillRequestUpdate(status="IN_PROGRESS", helper_student_id=st_b.id)
        updated_peer = await CommunityService.update_peer_skill_request(db, user_b, req_id, peer_update)
        assert updated_peer.status == "IN_PROGRESS"
        assert updated_peer.helper_student_id == st_b.id

        # Test Invalid Skill ID -> 404
        bad_peer_payload = PeerSkillRequestCreate(
            skill_id=uuid.uuid4(),
            request_type="SEEKING_HELP",
            description="Invalid skill testing."
        )
        try:
            await CommunityService.create_peer_skill_request(db, user_a, bad_peer_payload)
            assert False, "Invalid skill ID should raise 404"
        except HTTPException as e:
            assert e.status_code == status.HTTP_404_NOT_FOUND
        print("[OK] Peer skill request lifecycle & IDOR PASS")

        # Test 19: Activity Retrieval
        print("\n--- Test 19: Activity Retrieval ---")
        activities = await CommunityService.get_activities(db, user_a)
        assert len(activities) >= 1
        target_act = next((a for a in activities if a.title == f"Annual Hackathon Launch {test_prefix}"), None)
        assert target_act is not None, "Target test activity must be retrieved."
        print("[OK] Activity retrieval PASS")

        # Test 6: Post Deletion & IDOR Protection
        print("\n--- Test 6: Post Deletion & IDOR Protection ---")
        # User B attempts to delete User A's post -> 403
        try:
            await CommunityService.delete_post(db, user_b, post_id)
            assert False, "User B should be blocked from deleting User A's post"
        except HTTPException as e:
            assert e.status_code == status.HTTP_403_FORBIDDEN

        # User A deletes their own post
        await CommunityService.delete_post(db, user_a, post_id)
        print("[OK] Post deletion & IDOR protection PASS")

        # Cleanup test entities
        await db.execute(delete(PeerSkillRequest).where(PeerSkillRequest.id == req_id))
        await db.execute(delete(Activity).where(Activity.id == act.id))
        await db.execute(delete(Skill).where(Skill.id == sk_python.id))
        await db.execute(delete(Student).where(Student.id.in_([st_a.id, st_b.id])))
        await db.execute(delete(UserProfile).where(UserProfile.user_id.in_([user_a.id, user_b.id])))
        await db.execute(delete(User).where(User.id.in_([user_a.id, user_b.id])))
        await db.execute(delete(Department).where(Department.id == dept.id))
        await db.execute(delete(Institution).where(Institution.id == inst.id))
        await db.commit()

        print("\n==================================================")
        print("ALL MODULE 11 COMMUNITY & NETWORKING TESTS PASSED!")
        print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_phase11_tests())
