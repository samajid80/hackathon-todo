# Data Model: Task Tags/Categories

**Feature**: 003-task-tags
**Date**: 2025-12-23
**Purpose**: Define data structures, relationships, and validation rules for task tags

## 1. Entity Overview

### 1.1 Task (Enhanced)

Existing `Task` entity enhanced with tags support.

**Attributes**:
- `id` (UUID, PK) - Unique task identifier
- `user_id` (UUID, FK) - Owner of the task (references `users.id`)
- `title` (VARCHAR(200), NOT NULL) - Task title
- `description` (TEXT, NULLABLE) - Optional task description
- `due_date` (DATE, NULLABLE) - Optional deadline
- `priority` (VARCHAR(10), NOT NULL) - Priority level (low/medium/high)
- `status` (VARCHAR(10), NOT NULL) - Status (pending/completed)
- `tags` (TEXT[], NOT NULL DEFAULT '{}') - **NEW**: Category labels
- `created_at` (TIMESTAMP, NOT NULL) - Creation timestamp
- `updated_at` (TIMESTAMP, NOT NULL) - Last update timestamp

**Indexes**:
- PRIMARY KEY: `id`
- INDEX: `user_id` (for user-scoped queries)
- INDEX: `user_id, status` (for filtered lists)
- INDEX: `user_id, due_date` (for sorting by due date)
- **GIN INDEX**: `tags` (for tag containment queries) - **NEW**

**Constraints**:
- FOREIGN KEY: `user_id` REFERENCES `users(id)`
- CHECK: `array_length(tags, 1) <= 10` (max 10 tags per task)
- CHECK: `status IN ('pending', 'completed')`
- CHECK: `priority IN ('low', 'medium', 'high')`

### 1.2 Task Tag (Conceptual Entity)

Tags are not stored as separate entities but as array elements within tasks.

**Properties**:
- `tag_name` (VARCHAR(50)) - Lowercase alphanumeric string with hyphens
- `task_id` (implicit) - Parent task (many-to-many conceptually)
- `user_id` (implicit, inherited from task) - Owner (scoped per user)

**Validation Rules**:
- Length: 1-50 characters
- Format: `^[a-z0-9-]+$` (lowercase letters, numbers, hyphens only)
- Uniqueness: No duplicate tags within a single task
- Normalization: Automatically converted to lowercase, whitespace trimmed

**Lifecycle**:
- **Creation**: When user adds tag to task
- **Deletion**: When user removes tag from task or deletes task
- **Discovery**: User can view all unique tags they've used (computed query)

## 2. Database Schema

### 2.1 Migration Script

**File**: `backend/migrations/005_add_tags_to_tasks.sql`

```sql
-- Migration 005: Add tags support to tasks table
-- Date: 2025-12-23
-- Description: Add tags column as TEXT array for task categorization

-- Add tags column (nullable initially for backward compatibility)
ALTER TABLE tasks
ADD COLUMN tags TEXT[] DEFAULT '{}' NOT NULL;

-- Create GIN index for efficient tag containment queries
CREATE INDEX idx_tasks_tags ON tasks USING GIN (tags);

-- Add check constraint for max 10 tags per task
ALTER TABLE tasks
ADD CONSTRAINT chk_max_tags CHECK (array_length(tags, 1) IS NULL OR array_length(tags, 1) <= 10);

-- Comment for documentation
COMMENT ON COLUMN tasks.tags IS 'Task category labels (max 10, lowercase alphanumeric + hyphens)';
```

### 2.2 Schema After Migration

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date DATE,
    priority VARCHAR(10) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    status VARCHAR(10) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    tags TEXT[] NOT NULL DEFAULT '{}',  -- NEW
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_user_status ON tasks (user_id, status);
CREATE INDEX idx_user_due_date ON tasks (user_id, due_date);
CREATE INDEX idx_tasks_tags ON tasks USING GIN (tags);  -- NEW
```

## 3. ORM Models (SQLModel)

### 3.1 Task Model

**File**: `backend/models/task.py`

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String
from pydantic import field_validator
import re

class TaskBase(SQLModel):
    """Base task fields shared between models."""
    title: str = Field(max_length=200, min_length=1)
    description: str | None = Field(default=None, max_length=2000)
    due_date: date | None = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.PENDING)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String))
    )  # NEW

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and normalize tags.

        Rules:
        - Max 10 tags per task
        - Each tag: 1-50 chars, lowercase alphanumeric + hyphens
        - Automatically trim whitespace and lowercase
        - Remove duplicates
        """
        if not v:
            return []

        # Remove duplicates while preserving order
        unique_tags = list(dict.fromkeys(v))

        # Validate max count
        if len(unique_tags) > 10:
            raise ValueError("Maximum 10 tags allowed per task")

        # Normalize and validate each tag
        validated_tags = []
        for tag in unique_tags:
            # Trim and lowercase
            tag = tag.strip().lower()

            # Skip empty tags
            if not tag:
                continue

            # Validate length
            if len(tag) < 1 or len(tag) > 50:
                raise ValueError(f"Tag must be 1-50 characters, got '{tag}' ({len(tag)} chars)")

            # Validate format
            if not re.match(r'^[a-z0-9-]+$', tag):
                raise ValueError(f"Tag must contain only lowercase letters, numbers, and hyphens: '{tag}'")

            validated_tags.append(tag)

        return validated_tags

class Task(TaskBase, table=True):
    """Task ORM model for database table."""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Override priority and status to store as strings in database
    priority: str = Field(max_length=10, nullable=False, default="medium")
    status: str = Field(max_length=10, nullable=False, default="pending")
```

