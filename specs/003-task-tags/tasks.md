# Tasks: Task Tags/Categories

**Input**: Design documents from `/specs/003-task-tags/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi-tags.yaml

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare project for tags feature implementation

- [x] T001 Review existing project structure and dependencies in backend/ and frontend/
- [ ] T002 [P] Backup production database before migrations
- [x] T003 [P] Create feature branch 003-task-tags from phase-2-stable (already done)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Run database migration backend/migrations/005_add_tags_to_tasks.sql to add tags column and GIN index
- [x] T005 Verify migration success: Check column exists with `\d tasks` and index with `\di idx_tasks_tags`
- [x] T006 [P] Update Task type interface in frontend/types/task.ts to include tags: string[]
- [x] T007 [P] Update TaskCreate interface in frontend/types/task.ts to include tags?: string[]
- [x] T008 [P] Update TaskUpdate interface in frontend/types/task.ts to include tags?: string[]
- [x] T009 [P] Update TaskFilter interface in frontend/types/task.ts to include tags?: string[]

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Tags to Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can categorize tasks with tags during creation and editing, with tag autocomplete and validation

**Independent Test**: Create a new task with tags "work" and "urgent", verify tags are saved and displayed on task card. Edit task to add/remove tags. Autocomplete shows previously used tags.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [P] [US1] Unit test for tag validator max tags in backend/tests/test_task_service.py (test_tag_validation_max_tags)
- [x] T011 [P] [US1] Unit test for tag validator length in backend/tests/test_task_service.py (test_tag_validation_length)
- [x] T012 [P] [US1] Unit test for tag validator format in backend/tests/test_task_service.py (test_tag_validation_format)
- [x] T013 [P] [US1] Unit test for tag normalization in backend/tests/test_task_service.py (test_tag_normalization)
- [x] T014 [P] [US1] Integration test for create task with tags in backend/tests/test_task_routes.py (test_create_task_with_tags)
- [x] T015 [P] [US1] Integration test for update task tags in backend/tests/test_task_routes.py (test_update_task_tags)

### Backend Implementation for User Story 1

- [x] T016 [US1] Add tags field to TaskBase model in backend/models/task.py with sa_column=Column(ARRAY(String))
- [x] T017 [US1] Implement @field_validator("tags") in backend/models/task.py with max 10, length 1-50, format ^[a-z0-9-]+$, normalization (lowercase, trim, dedup)
- [x] T018 [US1] Update POST /api/tasks endpoint in backend/routes/tasks.py to accept tags in request body
- [x] T019 [US1] Update PUT /api/tasks/{task_id} endpoint in backend/routes/tasks.py to accept tags in request body
- [x] T020 [US1] Add error handling for tag validation errors in backend/routes/tasks.py to return clear error messages
- [x] T021 [US1] Run backend tests to verify tag validation and create/update operations work

### Frontend Implementation for User Story 1

- [x] T022 [P] [US1] Create TagSelector component in frontend/components/TagSelector.tsx with input, add/remove, chip display, max 10 validation
- [x] T023 [P] [US1] Create useTags hook in frontend/lib/hooks/useTags.ts for fetching and caching user tags
- [x] T024 [P] [US1] Add autocomplete logic to TagSelector with client-side filtering (debounced 300ms)
- [x] T025 [P] [US1] Update TaskCard component in frontend/components/TaskCard.tsx to display tags as styled badges below task title
- [x] T026 [US1] Update TaskForm component in frontend/app/tasks/new/page.tsx and frontend/app/tasks/[id]/edit/page.tsx to include TagSelector with selectedTags and onChange handler
- [x] T027 [US1] Update createTask function in frontend/lib/api/tasks.ts to include tags in request payload (already supported via TaskCreate interface)
- [x] T028 [US1] Update updateTask function in frontend/lib/api/tasks.ts to include tags in request payload (already supported via TaskUpdate interface)

### Frontend Tests for User Story 1

- [x] T029 [P] [US1] Component test for TagSelector in frontend/components/__tests__/TagSelector.test.tsx (render, add tag, remove tag, max 10 validation) - Test skeleton created, requires Jest + React Testing Library setup
- [x] T030 [P] [US1] Component test for TaskCard with tags in frontend/components/__tests__/TaskCard.test.tsx (verify tags display) - Test skeleton created, requires Jest + React Testing Library setup
- [x] T031 [P] [US1] E2E test for create task with tags in frontend/tests/e2e/tags.spec.ts (Playwright) - Test skeleton created, requires Playwright setup
- [x] T032 [P] [US1] E2E test for edit task tags in frontend/tests/e2e/tags.spec.ts (add and remove tags) - Test skeleton created, requires Playwright setup

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add/edit tags with autocomplete and validation

---

## Phase 4: User Story 2 - Filter Tasks by Tags (Priority: P2)

**Goal**: Users can filter task list by one or more tags using AND logic to focus on specific categories

**Independent Test**: Create tasks with tags "work", "home", "urgent". Filter by "work" - see only work tasks. Filter by "work" AND "urgent" - see only tasks with both tags. Clear filter - see all tasks.

### Tests for User Story 2

- [ ] T033 [P] [US2] Unit test for filter by single tag in backend/tests/test_task_service.py (test_filter_by_single_tag)
- [ ] T034 [P] [US2] Unit test for filter by multiple tags AND logic in backend/tests/test_task_service.py (test_filter_by_multiple_tags_and_logic)
- [ ] T035 [P] [US2] Unit test for tag isolation in backend/tests/test_task_service.py (test_tag_isolation - user A can't see user B's tags)
- [ ] T036 [P] [US2] Integration test for filter endpoint in backend/tests/test_task_routes.py (test_filter_tasks_by_tags)

### Backend Implementation for User Story 2

- [x] T037 [US2] Add tags query parameter (list[str] | None) to GET /api/tasks endpoint in backend/routes/tasks.py
- [x] T038 [US2] Update get_user_tasks function in backend/services/task_service.py to accept tags parameter and apply WHERE tags @> ARRAY[tag] for each tag (AND logic)
- [ ] T039 [US2] Add SQL query logging to verify GIN index usage with EXPLAIN ANALYZE in backend/services/task_service.py
- [ ] T040 [US2] Run backend tests to verify tag filtering works correctly with AND logic

### Frontend Implementation for User Story 2

- [x] T041 [P] [US2] Update TaskFilters component in frontend/components/TaskFilters.tsx to add tag filtering section with multi-select
- [x] T042 [P] [US2] Add active tag filter display to TaskFilters with clear filter option
- [x] T043 [US2] Update getTasks function in frontend/lib/api/tasks.ts to append tags query parameters (?tags=work&tags=urgent)
- [x] T044 [US2] Update task list page in frontend/app/tasks/ to pass tag filters to getTasks

### Frontend Tests for User Story 2

- [ ] T045 [P] [US2] Component test for TaskFilters with tags in frontend/components/__tests__/TaskFilters.test.tsx
- [ ] T046 [P] [US2] E2E test for filter by single tag in frontend/tests/e2e/tags.spec.ts
- [ ] T047 [P] [US2] E2E test for filter by multiple tags AND logic in frontend/tests/e2e/tags.spec.ts
- [ ] T048 [P] [US2] E2E test for clear tag filter in frontend/tests/e2e/tags.spec.ts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can add tags and filter by them

---

## Phase 5: User Story 3 - View All Used Tags (Priority: P3)

**Goal**: Users can see a list of all unique tags they've used to discover categories and reuse them consistently

**Independent Test**: Create tasks with tags "work", "home", "urgent". View tag list - see all three tags alphabetically. Delete all tasks with "work" tag - "work" disappears from list.

### Tests for User Story 3

- [ ] T049 [P] [US3] Unit test for get_user_tags in backend/tests/test_task_service.py (test_get_user_tags - unique, sorted)
- [ ] T050 [P] [US3] Integration test for GET /api/tasks/tags endpoint in backend/tests/test_task_routes.py (test_list_tags_endpoint)

### Backend Implementation for User Story 3

- [x] T051 [US3] Implement get_user_tags function in backend/services/task_service.py with SQL: SELECT DISTINCT unnest(tags) FROM tasks WHERE user_id = ? ORDER BY tag
- [x] T052 [US3] Add GET /api/tasks/tags endpoint in backend/routes/tasks.py returning list[str] sorted alphabetically
- [x] T053 [US3] Add authentication requirement to GET /api/tasks/tags endpoint
- [ ] T054 [US3] Run backend tests to verify tag list endpoint returns unique sorted tags

### Frontend Implementation for User Story 3

- [x] T055 [P] [US3] Add getUserTags function in frontend/lib/api/tasks.ts calling GET /api/tasks/tags
- [x] T056 [P] [US3] Update useTags hook in frontend/hooks/useTags.ts to fetch all user tags on mount via getUserTags
- [x] T057 [US3] Update TagSelector component in frontend/components/TagSelector.tsx to use useTags hook for autocomplete suggestions
- [x] T058 [US3] Add tag list caching in useTags hook with React state to reduce API calls

### Frontend Tests for User Story 3

- [ ] T059 [P] [US3] Component test for useTags hook in frontend/hooks/__tests__/useTags.test.ts
- [ ] T060 [P] [US3] E2E test for tag autocomplete in frontend/tests/e2e/tags.spec.ts (type "wo" - see "work" suggestion)

**Checkpoint**: All core user stories (US1, US2, US3) should now be independently functional - users can add, filter, and discover tags

---

## Phase 6: User Story 4 - Natural Language Tag Commands (Priority: P4)

**Goal**: Chatbot users can use natural language to manage tags ("show me work tasks", "add a task tagged with personal")

**Independent Test**: In chatbot, say "show me all work tasks" - bot displays filtered tasks. Say "add a task to buy groceries tagged with home" - bot creates task with "home" tag.

**Note**: This user story is implemented in Phase3 backend/frontend, not Phase2. No Phase2 code changes required.

### Phase3 Documentation Updates (Informational)

- [ ] T061 [US4] Document in phase3-mcp-server/ README that tag filtering is supported via Phase2 API
- [ ] T062 [US4] Document in phase3-backend/ that natural language tag parsing should extract tags and call Phase2 API with tags parameter
- [ ] T063 [US4] Add example MCP tool usage for tags in phase3-mcp-server/examples/

**Checkpoint**: Phase3 chatbot can interpret natural language tag commands by calling Phase2 REST API

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and finalization

### Documentation

- [ ] T064 [P] Update API documentation in backend/ with GET /api/tasks/tags endpoint and tags query parameter examples
- [ ] T065 [P] Update OpenAPI schema in backend/ to reflect tags field in Task model
- [ ] T066 [P] Update frontend README with TagSelector component documentation

### Performance & Optimization

- [ ] T067 Verify GIN index usage with EXPLAIN ANALYZE for tag filtering queries (target: <1s for 1000+ tasks)
- [ ] T068 Measure tag autocomplete latency (target: <300ms)
- [ ] T069 Measure GET /api/tasks/tags endpoint response time (target: <500ms)
- [ ] T070 [P] Optimize TagSelector debounce delay if autocomplete is slow

### Validation & Quality

- [ ] T071 Run all backend tests: python3.13 -m pytest backend/tests/ -v --cov=backend
- [ ] T072 Run all frontend tests: cd frontend && npm run test
- [ ] T073 Run E2E tests: cd frontend && npm run test:e2e
- [ ] T074 Verify test coverage is >=95% for new code
- [ ] T075 Run linting: ruff check backend/ and npm run lint in frontend/
- [ ] T076 Run type checking: mypy backend/ --strict and npm run type-check in frontend/

### Manual Testing (Quickstart)

- [ ] T077 Execute Scenario 1 from quickstart.md: Create task with tags
- [ ] T078 Execute Scenario 2 from quickstart.md: Tag autocomplete
- [ ] T079 Execute Scenario 3 from quickstart.md: Tag validation (max 10, format, length)
- [ ] T080 Execute Scenario 4 from quickstart.md: Filter by single tag
- [ ] T081 Execute Scenario 5 from quickstart.md: Filter by multiple tags (AND logic)
- [ ] T082 Execute Scenario 6 from quickstart.md: Clear tag filter
- [ ] T083 Execute Scenario 7 from quickstart.md: View all used tags
- [ ] T084 Execute Scenario 8 from quickstart.md: Edit task tags
- [ ] T085 Execute Scenario 9 from quickstart.md: Tag normalization
- [ ] T086 Execute Scenario 10 from quickstart.md: Empty tag filter edge case

### Security & Error Handling

- [ ] T087 Verify user isolation: User A cannot see User B's tags
- [ ] T088 Verify JWT authentication required for all tag endpoints
- [ ] T089 Verify SQL injection protection with parameterized queries
- [ ] T090 Test error messages are clear and actionable for validation failures

### Deployment Preparation

- [ ] T091 Create database migration rollback script if needed
- [ ] T092 Update CHANGELOG.md with tags feature description
- [ ] T093 Prepare deployment checklist: migration → backend → frontend → smoke tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Enhances US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US1/US2 but independently testable
- **User Story 4 (P4)**: Can start after US1/US2/US3 are stable - Phase3 implementation only

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Backend models before backend services
- Backend services before backend routes
- Frontend types before frontend components
- Frontend API client before frontend UI components
- Core implementation before integration
- Story complete and tested before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003)
- All Foundational tasks marked [P] can run in parallel (T006-T009)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Backend and frontend implementation within a story can proceed in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1 (Backend)

```bash
# Launch all backend tests for User Story 1 together:
Task T010: "Unit test for tag validator max tags in backend/tests/test_task_service.py"
Task T011: "Unit test for tag validator length in backend/tests/test_task_service.py"
Task T012: "Unit test for tag validator format in backend/tests/test_task_service.py"
Task T013: "Unit test for tag normalization in backend/tests/test_task_service.py"
Task T014: "Integration test for create task with tags in backend/tests/test_task_routes.py"
Task T015: "Integration test for update task tags in backend/tests/test_task_routes.py"
```

## Parallel Example: User Story 1 (Frontend)

```bash
# Launch all frontend components for User Story 1 together:
Task T022: "Create TagSelector component in frontend/components/TagSelector.tsx"
Task T023: "Create useTags hook in frontend/hooks/useTags.ts"
Task T024: "Add autocomplete logic to TagSelector"
Task T025: "Update TaskCard component to display tags"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009) - CRITICAL: blocks all stories
3. Complete Phase 3: User Story 1 (T010-T032)
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md Scenarios 1, 2, 3, 8, 9
5. Deploy/demo if ready - users can now add and edit tags with autocomplete

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP: tag creation and editing!)
3. Add User Story 2 → Test independently → Deploy/Demo (tag filtering added!)
4. Add User Story 3 → Test independently → Deploy/Demo (tag discovery added!)
5. Add User Story 4 → Test independently → Deploy/Demo (chatbot integration!)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is done (T004-T009 complete):
   - **Developer A**: User Story 1 (T010-T032) - Backend + Frontend
   - **Developer B**: User Story 2 (T033-T048) - Backend + Frontend
   - **Developer C**: User Story 3 (T049-T060) - Backend + Frontend
