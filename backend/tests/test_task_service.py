"""Tests for task service layer (T069-T071, T090-T095).

These tests validate the business logic for task CRUD operations,
including user isolation, ownership validation, and proper error handling.
"""

from datetime import date, timedelta
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlmodel import Session

from backend.models.enums import Priority, SortOrder, Status, TaskSortBy, TaskStatusFilter
from backend.models.task import Task, TaskCreate, TaskUpdate
from backend.services import task_service

# T069: Write unit tests for create_task service


async def test_create_task_success(session: Session, test_user_id: UUID):
    """Test creating a task with valid TaskCreate data.

    Validates:
    - Task is saved to database
    - user_id is correctly associated
    - Timestamps are set (created_at, updated_at)
    - Defaults applied (priority=medium, status=pending)
    """
    # Arrange
    task_data = TaskCreate(
        title="Complete project proposal",
        description="Write and submit the Q1 project proposal",
        due_date=date.today() + timedelta(days=7),
        priority=Priority.HIGH,
    )

    # Act
    task = await task_service.create_task(
        session=session,
        user_id=test_user_id,
        task_create=task_data,
    )

    # Assert
    assert task.id is not None
    assert task.user_id == test_user_id
    assert task.title == "Complete project proposal"
    assert task.description == "Write and submit the Q1 project proposal"
    assert task.due_date == date.today() + timedelta(days=7)
    assert task.priority == Priority.HIGH
    assert task.status == Status.PENDING  # Default
    assert task.created_at is not None
    assert task.updated_at is not None
    # Timestamps should be very close (within 1 second)
    time_diff = abs((task.created_at - task.updated_at).total_seconds())
    assert time_diff < 1

    # Verify task is in database
    db_task = session.get(Task, task.id)
    assert db_task is not None
    assert db_task.id == task.id
    assert db_task.user_id == test_user_id


async def test_create_task_with_defaults(session: Session, test_user_id: UUID):
    """Test creating a task with minimal data (defaults applied).

    Validates:
    - Only title required
    - priority defaults to MEDIUM
    - status defaults to PENDING
    - description and due_date can be None
    """
    # Arrange - minimal task with only title
    task_data = TaskCreate(title="Simple task")

    # Act
    task = await task_service.create_task(
        session=session,
        user_id=test_user_id,
        task_create=task_data,
    )

    # Assert
    assert task.title == "Simple task"
    assert task.description is None
    assert task.due_date is None
    assert task.priority == Priority.MEDIUM  # Default
    assert task.status == Status.PENDING  # Default
    assert task.user_id == test_user_id


async def test_create_task_with_empty_title(session: Session, test_user_id: UUID):
    """Test that empty title raises ValueError.

    Validates:
    - Empty string title is rejected
    - Appropriate error message
    """
    # Arrange - task with empty title
    task_data = TaskCreate(title="   ")  # Whitespace only

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await task_service.create_task(
            session=session,
            user_id=test_user_id,
            task_create=task_data,
        )

    assert "cannot be empty" in str(exc_info.value).lower()


async def test_create_task_missing_title():
    """Test that missing title raises ValidationError.

    Validates:
    - Pydantic validation catches missing required field
    - Appropriate error message
    """
    # Act & Assert - Pydantic validation should fail
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(description="Task without title")

    # Verify error mentions title field
    assert "title" in str(exc_info.value).lower()


async def test_create_task_title_too_long():
    """Test that title exceeding max length raises ValidationError.

    Validates:
    - Pydantic validation enforces max_length=200
    """
    # Arrange - title with 201 characters
    long_title = "x" * 201

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title=long_title)

    error_str = str(exc_info.value).lower()
    assert "title" in error_str
    assert "200" in error_str or "length" in error_str


async def test_create_task_description_too_long():
    """Test that description exceeding max length raises ValidationError.

    Validates:
    - Pydantic validation enforces max_length=2000
    """
    # Arrange - description with 2001 characters
    long_description = "x" * 2001

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="Valid title", description=long_description)

    error_str = str(exc_info.value).lower()
    assert "description" in error_str


async def test_create_task_trims_whitespace(session: Session, test_user_id: UUID):
    """Test that title and description are trimmed of whitespace.

    Validates:
    - Leading/trailing whitespace removed
    """
    # Arrange
    task_data = TaskCreate(
        title="  Task with spaces  ",
        description="  Description with spaces  ",
    )

    # Act
    task = await task_service.create_task(
        session=session,
        user_id=test_user_id,
        task_create=task_data,
    )

    # Assert
    assert task.title == "Task with spaces"
    assert task.description == "Description with spaces"


