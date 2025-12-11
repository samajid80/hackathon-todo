# Implementation Plan: Phase 2 Full-Stack Todo Web Application

**Branch**: `002-fullstack-web-app` | **Date**: 2025-12-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fullstack-web-app/spec.md`

## Summary

Transform Phase 1's in-memory console Todo application into a production-ready full-stack web application with:
- **Frontend**: Next.js 16 App Router + Better-Auth for authentication and session management
- **Backend**: FastAPI REST API with JWT validation and user-scoped data access
- **Database**: Neon PostgreSQL for persistent storage of users and tasks
- **Architecture**: Three-tier separation (frontend/backend/database) with RESTful communication

The implementation will deliver complete CRUD operations for tasks with filtering, sorting, user authentication, and responsive UI, all while maintaining strict user data isolation and preparing for Phase 3 (MCP/chatbot integration).

## Technical Context

**Language/Version**:
- Backend: Python 3.13
- Frontend: TypeScript 5.x with Next.js 16

**Primary Dependencies**:
- Backend: FastAPI, SQLModel, python-jose (JWT), passlib, psycopg2, uvicorn
- Frontend: Next.js 16, Better-Auth, React 19, Tailwind CSS, TypeScript
- Database: Neon PostgreSQL

**Storage**: Neon PostgreSQL (cloud-hosted)
- Users table (managed by Better-Auth)
- Tasks table (managed by FastAPI)
- Indexes on user_id, due_date, status

**Testing**:
- Backend: pytest, pytest-asyncio, httpx (for FastAPI testing)
- Frontend: Jest, React Testing Library, Playwright (E2E)
- Integration: Full flow testing from signup to task operations

**Target Platform**:
- Backend: Linux server (development + production)
- Frontend: Web browsers (Chrome, Firefox, Safari, Edge - last 2 years)
- Responsive design: 320px to 2560px screen width

**Project Type**: Web application (full-stack)

**Performance Goals**:
- Task list page load: <2 seconds for 1000 tasks
- Filtering/sorting: <500ms perceived latency
- API response: <200ms p95 for task operations
- Support 100 concurrent authenticated users

**Constraints**:
- User data isolation: 100% enforcement at backend layer
- JWT validation required on all task endpoints
- No shared state between requests (stateless backend)
- CORS restrictions for frontend domain only
- Database queries must use user_id indexing

**Scale/Scope**:
- Expected users: 100-1000 concurrent
- Tasks per user: Up to 10,000
- API endpoints: 6 core task operations + authentication
- Frontend pages: 5 main views (login, signup, task list, create, edit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance with Phase 2 Constitution v2.0.0

#### ✅ 3.1 Authentication (Next.js + Better-Auth)
- **Requirement**: Sign up, login, logout, session management, JWT issuance, persistent user storage
- **Compliance**: Plan includes Better-Auth setup in frontend with JWT generation for backend communication

#### ✅ 3.2 Task Management (FastAPI + Postgres)
- **Requirement**: CRUD operations with user-scoped access
- **Compliance**: Backend service layer enforces user_id filtering on all operations

#### ✅ 3.3 Frontend Requirements (Next.js 16)
- **Requirement**: Task list, create/edit forms, delete with confirmation, filtering/sorting, responsive UI
- **Compliance**: Plan includes all UI pages with filters, sorts, and responsive design (Tailwind CSS)

#### ✅ 3.4 Backend Requirements (FastAPI)
- **Requirement**: REST endpoints under `/api/tasks`, JWT validation, user_id matching
- **Compliance**: Plan defines 6 REST endpoints with JWT middleware and user validation

#### ✅ 3.5 Database (Postgres)
- **Requirement**: tasks table with all specified fields and indexes
- **Compliance**: Data model includes all fields (id, user_id, title, description, due_date, priority, status, timestamps) with proper indexing

#### ✅ 5.1 Full-Stack Separation
- **Requirement**: Separate frontend/, backend/, database services
- **Compliance**: Project structure clearly separates concerns

#### ✅ 5.2 Single Source of Truth
- **Requirement**: PostgreSQL as only data store, no duplication
- **Compliance**: Backend is sole data accessor; frontend calls backend only

#### ✅ 5.3 Stateless Backend
- **Requirement**: JWT for identity, no session state, horizontally scalable
- **Compliance**: Backend uses JWT extraction from headers, stores no session data

#### ✅ 5.4 Layered Backend Architecture
- **Requirement**: main.py, routes/, models/, services/, db.py structure
- **Compliance**: Project structure follows prescribed layout

#### ✅ 5.5 Layered Frontend Architecture
- **Requirement**: app/tasks/, app/login/, app/signup/, lib/auth.ts structure
- **Compliance**: Project structure follows prescribed layout

#### ✅ 5.6 Forward Compatibility
- **Requirement**: API stability for Phase 3 MCP/chatbot integration
- **Compliance**: RESTful API design, modular services, indexed database

#### ✅ 6.1 Technology Stack
- **Requirement**: FastAPI (Python 3.13), PostgreSQL (Neon), Next.js 16, Better-Auth, JWT, uv, node 24
- **Compliance**: All required technologies specified in Technical Context

#### ✅ 6.2 Security Constraints
- **Requirement**: JWT signature validation, user isolation, no sensitive info in logs
- **Compliance**: JWT middleware validates signatures; user_id enforcement at service layer; logging excludes sensitive data

#### ✅ 6.3 Performance Constraints
- **Requirement**: Indexed queries (user_id, due_date), reasonable response time for 1000+ tasks
- **Compliance**: Database schema includes indexes; performance goals defined

#### ✅ 7.1 Code Quality
- **Requirement**: Modular, documented, consistent, clear separation of concerns
- **Compliance**: Layered architecture enforces separation; documentation included

#### ✅ 7.2 Testing Requirements
- **Requirement**: Backend tests (CRUD, auth, DB), frontend tests (API hooks, UI), integration tests
- **Compliance**: Testing strategy covers all required areas

#### ✅ 7.3 User Experience Requirements
- **Requirement**: Clean, responsive, professional, error messages visible
- **Compliance**: UI/UX requirements included in frontend design; Tailwind CSS for responsive design

### Gate Result: ✅ PASS

All constitutional requirements are satisfied. No violations require justification.

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-web-app/
├── spec.md               # Feature specification (WHAT)
├── plan.md               # This file (HOW) - /sp.plan output
├── research.md           # Phase 0 output - technology research
├── data-model.md         # Phase 1 output - entity definitions
├── quickstart.md         # Phase 1 output - acceptance test scenarios
├── contracts/            # Phase 1 output - API contracts (OpenAPI)
│   └── tasks-api.yaml
├── checklists/           # Quality validation
│   └── requirements.md
└── tasks.md              # Phase 2 output - /sp.tasks (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── main.py                    # FastAPI application entry point
├── db.py                      # Database session management
├── auth/
│   ├── __init__.py
│   └── jwt_middleware.py      # JWT validation and user extraction
├── models/
│   ├── __init__.py
│   ├── task.py                # SQLModel ORM + Pydantic schemas
│   └── enums.py               # Priority, Status enums
├── routes/
│   ├── __init__.py
│   └── tasks.py               # REST endpoint controllers
├── services/
│   ├── __init__.py
│   └── task_service.py        # Business logic layer
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest fixtures
│   ├── test_auth.py           # JWT validation tests
│   ├── test_task_service.py   # Service layer tests
│   ├── test_task_routes.py    # API endpoint tests
│   └── test_integration.py    # End-to-end flow tests
├── pyproject.toml             # Python dependencies (uv)
├── .env.example               # Environment variables template
└── README.md                  # Backend documentation

frontend/
├── app/
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Landing/redirect page
│   ├── login/
│   │   └── page.tsx           # Login page
│   ├── signup/
│   │   └── page.tsx           # Signup page
│   └── tasks/
│       ├── page.tsx           # Task list with filters/sorts
│       ├── new/
│       │   └── page.tsx       # Create task form
│       └── [id]/
│           └── edit/
│               └── page.tsx   # Edit task form
├── components/
│   ├── TaskCard.tsx           # Individual task display
│   ├── TaskForm.tsx           # Reusable task form
│   ├── FilterBar.tsx          # Filter controls
│   ├── SortControls.tsx       # Sort controls
│   ├── ProtectedRoute.tsx     # Auth guard component
│   └── Toast.tsx              # Notification component
├── lib/
│   ├── auth.ts                # Better-Auth configuration
│   └── api/
│       └── tasks.ts           # API client (fetch wrappers)
├── types/
│   └── task.ts                # TypeScript type definitions
├── tests/
│   ├── unit/
│   │   └── components/        # Component tests
│   └── e2e/
│       └── tasks.spec.ts      # Playwright E2E tests
├── package.json               # Node dependencies
├── tsconfig.json              # TypeScript configuration
├── tailwind.config.js         # Tailwind CSS configuration
├── .env.local.example         # Environment variables template
└── README.md                  # Frontend documentation

database/
├── migrations/                # Database migration files
│   └── 001_initial_schema.sql
├── schema.sql                 # Complete schema definition
└── README.md                  # Database documentation

phase1/                        # ⚠️ DO NOT MODIFY - Phase 1 reference
├── src/
├── tests/
└── ...                        # Preserved as-is
```

