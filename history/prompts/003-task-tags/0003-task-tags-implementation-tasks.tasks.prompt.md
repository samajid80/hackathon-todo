---
id: 0003
title: task-tags-implementation-tasks
stage: tasks
date: 2025-12-23
surface: CLI
model: claude-sonnet-4-5
feature: 003-task-tags
branch: 003-task-tags
user: majid
command: /sp.tasks
labels: [tasks, planning, test-driven, incremental-delivery]
links:
  spec: specs/003-task-tags/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/003-task-tags/tasks.md
    status: created
    lines: 450
tests:
  - path: backend/tests/test_task_service.py
    status: planned
    count: 8
  - path: backend/tests/test_task_routes.py
    status: planned
    count: 4
  - path: frontend/components/__tests__/TagSelector.test.tsx
    status: planned
    count: 5
  - path: frontend/tests/e2e/tags.spec.ts
    status: planned
    count: 7
---

## Prompt

**Skill**: /sp.tasks

**Context**: Generate implementation tasks from the plan for Feature 003-task-tags (Task Tags/Categories)

**Input Documents**:
- spec.md: Feature specification with 4 user stories (P1: Add Tags, P2: Filter by Tags, P3: View All Tags, P4: Chatbot Integration)
- plan.md: Implementation plan with tech stack (FastAPI, SQLModel, Next.js 16, PostgreSQL TEXT[] arrays)
- data-model.md: Database schema with tags column and GIN index
- contracts/openapi-tags.yaml: API contract for GET /api/tasks/tags and tag filtering
- research.md: Technical decisions (TEXT[] vs junction table, GIN indexing, Pydantic validation)
- quickstart.md: Manual test scenarios

**Expected Output**: tasks.md file with dependency-ordered implementation tasks organized by user story, following checklist format with [ID] [P?] [Story] labels

## Response snapshot

Generated tasks.md with 93 tasks organized into 7 phases:

**Phase 1: Setup** (3 tasks) - Project preparation
**Phase 2: Foundational** (6 tasks) - Database migration and type definitions (BLOCKS all user stories)
**Phase 3: User Story 1 - Add Tags to Tasks (P1)** (23 tasks) - MVP: Tag creation and editing
  - Tests first (T010-T015): 6 test tasks
  - Backend (T016-T021): Model validators, routes, services
  - Frontend (T022-T028): TagSelector component, TaskCard, TaskForm
  - Frontend tests (T029-T032): Component and E2E tests
**Phase 4: User Story 2 - Filter Tasks by Tags (P2)** (16 tasks) - Tag filtering with AND logic
  - Tests (T033-T036): 4 test tasks
  - Backend (T037-T040): Filter endpoint and service logic
  - Frontend (T041-T044): TaskFilters component
  - Tests (T045-T048): Component and E2E tests
**Phase 5: User Story 3 - View All Used Tags (P3)** (12 tasks) - Tag discovery and autocomplete
  - Tests (T049-T050): 2 test tasks
  - Backend (T051-T054): GET /api/tasks/tags endpoint
  - Frontend (T055-T058): useTags hook, TagSelector autocomplete
  - Tests (T059-T060): Hook and E2E tests
**Phase 6: User Story 4 - Chatbot Integration (P4)** (3 tasks) - Phase3 documentation only
**Phase 7: Polish** (30 tasks) - Documentation, performance, validation, deployment

**Key Design Decisions**:
- Test-driven development: Write tests FIRST (marked with ⚠️), ensure they FAIL before implementation
- Organized by user story for independent implementation and testing
- 47 tasks marked [P] for parallel execution (50% of total)
- MVP scope: 32 tasks (Setup + Foundational + User Story 1)
- Each user story has independent test criteria from quickstart.md

**Task Format**: `- [ ] [ID] [P?] [Story] Description with file path`
Example: `- [ ] T016 [US1] Add tags field to TaskBase model in backend/models/task.py`

## Outcome

- ✅ Impact: Generated 93 dependency-ordered tasks organized by 4 user stories, enabling incremental MVP delivery and parallel execution
- 🧪 Tests: 24 test tasks planned (TDD approach - tests written before implementation)
- 📁 Files: Created specs/003-task-tags/tasks.md (450 lines) with 7 phases, task dependencies, and parallel execution examples
- 🔁 Next prompts: Run `/sp.implement` to execute the implementation tasks, or `/sp.analyze` to validate consistency across artifacts
- 🧠 Reflection: Tasks organized by user story enable independent testing and incremental delivery. MVP (US1) is 32 tasks. Foundation phase (T004-T009) must complete before any user story work can begin.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All tasks follow checklist format, include file paths, organized by user story with independent test criteria
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
