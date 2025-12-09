# Quickstart Guide: Phase 1 Console-Based Todo Application

**Feature**: 001-console-todo-app
**Date**: 2025-12-09
**Purpose**: Manual testing scenarios for all 5 user stories

## Overview

This document provides step-by-step manual testing scenarios for validating the Phase 1 todo application. Each scenario corresponds to a user story from the specification and can be executed independently.

---

## Setup

### Prerequisites
- Python 3.13 installed
- UV package manager configured
- Phase 1 code implemented in `phase1/src/`

### Installation

```bash
cd phase1
python3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync  # Install dependencies from pyproject.toml
```

### Running the Application

```bash
cd phase1
python src/main.py
```

You should see the main menu:
```
=== Todo Application ===
1. Add Task
2. List Tasks
3. Update Task
4. Complete Task
5. Delete Task
6. Exit

Select option:
```

---

## Test Scenario 1: Create and Manage Tasks (P1)

**User Story**: As a user, I want to create new tasks with a title and optional details so that I can track my work items in a simple console interface.

### Test Case 1.1: Create Task with Title Only

**Steps**:
1. Launch application: `python src/main.py`
2. Select option `1` (Add Task)
3. Enter title: `Buy groceries`
4. Leave description blank (press Enter)
5. Leave due_date blank (press Enter)
6. Leave priority blank (press Enter to accept default "medium")

**Expected Result**:
- Task created successfully message appears
- Task ID displayed (first 8 characters of UUID, e.g., `a3f2b1c4`)
- Task has default priority "medium" and status "pending"
- `created_at` and `updated_at` timestamps set to current time

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 1, Acceptance Scenario 1)

---

### Test Case 1.2: Create Task with All Fields

**Steps**:
1. Select option `1` (Add Task)
2. Enter title: `Team meeting`
3. Enter description: `Discuss Q4 deliverables`
4. Enter due_date: `2025-12-15`
5. Enter priority: `high`

**Expected Result**:
- Task created successfully message appears
- Task ID displayed
- All fields stored correctly (verify with List Tasks)

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 1, Acceptance Scenario 3)

---

### Test Case 1.3: Validation - Empty Title

**Steps**:
1. Select option `1` (Add Task)
2. Enter empty title (press Enter without typing)

**Expected Result**:
- Error message: `✗ Error: Title is required`
- User re-prompted for title
- Application does not crash

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 1, Acceptance Scenario 4)

---

### Test Case 1.4: Validation - Invalid Date Format

**Steps**:
1. Select option `1` (Add Task)
2. Enter title: `Project deadline`
3. Leave description blank
4. Enter due_date: `tomorrow` (invalid format)

**Expected Result**:
- Error message: `✗ Error: Date must be in ISO format YYYY-MM-DD`
- User re-prompted for due_date
- Application does not crash

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 1, Acceptance Scenario 5)

---

## Test Scenario 2: View and Filter Tasks (P1)

**User Story**: As a user, I want to view my tasks with sorting and filtering options so that I can focus on what's most important or urgent.

### Preparation: Create Sample Tasks

Before testing this scenario, create 5 tasks with different properties:

```
Task 1: "Buy groceries" | priority: high | status: pending | due_date: 2025-12-10
Task 2: "Team meeting" | priority: medium | status: pending | due_date: 2025-12-15
Task 3: "Complete report" | priority: high | status: pending | due_date: 2025-12-08 (overdue!)
Task 4: "Read documentation" | priority: low | status: completed | due_date: None
Task 5: "Fix bug #123" | priority: medium | status: completed | due_date: 2025-12-12
```

---

### Test Case 2.1: Filter by Status - Pending Only

**Steps**:
1. Select option `2` (List Tasks)
2. When prompted for filter, enter: `pending`

**Expected Result**:
- Only tasks with status "pending" displayed (Task 1, 2, 3)
- Completed tasks (Task 4, 5) not shown
- Table format: columns for ID (8 chars), Title (50 chars), Priority, Status, Due Date

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 2, Acceptance Scenario 1)