**Structure Decision**: Web application (Option 2) selected due to full-stack architecture requirement. Frontend and backend are separate projects communicating via REST API. Phase 1 code remains untouched for reference.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Constitution check passed all gates.

## Phase 0: Research & Technology Validation

**Objective**: Resolve all technology integration questions and document best practices before implementation.

### Research Areas

#### R1: Better-Auth JWT Integration with FastAPI
**Question**: How to configure Better-Auth to generate JWTs that FastAPI can validate?

**Research Tasks**:
- Review Better-Auth documentation for JWT configuration
- Identify JWT signing algorithm (HS256 recommended)
- Define shared secret management between frontend and backend
- Document JWT payload structure (user_id, email, exp, iat)
- Research token refresh strategy (if needed)

**Expected Output**:
- JWT configuration snippet for Better-Auth
- FastAPI JWT validation middleware implementation pattern
- Shared secret storage approach (.env files)

#### R2: SQLModel with Neon PostgreSQL
**Question**: Best practices for SQLModel migrations and Neon database connection?

**Research Tasks**:
- Review SQLModel documentation for async operations
- Research Alembic integration for migrations (SQLModel recommended approach)
- Identify Neon connection string format and SSL requirements
- Document connection pooling strategy for FastAPI
- Research best practices for UUID primary keys in PostgreSQL

