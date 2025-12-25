---
description: "Task list for Phase 3 Task Tags Integration"
---

# Tasks: Phase 3 Task Tags Integration

**Input**: Design documents from `/specs/001-phase3-task-tags/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mcp-tag-tools.yaml

**Tests**: Tests are NOT requested in this feature specification - no test tasks included

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a multi-service web application:
- **phase3-frontend/**: Next.js frontend components and types
- **phase3-backend/**: FastAPI proxy/adapter with caching
- **phase3-mcp-server/**: MCP server with NLP tools

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification of existing structure

- [ ] T001 Verify phase3-frontend project structure exists with components/, lib/, app/chat/ directories
- [ ] T002 Verify phase3-backend project structure exists with app/services/, app/routes/ directories
- [ ] T003 Verify phase3-mcp-server project structure exists with app/tools/, app/schemas/, app/utils/ directories
- [ ] T004 [P] Install frontend dependencies (Tailwind CSS already present, verify TypeScript 5.x + Next.js 16)
- [ ] T005 [P] Install MCP server dependencies (MCP SDK, httpx) in phase3-mcp-server/requirements.txt
- [ ] T006 [P] Install phase3-backend dependencies (FastAPI, httpx) in phase3-backend/requirements.txt
- [ ] T007 Verify Phase 2 backend endpoints are accessible (GET /api/tasks/tags, GET /api/tasks?tags=X)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create tag validation schemas in phase3-mcp-server/app/schemas/tag_schemas.py (format: ^[a-z0-9-]{1,50}$, max 10 tags)
- [X] T009 Create NLP tag extraction utility in phase3-mcp-server/app/tools/tag_extractor.py (pattern matching + confidence scoring)
- [X] T010 Create task context manager in phase3-mcp-server/app/utils/context_manager.py (track last_task_id, reset on task-related commands)
- [X] T011 Create cache service in phase3-backend/app/services/cache_service.py (60s TTL, per-user keying, invalidation logic)
- [X] T012 Add retry logic utility in phase3-mcp-server/app/utils/retry.py (single retry after 2s delay)
- [X] T013 Add selective logging configuration for tag operations (errors + confidence <70%) in both MCP server and phase3-backend

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Chat Interface Tag Display (Priority: P1) 🎯 MVP

**Goal**: Display tags as visual badges in the chat interface for all tasks

**Independent Test**: Ask chatbot "show me my tasks" and verify tags appear as badges alongside each task. Tasks without tags show no tag section.

### Implementation for User Story 1

- [X] T014 [P] [US1] Create TagBadge component in phase3-frontend/components/TagBadge.tsx (Tailwind pill badges, support sm/md sizes)
- [X] T015 [P] [US1] Update Task interface in phase3-frontend/lib/types.ts to include tags: string[] field
- [X] T016 [US1] Modify ChatMessage component in phase3-frontend/components/ChatMessage.tsx to render TagBadge components for task tags
- [X] T017 [US1] Add tag truncation logic to ChatMessage component (show max 5 tags, "...+N more" for overflow)
- [X] T018 [US1] Update API client in phase3-frontend/lib/api.ts to handle tags field in task responses
- [X] T019 [US1] Verify ChatInterface component in phase3-frontend/components/ChatInterface.tsx passes tag data to ChatMessage

**Checkpoint**: At this point, User Story 1 should be fully functional - tags display in chat for all tasks

---

## Phase 4: User Story 2 - Natural Language Tag Filtering (Priority: P2)

**Goal**: Enable filtering tasks by tags using natural language commands (e.g., "show me work tasks")

**Independent Test**: Say "show me work tasks" and verify only tasks tagged with "work" are returned. Say "show urgent work tasks" and verify AND logic (tasks must have BOTH tags).

### Implementation for User Story 2

- [X] T020 [P] [US2] Add tag filtering parameter support to list_tasks tool in phase3-mcp-server/app/tools/list_tasks.py (extract tags from NLP)
- [X] T021 [P] [US2] Update tag_extractor.py to recognize filtering patterns ("show X tasks", "tasks tagged with X", "my X tasks")
- [X] T022 [US2] Implement tag filter extraction with confidence threshold (70%) in list_tasks tool
- [X] T023 [US2] Add clarification prompt for ambiguous tag filter commands (confidence <70%)
- [X] T024 [US2] Update phase3-backend HTTP client in phase3-backend/app/utils/http_client.py to forward tags query parameters to Phase 2 backend
- [X] T025 [US2] Handle "no tasks found" response when filtering by non-existent tag
- [X] T026 [US2] Handle "clear filters" / "show all tasks" command to reset tag filtering

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can view and filter tasks by tags

---

## Phase 5: User Story 3 - Add Tags via Natural Language (Priority: P3)

**Goal**: Enable adding tags to tasks using natural language commands (e.g., "add task tagged with home", "tag this with urgent")

**Independent Test**: Say "add task buy groceries tagged with home" and verify task is created with "home" tag. Say "tag this with urgent" and verify tag is added to last-referenced task.

### Implementation for User Story 3

- [X] T027 [P] [US3] Modify add_task tool in phase3-mcp-server/app/tools/add_task.py to extract tags from NLP during task creation
- [X] T028 [P] [US3] Modify update_task tool in phase3-mcp-server/app/tools/update_task.py to support adding tags to existing tasks
- [X] T029 [US3] Add tag extraction for task creation patterns ("tagged with X", "with tags X, Y") to tag_extractor.py
- [X] T030 [US3] Add tag extraction for update patterns ("tag this with X", "add tag X") to tag_extractor.py
- [X] T031 [US3] Integrate context_manager.py with update_task tool to resolve "this" references to last_task_id
- [X] T032 [US3] Implement context reset logic (reset on "show tasks", "create task", "filter tasks" commands)
- [X] T033 [US3] Add tag count validation (max 10 tags) with user-friendly error message
- [X] T034 [US3] Add tag format validation with error messages ("Tags can only contain lowercase letters, numbers, and hyphens")
- [X] T035 [US3] Update phase3-backend proxy in phase3-backend/app/routes/proxy.py to invalidate tag cache when tasks are created/updated with tags

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - full tag workflow in chat (view, filter, create/edit with tags)

---

## Phase 6: User Story 4 - View User's Available Tags (Priority: P4)

**Goal**: Enable viewing all unique user tags via chat command (e.g., "what tags do I have?")

**Independent Test**: Say "what tags do I have?" and verify chatbot returns alphabetically sorted list of all unique tags. If no tags exist, verify appropriate message.

### Implementation for User Story 4

- [X] T036 [P] [US4] Create list_tags tool in phase3-mcp-server/app/tools/list_tags.py (calls GET /api/tasks/tags endpoint)
- [X] T037 [P] [US4] Add tag listing patterns to tag_extractor.py ("what tags do I have?", "list my tags", "show all tags")
- [X] T038 [US4] Implement cache logic in phase3-backend/app/routes/proxy.py for GET /api/tasks/tags endpoint (60s TTL)
- [X] T039 [US4] Add cache retrieval logic to proxy route (return cached tags if valid, otherwise fetch from Phase 2)
- [X] T040 [US4] Format tag list response in list_tags tool (alphabetically sorted, user-friendly message)
- [X] T041 [US4] Handle empty tag list scenario ("You haven't created any tags yet")
- [X] T042 [US4] Add performance logging for cache hits (<100ms) vs cache misses (<500ms)

**Checkpoint**: At this point, User Stories 1-4 should all work independently - users can view, filter, create, and list tags

---

## Phase 7: User Story 5 - Remove Tags via Natural Language (Priority: P5)

**Goal**: Enable removing tags from tasks using natural language commands (e.g., "remove the urgent tag")

**Independent Test**: Say "remove the urgent tag from this task" and verify tag is removed. Say "remove all tags" and verify all tags are removed.

### Implementation for User Story 5

- [X] T043 [P] [US5] Add tag removal patterns to tag_extractor.py ("remove X tag", "untag X", "delete tag X", "remove all tags")
- [X] T044 [US5] Extend update_task tool in phase3-mcp-server/app/tools/update_task.py to support tag removal operations
- [X] T045 [US5] Implement single tag removal logic (fetch current tags, remove specified tag, update task)
- [X] T046 [US5] Implement "remove all tags" logic (set tags to empty array)
- [X] T047 [US5] Add error handling for removing non-existent tag ("This task doesn't have the 'urgent' tag")
- [X] T048 [US5] Update phase3-backend proxy to invalidate tag cache when tags are removed
- [X] T049 [US5] Integrate context_manager.py for "this" reference resolution in tag removal

**Checkpoint**: All user stories (1-5) should now be independently functional - complete tag lifecycle management in chat

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T050 [P] Add error logging for Phase 2 backend communication failures in phase3-backend/app/routes/proxy.py
- [X] T051 [P] Add low-confidence logging (<70%) for tag extraction in phase3-mcp-server (FR-026 requirement)
- [X] T052 [P] Verify retry logic works across all MCP tools (single retry after 2s, then user-friendly error)
- [X] T053 Update frontend error display for tag operation failures (show retry option)
- [X] T054 Add loading indicators for tag operations in ChatMessage component
- [X] T055 Performance optimization: verify tag display renders <500ms (SC-001)
- [X] T056 Performance optimization: verify tag filtering responds <1s for 1000 tasks (SC-003)
- [X] T057 Performance optimization: verify cached tag list retrieval <100ms (SC-008)
- [X] T058 Run manual test scenarios from specs/001-phase3-task-tags/quickstart.md (all 5 user stories + edge cases)
- [X] T059 Verify constitution compliance: zero Phase 2 backend modifications
- [X] T060 Code cleanup and documentation updates (add inline comments for NLP patterns, cache logic)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 for display, but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses context manager from Foundational, independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Uses cache service from Foundational, independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Uses context manager + update_task, independently testable

### Within Each User Story

- Models/schemas before services
- Services/utilities before tool implementations
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: T004, T005, T006 can run in parallel (different projects)
- **Foundational (Phase 2)**: T008 can run in parallel with T011 (different projects)
- **User Story 1**: T014, T015 can run in parallel (TagBadge component + types update)
- **User Story 2**: T020, T021 can run in parallel (list_tasks tool + tag_extractor patterns)
- **User Story 3**: T027, T028 can run in parallel (add_task + update_task modifications)
- **User Story 4**: T036, T037 can run in parallel (list_tags tool + extraction patterns)
- **User Story 5**: T043, T044 can run in parallel (extraction patterns + update_task extension)
- **Polish (Phase 8)**: T050, T051, T052 can run in parallel (different concerns)
- **Once Foundational completes**: All user stories (US1-US5) can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch frontend tasks together:
Task T014: "Create TagBadge component in phase3-frontend/components/TagBadge.tsx"
Task T015: "Update Task interface in phase3-frontend/lib/types.ts"

# Then proceed sequentially:
Task T016: "Modify ChatMessage component to render TagBadge components"
Task T017: "Add tag truncation logic to ChatMessage component"
```

