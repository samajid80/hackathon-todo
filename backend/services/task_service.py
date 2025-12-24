"""Task service layer for business logic and database operations.

This module provides service functions for task CRUD operations with
user isolation and proper error handling.

Index Usage Documentation (T150):
- All queries filter by user_id, using idx_user_status or idx_user_due_date composite indexes
- Status filters use idx_user_status composite index for efficient filtering
- Due date sorting uses idx_user_due_date composite index for efficient ordering
- Single-column indexes (idx_status, idx_due_date) support non-user-filtered queries if needed
"""

from datetime import date
from uuid import UUID

from sqlmodel import Session, case, col, select

from ..models.enums import Priority, SortOrder, Status, TaskSortBy, TaskStatusFilter
from ..models.task import Task, TaskCreate, TaskUpdate


async def create_task(session: Session, user_id: str, task_create: TaskCreate) -> Task:
    """Create a new task for a user.

    Args:
        session: Database session
        user_id: str of the task owner
        task_create: Task creation data (title, description, due_date, priority)

    Returns:
        Task: Created task object with id and timestamps

    Raises:
        ValueError: If title is empty or validation fails

    Note:
        Validation is handled by Pydantic in TaskCreate schema.
        user_id is automatically set from authenticated user.
        Status defaults to PENDING, priority defaults to MEDIUM.
    """
    # Validate title (additional check beyond Pydantic)
    if not task_create.title or not task_create.title.strip():
        raise ValueError("Task title cannot be empty")

    # Create task object with user association
    # Convert enums to their string values for database storage
    task = Task(
        title=task_create.title.strip(),
        description=task_create.description.strip() if task_create.description else None,
        due_date=task_create.due_date,
        priority=task_create.priority.value if task_create.priority else Priority.MEDIUM.value,
        status=task_create.status.value if task_create.status else Status.PENDING.value,
        tags=task_create.tags,
        user_id=user_id,
    )

    # Save to database
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


