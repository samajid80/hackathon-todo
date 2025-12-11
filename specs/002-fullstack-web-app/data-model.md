# Data Model: Phase 2 Full-Stack Todo Web Application

**Feature**: 002-fullstack-web-app
**Date**: 2025-12-11
**Phase**: 1 (Design & Contracts)

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for Phase 2. The data model supports user authentication with task isolation, ensuring each user can only access their own tasks.

---

## Entity: User

**Managed by**: Better-Auth (Next.js frontend)

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique user identifier |
| `email` | String | Unique, Required, Email format | User's email address (login credential) |
| `password` | String | Required, Hashed (bcrypt) | User's password (minimum 8 characters) |
| `created_at` | Timestamp | Auto-generated (UTC) | Account creation timestamp |
| `updated_at` | Timestamp | Auto-updated (UTC) | Last account modification timestamp |

### Relationships

- **Has many** Tasks (one-to-many relationship via `user_id` foreign key)

### Validation Rules

1. **Email Format**: Must match RFC 5322 email format (validated by Better-Auth)
2. **Email Uniqueness**: Cannot create duplicate accounts with same email
3. **Password Length**: Minimum 8 characters
4. **Password Hashing**: Automatically hashed by Better-Auth using bcrypt

### Notes

- Better-Auth creates and manages the `users` table automatically
- Backend does NOT directly access the users table
- Backend receives user_id from validated JWT token
- User authentication flow handled entirely by Better-Auth in Next.js

---

## Entity: Task

**Managed by**: FastAPI backend + PostgreSQL

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique task identifier |
| `user_id` | UUID | Foreign Key (→ users.id), Required, Indexed | Owner of the task |
| `title` | String | Required, Max 200 chars | Task title/summary |
| `description` | String | Optional, Max 2000 chars | Detailed task description |
| `due_date` | Date | Optional, ISO 8601 format (YYYY-MM-DD) | Task deadline |
| `priority` | Enum | Required, Default: `medium` | Task priority level |
| `status` | Enum | Required, Default: `pending` | Task completion status |
| `created_at` | Timestamp | Auto-generated (UTC) | Task creation timestamp |
| `updated_at` | Timestamp | Auto-updated (UTC) | Last modification timestamp |

### Enum Definitions

**Priority Enum**:
- `low`: Low priority task
- `medium`: Medium priority task (default)
- `high`: High priority task

**Status Enum**:
- `pending`: Task not yet completed (default)
- `completed`: Task finished

### Relationships

- **Belongs to** one User (many-to-one relationship via `user_id`)

### Database Indexes

Performance-critical indexes for efficient queries:

1. **user_id** (B-tree index)
   - Supports user-scoped queries (list all user's tasks)
   - Required for all task operations

2. **status** (B-tree index)
   - Supports status filtering (pending, completed)

3. **due_date** (B-tree index)
   - Supports sorting by due date
   - Supports overdue filtering (where due_date < today AND status = pending)

4. **Composite: (user_id, status)** (B-tree index)
   - Optimizes filtered queries (e.g., user's pending tasks)
   - Most common query pattern

5. **Composite: (user_id, due_date)** (B-tree index)
   - Optimizes sorted queries by due date for a user
   - Supports overdue detection

### Validation Rules

1. **Title**:
   - NOT NULL
   - NOT EMPTY (after trimming whitespace)
   - Maximum 200 characters
   - Error: "Title is required" (if empty)
   - Error: "Title must be 200 characters or less" (if too long)

2. **Description**:
   - Optional (can be NULL)
   - Maximum 2000 characters
   - Error: "Description must be 2000 characters or less" (if too long)

3. **Due Date**:
   - Optional (can be NULL)
   - Must be valid ISO 8601 date format: YYYY-MM-DD
   - Past dates are allowed (task can be overdue at creation)
   - Error: "Please provide a valid date" (if invalid format)

4. **Priority**:
   - Must be one of: low, medium, high
   - Cannot be NULL (default: medium if not specified)
   - Error: "Priority must be one of: low, medium, high" (if invalid)

5. **Status**:
   - Must be one of: pending, completed
   - Cannot be NULL (default: pending if not specified)
   - Error: "Status must be one of: pending, completed" (if invalid)

6. **User Ownership**:
   - User can only access/modify tasks where `user_id` matches their JWT user_id
   - Error: "Access denied" (403) if attempting to access another user's task

### State Transitions

#### Task Creation
```
Initial State: None
Action: Create task (POST /api/tasks)
Result: New task with status = pending, priority = medium (default)
Timestamps: created_at and updated_at set to current UTC time
```

#### Mark Task Complete
```
From: status = pending
Action: Complete task (PATCH /api/tasks/{id}/complete)
To: status = completed
Idempotent: If already completed, remains completed (no error)
Timestamps: updated_at refreshed to current UTC time
```

#### Update Task
```
From: Any task state
Action: Update task (PUT /api/tasks/{id})
To: Updated fields (title, description, due_date, priority)
Note: Status can be manually changed via update
Timestamps: updated_at refreshed to current UTC time
```

#### Delete Task
```
From: Any task state
Action: Delete task (DELETE /api/tasks/{id})
Result: Task permanently removed from database
Note: Requires user confirmation in UI
```

### State Diagram

```
    [Create]
       ↓
  ┌─ pending ─┐
  │           │
  │ [Update]  │ [Complete]
  │     ↓     ↓
  └─ pending → completed ─┐
              ↑           │
              │ [Update]  │
              └───────────┘
                   ↓
              [Delete]
                   ↓
              (removed)
```

### Query Patterns

#### List User's Tasks (All)
```sql
SELECT * FROM tasks
WHERE user_id = :user_id
ORDER BY created_at DESC;
```
**Index used**: user_id

#### List User's Pending Tasks
```sql
SELECT * FROM tasks
WHERE user_id = :user_id AND status = 'pending'
ORDER BY due_date ASC NULLS LAST;
```
**Index used**: (user_id, status)

#### List User's Overdue Tasks
```sql
SELECT * FROM tasks
WHERE user_id = :user_id
  AND status = 'pending'
  AND due_date < CURRENT_DATE
ORDER BY due_date ASC;
```
**Index used**: (user_id, due_date)

#### Get Single Task (with ownership check)
```sql
SELECT * FROM tasks
WHERE id = :task_id AND user_id = :user_id;
```
**Index used**: id (primary key) + user_id

### Data Integrity Constraints

1. **Foreign Key Constraint**:
   - `tasks.user_id` REFERENCES `users.id`
   - ON DELETE: CASCADE (if user deleted, delete all their tasks)
   - ON UPDATE: CASCADE (if user_id changes, update tasks)

2. **Check Constraints**:
   - title: `LENGTH(title) > 0 AND LENGTH(title) <= 200`
   - description: `description IS NULL OR LENGTH(description) <= 2000`
   - priority: `priority IN ('low', 'medium', 'high')`
   - status: `status IN ('pending', 'completed')`

3. **NOT NULL Constraints**:
   - id, user_id, title, priority, status, created_at, updated_at

---

## SQLModel Implementation

### Task Model Definition

```python
# models/task.py
from sqlmodel import SQLModel, Field, Index
from datetime import datetime, date
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum

class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Status(str, Enum):
    """Task completion status."""
    PENDING = "pending"
    COMPLETED = "completed"

class TaskBase(SQLModel):
    """Base task fields (shared between models)."""
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.PENDING)

class Task(TaskBase, table=True):
    """Task ORM model (database table)."""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Composite indexes for efficient queries
    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
        Index("idx_user_due_date", "user_id", "due_date"),
    )

class TaskCreate(TaskBase):
    """Schema for creating a task (API request)."""
    pass  # Inherits from TaskBase, no id or user_id

class TaskUpdate(SQLModel):
    """Schema for updating a task (API request - all optional)."""
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = None
    priority: Optional[Priority] = None

class TaskRead(TaskBase):
    """Schema for reading a task (API response)."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
```

---

## Database Schema (SQL)

### Create Users Table
```sql
-- Managed by Better-Auth, included here for reference
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Hashed
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### Create Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL CHECK (LENGTH(title) > 0),
    description VARCHAR(2000),
    due_date DATE,
    priority VARCHAR(10) NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high')),
    status VARCHAR(10) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'completed')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date);

-- Updated timestamp trigger (PostgreSQL)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Summary

### Key Design Decisions

1. **User Table Managed by Better-Auth**: Simplifies authentication, no custom user management needed
2. **UUID Primary Keys**: Globally unique, no collisions in distributed systems
3. **Composite Indexes**: Optimizes most common query patterns (user-scoped + filtered/sorted)
4. **Enum Types**: Type-safe priority and status values, prevents invalid data
5. **Timestamp Triggers**: Automatic updated_at refresh on every update
6. **Foreign Key Cascade**: User deletion automatically removes their tasks
7. **Check Constraints**: Database-level validation as safety net

### Data Flow

1. User signs up via Better-Auth → `users` table entry created
2. User logs in → JWT issued with user_id
3. User creates task → JWT validated, task inserted with `tasks.user_id = jwt.user_id`
4. User lists tasks → Query filtered by `tasks.user_id = jwt.user_id`
5. User updates/completes/deletes task → Ownership verified (`tasks.user_id = jwt.user_id`)

### Security Guarantees

- **User Isolation**: Every task query includes `WHERE user_id = :user_id`
- **No Cross-User Access**: Attempting to access another user's task returns 403 Forbidden
- **JWT Validation**: All task operations require valid JWT with user_id claim
- **Database Constraints**: Foreign key prevents orphaned tasks

This data model satisfies all Phase 2 constitution requirements for user authentication, task management, and data isolation.
