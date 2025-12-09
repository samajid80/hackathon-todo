"""Tests for the TaskService."""

import pytest

from src.services.task_service import TaskService
from src.storage.repository import InMemoryTaskRepository
from src.domain.enums import Priority, Status


def test_create_task_success() -> None:
    """Test successful task creation."""
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    success, message, task = service.create_task(title="Buy groceries")

    assert success is True
    assert "created with ID" in message
    assert task is not None
    assert task.title == "Buy groceries"


def test_create_task_with_all_fields() -> None:
    """Test task creation with all fields."""
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    success, message, task = service.create_task(
        title="Team meeting",
        description="Discuss Q4",
        due_date="2025-12-15",
        priority=Priority.HIGH,
    )

    assert success is True
    assert task is not None
    assert task.title == "Team meeting"
    assert task.priority == Priority.HIGH


def test_create_task_invalid_title() -> None:
    """Test task creation with invalid title."""
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    success, message, task = service.create_task(title="")

    assert success is False
    assert "Title is required" in message
    assert task is None


def test_list_tasks_empty() -> None:
    """Test listing tasks when repository is empty."""
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    tasks = service.list_tasks()

    assert len(tasks) == 0


def test_list_tasks_with_filter_status() -> None:
    """Test listing tasks with status filter."""
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    service.create_task(title="Task 1")
    success, _, task = service.create_task(title="Task 2")
    if success and task:
        service.complete_task(task.id)

    pending_tasks = service.list_tasks(filter_status=Status.PENDING)
    completed_tasks = service.list_tasks(filter_status=Status.COMPLETED)

    assert len(pending_tasks) == 1
    assert len(completed_tasks) == 1


def test_complete_task() -> None:
    """Test marking a task as completed."""
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    success, _, task = service.create_task(title="Buy groceries")
    assert task is not None

    success, message, _ = service.complete_task(task.id)

    assert success is True
    assert "completed" in message
    assert repository.get(task.id).status == Status.COMPLETED


def test_complete_already_completed_task() -> None:
    """Test that completing an already completed task is idempotent."""
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    success, _, task = service.create_task(title="Test")
    assert task is not None

    service.complete_task(task.id)
    success, message, _ = service.complete_task(task.id)

    assert success is True
    assert "already completed" in message


def test_delete_task() -> None:
    """Test deleting a task."""
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    success, _, task = service.create_task(title="To delete")
    assert task is not None

    success, message, _ = service.delete_task(task.id)

    assert success is True
    assert "deleted" in message
    assert not repository.exists(task.id)


def test_delete_nonexistent_task() -> None:
    """Test deleting a task that doesn't exist."""
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    success, message, _ = service.delete_task("nonexistent-id")

    assert success is False
    assert "not found" in message