async def get_user_tasks(
    session: Session,
    user_id: str,
    status: TaskStatusFilter | None = None,
    tags: list[str] | None = None,
    sort_by: TaskSortBy | None = None,
    order: SortOrder | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Task]:
    """Get all tasks for a user with filtering, sorting, and pagination (T077-T080, T151, T038).

    Args:
        session: Database session
        user_id: str of the task owner
        status: Optional filter by status (pending, completed, overdue)
        tags: Optional filter by tags (AND logic - task must have ALL specified tags)
        sort_by: Optional sort field (due_date, priority, status, created_at)
        order: Optional sort order (asc, desc)
        skip: Number of tasks to skip (pagination offset) - default 0
        limit: Maximum number of tasks to return (pagination limit) - default 20

    Returns:
        List[Task]: List of tasks matching filters, sorted as requested, with pagination.
                    Returns empty list if no tasks found.

    Index Usage (T150):
        - Base query (user_id only): Uses user_id single-column index
        - Status filter queries: Use idx_user_status composite index (user_id, status)
        - Tag filter queries: Use idx_tasks_tags GIN index for @> containment operator
        - Due date sorting: Uses idx_user_due_date composite index (user_id, due_date)
        - Priority/status sorting: Uses user_id index + in-memory sort
        - Overdue filter: Uses idx_user_status + idx_due_date for due_date comparison

    Filter Logic (T077-T078, T038):
        - status='pending': Returns tasks with status=PENDING
        - status='completed': Returns tasks with status=COMPLETED
        - status='overdue': Returns tasks with status=PENDING AND due_date < today
        - status=None: Returns all tasks (no status filter)
        - tags=['work', 'urgent']: Returns tasks with BOTH "work" AND "urgent" tags (AND logic)
        - tags=None or tags=[]: Returns all tasks (no tag filter)

    Sort Logic (T079-T080):
        - sort_by='due_date': Order by due_date (NULLs last)
        - sort_by='priority': Order by priority (high → medium → low)
        - sort_by='status': Order by status (pending → completed)
        - sort_by='created_at' or None: Order by created_at (default)
        - order='asc': Ascending order
        - order='desc': Descending order (default)

    Pagination (T151):
        - skip: Offset for pagination (e.g., skip=20 for page 2 with limit=20)
        - limit: Max results per page (default 20, max enforced by API)

    Note:
        This function enforces user isolation by filtering on user_id.
        Users can only see their own tasks.
        Overdue is a computed status, not stored in database.
        Tag filtering uses PostgreSQL @> operator for efficient array containment checking.
    """
    # Start with base query: all user's tasks
    # Uses: user_id single-column index (or composite index if available)
    statement = select(Task).where(Task.user_id == user_id)

    # Apply status filter (T077-T078)
    if status is not None:
        if status == TaskStatusFilter.PENDING:
            # Uses: idx_user_status composite index (user_id, status)
            statement = statement.where(Task.status == Status.PENDING.value)
        elif status == TaskStatusFilter.COMPLETED:
            # Uses: idx_user_status composite index (user_id, status)
            statement = statement.where(Task.status == Status.COMPLETED.value)
        elif status == TaskStatusFilter.OVERDUE:
            # Overdue: pending tasks with due_date < today
            # Uses: idx_user_status for status filter, idx_due_date for date comparison
            today = date.today()
            statement = statement.where(
                Task.status == Status.PENDING.value,
                Task.due_date.is_not(None),
                Task.due_date < today,
            )

    # Apply tag filter (T038)
    # Uses: idx_tasks_tags GIN index for @> containment operator (efficient array matching)
    if tags is not None and len(tags) > 0:
        # PostgreSQL @> operator: Check if task's tags array contains ALL specified tags (AND logic)
        # Example: tags=['work', 'urgent'] matches task with tags=['work', 'urgent', 'home']
        # but does NOT match task with tags=['work'] or tags=['urgent'] alone
        statement = statement.where(Task.tags.contains(tags))

    # Apply sorting (T079-T080)
    # Default: created_at DESC (newest first)
    sort_field = sort_by or TaskSortBy.CREATED_AT
    sort_order = order or SortOrder.DESC

    # Get string value of enum for comparison (handles both enum objects and strings)
    sort_field_value = sort_field.value if hasattr(sort_field, 'value') else sort_field
    sort_order_value = sort_order.value if hasattr(sort_order, 'value') else sort_order

    if sort_field_value == "due_date":
        # Order by due_date with NULLs last
        # Uses: idx_user_due_date composite index (user_id, due_date) for efficient sorting
        if sort_order_value == "asc":
            statement = statement.order_by(col(Task.due_date).asc().nulls_last())
        else:
            statement = statement.order_by(col(Task.due_date).desc().nulls_last())
    elif sort_field_value == "priority":
        # Order by priority: high → medium → low
        # Priority enum: HIGH="high", MEDIUM="medium", LOW="low"
        # Alphabetical order doesn't work, so use CASE to map to numbers
        # high=3, medium=2, low=1
        # Uses: user_id index + in-memory sort (priority is not indexed)
        # Note: Use .value to ensure string comparison since priority is stored as VARCHAR
        priority_order = case(
            (Task.priority == Priority.HIGH.value, 3),
            (Task.priority == Priority.MEDIUM.value, 2),
            (Task.priority == Priority.LOW.value, 1),
            else_=0,
        )
        if sort_order_value == "asc":
            # low (1) → medium (2) → high (3)
            statement = statement.order_by(priority_order.asc())
        else:
            # high (3) → medium (2) → low (1)
            statement = statement.order_by(priority_order.desc())
    elif sort_field_value == "status":
        # Order by status: pending → completed (or reverse)
        # Uses: user_id index + in-memory sort (status alone is not ideal for sorting)
        if sort_order_value == "asc":
            statement = statement.order_by(Task.status.asc())
        else:
            statement = statement.order_by(Task.status.desc())
    else:  # created_at (default)
        # Uses: user_id index + created_at (created_at has default ordering)
        if sort_order_value == "asc":
            statement = statement.order_by(Task.created_at.asc())
        else:
            statement = statement.order_by(Task.created_at.desc())

    # T151: Apply pagination (skip and limit)
    statement = statement.offset(skip).limit(limit)

    tasks = session.exec(statement).all()
    return list(tasks)


