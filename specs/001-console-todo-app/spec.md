# Feature Specification: Phase 1 Console-Based Todo Application

**Feature Branch**: `001-console-todo-app`
**Created**: 2025-12-09
**Status**: Draft
**Input**: User description: "Phase 1 — Todo In-Memory Python Console App - Build a command-line todo application that stores tasks in memory using Claude Code and Spec-Kit Plus"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Manage Tasks (Priority: P1)

As a user, I want to create new tasks with a title and optional details so that I can track my work items in a simple console interface.

**Why this priority**: Task creation is the foundation of the application. Without the ability to create tasks, no other functionality has value. This represents the absolute minimum viable product.

**Independent Test**: Can be fully tested by launching the console app, selecting "Add Task", providing a title, and verifying the task appears with a generated UUID, status "pending", and timestamps. Delivers immediate value by allowing users to capture tasks.

**Acceptance Scenarios**:

1. **Given** the console menu is displayed, **When** I select "Add Task" and provide a title "Buy groceries", **Then** a new task is created with status "pending", a UUID is generated, created_at and updated_at timestamps are set to current time, and priority defaults to "medium"
2. **Given** I'm creating a task, **When** I provide title "Project review" and description "Review Q4 deliverables", **Then** both fields are stored correctly and retrievable
3. **Given** I'm creating a task, **When** I provide title "Team meeting", due_date "2025-12-15", and priority "high", **Then** all fields are stored with the specified values
4. **Given** I'm creating a task, **When** I provide an empty title, **Then** the system displays error "Title is required" and re-prompts for input
5. **Given** I'm creating a task, **When** I provide an invalid date format "tomorrow" for due_date, **Then** the system displays error "Date must be in ISO format YYYY-MM-DD" and re-prompts

---

### User Story 2 - View and Filter Tasks (Priority: P1)

As a user, I want to view my tasks with sorting and filtering options so that I can focus on what's most important or urgent.

**Why this priority**: Viewing tasks is essential for the application to be useful. Creating tasks without the ability to see them provides no value. This completes the minimal viable product when combined with creation.

**Independent Test**: Can be fully tested by creating 3-5 tasks with different priorities, statuses, and due dates, then using the "List Tasks" menu to apply various filters (pending only, completed only) and sorts (by priority, by due date, by status). Delivers value by helping users organize their workload.

**Acceptance Scenarios**:

1. **Given** I have created 5 tasks with mixed statuses, **When** I select "List Tasks" with filter "pending", **Then** only tasks with status "pending" are displayed
2. **Given** I have tasks with different priorities, **When** I select "List Tasks" with sort "priority", **Then** tasks are displayed in order: high, medium, low
3. **Given** I have tasks with various due dates, **When** I select "List Tasks" with sort "due_date", **Then** tasks are displayed chronologically with overdue tasks highlighted
4. **Given** I have no tasks, **When** I select "List Tasks", **Then** the system displays "No tasks found"
5. **Given** I have 10 tasks, **When** I select "List Tasks" with no filters, **Then** all tasks are displayed with their UUID (first 8 chars), title, priority, status, and due_date in a formatted table

---

### User Story 3 - Update Task Details (Priority: P2)

As a user, I want to update task details so that I can keep my tasks accurate as circumstances change.

**Why this priority**: While not essential for MVP, the ability to update tasks significantly improves usability. Users need to adjust priorities, extend due dates, or clarify descriptions as projects evolve.

**Independent Test**: Can be fully tested by creating a task, then using the "Update Task" menu to modify its title, description, priority, or due_date, and verifying the changes persist and updated_at timestamp is refreshed. Delivers value by allowing task management to adapt to changing priorities.

**Acceptance Scenarios**:

1. **Given** I have a task with title "Buy groceries", **When** I select "Update Task", provide the task UUID, and change the title to "Buy groceries and supplies", **Then** the title is updated and updated_at timestamp is refreshed
2. **Given** I have a task with priority "low", **When** I update its priority to "high", **Then** the priority changes and the task appears higher in priority-sorted lists
3. **Given** I have a task with due_date "2025-12-10", **When** I update the due_date to "2025-12-20", **Then** the new due date is stored and reflected in due-date-sorted lists
4. **Given** I have a task with no description, **When** I update it to add description "Need milk, bread, eggs", **Then** the description is stored and displayed when viewing the task
5. **Given** I provide an invalid UUID "abc123", **When** I attempt to update a task, **Then** the system displays error "Task not found" and returns to menu

---

### User Story 4 - Mark Tasks as Complete (Priority: P2)

As a user, I want to mark tasks as complete so that I can track my progress and distinguish finished work from pending items.

**Why this priority**: Completion tracking provides motivation and clarity about work progress. While users can work without this feature, it significantly improves the user experience and task management effectiveness.

**Independent Test**: Can be fully tested by creating a pending task, using the "Complete Task" menu option to mark it complete, then filtering by status to verify it no longer appears in pending lists but does appear in completed lists. Delivers value by providing a sense of accomplishment and clear task status.

