import uuid
from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.security import decode_access_token
from app.dependencies.database import get_db
from app.models.users import User
from app.schemas.auth import normalize_role

# OAuth2 scheme for extracting Bearer tokens from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extracts Bearer token, validates JWT signature and expiration, loads the user
    from PostgreSQL, and verifies account status (is_active).
    
    IMPORTANT: Authorization MUST use the current live user record from PostgreSQL,
    not stale or spoofed claims from the JWT.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials: missing subject claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials: malformed user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Load fresh user record from PostgreSQL with profile eagerly loaded
    stmt = (
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == user_uuid)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check account status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive or suspended. Please contact administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensures the authenticated user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
        )
    return current_user


def require_roles(*allowed_roles: str) -> Callable:
    """
    Role-Based Access Control (RBAC) dependency factory.
    Enforces authorization on the backend using the live database role.
    """
    # Pre-normalize the allowed roles to canonical database representation
    canonical_allowed = {normalize_role(r) for r in allowed_roles}

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_db_role = current_user.role.upper() if current_user.role else ""
        if user_db_role not in canonical_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access forbidden: User role '{current_user.role}' does not have permission "
                    f"to access this resource. Required role(s): {', '.join(sorted(canonical_allowed))}."
                ),
            )
        return current_user

    return role_checker


def require_role(role: str) -> Callable:
    """Convenience wrapper for a single required role."""
    return require_roles(role)
