---
id: 002
title: Phase 1 Spec Creation - Console Todo App
stage: spec
date: 2025-12-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: console-todo-app
branch: 001-console-todo-app
user: majid
command: /sp.specify
labels: ["spec", "phase1", "console-app", "crud", "in-memory"]
links:
  spec: specs/001-console-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-console-todo-app/spec.md
  - specs/001-console-todo-app/checklists/requirements.md
tests:
  - (spec stage - no tests yet)
---

## Prompt

User requested feature specification via `/sp.specify` command with comprehensive Phase 1 requirements:

```
PHASE 1 — SPECIFICATION
# Phase 1 — Console-Based Todo Application

## Overview
Build a fully functional in-memory Python console-based task manager that establishes the domain model,
business logic, and command structure for evolution into Phase 2 (web backend + frontend).

## Functional Requirements

### 1. Create Task
Users can create new tasks with:
- Title (required, 1-200 characters)
- Description (optional, up to 2000 characters)
- Due date (optional, ISO 8601 format YYYY-MM-DD)
- Priority (low/medium/high, defaults to medium)
- Status (pending/completed, defaults to pending)
- Auto-generated UUID and timestamps (created_at, updated_at)

### 2. List Tasks
Users can view tasks with:
- Filter by status (pending, completed, overdue)
- Filter by priority (low, medium, high)
- Sort by priority (high → medium → low)
- Sort by due_date (earliest first)
- Sort by status (pending first)
- Display: UUID (8 chars), title (50 chars), priority, status, due_date

### 3. Update Task
Users can modify any task field by UUID:
- Title, description, due_date, priority
- Auto-refresh updated_at timestamp
- Validate field values (title required, date format)
- Error if UUID not found

### 4. Complete Task
Users can mark tasks as complete:
- Change status from pending to completed
- Update updated_at timestamp
- Idempotent (no error if already completed)

### 5. Delete Task
Users can remove tasks:
- Prompt for confirmation (destructive action)
- Accept yes/y (case-insensitive) to confirm
- Accept no/n to cancel
- Permanent removal from memory

### 6. Console Menu
Interactive menu with options:
1. Add Task
2. List Tasks
3. Update Task
4. Complete Task
5. Delete Task
6. Exit

## Data Model
Task entity with 8 fields:
- id (UUID, auto-generated, immutable)
- title (string, required, 1-200 chars)
- description (string, optional, up to 2000 chars)
- due_date (ISO 8601 date YYYY-MM-DD, optional)
- priority (enum: low/medium/high, default medium)
- status (enum: pending/completed, default pending)
- created_at (ISO 8601 datetime, auto-set)
- updated_at (ISO 8601 datetime, auto-updated)

## Technical Requirements
- Python 3.13+ with UV package manager
- In-memory storage only (Python lists/dicts)
- No persistence (resets on restart)
- Layered architecture: commands/, domain/, services/, storage/, utils/
- Forward compatible with Phase 2 (FastAPI + database)

## UX Requirements
- Clear prompts and instructions
- Formatted table output
- Error messages for invalid inputs
- Confirmation on destructive actions
- Return to menu after operations
- Clean exit with "Goodbye!" message

## Acceptance Criteria
- 5 user stories with priorities (P1: Create/View, P2: Update/Complete, P3: Delete)
- Each story independently testable
- 30 functional requirements (FR-001 to FR-030)
- 12 success criteria with measurable outcomes
- 80% test coverage with pytest
- Type safety with mypy strict mode
- Zero ruff linting errors

## Edge Cases
- Past due dates (mark as overdue)
- Large datasets (500+ tasks, < 1s operations)
- Long input (10,000 chars, truncate display)
- Special characters and emojis (UTF-8 support)
- Quit during prompts (cancel and return to menu)
- Invalid menu options (error and re-prompt)

## Constraints
- Strictly in-memory (no files, JSON, databases)
- Console only (no GUI, no web)
- No external APIs or network calls
- Minimal dependencies (stdlib preferred)
- Deterministic behavior (repeatable tests)

## Out of Scope
- Persistence, FastAPI, Next.js frontend
- Authentication, multi-user, concurrency
- Database integration (Postgres, SQLite)
- AI chatbot, MCP agent features
- Cloud deployment, Docker, Kubernetes
- Advanced features (recurring tasks, subtasks, tags)

## Evolution Notes
Phase 2 migration path:
- Domain model → database schema (ORM)
- Service layer → FastAPI routes
- Storage layer → database repository
- Console UI → deprecated but runnable
```

## Response snapshot

Successfully created comprehensive Phase 1 specification for console-based todo application:

**Feature Branch**: `001-console-todo-app` (created and checked out)

