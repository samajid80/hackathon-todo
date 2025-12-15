# Hackathon Todo API Documentation

Comprehensive API documentation for the Hackathon Todo full-stack web application backend.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Task Management](#task-management)
- [Examples](#examples)
- [Testing with curl](#testing-with-curl)

## Overview

The Hackathon Todo API is a RESTful API that provides task management functionality with JWT-based authentication. All task endpoints are user-scoped, ensuring that users can only access their own tasks.

**Key Features**:
- JWT authentication for all task operations
- User-specific task isolation
- Filtering and sorting capabilities
- Input validation and sanitization
- Rate limiting for security
- Comprehensive error handling

## Base URL

**Development**: `http://localhost:8000`

**Production**: `https://api.your-domain.com`

## Authentication

All task endpoints require JWT authentication using Better-Auth.

### Authentication Header

Include the JWT token in the `Authorization` header for all authenticated requests:

```
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

Tokens are issued by Better-Auth during the signup/login process in the frontend application. The frontend handles token storage and automatically includes it in API requests.

### Example Authenticated Request

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  http://localhost:8000/api/tasks
```

## Error Handling

The API returns standard HTTP status codes with JSON error responses.

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Status Code | Description | Example |
|-------------|-------------|---------|
| `200 OK` | Successful GET/PUT/PATCH request | Task retrieved successfully |
| `201 Created` | Successful POST request | Task created successfully |
| `204 No Content` | Successful DELETE request | Task deleted successfully |
| `400 Bad Request` | Invalid request payload | Missing required field |
| `401 Unauthorized` | Missing or invalid JWT token | Token expired |
| `403 Forbidden` | Insufficient permissions | Accessing another user's task |
| `404 Not Found` | Resource not found | Task ID doesn't exist |
| `422 Unprocessable Entity` | Validation error | Invalid date format |
| `429 Too Many Requests` | Rate limit exceeded | Too many requests |
| `500 Internal Server Error` | Unexpected server error | Database connection failure |

### Example Error Responses

**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```

**404 Not Found**:
```json
{
  "detail": "Task not found"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**429 Rate Limit**:
```json
{
  "detail": "Rate limit exceeded. Retry after 3600 seconds."
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/auth/signup` | 5 requests | Per hour per IP |
| `/api/auth/login` | 5 requests | Per hour per IP |
| `/api/tasks` (all methods) | 100 requests | Per hour per user |
| `/api/tasks/{id}` (all methods) | 100 requests | Per hour per user |

**Rate Limit Headers**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)
- `Retry-After`: Seconds to wait before retrying (on 429 response)

## Endpoints

### Health Check

#### GET /

Get API information and status.

**Authentication**: Not required

**Request**:
```bash
curl http://localhost:8000/
```

**Response** (200 OK):
```json
{
  "status": "ok",
  "message": "Hackathon Todo API",
  "version": "1.0.0",
  "docs": "/api/docs"
}
```

#### GET /health

Check if the API service is running.

**Authentication**: Not required

**Request**:
```bash
curl http://localhost:8000/health
```

**Response** (200 OK):
```json
{
  "status": "healthy"
}
```

### Task Management

All task endpoints require JWT authentication.

#### POST /api/tasks

Create a new task.

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables",
  "due_date": "2025-12-15",
  "priority": "high"
}
```

**Field Constraints**:
- `title` (required): 1-200 characters
- `description` (optional): 0-2000 characters
- `due_date` (optional): ISO 8601 date format (YYYY-MM-DD)
- `priority` (optional): `low`, `medium`, or `high` (default: `medium`)

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "due_date": "2025-12-15",
    "priority": "high"
  }'
```

**Response** (201 Created):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "due_date": "2025-12-15",
  "priority": "high",
  "status": "pending",
  "created_at": "2025-12-12T10:30:00Z",
  "updated_at": "2025-12-12T10:30:00Z"
}
```

---

#### GET /api/tasks

List all tasks for the authenticated user with optional filtering, sorting, and pagination.

**Authentication**: Required (JWT)

**Query Parameters**:
- `status` (optional): Filter by status (`pending`, `completed`)
- `priority` (optional): Filter by priority (`low`, `medium`, `high`)
- `overdue` (optional): Filter overdue tasks (`true`, `false`)
- `sort_by` (optional): Sort field (`created_at`, `due_date`, `priority`, `status`)
- `sort_order` (optional): Sort direction (`asc`, `desc`) (default: `asc`)
- `skip` (optional): Number of tasks to skip for pagination (default: `0`)
- `limit` (optional): Maximum tasks to return (default: `100`, max: `100`)

**Example Request** (all tasks):
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/tasks
```

**Example Request** (filtered and sorted):
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/tasks?status=pending&priority=high&sort_by=due_date&sort_order=asc"
```

**Example Request** (overdue tasks):
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/tasks?overdue=true&sort_by=due_date"
```

**Response** (200 OK):
```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "user_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "due_date": "2025-12-15",
    "priority": "high",
    "status": "pending",
    "created_at": "2025-12-12T10:30:00Z",
    "updated_at": "2025-12-12T10:30:00Z"
  },
  {
    "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "user_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "title": "Finish project report",
    "description": null,
    "due_date": "2025-12-20",
    "priority": "medium",
    "status": "pending",
    "created_at": "2025-12-12T11:00:00Z",
    "updated_at": "2025-12-12T11:00:00Z"
  }
]
```

---

#### GET /api/tasks/{task_id}

Get details of a specific task.

**Authentication**: Required (JWT)

**Path Parameters**:
- `task_id` (required): UUID of the task

**Example Request**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response** (200 OK):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "due_date": "2025-12-15",
  "priority": "high",
  "status": "pending",
  "created_at": "2025-12-12T10:30:00Z",
  "updated_at": "2025-12-12T10:30:00Z"
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Task not found"
}
```

---

#### PUT /api/tasks/{task_id}

Update a task (full update - all fields required except description and due_date).

**Authentication**: Required (JWT)

**Path Parameters**:
- `task_id` (required): UUID of the task

**Request Body**:
```json
{
  "title": "Buy groceries and cook dinner",
  "description": "Updated description",
  "due_date": "2025-12-16",
  "priority": "medium",
  "status": "pending"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and cook dinner",
    "description": "Updated description",
    "due_date": "2025-12-16",
    "priority": "medium",
    "status": "pending"
  }'