async def get_task_count(
    session: Session,
    user_id: str,
    status: TaskStatusFilter | None = None,
    tags: list[str] | None = None,
) -> int:
    """Get total count of tasks for a user with optional status and tag filters (T151, T038).

    Args:
        session: Database session
        user_id: str of the task owner
        status: Optional filter by status (pending, completed, overdue)
        tags: Optional filter by tags (AND logic - task must have ALL specified tags)

    Returns:
        int: Total count of tasks matching filters

    Index Usage (T150):
        - Base query (user_id only): Uses user_id single-column index
        - Status filter queries: Use idx_user_status composite index (user_id, status)
        - Tag filter queries: Use idx_tasks_tags GIN index for @> containment operator

    Note:
        This is used for pagination metadata (total count, has_more calculation).
    """
    # Start with base query: count user's tasks
    # Uses: user_id single-column index (or composite index if available)
    statement = select(Task).where(Task.user_id == user_id)

    # Apply status filter (same logic as get_user_tasks)
    if status is not None:
        if status == TaskStatusFilter.PENDING:
            # Uses: idx_user_status composite index (user_id, status)
            statement = statement.where(Task.status == Status.PENDING.value)
        elif status == TaskStatusFilter.COMPLETED:
            # Uses: idx_user_status composite index (user_id, status)
            statement = statement.where(Task.status == Status.COMPLETED.value)
        elif status == TaskStatusFilter.OVERDUE:
            # Overdue: pending tasks with due_date < today
            # Uses: idx_user_status for status filter, idx_due_date for date comparison
            today = date.today()
            statement = statement.where(
                Task.status == Status.PENDING.value,
                Task.due_date.is_not(None),
                Task.due_date < today,
            )

    # Apply tag filter (T038) - same logic as get_user_tasks
    if tags is not None and len(tags) > 0:
        statement = statement.where(Task.tags.contains(tags))

    # Count results
    tasks = session.exec(statement).all()
    return len(tasks)


async def get_user_tags(
    session: Session,
    user_id: str,
) -> list[str]:
    """Get all unique tags used by a user, sorted alphabetically (T051, T049).

    Args:
        session: Database session
        user_id: str of the task owner

    Returns:
        list[str]: Unique tags sorted alphabetically. Empty list if no tags found.

    Index Usage:
        - Uses: idx_tasks_tags GIN index for efficient array unnesting
        - Uses: user_id index for filtering

    Implementation:
        Uses PostgreSQL unnest() to extract all tags from all user's tasks,
        then DISTINCT to get unique values, and ORDER BY for alphabetical sorting.

    Note:
        This function enforces user isolation by filtering on user_id.
        Users can only see tags from their own tasks.
    """
    # SQL: SELECT DISTINCT unnest(tags) as tag FROM tasks WHERE user_id = ? ORDER BY tag
    # SQLAlchemy/SQLModel approach: Get all tasks and extract tags in Python
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()

    # Extract all tags from all tasks and deduplicate
    all_tags: set[str] = set()
    for task in tasks:
        if task.tags:
            all_tags.update(task.tags)

    # Return sorted list
    return sorted(list(all_tags))


async def get_task_by_id(
    session: Session, task_id: UUID, user_id: str
) -> Task | None:
    """Get a single task by ID with ownership validation.

    Args:
        session: Database session
        task_id: UUID of the task to retrieve
        user_id: str of the requesting user (for ownership check)

    Returns:
        Optional[Task]: Task object if found and owned by user, None otherwise.

    Index Usage (T150):
        - Uses: Primary key index (id) + user_id index for ownership validation

    Note:
        This function enforces ownership validation by filtering on both
        task_id AND user_id. This ensures users cannot access other users' tasks.
        Returns None for both "not found" and "not owned" cases (security).
    """
    # Uses: Primary key index (id) + user_id index
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)

    task = session.exec(statement).first()
    return task


