# Technical Research: Phase 1 Console-Based Todo Application

**Feature**: 001-console-todo-app
**Date**: 2025-12-09
**Research Phase**: Phase 0 (Pre-Implementation)

## Overview

This document captures all technical research and decision-making for Phase 1 implementation. All unknowns from Technical Context have been resolved, and implementation patterns have been established.

---

## Research Area 1: Task Model Implementation

### Question
How should the Task entity be implemented in Python to satisfy constitutional requirements (type safety, forward compatibility) while remaining simple for Phase 1?

### Options Considered

1. **Python `dataclass` with manual validation**
   - Pros: Built-in (no dependencies), type hints supported, default values, immutable option, clean syntax
   - Cons: Manual validation required, no auto-serialization
   - Phase 2 Compatibility: Can convert to Pydantic or SQLAlchemy easily

2. **Pydantic `BaseModel`**
   - Pros: Auto-validation, JSON serialization, great for APIs, type coercion
   - Cons: External dependency, overkill for in-memory console app
   - Phase 2 Compatibility: Perfect for FastAPI, but adds complexity for Phase 1

3. **Plain Python class**
   - Pros: Maximum flexibility, no magic
   - Cons: Verbose, no type safety, no defaults, manual `__init__`
   - Phase 2 Compatibility: Harder to migrate to ORM

### Decision

**Use Python `dataclass` with manual validation.**

### Rationale

- **Simplicity**: dataclass provides type hints, default values, and clean syntax with zero external dependencies
- **Constitutional Compliance**: Satisfies type safety requirement (§6.1) without adding dependencies
- **Forward Compatibility**: Easy to convert to Pydantic (add decorators) or SQLAlchemy (add ORM decorators) in Phase 2
- **Validation Control**: Manual validation in `__post_init__` gives full control over error messages (constitutional requirement §6.2)

### Implementation Pattern

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class Task:
    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        # Validation logic
        if not self.title or len(self.title) < 1:
            raise ValidationError("Title is required")
        if len(self.title) > 200:
            raise ValidationError("Title must be 200 characters or less")
        if len(self.description) > 2000:
            raise ValidationError("Description must be 2000 characters or less")
        if self.due_date and not self._is_valid_iso_date(self.due_date):
            raise ValidationError("Date must be in ISO format YYYY-MM-DD")

    @staticmethod
    def _is_valid_iso_date(date_str: str) -> bool:
        try:
            datetime.fromisoformat(date_str)
            return True
        except ValueError:
            return False
