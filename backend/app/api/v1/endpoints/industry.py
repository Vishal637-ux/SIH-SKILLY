import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.users import User
from app.services.industry_service import IndustryService
from app.schemas.industry import (
    CompanyProfileResponse,
    CompanyProfileUpdateRequest,
    OpportunityCreateRequest,
    OpportunityUpdateRequest,
    OpportunityItem,
    OpportunityListResponse,
    ApplicationListResponse,
    ApplicationItem,
    ApplicationStatusUpdateRequest,
    ApplicationStatusHistoryItem,
    InternshipItem,
    InternshipEvaluationRequest,
    InternshipEvaluationResponse,
    PlacementInteractionCreateRequest,
    PlacementInteractionItem,
    IndustryDashboardResponse,
    IndustryAnalyticsResponse,
)

router = APIRouter(prefix="/industry", tags=["Industry / Company Workspace"])


@router.get(
    "/profile",
    response_model=CompanyProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get corporate company profile",
)
async def get_company_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_company_profile(db, current_user)


@router.put(
    "/profile",
    response_model=CompanyProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update corporate company profile",
)
async def update_company_profile(
    payload: CompanyProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.update_company_profile(db, current_user, payload)


@router.get(
    "/dashboard",
    response_model=IndustryDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get live industry recruiter dashboard metrics",
)
async def get_company_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_company_dashboard(db, current_user)


@router.get(
    "/opportunities",
    response_model=OpportunityListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get company's posted opportunities",
)
async def get_company_opportunities(
    status: Optional[str] = Query(None, description="Filter by status (OPEN, CLOSED)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_company_opportunities(db, current_user, status)


@router.post(
    "/opportunities",
    response_model=OpportunityItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job or internship opportunity",
)
async def create_opportunity(
    payload: OpportunityCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.create_opportunity(db, current_user, payload)


@router.get(
    "/opportunities/{id}",
    response_model=OpportunityItem,
    status_code=status.HTTP_200_OK,
    summary="Get opportunity details",
)
async def get_opportunity_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_opportunity_detail(db, current_user, id)


@router.put(
    "/opportunities/{id}",
    response_model=OpportunityItem,
    status_code=status.HTTP_200_OK,
    summary="Update opportunity details",
)
async def update_opportunity(
    id: uuid.UUID,
    payload: OpportunityUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.update_opportunity(db, current_user, id, payload)


@router.delete(
    "/opportunities/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Close or deactivate opportunity",
)
async def delete_opportunity(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    await IndustryService.delete_opportunity(db, current_user, id)


@router.get(
    "/opportunities/{id}/applications",
    response_model=ApplicationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get applications for a specific opportunity",
)
async def get_opportunity_applications(
    id: uuid.UUID,
    status: Optional[str] = Query(None),
    min_cgpa: Optional[float] = Query(None),
    graduation_year: Optional[int] = Query(None),
    skill_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_company_applications(
        db,
        current_user,
        opportunity_id=id,
        status_filter=status,
        min_cgpa=min_cgpa,
        graduation_year=graduation_year,
        skill_id=skill_id,
    )


@router.get(
    "/applications",
    response_model=ApplicationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all applications across company opportunities",
)
async def get_company_applications(
    opportunity_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    min_cgpa: Optional[float] = Query(None),
    graduation_year: Optional[int] = Query(None),
    skill_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_company_applications(
        db,
        current_user,
        opportunity_id=opportunity_id,
        status_filter=status,
        min_cgpa=min_cgpa,
        graduation_year=graduation_year,
        skill_id=skill_id,
    )


@router.get(
    "/applications/{application_id}",
    response_model=ApplicationItem,
    status_code=status.HTTP_200_OK,
    summary="Get application detail",
)
async def get_application_detail(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_application_detail(db, current_user, application_id)


@router.put(
    "/applications/{application_id}/status",
    response_model=ApplicationItem,
    status_code=status.HTTP_200_OK,
    summary="Update application ATS status",
)
async def update_application_status(
    application_id: uuid.UUID,
    payload: ApplicationStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.update_application_status(db, current_user, application_id, payload)


@router.get(
    "/applications/{application_id}/history",
    response_model=List[ApplicationStatusHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get application status history audit log",
)
async def get_application_status_history(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_application_status_history(db, current_user, application_id)


@router.get(
    "/internships",
    response_model=List[InternshipItem],
    status_code=status.HTTP_200_OK,
    summary="Get company's active/completed internships",
)
async def get_company_internships(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_company_internships(db, current_user)


@router.post(
    "/internships/{id}/evaluations",
    response_model=InternshipEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit evaluation for intern",
)
async def submit_internship_evaluation(
    id: uuid.UUID,
    payload: InternshipEvaluationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.submit_internship_evaluation(db, current_user, id, payload)


@router.get(
    "/interactions",
    response_model=List[PlacementInteractionItem],
    status_code=status.HTTP_200_OK,
    summary="Get company's recruitment interactions",
)
async def get_company_interactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_company_interactions(db, current_user)


@router.post(
    "/interactions",
    response_model=PlacementInteractionItem,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule a recruitment interaction (Interview, GD, Drive)",
)
async def create_company_interaction(
    payload: PlacementInteractionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.create_company_interaction(db, current_user, payload)


@router.get(
    "/analytics",
    response_model=IndustryAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get industry hiring analytics and skill metrics",
)
async def get_company_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("INDUSTRY")),
):
    return await IndustryService.get_company_analytics(db, current_user)
