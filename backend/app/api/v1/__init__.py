from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.student import router as student_router
from app.api.v1.endpoints.college import router as college_router
from app.api.v1.endpoints.teacher import router as teacher_router
from app.api.v1.endpoints.industry import router as industry_router
from app.api.v1.endpoints.alumni import router as alumni_router
from app.api.v1.endpoints.skills import router as skills_router
from app.api.v1.endpoints.community import router as community_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.recommendations import router as recommendations_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(student_router)
api_v1_router.include_router(college_router)
api_v1_router.include_router(teacher_router)
api_v1_router.include_router(industry_router)
api_v1_router.include_router(alumni_router)
api_v1_router.include_router(skills_router)
api_v1_router.include_router(community_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(recommendations_router)

__all__ = ["api_v1_router"]


