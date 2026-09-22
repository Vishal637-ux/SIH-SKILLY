import uuid
import re
from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict


class UserRole(str, Enum):
    """Canonical database roles for SKILLY platform."""
    STUDENT = "STUDENT"
    COLLEGE_ADMIN = "COLLEGE_ADMIN"
    TEACHER = "TEACHER"
    INDUSTRY = "INDUSTRY"
    ALUMNI = "ALUMNI"


# Mapping from accepted registration UI/API aliases to canonical database role values
ROLE_ALIASES = {
    "student": UserRole.STUDENT,
    "college": UserRole.COLLEGE_ADMIN,
    "college_admin": UserRole.COLLEGE_ADMIN,
    "tpo": UserRole.COLLEGE_ADMIN,
    "teacher": UserRole.TEACHER,
    "trainer": UserRole.TEACHER,
    "industry": UserRole.INDUSTRY,
    "company": UserRole.INDUSTRY,
    "alumni": UserRole.ALUMNI,
    "mentor": UserRole.ALUMNI,
}


def normalize_role(role_input: str) -> str:
    """Normalize input role strings into canonical database uppercase role values."""
    if not role_input or not isinstance(role_input, str):
        raise ValueError("Role must be a non-empty string")
    cleaned = role_input.strip().lower()
    if cleaned in ROLE_ALIASES:
        return ROLE_ALIASES[cleaned].value
    
    upper = role_input.strip().upper()
    valid_roles = {r.value for r in UserRole}
    if upper in valid_roles:
        return upper

    valid_display = sorted(valid_roles)
    raise ValueError(f"Invalid role '{role_input}'. Canonical roles are: {', '.join(valid_display)}")


class UserRegister(BaseModel):
    """User registration schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Password must be at least 8 characters")
    role: str = Field(default=UserRole.STUDENT.value, description="Platform role (canonical or alias)")
    fullName: Optional[str] = Field(default=None, description="Full name string (will be split into first_name and last_name)")
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    username: Optional[str] = Field(default=None, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("role")
    @classmethod
    def validate_and_normalize_role(cls, v: str) -> str:
        return normalize_role(v)

    @model_validator(mode="after")
    def populate_names_and_username(self) -> "UserRegister":
        # Extract first_name and last_name from fullName if not provided explicitly
        if self.fullName and (not self.first_name or not self.last_name):
            parts = self.fullName.strip().split(maxsplit=1)
            if parts:
                self.first_name = parts[0]
                self.last_name = parts[1] if len(parts) > 1 else ""
            else:
                self.first_name = "User"
                self.last_name = ""
        elif not self.first_name:
            self.first_name = self.email.split("@")[0]
            self.last_name = ""

        if not self.last_name:
            self.last_name = ""

        # Auto-generate username from email if not specified
        if not self.username:
            clean_email_prefix = re.sub(r"[^a-zA-Z0-9_]", "_", self.email.split("@")[0])[:50]
            self.username = clean_email_prefix

        return self


class UserLogin(BaseModel):
    """User login request schema. Strictly accepts email and password only."""
    email: EmailStr
    password: str = Field(..., min_length=1, description="Account password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserProfileResponse(BaseModel):
    """Safe public user profile data."""
    id: uuid.UUID
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Safe user information response schema. Never includes password or password hash."""
    id: uuid.UUID
    email: str
    username: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime] = None
    profile: Optional[UserProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user: UserResponse


class MessageResponse(BaseModel):
    """Generic status response schema."""
    message: str
    status: str = "ok"
