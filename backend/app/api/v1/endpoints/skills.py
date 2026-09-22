import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, get_optional_user
from app.models.users import User
from app.services.skill_service import get_all_skills, get_skill_detail

router = APIRouter(prefix="/skills", tags=["Skills Taxonomy"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List active master skills",
    description="Returns available master skills catalog with optional category and search filters.",
)
async def list_skills(
    category: Optional[str] = Query(None, description="Filter by skill category"),
    search: Optional[str] = Query(None, description="Search term in skill name or description"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    return await get_all_skills(db, category=category, search=search)


@router.get(
    "/{skill_id}",
    status_code=status.HTTP_200_OK,
    summary="Get detailed skill specification",
    description="Returns skill details including prerequisites and related skills graph edges.",
)
async def get_skill_by_id(
    skill_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await get_skill_detail(db, skill_id)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
