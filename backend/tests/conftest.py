"""Pytest configuration and shared fixtures for backend tests."""

import os
from collections.abc import Generator
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from backend.auth.jwt_middleware import CurrentUser
from backend.db import get_session
from backend.main import app
from backend.models.task import Task

# Test database configuration (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

# JWT test configuration
TEST_JWT_SECRET = "test-secret-key-for-testing-only"
TEST_JWT_ALGORITHM = "HS256"

# Override environment variables for testing
os.environ["JWT_SECRET"] = TEST_JWT_SECRET
os.environ["JWT_ALGORITHM"] = TEST_JWT_ALGORITHM
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


@pytest.fixture(name="engine")
def engine_fixture():
    """Create test database engine with in-memory SQLite.

    Uses StaticPool to keep the same in-memory database across connections.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session]:
    """Create test database session.

    Yields a fresh session for each test, automatically rolls back
    changes after the test completes.
    """
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient]:
    """Create FastAPI test client with test database session.

    Overrides the get_session dependency to use the test session.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user_id")
def test_user_id_fixture() -> UUID:
    """Generate a test user ID.

    Returns a consistent UUID for testing user-scoped operations.
    """
    return uuid4()


@pytest.fixture(name="test_user_id_2")
def test_user_id_2_fixture() -> UUID:
    """Generate a second test user ID.

    Used for testing user isolation and ownership validation.
    """
    return uuid4()


@pytest.fixture(name="test_jwt_token")
def test_jwt_token_fixture(test_user_id: UUID) -> str:
    """Generate a valid JWT token for testing.

    Creates a token with user_id claim and 1-hour expiration.

    Args:
        test_user_id: User ID to include in token

    Returns:
        str: Encoded JWT token
    """
    payload = {
        "sub": str(test_user_id),
        "user_id": str(test_user_id),
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm=TEST_JWT_ALGORITHM)


@pytest.fixture(name="test_jwt_token_2")
def test_jwt_token_2_fixture(test_user_id_2: UUID) -> str:
    """Generate a valid JWT token for second test user.

    Args:
        test_user_id_2: Second user ID to include in token

    Returns:
        str: Encoded JWT token
    """
    payload = {
        "sub": str(test_user_id_2),
        "user_id": str(test_user_id_2),
        "email": "test2@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm=TEST_JWT_ALGORITHM)


@pytest.fixture(name="expired_jwt_token")
def expired_jwt_token_fixture(test_user_id: UUID) -> str:
    """Generate an expired JWT token for testing.

    Args:
        test_user_id: User ID to include in token

    Returns:
        str: Encoded JWT token (expired)
    """
    payload = {
        "sub": str(test_user_id),
        "user_id": str(test_user_id),
        "email": "test@example.com",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
        "iat": datetime.utcnow() - timedelta(hours=2),
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm=TEST_JWT_ALGORITHM)


@pytest.fixture(name="current_user")
def current_user_fixture(test_user_id: UUID) -> CurrentUser:
    """Create a CurrentUser instance for testing.

    Args:
        test_user_id: User ID for the current user

    Returns:
        CurrentUser: Authenticated user object
    """
    return CurrentUser(user_id=test_user_id, email="test@example.com")


@pytest.fixture(name="sample_task")
def sample_task_fixture(session: Session, test_user_id: UUID) -> Task:
    """Create a sample task in the database for testing.

    Args:
        session: Database session
        test_user_id: User ID to associate with the task

    Returns:
        Task: Created task object
    """
    task = Task(
        user_id=test_user_id,
        title="Sample Task",
        description="This is a sample task for testing",
        priority="medium",
        status="pending",
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