# T070: Write unit tests for get_user_tasks service


async def test_get_user_tasks_returns_all_tasks(session: Session, test_user_id: UUID):
    """Test getting all tasks for a user.

    Validates:
    - All user's tasks are returned
    - Tasks ordered by created_at DESC (newest first)
    """
    # Arrange - create 3 tasks for user
    task1 = Task(
        user_id=test_user_id,
        title="Task 1",
        priority=Priority.LOW,
        status=Status.PENDING,
    )
    session.add(task1)
    session.commit()

    task2 = Task(
        user_id=test_user_id,
        title="Task 2",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    session.add(task2)
    session.commit()

    task3 = Task(
        user_id=test_user_id,
        title="Task 3",
        priority=Priority.HIGH,
        status=Status.COMPLETED,
    )
    session.add(task3)
    session.commit()

    # Act
    tasks = await task_service.get_user_tasks(session=session, user_id=test_user_id)

    # Assert
    assert len(tasks) == 3
    assert tasks[0].title == "Task 3"  # Newest first
    assert tasks[1].title == "Task 2"
    assert tasks[2].title == "Task 1"
    # Verify ordering: created_at DESC
    assert tasks[0].created_at >= tasks[1].created_at
    assert tasks[1].created_at >= tasks[2].created_at


async def test_get_user_tasks_returns_empty_list(session: Session, test_user_id: UUID):
    """Test getting tasks for user with no tasks.

    Validates:
    - Empty list returned (not None)
    - No errors raised
    """
    # Act - no tasks created
    tasks = await task_service.get_user_tasks(session=session, user_id=test_user_id)

    # Assert
    assert tasks == []
    assert isinstance(tasks, list)


async def test_get_user_tasks_excludes_other_users_tasks(
    session: Session, test_user_id: UUID, test_user_id_2: UUID
):
    """Test that users only see their own tasks.

    Validates:
    - User A's tasks not visible to User B
    - User B's tasks not visible to User A
    - Complete user isolation
    """
    # Arrange - create tasks for both users
    task_a1 = Task(
        user_id=test_user_id,
        title="User A Task 1",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    task_a2 = Task(
        user_id=test_user_id,
        title="User A Task 2",
        priority=Priority.HIGH,
        status=Status.PENDING,
    )
    task_b1 = Task(
        user_id=test_user_id_2,
        title="User B Task 1",
        priority=Priority.LOW,
        status=Status.COMPLETED,
    )
    task_b2 = Task(
        user_id=test_user_id_2,
        title="User B Task 2",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )

    session.add_all([task_a1, task_a2, task_b1, task_b2])
    session.commit()

    # Act - get tasks for each user
    tasks_a = await task_service.get_user_tasks(session=session, user_id=test_user_id)
    tasks_b = await task_service.get_user_tasks(session=session, user_id=test_user_id_2)

    # Assert - User A sees only their tasks
    assert len(tasks_a) == 2
    assert all(task.user_id == test_user_id for task in tasks_a)
    assert all("User A" in task.title for task in tasks_a)

    # Assert - User B sees only their tasks
    assert len(tasks_b) == 2
    assert all(task.user_id == test_user_id_2 for task in tasks_b)
    assert all("User B" in task.title for task in tasks_b)

    # Assert - No overlap
    task_a_ids = {task.id for task in tasks_a}
    task_b_ids = {task.id for task in tasks_b}
    assert task_a_ids.isdisjoint(task_b_ids)


# T071: Write unit tests for get_task_by_id with ownership validation


async def test_get_task_by_id_owned_by_user(session: Session, test_user_id: UUID):
    """Test getting a task owned by the requesting user.

    Validates:
    - Task returned when owned by user
    - All task fields present
    """
    # Arrange - create task for user
    task = Task(
        user_id=test_user_id,
        title="User's task",
        description="This task belongs to the user",
        priority=Priority.HIGH,
        status=Status.PENDING,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Act
    retrieved_task = await task_service.get_task_by_id(
        session=session,
        task_id=task.id,
        user_id=test_user_id,
    )

    # Assert
    assert retrieved_task is not None
    assert retrieved_task.id == task.id
    assert retrieved_task.user_id == test_user_id
    assert retrieved_task.title == "User's task"
    assert retrieved_task.description == "This task belongs to the user"


async def test_get_task_by_id_not_owned_by_user(
    session: Session, test_user_id: UUID, test_user_id_2: UUID
):
    """Test getting a task NOT owned by the requesting user.

    Validates:
    - None returned when task owned by different user
    - Security: doesn't reveal task existence
    """
    # Arrange - create task for User A
    task = Task(
        user_id=test_user_id,
        title="User A's task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Act - User B tries to access User A's task
    retrieved_task = await task_service.get_task_by_id(
        session=session,
        task_id=task.id,
        user_id=test_user_id_2,  # Different user
    )

    # Assert - None returned (not accessible)
    assert retrieved_task is None


async def test_get_task_by_id_does_not_exist(session: Session, test_user_id: UUID):
    """Test getting a task that doesn't exist.

    Validates:
    - None returned for non-existent task_id
    - No errors raised
    """
    from uuid import uuid4

    # Arrange - use random UUID that doesn't exist
    non_existent_id = uuid4()

    # Act
    retrieved_task = await task_service.get_task_by_id(
        session=session,
        task_id=non_existent_id,
        user_id=test_user_id,
    )

    # Assert
    assert retrieved_task is None


# T090: Write unit tests for status filter (pending, completed, overdue)


async def test_filter_by_status_pending(session: Session, test_user_id: UUID):
    """Test filtering tasks by status=pending.

    Validates:
    - Only pending tasks returned
    - Completed tasks excluded
    """
    # Arrange - create mixed status tasks
    pending_task = Task(
        user_id=test_user_id,
        title="Pending task",
        status=Status.PENDING,
        priority=Priority.MEDIUM,
    )
    completed_task = Task(
        user_id=test_user_id,
        title="Completed task",
        status=Status.COMPLETED,
        priority=Priority.MEDIUM,
    )
    session.add_all([pending_task, completed_task])
    session.commit()

    # Act
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
        status=TaskStatusFilter.PENDING,
    )

    # Assert
    assert len(tasks) == 1
    assert tasks[0].status == Status.PENDING
    assert tasks[0].title == "Pending task"


async def test_filter_by_status_completed(session: Session, test_user_id: UUID):
    """Test filtering tasks by status=completed.

    Validates:
    - Only completed tasks returned
    - Pending tasks excluded
    """
    # Arrange - create mixed status tasks
    pending_task = Task(
        user_id=test_user_id,
        title="Pending task",
        status=Status.PENDING,
        priority=Priority.MEDIUM,
    )
    completed_task = Task(
        user_id=test_user_id,
        title="Completed task",
        status=Status.COMPLETED,
        priority=Priority.MEDIUM,
    )
    session.add_all([pending_task, completed_task])
    session.commit()

    # Act
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
        status=TaskStatusFilter.COMPLETED,
    )

    # Assert
    assert len(tasks) == 1
    assert tasks[0].status == Status.COMPLETED
    assert tasks[0].title == "Completed task"


async def test_filter_by_status_overdue(session: Session, test_user_id: UUID):
    """Test filtering tasks by status=overdue (T078).

    Validates:
    - Only overdue tasks returned (pending with due_date < today)
    - Pending tasks with future due_date excluded
    - Pending tasks with NULL due_date excluded
    - Completed tasks with past due_date excluded
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # Arrange - create tasks with various states
    overdue_task = Task(
        user_id=test_user_id,
        title="Overdue task",
        status=Status.PENDING,
        due_date=yesterday,
        priority=Priority.HIGH,
    )
    future_task = Task(
        user_id=test_user_id,
        title="Future task",
        status=Status.PENDING,
        due_date=tomorrow,
        priority=Priority.MEDIUM,
    )
    pending_no_date = Task(
        user_id=test_user_id,
        title="Pending no date",
        status=Status.PENDING,
        due_date=None,
        priority=Priority.LOW,
    )
    completed_overdue = Task(
        user_id=test_user_id,
        title="Completed but was overdue",
        status=Status.COMPLETED,
        due_date=yesterday,
        priority=Priority.MEDIUM,
    )

    session.add_all([overdue_task, future_task, pending_no_date, completed_overdue])
    session.commit()

    # Act
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
        status=TaskStatusFilter.OVERDUE,
    )

    # Assert
    assert len(tasks) == 1
    assert tasks[0].title == "Overdue task"
    assert tasks[0].status == Status.PENDING
    assert tasks[0].due_date < today


# T091: Write unit tests for sort_by parameter


async def test_sort_by_due_date_asc(session: Session, test_user_id: UUID):
    """Test sorting tasks by due_date ascending (T079).

    Validates:
    - Tasks sorted by due_date (earliest first)
    - NULL due_dates appear last
    """
    today = date.today()

    # Arrange
    task1 = Task(
        user_id=test_user_id,
        title="Due tomorrow",
        due_date=today + timedelta(days=1),
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    task2 = Task(
        user_id=test_user_id,
        title="Due next week",
        due_date=today + timedelta(days=7),
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    task3 = Task(
        user_id=test_user_id,
        title="No due date",
        due_date=None,
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )

    session.add_all([task2, task3, task1])  # Add in random order
    session.commit()

    # Act
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
        sort_by=TaskSortBy.DUE_DATE,
        order=SortOrder.ASC,
    )

    # Assert
    assert len(tasks) == 3
    assert tasks[0].title == "Due tomorrow"
    assert tasks[1].title == "Due next week"
    assert tasks[2].title == "No due date"  # NULL last


async def test_sort_by_due_date_desc(session: Session, test_user_id: UUID):
    """Test sorting tasks by due_date descending (T079).

    Validates:
    - Tasks sorted by due_date (latest first)
    - NULL due_dates appear last
    """
    today = date.today()

    # Arrange
    task1 = Task(
        user_id=test_user_id,
        title="Due tomorrow",
        due_date=today + timedelta(days=1),
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    task2 = Task(
        user_id=test_user_id,
        title="Due next week",
        due_date=today + timedelta(days=7),
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    task3 = Task(
        user_id=test_user_id,
        title="No due date",
        due_date=None,
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )

    session.add_all([task1, task3, task2])  # Add in random order
    session.commit()

    # Act
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
        sort_by=TaskSortBy.DUE_DATE,
        order=SortOrder.DESC,
    )

    # Assert
    assert len(tasks) == 3
    assert tasks[0].title == "Due next week"
    assert tasks[1].title == "Due tomorrow"
    assert tasks[2].title == "No due date"  # NULL last


async def test_sort_by_priority_desc(session: Session, test_user_id: UUID):
    """Test sorting tasks by priority descending (high → medium → low).

    Validates:
    - High priority tasks first
    - Medium priority tasks second
    - Low priority tasks last
    """
    # Arrange
    low_task = Task(
        user_id=test_user_id,
        title="Low priority",
        priority=Priority.LOW,
        status=Status.PENDING,
    )
    high_task = Task(
        user_id=test_user_id,
        title="High priority",
        priority=Priority.HIGH,
        status=Status.PENDING,
    )
    medium_task = Task(
        user_id=test_user_id,
        title="Medium priority",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )

    session.add_all([low_task, medium_task, high_task])  # Random order
    session.commit()

    # Act
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
        sort_by=TaskSortBy.PRIORITY,
        order=SortOrder.DESC,
    )

    # Assert
    assert len(tasks) == 3
    assert tasks[0].priority == Priority.HIGH
    assert tasks[1].priority == Priority.MEDIUM
    assert tasks[2].priority == Priority.LOW


async def test_sort_by_priority_asc(session: Session, test_user_id: UUID):
    """Test sorting tasks by priority ascending (low → medium → high).

    Validates:
    - Low priority tasks first
    - Medium priority tasks second
    - High priority tasks last
    """
    # Arrange
    low_task = Task(
        user_id=test_user_id,
        title="Low priority",
        priority=Priority.LOW,
        status=Status.PENDING,
    )
    high_task = Task(
        user_id=test_user_id,
        title="High priority",
        priority=Priority.HIGH,
        status=Status.PENDING,
    )
    medium_task = Task(
        user_id=test_user_id,
        title="Medium priority",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )

    session.add_all([high_task, low_task, medium_task])  # Random order
    session.commit()

    # Act
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
        sort_by=TaskSortBy.PRIORITY,
        order=SortOrder.ASC,
    )

    # Assert
    assert len(tasks) == 3
    assert tasks[0].priority == Priority.LOW
    assert tasks[1].priority == Priority.MEDIUM
    assert tasks[2].priority == Priority.HIGH


async def test_sort_by_status(session: Session, test_user_id: UUID):
    """Test sorting tasks by status.

    Validates:
    - Tasks sorted by status field
    """
    # Arrange
    pending_task = Task(
        user_id=test_user_id,
        title="Pending task",
        status=Status.PENDING,
        priority=Priority.MEDIUM,
    )
    completed_task = Task(
        user_id=test_user_id,
        title="Completed task",
        status=Status.COMPLETED,
        priority=Priority.MEDIUM,
    )

    session.add_all([completed_task, pending_task])
    session.commit()

    # Act - ASC should be completed before pending
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
        sort_by=TaskSortBy.STATUS,
        order=SortOrder.ASC,
    )

    # Assert
    assert len(tasks) == 2
    assert tasks[0].status == Status.COMPLETED
    assert tasks[1].status == Status.PENDING


async def test_sort_by_created_at_default(session: Session, test_user_id: UUID):
    """Test default sorting by created_at DESC.

    Validates:
    - When no sort_by specified, sorts by created_at DESC
    - Newest tasks first
    """
    # Arrange - create tasks in sequence
    task1 = Task(
        user_id=test_user_id,
        title="First task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    session.add(task1)
    session.commit()

    task2 = Task(
        user_id=test_user_id,
        title="Second task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    session.add(task2)
    session.commit()

    task3 = Task(
        user_id=test_user_id,
        title="Third task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    session.add(task3)
    session.commit()

    # Act - no sort_by or order specified
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
    )

    # Assert - newest first
    assert len(tasks) == 3
    assert tasks[0].title == "Third task"
    assert tasks[1].title == "Second task"
    assert tasks[2].title == "First task"


# T092: Write unit tests for combined filter and sort


async def test_filter_pending_sort_by_due_date(session: Session, test_user_id: UUID):
    """Test combining status filter with sorting.

    Validates:
    - Filter applied first
    - Then sorting applied to filtered results
    """
    today = date.today()

    # Arrange - create mixed tasks
    pending1 = Task(
        user_id=test_user_id,
        title="Pending due tomorrow",
        status=Status.PENDING,
        due_date=today + timedelta(days=1),
        priority=Priority.MEDIUM,
    )
    pending2 = Task(
        user_id=test_user_id,
        title="Pending due next week",
        status=Status.PENDING,
        due_date=today + timedelta(days=7),
        priority=Priority.MEDIUM,
    )
    completed = Task(
        user_id=test_user_id,
        title="Completed task",
        status=Status.COMPLETED,
        due_date=today + timedelta(days=3),
        priority=Priority.HIGH,
    )

    session.add_all([pending2, completed, pending1])
    session.commit()

    # Act - filter pending, sort by due_date ASC
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
        status=TaskStatusFilter.PENDING,
        sort_by=TaskSortBy.DUE_DATE,
        order=SortOrder.ASC,
    )

    # Assert - only pending tasks, sorted by due_date
    assert len(tasks) == 2
    assert all(task.status == Status.PENDING for task in tasks)
    assert tasks[0].title == "Pending due tomorrow"
    assert tasks[1].title == "Pending due next week"


async def test_filter_overdue_sort_by_priority(session: Session, test_user_id: UUID):
    """Test filtering overdue tasks and sorting by priority.

    Validates:
    - Overdue filter returns only pending tasks with due_date < today
    - Results sorted by priority
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    # Arrange
    overdue_high = Task(
        user_id=test_user_id,
        title="Overdue high priority",
        status=Status.PENDING,
        due_date=yesterday,
        priority=Priority.HIGH,
    )
    overdue_low = Task(
        user_id=test_user_id,
        title="Overdue low priority",
        status=Status.PENDING,
        due_date=two_days_ago,
        priority=Priority.LOW,
    )
    pending_future = Task(
        user_id=test_user_id,
        title="Future task",
        status=Status.PENDING,
        due_date=today + timedelta(days=1),
        priority=Priority.HIGH,
    )

    session.add_all([overdue_low, pending_future, overdue_high])
    session.commit()

    # Act
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=test_user_id,
        status=TaskStatusFilter.OVERDUE,
        sort_by=TaskSortBy.PRIORITY,
        order=SortOrder.DESC,
    )

    # Assert
    assert len(tasks) == 2
    assert tasks[0].title == "Overdue high priority"
    assert tasks[1].title == "Overdue low priority"


# T116-T117: Update and Complete Task Service Tests

# T116-T117: Update and Complete Task Service Tests

async def test_update_task_success(session: Session, test_user_id: UUID):
    """T116: Update task with valid data."""
    # Arrange
    task_data = TaskCreate(title="Original", priority=Priority.MEDIUM)
    task = await task_service.create_task(session, test_user_id, task_data)

    # Act
    update_data = TaskUpdate(title="Updated", priority=Priority.HIGH)
    updated = await task_service.update_task(session, task.id, test_user_id, update_data)

    # Assert
    assert updated is not None
    assert updated.title == "Updated"
    assert updated.priority == Priority.HIGH


async def test_update_task_not_found(session: Session, test_user_id: UUID):
    """T116: Update non-existent task returns None."""
    from uuid import uuid4
    non_existent = uuid4()
    update_data = TaskUpdate(title="Updated")
    result = await task_service.update_task(session, non_existent, test_user_id, update_data)
    assert result is None


async def test_complete_task_success(session: Session, test_user_id: UUID):
    """T117: Complete pending task."""
    # Arrange
    task_data = TaskCreate(title="Complete me", status=Status.PENDING)
    task = await task_service.create_task(session, test_user_id, task_data)

    # Act
    completed = await task_service.complete_task(session, task.id, test_user_id)

    # Assert
    assert completed is not None
    assert completed.status == Status.COMPLETED


async def test_complete_task_idempotent(session: Session, test_user_id: UUID):
    """T117: Complete task is idempotent."""
    # Arrange
    task_data = TaskCreate(title="Already done", status=Status.COMPLETED)
    task = await task_service.create_task(session, test_user_id, task_data)

    # Act - Complete already-completed task
    result = await task_service.complete_task(session, task.id, test_user_id)

    # Assert - Should succeed without error
    assert result is not None
    assert result.status == Status.COMPLETED


# T135-T136: Delete Task Service Tests


async def test_delete_task_success(session: Session, test_user_id: UUID):
    """T135: Test deleting a task owned by the user.

    Validates:
    - Task is deleted from database
    - Function returns True
    - Task no longer retrievable
    """
    # Arrange - create task for user
    task_data = TaskCreate(
        title="Task to delete",
        description="This task will be deleted",
        priority=Priority.MEDIUM,
    )
    task = await task_service.create_task(session, test_user_id, task_data)
    task_id = task.id

    # Verify task exists before deletion
    existing_task = await task_service.get_task_by_id(session, task_id, test_user_id)
    assert existing_task is not None

    # Act - delete the task
    result = await task_service.delete_task(session, task_id, test_user_id)

    # Assert - deletion successful
    assert result is True

    # Verify task is deleted (no longer retrievable)
    deleted_task = await task_service.get_task_by_id(session, task_id, test_user_id)
    assert deleted_task is None

    # Verify task removed from database
    db_task = session.get(Task, task_id)
    assert db_task is None


async def test_delete_task_not_found(session: Session, test_user_id: UUID):
    """T136: Test deleting a non-existent task.

    Validates:
    - Function returns False when task doesn't exist
    - No errors raised
    """
    from uuid import uuid4

    # Arrange - use random UUID that doesn't exist
    non_existent_id = uuid4()

    # Act - attempt to delete non-existent task
    result = await task_service.delete_task(session, non_existent_id, test_user_id)

    # Assert - deletion failed (task not found)
    assert result is False


async def test_delete_task_not_owned(
    session: Session, test_user_id: UUID, test_user_id_2: UUID
):
    """T136: Test deleting a task NOT owned by the requesting user.

    Validates:
    - Function returns False when user doesn't own the task
    - Task remains in database (not deleted)
    - Security: ownership validation prevents unauthorized deletion
    """
    # Arrange - create task for User A
    task_data = TaskCreate(
        title="User A's task",
        description="Only User A can delete this",
        priority=Priority.HIGH,
    )
    task = await task_service.create_task(session, test_user_id, task_data)
    task_id = task.id

    # Verify task exists for User A
    existing_task = await task_service.get_task_by_id(session, task_id, test_user_id)
    assert existing_task is not None

    # Act - User B tries to delete User A's task
    result = await task_service.delete_task(session, task_id, test_user_id_2)

    # Assert - deletion failed (not owned)
    assert result is False

    # Verify task still exists for User A (not deleted)
    still_exists = await task_service.get_task_by_id(session, task_id, test_user_id)
    assert still_exists is not None
    assert still_exists.id == task_id
    assert still_exists.user_id == test_user_id

    # Verify task is still in database
    db_task = session.get(Task, task_id)
    assert db_task is not None
    assert db_task.user_id == test_user_id
