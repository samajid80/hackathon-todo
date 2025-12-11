# Implementation Tasks: Phase 2 Full-Stack Todo Web Application

**Branch**: `002-fullstack-web-app` | **Date**: 2025-12-11
**Input**: Design artifacts from `/sp.plan` (spec.md, plan.md, data-model.md, contracts/tasks-api.yaml, research.md, quickstart.md)

## Task Organization

Tasks are organized by user story to enable **independent implementation**. Each user story can be completed by a separate developer without blocking others (after foundational setup is complete).

**Task Format**: `- [ ] [TaskID] [P?] [Story?] Description (file path)`
- **TaskID**: Unique identifier (T001, T002, etc.)
- **P?**: Priority marker (P1=Critical, P2=Important, P3=Nice-to-have)
- **Story?**: User story reference (US1, US2, US3, US4, US5)
- **Description**: Clear, actionable task description
- **File path**: Target file(s) to create or modify

---

## Phase 1: Setup & Foundational Infrastructure

These tasks are **blocking prerequisites** for all user stories. Complete before starting any user story implementation.

### Backend Setup

- [x] [T001] [P1] Create backend directory structure (backend/main.py, backend/db.py, backend/auth/, backend/models/, backend/routes/, backend/services/, backend/tests/)
- [x] [T002] [P1] Initialize Python project with pyproject.toml using uv (backend/pyproject.toml)
- [x] [T003] [P1] Add backend dependencies: FastAPI, SQLModel, python-jose, passlib, psycopg2-binary, uvicorn, pytest, pytest-asyncio, httpx (backend/pyproject.toml)
- [x] [T004] [P1] Create environment variables template with DATABASE_URL, JWT_SECRET, CORS_ORIGINS (backend/.env.example)
- [x] [T005] [P1] Implement database connection with SQLModel engine (backend/db.py)
- [x] [T006] [P1] Create Priority and Status enums (backend/models/enums.py)
- [x] [T007] [P1] Define Task SQLModel with all fields and indexes (backend/models/task.py)
- [x] [T008] [P1] Create TaskCreate, TaskUpdate, TaskRead Pydantic schemas (backend/models/task.py)
- [x] [T009] [P1] Implement JWT middleware for token validation and user extraction (backend/auth/jwt_middleware.py)
- [x] [T010] [P1] Create pytest configuration and fixtures for database testing (backend/tests/conftest.py)
- [x] [T011] [P1] Write tests for JWT middleware validation (backend/tests/test_auth.py)
- [x] [T012] [P1] Create FastAPI app with CORS and JWT middleware registration (backend/main.py)
- [x] [T013] [P1] Write backend README with setup instructions (backend/README.md)

### Frontend Setup

- [x] [T014] [P1] Create frontend directory structure (frontend/app/, frontend/lib/, frontend/components/, frontend/styles/)
- [x] [T015] [P1] Initialize Next.js 16 project with TypeScript and App Router (frontend/package.json, frontend/tsconfig.json, frontend/next.config.js)
- [x] [T016] [P1] Add frontend dependencies: Next.js 16, React 19, Better-Auth, Tailwind CSS (frontend/package.json)
- [x] [T017] [P1] Configure Tailwind CSS with mobile-first responsive design (frontend/tailwind.config.js, frontend/postcss.config.js)
- [x] [T018] [P1] Create environment variables template with NEXT_PUBLIC_API_URL, JWT_SECRET (frontend/.env.local.example)
- [x] [T019] [P1] Configure Better-Auth with JWT and session management (frontend/lib/auth.ts)
- [x] [T020] [P1] Create API client utility for backend communication (frontend/lib/api-client.ts)
- [x] [T021] [P1] Implement root layout with navigation and auth context (frontend/app/layout.tsx)
- [x] [T022] [P1] Create landing page with redirect logic (frontend/app/page.tsx)
- [x] [T023] [P1] Add global styles and Tailwind imports (frontend/styles/globals.css)
- [x] [T024] [P1] Write frontend README with setup instructions (frontend/README.md)

### Database Setup