**Acceptance Scenarios**:

1. **Given** I have a task with status "pending", **When** I select "Complete Task" and provide its UUID, **Then** the status changes to "completed" and updated_at timestamp is refreshed
2. **Given** I have a completed task, **When** I filter tasks by "pending", **Then** the completed task does not appear in the results
3. **Given** I have a completed task, **When** I filter tasks by "completed", **Then** the task appears in the results
4. **Given** I have a task already marked "completed", **When** I attempt to mark it complete again, **Then** the system displays message "Task is already completed" but does not error
5. **Given** I provide an invalid UUID, **When** I attempt to complete a task, **Then** the system displays error "Task not found" and returns to menu

---

### User Story 5 - Delete Tasks (Priority: P3)

As a user, I want to delete tasks so that I can remove items that are no longer relevant or were created by mistake.

**Why this priority**: Deletion is useful for maintaining a clean task list but is not essential for core functionality. Users can work effectively even if they cannot delete tasks, though it improves long-term usability.

**Independent Test**: Can be fully tested by creating a task, using the "Delete Task" menu to remove it by UUID, then attempting to view or update the deleted task to confirm it no longer exists. Delivers value by preventing clutter and allowing correction of mistakes.

**Acceptance Scenarios**:

1. **Given** I have a task with UUID "abc-123", **When** I select "Delete Task" and provide the UUID, **Then** I am prompted "Are you sure you want to delete this task? (yes/no)"
2. **Given** I am prompted to confirm deletion, **When** I type "yes", **Then** the task is removed from storage and a confirmation message "Task deleted successfully" is displayed
3. **Given** I am prompted to confirm deletion, **When** I type "no", **Then** the deletion is cancelled and the task remains in storage
4. **Given** I have deleted a task with UUID "abc-123", **When** I attempt to view or update that UUID, **Then** the system displays error "Task not found"
5. **Given** I provide an invalid UUID, **When** I attempt to delete a task, **Then** the system displays error "Task not found" and returns to menu

---

### Edge Cases

- What happens when a user enters a due_date in the past? System accepts it but marks the task as "overdue" when filtering by due date
- What happens when storage contains 1000+ tasks? System performs well for in-memory operations but may have slower display times (acceptable for Phase 1)
- What happens when a user provides extremely long input (10,000 character title)? System truncates display to 100 characters with "..." but stores full content
- What happens when a user provides special characters or emojis in task fields? System accepts and displays them correctly (UTF-8 support)
- What happens when a user types "quit" during task creation prompts? System cancels the operation and returns to main menu
- What happens when system date/time changes during runtime? Timestamps reflect system time at moment of creation/update (no timezone handling in Phase 1)
- What happens when a user types invalid menu options (e.g., "7" when only 1-6 exist)? System displays error "Invalid option. Please enter a number between 1 and 6" and re-displays menu

## Requirements *(mandatory)*

### Functional Requirements

#### Task Creation
- **FR-001**: System MUST allow users to create new tasks with a required title field (1-200 characters)
- **FR-002**: System MUST support optional task fields: description (up to 2000 characters), due_date (ISO 8601 format YYYY-MM-DD), priority (low/medium/high)
- **FR-003**: System MUST auto-generate a unique UUID for each task upon creation
- **FR-004**: System MUST auto-set created_at and updated_at timestamps to current system time on task creation
- **FR-005**: System MUST default priority to "medium" and status to "pending" if not specified

#### Task Retrieval
- **FR-006**: System MUST provide a "List Tasks" command that displays all tasks by default
- **FR-007**: System MUST support filtering tasks by status (pending, completed)
- **FR-008**: System MUST support filtering tasks by priority (low, medium, high)
- **FR-009**: System MUST support filtering tasks by overdue status (due_date < current date and status = pending)
- **FR-010**: System MUST support sorting tasks by priority (high → medium → low)
- **FR-011**: System MUST support sorting tasks by due_date (earliest first, then null dates)
- **FR-012**: System MUST support sorting tasks by status (pending first, then completed)
- **FR-013**: System MUST display task UUID (first 8 characters), title (truncated to 50 chars), priority, status, and due_date in list view

#### Task Update
- **FR-014**: System MUST allow users to update any task field (title, description, due_date, priority) by providing the task UUID
- **FR-015**: System MUST update the updated_at timestamp whenever a task is modified
- **FR-016**: System MUST validate updated field values according to the same rules as creation (e.g., title required, date format)
- **FR-017**: System MUST return error "Task not found" if provided UUID does not match any existing task

#### Task Completion
- **FR-018**: System MUST allow users to mark a task as completed by providing its UUID
- **FR-019**: System MUST change status from "pending" to "completed" and update updated_at timestamp
- **FR-020**: System MUST allow marking an already completed task as completed without error (idempotent operation)