**Expected Output**:
- SQLModel model definition pattern
- Alembic migration setup guide
- Database connection configuration

#### R3: Next.js 16 App Router with Better-Auth
**Question**: How to implement protected routes and session management in Next.js 16 App Router?

**Research Tasks**:
- Review Next.js 16 App Router authentication patterns
- Document Better-Auth installation and configuration
- Research middleware for route protection
- Identify session storage approach (cookies vs localStorage)
- Document redirect logic for unauthenticated users

**Expected Output**:
- Protected route HOC/middleware pattern
- Session management implementation
- Better-Auth configuration template

#### R4: CORS Configuration for FastAPI + Next.js
**Question**: Proper CORS setup for development and production environments?

**Research Tasks**:
- Review FastAPI CORS middleware documentation
- Identify allowed origins for development (localhost:3000)
- Document production CORS configuration strategy
- Research credential handling (cookies, Authorization headers)
- Identify preflight request handling

**Expected Output**:
- FastAPI CORS middleware configuration
- Environment-specific CORS settings
- Security considerations

#### R5: Frontend State Management for Tasks
**Question**: Use React Context, Zustand, or direct API calls for task state management?

**Research Tasks**:
- Evaluate state management approaches for CRUD operations
- Consider caching strategy for task list
- Research optimistic updates for better UX
- Document error handling and retry logic
- Identify loading state patterns