- [x] [T025] [P1] Create Neon PostgreSQL project and obtain connection string (manual step, document in backend/.env.example)
- [x] [T026] [P1] Create database migration for tasks table with indexes (backend/migrations/001_create_tasks_table.sql)
- [x] [T027] [P1] Create database migration for updated_at trigger (backend/migrations/002_updated_at_trigger.sql)
- [x] [T028] [P1] Write documentation for running database migrations (backend/README.md)

---

## Phase 2: User Story 1 - User Account Creation and Authentication (US1, Priority: P1)

**Acceptance Scenarios**: 7 scenarios covering signup, login, logout, session management, error handling
**Independent**: Can be implemented independently after Phase 1 setup
**Dependencies**: Requires Better-Auth setup (T019), backend JWT middleware (T009)

### Backend Tasks (US1)

- [x] [T029] [P1] [US1] Verify User model exists in Better-Auth (no backend implementation needed, document in backend/README.md)
- [x] [T030] [P1] [US1] Write tests for JWT validation with valid/invalid/expired tokens (backend/tests/test_auth.py)
- [x] [T031] [P1] [US1] Test JWT middleware extracts user_id from token correctly (backend/tests/test_auth.py)

### Frontend Tasks (US1)

- [x] [T032] [P1] [US1] Create signup page with email/password form (frontend/app/signup/page.tsx)
- [x] [T033] [P1] [US1] Implement signup form validation (email format, password length >= 8) (frontend/app/signup/page.tsx)
- [x] [T034] [P1] [US1] Handle signup errors: duplicate email, validation failures (frontend/app/signup/page.tsx)
- [x] [T035] [P1] [US1] Create login page with email/password form (frontend/app/login/page.tsx)
- [x] [T036] [P1] [US1] Implement login form validation and error handling (frontend/app/login/page.tsx)
- [x] [T037] [P1] [US1] Implement auto-redirect to /tasks after successful login (frontend/app/login/page.tsx)
- [x] [T038] [P1] [US1] Add logout button to navigation with session termination (frontend/app/layout.tsx, frontend/components/Navbar.tsx)
- [x] [T039] [P1] [US1] Implement route protection middleware to redirect unauthenticated users (frontend/middleware.ts)
- [x] [T040] [P1] [US1] Display session expiration message on redirect to login (frontend/app/login/page.tsx)
- [x] [T041] [P1] [US1] Create reusable form components: Input, Button, ErrorMessage (frontend/components/ui/)

### Testing Tasks (US1)

- [x] [T042] [P1] [US1] Write integration test for signup flow (backend/tests/test_integration.py)
- [x] [T043] [P1] [US1] Write integration test for login flow (backend/tests/test_integration.py)
- [x] [T044] [P1] [US1] Write integration test for logout flow (backend/tests/test_integration.py)
- [x] [T045] [P1] [US1] Write integration test for unauthenticated access redirect (backend/tests/test_integration.py)

---

## Phase 3: User Story 2 - Create and View Tasks (US2, Priority: P1)

**Acceptance Scenarios**: 7 scenarios covering task creation, viewing, validation, user isolation
**Independent**: Can be implemented independently after Phase 1 setup
**Dependencies**: Requires Task model (T007), JWT middleware (T009), authentication (US1 for testing)

### Backend Tasks (US2)

- [x] [T046] [P1] [US2] Implement create_task service with user_id association (backend/services/task_service.py)
- [x] [T047] [P1] [US2] Implement get_user_tasks service with user_id filtering (backend/services/task_service.py)
- [x] [T048] [P1] [US2] Implement get_task_by_id service with ownership validation (backend/services/task_service.py)
- [x] [T049] [P1] [US2] Create POST /api/tasks endpoint for task creation (backend/routes/tasks.py)
- [x] [T050] [P1] [US2] Create GET /api/tasks endpoint for listing user tasks (backend/routes/tasks.py)
- [x] [T051] [P1] [US2] Create GET /api/tasks/{task_id} endpoint with ownership check (backend/routes/tasks.py)
- [x] [T052] [P1] [US2] Validate task creation: title required, max lengths (backend/routes/tasks.py)
- [x] [T053] [P1] [US2] Return 403 Forbidden when accessing another user's task (backend/routes/tasks.py)
- [x] [T054] [P1] [US2] Return 404 Not Found when task doesn't exist (backend/routes/tasks.py)
- [x] [T055] [P1] [US2] Register task routes with FastAPI app (backend/main.py)

