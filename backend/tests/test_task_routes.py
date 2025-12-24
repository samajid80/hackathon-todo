"""Tests for task API routes (T072-T074).

These tests validate the REST API endpoints for task CRUD operations,
including authentication, validation, and user isolation.
"""

from datetime import date, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import Session

from backend.models.enums import Priority, Status
from backend.models.task import Task

# T072: Write API tests for POST /api/tasks


def test_post_task_success(
    client: TestClient, test_jwt_token: str, test_user_id_str: str
):
    """Test creating a task via POST /api/tasks.

    Validates:
    - 201 Created status
    - Response includes id, user_id, created_at, updated_at
    - Task saved to database
    """
    # Arrange
    task_data = {
        "title": "Complete project proposal",
        "description": "Write and submit the Q1 project proposal",
        "due_date": str(date.today() + timedelta(days=7)),
        "priority": "high",
    }

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["user_id"] == test_user_id_str
    assert data["title"] == "Complete project proposal"
    assert data["description"] == "Write and submit the Q1 project proposal"
    assert data["priority"] == "high"
    assert data["status"] == "pending"  # Default
    assert "created_at" in data
    assert "updated_at" in data


def test_post_task_with_minimal_data(
    client: TestClient, test_jwt_token: str, test_user_id_str: str
):
    """Test creating a task with only required fields.

    Validates:
    - Only title required
    - Defaults applied (priority=medium, status=pending)
    """
    # Arrange - minimal task
    task_data = {"title": "Simple task"}

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Simple task"
    assert data["description"] is None
    assert data["due_date"] is None
    assert data["priority"] == "medium"  # Default
    assert data["status"] == "pending"  # Default
    assert data["user_id"] == test_user_id_str


def test_post_task_validation_error_empty_title(
    client: TestClient, test_jwt_token: str
):
    """Test POST /api/tasks with empty title.

    Validates:
    - 422 Unprocessable Entity (Pydantic validation)
    - Error message mentions title
    """
    # Arrange - empty title
    task_data = {"title": ""}

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert - Pydantic validation error
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data
    # Check error mentions title
    error_str = str(error_data).lower()
    assert "title" in error_str


def test_post_task_validation_error_title_too_long(
    client: TestClient, test_jwt_token: str
):
    """Test POST /api/tasks with title > 200 chars.

    Validates:
    - 422 Unprocessable Entity
    - Error message mentions title and length
    """
    # Arrange - title with 201 characters
    task_data = {"title": "x" * 201}

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 422
    error_data = response.json()
    error_str = str(error_data).lower()
    assert "title" in error_str


def test_post_task_validation_error_description_too_long(
    client: TestClient, test_jwt_token: str
):
    """Test POST /api/tasks with description > 2000 chars.

    Validates:
    - 422 Unprocessable Entity
    - Error message mentions description
    """
    # Arrange - description with 2001 characters
    task_data = {"title": "Valid title", "description": "x" * 2001}

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 422
    error_data = response.json()
    error_str = str(error_data).lower()
    assert "description" in error_str


def test_post_task_validation_error_invalid_priority(
    client: TestClient, test_jwt_token: str
):
    """Test POST /api/tasks with invalid priority.

    Validates:
    - 422 Unprocessable Entity
    - Error message mentions priority
    """
    # Arrange - invalid priority value
    task_data = {"title": "Valid title", "priority": "super-urgent"}

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 422
    error_data = response.json()
    error_str = str(error_data).lower()
    assert "priority" in error_str


def test_post_task_without_authentication(client: TestClient):
    """Test POST /api/tasks without Authorization header.

    Validates:
    - 401 Unauthorized
    - Error message "Not authenticated"
    """
    # Arrange
    task_data = {"title": "Unauthenticated task"}

    # Act - no Authorization header
    response = client.post("/api/tasks", json=task_data)

    # Assert
    assert response.status_code == 401
    error_data = response.json()
    assert "detail" in error_data
    assert "not authenticated" in error_data["detail"].lower()


