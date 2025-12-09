# Tasks: Phase 1 Console-Based Todo Application

**Feature**: 001-console-todo-app
**Branch**: `001-console-todo-app`
**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Tests are NOT requested in the feature specification. Focus is on implementation with manual testing via quickstart.md scenarios. Test infrastructure will be created for future use.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **Checkbox**: Always `- [ ]` (markdown task checkbox)
- **[ID]**: Sequential task number (T001, T002, T003...)
- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5) - only for user story phases
- File paths included in descriptions for clarity

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure and basic configuration

- [X] T001 Create folder structure: phase1/src/{__init__.py, main.py, commands/, domain/, services/, storage/, utils/}
- [X] T002 Create test folder structure: phase1/tests/{__init__.py, test_domain/, test_services/, test_storage/, test_commands/, conftest.py}
- [X] T003 [P] Configure pyproject.toml with uv dependencies: pytest, pytest-cov, ruff, mypy
- [X] T004 [P] Create phase1/.python-version with content "3.13"
- [X] T005 [P] Create mypy.ini in phase1/ with strict mode configuration
- [X] T006 [P] Create phase1/README.md with setup and usage instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Domain Layer (No Dependencies)

- [X] T007 [P] Implement Priority enum in phase1/src/domain/enums.py (LOW, MEDIUM, HIGH)
- [X] T008 [P] Implement Status enum in phase1/src/domain/enums.py (PENDING, COMPLETED)
- [X] T009 [P] Implement custom exceptions in phase1/src/domain/exceptions.py (ValidationError, TaskNotFoundError)
- [X] T010 Implement Task dataclass in phase1/src/domain/task.py with validation in __post_init__

### Storage Layer (Depends on Domain)

- [X] T011 Implement InMemoryTaskRepository in phase1/src/storage/repository.py with dict[str, Task] storage
- [X] T012 Implement repository methods: add(task), get(task_id), update(task), delete(task_id), list_all()

### Service Layer (Depends on Storage and Domain)

- [X] T013 Create TaskService class in phase1/src/services/task_service.py with repository dependency injection
- [X] T014 Implement TaskService.create_task() returning (bool, str, Optional[Task]) tuple

### Utils Layer (No Dependencies)

- [X] T015 [P] Implement datetime utilities in phase1/src/utils/datetime_utils.py (ISO validation, overdue check)
- [X] T016 [P] Implement display utilities in phase1/src/utils/display_utils.py (table formatting, text truncation)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Tasks (Priority: P1) 🎯 MVP

**Goal**: Allow users to create new tasks with title and optional details (description, due_date, priority)

**Independent Test**: Launch app, select "Add Task", provide title "Buy groceries", verify task created with UUID, status "pending", and timestamps. See quickstart.md Test Scenario 1.

### Implementation for User Story 1

- [X] T017 [US1] Implement add_task_command() in phase1/src/commands/add_task.py with input prompts and validation
- [X] T018 [US1] Add input validation loop for title (re-prompt on empty or too long)
- [X] T019 [US1] Add input validation loop for due_date (re-prompt on invalid ISO format)
- [X] T020 [US1] Add input validation loop for priority (re-prompt on invalid value)
- [X] T021 [US1] Integrate add_task_command with TaskService.create_task()
- [X] T022 [US1] Display success message with task ID (first 8 chars) or error message
- [X] T023 [US1] Handle "quit" input to cancel operation and return to menu

**Checkpoint**: User Story 1 complete - users can create tasks with validation and see confirmation

---

## Phase 4: User Story 2 - View and Filter Tasks (Priority: P1) 🎯 MVP

**Goal**: Allow users to view tasks with filtering (status, priority, overdue) and sorting (priority, due_date, status)

**Independent Test**: Create 5 tasks with mixed properties, select "List Tasks", apply filters (pending/completed) and sorts (priority/due_date). See quickstart.md Test Scenario 2.

### Service Layer Extensions for User Story 2

- [X] T024 [US2] Implement TaskService.list_tasks() with filter_status parameter (None, PENDING, COMPLETED)
- [X] T025 [US2] Implement TaskService.list_tasks() with filter_priority parameter (None, LOW, MEDIUM, HIGH)
- [X] T026 [US2] Implement TaskService.list_tasks() with filter_overdue parameter (bool)
- [X] T027 [US2] Implement TaskService.list_tasks() with sort_by parameter (None, "priority", "due_date", "status")
- [X] T028 [US2] Implement sorting logic: priority (HIGH→MEDIUM→LOW), due_date (earliest first, nulls last), status (PENDING→COMPLETED)

### Implementation for User Story 2

