import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.users import User
from app.schemas.notification import (
    NotificationRead,
    NotificationListResponse,
    UnreadCountResponse,
    NotificationMarkReadResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications Module"])


@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user's notifications",
    description="Returns notifications belonging strictly to the authenticated user.",
)
async def list_notifications(
    unread_only: bool = Query(False, description="Filter for unread notifications only"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await NotificationService.get_user_notifications(
        db=db,
        user=current_user,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user's unread notification count",
    description="Returns count of unread notifications belonging strictly to the authenticated user.",
)
async def get_unread_notification_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await NotificationService.get_unread_count(db=db, user=current_user)


@router.put(
    "/read-all",
    response_model=NotificationMarkReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark all notifications as read",
    description="Marks all unread notifications belonging strictly to the authenticated user as read.",
)
@router.patch(
    "/read-all",
    response_model=NotificationMarkReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark all notifications as read (PATCH alias)",
)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await NotificationService.mark_all_notifications_as_read(db=db, user=current_user)


@router.put(
    "/{notification_id}/read",
    response_model=NotificationRead,
    status_code=status.HTTP_200_OK,
    summary="Mark a specific notification as read",
    description="Marks a single notification as read if owned by the authenticated user.",
)
@router.patch(
    "/{notification_id}/read",
    response_model=NotificationRead,
    status_code=status.HTTP_200_OK,
    summary="Mark a specific notification as read (PATCH alias)",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await NotificationService.mark_notification_as_read(
        db=db,
        user=current_user,
        notification_id=notification_id,
    )
