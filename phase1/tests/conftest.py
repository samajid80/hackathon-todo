"""Pytest configuration and fixtures."""

import pytest

from src.storage.repository import InMemoryTaskRepository
from src.domain.task import Task
from src.domain.enums import Priority, Status


@pytest.fixture
def repository() -> InMemoryTaskRepository:
    """Create a fresh repository for each test."""
    return InMemoryTaskRepository()


@pytest.fixture
def sample_task() -> Task:
    """Create a sample task for testing."""
    return Task(
        title="Buy groceries",
        description="Get milk, bread, eggs",
        due_date="2025-12-10",
        priority=Priority.HIGH,
        status=Status.PENDING,
    )
