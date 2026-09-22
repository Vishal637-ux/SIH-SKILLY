import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.users import User
from app.models.notifications import Notification
from app.schemas.notification import (
    NotificationRead,
    NotificationListResponse,
    UnreadCountResponse,
    NotificationMarkReadResponse,
)


class NotificationService:

    @staticmethod
    async def create_notification(
        db: AsyncSession,
        recipient_user_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: str,
        reference_id: Optional[uuid.UUID] = None,
        reference_type: Optional[str] = None,
        commit: bool = True,
    ) -> Notification:
        """Server-side helper to record a system/workflow notification."""
        notif = Notification(
            user_id=recipient_user_id,
            title=title.strip(),
            message=message.strip(),
            notification_type=notification_type.strip(),
            reference_id=reference_id,
            reference_type=reference_type.strip() if reference_type else None,
            is_read=False,
        )
        db.add(notif)
        if commit:
            await db.commit()
            await db.refresh(notif)
        else:
            await db.flush()
        return notif

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user: User,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> NotificationListResponse:
        """Fetch notifications belonging strictly to the authenticated user."""
        stmt = select(Notification).where(Notification.user_id == user.id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))

        # Total count for user
        total_stmt = select(func.count(Notification.id)).where(Notification.user_id == user.id)
        if unread_only:
            total_stmt = total_stmt.where(Notification.is_read.is_(False))
        total_count = (await db.execute(total_stmt)).scalar() or 0

        # Unread count for user
        unread_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user.id,
            Notification.is_read.is_(False),
        )
        unread_count = (await db.execute(unread_stmt)).scalar() or 0

        # Order by created_at DESC deterministically
        stmt = stmt.order_by(Notification.created_at.desc(), Notification.id.desc())
        stmt = stmt.limit(limit).offset(offset)

        res = await db.execute(stmt)
        items = res.scalars().all()

        return NotificationListResponse(
            items=[NotificationRead.model_validate(n) for n in items],
            unread_count=unread_count,
            total_count=total_count,
        )

    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        user: User,
    ) -> UnreadCountResponse:
        """Fetch unread notification count belonging strictly to the authenticated user."""
        unread_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user.id,
            Notification.is_read.is_(False),
        )
        unread_count = (await db.execute(unread_stmt)).scalar() or 0
        return UnreadCountResponse(unread_count=unread_count)

    @staticmethod
    async def mark_notification_as_read(
        db: AsyncSession,
        user: User,
        notification_id: uuid.UUID,
    ) -> NotificationRead:
        """Mark a single notification as read, ensuring strict ownership check."""
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
        res = await db.execute(stmt)
        notif = res.scalar_one_or_none()

        if not notif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or access denied.",
            )

        if not notif.is_read:
            notif.is_read = True
            notif.read_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(notif)

        return NotificationRead.model_validate(notif)

    @staticmethod
    async def mark_all_notifications_as_read(
        db: AsyncSession,
        user: User,
    ) -> NotificationMarkReadResponse:
        """Mark all notifications as read belonging strictly to the authenticated user."""
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user.id,
                Notification.is_read.is_(False),
            )
            .values(
                is_read=True,
                read_at=datetime.now(timezone.utc),
            )
        )
        res = await db.execute(stmt)
        await db.commit()
        updated_count = res.rowcount or 0

        return NotificationMarkReadResponse(
            message="All notifications marked as read.",
            updated_count=updated_count,
        )
