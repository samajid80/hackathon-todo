"""JWT authentication middleware for Phase 3 Backend.

Reuses Phase 2 pattern with EdDSA + JWKS support for Better-Auth tokens.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError

from app.config import settings


# JWKS client (cached automatically by PyJWT)
_jwks_client: PyJWKClient | None = None


def get_jwks_client() -> PyJWKClient:
    """
    Get or create JWKS client for Better Auth.

    Returns:
        PyJWKClient: Client for fetching and caching JWKS

    Raises:
        HTTPException: If JWKS client cannot be created
    """
    global _jwks_client

    if _jwks_client is not None:
        return _jwks_client

    try:
        # Construct JWKS URL for Phase 3 frontend (port 3001)
        # In production: https://phase3-frontend.vercel.app/api/auth/jwks
        # In development: http://localhost:3001/api/auth/jwks
        better_auth_url = "http://localhost:3001"  # Phase 3 frontend runs on port 3001
        if settings.cors_origins:
            # Use first CORS origin that contains port 3001 or "phase3"
            for origin in settings.cors_origins:
                if "3001" in origin or "phase3" in origin.lower():
                    better_auth_url = origin
                    break
        jwks_url = f"{better_auth_url}/api/auth/jwks"

        print(f"[Phase3 JWKS] Initializing JWKS client for {jwks_url}")

        # PyJWKClient automatically caches JWKS and refreshes when needed
        _jwks_client = PyJWKClient(
            jwks_url,
            cache_keys=True,
            max_cached_keys=16,
            cache_jwk_set=True,
            lifespan=3600  # Cache for 1 hour
        )

        return _jwks_client

    except Exception as e:
        print(f"[JWKS] Failed to create JWKS client: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to initialize JWKS client: {str(e)}"
        )


# HTTP Bearer token scheme for FastAPI
security = HTTPBearer()


class CurrentUser:
    """
    Represents the authenticated user from JWT token.

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
    """
    Extract and validate user from EdDSA JWT token using JWKS.

    This dependency validates the JWT token from the Authorization header
    using the public key from Better Auth's JWKS endpoint and extracts
    the user_id claim.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        CurrentUser: Authenticated user with user_id

    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or missing user_id

    Usage:
        @app.post("/api/{user_id}/chat")
        async def chat(
            user_id: str,
            current_user: CurrentUser = Depends(get_current_user)
        ):
            # Verify user_id in URL matches authenticated user
            if current_user.user_id != user_id:
                raise HTTPException(403, "Forbidden")
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

        # Get JWKS client (cached)
        jwks_client = get_jwks_client()

        # Get the signing key from JWKS based on token's kid
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Decode and verify JWT token using public key
        # PyJWT automatically handles EdDSA, ES256, RS256, etc.
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "ES256", "ES384", "ES512", "RS256", "HS256"],
            options={"verify_aud": False}  # Better Auth doesn't always set audience
        )

        # Extract user_id from token claims
        # Better Auth uses 'sub' for user ID
        user_id: str | None = payload.get("sub") or payload.get("user_id") or payload.get("id")
        if not user_id:
            print(f"[JWT Debug] No 'sub', 'user_id', or 'id' found in payload. Available keys: {list(payload.keys())}")
            raise credentials_exception

        # Extract optional email
        email: str | None = payload.get("email")

        print(f"[JWT] Successfully validated token for user_id={user_id}")
        return CurrentUser(user_id=user_id, email=email)

    except HTTPException:
        # Re-raise HTTP exceptions (JWKS fetch errors, etc.)
        raise
    except PyJWTError as e:
        print(f"[JWT Debug] PyJWTError occurred: {type(e).__name__}: {str(e)}")
        raise credentials_exception
    except Exception as e:
        print(f"[JWT Debug] Unexpected error: {type(e).__name__}: {str(e)}")
        raise credentials_exception


# Type alias for dependency injection
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
