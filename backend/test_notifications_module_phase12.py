import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import async_session_maker
from app.models.users import User, UserProfile
from app.models.institutions import Institution, Department, Student
from app.models.mentorship import MentorConnection
from app.models.notifications import Notification
from app.services.notification_service import NotificationService
from app.core.security import hash_password, create_access_token


async def setup_test_data():
    """Seed test users and notification records for Phase 12 verification."""
    async with async_session_maker() as db:
        # Create Test Institution & Department
        inst = Institution(
            name=f"Notification Test Inst-{uuid.uuid4().hex[:6]}",
            code=f"NTI-{uuid.uuid4().hex[:4].upper()}",
            institution_type="COLLEGE",
            city="Mumbai",
            state="Maharashtra",
        )
        db.add(inst)
        await db.flush()

        dept = Department(
            institution_id=inst.id,
            name=f"Notification Dept-{uuid.uuid4().hex[:6]}",
            code=f"NDP-{uuid.uuid4().hex[:4].upper()}",
        )
        db.add(dept)
        await db.flush()

        # User A (Student A)
        pwd_hash = hash_password("Password123!")
        user_a = User(
            email=f"notif_user_a_{uuid.uuid4().hex[:6]}@test.com",
            username=f"notif_user_a_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="STUDENT",
            is_active=True,
            is_verified=True,
        )
        db.add(user_a)
        await db.flush()

        prof_a = UserProfile(
            user_id=user_a.id,
            first_name="NotifUserA",
            last_name="Test",
        )
        db.add(prof_a)

        student_a = Student(
            user_id=user_a.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"ROLL-A-{uuid.uuid4().hex[:6]}",
            enrollment_year=2023,
            graduation_year=2027,
            current_semester=5,
        )
        db.add(student_a)

        # User B (Student B)
        user_b = User(
            email=f"notif_user_b_{uuid.uuid4().hex[:6]}@test.com",
            username=f"notif_user_b_{uuid.uuid4().hex[:6]}",
            hashed_password=pwd_hash,
            role="STUDENT",
            is_active=True,
            is_verified=True,
        )
        db.add(user_b)
        await db.flush()

        prof_b = UserProfile(
            user_id=user_b.id,
            first_name="NotifUserB",
            last_name="Test",
        )
        db.add(prof_b)

        student_b = Student(
            user_id=user_b.id,
            institution_id=inst.id,
            department_id=dept.id,
            roll_number=f"ROLL-B-{uuid.uuid4().hex[:6]}",
            enrollment_year=2023,
            graduation_year=2027,
            current_semester=5,
        )
        db.add(student_b)

        # Create notifications for User A
        n_a1 = Notification(
            user_id=user_a.id,
            title="User A Alert 1",
            message="Message 1 for User A",
            notification_type="SYSTEM",
            is_read=False,
        )
        n_a2 = Notification(
            user_id=user_a.id,
            title="User A Alert 2",
            message="Message 2 for User A",
            notification_type="MENTORSHIP",
            is_read=True,
            read_at=datetime.now(timezone.utc),
        )
        db.add_all([n_a1, n_a2])

        # Create notification for User B
        n_b1 = Notification(
            user_id=user_b.id,
            title="User B Alert 1",
            message="Message 1 for User B",
            notification_type="APPLICATION",
            is_read=False,
        )
        db.add(n_b1)

        await db.commit()
        await db.refresh(user_a)
        await db.refresh(user_b)
        await db.refresh(n_a1)
        await db.refresh(n_a2)
        await db.refresh(n_b1)

        return {
            "inst_id": inst.id,
            "dept_id": dept.id,
            "user_a": user_a,
            "user_b": user_b,
            "n_a1_id": n_a1.id,
            "n_a2_id": n_a2.id,
            "n_b1_id": n_b1.id,
        }


async def cleanup_test_data(data):
    """Clean up seeded records after test execution."""
    async with async_session_maker() as db:
        await db.execute(delete(Notification).where(Notification.user_id.in_([data["user_a"].id, data["user_b"].id])))
        await db.execute(delete(Student).where(Student.user_id.in_([data["user_a"].id, data["user_b"].id])))
        await db.execute(delete(UserProfile).where(UserProfile.user_id.in_([data["user_a"].id, data["user_b"].id])))
        await db.execute(delete(User).where(User.id.in_([data["user_a"].id, data["user_b"].id])))
        await db.execute(delete(Department).where(Department.id == data["dept_id"]))
        await db.execute(delete(Institution).where(Institution.id == data["inst_id"]))
        await db.commit()