---

### Test Case 2.2: Sort by Priority

**Steps**:
1. Select option `2` (List Tasks)
2. No filter (press Enter for "all")
3. When prompted for sort, enter: `priority`

**Expected Result**:
- Tasks displayed in order: HIGH → MEDIUM → LOW
- Order: Task 1 (high), Task 3 (high), Task 2 (medium), Task 5 (medium), Task 4 (low)

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 2, Acceptance Scenario 2)

---

### Test Case 2.3: Sort by Due Date with Overdue Highlight

**Steps**:
1. Select option `2` (List Tasks)
2. No filter
3. Sort by: `due_date`

**Expected Result**:
- Tasks displayed chronologically (earliest first)
- Order: Task 3 (2025-12-08), Task 1 (2025-12-10), Task 5 (2025-12-12), Task 2 (2025-12-15), Task 4 (no date)
- Overdue tasks highlighted (Task 3 shows "OVERDUE" indicator or special marker)

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 2, Acceptance Scenario 3)

---

### Test Case 2.4: No Tasks Found

**Steps**:
1. Delete all tasks (or start fresh application)
2. Select option `2` (List Tasks)

**Expected Result**:
- Message displayed: `No tasks found`
- No table headers shown
- Application returns to menu

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 2, Acceptance Scenario 4)

---

### Test Case 2.5: Display All Tasks (No Filters)

**Steps**:
1. Ensure 10 tasks exist (create if needed)
2. Select option `2` (List Tasks)
3. No filter, no sort (press Enter for defaults)

**Expected Result**:
- All 10 tasks displayed in table format
- Columns: UUID (8 chars), Title (truncated to 50 chars with "..."), Priority, Status, Due Date
- Aligned columns with clear headers

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 2, Acceptance Scenario 5)

---

## Test Scenario 3: Update Task Details (P2)

**User Story**: As a user, I want to update task details so that I can keep my tasks accurate as circumstances change.

### Preparation
Create a task to update:
```
Title: "Buy groceries" | priority: low | due_date: 2025-12-10 | description: ""
```

---

### Test Case 3.1: Update Title

**Steps**:
1. Select option `2` (List Tasks) to get task ID
2. Copy task ID (e.g., `a3f2b1c4`)
3. Select option `3` (Update Task)
4. Enter task ID: `a3f2b1c4`
5. Select field to update: `title`
6. Enter new title: `Buy groceries and supplies`

**Expected Result**:
- Success message: `✓ Task updated successfully`
- Title changed to new value
- `updated_at` timestamp refreshed
- Verify with List Tasks

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 3, Acceptance Scenario 1)

---

### Test Case 3.2: Update Priority

**Steps**:
1. Select option `3` (Update Task)
2. Enter task ID
3. Select field: `priority`
4. Enter new priority: `high`

**Expected Result**:
- Priority changed from "low" to "high"
- Task appears higher in priority-sorted lists
- `updated_at` timestamp refreshed

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 3, Acceptance Scenario 2)

---

### Test Case 3.3: Update Due Date

**Steps**:
1. Select option `3` (Update Task)
2. Enter task ID
3. Select field: `due_date`
4. Enter new due_date: `2025-12-20`

**Expected Result**:
- Due date changed from "2025-12-10" to "2025-12-20"
- Task position changes in due-date-sorted lists
- `updated_at` timestamp refreshed

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 3, Acceptance Scenario 3)

---

### Test Case 3.4: Update Description

**Steps**:
1. Select option `3` (Update Task)
2. Enter task ID
3. Select field: `description`
4. Enter description: `Need milk, bread, eggs`

**Expected Result**:
- Description added (was empty before)
- Stored and retrievable
- `updated_at` timestamp refreshed

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 3, Acceptance Scenario 4)

---

### Test Case 3.5: Validation - Invalid UUID

**Steps**:
1. Select option `3` (Update Task)
2. Enter invalid UUID: `abc123`

