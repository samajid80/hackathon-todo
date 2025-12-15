# Quickstart & Acceptance Test Scenarios

**Feature**: 002-fullstack-web-app
**Date**: 2025-12-11
**Phase**: 1 (Design & Contracts)

## Overview

This document provides manual acceptance test scenarios that validate the Phase 2 implementation against the feature specification. Each scenario can be executed independently to verify specific functionality.

---

## Setup Prerequisites

Before running acceptance tests:

1. **Backend running**: `cd backend && uvicorn main:app --reload` (http://localhost:8000)
2. **Frontend running**: `cd frontend && npm run dev` (http://localhost:3000)
3. **Database**: Neon PostgreSQL connection configured and tables created
4. **Environment**: JWT_SECRET configured in both frontend and backend

---

## Scenario 1: User Signup and Login Flow

**Priority**: P1 (Critical)
**User Story**: User Account Creation and Authentication
**Estimated Duration**: 2-3 minutes

### Test Steps

1. Open browser and navigate to `http://localhost:3000`
2. **EXPECT**: Redirected to `/login` page (unauthenticated)

3. Click "Sign Up" link or navigate to `/signup`
4. Fill in signup form:
   - Email: `test@example.com`
   - Password: `password123`
5. Click "Sign Up" button
6. **EXPECT**: Account created successfully
7. **EXPECT**: Automatically logged in
8. **EXPECT**: Redirected to `/tasks` page
9. **EXPECT**: JWT token stored in session/cookie
10. **EXPECT**: Empty task list with message "No tasks yet. Create your first task to get started"

11. Click "Logout" button in navigation
12. **EXPECT**: Session terminated
13. **EXPECT**: Redirected to `/login` page

14. Enter login credentials:
    - Email: `test@example.com`
    - Password: `password123`
15. Click "Login" button
16. **EXPECT**: Successfully authenticated
17. **EXPECT**: Redirected to `/tasks` page
18. **EXPECT**: JWT token renewed in session

### Edge Cases

- **Duplicate email**: Try signing up with `test@example.com` again
  - **EXPECT**: Error message "Account already exists"
  - **EXPECT**: Form not submitted, remain on signup page

- **Invalid email format**: Try `notanemail`
  - **EXPECT**: Validation error "Please enter a valid email address"

- **Short password**: Try `pass123` (7 characters)
  - **EXPECT**: Validation error "Password must be at least 8 characters"

- **Wrong password**: Try logging in with `wrongpassword`
  - **EXPECT**: Error message "Invalid email or password"
  - **EXPECT**: Remain on login page

---

## Scenario 2: Create and View Task

**Priority**: P1 (Critical)
**User Story**: Create and View Tasks
**Estimated Duration**: 2-3 minutes

### Test Steps

1. Ensure logged in from Scenario 1
2. Navigate to `/tasks` page
3. Click "Create Task" or "New Task" button
4. **EXPECT**: Navigated to `/tasks/new` page

5. Fill in minimal task form:
   - Title: `Buy groceries`
   - Leave other fields empty
6. Click "Create" button
7. **EXPECT**: Task created successfully
8. **EXPECT**: Redirected to `/tasks` page
9. **EXPECT**: Success message "Task created successfully"
10. **EXPECT**: New task visible in list with:
    - Title: "Buy groceries"
    - Priority: "medium" (default)
    - Status: "pending" (default)
    - Due date: (none/empty)

11. Click "Create Task" again
12. Fill in complete task form:
    - Title: `Project review`
    - Description: `Review Q4 deliverables`
    - Due date: Select tomorrow's date
    - Priority: Select "high"
13. Click "Create" button
14. **EXPECT**: Task created successfully
15. **EXPECT**: New task visible with all fields populated
16. **EXPECT**: High priority indicator visible (red badge/color)
17. **EXPECT**: Due date displayed correctly

18. **EXPECT**: Task list shows 2 tasks total
19. **EXPECT**: Tasks ordered by creation date (newest first by default)

### Edge Cases

- **Empty title**: Try creating task without title
  - **EXPECT**: Validation error "Title is required"
  - **EXPECT**: Form not submitted

- **Title too long**: Try title with 201 characters
  - **EXPECT**: Validation error "Title must be 200 characters or less"

- **Invalid date format**: Manually enter invalid date in field
  - **EXPECT**: Browser date picker prevents invalid input OR validation error

- **Past due date**: Select yesterday's date
  - **EXPECT**: Task created successfully (allowed)
  - **EXPECT**: Task immediately shows as overdue in overdue filter

---

## Scenario 3: Filter and Sort Tasks

**Priority**: P2 (Important)
**User Story**: Filter and Sort Tasks
**Estimated Duration**: 3-4 minutes

### Test Steps (Preparation)

1. Create 5 diverse tasks:
   - Task A: "Morning jog", priority: low, status: pending, due: tomorrow
   - Task B: "Client meeting", priority: high, status: pending, due: today
   - Task C: "Code review", priority: medium, status: completed, due: yesterday
   - Task D: "Grocery shopping", priority: medium, status: pending, due: (none)
   - Task E: "Report submission", priority: high, status: pending, due: 2 days ago (overdue)

### Test Steps (Filtering)

2. On `/tasks` page, click "Pending" filter button
3. **EXPECT**: Only tasks with status "pending" displayed (A, B, D, E)
4. **EXPECT**: Completed task (C) hidden

5. Click "Completed" filter button
6. **EXPECT**: Only tasks with status "completed" displayed (C)
7. **EXPECT**: Pending tasks (A, B, D, E) hidden

8. Click "Overdue" filter button
9. **EXPECT**: Only tasks with due_date < today AND status = pending displayed (E)
10. **EXPECT**: Task E has visual overdue indicator (red border/badge/text)

11. Click "All" or "Clear Filters" button
12. **EXPECT**: All 5 tasks visible again

### Test Steps (Sorting)

13. Click "Sort by Priority" dropdown or button
14. **EXPECT**: Tasks ordered: high (B, E) → medium (C, D) → low (A)

15. Click "Sort by Due Date" dropdown or button
16. **EXPECT**: Tasks ordered chronologically:
    - E (2 days ago)
    - C (yesterday)
    - B (today)
    - A (tomorrow)
    - D (no due date - at end)

17. Click "Sort by Status" dropdown or button
18. **EXPECT**: Tasks grouped:
    - Pending tasks first (A, B, D, E)
    - Completed tasks second (C)

### Edge Cases

- **Multiple filters active**: Try applying both filter and sort
  - Click "Pending" filter + "Sort by Priority"
  - **EXPECT**: Only pending tasks shown, sorted by priority

- **Empty filter result**: Delete all completed tasks, then click "Completed" filter
  - **EXPECT**: Empty state message "No completed tasks"

---

## Scenario 4: Update and Complete Task

**Priority**: P2 (Important)
**User Story**: Update and Complete Tasks
**Estimated Duration**: 3-4 minutes

### Test Steps (Update)

1. From `/tasks` page, find a pending task
2. Click "Edit" button/icon on the task
3. **EXPECT**: Navigated to `/tasks/{id}/edit` page
4. **EXPECT**: Form pre-filled with current task values

5. Modify the title: "Buy groceries and supplies"
6. Modify the priority: Change from "medium" to "high"
7. Modify the due date: Change to 3 days from now
8. Add description: "Need milk, bread, eggs, and cleaning supplies"
9. Click "Save Changes" button

10. **EXPECT**: Task updated successfully
11. **EXPECT**: Redirected to `/tasks` page
12. **EXPECT**: Success message "Task updated successfully"
13. **EXPECT**: Updated values visible in task list
14. **EXPECT**: High priority indicator now shown
15. **EXPECT**: Due date changed to new value

16. Refresh the page (F5)
17. **EXPECT**: Updated values persist (database-backed)

### Test Steps (Complete)

18. Find a pending task in the list
19. Click "Mark Complete" button on the task
20. **EXPECT**: Task status changes to "completed" immediately
21. **EXPECT**: Visual indicator changes (green badge, strikethrough, etc.)
22. **EXPECT**: Success message "Task marked as completed"

23. Click "Completed" filter
24. **EXPECT**: Completed task now appears in this view

25. Click "Mark Complete" button on the same task again
26. **EXPECT**: Task remains completed (idempotent - no error)
27. **EXPECT**: No duplicate "completed" status

### Edge Cases

- **Update with empty title**: Try removing title and saving
  - **EXPECT**: Validation error "Title is required"
  - **EXPECT**: Changes not saved

- **Update another user's task**: Manually navigate to `/tasks/{other-user-task-id}/edit`
  - **EXPECT**: 403 Forbidden error OR redirect to tasks list
  - **EXPECT**: Error message "Access denied"

- **Update nonexistent task**: Navigate to `/tasks/00000000-0000-0000-0000-000000000000/edit`
  - **EXPECT**: 404 Not Found error
  - **EXPECT**: Error message "Task not found"

---

## Scenario 5: Delete Task with Confirmation

**Priority**: P3 (Nice to have)
**User Story**: Delete Tasks
**Estimated Duration**: 2-3 minutes

### Test Steps

1. From `/tasks` page, find a task to delete
2. Click "Delete" button/icon on the task
3. **EXPECT**: Confirmation modal/dialog appears
4. **EXPECT**: Message: "Are you sure you want to delete this task?"
5. **EXPECT**: Two buttons: "Cancel" and "Delete" (or "Yes"/"No")

6. Click "Cancel" button
7. **EXPECT**: Modal closes
8. **EXPECT**: Task still visible in list (not deleted)

9. Click "Delete" button/icon again on the same task
10. **EXPECT**: Confirmation modal appears again
11. Click "Delete" (or "Yes") button
12. **EXPECT**: Task permanently removed from list
13. **EXPECT**: Success message "Task deleted successfully"
14. **EXPECT**: Task no longer visible in any filter view

15. Refresh page (F5)
16. **EXPECT**: Deleted task does not reappear (database-backed)

17. Try manually navigating to deleted task's URL: `/tasks/{deleted-task-id}/edit`
18. **EXPECT**: 404 Not Found error
19. **EXPECT**: Error message "Task not found"

### Edge Cases

- **Delete another user's task**: Attempt to delete task belonging to different user
  - **EXPECT**: 403 Forbidden error
  - **EXPECT**: Error message "Access denied"
  - **EXPECT**: Task not deleted

- **Delete nonexistent task**: Attempt to delete already-deleted or invalid ID
  - **EXPECT**: 404 Not Found error
  - **EXPECT**: Error message "Task not found"

---

## Scenario 6: User Data Isolation

**Priority**: P1 (Critical - Security)
**User Story**: User Account Creation and Authentication
**Estimated Duration**: 3-4 minutes

### Test Steps

1. Create first user account:
   - Email: `user1@example.com`
   - Password: `password123`
2. Create 2-3 tasks as User 1
3. Note task IDs (visible in URL or developer tools)
4. Logout

5. Create second user account:
   - Email: `user2@example.com`
   - Password: `password123`
6. Login as User 2
7. **EXPECT**: Task list is empty (User 2 has no tasks)
8. **EXPECT**: User 1's tasks NOT visible

9. Create 1-2 tasks as User 2
10. **EXPECT**: Only User 2's tasks visible

11. Attempt to access User 1's task by URL:
    - Navigate to `/tasks/{user1-task-id}/edit`
12. **EXPECT**: 403 Forbidden error OR redirect to task list
13. **EXPECT**: Error message "Access denied"
14. **EXPECT**: Task details not revealed

15. Logout as User 2
16. Login as User 1
17. **EXPECT**: Only User 1's tasks visible
18. **EXPECT**: User 2's tasks NOT visible

### Edge Cases

- **API access without JWT**: Remove JWT from browser storage, try accessing `/tasks`
  - **EXPECT**: Redirected to login
  - **EXPECT**: Error message "Session expired" or "Authentication required"

- **Expired JWT**: Wait for JWT expiration (24 hours) or manually expire token
  - **EXPECT**: Redirected to login when attempting to access protected route
  - **EXPECT**: Error message "Session expired, please log in again"

---

## Scenario 7: Session Management

**Priority**: P1 (Critical)
**User Story**: User Account Creation and Authentication
**Estimated Duration**: 2-3 minutes

### Test Steps

1. Login as user: `test@example.com`
2. **EXPECT**: Redirected to `/tasks` page
3. **EXPECT**: JWT stored in session cookie

4. Open browser developer tools → Application/Storage → Cookies
5. **EXPECT**: Session cookie present with JWT value
6. **EXPECT**: Cookie has `HttpOnly` flag (more secure)

7. Navigate to protected route: `/tasks/new`
8. **EXPECT**: Page loads successfully (authenticated)

9. Open new browser tab/window (same browser)
10. Navigate to `http://localhost:3000/tasks`
11. **EXPECT**: Authenticated automatically (session shared across tabs)
12. **EXPECT**: Same JWT used

13. In original tab, click "Logout"
14. **EXPECT**: Redirected to login
15. Switch to second tab, refresh page
16. **EXPECT**: Session terminated in second tab too
17. **EXPECT**: Redirected to login

18. Close browser completely
19. Reopen browser and navigate to `http://localhost:3000/tasks`
20. **EXPECT**: Session expired (cookie not persisted)
21. **EXPECT**: Redirected to login

### Edge Cases

- **Session hijacking prevention**: Cannot manually forge JWT
- **XSS protection**: JWT in HttpOnly cookie, not accessible via JavaScript

---

## Scenario 8: Responsive UI (Mobile to Desktop)

**Priority**: P2 (Important)
**User Story**: Create and View Tasks (UX requirement)
**Estimated Duration**: 3-4 minutes

### Test Steps (Mobile - 375px width)

1. Open browser developer tools → Responsive Design Mode
2. Set viewport to 375px × 667px (iPhone SE)
3. Navigate to `/tasks` page while logged in

4. **EXPECT**: Task list displays as cards (vertical stack)
5. **EXPECT**: Each card shows title, priority badge, due date, status
6. **EXPECT**: Action buttons (Edit, Complete, Delete) visible
7. **EXPECT**: No horizontal scrolling
8. **EXPECT**: Text readable without zooming

9. Navigate to `/tasks/new` (create task form)
10. **EXPECT**: Form fields stack vertically
11. **EXPECT**: Input fields full width
12. **EXPECT**: Date picker accessible via touch
13. **EXPECT**: Submit button full width at bottom

### Test Steps (Tablet - 768px width)

14. Resize viewport to 768px × 1024px (iPad)
15. **EXPECT**: Task list still displays as cards
16. **EXPECT**: 2 cards per row (grid layout)
17. **EXPECT**: All functionality accessible

### Test Steps (Desktop - 1920px width)

18. Resize viewport to 1920px × 1080px (desktop)
19. **EXPECT**: Task list displays as table (desktop view)
20. **EXPECT**: Columns: Title, Priority, Due Date, Status, Actions
21. **EXPECT**: All data visible without wrapping
22. **EXPECT**: Hover effects on rows
23. **EXPECT**: Efficient use of space

### Edge Cases

- **320px width**: Test minimum supported width
  - **EXPECT**: Still usable (very narrow but functional)

- **2560px width**: Test maximum expected width
  - **EXPECT**: Content centered or max-width container
  - **EXPECT**: Not stretched to full width

---

## Pass/Fail Criteria

### Critical (Must Pass)
- ✅ Scenario 1: User Signup and Login Flow
- ✅ Scenario 2: Create and View Task
- ✅ Scenario 6: User Data Isolation

### Important (Should Pass)
- ✅ Scenario 3: Filter and Sort Tasks
- ✅ Scenario 4: Update and Complete Task
- ✅ Scenario 7: Session Management
- ✅ Scenario 8: Responsive UI

### Nice to Have (Can be deferred)
- ✅ Scenario 5: Delete Task with Confirmation

---

## Notes for Testers

- **Browser**: Test on latest Chrome, Firefox, Safari, Edge
- **Clean state**: Start with fresh database for consistent results
- **JWT expiration**: Default 24 hours, test expiration by manually changing exp claim
- **Network errors**: Simulate by stopping backend server during task operations
- **Console errors**: Monitor browser console for unexpected errors/warnings

---

## Success Criteria

Phase 2 acceptance testing is complete when:
1. All Critical scenarios pass without errors
2. All Important scenarios pass with documented edge cases
3. User data isolation verified with multiple user accounts
4. Responsive UI tested at 320px, 768px, and 1920px viewports
5. No JavaScript console errors during normal operation
6. All edge cases handled gracefully with clear error messages