```

---

## Research Area 2: Storage Implementation

### Question
What data structure should be used for in-memory task storage to satisfy performance goals (< 1s for 500 tasks) and forward compatibility (Phase 2 database swap)?

### Options Considered

1. **`dict[str, Task]` with UUID keys**
   - Pros: O(1) lookup by ID, natural mapping to database primary key, fast iteration
   - Cons: No built-in ordering (but Python 3.7+ dicts preserve insertion order)
   - Phase 2 Compatibility: Identical interface to database repository (get by ID)

2. **`list[Task]`**
   - Pros: Simple, preserves order, easy filtering
   - Cons: O(n) lookup by ID, slower for large datasets
   - Phase 2 Compatibility: Less natural for database migration (no indexed access)

3. **SQLite in-memory database**
   - Pros: Real SQL, practice for Phase 2
   - Cons: Violates constitution (§4: no databases in Phase 1), adds dependency
   - Phase 2 Compatibility: Perfect, but breaks constitutional rules

### Decision

**Use `dict[str, Task]` with UUID string keys.**

### Rationale

- **Performance**: O(1) lookup satisfies performance goal (< 1s for 500 tasks, < 5s for 100 filtered tasks)
- **Constitutional Compliance**: Pure in-memory Python data structure (§5.3), no persistence
- **Forward Compatibility**: Repository interface (`get(id)`, `add(task)`, `delete(id)`) maps 1:1 to database operations
- **Filtering/Sorting**: Iterate `dict.values()` for filtering/sorting (acceptable performance for Phase 1 scale)

### Implementation Pattern

```python
class InMemoryTaskRepository:
    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def add(self, task: Task) -> None:
        self.tasks[task.id] = task

    def get(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def update(self, task: Task) -> None:
        if task.id not in self.tasks:
            raise TaskNotFoundError(f"Task {task.id} not found")
        self.tasks[task.id] = task

    def delete(self, task_id: str) -> None:
        if task_id not in self.tasks:
            raise TaskNotFoundError(f"Task {task_id} not found")
        del self.tasks[task_id]

    def list_all(self) -> list[Task]:
        return list(self.tasks.values())
```

---

## Research Area 3: Enum Implementation

### Question
How should Priority and Status enums be implemented to ensure type safety and database compatibility?

### Options Considered

1. **Python `enum.Enum`**
   - Pros: Type-safe, auto-validation, string representation, database-compatible
   - Cons: Slightly verbose
   - Phase 2 Compatibility: SQLAlchemy supports Enum columns natively

2. **String literals with constants**
   - Pros: Simple
   - Cons: No type safety, no auto-validation, error-prone
   - Phase 2 Compatibility: Would need migration to enum

3. **`typing.Literal`**
   - Pros: Type-checked by mypy
   - Cons: No runtime validation, requires Python 3.8+
   - Phase 2 Compatibility: Still needs conversion to database enum

### Decision

**Use Python `enum.Enum` for Priority and Status.**

### Rationale

- **Type Safety**: mypy enforces enum types (constitutional requirement §7.1)
- **Auto-Validation**: Invalid values raise exception automatically
- **Database Compatibility**: SQLAlchemy and Pydantic support Enum types natively
- **String Representation**: `priority.value` gives lowercase string for console display

### Implementation Pattern

```python
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Status(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
```

**Note**: Inheriting from `str` makes enum values JSON-serializable for Phase 2 API responses.

---

## Research Area 4: Date Handling

### Question
How should due_date be stored and validated to satisfy ISO 8601 requirement (FR-002) and support sorting?

### Options Considered

1. **Store as ISO 8601 string, validate with `datetime.fromisoformat()`**
   - Pros: Matches spec, simple string comparison for sorting, database-compatible
   - Cons: Manual validation required
   - Phase 2 Compatibility: Can convert to database Date type or keep as string

2. **Store as `datetime` objects**
   - Pros: Rich datetime operations, built-in validation
   - Cons: Requires timezone handling (complex), serialization overhead
   - Phase 2 Compatibility: Would need conversion to/from ISO strings for API

3. **Store as Unix timestamps (int)**
   - Pros: Simple sorting, compact
   - Cons: Not human-readable, violates spec (requires ISO 8601)
   - Phase 2 Compatibility: Would need conversion layer

### Decision

**Store as ISO 8601 string, validate with `datetime.fromisoformat()`.**

### Rationale

- **Spec Compliance**: FR-002 explicitly requires ISO 8601 format (YYYY-MM-DD)
- **Sorting**: String comparison works for ISO dates ("2025-12-10" < "2025-12-20")
- **Simplicity**: No timezone complexity, no serialization overhead
- **Database Compatibility**: Most databases accept ISO 8601 strings or convert easily

### Implementation Pattern

```python
from datetime import datetime

def validate_iso_date(date_str: str) -> bool:
    """Validate ISO 8601 date format (YYYY-MM-DD)."""
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False

def is_overdue(due_date: Optional[str], status: Status) -> bool:
    """Check if task is overdue (due_date < today and status = pending)."""
    if not due_date or status == Status.COMPLETED:
        return False
    return due_date < datetime.now().date().isoformat()
```

---

## Research Area 5: Console Formatting

### Question
What approach should be used for console table formatting to satisfy UX requirements (FR-013: aligned columns, truncation)?

### Options Considered

1. **Manual string formatting with f-strings**
   - Pros: No dependencies, full control, lightweight
   - Cons: Manual alignment, manual truncation
   - Phase 2 Compatibility: Console UI will be deprecated anyway

2. **Rich library**
   - Pros: Beautiful tables, colors, automatic alignment
   - Cons: Adds dependency, overkill for Phase 1
   - Phase 2 Compatibility: Would be removed

3. **PrettyTable library**
   - Pros: Simple table API
   - Cons: Adds dependency, less flexible than Rich
   - Phase 2 Compatibility: Would be removed

### Decision

**Use manual string formatting with f-strings and `str.format()`.**

### Rationale

- **Constitutional Compliance**: Minimal dependencies (§6.1: no external libraries required)
- **Simplicity**: Sufficient for Phase 1 requirements (table with 5 columns, truncation)
- **Forward Compatibility**: Console UI will be deprecated in Phase 2, no need for fancy libraries

### Implementation Pattern

```python
def format_task_table(tasks: list[Task]) -> str:
    """Format tasks as aligned table."""
    if not tasks:
        return "No tasks found"

    header = f"{'ID':<10} {'Title':<50} {'Priority':<10} {'Status':<12} {'Due Date':<12}"
    separator = "-" * 94
    rows = [header, separator]

    for task in tasks:
        task_id = task.id[:8]  # First 8 chars of UUID
        title = task.title[:47] + "..." if len(task.title) > 50 else task.title.ljust(50)
        priority = task.priority.value.ljust(10)
        status = task.status.value.ljust(12)
        due_date = (task.due_date or "").ljust(12)

        row = f"{task_id:<10} {title:<50} {priority:<10} {status:<12} {due_date:<12}"
        rows.append(row)

    return "\n".join(rows)
```

---

## Research Area 6: Error Handling Strategy

### Question
How should errors be communicated from service layer to command layer while maintaining separation of concerns?

### Options Considered

1. **Service returns `(success: bool, message: str, data: Optional[Task])` tuples**
   - Pros: Clean separation, command layer formats for console, service remains UI-agnostic
   - Cons: Verbose
   - Phase 2 Compatibility: Service can return same tuple, FastAPI wrapper converts to HTTP response

2. **Raise exceptions, catch in command layer**
   - Pros: Pythonic, clean error flow
   - Cons: Mixes concerns (service knows about console error display)
   - Phase 2 Compatibility: FastAPI can catch exceptions and convert to HTTP errors

3. **Return error codes (int)**
   - Pros: Simple
   - Cons: Not Pythonic, requires error code documentation
   - Phase 2 Compatibility: Would need conversion to HTTP status codes

### Decision

**Service returns `(success: bool, message: str, data: Optional[Task])` tuples.**

### Rationale

- **Separation of Concerns**: Service layer remains UI-agnostic, command layer formats errors for console
- **Forward Compatibility**: FastAPI wrapper can convert tuple to JSON response or HTTP exception
- **Clear Contracts**: Service always returns same structure, easy to test
- **Type Safety**: Return type `tuple[bool, str, Optional[Task]]` is type-checked by mypy

### Implementation Pattern

```python
# Service layer
def create_task(self, title: str, description: str = "", ...) -> tuple[bool, str, Optional[Task]]:
    try:
        task = Task(title=title, description=description, ...)
        self.repository.add(task)
        return (True, "Task created successfully", task)
    except ValidationError as e:
        return (False, str(e), None)

# Command layer
def add_task_command(service: TaskService):
    title = input("Enter task title: ")
    description = input("Enter description (optional): ")
    success, message, task = service.create_task(title, description)

    if success:
        print(f"✓ {message}")
        print(f"  Task ID: {task.id[:8]}")
    else:
        print(f"✗ Error: {message}")
```

---

## Research Area 7: Testing Strategy

### Question
What pytest patterns should be used to achieve 80% coverage while testing command layer (input/output)?

### Options Considered

1. **pytest with fixtures + monkeypatch for stdin/stdout**
   - Pros: Clean test isolation, no dependencies, mocks input/output
   - Cons: Requires learning monkeypatch API
   - Phase 2 Compatibility: Command tests become deprecated

2. **pytest with pytest-mock library**
   - Pros: More flexible mocking
   - Cons: Adds dependency
   - Phase 2 Compatibility: Would be removed

3. **unittest framework**
   - Pros: Built-in (no dependency)
   - Cons: More verbose, less idiomatic
   - Phase 2 Compatibility: Would need migration to pytest for FastAPI tests

### Decision

**pytest with fixtures + monkeypatch for stdin/stdout.**

### Rationale

- **Constitutional Compliance**: pytest specified in constitution (§7.2)
- **Clean Isolation**: Fixtures enable test data reuse (sample tasks, mock repository)
- **Input/Output Mocking**: `monkeypatch.setattr('builtins.input', lambda _: "test")` mocks console input
- **Coverage**: Parametrize supports edge case testing (long input, special chars, etc.)

### Implementation Pattern

```python
# conftest.py
@pytest.fixture
def mock_repository():
    return InMemoryTaskRepository()

@pytest.fixture
def sample_task():
    return Task(
        title="Sample Task",
        description="This is a test task",
        priority=Priority.HIGH,
        status=Status.PENDING
    )

# test_commands/test_add_task.py
def test_add_task_success(monkeypatch, capsys, mock_repository):
    inputs = iter(["Buy groceries", "Get milk and bread"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    service = TaskService(mock_repository)
    add_task_command(service)

    captured = capsys.readouterr()
    assert "✓ Task created successfully" in captured.out
    assert mock_repository.list_all()[0].title == "Buy groceries"
```

---

## Research Area 8: Type Checking Configuration

### Question
What mypy configuration is needed to satisfy constitutional requirement (§7.1: 100% type hint coverage, strict mode)?

### Options Considered

1. **mypy strict mode with project-specific exceptions**
   - Pros: Maximum type safety, catches bugs early
   - Cons: Strict enforcement may flag false positives
   - Phase 2 Compatibility: Same strict mode for FastAPI

2. **mypy normal mode with manual flags**
   - Pros: More flexible
   - Cons: Doesn't satisfy constitutional requirement
   - Phase 2 Compatibility: Would need upgrade to strict

3. **Skip type checking (use pyright instead)**
   - Pros: Pyright is faster
   - Cons: Violates constitution (§7.1 specifies mypy)
   - Phase 2 Compatibility: Tool switch overhead

### Decision

**mypy strict mode with project-specific configuration.**

### Rationale

- **Constitutional Compliance**: §7.1 mandates "mypy in strict mode" with "100% type hint coverage"
- **Quality**: Catches type errors early, documents interfaces
- **Forward Compatibility**: FastAPI benefits from strict typing (Pydantic models)

### Implementation Pattern

Create `mypy.ini` in `phase1/`:

```ini
[mypy]
python_version = 3.13
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_unimported = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True

[mypy-pytest.*]
ignore_missing_imports = True
```

---

## Summary of Technical Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Task Model | Python `dataclass` with manual validation | Simple, type-safe, forward-compatible, no dependencies |
| Storage | `dict[str, Task]` with UUID keys | O(1) lookup, Phase 2 database compatibility, constitutional compliance |
| Enums | `enum.Enum` for Priority and Status | Type-safe, auto-validation, database-compatible |
| Date Handling | ISO 8601 string with `fromisoformat()` validation | Spec compliance, simple sorting, database-compatible |
| Console Formatting | Manual f-strings and `str.format()` | No dependencies, sufficient for Phase 1, console deprecated in Phase 2 |
| Error Handling | Service returns `(bool, str, Optional[Task])` tuples | Separation of concerns, forward-compatible, type-safe |
| Testing | pytest with fixtures + monkeypatch | Constitutional requirement, clean isolation, input/output mocking |
| Type Checking | mypy strict mode | Constitutional requirement, maximum type safety, catches bugs early |

---

## Remaining Unknowns

**None.** All technical decisions have been resolved. Implementation can proceed.

---

**Research Completed**: 2025-12-09
**Status**: All unknowns resolved, ready for Phase 1 design artifacts