**Expected Result**:
- Error message: `✗ Error: Task not found`
- Returns to menu
- Application does not crash

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 3, Acceptance Scenario 5)

---

## Test Scenario 4: Mark Tasks as Complete (P2)

**User Story**: As a user, I want to mark tasks as complete so that I can track my progress and distinguish finished work from pending items.

### Preparation
Create a pending task:
```
Title: "Read documentation" | status: pending
```

---

### Test Case 4.1: Complete Pending Task

**Steps**:
1. Select option `2` (List Tasks) to get task ID
2. Copy task ID
3. Select option `4` (Complete Task)
4. Enter task ID

**Expected Result**:
- Success message: `✓ Task marked as completed`
- Status changed from "pending" to "completed"
- `updated_at` timestamp refreshed
- Verify with List Tasks (filter by "completed")

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 4, Acceptance Scenario 1)

---

### Test Case 4.2: Filter Verification - Pending List

**Steps**:
1. Mark task as completed (Task 1)
2. Select option `2` (List Tasks)
3. Filter by: `pending`

**Expected Result**:
- Completed task (Task 1) does NOT appear in results
- Only pending tasks shown

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 4, Acceptance Scenario 2)

---

### Test Case 4.3: Filter Verification - Completed List

**Steps**:
1. Select option `2` (List Tasks)
2. Filter by: `completed`

**Expected Result**:
- Completed task (Task 1) DOES appear in results
- Pending tasks not shown

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 4, Acceptance Scenario 3)

---

### Test Case 4.4: Idempotency - Complete Already Completed Task

**Steps**:
1. Select option `4` (Complete Task)
2. Enter ID of already completed task

**Expected Result**:
- Message: `Task is already completed` (informational, not error)
- No exception raised
- `updated_at` timestamp NOT refreshed (no change occurred)

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 4, Acceptance Scenario 4)

---

### Test Case 4.5: Validation - Invalid UUID

**Steps**:
1. Select option `4` (Complete Task)
2. Enter invalid UUID: `invalid-id`

**Expected Result**:
- Error message: `✗ Error: Task not found`
- Returns to menu
- Application does not crash

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 4, Acceptance Scenario 5)

---

## Test Scenario 5: Delete Tasks (P3)

**User Story**: As a user, I want to delete tasks so that I can remove items that are no longer relevant or were created by mistake.

### Preparation
Create a task to delete:
```
Title: "Old task to remove" | ID: (note the ID)
```

---

### Test Case 5.1: Delete Task with Confirmation

**Steps**:
1. Select option `2` (List Tasks) to get task ID
2. Copy task ID
3. Select option `5` (Delete Task)
4. Enter task ID
5. When prompted "Are you sure you want to delete this task? (yes/no)", enter: `yes`

**Expected Result**:
- Confirmation prompt appears before deletion
- After typing "yes", success message: `✓ Task deleted successfully`
- Task removed from storage
- Verify with List Tasks (task no longer appears)

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 5, Acceptance Scenarios 1 & 2)

---

### Test Case 5.2: Cancel Deletion

**Steps**:
1. Select option `5` (Delete Task)
2. Enter task ID
3. When prompted for confirmation, enter: `no`

**Expected Result**:
- Message: `Deletion cancelled`
- Task remains in storage (verify with List Tasks)

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 5, Acceptance Scenario 3)

---

### Test Case 5.3: Verify Task Deleted (Not Found)

**Steps**:
1. Delete a task (confirm with "yes")
2. Copy the deleted task ID
3. Try to update the deleted task (option `3`)
4. Enter deleted task ID

**Expected Result**:
- Error message: `✗ Error: Task not found`
- No exception raised

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 5, Acceptance Scenario 4)

---

### Test Case 5.4: Validation - Invalid UUID

**Steps**:
1. Select option `5` (Delete Task)
2. Enter invalid UUID: `nonexistent`

**Expected Result**:
- Error message: `✗ Error: Task not found`
- Returns to menu
- Application does not crash