**Expected Output**:
- Recommended state management approach
- API client wrapper implementation pattern
- Error handling strategy

#### R6: Responsive UI with Tailwind CSS
**Question**: Best practices for responsive task list layout (320px to 2560px)?

**Research Tasks**:
- Review Tailwind CSS responsive design patterns
- Research mobile-first design approach
- Document breakpoint strategy (sm, md, lg, xl)
- Identify component library options (headlessui, shadcn/ui)
- Research table vs card layout for task list

**Expected Output**:
- Responsive layout pattern
- Mobile/desktop component strategy
- Tailwind configuration

### Research Deliverable

Create `specs/002-fullstack-web-app/research.md` with:
- Decisions made for each research area
- Code snippets and configuration examples
- Links to documentation and resources
- Rationale for technology choices
- Alternative approaches considered

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete

### D1: Data Model

Create `specs/002-fullstack-web-app/data-model.md` with:

#### Entity: User
**Managed by**: Better-Auth

Fields:
- `id`: UUID (Primary Key)
- `email`: String (Unique, Required)
- `password`: String (Hashed, Required)
- `created_at`: Timestamp
- `updated_at`: Timestamp

Relationships:
- Has many Tasks (one-to-many)

Validation:
- Email format validation (RFC 5322)
- Password minimum 8 characters

**Note**: Better-Auth handles user table creation and management. Backend does not directly access users table.

#### Entity: Task
**Managed by**: FastAPI

Fields:
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → users.id, Required)
- `title`: String (Required, max 200 chars)
- `description`: String (Optional, max 2000 chars)
- `due_date`: Date (Optional, ISO 8601 format)
- `priority`: Enum (low, medium, high) (Required, default: medium)
- `status`: Enum (pending, completed) (Required, default: pending)
- `created_at`: Timestamp (Required, auto-generated)
- `updated_at`: Timestamp (Required, auto-updated)

Relationships:
- Belongs to one User (many-to-one)

Indexes:
- `user_id` (for user-scoped queries)
- `due_date` (for sorting and overdue filtering)
- `status` (for status filtering)
- Composite: (`user_id`, `status`) for efficient filtered queries

Validation:
- Title not empty
- Title max 200 characters
- Description max 2000 characters
- Due date valid ISO 8601 format (YYYY-MM-DD)
- Priority one of: low, medium, high
- Status one of: pending, completed

State Transitions:
- Task creation: status = pending (default)
- Mark complete: status = pending → completed (idempotent)
- Update: status can remain or change
- Delete: permanent removal

### D2: API Contracts

Create `specs/002-fullstack-web-app/contracts/tasks-api.yaml` (OpenAPI 3.0):

**Base URL**: `http://localhost:8000` (development)

**Authentication**: All endpoints require JWT in Authorization header:
```
Authorization: Bearer <jwt_token>
```

**Endpoints**:

1. **POST /api/tasks**
   - Create new task
   - Request: TaskCreate schema (title, description, due_date, priority)
   - Response: 201 Created, TaskRead schema
   - Errors: 400 (validation), 401 (unauthorized)

2. **GET /api/tasks**
   - List all user's tasks with optional filters/sorts
   - Query params: status (pending|completed|overdue), sort_by (due_date|priority|status), order (asc|desc)
   - Response: 200 OK, List[TaskRead]
   - Errors: 401 (unauthorized)

