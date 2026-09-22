import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.users import User, UserProfile
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    MessageResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new SKILLY user",
    description="Registers a new platform user with an initial profile and assigns a canonical role.",
)
async def register_user(
    payload: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    # 1. Check if email already exists
    stmt_email = select(User).where(User.email == payload.email)
    existing_email_res = await db.execute(stmt_email)
    if existing_email_res.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # 2. Check and ensure unique username
    username_candidate = payload.username
    stmt_uname = select(User).where(User.username == username_candidate)
    existing_uname_res = await db.execute(stmt_uname)
    if existing_uname_res.scalar_one_or_none() is not None:
        # Append short random suffix if colliding
        username_candidate = f"{payload.username}_{uuid.uuid4().hex[:6]}"

    # 3. Hash password using Argon2
    hashed_pw = hash_password(payload.password)

    # 4. Create User entity with canonical role
    new_user = User(
        email=payload.email,
        username=username_candidate,
        hashed_password=hashed_pw,
        role=payload.role,
        is_active=True,
        is_verified=False,
    )
    db.add(new_user)
    await db.flush()

    # 5. Create associated UserProfile entity
    new_profile = UserProfile(
        user_id=new_user.id,
        first_name=payload.first_name or "User",
        last_name=payload.last_name or "",
        country="India",
    )
    db.add(new_profile)
    await db.commit()

    # 6. Reload user with profile relationship eagerly loaded
    stmt_load = (
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == new_user.id)
    )
    res = await db.execute(stmt_load)
    created_user = res.scalar_one()

    return created_user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and obtain JWT access token",
    description="Validates user credentials against stored Argon2 hash and issues a signed JWT token.",
)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    # 1. Query user by email with profile loaded
    stmt = (
        select(User)
        .options(selectinload(User.profile))
        .where(User.email == payload.email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # 2. Verify existence and password
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Check account active status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive or suspended. Please contact administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Create JWT token (minimal claims: sub=user.id, role=canonical db role, exp, iat, type)
    access_token = create_access_token(
        subject=user.id,
        role=user.role,
    )
    expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in_seconds,
        user=user,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
    description="Returns the profile and account details of the currently authenticated user.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Client logout acknowledgement",
    description=(
        "Current Phase 2.3 uses stateless access tokens. Client logout removes the stored token. "
        "Server-side token revocation is not implemented in this phase."
    ),
)
async def logout(
    current_user: User = Depends(get_current_user),
):
    return MessageResponse(
        message="Logged out successfully. Discard token on client.",
        status="ok",
    )