---

## Parallel Example: User Story 3

```bash
# Launch tool modifications together:
Task T027: "Modify add_task tool to extract tags from NLP"
Task T028: "Modify update_task tool to support adding tags"

# Launch extraction patterns together:
Task T029: "Add tag extraction for task creation patterns"
Task T030: "Add tag extraction for update patterns"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T013) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T014-T019)
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md Scenario 1
5. Deploy/demo if ready

**Deliverable**: Users can see tags displayed in chat interface - immediate value

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! Tag visibility)
3. Add User Story 2 → Test independently → Deploy/Demo (Tag filtering)
4. Add User Story 3 → Test independently → Deploy/Demo (Tag creation/editing)
5. Add User Story 4 → Test independently → Deploy/Demo (Tag discovery)
6. Add User Story 5 → Test independently → Deploy/Demo (Tag removal - full CRUD)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Frontend focus - tag display)
   - Developer B: User Story 2 (MCP focus - tag filtering)
   - Developer C: User Story 3 (MCP + Backend focus - tag creation)
   - Developer D: User Story 4 (Backend focus - caching)
   - Developer E: User Story 5 (MCP focus - tag removal)
3. Stories complete and integrate independently
4. Polish phase done collaboratively

---

## Notes

- [P] tasks = different files/projects, no dependencies, safe to parallelize
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- NO test tasks included (not requested in specification)
- Phase 2 backend is READ-ONLY - zero modifications allowed
- All MCP tools must use existing Phase 2 endpoints (GET /api/tasks/tags, GET /api/tasks?tags=X, POST/PUT /api/tasks)
- Tag validation enforced by Phase 2 backend (max 10 tags, 1-50 chars, format ^[a-z0-9-]+$)
- MCP server confidence threshold: 70% (ask for clarification below this)
- Context retention: "this" references valid until next task-related command
- Retry strategy: Single retry after 2 seconds for failed operations
- Caching: 60-second TTL with invalidation on tag operations
- Logging: Selective (errors + confidence <70% only)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Verify against quickstart.md test scenarios after each user story
