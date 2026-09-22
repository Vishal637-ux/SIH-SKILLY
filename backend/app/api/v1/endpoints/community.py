import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.users import User
from app.services.community_service import CommunityService
from app.schemas.community import (
    CommunityPostCreate,
    CommunityPostUpdate,
    CommunityPostRead,
    CommunityCommentCreate,
    CommunityCommentUpdate,
    CommunityCommentRead,
    PeerSkillRequestCreate,
    PeerSkillRequestUpdate,
    PeerSkillRequestRead,
    ActivityRead,
)

router = APIRouter(prefix="/community", tags=["Community & Networking Workspace"])


@router.get(
    "/posts",
    response_model=List[CommunityPostRead],
    status_code=status.HTTP_200_OK,
    summary="Get community discussion posts feed",
)
async def get_community_posts(
    post_type: Optional[str] = Query(None, description="GENERAL, DISCUSSION, RESOURCE, SHOWCASE"),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.get_posts(db, current_user, post_type=post_type, tag=tag, search=search)


@router.post(
    "/posts",
    response_model=CommunityPostRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new community discussion post",
)
async def create_community_post(
    payload: CommunityPostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.create_post(db, current_user, payload)


@router.get(
    "/posts/{post_id}",
    response_model=CommunityPostRead,
    status_code=status.HTTP_200_OK,
    summary="Get detailed community post with comment thread",
)
async def get_community_post_detail(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.get_post_detail(db, current_user, post_id)


@router.put(
    "/posts/{post_id}",
    response_model=CommunityPostRead,
    status_code=status.HTTP_200_OK,
    summary="Update own community discussion post",
)
async def update_community_post(
    post_id: uuid.UUID,
    payload: CommunityPostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.update_post(db, current_user, post_id, payload)


@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete own community discussion post",
)
async def delete_community_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await CommunityService.delete_post(db, current_user, post_id)


@router.get(
    "/posts/{post_id}/comments",
    response_model=List[CommunityCommentRead],
    status_code=status.HTTP_200_OK,
    summary="Get comments for a community post",
)
async def get_post_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.get_comments(db, current_user, post_id)


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommunityCommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add comment to a community post",
)
async def create_post_comment(
    post_id: uuid.UUID,
    payload: CommunityCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.create_comment(db, current_user, post_id, payload)


@router.put(
    "/comments/{comment_id}",
    response_model=CommunityCommentRead,
    status_code=status.HTTP_200_OK,
    summary="Update own comment",
)
async def update_comment(
    comment_id: uuid.UUID,
    payload: CommunityCommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.update_comment(db, current_user, comment_id, payload)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete own comment",
)
async def delete_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await CommunityService.delete_comment(db, current_user, comment_id)


@router.get(
    "/peer-skills",
    response_model=List[PeerSkillRequestRead],
    status_code=status.HTTP_200_OK,
    summary="Get peer skill exchange requests marketplace",
)
async def get_peer_skill_requests(
    skill_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None, description="OPEN, IN_PROGRESS, COMPLETED, CLOSED"),
    request_type: Optional[str] = Query(None, description="SEEKING_HELP, OFFERING_HELP"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.get_peer_skill_requests(
        db, current_user, skill_id=skill_id, status_filter=status, request_type=request_type
    )


@router.post(
    "/peer-skills",
    response_model=PeerSkillRequestRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a peer skill exchange request",
)
async def create_peer_skill_request(
    payload: PeerSkillRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.create_peer_skill_request(db, current_user, payload)


@router.get(
    "/peer-skills/{request_id}",
    response_model=PeerSkillRequestRead,
    status_code=status.HTTP_200_OK,
    summary="Get peer skill exchange request detail",
)
async def get_peer_skill_request_detail(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.get_peer_skill_request_detail(db, current_user, request_id)


@router.put(
    "/peer-skills/{request_id}",
    response_model=PeerSkillRequestRead,
    status_code=status.HTTP_200_OK,
    summary="Update or accept a peer skill request",
)
async def update_peer_skill_request(
    request_id: uuid.UUID,
    payload: PeerSkillRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.update_peer_skill_request(db, current_user, request_id, payload)


@router.get(
    "/activities",
    response_model=List[ActivityRead],
    status_code=status.HTTP_200_OK,
    summary="Get platform and campus activities",
)
async def get_community_activities(
    activity_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CommunityService.get_activities(db, current_user, activity_type=activity_type)