#### Task Deletion
- **FR-021**: System MUST prompt for confirmation before deleting a task (destructive action)
- **FR-022**: System MUST accept "yes" or "y" (case-insensitive) to confirm deletion
- **FR-023**: System MUST accept "no" or "n" (case-insensitive) to cancel deletion
- **FR-024**: System MUST permanently remove the task from in-memory storage upon confirmed deletion
- **FR-025**: System MUST return error "Task not found" if provided UUID does not match any existing task

#### Console Interface
- **FR-026**: System MUST display a main menu with numbered options: 1) Add Task, 2) List Tasks, 3) Update Task, 4) Complete Task, 5) Delete Task, 6) Exit
- **FR-027**: System MUST accept numeric input (1-6) to navigate menu options
- **FR-028**: System MUST display clear prompts for each user input (e.g., "Enter task title: ")
- **FR-029**: System MUST return to main menu after completing each operation
- **FR-030**: System MUST exit cleanly when user selects "Exit" option, displaying "Goodbye!" message

### Key Entities

- **Task**: Represents a single todo item with:
  - `id` (UUID, auto-generated, immutable)
  - `title` (string, required, 1-200 chars)
  - `description` (string, optional, up to 2000 chars)
  - `due_date` (ISO 8601 date string YYYY-MM-DD, optional)
  - `priority` (enum: "low", "medium", "high", defaults to "medium")
  - `status` (enum: "pending", "completed", defaults to "pending")
  - `created_at` (ISO 8601 datetime, auto-set on creation)
  - `updated_at` (ISO 8601 datetime, auto-updated on modification)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a new task in under 30 seconds from menu selection to confirmation
- **SC-002**: Users can view all tasks with filters applied in under 5 seconds (for up to 100 tasks)
- **SC-003**: Users can update any task field in under 45 seconds (locate task, modify field, confirm)
- **SC-004**: Users can mark a task as complete in under 20 seconds (locate task, confirm completion)
- **SC-005**: Users can delete a task in under 30 seconds including confirmation step
- **SC-006**: System displays clear error messages for 100% of invalid inputs (empty title, bad date format, invalid UUID, etc.)
- **SC-007**: System prevents crashes or unhandled exceptions for all user inputs (including edge cases)
- **SC-008**: Console output is readable and well-formatted (aligned columns, clear headers, no text overflow)
- **SC-009**: Users can independently test each of the 5 user stories without dependencies on other stories
- **SC-010**: System handles 500 tasks in memory without noticeable performance degradation (< 1 second for list operations)
- **SC-011**: System resets to empty state on each program restart (no persistence between runs)
- **SC-012**: All menu navigation flows return to main menu (no dead-ends or forced exits except via Exit option)

### Quality Measures

- **Test Coverage**: Minimum 80% code coverage with pytest
- **Type Safety**: 100% type hint coverage with mypy strict mode, zero type errors
- **Code Quality**: Zero ruff linting errors, consistent formatting
- **Console UX**: Clear instructions, helpful error messages, logical menu flow, confirmation on destructive actions
- **Architecture**: Layered design (domain, services, storage, commands) allowing easy migration to Phase 2 (FastAPI + database)

## Constraints

- **Technical**: Python 3.13+, UV package manager, in-memory storage only (Python lists/dicts)
- **No Persistence**: Data MUST reset on program restart (no files, JSON, databases)
- **No External APIs**: No network calls, no external services
- **Console Only**: Text-based interface using stdin/stdout (no GUI, no web interface)
- **Minimal Dependencies**: Use Python standard library where possible; pytest, ruff, mypy allowed for testing/quality only
- **Deterministic**: All operations must be repeatable and testable (no random behavior except UUID generation)

## Out of Scope (Phase 1)

The following are explicitly excluded from Phase 1 and deferred to future phases:

- ❌ Persistent storage (files, JSON, databases)
- ❌ FastAPI / REST API backend
- ❌ Web frontend (Next.js or any UI framework)
- ❌ User authentication or authorization
- ❌ Multi-user support or concurrency
- ❌ Database integration (Postgres, SQLite, etc.)
- ❌ AI chatbot or MCP agent features
- ❌ Cloud deployment (Docker, Kubernetes)
- ❌ Network features (webhooks, notifications, sync)
- ❌ Advanced features (recurring tasks, subtasks, tags, attachments)

## Evolution Notes

This Phase 1 specification is designed for forward compatibility with Phase 2 (FastAPI + Database):

- **Domain Model**: Task entity can map directly to database schema (ORM model)
- **Service Layer**: CRUD operations in services/ can move into FastAPI route handlers
- **Storage Layer**: In-memory repository can be swapped for database repository with same interface
- **Console UI**: Can be deprecated but remain runnable alongside API

Constitutional principles from `.specify/memory/constitution.md` require:
- Mandatory folder structure: `commands/`, `domain/`, `services/`, `storage/`, `utils/`
- Layered architecture with clear separation of concerns
- No persistence logic in Phase 1 (RAM only)
- All changes must allow Phase 2 storage layer replacement without breaking service/domain layers