async def update_task(
    session: Session, task_id: UUID, user_id: str, task_update: TaskUpdate
) -> Task | None:
    """Update a task with ownership validation (T098).

    Args:
        session: Database session
        task_id: UUID of the task to update
        user_id: str of the requesting user (for ownership check)
        task_update: Task update data (partial updates supported)

    Returns:
        Optional[Task]: Updated task object if found and owned by user, None otherwise.

    Index Usage (T150):
        - Uses: Primary key index (id) + user_id index for ownership validation

    Note:
        Only fields provided in task_update will be updated (partial updates).
        Returns None if task not found or not owned by user.
        updated_at timestamp is automatically updated by database trigger (T103).

    Validation (T102):
        - title: If provided, must not be empty and max 200 chars
        - description: If provided, max 2000 chars
        - due_date: If provided, must be valid ISO 8601 date
        - priority: If provided, must be valid enum
        - status: If provided, must be valid enum

    Security (T104):
        Returns None for both "not found" and "not owned" cases to prevent
        task enumeration attacks.

    Immutable Fields:
        - id: Cannot be changed
        - user_id: Cannot be changed (ownership is permanent)
        - created_at: Cannot be changed (creation time is fixed)
    """
    # Get task with ownership check
    # Uses: Primary key index (id) + user_id index
    task = await get_task_by_id(session, task_id, user_id)
    if task is None:
        return None

    # Validate title if provided (additional check beyond Pydantic)
    if task_update.title is not None:
        title_stripped = task_update.title.strip()
        if not title_stripped:
            raise ValueError("Task title cannot be empty")
        # Update with stripped version
        task.title = title_stripped

    # Update other fields (only non-None values from task_update)
    update_data = task_update.model_dump(exclude_unset=True, exclude={"title"})
    for key, value in update_data.items():
        # Strip description if provided
        if key == "description" and value is not None:
            value = value.strip() if value else None
        # Convert enums to string values for database storage
        elif key in ("priority", "status") and value is not None:
            # model_dump() returns enum objects, convert to string values
            value = value.value if hasattr(value, "value") else value
        setattr(task, key, value)

    # Save to database
    # Note: updated_at is automatically updated by database trigger (T103)
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


async def delete_task(session: Session, task_id: UUID, user_id: str) -> bool:
    """Delete a task with ownership validation.

    Args:
        session: Database session
        task_id: UUID of the task to delete
        user_id: str of the requesting user (for ownership check)

    Returns:
        bool: True if task was deleted, False if not found or not owned.

    Index Usage (T150):
        - Uses: Primary key index (id) + user_id index for ownership validation

    Note:
        Returns False for both "not found" and "not owned" cases (security).
        Deletion is permanent and cannot be undone.
    """
    # Get task with ownership check
    # Uses: Primary key index (id) + user_id index
    task = await get_task_by_id(session, task_id, user_id)
    if task is None:
        return False

    # Delete from database
    session.delete(task)
    session.commit()

    return True


async def complete_task(session: Session, task_id: UUID, user_id: str) -> Task | None:
    """Mark a task as completed with ownership validation (T099).

    Args:
        session: Database session
        task_id: UUID of the task to complete
        user_id: str of the requesting user (for ownership check)

    Returns:
        Optional[Task]: Updated task object if found and owned by user, None otherwise.

    Index Usage (T150):
        - Uses: Primary key index (id) + user_id index for ownership validation

    Note:
        This is a convenience method that updates status to COMPLETED.
        Returns None if task not found or not owned by user.
        updated_at timestamp is automatically updated by database trigger (T103).

    Idempotent Operation:
        This operation is idempotent - if a task is already completed,
        it will remain completed. No error is raised for completing
        an already-completed task.

    Security (T104-T105):
        Returns None for both "not found" and "not owned" cases to prevent
        task enumeration attacks.
    """
    # Get task with ownership check
    # Uses: Primary key index (id) + user_id index
    task = await get_task_by_id(session, task_id, user_id)
    if task is None:
        return None

    # Update status to completed (idempotent)
    # Convert enum to string value for database storage
    task.status = Status.COMPLETED.value

    # Save to database
    # Note: updated_at is automatically updated by database trigger (T103)
    session.add(task)
    session.commit()
    session.refresh(task)

    return task
