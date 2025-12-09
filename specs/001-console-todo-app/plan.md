# Implementation Plan: Phase 1 Console-Based Todo Application

**Branch**: `001-console-todo-app` | **Date**: 2025-12-09 | **Spec**: specs/001-console-todo-app/spec.md
**Input**: Feature specification from `/specs/001-console-todo-app/spec.md`

**Note**: This plan follows the Hackathon II Spec-Driven Development process with constitutional compliance verification.

## Summary

Build a fully functional in-memory Python console-based task manager implementing 5 prioritized user stories (Create Tasks, View/Filter Tasks, Update Tasks, Complete Tasks, Delete Tasks). The application uses layered architecture (domain, services, storage, commands, utils) with strict in-memory storage (no persistence) and forward compatibility for Phase 2 migration to FastAPI + database. All CRUD operations, filtering (status, priority, overdue), and sorting (priority, due_date, status) will be implemented with comprehensive error handling and 80% test coverage.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: Python standard library (uuid, datetime, enum); pytest, ruff, mypy for testing/quality only
**Storage**: In-memory only (Python dict mapping UUID → Task object)
**Testing**: pytest with pytest-cov for coverage (80% minimum target)
**Target Platform**: Linux/WSL2 console (also compatible with macOS, Windows)
**Project Type**: Single console application with layered architecture
**Performance Goals**: < 1 second for list operations with up to 500 tasks; < 5 seconds for filtered views with 100 tasks
**Constraints**: No persistence (resets on restart), no external APIs, console-only interface, deterministic behavior
**Scale/Scope**: Single-user, in-memory storage, 5 user stories, 30 functional requirements, layered architecture ready for Phase 2 expansion

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Mandatory Folder Structure (Constitution §5.1)
- ✅ **PASS**: Plan specifies `phase1/src/{main.py, commands/, domain/, services/, storage/, utils/}` structure
- ✅ **PASS**: Test directory `phase1/tests/` mirrors source structure
- ✅ **PASS**: Project root includes `pyproject.toml`, `.python-version`, `README.md`

### Separation of Concerns (Constitution §5.2)
- ✅ **PASS**: Domain layer isolated (Task model, enums, validation only)
- ✅ **PASS**: Service layer centralized (all CRUD business logic, no console dependencies)
- ✅ **PASS**: Storage layer pure in-memory (dict-based repository, no I/O)
- ✅ **PASS**: Console/UI layer separate (command handlers only interact with service layer)

### In-Memory Storage Rules (Constitution §5.3)
- ✅ **PASS**: Storage uses Python dict (`tasks: dict[str, Task]`) in RAM only
- ✅ **PASS**: No persistence logic (no file I/O, no JSON, no databases)
- ✅ **PASS**: Data resets on program restart per requirement
- ✅ **PASS**: Storage interface designed for Phase 2 database swap (repository pattern)

### Forward Compatibility (Constitution §5.4)
- ✅ **PASS**: Service layer operations map to future FastAPI routes (create_task → POST /tasks)
- ✅ **PASS**: Domain model (Task dataclass) maps to Phase 2 ORM model (add SQLAlchemy decorators)
- ✅ **PASS**: Storage layer uses repository interface (swap InMemoryTaskRepository → DatabaseRepository)
- ✅ **PASS**: Console UI isolated in commands/ (can be deprecated without breaking services/domain)

### Deterministic Behavior (Constitution §5.5)
- ✅ **PASS**: All operations repeatable (UUID generation is only non-deterministic part, acceptable)
- ✅ **PASS**: Test coverage target 80% ensures predictable behavior
- ✅ **PASS**: No random behavior, no external API calls, no time-based logic beyond timestamps

### Language & Tools (Constitution §6.1)
- ✅ **PASS**: Python 3.13 specified
- ✅ **PASS**: UV package manager configured in `phase1/pyproject.toml`
- ✅ **PASS**: Minimal dependencies (stdlib only for core; pytest, ruff, mypy for quality)
- ✅ **PASS**: Pydantic not required (using dataclass with manual validation)

### Input & Error Handling (Constitution §6.2)
- ✅ **PASS**: Crash prevention via try/except in all command handlers
- ✅ **PASS**: Input validation at domain layer (title required, date format, priority/status enums)
- ✅ **PASS**: Clear error messages specified (FR-006: "Title is required", "Task not found", etc.)
- ✅ **PASS**: Re-prompting on invalid input per UX requirements
- ✅ **PASS**: No ambiguous console instructions (numbered menu, clear prompts)