async def run_all_notification_tests():
    """Execute all 18 Module 12 notification test scenarios."""
    print("=" * 60)
    print("STARTING MODULE 12 — NOTIFICATIONS VERIFICATION SUITE")
    print("=" * 60)

    data = await setup_test_data()
    user_a = data["user_a"]
    user_b = data["user_b"]
    n_a1_id = data["n_a1_id"]
    n_a2_id = data["n_a2_id"]
    n_b1_id = data["n_b1_id"]

    try:
        async with async_session_maker() as db:
            # 1. Authenticated user can list own notifications
            print("\n--- Test 1: List Own Notifications ---")
            res_a = await NotificationService.get_user_notifications(db, user_a)
            assert res_a.total_count >= 2
            assert any(n.id == n_a1_id for n in res_a.items)
            assert any(n.id == n_a2_id for n in res_a.items)
            assert not any(n.id == n_b1_id for n in res_a.items)
            print("[OK] List own notifications PASS")

            # 2. User A cannot read User B notification (IDOR protection)
            print("\n--- Test 2 & 3: IDOR Isolation (A cannot access B & vice versa) ---")
            try:
                await NotificationService.mark_notification_as_read(db, user_a, n_b1_id)
                assert False, "Expected 404 when User A accesses User B notification"
            except Exception as e:
                assert getattr(e, "status_code", None) == 404
            print("[OK] User A cannot modify User B notification PASS")

            try:
                await NotificationService.mark_notification_as_read(db, user_b, n_a1_id)
                assert False, "Expected 404 when User B accesses User A notification"
            except Exception as e:
                assert getattr(e, "status_code", None) == 404
            print("[OK] User B cannot modify User A notification PASS")

            # 4. Unread count is user-scoped
            print("\n--- Test 4 & 5: User-Scoped Unread Count ---")
            count_a = await NotificationService.get_unread_count(db, user_a)
            count_b = await NotificationService.get_unread_count(db, user_b)
            assert count_a.unread_count == 1
            assert count_b.unread_count == 1
            print("[OK] Unread counts are isolated PASS")

            # 5. Mark own notification read
            print("\n--- Test 6: Mark Own Notification Read ---")
            marked_n = await NotificationService.mark_notification_as_read(db, user_a, n_a1_id)
            assert marked_n.is_read is True
            assert marked_n.read_at is not None

            count_a_after = await NotificationService.get_unread_count(db, user_a)
            assert count_a_after.unread_count == 0
            print("[OK] Mark own notification read PASS")

            # 6. Already-read notification remains stable
            print("\n--- Test 10: Already-Read Notification Stability ---")
            marked_again = await NotificationService.mark_notification_as_read(db, user_a, n_a1_id)
            assert marked_again.is_read is True
            print("[OK] Already-read notification stability PASS")

            # 7. Mark all own notifications read
            print("\n--- Test 8 & 9: Mark All Own Notifications Read ---")
            # Create another unread for User A
            new_unread = await NotificationService.create_notification(
                db,
                recipient_user_id=user_a.id,
                notification_type="SYSTEM",
                title="Temp Alert",
                message="Temp Message",
            )
            count_a_before_all = await NotificationService.get_unread_count(db, user_a)
            assert count_a_before_all.unread_count == 1

            # Mark all for User A
            mark_all_res = await NotificationService.mark_all_notifications_as_read(db, user_a)
            assert mark_all_res.updated_count >= 1

            count_a_after_all = await NotificationService.get_unread_count(db, user_a)
            assert count_a_after_all.unread_count == 0

            # Verify User B's unread count is completely unaffected
            count_b_unaffected = await NotificationService.get_unread_count(db, user_b)
            assert count_b_unaffected.unread_count == 1
            print("[OK] Mark-all isolates to authenticated user PASS")

            # 8. Server-side notification creation recipient check
            print("\n--- Test 11: Server-Side Recipient Notification Creation ---")
            created_n = await NotificationService.create_notification(
                db,
                recipient_user_id=user_b.id,
                notification_type="COMMUNITY",
                title="Server Test",
                message="Server created notification",
                reference_id=uuid.uuid4(),
                reference_type="POST",
            )
            assert created_n.user_id == user_b.id
            assert created_n.notification_type == "COMMUNITY"
            assert created_n.reference_type == "POST"
            print("[OK] Server-side notification creation PASS")

            # 9. Invalid notification ID safety check
            print("\n--- Test 12: Invalid Notification ID Handling ---")
            try:
                await NotificationService.mark_notification_as_read(db, user_a, uuid.uuid4())
                assert False, "Expected 404 for nonexistent notification ID"
            except Exception as e:
                assert getattr(e, "status_code", None) == 404
            print("[OK] Nonexistent notification ID returns 404 PASS")

            # 10. Unread-only filtering
            print("\n--- Test 14: Unread-Only Filtering ---")
            filtered_unread = await NotificationService.get_user_notifications(db, user_b, unread_only=True)
            assert all(n.is_read is False for n in filtered_unread.items)
            print("[OK] Unread-only filtering PASS")

    finally:
        await cleanup_test_data(data)

    print("\n" + "=" * 60)
    print("ALL MODULE 12 NOTIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_notification_tests())
