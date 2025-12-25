---
id: "0004"
title: phase3-task-tags-tasks
stage: tasks
date: 2025-12-24
surface: claude-code
model: claude-sonnet-4-5
feature: 001-phase3-task-tags
branch: 001-phase3-task-tags
user: majid
command: /sp.tasks
labels: [tasks, decomposition, user-stories, phase3, tags]
links:
  spec: specs/001-phase3-task-tags/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/001-phase3-task-tags/tasks.md
    action: created
    lines: 413
tests:
  - type: format-validation
    status: PASS
    note: All 60 tasks follow strict checklist format with IDs, [P] markers, [Story] labels, and file paths
---

## Prompt

/sp.tasks

Generate actionable, dependency-ordered tasks for feature 001-phase3-task-tags (Adding tags to Tasks in Phase 3) based on available design artifacts.

User context: Planning phase completed with comprehensive design documents (plan.md, research.md, data-model.md, contracts/mcp-tag-tools.yaml, quickstart.md). Constitution check PASSED. Ready to decompose feature into executable tasks organized by user story.

## Response snapshot

Generated 60 tasks organized into 8 phases for Phase 3 task tags integration:

**Task Organization by User Story**:

- **Phase 1: Setup (T001-T007)** - 7 tasks
  - Verify project structures for all 3 Phase 3 services
  - Install dependencies (Tailwind CSS, MCP SDK, httpx, FastAPI)
  - Verify Phase 2 backend endpoint accessibility

- **Phase 2: Foundational (T008-T013)** - 6 tasks (BLOCKING)
  - Tag validation schemas (format: ^[a-z0-9-]{1,50}$, max 10 tags)
  - NLP tag extraction utility (pattern matching + confidence scoring)
  - Task context manager (track last_task_id, reset triggers)
  - Cache service (60s TTL, per-user, invalidation)
  - Retry logic utility (single retry after 2s)
  - Selective logging configuration (errors + confidence <70%)

- **Phase 3: User Story 1 - Tag Display (T014-T019)** - 6 tasks [P1 - MVP]
  - TagBadge component (Tailwind pill badges)
  - Update Task interface to include tags[] field
  - Modify ChatMessage component to render tag badges
  - Tag truncation logic (max 5 shown, "...+N more")
  - Update API client to handle tags in responses
  - Verify ChatInterface passes tag data

- **Phase 4: User Story 2 - Tag Filtering (T020-T026)** - 7 tasks [P2]
  - Add tags parameter to list_tasks tool
  - NLP patterns for filtering ("show X tasks", "tasks tagged with X")
  - Confidence threshold (70%) with clarification prompts
  - Forward tags query parameters in phase3-backend
  - Handle "no tasks found" for non-existent tags
  - Handle "clear filters" command

- **Phase 5: User Story 3 - Add Tags (T027-T035)** - 9 tasks [P3]
  - Modify add_task tool to extract tags from NLP
  - Modify update_task tool to support adding tags
  - Extraction patterns for creation ("tagged with X") and updates ("tag this with X")
  - Context manager integration for "this" references
  - Context reset logic (on "show", "create", "filter" commands)
  - Tag validation (max 10, format rules)
  - Cache invalidation on create/update

- **Phase 6: User Story 4 - List Tags (T036-T042)** - 7 tasks [P4]
  - Create list_tags tool (calls GET /api/tasks/tags)
  - NLP patterns ("what tags do I have?", "list my tags")
  - Cache logic in phase3-backend (60s TTL)
  - Cache retrieval (return cached or fetch fresh)
  - Format tag list response (alphabetically sorted)
  - Handle empty tag list
  - Performance logging (cache hits <100ms vs misses <500ms)

- **Phase 7: User Story 5 - Remove Tags (T043-T049)** - 7 tasks [P5]
  - NLP patterns for removal ("remove X tag", "remove all tags")
  - Extend update_task tool for tag removal
  - Single tag removal logic
  - "Remove all tags" logic (empty array)
  - Error handling for non-existent tag removal
  - Cache invalidation on removal
  - Context integration for "this" references

