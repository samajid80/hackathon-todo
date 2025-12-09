---
id: 0001
title: Phase 1 Plan Generation - Console Todo App
stage: plan
date: 2025-12-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-console-todo-app
branch: 001-console-todo-app
user: majid
command: /sp.plan
labels: ["plan", "phase1", "console-app", "architecture", "design"]
links:
  spec: specs/001-console-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-console-todo-app/plan.md
  - specs/001-console-todo-app/research.md
  - specs/001-console-todo-app/data-model.md
  - specs/001-console-todo-app/quickstart.md
tests:
  - (plan stage - no tests yet)
---

## Prompt

User requested implementation plan generation via `/sp.plan` command with comprehensive Phase 1 implementation breakdown from user's hackathon requirements:

```
# Phase 1 Implementation Plan — Console-Based Todo Application
# Hackathon II — Spec Driven Development

## 1. Objective
Implement a fully functional, in-memory Python console-based Todo application that follows:
- Phase 1 Constitution
- Phase 1 Specifications
- In-memory only state (no persistence)
- Console-only user interface
- Modular architecture ready for Phase 2 expansion

## 2. Work Breakdown Structure (WBS)

### 2.1 Project Initialization
- Create folder structure (src/main.py, commands/, domain/, services/, storage/, utils/)
- Initialize UV project
- Document initial structure in README

### 2.2 Domain Layer Implementation (Models)
- Create domain/task.py with Task dataclass
- Define 8 properties (id, title, description, due_date, priority, status, created_at, updated_at)
- Implement validation rules (title non-empty, priority/status enums, ISO date validation)
- Create enum classes for Priority and Status

### 2.3 Storage Layer Implementation (In-Memory)
- Create storage/repository.py with InMemoryTaskRepository
- Implement methods: add, get, update, delete, list_all
- Ensure no persistence, clean error handling

### 2.4 Service Layer Implementation (Business Logic)
- Create services/task_service.py
- Implement operations: create_task, list_tasks (with filter/sort), update_task, complete_task, delete_task
- Apply validation rules and business logic

### 2.5 Command Layer Implementation (CLI Actions)
- Create commands/ folder with files: add_task.py, list_tasks.py, update_task.py, complete_task.py, delete_task.py
- Each command prompts for input, validates, calls service layer, shows results

### 2.6 Console Menu (main.py)
- Implement menu with 6 options (Add/List/Update/Complete/Delete/Exit)
- Input validation, routing to command handlers
- Graceful error handling

### 2.7 Sorting & Filtering Logic
- Filtering: pending, completed, overdue
- Sorting: due_date, priority, status
- Integrate into service layer

### 2.8 Error Handling Layer
- Wrap user input parsing
- Validate IDs (UUID format)
- Catch invalid dates
- User-friendly errors

### 2.9 Testing Strategy
- Domain tests (Task creation, validation)
- Storage tests (add/update/delete, not found errors)
- Service tests (filtering, sorting, error cases)
- Command-level tests (integration, simulated I/O)

### 2.10 Documentation
- Update README with instructions
- Add usage examples
- Architecture overview
- Phase 2 migration path

## 3. Milestones
M1: Architecture Setup → M2: Domain+Storage → M3: Service Layer → M4: Commands+Menu → M5: Sorting/Filtering → M6: Testing → M7: Documentation

## 4. Phase 1 Completion Criteria
- All features from spec implemented
- Application runs fully in console
- In-memory storage only
- No crashes on bad input
- Tests pass successfully
- Documentation complete
- Architecture ready for Phase 2

## 5. Evolution Path (Forward Planning)
Phase 1 → Phase 2:
- Replace InMemoryTaskRepository with Postgres-based repository
- Convert service layer to FastAPI routes
- Keep domain model with minor upgrades (Pydantic/SQLModel)
- Console UI becomes optional module
```

## Response snapshot

Successfully generated comprehensive Phase 1 implementation plan with constitutional compliance verification and complete design artifacts:

**Plan Document** (`plan.md`):
- **Summary**: Layered architecture (domain, services, storage, commands, utils) with in-memory storage and forward compatibility for Phase 2 (FastAPI + database)
- **Technical Context**: Python 3.13, stdlib dependencies, pytest/ruff/mypy for quality, dict-based in-memory storage, < 1s performance for 500 tasks
- **Constitution Check**: ✅ **ALL GATES PASSED** (12/12 principle categories):
  - Mandatory folder structure (commands, domain, services, storage, utils) ✅
  - Separation of concerns (domain isolated, services pure, storage in-memory, UI separate) ✅
  - In-memory storage rules (Python dict, no persistence, Phase 2 swappable) ✅
  - Forward compatibility (services → FastAPI routes, domain → ORM, storage → database) ✅
  - Deterministic behavior (repeatable tests, 80% coverage) ✅
  - Language & tools (Python 3.13, UV, minimal dependencies) ✅
  - Input & error handling (validation, clear messages, re-prompting) ✅
  - Code quality (modular, type hints, docstrings) ✅
  - Tests (unit tests for domain/services/storage, integration for commands) ✅
  - Console UX (clear instructions, confirmations, formatting) ✅
  - Evolution rules (repository pattern, service purity) ✅