3. **GET /api/tasks/{task_id}**
   - Get single task details
   - Path param: task_id (UUID)
   - Response: 200 OK, TaskRead schema
   - Errors: 401 (unauthorized), 403 (not owner), 404 (not found)

4. **PUT /api/tasks/{task_id}**
   - Update task fields
   - Path param: task_id (UUID)
   - Request: TaskUpdate schema (title, description, due_date, priority)
   - Response: 200 OK, TaskRead schema
   - Errors: 400 (validation), 401 (unauthorized), 403 (not owner), 404 (not found)

5. **PATCH /api/tasks/{task_id}/complete**
   - Mark task as completed
   - Path param: task_id (UUID)
   - Response: 200 OK, TaskRead schema
   - Errors: 401 (unauthorized), 403 (not owner), 404 (not found)

6. **DELETE /api/tasks/{task_id}**
   - Delete task permanently
   - Path param: task_id (UUID)
   - Response: 204 No Content
   - Errors: 401 (unauthorized), 403 (not owner), 404 (not found)

**Schemas**:

- **TaskCreate**: { title, description?, due_date?, priority? }
- **TaskUpdate**: { title?, description?, due_date?, priority? }
- **TaskRead**: { id, user_id, title, description, due_date, priority, status, created_at, updated_at }
- **ErrorResponse**: { detail: string }

### D3: Acceptance Test Scenarios

Create `specs/002-fullstack-web-app/quickstart.md` with:

#### Scenario 1: User Signup and Login Flow
```
1. Navigate to http://localhost:3000/signup
2. Fill email: test@example.com, password: password123
3. Submit form
4. EXPECT: Redirect to /tasks, JWT stored in session
5. Click logout
6. EXPECT: Redirect to /login
7. Login with same credentials
8. EXPECT: Redirect to /tasks with active session
```

#### Scenario 2: Create and View Task
```
1. Login as authenticated user
2. Navigate to /tasks/new
3. Fill title: "Buy groceries", priority: high, due_date: tomorrow
4. Submit form
5. EXPECT: Redirect to /tasks, new task visible in list
6. EXPECT: Task shows high priority indicator, due date visible
```

#### Scenario 3: Filter and Sort Tasks
```
1. Create 5 tasks (mix of pending/completed, various priorities)
2. On /tasks page, click "Pending" filter
3. EXPECT: Only pending tasks shown
4. Click "Sort by Priority"
5. EXPECT: Tasks ordered high → medium → low
6. Clear filters
7. EXPECT: All tasks visible again
```

#### Scenario 4: Update and Complete Task
```
1. From task list, click Edit on a pending task
2. Change title to "Updated title"
3. Save changes
4. EXPECT: Title updated in list, updated_at refreshed
5. Click "Mark Complete" button
6. EXPECT: Task moves to completed filter, status indicator changes
```

#### Scenario 5: Delete Task with Confirmation
```
1. From task list, click Delete on a task
2. EXPECT: Confirmation modal appears: "Are you sure you want to delete this task?"
3. Click Cancel
4. EXPECT: Modal closes, task still in list
5. Click Delete again, confirm
6. EXPECT: Task removed from list permanently
```

### D4: Agent Context Update

Run agent context update script:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will update `.claude/agent-context.md` or appropriate agent-specific file with:
- Phase 2 technology stack (Next.js 16, FastAPI, Better-Auth, Neon PostgreSQL)
- Project structure (frontend/, backend/, database/)
- Key integration points (JWT between Better-Auth and FastAPI)

## Implementation Phases (Post-Planning)

**Note**: The following phases are executed by `/sp.tasks` and `/sp.implement` commands, NOT by `/sp.plan`.

### Overview

After planning is approved, implementation proceeds through `/sp.tasks` (generates tasks.md) and `/sp.implement` (executes tasks):