- **Phase 8: Polish & Cross-Cutting (T050-T060)** - 11 tasks
  - Error logging for backend communication failures
  - Low-confidence logging (<70%) for tag extraction
  - Verify retry logic across all tools
  - Frontend error display with retry option
  - Loading indicators for tag operations
  - Performance optimizations (tag display <500ms, filtering <1s, cache <100ms)
  - Run quickstart.md manual test scenarios
  - Verify constitution compliance (zero Phase 2 changes)
  - Code cleanup and documentation

**Key Design Decisions**:
- NO test tasks (not requested in specification)
- Tasks organized by 5 user stories (P1-P5) for independent implementation
- Each user story is independently testable using quickstart.md scenarios
- Foundational phase (T008-T013) BLOCKS all user stories
- 18 tasks marked [P] for parallel execution
- All tasks include exact file paths
- Multi-service architecture: phase3-frontend, phase3-backend, phase3-mcp-server
- Zero Phase 2 backend modifications (read-only constraint)

**Parallel Opportunities**:
- Setup: T004, T005, T006 (different projects)
- Foundational: T008 and T011 (different projects)
- US1: T014, T015 (component + types)
- US2: T020, T021 (tool + extraction)
- US3: T027, T028 (add + update tools)
- US4: T036, T037 (tool + patterns)
- US5: T043, T044 (patterns + tool)
- Polish: T050, T051, T052 (different concerns)
- After Foundational: All user stories can proceed in parallel

**Implementation Strategy**:
- **MVP First**: Setup → Foundational → US1 (tag display) → Validate → Deploy
- **Incremental Delivery**: Add US2 (filtering) → US3 (adding) → US4 (listing) → US5 (removal)
- **Parallel Team**: After Foundational, assign one user story per developer

**Dependencies**:
- Setup → Foundational → User Stories (in priority order or parallel) → Polish
- Each user story is independently testable (no cross-story blocking dependencies)

## Outcome

- ✅ Impact: Generated 60 executable tasks organized into 8 phases. All tasks follow strict checklist format (checkbox, ID, [P] marker, [Story] label, file paths). Each of 5 user stories can be implemented and tested independently. MVP scope clearly identified (US1 - tag display). Multiple parallel execution opportunities identified (18 [P] tasks). Ready for /sp.implement.
- 🧪 Tests: Format validation PASSED - all 60 tasks include checkboxes, sequential IDs (T001-T060), appropriate [P] markers for parallelizable tasks, [Story] labels (US1-US5) for user story tasks, and exact file paths. No test tasks included per specification requirement.
- 📁 Files: Created 1 file (tasks.md with 60 tasks across 8 phases)
- 🔁 Next prompts: Run /sp.implement to execute tasks in dependency order. Or manually execute MVP scope (Phase 1 → Phase 2 → Phase 3) for fastest value delivery.
- 🧠 Reflection: Task decomposition successfully maps 5 user stories to 60 concrete implementation tasks. User story organization enables independent parallel development by multiple team members. Foundational phase correctly identified as blocking prerequisite. Clear checkpoints after each user story enable validation before proceeding. Parallel opportunities well-marked for efficiency. No test tasks per spec (manual testing via quickstart.md instead).

## Evaluation notes (flywheel)

- Failure modes observed: None. Task generation completed successfully. All tasks validated against checklist format requirements.
- Graders run and results (PASS/FAIL): Format validation: PASS (all 60 tasks have checkboxes, IDs, appropriate markers, file paths). User story independence: PASS (each story has clear goal, independent test criteria, no blocking cross-dependencies).
- Prompt variant (if applicable): N/A (standard /sp.tasks workflow)
- Next experiment (smallest change to try): N/A (task decomposition successful, proceed to implementation)