### 3.2 Pydantic Schemas

**File**: `backend/models/task.py` (continued)

```python
class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass  # Inherits validation from TaskBase

class TaskUpdate(SQLModel):
    """Schema for updating a task (partial updates)."""
    title: str | None = Field(default=None, max_length=200, min_length=1)
    description: str | None = Field(default=None, max_length=2000)
    due_date: date | None = None
    priority: Priority | None = None
    status: Status | None = None
    tags: list[str] | None = None  # NEW

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate tags for updates (same rules as TaskBase)."""
        if v is None:
            return None

        # Apply same validation as TaskBase
        return TaskBase.validate_tags(v)

class TaskRead(TaskBase):
    """Schema for reading a task (API response)."""
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
```

## 4. Relationships

### 4.1 Task ↔ Tags (Many-to-Many, Conceptual)

```
Task (1) ----< Tags (N)
```

**Relationship Type**: Embedded many-to-many (stored as array, not junction table)

**Cardinality**:
- One task can have 0 to 10 tags
- One tag can be associated with multiple tasks
- Tags are not first-class entities (no separate `tags` table)

**Query Patterns**:

1. **Get task with tags**:
```sql
SELECT id, title, tags FROM tasks WHERE id = 'abc';
-- Result: {id: 'abc', title: 'Buy groceries', tags: ['home', 'shopping']}
```

2. **Filter tasks by tag**:
```sql
SELECT * FROM tasks WHERE user_id = 'xyz' AND tags @> ARRAY['work'];
```

3. **Filter tasks by multiple tags (AND logic)**:
```sql
SELECT * FROM tasks WHERE user_id = 'xyz'
  AND tags @> ARRAY['work']
  AND tags @> ARRAY['urgent'];
```

4. **Get all unique tags for user**:
```sql
SELECT DISTINCT unnest(tags) as tag
FROM tasks
WHERE user_id = 'xyz'
ORDER BY tag;
```

### 4.2 User ↔ Tasks (One-to-Many, Existing)

```
User (1) ----< Tasks (N)
```

**Relationship Type**: One-to-many with foreign key
**Constraint**: `tasks.user_id` REFERENCES `users.id` ON DELETE CASCADE
**User Isolation**: All task queries filtered by `user_id`

## 5. Data Validation Rules

### 5.1 Tag Validation

| Rule | Constraint | Error Message |
|------|-----------|---------------|
| Max tags | `<= 10` | "Maximum 10 tags allowed per task" |
| Min length | `>= 1 char` | "Tag cannot be empty" |
| Max length | `<= 50 chars` | "Tag must be 1-50 characters long" |
| Format | `^[a-z0-9-]+$` | "Tags can only contain lowercase letters, numbers, and hyphens" |
| Normalization | Lowercase + trim | (automatic, no error) |
| Deduplication | Remove duplicates | (automatic, no error) |

### 5.2 Validation Flow

```
User Input: ["Work", "  urgent  ", "work", "URGENT!!!"]
    ↓
Trim & Lowercase: ["work", "urgent", "work", "urgent!!!"]
    ↓
Deduplicate: ["work", "urgent", "urgent!!!"]
    ↓
Validate Format: ❌ "urgent!!!" fails regex
    ↓
Error: "Tags can only contain lowercase letters, numbers, and hyphens: 'urgent!!!'"
```

**Successful Example**:
```
User Input: ["Work", "  urgent  ", "work", "home"]
    ↓
Trim & Lowercase: ["work", "urgent", "work", "home"]
    ↓
Deduplicate: ["work", "urgent", "home"]
    ↓
Validate Format: ✅ All pass
    ↓
Stored: ["work", "urgent", "home"]
```

## 6. State Transitions

