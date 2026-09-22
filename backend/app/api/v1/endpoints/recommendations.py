import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.users import User
from app.schemas.recommendation import (
    RecommendationItem,
    RecommendationOverviewResponse,
    RecommendationCategoryResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/student/recommendations", tags=["AI & Recommendations Module"])


@router.get(
    "",
    response_model=RecommendationOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get unified AI recommendations overview for student",
    description="Returns skill-aware, explainable AI recommendations across career roles, learning programs, opportunities, and mentors.",
)
async def get_student_recommendations_overview(
    current_user: User = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    return await RecommendationService.get_student_recommendations_overview(db=db, user=current_user)


@router.get(
    "/careers",
    response_model=RecommendationCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get recommended career roles",
    description="Returns career role recommendations matching verified skills and skill gaps.",
)
async def get_recommended_career_roles(
    limit: int = Query(10, ge=1, le=50, description="Limit count"),
    current_user: User = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    items = await RecommendationService.get_career_recommendations(db=db, user=current_user, limit=limit)
    return RecommendationCategoryResponse(
        category="CAREER_ROLE",
        total_count=len(items),
        items=items,
    )


@router.get(
    "/learning",
    response_model=RecommendationCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get recommended learning and training programs",
    description="Returns training program recommendations addressing active skill gaps.",
)
async def get_recommended_learning_programs(
    limit: int = Query(10, ge=1, le=50, description="Limit count"),
    current_user: User = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    items = await RecommendationService.get_learning_recommendations(db=db, user=current_user, limit=limit)
    return RecommendationCategoryResponse(
        category="TRAINING_PROGRAM",
        total_count=len(items),
        items=items,
    )


@router.get(
    "/opportunities",
    response_model=RecommendationCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get recommended internship and placement opportunities",
    description="Returns opportunity recommendations based on hard eligibility filtering and skill compatibility.",
)
async def get_recommended_opportunities(
    limit: int = Query(10, ge=1, le=50, description="Limit count"),
    current_user: User = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    items = await RecommendationService.get_opportunity_recommendations(db=db, user=current_user, limit=limit)
    return RecommendationCategoryResponse(
        category="OPPORTUNITY",
        total_count=len(items),
        items=items,
    )


@router.get(
    "/mentors",
    response_model=RecommendationCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get recommended alumni and industry mentors",
    description="Returns mentor recommendations based on career domain alignment and professional profile overlap.",
)
async def get_recommended_mentors(
    limit: int = Query(10, ge=1, le=50, description="Limit count"),
    current_user: User = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    items = await RecommendationService.get_mentor_recommendations(db=db, user=current_user, limit=limit)
    return RecommendationCategoryResponse(
        category="MENTOR",
        total_count=len(items),
        items=items,
    )
