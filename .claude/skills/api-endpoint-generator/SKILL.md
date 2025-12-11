---
name: api-endpoint-generator
description: Generate RESTful FastAPI endpoints from API specs, including route handlers, Pydantic models, JWT auth, and SQLModel operations.
version: 1.0
---

# API Endpoint Generator Skill

## Overview
This skill creates FastAPI API endpoints (e.g., CRUD for /api/tasks) based on specs, incorporating JWT authentication for user filtering, Pydantic for validation, and SQLModel for database interactions in Phase 2.

## Instructions
1. Parse the API spec (e.g., @specs/api/rest.md) for endpoints, methods, params, bodies, and responses.
2. Generate route handlers:
   - Use FastAPI decorators (e.g., @app.get("/api/tasks")).
   - Include dependencies for JWT auth (e.g., get_current_user).
   - Use SQLModel for queries (e.g., session.query(Task).filter(Task.user_id == current_user.id)).
   - Add Pydantic models for request/response (e.g., TaskCreate, TaskResponse).
3. Handle query params: e.g., status, sort for filtering/sorting.
4. Error handling: Use HTTPException for 404, 401, etc.
5. Output full route file using @resources/endpoint-template.py, ready for /backend/routes/tasks.py.
6. Suggest additions to main.py (e.g., include_router) and pyproject.toml deps.

## Inputs
- Spec reference: e.g., @specs/api/rest-endpoints.md
- Optional: Existing route paths for extension (e.g., /backend/routes/auth.py)

## Outputs
- Generated Python file (e.g., routes/tasks.py)
- Pydantic model suggestions
- Integration notes for app mounting

## Examples
### Example 1: List Tasks Endpoint
Input Spec: "GET /api/tasks with status/sort params, filtered by user."
Output: Handler with query params, SQLModel select, JWT dependency.

### Example 2: Create Task Endpoint
Input Spec: "POST /api/tasks with title/description body."
Output: Handler with TaskCreate Pydantic, insert to DB, return created task.

## Dependencies
- Backend: fastapi, sqlmodel, pydantic (add to pyproject.toml if missing).

## Testing
Run the included script generate-route.py with method/endpoint to preview code.