1. **Project Initialization**: Setup frontend and backend projects, install dependencies
2. **Database Setup**: Create Neon database, define schema, run migrations
3. **Backend Core**: Implement models, services, JWT middleware
4. **Backend API**: Implement REST endpoints with validation and error handling
5. **Frontend Auth**: Setup Better-Auth, implement login/signup pages, protected routes
6. **Frontend UI**: Build task list, create/edit forms, filters, sorts
7. **Frontend API Integration**: Connect UI to backend via API client
8. **Testing**: Write and run backend, frontend, and integration tests
9. **Documentation**: Update READMEs, add setup instructions, document API

### Milestones (Tracked in `/sp.implement`)

- **M1**: Project structure initialized, dependencies installed
- **M2**: Database schema deployed to Neon
- **M3**: Backend API functional with JWT validation
- **M4**: Frontend authentication working (signup/login/logout)
- **M5**: Task CRUD UI complete with filters and sorts
- **M6**: End-to-end integration verified (auth + tasks)
- **M7**: Test suite passing (backend + frontend + E2E)
- **M8**: Documentation complete, deployment ready

### Success Criteria (from Spec)

Phase 2 implementation is complete when:
1. ✅ Users can register, log in, and maintain sessions (Better-Auth)
2. ✅ Authenticated users can access task dashboard with JWT validation
3. ✅ All CRUD operations work end-to-end via REST API
4. ✅ Filtering (pending, completed, overdue) and sorting (priority, due_date, status) produce correct results
5. ✅ Task ownership correctly enforced (user_id validation at service layer)
6. ✅ Tasks persist across sessions (PostgreSQL storage)
7. ✅ UI is complete, responsive (320px-2560px), and user-friendly
8. ✅ Errors handled gracefully with clear messages
9. ✅ All functional requirements (FR-001 to FR-072) implemented
10. ✅ All success criteria (SC-001 to SC-015) validated

## Architecture Decision Records (ADRs)

### Recommended ADRs for this Feature

Based on the architectural decisions in this plan, the following ADRs should be created:

1. **ADR: Next.js 16 App Router for Frontend Architecture**
   - Decision: Use Next.js 16 with App Router instead of Pages Router
   - Rationale: Better-Auth compatibility, modern routing patterns, server components
   - Alternatives: Next.js Pages Router, React SPA with React Router

2. **ADR: Better-Auth for Authentication vs Auth.js (NextAuth)**
   - Decision: Use Better-Auth for authentication and JWT generation
   - Rationale: Explicit JWT control for FastAPI integration, simpler configuration
   - Alternatives: Auth.js, custom JWT implementation, Supabase Auth

3. **ADR: FastAPI for Backend vs Django REST Framework**
   - Decision: Use FastAPI for REST API implementation
   - Rationale: Async support, automatic OpenAPI docs, Pydantic validation, performance
   - Alternatives: Django REST Framework, Flask with extensions

4. **ADR: SQLModel for ORM vs SQLAlchemy**
   - Decision: Use SQLModel (combines SQLAlchemy + Pydantic)
   - Rationale: Single source of truth for models, FastAPI integration, type safety
   - Alternatives: Pure SQLAlchemy with separate Pydantic models, Django ORM

5. **ADR: Neon PostgreSQL for Database**
   - Decision: Use Neon for managed PostgreSQL hosting
   - Rationale: Serverless architecture, branching, connection pooling, free tier
   - Alternatives: Self-hosted PostgreSQL, AWS RDS, Supabase

6. **ADR: Tailwind CSS for Styling**
   - Decision: Use Tailwind CSS for responsive design
   - Rationale: Utility-first approach, responsive design helpers, small bundle size
   - Alternatives: CSS Modules, Styled Components, Material-UI

**To create these ADRs**, run:
```bash
/sp.adr "Next.js 16 App Router for Frontend Architecture"
/sp.adr "Better-Auth for Authentication"
/sp.adr "FastAPI for Backend REST API"
/sp.adr "SQLModel for ORM"
/sp.adr "Neon PostgreSQL for Database"
/sp.adr "Tailwind CSS for Styling"
```

