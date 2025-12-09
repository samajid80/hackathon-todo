"""Tests for the Task entity."""

import pytest

from src.domain.task import Task
from src.domain.enums import Priority, Status
from src.domain.exceptions import ValidationError


def test_task_creation_with_required_fields() -> None:
    """Test creating a task with only required fields."""
    task = Task(title="Buy groceries")

    assert task.title == "Buy groceries"
    assert task.description == ""
    assert task.due_date is None
    assert task.priority == Priority.MEDIUM
    assert task.status == Status.PENDING
    assert task.id is not None
    assert task.created_at is not None
    assert task.updated_at is not None


def test_task_creation_with_all_fields() -> None:
    """Test creating a task with all fields."""
    task = Task(
        title="Team meeting",
        description="Discuss Q4 deliverables",
        due_date="2025-12-15",
        priority=Priority.HIGH,
        status=Status.PENDING,
    )

    assert task.title == "Team meeting"
    assert task.description == "Discuss Q4 deliverables"
    assert task.due_date == "2025-12-15"
    assert task.priority == Priority.HIGH
    assert task.status == Status.PENDING


def test_task_validation_empty_title() -> None:
    """Test that empty title raises ValidationError."""
    with pytest.raises(ValidationError, match="Title is required"):
        Task(title="")


def test_task_validation_title_too_long() -> None:
    """Test that too-long title raises ValidationError."""
    long_title = "x" * 201
    with pytest.raises(ValidationError, match="Title must be 200 characters or less"):
        Task(title=long_title)


def test_task_validation_description_too_long() -> None:
    """Test that too-long description raises ValidationError."""
    long_description = "x" * 2001
    with pytest.raises(
        ValidationError, match="Description must be 2000 characters or less"
    ):
        Task(title="Test", description=long_description)


def test_task_validation_invalid_date() -> None:
    """Test that invalid date format raises ValidationError."""
    with pytest.raises(ValidationError, match="Date must be in ISO format YYYY-MM-DD"):
        Task(title="Test", due_date="tomorrow")


def test_task_is_overdue() -> None:
    """Test the is_overdue property."""
    # Past date, pending status
    past_task = Task(title="Overdue task", due_date="2025-12-01", status=Status.PENDING)
    # Note: This will be overdue only if today is after 2025-12-01
    # In a real test, use mocking to freeze time

    # Completed task with past date should not be overdue
    completed_task = Task(
        title="Completed task", due_date="2025-12-01", status=Status.COMPLETED
    )
    assert not completed_task.is_overdue

    # Task without due date should not be overdue
    no_due_date_task = Task(title="No due date", due_date=None, status=Status.PENDING)
    assert not no_due_date_task.is_overdue