Tags have no explicit state machine, but follow task lifecycle:

```
Task Created → Tags = [] (empty)
    ↓
User Adds Tag → Tags = ["work"]
    ↓
User Adds Another → Tags = ["work", "urgent"]
    ↓
User Removes Tag → Tags = ["urgent"]
    ↓
Task Deleted → Tags deleted (cascade)
```

## 7. Data Access Patterns

### 7.1 Read Patterns

| Pattern | Frequency | Query |
|---------|-----------|-------|
| Get task with tags | High | `SELECT * FROM tasks WHERE id = ?` |
| Filter by single tag | Medium | `WHERE tags @> ARRAY['work']` |
| Filter by multiple tags | Low | `WHERE tags @> ARRAY['work'] AND tags @> ARRAY['urgent']` |
| List all user tags | Low | `SELECT DISTINCT unnest(tags) FROM tasks WHERE user_id = ?` |

### 7.2 Write Patterns

| Pattern | Frequency | Query |
|---------|-----------|-------|
| Create task with tags | High | `INSERT INTO tasks (..., tags) VALUES (..., ARRAY['work'])` |
| Add tag to task | Medium | `UPDATE tasks SET tags = array_append(tags, 'urgent') WHERE id = ?` |
| Remove tag from task | Medium | `UPDATE tasks SET tags = array_remove(tags, 'work') WHERE id = ?` |
| Replace all tags | Low | `UPDATE tasks SET tags = ARRAY['new1', 'new2'] WHERE id = ?` |

## 8. Performance Considerations

### 8.1 Index Usage

**GIN Index on `tags` column**:
- Optimizes: `@>` (contains), `&&` (overlaps), `<@` (contained by)
- Query time: O(log n) for containment checks
- Index size: ~30% of column size
- Maintenance: Updated on INSERT/UPDATE (acceptable overhead)

### 8.2 Query Optimization

**Efficient**:
```sql
-- Uses GIN index
SELECT * FROM tasks WHERE user_id = 'xyz' AND tags @> ARRAY['work'];
```

**Inefficient**:
```sql
-- Sequential scan (no index on unnest)
SELECT * FROM tasks WHERE user_id = 'xyz' AND 'work' = ANY(tags);
```

### 8.3 Scalability

| Metric | Limit | Rationale |
|--------|-------|-----------|
| Tags per task | 10 | Prevents UX clutter, reasonable categorization |
| Unique tags per user | ~100 | Expected typical usage (10-50 common) |
| Tasks per user | ~10,000 | GIN index performs well at this scale |
| Tag autocomplete | <300ms | Client-side filtering of ~100 tags is instant |

## 9. Data Integrity

### 9.1 Constraints

1. **Foreign Key**: `user_id` references `users.id` (CASCADE DELETE)
2. **Check Constraint**: `array_length(tags, 1) <= 10`
3. **NOT NULL**: `tags` defaults to `'{}'` (empty array)
4. **Application Validation**: Pydantic validates format, length, normalization

### 9.2 Referential Integrity

- **Task Deletion**: Tags deleted automatically (no orphans)
- **User Deletion**: All tasks (and their tags) deleted (CASCADE)
- **Tag Removal**: If tag removed from all tasks, it disappears from tag list (computed)

## 10. Migration Strategy

### 10.1 Backward Compatibility

**Existing tasks** (before migration):
- `tags` column added with `DEFAULT '{}'`
- All existing tasks get empty array automatically
- No data loss

**Rollback plan** (if migration fails):
```sql
-- Rollback 005
ALTER TABLE tasks DROP COLUMN tags;
DROP INDEX idx_tasks_tags;
```

### 10.2 Data Seeding (Optional)

For testing:
```sql
-- Add sample tags to existing tasks
UPDATE tasks SET tags = ARRAY['work'] WHERE title ILIKE '%meeting%';
UPDATE tasks SET tags = ARRAY['home'] WHERE title ILIKE '%clean%';
UPDATE tasks SET tags = ARRAY['urgent', 'work'] WHERE priority = 'high';
```

## 11. Summary

| Aspect | Design Decision |
|--------|----------------|
| **Storage** | PostgreSQL TEXT[] array in `tasks` table |
| **Validation** | Pydantic validators (1-50 chars, alphanumeric + hyphens) |
| **Indexing** | GIN index for fast containment queries |
| **Max Tags** | 10 per task (enforced by application + DB constraint) |
| **Normalization** | Automatic lowercase + trim + deduplication |
| **User Isolation** | Tags scoped per user (inherited from task's `user_id`) |
| **Relationships** | Embedded many-to-many (no junction table) |
| **Migration** | Backward compatible (defaults to empty array) |