```

**Response** (200 OK):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "title": "Buy groceries and cook dinner",
  "description": "Updated description",
  "due_date": "2025-12-16",
  "priority": "medium",
  "status": "pending",
  "created_at": "2025-12-12T10:30:00Z",
  "updated_at": "2025-12-12T14:45:00Z"
}
```

---

#### PATCH /api/tasks/{task_id}/complete

Mark a task as completed.

**Authentication**: Required (JWT)

**Path Parameters**:
- `task_id` (required): UUID of the task

**Example Request**:
```bash
curl -X PATCH http://localhost:8000/api/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890/complete \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response** (200 OK):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "due_date": "2025-12-15",
  "priority": "high",
  "status": "completed",
  "created_at": "2025-12-12T10:30:00Z",
  "updated_at": "2025-12-12T15:00:00Z"
}
```

---

#### DELETE /api/tasks/{task_id}

Delete a task.

**Authentication**: Required (JWT)

**Path Parameters**:
- `task_id` (required): UUID of the task

**Example Request**:
```bash
curl -X DELETE http://localhost:8000/api/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response** (204 No Content):
```
(No response body)
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Task not found"
}
```

## Examples

### Complete Workflow Example

This example demonstrates a complete task management workflow:

```bash
# 1. Check API health
curl http://localhost:8000/health

# 2. Create a new task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prepare presentation",
    "description": "Create slides for Monday meeting",
    "due_date": "2025-12-14",
    "priority": "high"
  }'

# Response:
# {
#   "id": "task-uuid-here",
#   "title": "Prepare presentation",
#   ...
# }

# 3. List all pending tasks
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/tasks?status=pending&sort_by=due_date"

# 4. Update the task
curl -X PUT http://localhost:8000/api/tasks/task-uuid-here \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prepare presentation with demo",
    "description": "Create slides and record demo video",
    "due_date": "2025-12-14",
    "priority": "high",
    "status": "pending"
  }'

# 5. Mark task as completed
curl -X PATCH http://localhost:8000/api/tasks/task-uuid-here/complete \
  -H "Authorization: Bearer YOUR_TOKEN"

# 6. Delete the task
curl -X DELETE http://localhost:8000/api/tasks/task-uuid-here \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filtering Examples

**Get all high-priority pending tasks**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/tasks?status=pending&priority=high"
```

**Get overdue tasks sorted by due date**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/tasks?overdue=true&sort_by=due_date&sort_order=asc"
```

**Get completed tasks**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/tasks?status=completed"
```

**Pagination example** (get 10 tasks, skip first 20):
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/tasks?skip=20&limit=10"
```

## Testing with curl

### Setting Up Environment Variables

For easier testing, set your JWT token as an environment variable:

```bash
export TOKEN="your-jwt-token-here"
```

Then use it in requests:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/tasks
```

### Common curl Options

- `-X METHOD`: Specify HTTP method (GET, POST, PUT, PATCH, DELETE)
- `-H "Header: Value"`: Add HTTP header
- `-d '{"json": "data"}'`: Send JSON data in request body
- `-v`: Verbose output (shows headers and debug info)
- `-i`: Include response headers in output
- `-s`: Silent mode (hide progress)

### Error Debugging

Use verbose mode to debug authentication issues:

```bash
curl -v -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/tasks
```

Check response headers:
```bash
curl -i -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/tasks
```

## Interactive API Documentation

The API provides interactive documentation using Swagger UI and ReDoc:

- **Swagger UI**: http://localhost:8000/api/docs
  - Interactive interface to test endpoints
  - Built-in authentication support
  - Request/response examples

- **ReDoc**: http://localhost:8000/api/redoc
  - Clean, readable documentation
  - Better for reference and sharing

- **OpenAPI JSON**: http://localhost:8000/api/openapi.json
  - Raw OpenAPI specification
  - Can be imported into Postman, Insomnia, etc.

## Additional Resources

- **Backend Repository**: https://github.com/your-repo/backend
- **Frontend Repository**: https://github.com/your-repo/frontend
- **Deployment Guide**: [backend/DEPLOY.md](backend/DEPLOY.md)
- **Database Schema**: [backend/README.md#database-schema](backend/README.md#database-schema)
- **Security Features**: [backend/README.md#security-features](backend/README.md#security-features)

## Support

For issues and questions:
- Check the [Troubleshooting section](backend/README.md#troubleshooting) in the backend README
- Review error responses for specific error codes
- Use interactive Swagger docs for testing: http://localhost:8000/api/docs