- [X] T029 [US2] Implement list_tasks_command() in phase1/src/commands/list_tasks.py with filter/sort prompts
- [X] T030 [US2] Add filter input prompts (status, priority, overdue) with validation
- [X] T031 [US2] Add sort input prompt (priority, due_date, status, none) with validation
- [X] T032 [US2] Integrate list_tasks_command with TaskService.list_tasks()
- [X] T033 [US2] Format tasks using display_utils.format_task_table() with columns: ID (8 chars), Title (50 chars), Priority, Status, Due Date
- [X] T034 [US2] Display "No tasks found" message when result list is empty
- [X] T035 [US2] Add overdue indicator for tasks with due_date < today and status = pending

**Checkpoint**: User Story 2 complete - users can view, filter, and sort tasks

---

## Phase 5: User Story 3 - Update Tasks (Priority: P2)

**Goal**: Allow users to update task fields (title, description, due_date, priority) to keep tasks accurate

**Independent Test**: Create task, use "Update Task" menu, modify title/priority/due_date, verify changes persist and updated_at refreshed. See quickstart.md Test Scenario 3.

### Service Layer Extensions for User Story 3

- [X] T036 [US3] Implement TaskService.update_task() with task_id and field parameters
- [X] T037 [US3] Add field validation in update_task() (title length, date format, priority/status enums)
- [X] T038 [US3] Update task.updated_at timestamp on successful modification
- [X] T039 [US3] Return (False, "Task not found", None) for invalid task_id

### Implementation for User Story 3

- [X] T040 [US3] Implement update_task_command() in phase1/src/commands/update_task.py with UUID and field prompts
- [X] T041 [US3] Add UUID input validation (check task exists, re-prompt on not found)
- [X] T042 [US3] Display menu of fields to update (title, description, due_date, priority)
- [X] T043 [US3] Prompt for new value with validation based on selected field
- [X] T044 [US3] Integrate update_task_command with TaskService.update_task()
- [X] T045 [US3] Display success message with updated field or error message

**Checkpoint**: User Story 3 complete - users can update task details

---

## Phase 6: User Story 4 - Complete Tasks (Priority: P2)

**Goal**: Allow users to mark tasks as complete to track progress and distinguish finished work

**Independent Test**: Create pending task, use "Complete Task" menu, verify status changes to completed and updated_at refreshed. See quickstart.md Test Scenario 4.

### Service Layer Extensions for User Story 4

- [X] T046 [US4] Implement TaskService.complete_task() with task_id parameter
- [X] T047 [US4] Change task.status from PENDING to COMPLETED and refresh updated_at
- [X] T048 [US4] Make complete_task() idempotent (allow completing already completed tasks without error)
- [X] T049 [US4] Return (False, "Task not found", None) for invalid task_id

### Implementation for User Story 4

- [X] T050 [US4] Implement complete_task_command() in phase1/src/commands/complete_task.py with UUID prompt
- [X] T051 [US4] Add UUID input validation (check task exists, re-prompt on not found)
- [X] T052 [US4] Integrate complete_task_command with TaskService.complete_task()
- [X] T053 [US4] Display "Task marked as completed" or "Task is already completed" (idempotent case)

**Checkpoint**: User Story 4 complete - users can mark tasks as complete

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P3)

**Goal**: Allow users to delete tasks to remove items no longer relevant or created by mistake

**Independent Test**: Create task, use "Delete Task" menu with UUID, confirm deletion with "yes", verify task removed. See quickstart.md Test Scenario 5.

### Service Layer Extensions for User Story 5

- [X] T054 [US5] Implement TaskService.delete_task() with task_id parameter
- [X] T055 [US5] Remove task from repository on successful deletion
- [X] T056 [US5] Return (False, "Task not found", None) for invalid task_id

### Implementation for User Story 5

- [X] T057 [US5] Implement delete_task_command() in phase1/src/commands/delete_task.py with UUID and confirmation prompts
- [X] T058 [US5] Add UUID input validation (check task exists, re-prompt on not found)
- [X] T059 [US5] Display confirmation prompt: "Are you sure you want to delete this task? (yes/no)"
- [X] T060 [US5] Accept "yes" or "y" (case-insensitive) to proceed with deletion
- [X] T061 [US5] Accept "no" or "n" (case-insensitive) to cancel and return to menu
- [X] T062 [US5] Integrate delete_task_command with TaskService.delete_task() only on "yes" confirmation
- [X] T063 [US5] Display "Task deleted successfully" or "Deletion cancelled" message

**Checkpoint**: User Story 5 complete - users can delete tasks with confirmation

---

## Phase 8: Console Menu and Main Loop

**Purpose**: Tie all commands together with menu-driven interface