### Code Quality (Constitution §7.1)
- ✅ **PASS**: Modular design (layered architecture)
- ✅ **PASS**: Type hints mandatory (mypy strict mode enforcement)
- ✅ **PASS**: Docstrings for public APIs (Google style)
- ✅ **PASS**: Consistent naming (snake_case functions, PascalCase classes)
- ✅ **PASS**: No repeated logic (DRY principle via service layer)

### Tests (Constitution §7.2)
- ✅ **PASS**: Unit tests for domain model validation planned
- ✅ **PASS**: Unit tests for service-layer operations planned
- ✅ **PASS**: Storage tests for in-memory behaviors planned
- ✅ **PASS**: Integration tests for command handling planned
- ✅ **PASS**: 80% coverage target set (pytest-cov)

### Console UX (Constitution §7.3)
- ✅ **PASS**: Clear instructions (FR-026: numbered menu, FR-028: prompts)
- ✅ **PASS**: Helpful messages (FR-006: error messages, confirmation messages)
- ✅ **PASS**: Confirmation on destructive actions (FR-021: delete confirmation)
- ✅ **PASS**: Neat formatting (FR-013: table format with columns, truncation rules)
- ✅ **PASS**: Logical menu flow (FR-029: return to menu after operations)

### Evolution Rules (Constitution §8)
- ✅ **PASS**: Storage layer replaceable (repository interface design)
- ✅ **PASS**: Console UI deprecation plan (commands/ isolated from services/)
- ✅ **PASS**: Domain model compatibility (Task → ORM model mapping documented)
- ✅ **PASS**: Service layer to FastAPI routes (operations designed as pure functions)
- ✅ **PASS**: No breaking changes without constitutional amendment

**Constitution Check Result**: ✅ **ALL GATES PASSED** (12/12 principle categories compliant)

## Project Structure

### Documentation (this feature)

```text
specs/001-console-todo-app/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (N/A for console app - no API contracts)
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec validation checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phase1/
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entrypoint: console menu loop
│   ├── commands/                # Command handlers (console UI layer)
│   │   ├── __init__.py
│   │   ├── add_task.py          # User Story 1: Create task command
│   │   ├── list_tasks.py        # User Story 2: View/filter tasks command
│   │   ├── update_task.py       # User Story 3: Update task command
│   │   ├── complete_task.py     # User Story 4: Complete task command
│   │   └── delete_task.py       # User Story 5: Delete task command
│   ├── domain/                  # Domain models and validation
│   │   ├── __init__.py
│   │   ├── task.py              # Task dataclass with validation
│   │   ├── enums.py             # Priority and Status enums
│   │   └── exceptions.py        # Domain exceptions (ValidationError, etc.)
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   └── task_service.py      # CRUD operations, filtering, sorting
│   ├── storage/                 # Data persistence layer (in-memory)
│   │   ├── __init__.py
│   │   └── repository.py        # InMemoryTaskRepository
│   └── utils/                   # Helper functions
│       ├── __init__.py
│       ├── datetime_utils.py    # ISO 8601 formatting, date validation
│       └── display_utils.py     # Table formatting, truncation
├── tests/
│   ├── __init__.py
│   ├── test_domain/             # Domain layer tests
│   │   ├── __init__.py
│   │   ├── test_task.py         # Task model validation tests
│   │   └── test_enums.py        # Enum validation tests
│   ├── test_services/           # Service layer tests
│   │   ├── __init__.py
│   │   └── test_task_service.py # CRUD, filtering, sorting tests
│   ├── test_storage/            # Storage layer tests
│   │   ├── __init__.py
│   │   └── test_repository.py   # In-memory repository tests
│   ├── test_commands/           # Command layer tests (integration)
│   │   ├── __init__.py
│   │   ├── test_add_task.py
│   │   ├── test_list_tasks.py
│   │   ├── test_update_task.py
│   │   ├── test_complete_task.py
│   │   └── test_delete_task.py
│   └── conftest.py              # Pytest fixtures (mock repository, sample tasks)
├── pyproject.toml               # UV project configuration
├── .python-version              # Python 3.13
└── README.md                    # Setup and usage instructions
```