**Acceptance Criteria**: ✅ Matches spec scenario (User Story 5, Acceptance Scenario 5)

---

## Edge Case Testing

### Edge Case 1: Past Due Date

**Steps**:
1. Create task with due_date: `2025-12-01` (in the past)
2. List tasks with filter: `overdue`

**Expected Result**:
- System accepts past date without error
- Task appears in "overdue" filter results
- Overdue indicator shown in list view

**Spec Reference**: Edge case (spec.md line 102)

---

### Edge Case 2: Large Dataset (500+ Tasks)

**Steps**:
1. Create 500 tasks (use script or loop)
2. Select option `2` (List Tasks)

**Expected Result**:
- List operation completes in < 1 second
- All tasks displayed (or paginated if implemented)
- No performance degradation

**Spec Reference**: Success criteria SC-010

---

### Edge Case 3: Long Input (10,000 Character Title)

**Steps**:
1. Create task with 10,000 character title (paste long text)

**Expected Result**:
- Validation error: `Title must be 200 characters or less`
- Application does not crash
- User re-prompted

**Spec Reference**: Edge case (spec.md line 104)

---

### Edge Case 4: Special Characters and Emojis

**Steps**:
1. Create task with title: `Buy groceries 🛒 & supplies (urgent!)`
2. List tasks

**Expected Result**:
- Title stored correctly with special characters and emojis
- UTF-8 encoding preserved
- Display shows characters correctly (if terminal supports Unicode)

**Spec Reference**: Edge case (spec.md line 105)

---

### Edge Case 5: Quit During Prompts

**Steps**:
1. Select option `1` (Add Task)
2. When prompted for title, type: `quit`

**Expected Result**:
- Operation cancelled
- Returns to main menu
- No task created
- Application does not crash

**Spec Reference**: Edge case (spec.md line 106)

---

### Edge Case 6: Invalid Menu Option

**Steps**:
1. At main menu, enter: `7` (invalid option, menu only has 1-6)

**Expected Result**:
- Error message: `✗ Invalid option. Please enter a number between 1 and 6`
- Menu re-displayed
- User re-prompted

**Spec Reference**: Edge case (spec.md line 108)

---

## Performance Testing

### Performance Test 1: Create Task Speed

**Steps**:
1. Time how long it takes to create a task from menu selection to confirmation
2. Repeat 10 times, take average

**Expected Result**:
- Average time < 30 seconds (user input time excluded, measure system response only)

**Spec Reference**: Success criteria SC-001

---

### Performance Test 2: View Tasks Speed

**Steps**:
1. Create 100 tasks
2. Time how long it takes to list all tasks with a filter applied

**Expected Result**:
- List operation completes in < 5 seconds

**Spec Reference**: Success criteria SC-002

---

## Exit and Restart Test

### Test: In-Memory Reset

**Steps**:
1. Create 5 tasks
2. Select option `6` (Exit)
3. Verify exit message: `Goodbye!`
4. Restart application: `python src/main.py`
5. Select option `2` (List Tasks)

**Expected Result**:
- Application exits cleanly without errors
- On restart, all tasks cleared (in-memory reset)
- Message: `No tasks found`

**Spec Reference**: Constitutional requirement §5.3, Success criteria SC-011

---

## Summary

**Total Test Scenarios**: 5 user stories
**Total Test Cases**: 30+ (including edge cases and performance tests)
**Manual Testing Time**: Approximately 30-45 minutes for full suite

**Next Steps After Manual Testing**:
1. Run automated pytest suite: `pytest tests/ --cov=src --cov-report=term-missing`
2. Verify 80% code coverage achieved
3. Run ruff linting: `ruff check src/`
4. Run mypy type checking: `mypy src/ --strict`

---

**Quickstart Guide Completed**: 2025-12-09
**Aligned with Spec**: ✅ All 5 user stories + edge cases + success criteria covered
**Ready for Implementation**: Yes