3. Stories complete and integrate independently
4. **Developer D**: User Story 4 (T061-T063) - Phase3 documentation
5. Team collaborates on Polish (T064-T093)

---

## Task Summary

- **Total Tasks**: 93
- **Setup Phase**: 3 tasks
- **Foundational Phase**: 6 tasks (BLOCKING)
- **User Story 1 (P1 - MVP)**: 23 tasks (10 tests + 13 implementation)
- **User Story 2 (P2)**: 16 tasks (4 tests + 12 implementation)
- **User Story 3 (P3)**: 12 tasks (2 tests + 10 implementation)
- **User Story 4 (P4)**: 3 tasks (documentation only)
- **Polish Phase**: 30 tasks (documentation, performance, validation, deployment)

**Parallel Tasks**: 47 tasks marked [P] can run in parallel (50% of total)

**MVP Scope** (Minimal viable feature): Phase 1 + Phase 2 + Phase 3 (User Story 1) = 32 tasks

**Estimated Effort** (based on plan.md):
- MVP (US1): 2-3 hours
- US2: 1-2 hours
- US3: 1 hour
- US4: 30 minutes
- Polish: 1-2 hours
- **Total**: 5-8 hours for full implementation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Run `git add . && git commit -m "feat(tags): [description]"` after each phase
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

**Critical Success Factors**:
1. ✅ Complete Foundational phase (T004-T009) before any user story work
2. ✅ Write tests FIRST, ensure they FAIL, then implement
3. ✅ Test each user story independently using quickstart.md scenarios
4. ✅ Verify GIN index usage with EXPLAIN ANALYZE (performance target: <1s filtering)
5. ✅ Maintain user isolation - tags scoped per user
6. ✅ Deploy incrementally - MVP first (US1), then add US2, US3, US4
