---
id: 0001
title: Phase 2 Constitution Amendment
stage: constitution
date: 2025-12-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: majid
command: /sp.constitution
labels: ["constitution", "phase2", "architecture", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

```text
# Phase 2 Constitution — Todo Full-Stack Web Application
# Hackathon II — Spec Driven Development

## 1. Purpose
This constitution establishes the rules, constraints, architecture, and required behaviors for **Phase 2: Full-Stack Todo Web Application**.

Phase 2 transforms the in-memory console application from Phase 1 into a fully authenticated, full-stack web application consisting of:

- Next.js 16+ frontend
- Better-Auth for authentication
- FastAPI backend (REST API)
- Neon PostgreSQL database
- Shared domain model and consistent task behavior

All decisions, code generation, and architecture must adhere strictly to this constitution.

---

## 2. High-Level Goals

1. Implement a **production-ready full-stack Todo web application**.
2. Add **user authentication** using Better-Auth (Next.js) with JWT.
3. Add **persistent storage** using PostgreSQL hosted on Neon.
4. Replace Phase 1's in-memory structures with database-backed models.
5. Implement a fully functional **web UI** for CRUD operations.
6. Implement a complete **FastAPI REST API** powering the frontend.
7. Maintain architectural clarity for Phase 3 (Chatbot + MCP tools).
8. Ensure all data is **per-user** and securely isolated.

---

## 3. Scope (Functional Requirements)

### 3.1 Authentication (Next.js + Better-Auth)
- Sign up
- Login
- Logout
- Session management
- JWT issuance inside Next.js backend routes
- Persistent user storage in Postgres
- Provide JWT to FastAPI on every API call

### 3.2 Task Management (FastAPI + Postgres)
Tasks must support:
- Create
- Read (single + list)
- Update
- Delete
- Mark complete

All operations must be **user-scoped**, meaning:
- A user can see/update only their own tasks
- All task queries must filter by `user_id`

### 3.3 Frontend Requirements (Next.js 16)
- Task list page
- Create task form
- Edit task page
- Delete action
- Mark complete action
- Sorting: due_date, priority, status
- Filtering: pending, completed, overdue
- Responsive UI
- Error messages (client + server)
- Auth-protected routes

Frontend must call FastAPI through REST.

### 3.4 Backend Requirements (FastAPI)
The backend must provide the following routes under `/api/{user_id}/tasks`:

- `POST /tasks` → Create
- `GET /tasks` → List
- `GET /tasks/{task_id}` → Get one
- `PUT /tasks/{task_id}` → Update
- `PATCH /tasks/{task_id}/complete` → Mark complete
- `DELETE /tasks/{task_id}` → Delete

Authentication Handling:
- Accept JWT from Better-Auth via Authorization header
- Validate signature + expiry
- Extract `user_id`
- Reject if `user_id` in URL mismatches token

### 3.5 Database (Postgres)
A `tasks` table must exist with fields:

- id (UUID, PK)
- user_id (UUID, FK)
- title
- description
- due_date
- priority
- status
- created_at
- updated_at

`users` table created and managed by Better-Auth.

---

## 4. Non-Goals (Out of Scope for Phase 2)

❌ No console-based UI
❌ No in-memory storage
❌ No MCP server
❌ No agents
❌ No ChatKit integration
❌ No Docker/Kubernetes
❌ No Dapr/Kafka
❌ No streaming or websockets
❌ No mobile app

These are reserved for Phase 3–5.

---

## 5. Architectural Principles

### 5.1 Full-Stack Separation
Frontend and backend must be separate but cooperative services:

frontend/ → Next.js + Better-Auth
backend/ → FastAPI + database logic
database → Neon Postgres

### 5.2 Single Source of Truth
- PostgreSQL is the only data store.
- Better-Auth handles user storage.
- FastAPI handles task storage.
- No duplication of logic.

### 5.3 Stateless Backend
The FastAPI backend must:
- Use JWT for identity
- Store no session state
- Be horizontally scalable

### 5.4 Layered Backend Architecture
Backend code must be structured as:

backend/
main.py → FastAPI entrypoint
routes/ → controllers
models/ → Pydantic models + SQLModel/SQLAlchemy ORM entities
db.py → DB session + engine
services/ → business logic

### 5.5 Layered Frontend Architecture
Frontend architecture:

frontend/
app/
tasks/ → task pages
login/ → auth
signup/
api/ → fetch wrappers
lib/auth.ts → Better-Auth config
components/

### 5.6 Forward Compatibility
Phase 2 design must support:

- Phase 3: MCP tools calling FastAPI directly
- Phase 3: Chat endpoint consuming FastAPI's task API
- Phase 3: Agent execution interacting with tasks

Thus:
- API must be stable and REST-compliant
- Backend must be modular
- DB model must include indexing for query efficiency

---

## 6. Constraints

### 6.1 Technology Stack
- FastAPI (Python 3.13)
- PostgreSQL (Neon)
- Next.js 16 App Router
- Better-Auth for authentication
- JWT for backend authentication
- uv for Python environment
- node 24 for Next.js

### 6.2 Security Constraints
- JWT signature must be validated using shared secret.
- A user cannot access or modify another user's tasks.
- Sensitive information must never leak in logs.

### 6.3 Performance Constraints
- All task list queries must be indexed by user_id and due_date.
- API must respond within reasonable time for 1000+ tasks.

---

## 7. Quality Requirements

### 7.1 Code Quality
- Maintainability: modular, documented, consistent
- Testability: clear service boundaries
- Clear separation of concerns

### 7.2 Testing Requirements
Must include:
- Backend tests (CRUD, auth, DB)
- Frontend tests (API hooks, UI interactions)
- Integration tests (end-to-end API flows)

### 7.3 User Experience Requirements
Frontend must be:
- Clean
- Responsive
- Sleek And Professional looking
- Usable without confusion
- Error messages must be visible and understandable

---

## 8. Evolution Rules (Phase 3 Preparation)

Phase 2 must be built so it evolves cleanly into Phase 3:

1. REST API design must remain stable.
2. Task schema must remain forward-compatible.
3. Backend services must be extractable for MCP tools.
4. Authentication must remain unchanged (Better-Auth → JWT → FastAPI).
5. No logic should be placed in controllers; services must hold all logic.

---

## 9. Final Commitment
All development, refactoring, and enhancements for Phase 2 must strictly follow this constitution unless formally amended through SpecKit+ procedures.
```

## Response snapshot

**Constitution Update Complete: v1.0.0 → v2.0.0 (MAJOR)**

Successfully updated the project constitution for Phase 2 transition.

**Version Bump: MAJOR (1.0.0 → 2.0.0)**

Rationale: This represents a fundamental architectural shift from Phase 1 (console, in-memory) to Phase 2 (full-stack web application), introducing breaking changes:
- Removed console-only and in-memory constraints
- Added web frontend (Next.js), backend (FastAPI), and database (PostgreSQL)
- Introduced authentication and user isolation
- Changed project structure from phase1/src/ to backend/ and frontend/
- Replaced local-only with networked client-server architecture

**Key Changes:**
- Added 5 new sections covering authentication, frontend, backend, database, and security
- Removed 2 Phase 1-specific sections (in-memory storage, console UX)
- Updated architectural principles for full-stack separation
- Added security and performance constraints
- Updated forward compatibility to target Phase 3 (MCP/Chatbot)

**Files Modified:**
- `.specify/memory/constitution.md` - Updated with full Phase 2 requirements

**Template Status:**
- ✅ Templates reviewed and compatible with Phase 2 structure
- ⚠️  4 slash command files flagged for manual review (contain Phase 1 references)

**Follow-up Actions:**
- Review `.claude/commands/sp.{clarify,git.commit_pr,plan,tasks}.md` for Phase 1 references
- Consider archiving Phase 1 constitution as `constitution-v1.0.0-phase1.md`

## Outcome

- ✅ Impact: MAJOR constitutional amendment establishing Phase 2 governance (full-stack web architecture)
- 🧪 Tests: Not applicable (governance document)
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Review slash commands for Phase 1 references; begin Phase 2 feature specification
- 🧠 Reflection: Clean phase transition with comprehensive sync impact report; version bump properly justified; templates validated for compatibility

## Evaluation notes (flywheel)

- Failure modes observed: None - all placeholders filled, version incremented correctly, sync impact report complete
- Graders run and results (PASS/FAIL): PASS - Constitution follows semantic versioning, all sections complete, no unresolved placeholders
- Prompt variant (if applicable): Standard /sp.constitution workflow
- Next experiment (smallest change to try): User should proceed with Phase 2 feature specification using /sp.specify
