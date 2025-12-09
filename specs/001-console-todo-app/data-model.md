# Data Model: Phase 1 Console-Based Todo Application

**Feature**: 001-console-todo-app
**Date**: 2025-12-09
**Phase**: Phase 1 Design Artifacts

## Overview

This document defines the complete data model for Phase 1, including entities, enums, validation rules, and state transitions. The model is designed for in-memory storage (Phase 1) with forward compatibility for database persistence (Phase 2).

---

## Entity: Task

### Description
Represents a single todo item with metadata for tracking work items.

### Fields

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | `str` (UUID) | Immutable, unique | Auto-generated | Unique identifier (UUID4 format) |
| `title` | `str` | Required, 1-200 chars | None | Task title (user-facing name) |
| `description` | `str` | Optional, 0-2000 chars | `""` (empty string) | Detailed task description |
| `due_date` | `Optional[str]` | Optional, ISO 8601 (YYYY-MM-DD) | `None` | Task deadline |
| `priority` | `Priority` (enum) | LOW, MEDIUM, HIGH | `Priority.MEDIUM` | Task importance level |
| `status` | `Status` (enum) | PENDING, COMPLETED | `Status.PENDING` | Task completion state |
| `created_at` | `str` (ISO 8601) | Immutable | Auto-generated (current time) | Task creation timestamp |
| `updated_at` | `str` (ISO 8601) | Auto-updated on modification | Auto-generated (current time) | Last modification timestamp |

### Validation Rules

1. **Title Validation**
   - **Rule**: `1 <= len(title) <= 200`
   - **Error**: "Title is required" (if empty), "Title must be 200 characters or less" (if too long)
   - **When**: On task creation and update

2. **Description Validation**
   - **Rule**: `len(description) <= 2000`
   - **Error**: "Description must be 2000 characters or less"
   - **When**: On task creation and update

3. **Due Date Validation**
   - **Rule**: If provided, must match ISO 8601 format `YYYY-MM-DD` (validated via `datetime.fromisoformat()`)
   - **Error**: "Date must be in ISO format YYYY-MM-DD"
   - **When**: On task creation and update
   - **Note**: Past dates are allowed (marked as overdue if status = pending)

4. **Priority Validation**
   - **Rule**: Must be one of `Priority.LOW`, `Priority.MEDIUM`, `Priority.HIGH`
   - **Error**: Auto-validated by Python enum (raises `ValueError` for invalid values)
   - **When**: On task creation and update

5. **Status Validation**
   - **Rule**: Must be one of `Status.PENDING`, `Status.COMPLETED`
   - **Error**: Auto-validated by Python enum (raises `ValueError` for invalid values)
   - **When**: On task creation and update

6. **ID Validation**
   - **Rule**: UUID4 format (auto-generated, cannot be modified)
   - **Error**: N/A (user cannot set ID manually)
   - **When**: On task creation only

7. **Timestamp Validation**
   - **Rule**: ISO 8601 datetime format (auto-generated, cannot be set manually for `created_at`)
   - **Error**: N/A (timestamps auto-managed)
   - **When**: `created_at` on creation, `updated_at` on creation and every modification