- **Project Structure**: Source code in `phase1/src/`, tests mirror structure, documentation in `specs/001-console-todo-app/`
- **Complexity Tracking**: No violations identified
- **Risks & Mitigations**: 5 risks documented (in-memory limitations, console UX, type checking, test coverage, forward compatibility assumptions)

**Research Document** (`research.md`):
8 technical decisions resolved:
1. **Task Model**: Python `dataclass` with manual validation (simple, type-safe, forward-compatible)
2. **Storage**: `dict[str, Task]` with UUID keys (O(1) lookup, database-compatible interface)
3. **Enums**: `enum.Enum` for Priority and Status (type-safe, auto-validation)
4. **Date Handling**: ISO 8601 string with `fromisoformat()` validation (spec compliance, simple sorting)
5. **Console Formatting**: Manual f-strings (no dependencies, sufficient for Phase 1)
6. **Error Handling**: Service returns `(bool, str, Optional[Task])` tuples (separation of concerns)
7. **Testing**: pytest with fixtures + monkeypatch (clean isolation, input/output mocking)
8. **Type Checking**: mypy strict mode (constitutional requirement, maximum safety)

**Data Model Document** (`data-model.md`):
- **Task Entity**: 8 fields with full validation rules and implementation code
- **Priority Enum**: LOW, MEDIUM, HIGH with sorting logic
- **Status Enum**: PENDING, COMPLETED with state transitions
- **Custom Exceptions**: ValidationError, TaskNotFoundError
- **Derived Properties**: is_overdue (computed, not stored)
- **Filtering/Sorting Criteria**: By status, priority, overdue; sort by priority, due_date, status
- **Phase 2 Migration**: Clear path to SQLAlchemy/Pydantic with code examples

**Quickstart Guide** (`quickstart.md`):
- 30+ manual test scenarios covering all 5 user stories
- Test Case 1.1-1.4: Create tasks (valid, all fields, empty title error, invalid date error)
- Test Case 2.1-2.5: View/filter tasks (pending only, sort by priority/due_date, no tasks found, display all)
- Test Case 3.1-3.5: Update tasks (title, priority, due_date, description, invalid UUID)
- Test Case 4.1-4.5: Complete tasks (pending → completed, filter verification, idempotency)
- Test Case 5.1-5.4: Delete tasks (confirmation, cancel, not found verification)
- Edge Cases: past due dates, 500+ tasks, long input, special chars, quit during prompts, invalid menu options
- Performance Tests: create < 30s, view < 5s
- Exit/Restart Test: in-memory reset verification

**Agent Context Update**: CLAUDE.md updated with Python 3.13, stdlib dependencies, in-memory storage details

## Outcome

- ✅ Impact: Comprehensive Phase 1 implementation plan with architecture design, technical decisions, data model, and test scenarios. Constitutional compliance validated (12/12 gates passed). Layered architecture supports Phase 2 migration (FastAPI + database).
- 🧪 Tests: (plan stage - no tests yet; testing strategy documented in plan with 80% coverage target, pytest fixtures, mypy strict mode)
- 📁 Files: Created 4 files (plan.md, research.md, data-model.md, quickstart.md in specs/001-console-todo-app/)
- 🔁 Next prompts: Run `/sp.tasks` to generate dependency-ordered task list, then `/sp.implement` for TDD execution, `/sp.analyze` for consistency check
- 🧠 Reflection: Plan successfully established layered architecture (domain, services, storage, commands, utils) matching constitutional mandatory folder structure. All technical unknowns resolved through research phase (8 decisions: dataclass vs Pydantic, dict vs list storage, enum implementation, ISO date handling, f-string formatting, tuple error returns, pytest fixtures, mypy strict). Constitution Check passed all 12 categories without violations. Data model defines Task entity (8 fields), Priority/Status enums, validation rules, and Phase 2 migration path (SQLAlchemy/Pydantic). Quickstart guide provides 30+ manual test scenarios aligned with 5 user stories. Forward compatibility ensured via repository pattern (storage interface swappable), service purity (no console dependencies), domain model mapping (dataclass → ORM). Agent context updated with project-specific technology stack.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generation completed without errors. Script `create-phr.sh` initially failed due to incorrect feature name format (`console-todo-app` vs `001-console-todo-app`), resolved by using numbered feature directory name.
- Graders run and results (PASS/FAIL): Constitution Check - 12/12 categories PASSED (mandatory folder structure, separation of concerns, in-memory storage rules, forward compatibility, deterministic behavior, language & tools, error handling, code quality, tests, console UX, evolution rules). Quality validation - all design artifacts aligned with spec requirements.
- Prompt variant (if applicable): v1 - User provided complete implementation plan via `/sp.plan` command argument including WBS (2.1-2.10), milestones (M1-M7), completion criteria, and evolution path
- Next experiment (smallest change to try): Run `/sp.tasks` to generate dependency-ordered task list from plan, validating task categorization (Domain → Storage → Service → Utils → Commands → Menu → Tests → QA → Docs) and TDD workflow integration