- [X] T064 Implement main menu loop in phase1/src/main.py
- [X] T065 Display numbered menu options: 1) Add Task, 2) List Tasks, 3) Update Task, 4) Complete Task, 5) Delete Task, 6) Exit
- [X] T066 Accept numeric input 1-6 and route to appropriate command handler
- [X] T067 Add input validation for menu selection (re-prompt on invalid option with error message)
- [X] T068 Implement graceful exit on option 6 with "Goodbye!" message
- [X] T069 Wrap each command handler in try/except to prevent crashes and display user-friendly error messages
- [X] T070 Return to main menu after completing each operation (except Exit)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Code quality, documentation, and validation

- [X] T071 [P] Run ruff linting and fix all errors: `cd phase1 && ruff check src/ --fix`
- [X] T072 [P] Run ruff formatting: `cd phase1 && ruff format src/`
- [X] T073 [P] Run mypy strict type checking and fix errors: `cd phase1 && mypy src/ --strict`
- [X] T074 Add docstrings (Google style) to all public functions and classes in src/
- [X] T075 Add inline comments for complex logic (validation, filtering, sorting)
- [X] T076 Update phase1/README.md with complete setup instructions and usage examples
- [X] T077 [P] Run manual testing scenarios from quickstart.md (all 5 user stories + edge cases)
- [X] T078 Create pytest fixtures in phase1/tests/conftest.py (mock_repository, sample_task)
- [X] T079 [P] Create placeholder tests for future: phase1/tests/test_domain/test_task.py
- [X] T080 [P] Create placeholder tests for future: phase1/tests/test_services/test_task_service.py
- [X] T081 Verify application resets on restart (in-memory storage, no persistence)
- [X] T082 Test edge cases: past due dates, long input, special characters, invalid menu options

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Phase 1 (Setup)**: No dependencies - start immediately
2. **Phase 2 (Foundational)**: Depends on Phase 1 completion - **BLOCKS all user stories**
3. **Phases 3-7 (User Stories)**: All depend on Phase 2 completion
   - User stories CAN proceed in parallel (if multiple developers)
   - OR sequentially in priority order: US1 (P1) → US2 (P1) → US3 (P2) → US4 (P2) → US5 (P3)
4. **Phase 8 (Console Menu)**: Depends on at least US1 and US2 completion (MVP = create + view tasks)
5. **Phase 9 (Polish)**: Depends on all desired user stories + Phase 8 completion

### User Story Dependencies

- **User Story 1 (Create Tasks, P1)**: Depends ONLY on Phase 2 - No dependencies on other stories ✅ MVP-ready
- **User Story 2 (View Tasks, P1)**: Depends ONLY on Phase 2 - No dependencies on other stories ✅ MVP-ready
- **User Story 3 (Update Tasks, P2)**: Depends ONLY on Phase 2 - No dependencies on other stories ✅ Independently testable
- **User Story 4 (Complete Tasks, P2)**: Depends ONLY on Phase 2 - No dependencies on other stories ✅ Independently testable
- **User Story 5 (Delete Tasks, P3)**: Depends ONLY on Phase 2 - No dependencies on other stories ✅ Independently testable

### Within Each Phase

- **Phase 2 (Foundational)**:
  - T007, T008, T009 can run in parallel (enums and exceptions, different files)
  - T010 depends on T007, T008, T009 (Task depends on enums)
  - T011, T012 depend on T010 (repository depends on Task)
  - T013, T014 depend on T011, T012 (service depends on repository)
  - T015, T016 can run in parallel with any other tasks (utils have no dependencies)

- **User Story Phases**:
  - Service layer extensions can run sequentially (extend same TaskService class)
  - Command implementations are independent and can run in parallel IF different developers
  - Within a story, complete service methods before command implementation

### Parallel Opportunities

#### Phase 1 (Setup)
```
T001, T002 (sequential - folder structure first)
T003, T004, T005, T006 (parallel - different config files)
```

#### Phase 2 (Foundational)
```
Parallel Group 1: T007, T008, T009, T015, T016 (enums, exceptions, utils - all different files)
Sequential: T010 (depends on enums)
Sequential: T011, T012 (depends on Task)
Sequential: T013, T014 (depends on repository)
```

#### User Story Phases (If Multiple Developers)
```
After Phase 2 completes:
Developer A: All User Story 1 tasks (T017-T023)
Developer B: All User Story 2 tasks (T024-T035)
Developer C: All User Story 3 tasks (T036-T045)
Developer D: All User Story 4 tasks (T046-T053)
Developer E: All User Story 5 tasks (T054-T063)

Stories integrate via shared TaskService without conflicts
```

