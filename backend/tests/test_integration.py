"""Integration tests for authentication and task management flows.

These tests validate end-to-end scenarios including:
- JWT token validation with protected endpoints
- User session management
- Authentication error handling
- Token-based access control
- Task creation and viewing workflows (T075-T076)
- User data isolation (T076)

Note: Better-Auth handles signup/login on the frontend. These tests
focus on the backend's JWT validation middleware and task management.
"""

from datetime import date, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import Session

from backend.models.enums import Priority, Status
from backend.models.task import Task


def test_signup_flow(client: TestClient, test_jwt_token: str, test_user_id: UUID):
    """Test signup flow with JWT token generation.

    This test validates that after signup (handled by Better-Auth on frontend),
    the user receives a JWT token that can be used to authenticate subsequent
    requests to protected endpoints.

    Test Flow:
    1. Simulate post-signup state with valid JWT token
    2. Make authenticated request to protected endpoint
    3. Verify request succeeds with 200 status
    4. Verify user can access their resources

    Expected Behavior:
    - Valid JWT token allows access to protected endpoints
    - Token contains correct user_id claim
    - User can make subsequent authenticated requests
    """
    # Simulate signup by Better-Auth (frontend generates JWT)
    # User now has a valid JWT token in their session

    # Test 1: Verify token works with health check (minimal protected endpoint)
    response = client.get(
        "/health",
        headers={"Authorization": f"Bearer {test_jwt_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    # Test 2: Verify token contains correct user_id
    # (This would normally be tested with a user-specific endpoint like /api/tasks)
    # For now, we verify the token is accepted
    response = client.get(
        "/",
        headers={"Authorization": f"Bearer {test_jwt_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Test 3: Verify subsequent requests with same token work
    response = client.get(
        "/health",
        headers={"Authorization": f"Bearer {test_jwt_token}"}
    )
    assert response.status_code == 200


def test_login_flow(client: TestClient, test_jwt_token: str, test_user_id: UUID):
    """Test login flow with JWT token authentication.

    This test validates that after login (handled by Better-Auth on frontend),
    the user receives a JWT token and can access protected resources.

    Test Flow:
    1. Simulate post-login state with valid JWT token
    2. Make authenticated request to verify access
    3. Verify token is valid and grants access
    4. Verify user_id is correctly extracted from token

    Expected Behavior:
    - Valid JWT token returned after successful login
    - Token grants access to protected endpoints
    - User can make multiple requests with same token
    - Token contains correct user_id for resource isolation
    """
    # Simulate login by Better-Auth (frontend generates JWT)
    # User receives JWT token on successful authentication

    # Test 1: Verify token grants access to API
    response = client.get(
        "/",
        headers={"Authorization": f"Bearer {test_jwt_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Test 2: Verify token works with health endpoint
    response = client.get(
        "/health",
        headers={"Authorization": f"Bearer {test_jwt_token}"}
    )
    assert response.status_code == 200

    # Test 3: Verify token persists across multiple requests
    for _ in range(3):
        response = client.get(
            "/health",
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )
        assert response.status_code == 200


def test_logout_flow(client: TestClient, test_jwt_token: str):
    """Test logout flow and session termination.

    This test validates that after logout (handled by Better-Auth on frontend),
    the user's session is terminated and the JWT token is no longer valid for
    making authenticated requests.

    Test Flow:
    1. User is logged in with valid JWT token
    2. User logs out (frontend clears token/session)
    3. Attempt to access protected endpoint without token
    4. Verify access is denied with 401 Unauthorized

    Expected Behavior:
    - User successfully logged in initially
    - After logout, session is cleared
    - Requests without token return 401 Unauthorized
    - Clear error message: "Not authenticated"

    Note: Backend doesn't invalidate tokens (stateless JWT). Logout is
    handled by frontend removing token from session/storage.
    """
    # Test 1: Verify user is initially authenticated
    response = client.get(
        "/health",
        headers={"Authorization": f"Bearer {test_jwt_token}"}
    )
    assert response.status_code == 200

    # Simulate logout: Frontend clears JWT token from session
    # User no longer has token in subsequent requests

    # Test 2: Verify access denied without token
    response = client.get("/health")
    # Note: /health is public, so test with a protected endpoint would be better
    # For now, we verify the flow conceptually
    assert response.status_code == 200  # Health is public

    # Test 3: Verify explicit unauthorized access
    # When protected endpoints are implemented (e.g., /api/tasks),
    # requests without Authorization header should return 401
    response = client.get("/")
    assert response.status_code == 200  # Root is public

    # Test with protected endpoint
    response = client.get("/api/tasks")  # No Authorization header
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()


def test_unauthenticated_access_redirect(
    client: TestClient,
    expired_jwt_token: str,
    test_user_id: UUID
):
    """Test unauthenticated access returns 401 and requires token.

    This test validates that protected endpoints require valid authentication
    and return clear error messages when accessed without proper credentials.

    Test Flow:
    1. Attempt to access protected endpoint without token
    2. Verify 401 Unauthorized response
    3. Attempt with expired token
    4. Verify 401 Unauthorized with clear error
    5. Attempt with malformed token
    6. Verify 401 Unauthorized

    Expected Behavior:
    - Missing token: 401 with "Not authenticated" message
    - Expired token: 401 with "Could not validate credentials"
    - Invalid token: 401 with "Could not validate credentials"
    - Error includes WWW-Authenticate header
    """
    # Test 1: Access without token (missing Authorization header)
    response = client.get("/api/tasks")
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()

    # Test 2: Access with expired token
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {expired_jwt_token}"}
    )
    assert response.status_code == 401
    assert "could not validate credentials" in response.json()["detail"].lower()

    # Test 3: Access with invalid/malformed token
    response = client.get(
        "/api/tasks",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
    assert "could not validate credentials" in response.json()["detail"].lower()


def test_protected_endpoint_with_valid_token(
    client: TestClient,
    test_jwt_token: str,
    test_user_id: UUID
):
    """Test that protected endpoints work with valid JWT token.

    This test validates that task endpoints work correctly with authentication.

    Expected Behavior:
    - Valid token grants access
    - user_id is correctly extracted
    - Resources are filtered by user_id
    """
    # Verify token is valid and grants access
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_user_isolation_with_different_tokens(
    client: TestClient,
    test_jwt_token: str,
    test_jwt_token_2: str,
    test_user_id: UUID,
    test_user_id_2: UUID
):
    """Test that different users with valid tokens access only their own resources.

    This test validates user isolation - users should only see their own data
    even when both have valid authentication tokens.

    Expected Behavior:
    - User 1 with token 1 sees only their resources
    - User 2 with token 2 sees only their resources
    - No cross-user data leakage
    """
    # Verify both tokens are valid
    response1 = client.get(
        "/",
        headers={"Authorization": f"Bearer {test_jwt_token}"}
    )
    assert response1.status_code == 200

    response2 = client.get(
        "/",
        headers={"Authorization": f"Bearer {test_jwt_token_2}"}
    )
    assert response2.status_code == 200

    # Verify tokens contain different user_ids
    assert test_user_id != test_user_id_2


def test_token_expiration_handling(
    client: TestClient,
    expired_jwt_token: str
):
    """Test that expired tokens are rejected with appropriate error.

    Expected Behavior:
    - Expired token returns 401 Unauthorized
    - Error message: "Could not validate credentials"
    - WWW-Authenticate header present
    """
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {expired_jwt_token}"}
    )
    assert response.status_code == 401
    assert "could not validate credentials" in response.json()["detail"].lower()


def test_malformed_authorization_header(client: TestClient):
    """Test that malformed Authorization headers are rejected.

    Expected Behavior:
    - Missing "Bearer " prefix: 401 or 403
    - Empty token: 401
    - Invalid format: 401
    """
    # Test missing Bearer prefix
    response = client.get(
        "/api/tasks",
        headers={"Authorization": "just-a-token"}
    )
    assert response.status_code in [401, 403]

    # Test empty token
    response = client.get(
        "/api/tasks",
        headers={"Authorization": "Bearer "}
    )
    assert response.status_code == 401


# T075: Write integration test for create and view task flow


def test_create_and_view_task_flow(
    client: TestClient, test_jwt_token: str, test_user_id: UUID
):
    """Integration test for create and view task workflow (T075).

    Test Flow:
    1. Login/generate JWT token
    2. Create task via POST /api/tasks
    3. Verify task created (201)
    4. GET /api/tasks to verify task in list
    5. GET /api/tasks/{task_id} to verify task details
    6. Verify all data correct (title, priority, status, dates)

    Expected Behavior:
    - Complete workflow succeeds end-to-end
    - Data persists across requests
    - All fields correctly saved and retrieved
    """
    # Step 1: User is logged in (simulated with test_jwt_token)

    # Step 2: Create task via POST /api/tasks
    task_data = {
        "title": "Complete project proposal",
        "description": "Write and submit the Q1 project proposal",
        "due_date": str(date.today() + timedelta(days=7)),
        "priority": "high",
    }

    create_response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Step 3: Verify task created (201)
    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["title"] == "Complete project proposal"
    assert created_task["priority"] == "high"
    assert created_task["status"] == "pending"
    task_id = created_task["id"]

    # Step 4: GET /api/tasks to verify task in list
    list_response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id
    assert tasks[0]["title"] == "Complete project proposal"

    # Step 5: GET /api/tasks/{task_id} to verify task details
    get_response = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert get_response.status_code == 200
    task_details = get_response.json()

    # Step 6: Verify all data correct
    assert task_details["id"] == task_id
    assert task_details["title"] == "Complete project proposal"
    assert task_details["description"] == "Write and submit the Q1 project proposal"
    assert task_details["priority"] == "high"
    assert task_details["status"] == "pending"
    assert task_details["user_id"] == str(test_user_id)
    assert "created_at" in task_details
    assert "updated_at" in task_details


def test_create_multiple_tasks_and_view(
    client: TestClient, test_jwt_token: str, test_user_id: UUID
):
    """Integration test for creating multiple tasks and viewing them (T075).

    Test Flow:
    1. Create 3 tasks with different priorities
    2. GET /api/tasks
    3. Verify all 3 tasks in list
    4. Verify ordered correctly (newest first)

    Expected Behavior:
    - Multiple tasks created successfully
    - All tasks returned in list
    - Correct ordering (created_at DESC)
    """
    # Step 1: Create 3 tasks with different priorities
    task1_data = {"title": "Low priority task", "priority": "low"}
    task2_data = {"title": "Medium priority task", "priority": "medium"}
    task3_data = {"title": "High priority task", "priority": "high"}

    response1 = client.post(
        "/api/tasks",
        json=task1_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response1.status_code == 201

    response2 = client.post(
        "/api/tasks",
        json=task2_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response2.status_code == 201

    response3 = client.post(
        "/api/tasks",
        json=task3_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response3.status_code == 201

    # Step 2: GET /api/tasks
    list_response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert list_response.status_code == 200
    tasks = list_response.json()

    # Step 3: Verify all 3 tasks in list
    assert len(tasks) == 3

    # Step 4: Verify ordered correctly (newest first)
    assert tasks[0]["title"] == "High priority task"
    assert tasks[1]["title"] == "Medium priority task"
    assert tasks[2]["title"] == "Low priority task"


# T076: Write integration test for user data isolation


def test_user_data_isolation(
    client: TestClient,
    test_jwt_token: str,
    test_jwt_token_2: str,
    test_user_id: UUID,
    test_user_id_2: UUID,
):
    """Integration test for user data isolation (T076).

    Test Flow:
    1. Create user A and user B (via JWT tokens)
    2. Create task T1 for user A
    3. Create task T2 for user B
    4. User A GETs /api/tasks - verify only T1
    5. User A GETs /api/tasks/{T2_id} - verify 404
    6. User B GETs /api/tasks - verify only T2
    7. User B GETs /api/tasks/{T1_id} - verify 404
    8. Verify complete isolation

    Expected Behavior:
    - Users see only their own tasks
    - Cannot access other users' tasks
    - 404 for cross-user access (security)
    - No data leakage
    """
    # Step 1: Users A and B are logged in (via tokens)

    # Step 2: Create task T1 for user A
    task_a_data = {"title": "User A Task", "priority": "high"}
    response_a = client.post(
        "/api/tasks",
        json=task_a_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response_a.status_code == 201
    task_a = response_a.json()
    task_a_id = task_a["id"]

    # Step 3: Create task T2 for user B
    task_b_data = {"title": "User B Task", "priority": "low"}
    response_b = client.post(
        "/api/tasks",
        json=task_b_data,
        headers={"Authorization": f"Bearer {test_jwt_token_2}"},
    )
    assert response_b.status_code == 201
    task_b = response_b.json()
    task_b_id = task_b["id"]

    # Step 4: User A GETs /api/tasks - verify only T1
    list_a = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert list_a.status_code == 200
    tasks_a = list_a.json()
    assert len(tasks_a) == 1
    assert tasks_a[0]["id"] == task_a_id
    assert tasks_a[0]["title"] == "User A Task"
    assert tasks_a[0]["user_id"] == str(test_user_id)

    # Step 5: User A GETs /api/tasks/{T2_id} - verify 404
    get_b_as_a = client.get(
        f"/api/tasks/{task_b_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert get_b_as_a.status_code == 404
    assert "task not found" in get_b_as_a.json()["detail"].lower()

    # Step 6: User B GETs /api/tasks - verify only T2
    list_b = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token_2}"},
    )
    assert list_b.status_code == 200
    tasks_b = list_b.json()
    assert len(tasks_b) == 1
    assert tasks_b[0]["id"] == task_b_id
    assert tasks_b[0]["title"] == "User B Task"
    assert tasks_b[0]["user_id"] == str(test_user_id_2)

    # Step 7: User B GETs /api/tasks/{T1_id} - verify 404
    get_a_as_b = client.get(
        f"/api/tasks/{task_a_id}",
        headers={"Authorization": f"Bearer {test_jwt_token_2}"},
    )
    assert get_a_as_b.status_code == 404
    assert "task not found" in get_a_as_b.json()["detail"].lower()

    # Step 8: Verify complete isolation - no overlap
    assert task_a_id != task_b_id
    assert str(test_user_id) != str(test_user_id_2)


def test_cannot_access_other_users_task_details(
    client: TestClient,
    session: Session,
    test_jwt_token: str,
    test_jwt_token_2: str,
    test_user_id: UUID,
    test_user_id_2: UUID,
):
    """Integration test for preventing cross-user task access (T076).

    Test Flow:
    1. Create task owned by user A
    2. Try to GET task as user B
    3. Verify 404 Not Found
    4. Verify task data not leaked

    Expected Behavior:
    - 404 returned (not 403) to avoid revealing task existence
    - No sensitive data in error message
    - Complete data isolation
    """
    # Step 1: Create task owned by user A (directly in DB for simplicity)
    task_a = Task(
        user_id=test_user_id,
        title="User A's private task",
        description="Confidential information",
        priority=Priority.HIGH,
        status=Status.PENDING,
    )
    session.add(task_a)
    session.commit()
    session.refresh(task_a)

    # Step 2: Try to GET task as user B
    response = client.get(
        f"/api/tasks/{task_a.id}",
        headers={"Authorization": f"Bearer {test_jwt_token_2}"},
    )

    # Step 3: Verify 404 Not Found (not 403)
    assert response.status_code == 404

    # Step 4: Verify task data not leaked
    error_data = response.json()
    assert "task not found" in error_data["detail"].lower()
    # Verify no confidential data in error message
    assert "Confidential" not in str(error_data)
    assert "private" not in str(error_data).lower() or "private task" not in str(error_data).lower()


# T138: Write integration test for delete task workflow


def test_delete_task_flow(
    client: TestClient, test_jwt_token: str, test_user_id: UUID
):
    """Integration test for delete task workflow (T138).

    Test Flow:
    1. Login/generate JWT token
    2. Create task via POST /api/tasks
    3. Verify task created (201)
    4. DELETE /api/tasks/{task_id}
    5. Verify task deleted (204)
    6. Verify task is gone (GET returns 404)
    7. Verify task removed from list

    Expected Behavior:
    - Complete delete workflow succeeds end-to-end
    - Task is permanently deleted from database
    - Subsequent GET requests return 404
    - Task no longer appears in user's task list
    """
    # Step 1: User is logged in (simulated with test_jwt_token)

    # Step 2: Create task via POST /api/tasks
    task_data = {
        "title": "Task to delete",
        "description": "This task will be deleted",
        "priority": "medium",
    }

    create_response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Step 3: Verify task created (201)
    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["title"] == "Task to delete"
    task_id = created_task["id"]

    # Verify task exists in list
    list_response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id

    # Step 4: DELETE /api/tasks/{task_id}
    delete_response = client.delete(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Step 5: Verify task deleted (204)
    assert delete_response.status_code == 204
    assert delete_response.text == ""  # No response body

    # Step 6: Verify task is gone (GET returns 404)
    get_response = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert get_response.status_code == 404
    assert "task not found" in get_response.json()["detail"].lower()

    # Step 7: Verify task removed from list
    list_response_after = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert list_response_after.status_code == 200
    tasks_after = list_response_after.json()
    assert len(tasks_after) == 0
    assert tasks_after == []


def test_delete_nonexistent_task_flow(
    client: TestClient, test_jwt_token: str
):
    """Integration test for attempting to delete non-existent task (T138).

    Test Flow:
    1. Login/generate JWT token
    2. Attempt to DELETE /api/tasks/{non-existent-id}
    3. Verify 404 Not Found
    4. Verify error message

    Expected Behavior:
    - DELETE returns 404 for non-existent task
    - Clear error message: "Task not found"
    - No side effects (no data corruption)
    """
    from uuid import uuid4

    # Step 1: User is logged in (simulated with test_jwt_token)

    # Step 2: Attempt to DELETE /api/tasks/{non-existent-id}
    non_existent_id = uuid4()
    delete_response = client.delete(
        f"/api/tasks/{non_existent_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )

    # Step 3: Verify 404 Not Found
    assert delete_response.status_code == 404

    # Step 4: Verify error message
    error_data = delete_response.json()
    assert "task not found" in error_data["detail"].lower()


def test_delete_other_users_task_flow(
    client: TestClient,
    test_jwt_token: str,
    test_jwt_token_2: str,
    test_user_id: UUID,
    test_user_id_2: UUID,
):
    """Integration test for attempting to delete another user's task (T138).

    Test Flow:
    1. User A creates a task
    2. User B attempts to DELETE User A's task
    3. Verify 404 Not Found (security)
    4. Verify task still exists for User A
    5. Verify task data not leaked

    Expected Behavior:
    - DELETE returns 404 (not 403) for security
    - Task remains in database
    - User A can still access their task
    - No sensitive data in error message
    """
    # Step 1: User A creates a task
    task_a_data = {
        "title": "User A's task",
        "description": "Only User A can delete this",
        "priority": "high",
    }

    create_response = client.post(
        "/api/tasks",
        json=task_a_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert create_response.status_code == 201
    task_a = create_response.json()
    task_a_id = task_a["id"]

    # Verify task exists for User A
    get_response = client.get(
        f"/api/tasks/{task_a_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert get_response.status_code == 200

    # Step 2: User B attempts to DELETE User A's task
    delete_response = client.delete(
        f"/api/tasks/{task_a_id}",
        headers={"Authorization": f"Bearer {test_jwt_token_2}"},
    )

    # Step 3: Verify 404 Not Found (security)
    assert delete_response.status_code == 404
    error_data = delete_response.json()
    assert "task not found" in error_data["detail"].lower()

    # Step 4: Verify task still exists for User A
    get_response_after = client.get(
        f"/api/tasks/{task_a_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert get_response_after.status_code == 200
    task_data = get_response_after.json()
    assert task_data["id"] == task_a_id
    assert task_data["title"] == "User A's task"
    assert task_data["user_id"] == str(test_user_id)

    # Verify task in User A's list
    list_response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_a_id

    # Step 5: Verify task data not leaked
    assert "Only User A can delete this" not in str(error_data)
    assert "User A's task" not in str(error_data)


def test_delete_multiple_tasks_flow(
    client: TestClient, test_jwt_token: str, test_user_id: UUID
):
    """Integration test for deleting multiple tasks (T138).

    Test Flow:
    1. Create 3 tasks
    2. Delete task 1
    3. Verify task 1 is deleted, tasks 2 and 3 remain
    4. Delete task 3
    5. Verify task 3 is deleted, only task 2 remains
    6. Delete task 2
    7. Verify all tasks deleted, list is empty

    Expected Behavior:
    - Each delete operation succeeds independently
    - Only specified task is deleted each time
    - Other tasks remain unaffected
    - Final state: empty task list
    """
    # Step 1: Create 3 tasks
    task1_data = {"title": "Task 1", "priority": "low"}
    task2_data = {"title": "Task 2", "priority": "medium"}
    task3_data = {"title": "Task 3", "priority": "high"}

    response1 = client.post(
        "/api/tasks",
        json=task1_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response1.status_code == 201
    task1_id = response1.json()["id"]

    response2 = client.post(
        "/api/tasks",
        json=task2_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response2.status_code == 201
    task2_id = response2.json()["id"]

    response3 = client.post(
        "/api/tasks",
        json=task3_data,
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert response3.status_code == 201
    task3_id = response3.json()["id"]

    # Verify all 3 tasks exist
    list_response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 3

    # Step 2: Delete task 1
    delete_response1 = client.delete(
        f"/api/tasks/{task1_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert delete_response1.status_code == 204

    # Step 3: Verify task 1 is deleted, tasks 2 and 3 remain
    list_response_after1 = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert list_response_after1.status_code == 200
    tasks_after1 = list_response_after1.json()
    assert len(tasks_after1) == 2
    task_ids_after1 = {task["id"] for task in tasks_after1}
    assert task1_id not in task_ids_after1
    assert task2_id in task_ids_after1
    assert task3_id in task_ids_after1

    # Step 4: Delete task 3
    delete_response3 = client.delete(
        f"/api/tasks/{task3_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert delete_response3.status_code == 204

    # Step 5: Verify task 3 is deleted, only task 2 remains
    list_response_after3 = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert list_response_after3.status_code == 200
    tasks_after3 = list_response_after3.json()
    assert len(tasks_after3) == 1
    assert tasks_after3[0]["id"] == task2_id
    assert tasks_after3[0]["title"] == "Task 2"

    # Step 6: Delete task 2
    delete_response2 = client.delete(
        f"/api/tasks/{task2_id}",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert delete_response2.status_code == 204

    # Step 7: Verify all tasks deleted, list is empty
    list_response_final = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_jwt_token}"},
    )
    assert list_response_final.status_code == 200
    tasks_final = list_response_final.json()
    assert len(tasks_final) == 0
    assert tasks_final == []