### Frontend Tasks (US2)

- [x] [T056] [P1] [US2] Create task list page with empty state message (frontend/app/tasks/page.tsx)
- [x] [T057] [P1] [US2] Implement task list rendering with title, priority, status, due date (frontend/app/tasks/page.tsx)
- [x] [T058] [P1] [US2] Create task card component for mobile view (frontend/components/TaskCard.tsx)
- [x] [T059] [P1] [US2] Create task table component for desktop view (frontend/components/TaskTable.tsx)
- [x] [T060] [P1] [US2] Implement responsive layout switching (card on mobile, table on desktop) (frontend/app/tasks/page.tsx)
- [x] [T061] [P1] [US2] Create task creation page with form (frontend/app/tasks/new/page.tsx)
- [x] [T062] [P1] [US2] Implement task form validation: title required, max lengths (frontend/app/tasks/new/page.tsx)
- [x] [T063] [P1] [US2] Handle task creation submission and redirect to task list (frontend/app/tasks/new/page.tsx)
- [x] [T064] [P1] [US2] Display success message after task creation (frontend/components/Toast.tsx, frontend/app/tasks/page.tsx)
- [x] [T065] [P1] [US2] Display validation errors on task creation form (frontend/app/tasks/new/page.tsx)
- [x] [T066] [P1] [US2] Add "Create Task" button to task list page (frontend/app/tasks/page.tsx)
- [x] [T067] [P1] [US2] Implement priority badge component with color coding (frontend/components/PriorityBadge.tsx)
- [x] [T068] [P1] [US2] Implement status badge component with visual distinction (frontend/components/StatusBadge.tsx)

### Testing Tasks (US2)

- [x] [T069] [P1] [US2] Write unit tests for create_task service (backend/tests/test_task_service.py)
- [x] [T070] [P1] [US2] Write unit tests for get_user_tasks service (backend/tests/test_task_service.py)
- [x] [T071] [P1] [US2] Write unit tests for get_task_by_id with ownership validation (backend/tests/test_task_service.py)
- [x] [T072] [P1] [US2] Write API tests for POST /api/tasks with valid/invalid data (backend/tests/test_task_routes.py)
- [x] [T073] [P1] [US2] Write API tests for GET /api/tasks (backend/tests/test_task_routes.py)
- [x] [T074] [P1] [US2] Write API tests for GET /api/tasks/{task_id} with 403/404 cases (backend/tests/test_task_routes.py)
- [x] [T075] [P1] [US2] Write integration test for create and view task flow (backend/tests/test_integration.py)
- [x] [T076] [P1] [US2] Write integration test for user data isolation (backend/tests/test_integration.py)

---

## Phase 4: User Story 3 - Filter and Sort Tasks (US3, Priority: P2)

**Acceptance Scenarios**: 7 scenarios covering filtering by status/overdue and sorting by priority/due date/status
**Independent**: Can be implemented independently after Phase 1 setup
**Dependencies**: Requires task listing (T047, T050), US2 for testing data

### Backend Tasks (US3)

- [x] [T077] [P2] [US3] Extend get_user_tasks service with status filter parameter (backend/services/task_service.py)
- [x] [T078] [P2] [US3] Extend get_user_tasks service with overdue filter logic (backend/services/task_service.py)
- [x] [T079] [P2] [US3] Extend get_user_tasks service with sort_by parameter (backend/services/task_service.py)
- [x] [T080] [P2] [US3] Extend get_user_tasks service with order parameter (asc/desc) (backend/services/task_service.py)
- [x] [T081] [P2] [US3] Update GET /api/tasks with query params: status, sort_by, order (backend/routes/tasks.py)
- [x] [T082] [P2] [US3] Validate query parameters: status enum, sort_by enum, order enum (backend/routes/tasks.py)

### Frontend Tasks (US3)