**Structure Decision**: Single console application with layered architecture. The `phase1/src/` directory follows constitutional mandatory folder structure (commands, domain, services, storage, utils). Test directory mirrors source structure for clarity. This design supports Phase 2 migration: domain → ORM models, services → FastAPI routes, storage → database repository, commands → deprecated.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations identified.** All constitutional principles (12 categories) are satisfied by the planned architecture.

---

## Phase 0: Research & Technical Decisions

**Goal**: Resolve technical unknowns and establish implementation patterns.

### Research Areas

No major unknowns identified. All technical decisions are straightforward for Phase 1:

1. **Task Model Implementation**
   - **Decision**: Python `dataclass` with manual validation
   - **Rationale**: Simpler than Pydantic for in-memory use case, provides type hints and default values, easily migrates to SQLAlchemy/Pydantic in Phase 2
   - **Alternatives Considered**: Pydantic (overkill for Phase 1, adds dependency), plain class (loses type safety and defaults)

2. **Storage Implementation**
   - **Decision**: `dict[str, Task]` with UUID string keys
   - **Rationale**: O(1) lookup by ID, natural mapping to database primary key, easy to iterate for filtering/sorting
   - **Alternatives Considered**: List (requires O(n) lookup), SQLite in-memory (violates constitution's "no databases" rule for Phase 1)

3. **Enum Implementation**
   - **Decision**: Python `enum.Enum` for Priority and Status
   - **Rationale**: Type-safe, auto-validation, compatible with database enums in Phase 2
   - **Alternatives Considered**: String literals (no type safety), constants (no validation)

4. **Date Handling**
   - **Decision**: Store as ISO 8601 string, validate with `datetime.fromisoformat()`
   - **Rationale**: Matches spec requirement (FR-002), simple string comparison for sorting, database-compatible
   - **Alternatives Considered**: datetime objects (requires timezone handling complexity), Unix timestamps (not human-readable)

5. **Console Formatting**
   - **Decision**: Manual string formatting with f-strings and `str.format()`
   - **Rationale**: No external dependencies, sufficient for table display, clear implementation
   - **Alternatives Considered**: Rich library (adds dependency, overkill for Phase 1), PrettyTable (adds dependency)

6. **Error Handling Strategy**
   - **Decision**: Custom domain exceptions, service layer catches and returns error tuples `(success: bool, message: str, data: Optional[Task])`
   - **Rationale**: Clean separation of concerns, command layer formats errors for console, services remain UI-agnostic
   - **Alternatives Considered**: Raising exceptions to command layer (mixes concerns), error codes (not Pythonic)

7. **Testing Strategy**
   - **Decision**: pytest with fixtures for mock repository and sample tasks
   - **Rationale**: Pytest is industry standard, fixtures enable clean test isolation, parametrize supports edge cases
   - **Alternatives Considered**: unittest (more verbose), doctest (insufficient for complex scenarios)

8. **Type Checking**
   - **Decision**: mypy in strict mode with 100% type hint coverage
   - **Rationale**: Constitutional requirement (§7.1), catches errors early, documents interfaces
   - **Alternatives Considered**: Type hints without enforcement (defeats purpose), pyright (adds tool complexity)

### Research Output

All technical decisions resolved. No blocking unknowns remaining. See `research.md` for detailed decision documentation.

---

## Phase 1: Design Artifacts

**Goal**: Generate data model, API contracts (N/A for console), and quickstart guide.

### Data Model

See `data-model.md` for complete entity definitions. Summary:

- **Task Entity**: 8 fields (id, title, description, due_date, priority, status, created_at, updated_at)
- **Priority Enum**: LOW, MEDIUM, HIGH
- **Status Enum**: PENDING, COMPLETED
- **Validation Rules**: Title 1-200 chars, description 0-2000 chars, due_date ISO 8601 format, priority/status enum values

### API Contracts

**N/A for Phase 1** - Console application has no external API. Phase 2 will generate OpenAPI spec when migrating to FastAPI.

### Quickstart Guide

See `quickstart.md` for complete test scenarios. Summary:

- **Scenario 1**: Create task, verify UUID and defaults
- **Scenario 2**: List tasks, apply filters (pending, completed, overdue)
- **Scenario 3**: Update task fields, verify timestamp refresh
- **Scenario 4**: Complete task, verify status change
- **Scenario 5**: Delete task with confirmation, verify removal

---

## Phase 2: Implementation Tasks (Generated by `/sp.tasks`)

**Note**: Task generation is handled by `/sp.tasks` command, not `/sp.plan`. This section provides high-level task categories for planning purposes.

### Task Categories

1. **Project Initialization**
   - Create folder structure (src/, tests/, subdirectories)
   - Configure UV project (pyproject.toml with dependencies)
   - Initialize README.md with setup instructions

2. **Domain Layer**
   - Implement Task dataclass with validation
   - Implement Priority and Status enums
   - Implement custom domain exceptions
   - Write unit tests for Task model and enums

3. **Storage Layer**
   - Implement InMemoryTaskRepository with dict storage
   - Implement CRUD methods (add, get, update, delete, list_all)
   - Write unit tests for repository operations
   - Write tests for "Task not found" error cases

4. **Service Layer**
   - Implement TaskService with business logic
   - Implement create_task with validation and defaults
   - Implement list_tasks with filtering (status, priority, overdue)
   - Implement list_tasks with sorting (priority, due_date, status)
   - Implement update_task with field validation
   - Implement complete_task with idempotency
   - Implement delete_task with confirmation flow
   - Write unit tests for all service operations
   - Write tests for filtering and sorting edge cases

5. **Utils Layer**
   - Implement datetime_utils (ISO 8601 parsing, formatting, validation)
   - Implement display_utils (table formatting, text truncation)
   - Write unit tests for utility functions

6. **Command Layer**
   - Implement add_task command (prompts, validation, service call)
   - Implement list_tasks command (filter/sort prompts, display)
   - Implement update_task command (UUID prompt, field selection, update)
   - Implement complete_task command (UUID prompt, confirmation)
   - Implement delete_task command (UUID prompt, yes/no confirmation)
   - Write integration tests for each command (simulated input/output)

7. **Console Menu**
   - Implement main.py with menu loop
   - Implement menu display (numbered options 1-6)
   - Implement input routing to command handlers
   - Implement error handling for invalid menu options
   - Implement graceful exit on "Exit" option
   - Write integration tests for menu navigation

8. **Quality Assurance**
   - Run ruff linting and formatting (zero errors)
   - Run mypy type checking (zero errors, 100% coverage)
   - Run pytest with coverage report (80% minimum)
   - Manual testing of all user stories
   - Edge case testing (long input, special chars, past dates, etc.)

9. **Documentation**
   - Complete README.md with installation and usage
   - Add architecture overview diagram to README
   - Document Phase 2 migration path
   - Add code comments for complex logic
   - Generate API documentation (if using sphinx)

### Dependency Order

1. Domain layer (no dependencies)
2. Storage layer (depends on domain)
3. Service layer (depends on storage, domain)
4. Utils layer (no dependencies)
5. Command layer (depends on services, utils)
6. Console menu (depends on commands)
7. Tests (parallel to implementation, layer by layer)
8. QA and documentation (after implementation complete)

---

## Phase 2 Migration Path

**Note**: This section documents forward compatibility planning for Phase 2 (FastAPI + Database).

### Storage Layer Migration

**Current (Phase 1)**:
```python
class InMemoryTaskRepository:
    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def add(self, task: Task) -> None:
        self.tasks[task.id] = task
```

**Future (Phase 2)**:
```python
class DatabaseTaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, task: Task) -> None:
        db_task = TaskModel(**task.__dict__)  # ORM model
        self.session.add(db_task)
        self.session.commit()
```

**Migration Strategy**: Repository interface remains identical. Swap `InMemoryTaskRepository` for `DatabaseTaskRepository` via dependency injection in service layer.

### Service Layer Migration

**Current (Phase 1)**:
```python
class TaskService:
    def __init__(self, repository: InMemoryTaskRepository):
        self.repository = repository

    def create_task(self, title: str, description: str = "", ...) -> tuple[bool, str, Optional[Task]]:
        task = Task(title=title, description=description, ...)
        self.repository.add(task)
        return (True, "Task created", task)
```

**Future (Phase 2)**:
```python
@app.post("/tasks")
def create_task_endpoint(request: TaskCreateRequest, service: TaskService = Depends()):
    success, message, task = service.create_task(
        title=request.title,
        description=request.description,
        ...
    )
    if success:
        return {"task": task.dict(), "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)
```

**Migration Strategy**: Service layer methods map 1:1 to FastAPI route handlers. Business logic unchanged, only wrapper changes from command handler to HTTP endpoint.

### Domain Layer Migration

**Current (Phase 1)**:
```python
@dataclass
class Task:
    id: str
    title: str
    description: str
    due_date: Optional[str]
    priority: Priority
    status: Status
    created_at: str
    updated_at: str
```

**Future (Phase 2 Option A - Pydantic)**:
```python
class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    due_date: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
```

**Future (Phase 2 Option B - SQLAlchemy)**:
```python
class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), default="")
    due_date = Column(String, nullable=True)  # Or Date type
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    status = Column(Enum(Status), default=Status.PENDING)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, onupdate=lambda: datetime.now().isoformat())
```

**Migration Strategy**: Domain model fields remain identical. Add Pydantic validation decorators or SQLAlchemy ORM decorators. Business logic in services/ references the domain model without changes.

### Console UI Deprecation

**Current (Phase 1)**:
```python
# main.py
def main():
    while True:
        print_menu()
        choice = input("Select option: ")
        if choice == "1":
            add_task_command()
        # ... other menu options
```

**Future (Phase 2)**:
```python
# main.py (kept for backward compatibility)
def main():
    print("Console UI is deprecated. Use API at http://localhost:8000")
    print("Continue with console UI? (yes/no)")
    if input().lower() == "yes":
        # ... existing menu code
```

**Migration Strategy**: Console UI moved to `deprecated/` folder. Optionally kept runnable for local testing. All new features use FastAPI endpoints only.

---

## Risks & Mitigations

### Risk 1: In-Memory Storage Limitations
- **Description**: Users lose all tasks on program restart, may frustrate testing
- **Probability**: High (by design)
- **Impact**: Medium (acceptable for Phase 1 demo, unacceptable for production)
- **Mitigation**: Clearly document in README that Phase 1 is in-memory only. Provide sample tasks via script for demo. Plan Phase 2 migration to database persistence.

### Risk 2: Console UX Complexity
- **Description**: Table formatting, text truncation, menu navigation may be harder than expected
- **Probability**: Low (well-defined requirements)
- **Impact**: Low (can iterate on formatting)
- **Mitigation**: Implement display_utils early with unit tests. Use fixtures for edge cases (long titles, emojis, special chars).

### Risk 3: Type Checking Overhead
- **Description**: mypy strict mode may flag false positives, slow iteration
- **Probability**: Medium (strict mode is strict)
- **Impact**: Low (improves code quality)
- **Mitigation**: Use `# type: ignore` sparingly with justification comments. Configure mypy.ini with project-specific settings if needed.

### Risk 4: Test Coverage Target
- **Description**: 80% coverage may be difficult to achieve for command layer (input/output mocking)
- **Probability**: Medium (integration tests are harder)
- **Impact**: Medium (constitutional requirement)
- **Mitigation**: Use pytest fixtures for mocking input/output. Use `monkeypatch` for stdin/stdout. Focus on happy path + error cases per user story.

### Risk 5: Forward Compatibility Assumptions
- **Description**: Phase 2 requirements may differ from assumptions (e.g., different database, API structure)
- **Probability**: Low (hackathon phases are well-defined)
- **Impact**: Medium (may require refactoring)
- **Mitigation**: Follow repository pattern strictly. Keep service layer pure (no console dependencies). Document Phase 2 migration assumptions in ADR if significant architectural decision needed.

---

## Open Questions

**None at this stage.** All technical decisions resolved through research phase. If questions arise during implementation, use `/sp.clarify` command to update specification.

---

## Next Steps

1. ✅ **Plan Complete**: This document
2. ⏭️ **Generate Tasks**: Run `/sp.tasks` to create dependency-ordered task list
3. ⏭️ **Implement**: Run `/sp.implement` to execute TDD cycle
4. ⏭️ **Review**: Run `/sp.analyze` for cross-artifact consistency check

---

**Plan Completed**: 2025-12-09
**Constitutional Compliance**: ✅ All gates passed (12/12 categories)
**Ready for Task Generation**: Yes
**Blocking Issues**: None