## Risk Analysis

### R1: Better-Auth JWT Configuration Complexity
**Risk**: Difficulty configuring Better-Auth to generate JWTs compatible with FastAPI validation

**Mitigation**:
- Research phase includes Better-Auth JWT configuration documentation review
- Use standard HS256 algorithm with shared secret
- Test JWT generation and validation early in implementation
- Fallback: Implement custom JWT generation if Better-Auth incompatible

**Impact**: Medium (could delay authentication integration)
**Probability**: Low (Better-Auth designed for JWT support)

### R2: CORS Issues Between Frontend and Backend
**Risk**: CORS configuration errors preventing frontend from calling backend API

**Mitigation**:
- Configure CORS middleware early in FastAPI setup
- Test with frontend development server immediately
- Use environment variables for allowed origins
- Document CORS setup in research phase

**Impact**: Low (CORS well-documented in FastAPI)
**Probability**: Medium (common development issue)

### R3: User Data Isolation Bugs
**Risk**: Backend service layer fails to enforce user_id filtering, exposing user data

**Mitigation**:
- Write comprehensive tests for user isolation (test_auth.py)
- Code review focus on user_id enforcement in service layer
- Manual testing with multiple user accounts
- Add integration test for cross-user access attempts

**Impact**: High (security vulnerability)
**Probability**: Low (explicit service layer filtering)

### R4: Database Migration Management
**Risk**: Alembic migrations become complex or fail during development

**Mitigation**:
- Start with manual schema.sql for simplicity
- Introduce Alembic only when schema stabilizes
- Use Neon branching for testing migrations
- Keep migration history clean and linear

**Impact**: Medium (could slow development)
**Probability**: Low (simple schema initially)

### R5: Performance with 1000+ Tasks
**Risk**: Task list page slow with large number of tasks per user

**Mitigation**:
- Implement pagination early (default: 50 tasks per page)
- Use database indexes on user_id, due_date, status
- Add query optimization in service layer
- Load test with 10,000 tasks per user

**Impact**: Medium (affects user experience)
**Probability**: Low (proper indexing sufficient)

## Next Steps

After plan approval:

1. **Execute Phase 0 (Research)**:
   ```bash
   # Research will be conducted as part of /sp.plan execution
   # Output: specs/002-fullstack-web-app/research.md
   ```

2. **Execute Phase 1 (Design)**:
   ```bash
   # Design artifacts will be created as part of /sp.plan execution
   # Output: data-model.md, contracts/tasks-api.yaml, quickstart.md
   ```

3. **Generate Tasks**:
   ```bash
   /sp.tasks
   # Output: specs/002-fullstack-web-app/tasks.md
   ```

4. **Implement Features**:
   ```bash
   /sp.implement
   # Executes tasks from tasks.md in dependency order
   ```

5. **Create ADRs** (as architectural decisions are made):
   ```bash
   /sp.adr "<decision-title>"
   ```

6. **Document Progress**:
   - PHRs created automatically for each phase
   - Update checklists as milestones complete
   - Maintain ADRs for significant decisions

## Appendix: Technology References

### Documentation Links

- **Next.js 16**: https://nextjs.org/docs
- **Better-Auth**: https://better-auth.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **SQLModel**: https://sqlmodel.tiangolo.com
- **Neon PostgreSQL**: https://neon.tech/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **JWT**: https://jwt.io/introduction
- **Python Jose**: https://python-jose.readthedocs.io

### Code Examples from Phase 1

Phase 1 implementation (in `phase1/src/`) provides reference for:
- Task domain model (`phase1/src/domain/task.py`)
- Task service layer pattern (`phase1/src/services/task_service.py`)
- Priority and Status enums (`phase1/src/domain/enums.py`)
- Testing patterns (`phase1/tests/`)

**Note**: Phase 1 code should NOT be modified, but can be referenced for domain logic consistency.