- [x] [T083] [P2] [US3] Create filter button group: All, Pending, Completed, Overdue (frontend/components/TaskFilters.tsx)
- [x] [T084] [P2] [US3] Implement filter state management and API integration (frontend/app/tasks/page.tsx)
- [x] [T085] [P2] [US3] Create sort dropdown: By Priority, By Due Date, By Status (frontend/components/TaskSort.tsx)
- [x] [T086] [P2] [US3] Implement sort state management and API integration (frontend/app/tasks/page.tsx)
- [x] [T087] [P2] [US3] Display overdue indicator (red border/badge) for overdue tasks (frontend/components/TaskCard.tsx, frontend/components/TaskTable.tsx)
- [x] [T088] [P2] [US3] Add "Clear Filters" button to reset to default view (frontend/components/TaskFilters.tsx)
- [x] [T089] [P2] [US3] Display empty state message when no tasks match filter (frontend/app/tasks/page.tsx)

### Testing Tasks (US3)

- [x] [T090] [P2] [US3] Write unit tests for filtering by pending status (backend/tests/test_task_service.py)
- [x] [T091] [P2] [US3] Write unit tests for filtering by completed status (backend/tests/test_task_service.py)
- [x] [T092] [P2] [US3] Write unit tests for filtering by overdue (backend/tests/test_task_service.py)
- [x] [T093] [P2] [US3] Write unit tests for sorting by priority (backend/tests/test_task_service.py)
- [x] [T094] [P2] [US3] Write unit tests for sorting by due date (backend/tests/test_task_service.py)
- [x] [T095] [P2] [US3] Write unit tests for sorting by status (backend/tests/test_task_service.py)
- [x] [T096] [P2] [US3] Write API tests for GET /api/tasks with filter and sort params (backend/tests/test_task_routes.py)
- [x] [T097] [P2] [US3] Write integration test for filter and sort combinations (backend/tests/test_integration.py)

---

## Phase 5: User Story 4 - Update and Complete Tasks (US4, Priority: P2)

**Acceptance Scenarios**: 8 scenarios covering task editing, completion, validation, ownership checks
**Independent**: Can be implemented independently after Phase 1 setup
**Dependencies**: Requires task retrieval (T048, T051), US2 for testing data

### Backend Tasks (US4)

- [x] [T098] [P2] [US4] Implement update_task service with ownership validation (backend/services/task_service.py)
- [x] [T099] [P2] [US4] Implement complete_task service with idempotent status change (backend/services/task_service.py)
- [ ] [T100] [P2] [US4] Create PUT /api/tasks/{task_id} endpoint for task updates (backend/routes/tasks.py)
- [ ] [T101] [P2] [US4] Create PATCH /api/tasks/{task_id}/complete endpoint (backend/routes/tasks.py)
- [ ] [T102] [P2] [US4] Validate update payload: non-empty title, max lengths (backend/routes/tasks.py)
- [ ] [T103] [P2] [US4] Update updated_at timestamp automatically on task modification (backend/models/task.py)
- [ ] [T104] [P2] [US4] Return 403 Forbidden when updating another user's task (backend/routes/tasks.py)
- [ ] [T105] [P2] [US4] Return 404 Not Found when updating nonexistent task (backend/routes/tasks.py)

### Frontend Tasks (US4)

- [ ] [T106] [P2] [US4] Create task edit page with pre-filled form (frontend/app/tasks/[id]/edit/page.tsx)
- [ ] [T107] [P2] [US4] Implement task update form validation (frontend/app/tasks/[id]/edit/page.tsx)
- [ ] [T108] [P2] [US4] Handle task update submission and redirect to task list (frontend/app/tasks/[id]/edit/page.tsx)
- [ ] [T109] [P2] [US4] Display success message after task update (frontend/app/tasks/page.tsx)
- [ ] [T110] [P2] [US4] Add "Edit" button/icon to task card and table row (frontend/components/TaskCard.tsx, frontend/components/TaskTable.tsx)
- [ ] [T111] [P2] [US4] Add "Mark Complete" button to task card and table row (frontend/components/TaskCard.tsx, frontend/components/TaskTable.tsx)
- [ ] [T112] [P2] [US4] Implement mark complete action with optimistic UI update (frontend/app/tasks/page.tsx)
- [ ] [T113] [P2] [US4] Display visual distinction for completed tasks (strikethrough, green badge) (frontend/components/TaskCard.tsx, frontend/components/TaskTable.tsx)
- [ ] [T114] [P2] [US4] Handle 403 Forbidden errors with "Access denied" message (frontend/lib/api-client.ts)
- [ ] [T115] [P2] [US4] Handle 404 Not Found errors with "Task not found" message (frontend/lib/api-client.ts)

