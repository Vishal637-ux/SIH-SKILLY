import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class SkillMatchItem(BaseModel):
    skill_id: uuid.UUID
    name: str
    category: Optional[str] = None
    proficiency: Optional[int] = None


class RecommendationItem(BaseModel):
    id: uuid.UUID
    category: str  # CAREER_ROLE, TRAINING_PROGRAM, OPPORTUNITY, MENTOR
    title: str
    subtitle: Optional[str] = None
    organization_or_provider: Optional[str] = None
    score: float  # 0.0 to 100.0
    matched_skills: List[str]
    skill_gaps: List[str]
    explanation: str
    eligibility: bool = True
    action_link: str

    model_config = ConfigDict(from_attributes=True)


class RecommendationOverviewResponse(BaseModel):
    student_id: uuid.UUID
    target_role_title: Optional[str] = None
    assessed_skills_count: int
    active_gaps_count: int
    career_recommendations: List[RecommendationItem]
    learning_recommendations: List[RecommendationItem]
    opportunity_recommendations: List[RecommendationItem]
    mentor_recommendations: List[RecommendationItem]


class RecommendationCategoryResponse(BaseModel):
    category: str
    total_count: int
    items: List[RecommendationItem]
