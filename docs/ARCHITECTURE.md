# Hackathon Todo - System Architecture

Comprehensive architecture documentation for the full-stack todo application.

## Table of Contents

- [Overview](#overview)
- [Architecture Diagram](#architecture-diagram)
- [Component Layers](#component-layers)
- [Data Flow](#data-flow)
- [Security Model](#security-model)
- [Database Design](#database-design)
- [API Design](#api-design)
- [Authentication Flow](#authentication-flow)
- [Deployment Architecture](#deployment-architecture)
- [Performance Optimizations](#performance-optimizations)

## Overview

The Hackathon Todo application is a full-stack web application built with modern technologies and best practices for security, performance, and scalability.

**Technology Stack**:
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python 3.13), SQLModel ORM
- **Database**: Neon PostgreSQL (cloud-hosted)
- **Authentication**: Better-Auth (JWT-based)
- **Hosting**: Vercel (frontend), Railway/Render (backend)

**Key Features**:
- User authentication with JWT tokens
- User-scoped task management (CRUD operations)
- Real-time filtering and sorting
- Security hardening (rate limiting, CSP, input validation)
- RESTful API design
- Responsive UI design

## Architecture Diagram

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Browser (Chrome, Firefox, Safari)              │  │
│  │                                                          │  │
│  │  - JavaScript Runtime                                    │  │
│  │  - React Components                                      │  │
│  │  - State Management                                      │  │
│  │  - Local Storage (JWT tokens)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓ HTTPS                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Next.js 16 Application                       │  │
│  │              (Deployed on Vercel)                         │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Pages (App Router)                                │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  /                 - Landing page            │  │  │  │
│  │  │  │  /login            - Login page              │  │  │  │
│  │  │  │  /signup           - Signup page             │  │  │  │
│  │  │  │  /tasks            - Task list page          │  │  │  │
│  │  │  │  /tasks/[id]/edit  - Task edit page          │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Components                                        │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  - TaskCard       (Display single task)      │  │  │  │
│  │  │  │  - TaskTable      (Display task list)        │  │  │  │
│  │  │  │  - TaskFilters    (Filter controls)          │  │  │  │
│  │  │  │  - TaskForm       (Create/edit form)         │  │  │  │
│  │  │  │  - UI Components  (Button, Input, etc.)      │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  API Client (lib/api/tasks.ts)                     │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  - getTasks()                                │  │  │  │
│  │  │  │  - createTask()                              │  │  │  │
│  │  │  │  - updateTask()                              │  │  │  │
│  │  │  │  - deleteTask()                              │  │  │  │
│  │  │  │  - completeTask()                            │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Better-Auth (lib/auth.ts)                         │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  - Signup/Login                              │  │  │  │
│  │  │  │  - JWT Token Management                      │  │  │  │
│  │  │  │  - Session State                             │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓ REST API (HTTPS)                   │
│                     Authorization: Bearer <JWT>                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Application                          │  │
│  │         (Deployed on Railway/Render/VPS)                  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Middleware Stack                                  │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  1. CORS Middleware                          │  │  │  │
│  │  │  │     - Allow frontend origin                  │  │  │  │
│  │  │  │     - Credentials enabled                    │  │  │  │
│  │  │  │                                              │  │  │  │
│  │  │  │  2. Security Headers Middleware (T159)       │  │  │  │
│  │  │  │     - X-Content-Type-Options: nosniff        │  │  │  │
│  │  │  │     - X-Frame-Options: DENY                  │  │  │  │
│  │  │  │     - X-XSS-Protection: 1; mode=block        │  │  │  │
│  │  │  │     - Referrer-Policy                        │  │  │  │
│  │  │  │                                              │  │  │  │
│  │  │  │  3. Cache Control Middleware (T152)          │  │  │  │
│  │  │  │     - GET requests: Cache-Control headers   │  │  │  │
│  │  │  │     - POST/PUT/DELETE: No cache              │  │  │  │
│  │  │  │                                              │  │  │  │
│  │  │  │  4. Rate Limiting Middleware (T156)          │  │  │  │
│  │  │  │     - Auth endpoints: 5 req/hour per IP     │  │  │  │
│  │  │  │     - Task endpoints: 100 req/hour per user │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Routes Layer (/api/tasks)                         │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  GET    /api/tasks          - List tasks     │  │  │  │
│  │  │  │  POST   /api/tasks          - Create task    │  │  │  │
│  │  │  │  GET    /api/tasks/{id}     - Get task       │  │  │  │
│  │  │  │  PUT    /api/tasks/{id}     - Update task    │  │  │  │
│  │  │  │  PATCH  /api/tasks/{id}/... - Complete task  │  │  │  │
│  │  │  │  DELETE /api/tasks/{id}     - Delete task    │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  │                  ↓ Depends(get_current_user)        │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  JWT Authentication (auth/jwt_middleware.py)       │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  - Extract JWT from Authorization header     │  │  │  │
│  │  │  │  - Verify signature with JWT_SECRET          │  │  │  │
│  │  │  │  - Decode payload (user_id, email)           │  │  │  │
│  │  │  │  - Return current user                       │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Service Layer (services/task_service.py)          │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  - create_task(user_id, task_data)           │  │  │  │
│  │  │  │  - get_tasks(user_id, filters, sort, page)   │  │  │  │
│  │  │  │  - get_task(user_id, task_id)                │  │  │  │
│  │  │  │  - update_task(user_id, task_id, task_data)  │  │  │  │
│  │  │  │  - delete_task(user_id, task_id)             │  │  │  │
│  │  │  │  - complete_task(user_id, task_id)           │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  │     Business Logic & Validation                     │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Models Layer (models/task.py)                     │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  Task (SQLModel ORM)                         │  │  │  │
│  │  │  │  - id: UUID (Primary Key)                    │  │  │  │
│  │  │  │  - user_id: UUID (Foreign Key)               │  │  │  │
│  │  │  │  - title: str (1-200 chars)                  │  │  │  │
│  │  │  │  - description: str | None (0-2000 chars)    │  │  │  │
│  │  │  │  - due_date: date | None                     │  │  │  │
│  │  │  │  - priority: Priority (low|medium|high)      │  │  │  │
│  │  │  │  - status: Status (pending|completed)        │  │  │  │
│  │  │  │  - created_at: datetime                      │  │  │  │
│  │  │  │  - updated_at: datetime                      │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  │     Pydantic Validation (T157)                      │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                      ↓ SQLAlchemy ORM                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Neon PostgreSQL (Cloud-Hosted)                    │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Tables                                            │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  tasks                                       │  │  │  │
│  │  │  │  - id (UUID, PK)                             │  │  │  │
│  │  │  │  - user_id (UUID, FK → users.id, INDEXED)   │  │  │  │
│  │  │  │  - title (VARCHAR(200), NOT NULL)            │  │  │  │
│  │  │  │  - description (TEXT, NULLABLE)              │  │  │  │
│  │  │  │  - due_date (DATE, NULLABLE, INDEXED)        │  │  │  │
│  │  │  │  - priority (ENUM, NOT NULL, DEFAULT medium) │  │  │  │
│  │  │  │  - status (ENUM, NOT NULL, DEFAULT pending)  │  │  │  │
│  │  │  │  - created_at (TIMESTAMP, NOT NULL)          │  │  │  │
│  │  │  │  - updated_at (TIMESTAMP, NOT NULL)          │  │  │  │
│  │  │  │                                              │  │  │  │
│  │  │  │  users (Managed by Better-Auth)              │  │  │  │
│  │  │  │  - id (UUID, PK)                             │  │  │  │
│  │  │  │  - email (VARCHAR, UNIQUE)                   │  │  │  │
│  │  │  │  - name (VARCHAR)                            │  │  │  │
│  │  │  │  - created_at (TIMESTAMP)                    │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Indexes (Performance Optimization)                │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  - idx_user_id (user_id)                     │  │  │  │
│  │  │  │  - idx_status (status)                       │  │  │  │
│  │  │  │  - idx_due_date (due_date)                   │  │  │  │
│  │  │  │  - idx_user_status (user_id, status)         │  │  │  │
│  │  │  │  - idx_user_due_date (user_id, due_date)     │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Layers

### 1. Client Layer

**Technology**: Browser (JavaScript runtime)

**Responsibilities**:
- Render React components
- Execute JavaScript/TypeScript
- Store JWT tokens in localStorage/cookies
- Handle user interactions
- Make HTTP requests to frontend

### 2. Frontend Layer

**Technology**: Next.js 16 + React 19 + TypeScript

**Responsibilities**:
- Server-side rendering (SSR) and static generation
- API route handling
- Authentication state management
- UI component rendering
- API client for backend communication

**Key Components**:
- **Pages**: Route-based page components
- **Components**: Reusable UI components
- **API Client**: HTTP client for backend API
- **Auth**: Better-Auth integration

### 3. Backend Layer

**Technology**: FastAPI + Python 3.13

**Responsibilities**:
- RESTful API endpoints
- JWT token validation
- Business logic enforcement
- Data validation and sanitization
- Database operations (via ORM)
- Security middleware (CORS, rate limiting, headers)

**Key Components**:
- **Routes**: API endpoint handlers
- **Services**: Business logic layer
- **Models**: SQLModel ORM models
- **Auth**: JWT middleware
- **Middleware**: Security, caching, rate limiting

### 4. Database Layer

**Technology**: Neon PostgreSQL (cloud-hosted)

**Responsibilities**:
- Persistent data storage
- ACID transactions
- Indexing for performance
- User and task data management

## Data Flow

### 1. Create Task Flow

```
User fills form → Frontend validates → API Client sends POST request
                                              ↓
                                       Authorization: Bearer <JWT>
                                              ↓
Backend receives request → CORS middleware → Security headers middleware
                                              ↓
                                    Cache middleware (skip for POST)
                                              ↓
                                    Rate limiter checks limit
                                              ↓
                                    Route handler (POST /api/tasks)
                                              ↓
                                    JWT middleware validates token
                                              ↓
                                    Extract user_id from JWT payload
                                              ↓
                                    Pydantic validates request body
                                              ↓
                                    TaskService.create_task(user_id, task_data)
                                              ↓
                                    SQLModel creates Task instance
                                              ↓
                                    Database INSERT with user_id
                                              ↓
                                    Return Task object with 201 Created
                                              ↓
Frontend receives response → Update UI → Display new task in list
```

### 2. List Tasks Flow (with Filtering)

```
User visits /tasks page → Frontend fetches tasks → API Client sends GET request
                                                           ↓
                                                  Authorization: Bearer <JWT>
                                                           ↓
                                                  Query params: ?status=pending&sort_by=due_date
                                                           ↓
Backend receives request → Middleware stack (CORS, security, cache, rate limit)
                                                           ↓
                                                  Route handler (GET /api/tasks)
                                                           ↓
                                                  JWT middleware validates token
                                                           ↓
                                                  Extract user_id from JWT
                                                           ↓
                                                  Parse query parameters
                                                           ↓
                                                  TaskService.get_tasks(user_id, filters, sort)
                                                           ↓
                                                  Build SQL query:
                                                  SELECT * FROM tasks
                                                  WHERE user_id = ? AND status = ?
                                                  ORDER BY due_date ASC
                                                           ↓
                                                  Database executes query (uses indexes)
                                                           ↓
                                                  Return list of Task objects
                                                           ↓
                                                  Add Cache-Control: max-age=60
                                                           ↓
Frontend receives response → Render TaskTable component → Display tasks
```

### 3. Update Task Flow

```
User edits task → Frontend validates → API Client sends PUT request
                                              ↓
                                       Authorization: Bearer <JWT>
                                              ↓
                                       Request body: {title, description, ...}
                                              ↓
Backend receives request → Middleware stack → Route handler (PUT /api/tasks/{id})
                                              ↓
                                       JWT middleware validates token
                                              ↓
                                       Extract user_id from JWT
                                              ↓
                                       Pydantic validates request body
                                              ↓
                                       TaskService.update_task(user_id, task_id, task_data)
                                              ↓
                                       Database query:
                                       SELECT * FROM tasks WHERE id = ? AND user_id = ?
                                       (ensures ownership)
                                              ↓
                                       If not found → 404 Not Found
                                       If found → Update fields
                                              ↓
                                       Database UPDATE with new values
                                       SET updated_at = NOW() (via trigger)
                                              ↓
                                       Return updated Task object
                                              ↓
Frontend receives response → Update UI → Display updated task
```

### 4. Delete Task Flow

```
User clicks delete → Confirmation dialog → API Client sends DELETE request
                                                    ↓
                                           Authorization: Bearer <JWT>
                                                    ↓
Backend receives request → Middleware stack → Route handler (DELETE /api/tasks/{id})
                                                    ↓
                                           JWT middleware validates token
                                                    ↓
                                           Extract user_id from JWT
                                                    ↓
                                           TaskService.delete_task(user_id, task_id)
                                                    ↓
                                           Database query:
                                           SELECT * FROM tasks WHERE id = ? AND user_id = ?
                                                    ↓
                                           If not found → 404 Not Found
                                           If found → DELETE FROM tasks WHERE id = ?
                                                    ↓
                                           Return 204 No Content
                                                    ↓
Frontend receives response → Remove task from UI → Update task list
```

## Security Model

### 1. Authentication

**JWT Token-Based Authentication**:

```
1. User signs up/logs in (Better-Auth)
   ↓
2. Better-Auth creates user in database
   ↓
3. Better-Auth generates JWT token
   - Header: {"alg": "HS256", "typ": "JWT"}
   - Payload: {"user_id": "uuid", "email": "user@example.com", "exp": timestamp}
   - Signature: HMACSHA256(header + payload, JWT_SECRET)
   ↓
4. Token stored in browser (cookie/localStorage)
   ↓
5. All API requests include: Authorization: Bearer <token>
   ↓
6. Backend verifies token signature
   ↓
7. Extract user_id from payload
   ↓
8. Use user_id for database queries
```

### 2. User Isolation

**Database-Level Enforcement**:

All task queries MUST include `user_id` filter:

```sql
-- Correct (user-scoped)
SELECT * FROM tasks WHERE user_id = 'current-user-id';

-- Incorrect (security vulnerability!)
SELECT * FROM tasks;  -- Would return all users' tasks
```

**Backend Enforcement**:
- JWT middleware extracts `user_id` from token
- All service methods require `user_id` parameter
- Database queries automatically filtered by `user_id`

**Security for "Not Found" vs "Forbidden"**:
- Return 404 for both "task doesn't exist" and "task belongs to another user"
- Prevents user enumeration attacks

### 3. Input Validation (T157)

**Frontend Validation**:
- React form validation (client-side)
- TypeScript type checking
- Prevent submission of invalid data

**Backend Validation** (Primary Defense):
- Pydantic models enforce field constraints
- SQLModel validates data types
- Parameterized queries prevent SQL injection

**Validation Rules**:
```python
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)  # Required, 1-200 chars
    description: str | None = Field(None, max_length=2000)  # Optional, max 2000
    due_date: date | None = None  # Optional, ISO date format
    priority: Priority = Priority.MEDIUM  # Enum: low|medium|high
```

### 4. Rate Limiting (T156)

**Protection Against Abuse**:

| Endpoint | Limit | Window | Key |
|----------|-------|--------|-----|
| Auth endpoints | 5 requests | 1 hour | IP address |
| Task endpoints | 100 requests | 1 hour | user_id |

**Implementation**:
- In-memory rate limit tracking (per process)
- Returns 429 Too Many Requests when exceeded
- Includes `Retry-After` header with seconds to wait

### 5. Security Headers (T159)

**OWASP Best Practices**:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000 (production only)
```

### 6. Content Security Policy (T158)

**Frontend CSP Headers**:

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  connect-src 'self' https://api.your-domain.com;
  object-src 'none';
  frame-src 'none';
```

## Database Design

### Tasks Table Schema

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date DATE,
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    status VARCHAR(10) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_user_id ON tasks(user_id);
CREATE INDEX idx_status ON tasks(status);
CREATE INDEX idx_due_date ON tasks(due_date);
CREATE INDEX idx_user_status ON tasks(user_id, status);
CREATE INDEX idx_user_due_date ON tasks(user_id, due_date);

-- Trigger for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Index Strategy

**Query Patterns**:
1. List all user's tasks: `WHERE user_id = ?`
2. Filter by status: `WHERE user_id = ? AND status = ?`
3. Sort by due date: `ORDER BY due_date`
4. Overdue tasks: `WHERE user_id = ? AND due_date < NOW() AND status = 'pending'`

**Index Coverage**:
- `idx_user_id`: Covers user-scoped queries
- `idx_user_status`: Covers status filtering
- `idx_user_due_date`: Covers date sorting and overdue detection

## API Design

### RESTful Principles

**Resource-Based URLs**:
- `/api/tasks` - Collection of tasks
- `/api/tasks/{id}` - Single task resource

**HTTP Methods**:
- `GET`: Retrieve resources (idempotent)
- `POST`: Create new resource
- `PUT`: Full update of resource (idempotent)
- `PATCH`: Partial update (e.g., complete task)
- `DELETE`: Remove resource (idempotent)

**Status Codes**:
- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Invalid/missing JWT
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded

### API Versioning

**Current**: No versioning (v1 implied)

**Future**: Add version prefix if breaking changes needed:
- `/api/v2/tasks`

## Authentication Flow

### Signup Flow

```
1. User submits signup form (email, password, name)
   ↓
2. Frontend sends to Better-Auth
   ↓
3. Better-Auth hashes password (bcrypt)
   ↓
4. Better-Auth creates user in database
   ↓
5. Better-Auth generates JWT token
   - Payload: {user_id, email, exp}
   - Signature: HMACSHA256(payload, BETTER_AUTH_SECRET)
   ↓
6. Token returned to frontend
   ↓
7. Frontend stores token in cookie/localStorage
   ↓
8. Redirect to /tasks
```

### Login Flow

```
1. User submits login form (email, password)
   ↓
2. Frontend sends to Better-Auth
   ↓
3. Better-Auth queries database for user
   ↓
4. Better-Auth verifies password hash
   ↓
5. If valid, generate JWT token
   ↓
6. Return token to frontend
   ↓
7. Frontend stores token
   ↓
8. Redirect to /tasks
```

### API Request Flow (Authenticated)

```
1. Frontend makes API request
   ↓
2. Include Authorization header: Bearer <JWT>
   ↓
3. Backend JWT middleware receives request
   ↓
4. Extract token from header
   ↓
5. Verify signature using JWT_SECRET
   ↓
6. If invalid → 401 Unauthorized
   ↓
7. If valid, decode payload
   ↓
8. Extract user_id, email
   ↓
9. Inject user into request context
   ↓
10. Route handler uses current_user.id for queries
```

## Deployment Architecture

### Production Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    USERS (Browsers)                         │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                    CDN (Vercel Edge)                        │
│  - Global edge network                                      │
│  - Static asset caching                                     │
│  - DDoS protection                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               FRONTEND (Vercel/Netlify)                     │
│  - Next.js SSR/SSG                                          │
│  - Auto-scaling                                             │
│  - HTTPS (auto-renewed)                                     │
│  - Environment variables                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓ REST API (HTTPS)
┌─────────────────────────────────────────────────────────────┐
│               BACKEND (Railway/Render/VPS)                  │
│  - FastAPI application                                      │
│  - Uvicorn ASGI server (4 workers)                          │
│  - Auto-scaling (Railway/Render)                            │
│  - HTTPS (auto-renewed)                                     │
│  - Environment variables                                    │
│  - Health checks                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓ PostgreSQL Protocol (SSL)
┌─────────────────────────────────────────────────────────────┐
│               DATABASE (Neon PostgreSQL)                    │
│  - Cloud-hosted PostgreSQL                                  │
│  - Auto-scaling storage                                     │
│  - Auto-backups (daily)                                     │
│  - Point-in-time recovery                                   │
│  - SSL/TLS encryption                                       │
└─────────────────────────────────────────────────────────────┘
```

## Performance Optimizations

### 1. Caching Strategy

**Frontend**:
- Next.js static generation for landing page
- Client-side caching (React Query/SWR)
- Browser caching for static assets

**Backend**:
- Cache-Control headers on GET requests
- Task list: 60 seconds
- Individual tasks: 300 seconds

### 2. Database Optimizations

**Indexes**:
- B-tree indexes on `user_id`, `status`, `due_date`
- Composite indexes for common query patterns

**Connection Pooling**:
- SQLAlchemy manages connection pool
- Reuses connections for better performance

### 3. API Optimizations

**Pagination**:
- Default limit: 100 tasks per request
- Skip/limit parameters for large datasets

**Selective Fields** (Future):
- Query parameter to select specific fields
- Reduce payload size

### 4. Frontend Optimizations

**Code Splitting**:
- Next.js automatic code splitting
- Dynamic imports for large components

**Image Optimization**:
- Next.js Image component
- WebP format with fallbacks

**Bundle Size**:
- Tree-shaking for unused code
- Minification and compression

---

## Conclusion

This architecture provides:
- **Security**: JWT auth, input validation, rate limiting, security headers
- **Scalability**: Horizontal scaling, caching, database indexing
- **Maintainability**: Layered architecture, separation of concerns
- **Performance**: Optimized queries, caching, CDN delivery
- **Reliability**: Auto-backups, error handling, monitoring

For more details, see:
- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
- [API Documentation](../API_DOCUMENTATION.md)
- [Deployment Guides](../backend/DEPLOY.md)