### Testing Tasks (US4)

- [ ] [T116] [P2] [US4] Write unit tests for update_task service with ownership validation (backend/tests/test_task_service.py)
- [ ] [T117] [P2] [US4] Write unit tests for complete_task service with idempotency (backend/tests/test_task_service.py)
- [ ] [T118] [P2] [US4] Write API tests for PUT /api/tasks/{task_id} with valid/invalid data (backend/tests/test_task_routes.py)
- [ ] [T119] [P2] [US4] Write API tests for PATCH /api/tasks/{task_id}/complete (backend/tests/test_task_routes.py)
- [ ] [T120] [P2] [US4] Write API tests for 403/404 error cases on update (backend/tests/test_task_routes.py)
- [ ] [T121] [P2] [US4] Write integration test for update task flow (backend/tests/test_integration.py)
- [ ] [T122] [P2] [US4] Write integration test for complete task flow (backend/tests/test_integration.py)

---

## Phase 6: User Story 5 - Delete Tasks (US5, Priority: P3)

**Acceptance Scenarios**: 6 scenarios covering task deletion with confirmation, persistence, ownership checks
**Independent**: Can be implemented independently after Phase 1 setup
**Dependencies**: Requires task retrieval (T048, T051), US2 for testing data

### Backend Tasks (US5)

- [ ] [T123] [P3] [US5] Implement delete_task service with ownership validation (backend/services/task_service.py)
- [ ] [T124] [P3] [US5] Create DELETE /api/tasks/{task_id} endpoint (backend/routes/tasks.py)
- [ ] [T125] [P3] [US5] Return 204 No Content on successful deletion (backend/routes/tasks.py)
- [ ] [T126] [P3] [US5] Return 403 Forbidden when deleting another user's task (backend/routes/tasks.py)
- [ ] [T127] [P3] [US5] Return 404 Not Found when deleting nonexistent task (backend/routes/tasks.py)

### Frontend Tasks (US5)

- [ ] [T128] [P3] [US5] Create confirmation dialog component (frontend/components/ConfirmDialog.tsx)
- [ ] [T129] [P3] [US5] Add "Delete" button/icon to task card and table row (frontend/components/TaskCard.tsx, frontend/components/TaskTable.tsx)
- [ ] [T130] [P3] [US5] Implement delete action with confirmation prompt (frontend/app/tasks/page.tsx)
- [ ] [T131] [P3] [US5] Handle delete cancellation (close dialog, no action) (frontend/app/tasks/page.tsx)
- [ ] [T132] [P3] [US5] Remove deleted task from UI immediately on success (frontend/app/tasks/page.tsx)
- [ ] [T133] [P3] [US5] Display success message after task deletion (frontend/app/tasks/page.tsx)
- [ ] [T134] [P3] [US5] Handle 403 Forbidden and 404 Not Found errors on delete (frontend/lib/api-client.ts)

### Testing Tasks (US5)

- [ ] [T135] [P3] [US5] Write unit tests for delete_task service with ownership validation (backend/tests/test_task_service.py)
- [ ] [T136] [P3] [US5] Write API tests for DELETE /api/tasks/{task_id} (backend/tests/test_task_routes.py)
- [ ] [T137] [P3] [US5] Write API tests for 403/404 error cases on delete (backend/tests/test_task_routes.py)
- [ ] [T138] [P3] [US5] Write integration test for delete task flow with confirmation (backend/tests/test_integration.py)

---

## Phase 7: Polish & Cross-Cutting Concerns

These tasks improve the overall application quality but don't belong to a single user story. Complete after all user stories are implemented.