#### Phase 9 (Polish)
```
Parallel Group: T071, T072, T073, T077, T079, T080 (linting, formatting, type checking, testing - independent)
```

---

## Implementation Strategy

### Recommended: MVP First (User Stories 1 & 2 Only)

This delivers a working todo app with create and view capabilities:

1. **Complete Phase 1**: Setup (T001-T006)
2. **Complete Phase 2**: Foundational (T007-T016) - **CRITICAL**
3. **Complete Phase 3**: User Story 1 - Create Tasks (T017-T023)
4. **Complete Phase 4**: User Story 2 - View Tasks (T024-T035)
5. **Complete Phase 8**: Console Menu (T064-T070) - with options 1, 2, 6 only
6. **VALIDATE**: Test US1 and US2 independently using quickstart.md scenarios
7. **Deploy/Demo**: MVP is ready! ✅

**Result**: Users can create tasks and view them with filters/sorts. This is a complete, usable todo application.

---

### Incremental Delivery (Add Features Progressively)

After MVP, add features one story at a time:

1. **MVP Delivered** (US1 + US2 + Menu)
2. **Add Phase 5**: User Story 3 - Update Tasks (T036-T045) + update menu option 3
3. **Deploy/Demo**: Now users can also update tasks ✅
4. **Add Phase 6**: User Story 4 - Complete Tasks (T046-T053) + update menu option 4
5. **Deploy/Demo**: Now users can mark tasks complete ✅
6. **Add Phase 7**: User Story 5 - Delete Tasks (T054-T063) + update menu option 5
7. **Deploy/Demo**: Full feature set complete ✅
8. **Complete Phase 9**: Polish & validation (T071-T082)
9. **Final Deploy**: Production-ready application ✅

**Benefit**: Each increment adds value without breaking existing functionality. Users get value sooner.

---

### Parallel Team Strategy (Multiple Developers)

If you have multiple developers available:

1. **Team completes Phase 1 + Phase 2 together** (Foundation)
2. **Once Phase 2 is done, parallel work begins**:
   - Developer 1: User Story 1 (T017-T023)
   - Developer 2: User Story 2 (T024-T035)
   - Developer 3: User Story 3 (T036-T045)
   - Developer 4: User Story 4 (T046-T053)
   - Developer 5: User Story 5 (T054-T063)
3. **Developer 6** (or 1 after US1 complete): Phase 8 - Console Menu (T064-T070)
4. **Integration**: All stories plug into menu, test independently, then together
5. **Team completes Phase 9 together**: Polish & validation (T071-T082)

**Benefit**: Maximum parallelization, fastest delivery, each developer owns a complete user story.

---

## Task Summary

**Total Tasks**: 82
**Tasks by Phase**:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 10 tasks (BLOCKING)
- Phase 3 (User Story 1 - P1): 7 tasks
- Phase 4 (User Story 2 - P1): 12 tasks
- Phase 5 (User Story 3 - P2): 10 tasks
- Phase 6 (User Story 4 - P2): 8 tasks
- Phase 7 (User Story 5 - P3): 9 tasks
- Phase 8 (Console Menu): 7 tasks
- Phase 9 (Polish): 13 tasks

**MVP Scope (Recommended)**: Phases 1, 2, 3, 4, 8 = 42 tasks for working create+view todo app

**Parallel Opportunities Identified**:
- 14 tasks marked [P] can run in parallel within their phases
- All 5 user stories can run in parallel after Phase 2 completion (if team capacity allows)

**Independent Test Criteria**:
- User Story 1: Create task, verify UUID and defaults (quickstart.md Test Scenario 1)
- User Story 2: Apply filters and sorts, verify results (quickstart.md Test Scenario 2)
- User Story 3: Update task fields, verify changes persist (quickstart.md Test Scenario 3)
- User Story 4: Complete task, verify status change and filtering (quickstart.md Test Scenario 4)
- User Story 5: Delete task with confirmation, verify removal (quickstart.md Test Scenario 5)

---

## Notes

- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- Tasks are immediately executable by LLM or developer
- Each user story is independently completable and testable
- No tests requested in spec, but test infrastructure created for future
- Manual testing via quickstart.md is the validation approach
- Stop at any checkpoint to validate story independently
- Commit after each task or logical group for safety
- Constitutional compliance verified in plan.md (all gates passed)

---

**Tasks Generated**: 2025-12-09
**Total Task Count**: 82 tasks
**MVP Task Count**: 42 tasks (Setup + Foundational + US1 + US2 + Menu)
**Format Validation**: ✅ All tasks follow checklist format with IDs, optional [P] markers, [Story] labels, and file paths
**Ready for Implementation**: Yes - `/sp.implement` can execute these tasks
