import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.users import User
from app.services.alumni_service import AlumniService
from app.schemas.alumni import (
    AlumniProfileResponse,
    AlumniProfileUpdateRequest,
    MentorshipRequestItem,
    MentorshipRequestListResponse,
    MentorshipRequestActionRequest,
    MentorConnectionItem,
    MentorConnectionListResponse,
    MentorshipSessionCreateRequest,
    MentorshipSessionUpdateRequest,
    MentorshipSessionItem,
    MentorshipSessionListResponse,
    AlumniDashboardResponse,
)

router = APIRouter(prefix="/alumni", tags=["Alumni / Mentor Workspace"])


@router.get(
    "/dashboard",
    response_model=AlumniDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get alumni mentor dashboard metrics",
)
async def get_alumni_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.get_alumni_dashboard(db, current_user)


@router.get(
    "/profile",
    response_model=AlumniProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get mentor profile",
)
async def get_alumni_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.get_alumni_profile(db, current_user)


@router.put(
    "/profile",
    response_model=AlumniProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update mentor profile",
)
async def update_alumni_profile(
    payload: AlumniProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.update_alumni_profile(db, current_user, payload)


@router.get(
    "/requests",
    response_model=MentorshipRequestListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get mentorship connection requests",
)
async def get_mentorship_requests(
    status: Optional[str] = Query(None, description="Filter by status (PENDING, ACCEPTED, REJECTED)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.get_mentorship_requests(db, current_user, status)


@router.put(
    "/requests/{connection_id}",
    response_model=MentorshipRequestItem,
    status_code=status.HTTP_200_OK,
    summary="Accept or reject a mentorship request",
)
async def respond_to_mentorship_request(
    connection_id: uuid.UUID,
    payload: MentorshipRequestActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.respond_to_mentorship_request(db, current_user, connection_id, payload)


@router.get(
    "/connections",
    response_model=MentorConnectionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get active mentor connections",
)
async def get_active_connections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.get_active_connections(db, current_user)


@router.get(
    "/connections/{connection_id}",
    response_model=MentorConnectionItem,
    status_code=status.HTTP_200_OK,
    summary="Get mentor connection details",
)
async def get_connection_detail(
    connection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.get_connection_detail(db, current_user, connection_id)


@router.get(
    "/sessions",
    response_model=MentorshipSessionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get mentorship sessions",
)
async def get_mentorship_sessions(
    status: Optional[str] = Query(None, description="Filter by status (SCHEDULED, COMPLETED, CANCELLED)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.get_mentorship_sessions(db, current_user, status)


@router.post(
    "/sessions",
    response_model=MentorshipSessionItem,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule a mentorship session",
)
async def create_mentorship_session(
    payload: MentorshipSessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.create_mentorship_session(db, current_user, payload)


@router.get(
    "/sessions/{session_id}",
    response_model=MentorshipSessionItem,
    status_code=status.HTTP_200_OK,
    summary="Get mentorship session detail",
)
async def get_session_detail(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.get_session_detail(db, current_user, session_id)


@router.put(
    "/sessions/{session_id}",
    response_model=MentorshipSessionItem,
    status_code=status.HTTP_200_OK,
    summary="Update mentorship session status or notes",
)
async def update_mentorship_session(
    session_id: uuid.UUID,
    payload: MentorshipSessionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ALUMNI")),
):
    return await AlumniService.update_mentorship_session(db, current_user, session_id, payload)