### Error Handling & UX

- [ ] [T139] [P2] Create global error boundary for frontend (frontend/app/error.tsx)
- [ ] [T140] [P2] Implement toast notification system for success/error messages (frontend/components/Toast.tsx, frontend/lib/toast-context.tsx)
- [ ] [T141] [P2] Add loading states to all async operations (frontend/components/LoadingSpinner.tsx)
- [ ] [T142] [P2] Implement network error handling with retry options (frontend/lib/api-client.ts)
- [ ] [T143] [P2] Add form submission disabled state during API calls (frontend/components/ui/)

### Responsive Design & Accessibility

- [ ] [T144] [P2] Test responsive layout at 320px, 768px, 1920px, 2560px widths (frontend/app/tasks/page.tsx)
- [ ] [T145] [P2] Ensure all interactive elements have visible focus states (frontend/styles/globals.css)
- [ ] [T146] [P2] Add ARIA labels to buttons and form inputs (frontend/components/)
- [ ] [T147] [P2] Test keyboard navigation for all forms and buttons (manual testing)
- [ ] [T148] [P2] Ensure color contrast meets WCAG 2.1 Level A (manual testing)

### Performance & Optimization

- [ ] [T149] [P2] Add database query performance logging (backend/db.py)
- [ ] [T150] [P2] Verify indexes are used in all queries (backend/services/task_service.py)
- [ ] [T151] [P2] Implement pagination for task lists (>100 tasks) (backend/routes/tasks.py, frontend/app/tasks/page.tsx)
- [ ] [T152] [P3] Add API response caching headers (backend/main.py)
- [ ] [T153] [P3] Optimize frontend bundle size with code splitting (frontend/next.config.js)

### Security & Hardening

- [ ] [T154] [P1] Verify JWT_SECRET is not committed to git (add to .gitignore)
- [ ] [T155] [P1] Verify DATABASE_URL is not committed to git (add to .gitignore)
- [ ] [T156] [P1] Add rate limiting to API endpoints (backend/main.py)
- [ ] [T157] [P1] Sanitize user inputs to prevent XSS (backend/routes/tasks.py, frontend/components/)
- [ ] [T158] [P2] Add CSP headers to frontend (frontend/next.config.js)
- [ ] [T159] [P2] Add security headers (HSTS, X-Frame-Options) (backend/main.py)

### Documentation & Deployment

- [ ] [T160] [P1] Document environment variable setup in README files (backend/README.md, frontend/README.md)
- [ ] [T161] [P1] Create comprehensive API documentation with OpenAPI/Swagger (backend/main.py)
- [ ] [T162] [P2] Document database migration process (backend/README.md)
- [ ] [T163] [P2] Create deployment guide for backend (backend/DEPLOY.md)
- [ ] [T164] [P2] Create deployment guide for frontend (frontend/DEPLOY.md)
- [ ] [T165] [P3] Add architecture diagram to docs (specs/002-fullstack-web-app/architecture.png)

### Testing & Quality Assurance

- [ ] [T166] [P1] Run all backend tests and ensure 100% pass rate (backend/tests/)
- [ ] [T167] [P1] Verify test coverage for services >80% (backend/tests/)
- [ ] [T168] [P1] Run all acceptance test scenarios from quickstart.md (manual testing)
- [ ] [T169] [P2] Add E2E tests with Playwright for critical flows (frontend/e2e/)
- [ ] [T170] [P2] Run linters: ruff for backend, ESLint for frontend (backend/, frontend/)
- [ ] [T171] [P2] Run type checkers: mypy for backend, TypeScript check for frontend (backend/, frontend/)
- [ ] [T172] [P3] Add CI/CD pipeline configuration (.github/workflows/)

---

## Task Dependencies & Parallel Execution

### Dependency Graph

