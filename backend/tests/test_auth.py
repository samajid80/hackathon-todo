"""Tests for JWT authentication middleware."""

from uuid import UUID

import pytest
from fastapi import HTTPException

from backend.auth.jwt_middleware import get_current_user


class MockCredentials:
    """Mock HTTPAuthorizationCredentials for testing."""

    def __init__(self, token: str):
        self.credentials = token


def test_get_current_user_with_valid_token(test_jwt_token: str, test_user_id: UUID):
    """Test JWT validation with a valid token.

    Verifies that get_current_user correctly extracts user_id from a valid token.
    """
    credentials = MockCredentials(test_jwt_token)
    current_user = get_current_user(credentials)

    assert current_user.user_id == test_user_id
    assert current_user.email == "test@example.com"


def test_get_current_user_with_expired_token(expired_jwt_token: str):
    """Test JWT validation with an expired token.

    Verifies that get_current_user raises HTTPException for expired tokens.
    """
    credentials = MockCredentials(expired_jwt_token)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail


def test_get_current_user_with_invalid_token():
    """Test JWT validation with an invalid token.

    Verifies that get_current_user raises HTTPException for malformed tokens.
    """
    credentials = MockCredentials("invalid.token.here")

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail


def test_get_current_user_with_missing_user_id():
    """Test JWT validation with token missing user_id claim.

    Verifies that get_current_user raises HTTPException when token
    doesn't contain sub or user_id claim.
    """
    from datetime import datetime, timedelta

    from jose import jwt

    # Create token without user_id
    payload = {
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, "test-secret-key-for-testing-only", algorithm="HS256")
    credentials = MockCredentials(token)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail


def test_get_current_user_with_invalid_user_id_format():
    """Test JWT validation with invalid UUID format in user_id.

    Verifies that get_current_user raises HTTPException when user_id
    cannot be converted to UUID.
    """
    from datetime import datetime, timedelta

    from jose import jwt

    # Create token with invalid UUID
    payload = {
        "sub": "not-a-valid-uuid",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, "test-secret-key-for-testing-only", algorithm="HS256")
    credentials = MockCredentials(token)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail


def test_get_current_user_extracts_from_sub_claim(test_user_id: UUID):
    """Test that user_id is correctly extracted from 'sub' claim.

    Better-Auth typically uses 'sub' claim for user ID.
    """
    from datetime import datetime, timedelta

    from jose import jwt

    payload = {
        "sub": str(test_user_id),
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, "test-secret-key-for-testing-only", algorithm="HS256")
    credentials = MockCredentials(token)

    current_user = get_current_user(credentials)
    assert current_user.user_id == test_user_id


def test_get_current_user_extracts_from_user_id_claim(test_user_id: UUID):
    """Test that user_id is correctly extracted from 'user_id' claim.

    Fallback to 'user_id' claim if 'sub' is not present.
    """
    from datetime import datetime, timedelta

    from jose import jwt

    payload = {
        "user_id": str(test_user_id),
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, "test-secret-key-for-testing-only", algorithm="HS256")
    credentials = MockCredentials(token)

    current_user = get_current_user(credentials)
    assert current_user.user_id == test_user_id
