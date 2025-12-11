"""JWT authentication middleware for FastAPI.

This module provides JWT token validation and user extraction from
Better-Auth generated tokens. All task-related endpoints require valid JWT.
"""

import os
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt


def get_jwt_secret() -> str:
    """Get JWT secret from environment, with validation.

    Returns:
        str: JWT secret key

    Raises:
        ValueError: If JWT_SECRET is not set (in non-test environment)
    """
    secret = os.getenv("JWT_SECRET", "")
    if not secret:
        raise ValueError(
            "JWT_SECRET environment variable is not set. "
            "Please configure it in .env file or environment. "
            "It must match the BETTER_AUTH_SECRET in the frontend."
        )
    return secret


def get_jwt_algorithm() -> str:
    """Get JWT algorithm from environment.

    Returns:
        str: JWT algorithm (default: HS256)
    """
    return os.getenv("JWT_ALGORITHM", "HS256")


# HTTP Bearer token scheme for FastAPI
security = HTTPBearer()


class CurrentUser:
    """Represents the authenticated user from JWT token.

    Attributes:
        user_id: UUID of the authenticated user
        email: User's email address (optional)
    """

    def __init__(self, user_id: UUID, email: str | None = None):
        self.user_id = user_id
        self.email = email


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> CurrentUser:
    """Extract and validate user from JWT token.

    This dependency validates the JWT token from the Authorization header
    and extracts the user_id claim. Use this dependency on all protected
    endpoints to ensure user authentication.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        CurrentUser: Authenticated user with user_id

    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or missing user_id

    Usage:
        @app.get("/api/tasks")
        def get_tasks(current_user: CurrentUser = Depends(get_current_user)):
            user_id = current_user.user_id
            ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials

        # Get JWT configuration
        jwt_secret = get_jwt_secret()
        jwt_algorithm = get_jwt_algorithm()

        # Decode and validate JWT
        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])

        # Extract user_id from token claims
        user_id_str: str | None = payload.get("sub") or payload.get("user_id")
        if user_id_str is None:
            raise credentials_exception

        # Convert user_id to UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise credentials_exception

        # Extract optional email
        email: str | None = payload.get("email")

        return CurrentUser(user_id=user_id, email=email)

    except JWTError:
        raise credentials_exception


# Type alias for dependency injection
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