def test_post_task_with_expired_token(client: TestClient, expired_jwt_token: str):
    """Test POST /api/tasks with expired JWT token.

    Validates:
    - 401 Unauthorized
    - Error message about credentials validation
    """
    # Arrange
    task_data = {"title": "Task with expired token"}

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {expired_jwt_token}"},
    )

    # Assert
    assert response.status_code == 401
    error_data = response.json()
    assert "could not validate credentials" in error_data["detail"].lower()


# T073: Write API tests for GET /api/tasks


def test_get_tasks_returns_all_user_tasks(
    client: TestClient,
    session: Session,
    test_jwt_token: str,
    test_user_id_str: str,
):
    """Test GET /api/tasks returns all user's tasks.

    Validates:
    - 200 OK
    - All user's tasks in response
    - Ordered by created_at DESC
    """
    # Arrange - create 3 tasks for user
    task1 = Task(
        user_id=test_user_id_str,
        title="Task 1",
        priority=Priority.LOW,
        status=Status.PENDING,
    )
    task2 = Task(
        user_id=test_user_id_str,
        title="Task 2",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    task3 = Task(
        user_id=test_user_id_str,
        title="Task 3",
        priority=Priority.HIGH,
        status=Status.COMPLETED,
    )
    session.add_all([task1, task2, task3])
    session.commit()

    # Act
    response = client.get(
        "/api/tasks", headers={"Authorization": f"Bearer {test_jwt_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 3
    assert data["total"] == 3
    # Verify ordering: newest first
    assert data["items"][0]["title"] == "Task 3"
    assert data["items"][1]["title"] == "Task 2"
    assert data["items"][2]["title"] == "Task 1"


def test_get_tasks_empty(client: TestClient, test_jwt_token: str):
    """Test GET /api/tasks for user with no tasks.

    Validates:
    - 200 OK
    - Empty list returned
    """
    # Act - no tasks created
    response = client.get(
        "/api/tasks", headers={"Authorization": f"Bearer {test_jwt_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["items"] == []
    assert data["total"] == 0
    assert isinstance(data["items"], list)


def test_get_tasks_excludes_other_users_tasks(
    client: TestClient,
    session: Session,
    test_jwt_token: str,
    test_jwt_token_2: str,
    test_user_id_str: str,
    test_user_id_2_str: str,
):
    """Test GET /api/tasks excludes other users' tasks.

    Validates:
    - User A sees only their tasks
    - User B sees only their tasks
    - No cross-user data leakage
    """
    # Arrange - create tasks for both users
    task_a = Task(
        user_id=test_user_id_str,
        title="User A Task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    task_b = Task(
        user_id=test_user_id_2_str,
        title="User B Task",
        priority=Priority.HIGH,
        status=Status.COMPLETED,
    )
    session.add_all([task_a, task_b])
    session.commit()

    # Act - get tasks for User A
    response_a = client.get(
        "/api/tasks", headers={"Authorization": f"Bearer {test_jwt_token}"}
    )

    # Act - get tasks for User B
    response_b = client.get(
        "/api/tasks", headers={"Authorization": f"Bearer {test_jwt_token_2}"}
    )

    # Assert - User A sees only their task
    assert response_a.status_code == 200
    data_a = response_a.json()
    assert len(data_a["items"]) == 1
    assert data_a["total"] == 1
    assert data_a["items"][0]["title"] == "User A Task"
    assert data_a["items"][0]["user_id"] == test_user_id_str

    # Assert - User B sees only their task
    assert response_b.status_code == 200
    data_b = response_b.json()
    assert len(data_b["items"]) == 1
    assert data_b["total"] == 1
    assert data_b["items"][0]["title"] == "User B Task"
    assert data_b["items"][0]["user_id"] == test_user_id_2_str


def test_get_tasks_without_authentication(client: TestClient):
    """Test GET /api/tasks without Authorization header.

    Validates:
    - 401 Unauthorized
    """
    # Act - no Authorization header
    response = client.get("/api/tasks")

    # Assert
    assert response.status_code == 401
    error_data = response.json()
    assert "not authenticated" in error_data["detail"].lower()


# T074: Write API tests for GET /api/tasks/{task_id}


def test_get_task_by_id_success(
    client: TestClient,
    session: Session,
    test_jwt_token: str,
    test_user_id_str: str,
):
    """Test GET /api/tasks/{task_id} for owned task.

    Validates:
    - 200 OK
    - Response includes all task fields
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id_str,
        title="User's task",
        description="Task details",
        priority=Priority.HIGH,
        status=Status.PENDING,
        due_date=date.today() + timedelta(days=7),
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Act
    response = client.get(
        f"/api/tasks/{task.id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(task.id)
    assert data["title"] == "User's task"
    assert data["description"] == "Task details"
    assert data["priority"] == "high"
    assert data["status"] == "pending"
    assert data["user_id"] == test_user_id_str
    assert "created_at" in data
    assert "updated_at" in data


def test_get_task_by_id_not_found(
    client: TestClient, test_jwt_token: str
):
    """Test GET /api/tasks/{non-existent-id}.

    Validates:
    - 404 Not Found
    - Error message "Task not found"
    """
    from uuid import uuid4

    # Arrange - use non-existent task ID
    non_existent_id = uuid4()

    # Act
    response = client.get(
        f"/api/tasks/{non_existent_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 404
    error_data = response.json()
    assert "task not found" in error_data["detail"].lower()


def test_get_task_by_id_not_owned(
    client: TestClient,
    session: Session,
    test_jwt_token: str,
    test_jwt_token_2: str,
    test_user_id_str: str,
    test_user_id_2_str: str,
):
    """Test GET /api/tasks/{task_id} for task owned by another user.

    Validates:
    - 404 Not Found (security: don't reveal task exists)
    - Error message "Task not found"
    """
    # Arrange - create task for User A
    task = Task(
        user_id=test_user_id_str,
        title="User A's task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Act - User B tries to access User A's task
    response = client.get(
        f"/api/tasks/{task.id}",
        headers={"Authorization": f"Bearer {test_jwt_token_2}"},
    )

    # Assert - 404 (not 403) to avoid revealing task existence
    assert response.status_code == 404
    error_data = response.json()
    assert "task not found" in error_data["detail"].lower()


def test_get_task_by_id_without_authentication(
    client: TestClient, session: Session, test_user_id_str: str
):
    """Test GET /api/tasks/{task_id} without token.

    Validates:
    - 401 Unauthorized
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id_str,
        title="Task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Act - no Authorization header
    response = client.get(f"/api/tasks/{task.id}")

    # Assert
    assert response.status_code == 401
    error_data = response.json()
    assert "not authenticated" in error_data["detail"].lower()


def test_get_task_by_id_invalid_uuid_format(
    client: TestClient, test_jwt_token: str
):
    """Test GET /api/tasks/{invalid-uuid}.

    Validates:
    - 422 Unprocessable Entity (invalid UUID format)
    """
    # Act - invalid UUID format
    response = client.get(
        "/api/tasks/not-a-valid-uuid",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert - FastAPI validation error
    assert response.status_code == 422


# T137: Write API tests for DELETE /api/tasks/{task_id}


def test_delete_task_success(
    client: TestClient,
    session: Session,
    test_jwt_token: str,
    test_user_id_str: str,
):
    """Test DELETE /api/tasks/{task_id} for owned task.

    Validates:
    - 204 No Content status
    - Task is deleted from database
    - No response body
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id_str,
        title="Task to delete",
        description="This task will be deleted",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    # Verify task exists before deletion
    response_before = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response_before.status_code == 200

    # Act - delete the task
    response = client.delete(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert - 204 No Content (successful deletion)
    assert response.status_code == 204
    # No response body for 204
    assert response.text == ""

    # Verify task is deleted (404 when trying to GET)
    response_after = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response_after.status_code == 404


def test_delete_task_not_found(
    client: TestClient, test_jwt_token: str
):
    """Test DELETE /api/tasks/{non-existent-id}.

    Validates:
    - 404 Not Found
    - Error message "Task not found"
    """
    from uuid import uuid4

    # Arrange - use non-existent task ID
    non_existent_id = uuid4()

    # Act - attempt to delete non-existent task
    response = client.delete(
        f"/api/tasks/{non_existent_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 404
    error_data = response.json()
    assert "task not found" in error_data["detail"].lower()


def test_delete_task_not_owned(
    client: TestClient,
    session: Session,
    test_jwt_token: str,
    test_jwt_token_2: str,
    test_user_id_str: str,
    test_user_id_2_str: str,
):
    """Test DELETE /api/tasks/{task_id} for task owned by another user.

    Validates:
    - 404 Not Found (security: don't reveal task exists)
    - Task remains in database (not deleted)
    - Error message "Task not found"
    """
    # Arrange - create task for User A
    task = Task(
        user_id=test_user_id_str,
        title="User A's task",
        description="Only User A can delete this",
        priority=Priority.HIGH,
        status=Status.PENDING,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    # Verify task exists for User A
    response_before = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response_before.status_code == 200

    # Act - User B tries to delete User A's task
    response = client.delete(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_jwt_token_2}"},
    )

    # Assert - 404 (not 403) for security
    assert response.status_code == 404
    error_data = response.json()
    assert "task not found" in error_data["detail"].lower()

    # Verify task still exists for User A (not deleted)
    response_after = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response_after.status_code == 200
    assert response_after.json()["title"] == "User A's task"


def test_delete_task_without_authentication(
    client: TestClient, session: Session, test_user_id_str: str
):
    """Test DELETE /api/tasks/{task_id} without Authorization header.

    Validates:
    - 401 Unauthorized
    - Error message "Not authenticated"
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id_str,
        title="Task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Act - no Authorization header
    response = client.delete(f"/api/tasks/{task.id}")

    # Assert
    assert response.status_code == 401
    error_data = response.json()
    assert "not authenticated" in error_data["detail"].lower()


def test_delete_task_with_expired_token(
    client: TestClient,
    session: Session,
    expired_jwt_token: str,
    test_user_id_str: str,
):
    """Test DELETE /api/tasks/{task_id} with expired JWT token.

    Validates:
    - 401 Unauthorized
    - Error message about credentials validation
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id_str,
        title="Task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Act - expired token
    response = client.delete(
        f"/api/tasks/{task.id}",
        headers={"Authorization": f"Bearer {expired_jwt_token}"},
    )

    # Assert
    assert response.status_code == 401
    error_data = response.json()
    assert "could not validate credentials" in error_data["detail"].lower()


def test_delete_task_invalid_uuid_format(
    client: TestClient, test_jwt_token: str
):
    """Test DELETE /api/tasks/{invalid-uuid}.

    Validates:
    - 422 Unprocessable Entity (invalid UUID format)
    """
    # Act - invalid UUID format
    response = client.delete(
        "/api/tasks/not-a-valid-uuid",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert - FastAPI validation error
    assert response.status_code == 422


# ============================================================================
# Tag Integration Tests (T014-T015, User Story 1)
# ============================================================================


def test_create_task_with_tags(
    client: TestClient, test_jwt_token: str, test_user_id_str: str
):
    """T014: Test creating a task with tags via POST /api/tasks.

    Validates:
    - 201 Created status
    - Tags are saved and returned in response
    - Tags are normalized (lowercase, trimmed, deduplicated)
    - Tags persist in database
    """
    # Arrange
    task_data = {
        "title": "Complete project proposal",
        "description": "Write and submit the Q1 project proposal",
        "tags": ["work", "urgent"],
    }

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "tags" in data
    assert data["tags"] == ["work", "urgent"]
    assert data["title"] == "Complete project proposal"
    
    # Verify tags are persisted
    task_id = data["id"]
    get_response = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["tags"] == ["work", "urgent"]


def test_create_task_with_tags_normalization(
    client: TestClient, test_jwt_token: str, test_user_id_str: str
):
    """T014: Test that tags are normalized when creating a task.

    Validates:
    - Tags converted to lowercase
    - Whitespace trimmed
    - Duplicates removed
    """
    # Arrange - tags with mixed case, whitespace, duplicates
    task_data = {
        "title": "Task with messy tags",
        "tags": ["Work", "  urgent  ", "work", "URGENT", "home"],
    }

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["tags"] == ["work", "urgent", "home"]


def test_create_task_with_invalid_tags_max_10(
    client: TestClient, test_jwt_token: str
):
    """T014: Test creating a task with more than 10 tags fails.

    Validates:
    - 422 Unprocessable Entity (validation error from Pydantic)
    - Clear error message about max 10 tags
    """
    # Arrange - 11 tags (exceeds limit)
    task_data = {
        "title": "Task with too many tags",
        "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11"],
    }

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 422
    error_data = response.json()
    # FastAPI returns validation errors as a list of error objects
    assert "Maximum 10 tags allowed per task" in str(error_data["detail"])


def test_create_task_with_invalid_tags_format(
    client: TestClient, test_jwt_token: str
):
    """T014: Test creating a task with invalid tag format fails.

    Validates:
    - 422 Unprocessable Entity for tags with invalid characters
    - Clear error message about allowed characters
    """
    # Arrange - tag with invalid characters
    task_data = {
        "title": "Task with invalid tag",
        "tags": ["urgent!!!"],
    }

    # Act
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 422
    error_data = response.json()
    # FastAPI returns validation errors as a list of error objects
    assert "Tags can only contain lowercase letters, numbers, and hyphens" in str(error_data["detail"])


def test_update_task_tags(
    client: TestClient, session: Session, test_jwt_token: str, test_user_id_str: str
):
    """T015: Test updating task tags via PUT /api/tasks/{task_id}.

    Validates:
    - 200 OK status
    - Tags are updated in response
    - Tags persist in database
    - Can add, remove, and replace tags
    """
    # Arrange - create task with initial tags
    task = Task(
        user_id=test_user_id_str,
        title="Task to update",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
        tags=["work"],
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Act - update tags
    update_data = {
        "tags": ["work", "urgent", "important"],
    }
    response = client.put(
        f"/api/tasks/{task.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["tags"] == ["work", "urgent", "important"]
    
    # Verify tags are persisted
    get_response = client.get(
        f"/api/tasks/{task.id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["tags"] == ["work", "urgent", "important"]


def test_update_task_remove_all_tags(
    client: TestClient, session: Session, test_jwt_token: str, test_user_id_str: str
):
    """T015: Test removing all tags from a task.

    Validates:
    - Can set tags to empty array
    - Tags are removed from database
    """
    # Arrange - create task with tags
    task = Task(
        user_id=test_user_id_str,
        title="Task with tags",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
        tags=["work", "urgent"],
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Act - remove all tags
    update_data = {
        "tags": [],
    }
    response = client.put(
        f"/api/tasks/{task.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["tags"] == []


def test_update_task_tags_with_invalid_format(
    client: TestClient, session: Session, test_jwt_token: str, test_user_id_str: str
):
    """T015: Test updating tags with invalid format fails.

    Validates:
    - 422 Unprocessable Entity for invalid tag format
    - Clear error message
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id_str,
        title="Task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
        tags=[],
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Act - update with invalid tag
    update_data = {
        "tags": ["work@home"],
    }
    response = client.put(
        f"/api/tasks/{task.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert
    assert response.status_code == 422
    error_data = response.json()
    # FastAPI returns validation errors as a list of error objects
    assert "Tags can only contain lowercase letters, numbers, and hyphens" in str(error_data["detail"])


def test_filter_tasks_by_tags(
    client: TestClient, session: Session, test_jwt_token: str, test_user_id_str: str
):
    """T036: Test filtering tasks by tags via API endpoint.

    Validates:
    - GET /api/tasks?tags=work returns tasks with "work" tag
    - GET /api/tasks?tags=work&tags=urgent uses AND logic (must have BOTH tags)
    - Correct tasks returned in each case
    - HTTP 200 status and proper JSON response format
    """
    # Arrange - create tasks with different tag combinations
    task1 = Task(
        user_id=test_user_id_str,
        title="Work task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
        tags=["work"],
    )
    task2 = Task(
        user_id=test_user_id_str,
        title="Work urgent task",
        priority=Priority.HIGH,
        status=Status.PENDING,
        tags=["work", "urgent"],
    )
    task3 = Task(
        user_id=test_user_id_str,
        title="Home task",
        priority=Priority.LOW,
        status=Status.PENDING,
        tags=["home"],
    )
    task4 = Task(
        user_id=test_user_id_str,
        title="Urgent task",
        priority=Priority.HIGH,
        status=Status.PENDING,
        tags=["urgent"],
    )
    session.add_all([task1, task2, task3, task4])
    session.commit()

    # Act & Assert - filter by single tag "work"
    response = client.get(
        "/api/tasks",
        params={"tags": "work"},
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    items = data["items"]
    assert len(items) == 2
    titles = [task["title"] for task in items]
    assert "Work task" in titles
    assert "Work urgent task" in titles
    assert "Home task" not in titles
    assert "Urgent task" not in titles

    # Act & Assert - filter by multiple tags "work" AND "urgent" (AND logic)
    response = client.get(
        "/api/tasks",
        params={"tags": ["work", "urgent"]},
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    items = data["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Work urgent task"
    assert set(items[0]["tags"]) == {"work", "urgent"}

    # Act & Assert - filter by tag that matches no tasks
    response = client.get(
        "/api/tasks",
        params={"tags": "nonexistent"},
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    items = data["items"]
    assert len(items) == 0


def test_list_tags_endpoint(
    client: TestClient, session: Session, test_jwt_token: str, test_user_id_str: str
):
    """T050: Test GET /api/tasks/tags endpoint returns unique sorted tags.

    Validates:
    - GET /api/tasks/tags returns all unique tags used by user
    - Tags are sorted alphabetically
    - Duplicate tags are removed
    - Empty result when user has no tasks with tags
    - User isolation (only user's own tags)
    - HTTP 200 status and proper JSON array response
    """
    # Arrange - create tasks with various tags
    task1 = Task(
        user_id=test_user_id_str,
        title="Task 1",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
        tags=["work", "urgent", "home"],
    )
    task2 = Task(
        user_id=test_user_id_str,
        title="Task 2",
        priority=Priority.HIGH,
        status=Status.PENDING,
        tags=["work", "personal"],
    )
    task3 = Task(
        user_id=test_user_id_str,
        title="Task 3",
        priority=Priority.LOW,
        status=Status.COMPLETED,
        tags=["home"],
    )
    task4 = Task(
        user_id=test_user_id_str,
        title="Task 4",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
        tags=[],  # No tags
    )
    session.add_all([task1, task2, task3, task4])
    session.commit()

    # Act - get all tags via API
    response = client.get(
        "/api/tasks/tags",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Assert - returns unique sorted tags
    assert response.status_code == 200
    tags = response.json()
    assert isinstance(tags, list)
    assert len(tags) == 4  # work, urgent, home, personal
    assert tags == ["home", "personal", "urgent", "work"]  # Alphabetically sorted

    # Verify all expected tags are present
    assert "work" in tags
    assert "urgent" in tags
    assert "home" in tags
    assert "personal" in tags