**Specification Structure**:
1. **5 Prioritized User Stories**:
   - P1: Create and Manage Tasks (foundation MVP)
   - P1: View and Filter Tasks (completes MVP)
   - P2: Update Task Details (usability enhancement)
   - P2: Mark Tasks as Complete (progress tracking)
   - P3: Delete Tasks (quality of life)

2. **30 Functional Requirements** organized by category:
   - FR-001 to FR-005: Task Creation (title, fields, UUID, timestamps, defaults)
   - FR-006 to FR-013: Task Retrieval (list, filters, sorts, display format)
   - FR-014 to FR-017: Task Update (modify fields, validation, errors)
   - FR-018 to FR-020: Task Completion (status change, idempotency)
   - FR-021 to FR-025: Task Deletion (confirmation, permanent removal)
   - FR-026 to FR-030: Console Interface (menu, navigation, prompts, exit)

3. **12 Measurable Success Criteria**:
   - SC-001 to SC-005: User task times (30s create, 5s view, 45s update, 20s complete, 30s delete)
   - SC-006 to SC-012: Quality gates (error handling, formatting, independence, performance, reset, navigation)

4. **Quality Measures**:
   - 80% test coverage (pytest)
   - 100% type hint coverage (mypy strict)
   - Zero ruff linting errors
   - Console UX requirements
   - Layered architecture for Phase 2 compatibility

5. **Edge Cases**: 7 scenarios documented (past dates, large datasets, long input, special chars, quit flows, time changes, invalid options)

6. **Constraints**: Technical stack, no persistence, console only, minimal dependencies, deterministic behavior

7. **Out of Scope**: 10 items explicitly excluded (persistence, web, auth, DB, AI, cloud, networking, advanced features)

8. **Evolution Notes**: Phase 2 migration path for domain, services, storage, and console layers

**Quality Validation Checklist**: Created comprehensive checklist with 50 validation checks across 10 categories:
1. Completeness (7 checks) - ✅ PASS
2. Clarity & Testability (5 checks) - ✅ PASS
3. Independent User Stories (5 checks) - ✅ PASS
4. Priority Alignment (4 checks) - ✅ PASS
5. Constitutional Compliance (6 checks) - ✅ PASS
6. Error Handling & Edge Cases (5 checks) - ✅ PASS
7. Scope Discipline (4 checks) - ✅ PASS
8. Data Model Clarity (4 checks) - ✅ PASS
9. Console UX Specification (6 checks) - ✅ PASS
10. Acceptance & Deployment Readiness (5 checks) - ✅ PASS

**Checklist Result**: ✅ **APPROVED FOR PLANNING** (50/50 checks passed, 0 failures, 0 warnings)

## Outcome

- ✅ Impact: Comprehensive Phase 1 specification created with 5 independently testable user stories, 30 functional requirements, and 12 measurable success criteria. Specification fully aligned with constitution v1.0.0 (layered architecture, in-memory storage, forward compatibility).
- 🧪 Tests: (spec stage - no tests yet; 80% coverage target set for implementation)
- 📁 Files: Created 2 files (spec.md, checklists/requirements.md in specs/001-console-todo-app/)
- 🔁 Next prompts: Run `/sp.clarify` if clarifications needed (none identified), then `/sp.plan` for architecture design, `/sp.tasks` for task generation, `/sp.implement` for TDD execution
- 🧠 Reflection: Specification successfully breaks down Phase 1 into 5 priority-ordered user stories supporting incremental delivery. P1 stories (Create + View) form minimal viable product, P2 stories (Update + Complete) enhance usability, P3 story (Delete) improves long-term experience. Each story is independently testable and delivers standalone value. Constitutional compliance validated: mandatory folder structure referenced, in-memory storage enforced, task model matches 8 required fields, forward compatibility path to Phase 2 documented. Edge cases comprehensively covered (past dates, large datasets, long input, special chars, quit flows, invalid options). Quality checklist validates all 50 requirements passed.

## Evaluation notes (flywheel)

- Failure modes observed: Initial Write command failed with "File has not been read yet" error - resolved by reading initialized spec file before writing comprehensive content
- Graders run and results (PASS/FAIL): Quality checklist validation - 50/50 checks PASSED, 0 failures, 0 warnings. Specification APPROVED FOR PLANNING.
- Prompt variant (if applicable): v1 - User provided complete Phase 1 specification via `/sp.specify` command argument including 5 functional requirements sections, data model, technical requirements, UX requirements, acceptance criteria, edge cases, constraints, out-of-scope items, and evolution notes
- Next experiment (smallest change to try): Run `/sp.plan` to generate architecture design and implementation plan, validating constitution's layered architecture (commands, domain, services, storage, utils) and forward compatibility requirements
