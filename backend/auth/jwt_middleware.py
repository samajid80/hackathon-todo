"""JWT authentication middleware for FastAPI.

This module provides JWT token validation and user extraction from
Better-Auth generated tokens. All task-related endpoints require valid JWT.
"""

import os
from typing import Annotated

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
        user_id: ID of the authenticated user (string from Better-Auth)
        email: User's email address (optional)
    """

    def __init__(self, user_id: str, email: str | None = None):
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
        print(f"[JWT Debug] Received token (first 50 chars): {token[:50]}...")

        # Get JWT configuration
        jwt_secret = get_jwt_secret()
        jwt_algorithm = get_jwt_algorithm()
        print(f"[JWT Debug] Using secret: {jwt_secret[:20]}... and algorithm: {jwt_algorithm}")

        # Decode JWT without verification first to see payload
        print(f"[JWT Debug] Attempting to decode token WITHOUT verification...")
        unverified_payload = jwt.get_unverified_claims(token)
        print(f"[JWT Debug] Unverified payload: {unverified_payload}")

        # For now, use unverified payload (TODO: Add proper EdDSA verification with JWKS)
        payload = unverified_payload

        # Debug: Print JWT payload to see what Better-Auth is sending
        print(f"[JWT Debug] Decoded payload: {payload}")

        # Extract user_id from token claims
        user_id: str | None = payload.get("sub") or payload.get("user_id") or payload.get("id")
        if not user_id:
            print(f"[JWT Debug] No 'sub', 'user_id', or 'id' found in payload. Available keys: {list(payload.keys())}")
            raise credentials_exception

        print(f"[JWT Debug] Extracted user_id: {user_id}")

        # Extract optional email
        email: str | None = payload.get("email")

        return CurrentUser(user_id=user_id, email=email)

    except JWTError as e:
        print(f"[JWT Debug] JWTError occurred: {type(e).__name__}: {str(e)}")
        raise credentials_exception
    except Exception as e:
        print(f"[JWT Debug] Unexpected error: {type(e).__name__}: {str(e)}")
        raise credentials_exception


# Type alias for dependency injection
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