### Implementation (Python)

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class Task:
    """
    Represents a todo task with metadata for tracking work items.

    Attributes:
        title: Task title (required, 1-200 characters)
        description: Detailed task description (optional, up to 2000 characters)
        due_date: Task deadline in ISO 8601 format YYYY-MM-DD (optional)
        priority: Task importance level (LOW, MEDIUM, HIGH)
        status: Task completion state (PENDING, COMPLETED)
        id: Unique identifier (auto-generated UUID4)
        created_at: Task creation timestamp (auto-generated ISO 8601)
        updated_at: Last modification timestamp (auto-generated ISO 8601)

    Raises:
        ValidationError: If validation rules are violated (invalid title, description, or due_date)
    """
    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        """Validate task fields after initialization."""
        self._validate_title()
        self._validate_description()
        self._validate_due_date()

    def _validate_title(self) -> None:
        """Validate title field (required, 1-200 chars)."""
        if not self.title or len(self.title) < 1:
            raise ValidationError("Title is required")
        if len(self.title) > 200:
            raise ValidationError("Title must be 200 characters or less")

    def _validate_description(self) -> None:
        """Validate description field (optional, up to 2000 chars)."""
        if len(self.description) > 2000:
            raise ValidationError("Description must be 2000 characters or less")

    def _validate_due_date(self) -> None:
        """Validate due_date field (optional, ISO 8601 format YYYY-MM-DD)."""
        if self.due_date and not self._is_valid_iso_date(self.due_date):
            raise ValidationError("Date must be in ISO format YYYY-MM-DD")

    @staticmethod
    def _is_valid_iso_date(date_str: str) -> bool:
        """Check if date string is valid ISO 8601 format (YYYY-MM-DD)."""
        try:
            datetime.fromisoformat(date_str)
            return True
        except ValueError:
            return False

    def mark_updated(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now().isoformat()
```

---

## Enum: Priority

### Description
Represents task importance level (LOW, MEDIUM, HIGH).

### Values

| Value | String Representation | Description |
|-------|----------------------|-------------|
| `Priority.LOW` | `"low"` | Low-priority task (can be deferred) |
| `Priority.MEDIUM` | `"medium"` | Medium-priority task (default) |
| `Priority.HIGH` | `"high"` | High-priority task (urgent, important) |

### Sorting Order
HIGH → MEDIUM → LOW (descending priority)

### Implementation (Python)

```python
from enum import Enum

class Priority(str, Enum):
    """
    Task priority levels.

    Inherits from str to support JSON serialization for Phase 2 API.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """Convert string to Priority enum (case-insensitive)."""
        value_lower = value.lower()
        for priority in cls:
            if priority.value == value_lower:
                return priority
        raise ValueError(f"Invalid priority: {value}. Must be one of: low, medium, high")

    def __lt__(self, other: "Priority") -> bool:
        """Enable sorting: HIGH < MEDIUM < LOW (for descending sort)."""
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return order[self] < order[other]
```

---

## Enum: Status

### Description
Represents task completion state (PENDING, COMPLETED).

### Values

| Value | String Representation | Description |
|-------|----------------------|-------------|
| `Status.PENDING` | `"pending"` | Task not yet completed (default) |
| `Status.COMPLETED` | `"completed"` | Task finished |

### State Transitions

```
[PENDING] --mark_complete()--> [COMPLETED]
[COMPLETED] --mark_complete()--> [COMPLETED] (idempotent, no error)
```

**Note**: Phase 1 does not support unmarking tasks as pending. Phase 2 may add `Status.ARCHIVED` or `Status.CANCELLED`.

### Implementation (Python)

```python
from enum import Enum

class Status(str, Enum):
    """
    Task completion status.

    Inherits from str to support JSON serialization for Phase 2 API.
    """
    PENDING = "pending"
    COMPLETED = "completed"

    @classmethod
    def from_string(cls, value: str) -> "Status":
        """Convert string to Status enum (case-insensitive)."""
        value_lower = value.lower()
        for status in cls:
            if status.value == value_lower:
                return status
        raise ValueError(f"Invalid status: {value}. Must be one of: pending, completed")
```

---

## Custom Exceptions

### ValidationError

**Purpose**: Raised when task field validation fails (title too long, invalid date format, etc.)

**Usage**:
```python
class ValidationError(Exception):
    """Raised when task validation rules are violated."""
    pass
```

### TaskNotFoundError

**Purpose**: Raised when attempting to access a task by ID that doesn't exist

**Usage**:
```python
class TaskNotFoundError(Exception):
    """Raised when task is not found in repository."""
    pass
```

---

## Relationships

**Phase 1**: No relationships (single Task entity, no users, no projects, no tags)

**Phase 2**: Potential relationships for future expansion:
- `Task` → `User` (many-to-one: tasks belong to users)
- `Task` → `Project` (many-to-one: tasks belong to projects)
- `Task` → `Tag` (many-to-many: tasks can have multiple tags)

---

## Derived Properties

### is_overdue

**Type**: `bool` (computed property, not stored)

**Logic**: `due_date is not None AND due_date < today() AND status == PENDING`

**Implementation**:
```python
@property
def is_overdue(self) -> bool:
    """Check if task is overdue (past due date and still pending)."""
    if not self.due_date or self.status == Status.COMPLETED:
        return False
    return self.due_date < datetime.now().date().isoformat()
```

---

## Filtering Criteria (Spec Requirements)

| Filter | Logic | Example |
|--------|-------|---------|
| **By Status** | `task.status == filter_value` | Filter by `PENDING` or `COMPLETED` |
| **By Priority** | `task.priority == filter_value` | Filter by `LOW`, `MEDIUM`, `HIGH` |
| **By Overdue** | `task.is_overdue == True` | Show only overdue tasks |

---

## Sorting Criteria (Spec Requirements)

| Sort By | Logic | Order |
|---------|-------|-------|
| **Priority** | `Priority` enum ordering | HIGH → MEDIUM → LOW |
| **Due Date** | ISO date string comparison | Earliest first, null dates last |
| **Status** | `Status` enum ordering | PENDING → COMPLETED |

**Implementation**:
```python
# Sort by priority (descending: high → medium → low)
tasks_sorted = sorted(tasks, key=lambda t: t.priority)

# Sort by due_date (ascending: earliest first, nulls last)
tasks_sorted = sorted(tasks, key=lambda t: (t.due_date is None, t.due_date or ""))

# Sort by status (pending first, then completed)
tasks_sorted = sorted(tasks, key=lambda t: t.status.value)
```

---

## Phase 2 Migration Notes

### Task Entity Changes

**Current (Phase 1 - `dataclass`)**:
```python
@dataclass
class Task:
    id: str
    title: str
    # ... other fields
```

**Future (Phase 2 - SQLAlchemy ORM)**:
```python
from sqlalchemy import Column, String, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(String(2000), default="")
    due_date = Column(String, nullable=True)  # Or use Date type
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM)
    status = Column(SQLEnum(Status), default=Status.PENDING)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, onupdate=lambda: datetime.now().isoformat())
```

**Migration Strategy**:
- Add SQLAlchemy decorators to existing Task class
- Keep validation logic in `__post_init__` or move to Pydantic schema layer
- Repository layer swaps `dict[str, Task]` for `session.query(Task)` calls

---

## Sample Data (for Testing)

```python
# Sample tasks for testing filters and sorts
sample_tasks = [
    Task(
        title="Buy groceries",
        description="Get milk, bread, eggs",
        due_date="2025-12-10",
        priority=Priority.HIGH,
        status=Status.PENDING
    ),
    Task(
        title="Team meeting",
        description="",
        due_date="2025-12-15",
        priority=Priority.MEDIUM,
        status=Status.PENDING
    ),
    Task(
        title="Complete project report",
        description="Q4 deliverables",
        due_date="2025-12-08",  # Overdue!
        priority=Priority.HIGH,
        status=Status.PENDING
    ),
    Task(
        title="Read documentation",
        description="",
        due_date=None,
        priority=Priority.LOW,
        status=Status.COMPLETED
    )
]
```

---

**Data Model Completed**: 2025-12-09
**Entities**: 1 (Task)
**Enums**: 2 (Priority, Status)
**Custom Exceptions**: 2 (ValidationError, TaskNotFoundError)
**Phase 2 Ready**: Yes (clear migration path to SQLAlchemy/Pydantic)