```
Phase 1 (Setup)
├── T001-T028 (All setup tasks must complete first)
│
├─ Phase 2 (US1 - Authentication)
│  └── T029-T045 (Depends on: T001-T024)
│
├─ Phase 3 (US2 - Create/View)
│  └── T046-T076 (Depends on: T001-T028, optionally T032-T039 for testing)
│
├─ Phase 4 (US3 - Filter/Sort)
│  └── T077-T097 (Depends on: T001-T028, T046-T056)
│
├─ Phase 5 (US4 - Update/Complete)
│  └── T098-T122 (Depends on: T001-T028, T046-T056)
│
├─ Phase 6 (US5 - Delete)
│  └── T123-T138 (Depends on: T001-T028, T046-T056)
│
└─ Phase 7 (Polish)
   └── T139-T172 (Depends on: All previous phases)
```

### Parallel Execution Examples

**After Phase 1 setup completes**, the following user stories can be developed **in parallel by separate developers**:

**Team A (Developer 1)**: US1 Authentication (T029-T045)
**Team B (Developer 2)**: US2 Create/View (T046-T076)
**Team C (Developer 3)**: US3 Filter/Sort (T077-T097)
**Team D (Developer 4)**: US4 Update/Complete (T098-T122)
**Team E (Developer 5)**: US5 Delete (T123-T138)

Each team works independently on their user story. No merge conflicts expected as each user story touches different service methods and UI components.

**Within a single user story**, backend and frontend tasks can be parallelized:

**US2 Example**:
- **Backend Developer**: T046-T055 (Services and routes)
- **Frontend Developer**: T056-T068 (UI components and pages)
- **QA Engineer**: T069-T076 (Tests - starts when backend/frontend tasks are complete)

---

## Validation Checklist

Before marking Phase 2 as complete, verify:

- [ ] All P1 tasks (Critical) are completed and tested
- [ ] All P2 tasks (Important) are completed and tested
- [ ] All 5 user stories pass their acceptance scenarios from quickstart.md
- [ ] All unit tests pass (backend/tests/)
- [ ] All integration tests pass (backend/tests/test_integration.py)
- [ ] User data isolation verified with multi-user testing
- [ ] Responsive design tested at mobile (320px), tablet (768px), and desktop (1920px) widths
- [ ] All error cases handled with clear user-facing messages
- [ ] Environment variables documented and .env.example files created
- [ ] README files complete with setup and running instructions
- [ ] Constitution compliance verified (all 18 requirements from plan.md)
- [ ] No security vulnerabilities (JWT secrets, XSS, user isolation)
- [ ] Performance goals met (task list <2s, filtering <500ms)

---

## Task Count Summary

- **Total Tasks**: 172
- **Phase 1 (Setup)**: 28 tasks
- **Phase 2 (US1 - Auth)**: 17 tasks
- **Phase 3 (US2 - Create/View)**: 31 tasks
- **Phase 4 (US3 - Filter/Sort)**: 21 tasks
- **Phase 5 (US4 - Update/Complete)**: 25 tasks
- **Phase 6 (US5 - Delete)**: 16 tasks
- **Phase 7 (Polish)**: 34 tasks

**Priority Breakdown**:
- **P1 (Critical)**: 91 tasks (53%)
- **P2 (Important)**: 69 tasks (40%)
- **P3 (Nice-to-have)**: 12 tasks (7%)

---

## Notes

1. **User Story Independence**: After Phase 1 setup, all 5 user stories (US1-US5) can be implemented in parallel by different developers. Each user story is self-contained with its own service methods, routes, and UI components.

2. **Testing Strategy**: Each user story includes unit tests (services), API tests (routes), and integration tests (end-to-end flows). Tests should be written alongside implementation (TDD encouraged).

3. **Incremental Delivery**: Complete user stories in priority order (P1 → P2 → P3) to deliver value incrementally. P1 user stories (US1, US2) form the Minimum Viable Product (MVP).

4. **Phase 7 Flexibility**: Polish tasks (T139-T172) can be completed alongside user story implementation or deferred to the end. Prioritize P1 polish tasks (security, error handling) early.

5. **Task Estimation**: Each task is designed to be completable in 1-4 hours by an experienced developer. Frontend and backend tasks within a user story are similar in scope for balanced workload distribution.

6. **Constitution Compliance**: All tasks align with Phase 2 Constitution v2.0.0 requirements. No tasks violate architectural constraints or technology mandates.
