import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class AuthorInfo(BaseModel):
    user_id: uuid.UUID
    name: str
    avatar_url: Optional[str] = None
    role: str

    model_config = ConfigDict(from_attributes=True)


class CommunityCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    parent_comment_id: Optional[uuid.UUID] = None


class CommunityCommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommunityCommentRead(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    author: AuthorInfo
    parent_comment_id: Optional[uuid.UUID] = None
    content: str
    created_at: Any
    replies: List["CommunityCommentRead"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CommunityPostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=5)
    post_type: str = Field(default="GENERAL", description="GENERAL, DISCUSSION, RESOURCE, SHOWCASE")
    tags: Optional[List[str]] = Field(default_factory=list)


class CommunityPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    content: Optional[str] = Field(None, min_length=5)
    post_type: Optional[str] = None
    tags: Optional[List[str]] = None


class CommunityPostRead(BaseModel):
    id: uuid.UUID
    author: AuthorInfo
    title: str
    content: str
    post_type: str
    tags: Optional[Any] = None
    upvotes_count: int = 0
    created_at: Any
    comments_count: int = 0
    comments: List[CommunityCommentRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PeerSkillRequestCreate(BaseModel):
    skill_id: uuid.UUID
    request_type: str = Field(default="SEEKING_HELP", description="SEEKING_HELP or OFFERING_HELP")
    description: str = Field(..., min_length=5)


class PeerSkillRequestUpdate(BaseModel):
    status: Optional[str] = Field(None, description="OPEN, IN_PROGRESS, COMPLETED, CLOSED")
    helper_student_id: Optional[uuid.UUID] = None
    description: Optional[str] = None


class PeerSkillRequestRead(BaseModel):
    id: uuid.UUID
    requester_student_id: uuid.UUID
    requester_name: str
    helper_student_id: Optional[uuid.UUID] = None
    helper_name: Optional[str] = None
    skill_id: uuid.UUID
    skill_name: str
    request_type: str
    description: str
    status: str
    created_at: Any

    model_config = ConfigDict(from_attributes=True)


class ActivityRead(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    institution_name: str
    title: str
    description: str
    activity_type: str
    start_time: datetime
    end_time: datetime
    location_or_url: Optional[str] = None
    conducted_by_user_id: Optional[uuid.UUID] = None
    conducted_by_name: Optional[str] = None
    created_at: Any

    model_config = ConfigDict(from_attributes=True)
