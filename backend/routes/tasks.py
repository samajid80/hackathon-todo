"""Task API routes for CRUD operations.

This module provides REST API endpoints for task management with
JWT authentication, user isolation, and pagination (T151).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel
from sqlmodel import Session

from ..auth.jwt_middleware import CurrentUserDep
from ..db import get_session
from ..models.enums import SortOrder, TaskSortBy, TaskStatusFilter
from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate
from ..services import task_service

# Create router with tags for OpenAPI documentation
router = APIRouter(prefix="/tasks", tags=["tasks"])


class PaginatedTasksResponse(BaseModel):
    """Paginated response for task list (T151)."""
    items: list[TaskRead]
    total: int
    skip: int
    limit: int
    has_more: bool


@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user. "
    "Title is required and must not be empty. "
    "Description, due_date, priority, and tags are optional. "
    "Tags support: max 10 tags, 1-50 chars each, lowercase alphanumeric + hyphens.",
)
async def create_task(
    task_create: TaskCreate,
    current_user: CurrentUserDep,
    session: Session = Depends(get_session),
) -> Task:
    """Create a new task (T049).

    Args:
        task_create: Task creation data from request body
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        TaskRead: Created task with id and timestamps

    Raises:
        HTTPException 400: If validation fails (title empty, too long, etc.)
        HTTPException 401: If JWT token is invalid or missing

    Example Request:
        POST /api/tasks
        Authorization: Bearer <jwt_token>
        {
            "title": "Complete project proposal",
            "description": "Write and submit the Q1 project proposal",
            "due_date": "2025-01-15",
            "priority": "high",
            "tags": ["work", "urgent"]
        }

    Example Response (201 Created):
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Complete project proposal",
            "description": "Write and submit the Q1 project proposal",
            "due_date": "2025-01-15",
            "priority": "high",
            "status": "pending",
            "tags": ["work", "urgent"],
            "user_id": "987e6543-e21b-12d3-a456-426614174000",
            "created_at": "2025-12-11T10:30:00Z",
            "updated_at": "2025-12-11T10:30:00Z"
        }
    """
    try:
        task = await task_service.create_task(
            session=session,
            user_id=current_user.user_id,
            task_create=task_create,
        )
        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=PaginatedTasksResponse,
    summary="List user's tasks with filtering, sorting, and pagination",
    description="Get tasks owned by the authenticated user with pagination support. "
    "Supports filtering by status (pending, completed, overdue) and tags, "
    "sorting by various fields (due_date, priority, status, created_at), "
    "and pagination (skip, limit). "
    "Returns paginated response with metadata. "
    "Tag filtering uses AND logic (task must have ALL specified tags).",
)
async def list_tasks(
    current_user: CurrentUserDep,
    session: Session = Depends(get_session),
    status_filter: TaskStatusFilter | None = Query(
        None,
        alias="status",
        description="Filter by status: pending, completed, or overdue (pending tasks with due_date < today)",
    ),
    tags: list[str] | None = Query(
        None,
        description="Filter by tags (AND logic - task must have ALL specified tags). Can specify multiple times: ?tags=work&tags=urgent",
    ),
    sort_by: TaskSortBy | None = Query(
        None,
        description="Sort field: due_date, priority, status, or created_at (default)",
    ),
    order: SortOrder | None = Query(
        None,
        description="Sort order: asc or desc (default)",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of tasks to skip (pagination offset)",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Maximum number of tasks to return (default 20, max 100)",
    ),
) -> PaginatedTasksResponse:
    """List tasks for the authenticated user with filtering, sorting, and pagination (T050, T081-T082, T151, T037).

    Args:
        current_user: Authenticated user from JWT token
        session: Database session
        status_filter: Optional filter by status (pending, completed, overdue)
        tags: Optional filter by tags (AND logic - task must have ALL specified tags)
        sort_by: Optional sort field (due_date, priority, status, created_at)
        order: Optional sort order (asc, desc)
        skip: Number of tasks to skip (pagination offset) - default 0
        limit: Maximum number of tasks to return (default 20, max 100)

    Returns:
        PaginatedTasksResponse: Paginated list of tasks with metadata
            - items: List of tasks matching filters
            - total: Total count of tasks matching filters
            - skip: Current pagination offset
            - limit: Current pagination limit
            - has_more: Whether there are more tasks to fetch

    Raises:
        HTTPException 400: If invalid query parameter values provided
        HTTPException 401: If JWT token is invalid or missing

    Query Parameters (T081-T082, T151, T037):
        - status: Filter by status (pending, completed, overdue)
          - pending: Tasks with status=PENDING
          - completed: Tasks with status=COMPLETED
          - overdue: Tasks with status=PENDING AND due_date < today
        - tags: Filter by tags (AND logic - task must have ALL specified tags)
          - Can specify multiple times: ?tags=work&tags=urgent
          - Empty or omitted = no tag filtering
        - sort_by: Sort field (due_date, priority, status, created_at)
          - due_date: Order by due_date (NULLs last)
          - priority: Order by priority (high → medium → low in DESC)
          - status: Order by status
          - created_at: Order by created_at (default)
        - order: Sort order (asc, desc)
          - asc: Ascending order
          - desc: Descending order (default)
        - skip: Pagination offset (default 0, min 0)
        - limit: Pagination limit (default 20, min 1, max 100)

    Validation (T082):
        All query parameters are validated using Pydantic enums.
        Invalid values return 422 Unprocessable Entity automatically.

    Example Requests:
        GET /api/tasks
        Authorization: Bearer <jwt_token>
        (Returns first 20 tasks, sorted by created_at DESC)

        GET /api/tasks?status=pending&sort_by=due_date&order=asc&skip=0&limit=10
        Authorization: Bearer <jwt_token>
        (Returns first 10 pending tasks, sorted by due_date ascending)

        GET /api/tasks?tags=work
        Authorization: Bearer <jwt_token>
        (Returns tasks with "work" tag)

        GET /api/tasks?tags=work&tags=urgent
        Authorization: Bearer <jwt_token>
        (Returns tasks with BOTH "work" AND "urgent" tags - AND logic)

        GET /api/tasks?skip=20&limit=20
        Authorization: Bearer <jwt_token>
        (Returns tasks 21-40, page 2 with limit=20)

    Example Response (200 OK):
        {
            "items": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Complete project proposal",
                    "description": "Write and submit the Q1 project proposal",
                    "due_date": "2025-01-15",
                    "priority": "high",
                    "status": "pending",
                    "user_id": "987e6543-e21b-12d3-a456-426614174000",
                    "created_at": "2025-12-11T10:30:00Z",
                    "updated_at": "2025-12-11T10:30:00Z"
                }
            ],
            "total": 150,
            "skip": 0,
            "limit": 20,
            "has_more": true
        }
    """
    # Fetch paginated tasks
    tasks = await task_service.get_user_tasks(
        session=session,
        user_id=current_user.user_id,
        status=status_filter,
        tags=tags,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )

    # Get total count for pagination metadata
    total = await task_service.get_task_count(
        session=session,
        user_id=current_user.user_id,
        status=status_filter,
        tags=tags,
    )

    # Calculate has_more
    has_more = (skip + limit) < total

    return PaginatedTasksResponse(
        items=tasks,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get(
    "/tags",
    response_model=list[str],
    summary="Get all unique tags used by the authenticated user",
    description="Get a sorted list of all unique tags across all user's tasks. "
    "Returns an empty array if user has no tasks with tags. "
    "Tags are sorted alphabetically.",
)
async def list_tags(
    current_user: CurrentUserDep,
    session: Session = Depends(get_session),
) -> list[str]:
    """Get all unique tags for the authenticated user (T052-T053, T050).

    Args:
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        list[str]: Unique tags sorted alphabetically. Empty list if no tags found.

    Raises:
        HTTPException 401: If JWT token is invalid or missing

    Example Request:
        GET /api/tasks/tags
        Authorization: Bearer <jwt_token>

    Example Response (200 OK):
        ["home", "personal", "urgent", "work"]

    Example Response (200 OK - no tags):
        []
    """
    tags = await task_service.get_user_tags(
        session=session,
        user_id=current_user.user_id,
    )
    return tags


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get a single task",
    description="Get a task by ID. User must own the task. "
    "Returns 404 if task not found or not owned by user "
    "(doesn't distinguish for security).",
)
async def get_task(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: Session = Depends(get_session),
) -> Task:
    """Get a single task by ID with ownership validation (T051).

    Args:
        task_id: UUID of the task to retrieve
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        TaskRead: Task object if found and owned by user

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 404: If task not found or not owned by user

    Security:
        For security reasons, we return 404 for both "not found" and
        "not owned" cases. This prevents users from discovering which
        task IDs exist in the system.

    Example Request:
        GET /api/tasks/123e4567-e89b-12d3-a456-426614174000
        Authorization: Bearer <jwt_token>

    Example Response (200 OK):
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Complete project proposal",
            "description": "Write and submit the Q1 project proposal",
            "due_date": "2025-01-15",
            "priority": "high",
            "status": "pending",
            "user_id": "987e6543-e21b-12d3-a456-426614174000",
            "created_at": "2025-12-11T10:30:00Z",
            "updated_at": "2025-12-11T10:30:00Z"
        }

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }
    """
    task = await task_service.get_task_by_id(
        session=session,
        task_id=task_id,
        user_id=current_user.user_id,
    )

    if task is None:
        # Return 404 for both "not found" and "not owned" (T054)
        # Don't reveal task existence to unauthorized users
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    description="Update a task by ID. User must own the task. "
    "All fields are optional (partial update supported). "
    "Tags can be updated (max 10 tags, 1-50 chars each, lowercase alphanumeric + hyphens). "
    "Returns 404 if task not found or not owned by user "
    "(doesn't distinguish for security).",
)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: CurrentUserDep,
    session: Session = Depends(get_session),
) -> Task:
    """Update a task with ownership validation (T100).

    Args:
        task_id: UUID of the task to update
        task_update: Task update data (all fields optional)
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        TaskRead: Updated task object with new updated_at timestamp

    Raises:
        HTTPException 400: If validation fails (empty title, too long, etc.)
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 404: If task not found or not owned by user

    Validation (T102):
        - title: If provided, must not be empty and max 200 chars
        - description: If provided, max 2000 chars
        - due_date: If provided, must be valid ISO 8601 date format
        - priority: If provided, must be valid enum (low, medium, high)
        - status: If provided, must be valid enum (pending, completed)
        - tags: If provided, max 10 tags, 1-50 chars each, format ^[a-z0-9-]+$

    Security (T104-T105):
        For security reasons, we return 404 for both "not found" and
        "not owned" cases. This prevents users from discovering which
        task IDs exist in the system and prevents enumeration attacks.

    Immutable Fields:
        - id: Cannot be changed
        - user_id: Cannot be changed (ownership is permanent)
        - created_at: Cannot be changed (creation time is fixed)

    Auto-Updated Fields (T103):
        - updated_at: Automatically set to current timestamp via database trigger

    Example Request:
        PUT /api/tasks/123e4567-e89b-12d3-a456-426614174000
        Authorization: Bearer <jwt_token>
        {
            "title": "Complete project proposal (UPDATED)",
            "priority": "high",
            "tags": ["work", "urgent", "important"]
        }

    Example Response (200 OK):
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Complete project proposal (UPDATED)",
            "description": "Write and submit the Q1 project proposal",
            "due_date": "2025-01-15",
            "priority": "high",
            "status": "pending",
            "tags": ["work", "urgent", "important"],
            "user_id": "987e6543-e21b-12d3-a456-426614174000",
            "created_at": "2025-12-11T10:30:00Z",
            "updated_at": "2025-12-11T14:45:00Z"
        }

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }

    Example Response (400 Bad Request - validation error):
        {
            "detail": "Task title cannot be empty"
        }
    """
    try:
        # Validate title if provided (additional check beyond Pydantic)
        if task_update.title is not None and not task_update.title.strip():
            raise ValueError("Task title cannot be empty")

        task = await task_service.update_task(
            session=session,
            task_id=task_id,
            user_id=current_user.user_id,
            task_update=task_update,
        )

        if task is None:
            # Return 404 for both "not found" and "not owned" (T104-T105)
            # Don't reveal task existence to unauthorized users
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{task_id}/complete",
    response_model=TaskRead,
    summary="Mark a task as completed",
    description="Mark a task as completed by ID. User must own the task. "
    "This is an idempotent operation - completing an already completed task is safe. "
    "Returns 404 if task not found or not owned by user "
    "(doesn't distinguish for security).",
)
async def complete_task(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: Session = Depends(get_session),
) -> Task:
    """Mark a task as completed with ownership validation (T101).

    Args:
        task_id: UUID of the task to complete
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        TaskRead: Updated task object with status='completed' and new updated_at

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 404: If task not found or not owned by user

    Idempotent Operation (T099):
        This operation is idempotent - if a task is already completed,
        it will remain completed. No error is raised for completing
        an already-completed task.

    Security (T104-T105):
        For security reasons, we return 404 for both "not found" and
        "not owned" cases. This prevents users from discovering which
        task IDs exist in the system.

    Auto-Updated Fields (T103):
        - status: Set to 'completed'
        - updated_at: Automatically set to current timestamp via database trigger

    Example Request:
        PATCH /api/tasks/123e4567-e89b-12d3-a456-426614174000/complete
        Authorization: Bearer <jwt_token>

    Example Response (200 OK):
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Complete project proposal",
            "description": "Write and submit the Q1 project proposal",
            "due_date": "2025-01-15",
            "priority": "high",
            "status": "completed",
            "user_id": "987e6543-e21b-12d3-a456-426614174000",
            "created_at": "2025-12-11T10:30:00Z",
            "updated_at": "2025-12-11T15:20:00Z"
        }

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }
    """
    task = await task_service.complete_task(
        session=session,
        task_id=task_id,
        user_id=current_user.user_id,
    )

    if task is None:
        # Return 404 for both "not found" and "not owned" (T104-T105)
        # Don't reveal task existence to unauthorized users
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task by ID. User must own the task. "
    "Returns 204 No Content on success. "
    "Returns 404 if task not found or not owned by user "
    "(doesn't distinguish for security).",
)
async def delete_task(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: Session = Depends(get_session),
) -> Response:
    """Delete a task with ownership validation (T124-T127).

    Args:
        task_id: UUID of the task to delete
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Response: 204 No Content on successful deletion

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 404: If task not found or not owned by user

    HTTP Status Codes (T125, T127):
        - 204 No Content: Task was successfully deleted (no response body)
        - 404 Not Found: Task not found or not owned by user
        - 401 Unauthorized: JWT token is invalid or missing

    Security (T126-T127):
        For security reasons, we return 404 for both "not found" and
        "not owned" cases. This prevents users from discovering which
        task IDs exist in the system and prevents enumeration attacks.
        Note: The spec mentions 403 Forbidden (T126), but we use 404
        consistently with other endpoints for better security.

    Permanent Operation:
        Deletion is permanent and cannot be undone. There is no soft delete.
        Once a task is deleted, it is removed from the database completely.

    Example Request:
        DELETE /api/tasks/123e4567-e89b-12d3-a456-426614174000
        Authorization: Bearer <jwt_token>

    Example Response (204 No Content):
        (No response body)

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }
    """
    # Attempt to delete the task with ownership validation
    deleted = await task_service.delete_task(
        session=session,
        task_id=task_id,
        user_id=current_user.user_id,
    )

    if not deleted:
        # Return 404 for both "not found" and "not owned" (T126-T127)
        # Don't reveal task existence to unauthorized users
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Return 204 No Content on success (T125)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
