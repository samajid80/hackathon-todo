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
    client: TestClient, test_jwt_token: str, test_user_id: UUID
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
    assert data["user_id"] == str(test_user_id)
    assert data["title"] == "Complete project proposal"
    assert data["description"] == "Write and submit the Q1 project proposal"
    assert data["priority"] == "high"
    assert data["status"] == "pending"  # Default
    assert "created_at" in data
    assert "updated_at" in data


def test_post_task_with_minimal_data(
    client: TestClient, test_jwt_token: str, test_user_id: UUID
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
    assert data["user_id"] == str(test_user_id)


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
    test_user_id: UUID,
):
    """Test GET /api/tasks returns all user's tasks.

    Validates:
    - 200 OK
    - All user's tasks in response
    - Ordered by created_at DESC
    """
    # Arrange - create 3 tasks for user
    task1 = Task(
        user_id=test_user_id,
        title="Task 1",
        priority=Priority.LOW,
        status=Status.PENDING,
    )
    task2 = Task(
        user_id=test_user_id,
        title="Task 2",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    task3 = Task(
        user_id=test_user_id,
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
    assert isinstance(data, list)
    assert len(data) == 3
    # Verify ordering: newest first
    assert data[0]["title"] == "Task 3"
    assert data[1]["title"] == "Task 2"
    assert data[2]["title"] == "Task 1"


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
    assert data == []
    assert isinstance(data, list)


def test_get_tasks_excludes_other_users_tasks(
    client: TestClient,
    session: Session,
    test_jwt_token: str,
    test_jwt_token_2: str,
    test_user_id: UUID,
    test_user_id_2: UUID,
):
    """Test GET /api/tasks excludes other users' tasks.

    Validates:
    - User A sees only their tasks
    - User B sees only their tasks
    - No cross-user data leakage
    """
    # Arrange - create tasks for both users
    task_a = Task(
        user_id=test_user_id,
        title="User A Task",
        priority=Priority.MEDIUM,
        status=Status.PENDING,
    )
    task_b = Task(
        user_id=test_user_id_2,
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
    assert len(data_a) == 1
    assert data_a[0]["title"] == "User A Task"
    assert data_a[0]["user_id"] == str(test_user_id)

    # Assert - User B sees only their task
    assert response_b.status_code == 200
    data_b = response_b.json()
    assert len(data_b) == 1
    assert data_b[0]["title"] == "User B Task"
    assert data_b[0]["user_id"] == str(test_user_id_2)


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
    test_user_id: UUID,
):
    """Test GET /api/tasks/{task_id} for owned task.

    Validates:
    - 200 OK
    - Response includes all task fields
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id,
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
    assert data["user_id"] == str(test_user_id)
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
    test_user_id: UUID,
    test_user_id_2: UUID,
):
    """Test GET /api/tasks/{task_id} for task owned by another user.

    Validates:
    - 404 Not Found (security: don't reveal task exists)
    - Error message "Task not found"
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
    response = client.get(
        f"/api/tasks/{task.id}",
        headers={"Authorization": f"Bearer {test_jwt_token_2}"},
    )

    # Assert - 404 (not 403) to avoid revealing task existence
    assert response.status_code == 404
    error_data = response.json()
    assert "task not found" in error_data["detail"].lower()


def test_get_task_by_id_without_authentication(
    client: TestClient, session: Session, test_user_id: UUID
):
    """Test GET /api/tasks/{task_id} without token.

    Validates:
    - 401 Unauthorized
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id,
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
    test_user_id: UUID,
):
    """Test DELETE /api/tasks/{task_id} for owned task.

    Validates:
    - 204 No Content status
    - Task is deleted from database
    - No response body
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id,
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
    test_user_id: UUID,
    test_user_id_2: UUID,
):
    """Test DELETE /api/tasks/{task_id} for task owned by another user.

    Validates:
    - 404 Not Found (security: don't reveal task exists)
    - Task remains in database (not deleted)
    - Error message "Task not found"
    """
    # Arrange - create task for User A
    task = Task(
        user_id=test_user_id,
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
    client: TestClient, session: Session, test_user_id: UUID
):
    """Test DELETE /api/tasks/{task_id} without Authorization header.

    Validates:
    - 401 Unauthorized
    - Error message "Not authenticated"
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id,
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
    test_user_id: UUID,
):
    """Test DELETE /api/tasks/{task_id} with expired JWT token.

    Validates:
    - 401 Unauthorized
    - Error message about credentials validation
    """
    # Arrange - create task
    task = Task(
        user_id=test_user_id,
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
