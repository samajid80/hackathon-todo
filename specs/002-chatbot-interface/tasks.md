---
description: "Implementation tasks for Natural Language Chatbot for Todo Management"
---

# Tasks: Natural Language Chatbot for Todo Management

**Input**: Design documents from `/specs/002-chatbot-interface/`
**Prerequisites**: plan.md (✅), spec.md (✅)

**Tests**: Tests are OPTIONAL for this feature. Tasks below focus on implementation only as tests were not explicitly requested in the specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Phase 2 (Existing - NO CHANGES)**: `backend/`, `frontend/`
- **Phase 3 (New Services)**: `phase3-backend/`, `phase3-mcp-server/`, `phase3-frontend/`
- **Database**: `backend/migrations/` (extend only - add new migration files)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Phase 3 service structure and database schema

- [X] T001 Create phase3-backend/ directory structure per plan.md
- [X] T002 Create phase3-mcp-server/ directory structure per plan.md
- [X] T003 Create phase3-frontend/ directory structure per plan.md
- [X] T004 [P] Initialize phase3-backend pyproject.toml with dependencies (fastapi, openai, openai-agents, sqlmodel, httpx, pyjwt, python-dotenv)
- [X] T005 [P] Initialize phase3-mcp-server pyproject.toml with dependencies (fastapi, mcp, httpx, pyjwt, python-dotenv)
- [X] T006 [P] Initialize phase3-frontend package.json with dependencies (next@16+, react@19+, @openai/chatkit-react, better-auth, typescript@5+)
- [X] T007 [P] Create phase3-backend .env.example file with DATABASE_URL, OPENAI_API_KEY, JWT_SECRET, MCP_SERVER_URL
- [X] T008 [P] Create phase3-mcp-server .env.example file with PHASE2_BACKEND_URL, JWT_SECRET
- [X] T009 [P] Create phase3-frontend .env.local.example file with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET
- [X] T010 [P] Create phase3-backend railway.json deployment config
- [X] T011 [P] Create phase3-mcp-server railway.json deployment config
- [X] T012 [P] Create phase3-frontend vercel.json deployment config
- [X] T013 Create database migration backend/migrations/003_create_conversations_table.sql
- [X] T014 Create database migration backend/migrations/004_create_messages_table.sql

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete. This phase establishes the foundation for all chat functionality.

### Database Setup

- [X] T015 Run migration 003_create_conversations_table.sql on Neon PostgreSQL
- [X] T016 Run migration 004_create_messages_table.sql on Neon PostgreSQL
- [X] T017 Verify Phase 2 backend tests still pass (backward compatibility check)

### phase3-backend Foundation

- [X] T018 Create phase3-backend/app/config.py for environment variable loading
- [X] T019 Create phase3-backend/app/db.py with async SQLModel engine and session management
- [X] T020 [P] Create phase3-backend/app/models/chat.py with Conversation and Message SQLModels
- [X] T021 [P] Create phase3-backend/app/main.py with FastAPI app initialization, CORS config for Vercel
- [X] T022 [P] Create phase3-backend/app/routes/health.py with /health and /readiness endpoints
- [X] T023 [P] Implement JWT validation middleware in phase3-backend/app/auth/jwt_middleware.py (reuse pattern from backend/auth/jwt_middleware.py)
- [X] T024 [P] Create phase3-backend/app/services/chat_service.py with conversation CRUD operations (get_or_create_conversation, save_message, get_message_history)

### phase3-mcp-server Foundation

- [X] T025 Create phase3-mcp-server/app/config.py for environment variable loading
- [X] T026 Create phase3-mcp-server/app/main.py with FastAPI app and /mcp endpoint routing
- [X] T027 Create phase3-mcp-server/app/server.py with MCP Server initialization using Official MCP SDK
- [X] T028 Create phase3-mcp-server/app/clients/phase2_client.py as HTTP client for phase2-backend REST API

### phase3-backend AI Integration

- [X] T029 Create phase3-backend/app/agents/openai_agent.py with OpenAI Agents SDK initialization
- [X] T030 Define system prompt for todo assistant in phase3-backend/app/agents/openai_agent.py
- [X] T031 Create phase3-backend/app/agents/mcp_client.py as HTTP client for phase3-mcp-server

### phase3-frontend Foundation

- [X] T032 [P] Create phase3-frontend/app/layout.tsx with root layout and Better-Auth provider
- [X] T033 [P] Create phase3-frontend/lib/auth.ts with Better-Auth config (copy from frontend/lib/auth.ts)
- [X] T034 [P] Create phase3-frontend/lib/types.ts with TypeScript interfaces for chat messages and API responses
- [X] T035 [P] Create phase3-frontend/lib/api.ts with API client for phase3-backend /chat endpoint
- [X] T036 [P] Create phase3-frontend/components/AuthGuard.tsx for protected route wrapper
- [X] T037 [P] Create phase3-frontend/components/LoadingSpinner.tsx for loading states

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Task via Conversation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks through natural language commands like "Add a task to buy groceries tomorrow"

**Independent Test**:
1. User sends message "Add a task to buy milk"
2. System creates task in phase2-backend database
3. User receives confirmation "I've added 'buy milk' to your tasks"
4. Verify task exists in phase2-backend via existing Phase 2 frontend

### MCP Tool: add_task

- [X] T038 [US1] Create phase3-mcp-server/app/tools/add_task.py with add_task MCP tool handler
- [X] T039 [US1] Implement add_task tool to call phase2-backend POST /api/{user_id}/tasks endpoint via Phase2Client
- [X] T040 [US1] Register add_task tool in phase3-mcp-server/app/server.py MCP Server
- [X] T041 [US1] Add add_task tool validation (user_id, title required; description optional)

### OpenAI Agent Integration

- [X] T042 [US1] Define add_task MCP tool schema for OpenAI function calling in phase3-backend/app/agents/openai_agent.py
- [X] T043 [US1] Implement MCP tool invocation flow in phase3-backend/app/agents/mcp_client.py for add_task
- [X] T044 [US1] Add natural language intent detection for task creation commands in OpenAI system prompt

### Chat Endpoint

- [X] T045 [US1] Create phase3-backend/app/routes/chat.py with POST /api/{user_id}/chat endpoint
- [X] T046 [US1] Implement chat endpoint flow: validate JWT, get/create conversation, fetch history, store user message
- [X] T047 [US1] Integrate OpenAI Agents SDK call in chat endpoint with add_task tool
- [X] T048 [US1] Store assistant response message after tool execution
- [X] T049 [US1] Return formatted response with conversation_id, message, timestamp, tool_calls

### Frontend Chat Interface

- [X] T050 [US1] Create phase3-frontend/components/ChatKitWrapper.tsx with ChatKit React integration
- [X] T051 [US1] Implement ChatKit session management and API configuration
- [X] T052 [US1] Create phase3-frontend/app/chat/page.tsx with main chat interface
- [X] T053 [US1] Create phase3-frontend/app/api/chatkit/session/route.ts for ChatKit client secret generation
- [X] T054 [US1] Add error handling and loading states in chat interface

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add tasks via natural language and receive confirmations

---

## Phase 4: User Story 2 - List Tasks via Conversation (Priority: P2)

**Goal**: Enable users to view their tasks through conversational queries like "What tasks do I have?" or "Show me my incomplete tasks"

**Independent Test**:
1. User creates 3 tasks via Phase 2 UI or US1 chat
2. User sends message "What are my tasks?"
3. System retrieves all tasks from phase2-backend
4. User receives formatted list with all 3 tasks

### MCP Tool: list_tasks

- [X] T055 [P] [US2] Create phase3-mcp-server/app/tools/list_tasks.py with list_tasks MCP tool handler
- [X] T056 [US2] Implement list_tasks tool to call phase2-backend GET /api/{user_id}/tasks endpoint via Phase2Client
- [X] T057 [US2] Register list_tasks tool in phase3-mcp-server/app/server.py MCP Server
- [X] T058 [US2] Add list_tasks tool optional filtering (completed status parameter)

### OpenAI Agent Integration

- [X] T059 [US2] Define list_tasks MCP tool schema for OpenAI function calling in phase3-backend/app/agents/openai_agent.py
- [X] T060 [US2] Implement MCP tool invocation flow in phase3-backend/app/agents/mcp_client.py for list_tasks
- [X] T061 [US2] Add natural language intent detection for task listing queries in OpenAI system prompt
- [X] T062 [US2] Implement task formatting logic in agent to present lists conversationally

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can add tasks and view their task list via chat

---

## Phase 5: User Story 3 - Complete Task via Conversation (Priority: P3)

**Goal**: Enable users to mark tasks complete through conversational commands like "I finished buying groceries" or "Mark task X as done"

**Independent Test**:
1. User creates task "Buy groceries" via US1
2. User sends message "I finished buying groceries"
3. System identifies task by title and marks it complete in phase2-backend
4. User receives confirmation "Task 'Buy groceries' marked as complete"
5. Verify task status in Phase 2 UI shows completed

### MCP Tool: complete_task

- [X] T063 [P] [US3] Create phase3-mcp-server/app/tools/complete_task.py with complete_task MCP tool handler
- [X] T064 [US3] Implement complete_task tool to call phase2-backend PATCH /api/{user_id}/tasks/{task_id}/complete endpoint via Phase2Client
- [X] T065 [US3] Register complete_task tool in phase3-mcp-server/app/server.py MCP Server
- [X] T066 [US3] Add complete_task tool validation (user_id, task_id, completed status required)

### OpenAI Agent Integration

- [X] T067 [US3] Define complete_task MCP tool schema for OpenAI function calling in phase3-backend/app/agents/openai_agent.py
- [X] T068 [US3] Implement MCP tool invocation flow in phase3-backend/app/agents/mcp_client.py for complete_task
- [X] T069 [US3] Add natural language intent detection for task completion commands in OpenAI system prompt
- [X] T070 [US3] Implement task identification logic (by title or ID) in agent conversation handling
- [X] T071 [US3] Add ambiguity detection - ask clarifying questions if multiple matching tasks found

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - full create, list, complete workflow via chat

---

## Phase 6: User Story 4 - Update Task via Conversation (Priority: P4)

**Goal**: Enable users to modify task details through conversational commands like "Change the deadline for X to tomorrow" or "Rename task Y to Z"

**Independent Test**:
1. User creates task "Review report" via US1
2. User sends message "Rename 'Review report' to 'Review quarterly report'"
3. System updates task title in phase2-backend
4. User receives confirmation with new title
5. Verify updated title in Phase 2 UI

### MCP Tool: update_task

- [X] T072 [P] [US4] Create phase3-mcp-server/app/tools/update_task.py with update_task MCP tool handler
- [X] T073 [US4] Implement update_task tool to call phase2-backend PUT /api/{user_id}/tasks/{task_id} endpoint via Phase2Client
- [X] T074 [US4] Register update_task tool in phase3-mcp-server/app/server.py MCP Server
- [X] T075 [US4] Add update_task tool validation (user_id, task_id required; title and description optional)

### OpenAI Agent Integration

- [X] T076 [US4] Define update_task MCP tool schema for OpenAI function calling in phase3-backend/app/agents/openai_agent.py
- [X] T077 [US4] Implement MCP tool invocation flow in phase3-backend/app/agents/mcp_client.py for update_task
- [X] T078 [US4] Add natural language intent detection for task update commands in OpenAI system prompt
- [X] T079 [US4] Implement field extraction logic (distinguish title changes from description changes)

**Checkpoint**: User Stories 1-4 complete - full CRUD except delete available via chat

---

## Phase 7: User Story 5 - Delete Task via Conversation (Priority: P5)

**Goal**: Enable users to remove tasks through conversational commands with confirmation prompts like "Delete my task about groceries"

**Independent Test**:
1. User creates task "Buy groceries" via US1
2. User sends message "Delete the groceries task"
3. System asks confirmation "Are you sure you want to delete 'Buy groceries'?"
4. User confirms "Yes"
5. System deletes task from phase2-backend
6. User receives confirmation "Task deleted successfully"
7. Verify task no longer exists in Phase 2 UI

### MCP Tool: delete_task

- [X] T080 [P] [US5] Create phase3-mcp-server/app/tools/delete_task.py with delete_task MCP tool handler
- [X] T081 [US5] Implement delete_task tool to call phase2-backend DELETE /api/{user_id}/tasks/{task_id} endpoint via Phase2Client
- [X] T082 [US5] Register delete_task tool in phase3-mcp-server/app/server.py MCP Server
- [X] T083 [US5] Add delete_task tool validation (user_id, task_id required)

### OpenAI Agent Integration

- [X] T084 [US5] Define delete_task MCP tool schema for OpenAI function calling in phase3-backend/app/agents/openai_agent.py
- [X] T085 [US5] Implement MCP tool invocation flow in phase3-backend/app/agents/mcp_client.py for delete_task
- [X] T086 [US5] Add natural language intent detection for task deletion commands in OpenAI system prompt
- [X] T087 [US5] Implement confirmation prompt logic before executing delete_task tool
- [X] T088 [US5] Add conversation context tracking for multi-turn confirmation flow

**Checkpoint**: All user stories complete - full CRUD operations available via natural language chat interface

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Error Handling & Resilience

- [X] T089 [P] Add OpenAI API error handling with exponential backoff in phase3-backend/app/agents/openai_agent.py
- [X] T090 [P] Add rate limiting (10 req/min per user) to phase3-backend/app/routes/chat.py
- [X] T091 [P] Implement graceful degradation when OpenAI API unavailable in chat endpoint
- [X] T092 [P] Add standardized error response format in phase3-backend/app/routes/chat.py
- [X] T093 [P] Add error handling for phase2-backend unavailability in phase3-mcp-server tools
- [X] T094 [P] Add user-friendly error messages for all failure scenarios

### Security & Validation

- [X] T095 [P] Add input validation for message length (1-2000 chars) in chat endpoint
- [X] T096 [P] Add user isolation verification in all MCP tools (user_id from JWT matches request)
- [X] T097 [P] Add sanitization for user messages before storing in database
- [X] T098 [P] Verify JWT secret matches across phase2-backend, phase3-backend, phase3-mcp-server

### Performance & Optimization

- [X] T099 [P] Add database connection pooling configuration in phase3-backend/app/db.py
- [X] T100 [P] Verify indexes on conversations(user_id, created_at) and messages(conversation_id, created_at)
- [X] T101 [P] Add conversation history pagination (limit to last 20 messages)
- [ ] T102 [P] Implement caching strategy for frequently used phase2-backend data (optional)

### Deployment & Configuration

- [X] T103 [P] Create phase3-backend README.md with setup instructions, environment variables, deployment guide
- [X] T104 [P] Create phase3-mcp-server README.md with setup instructions, tool documentation, testing guide
- [X] T105 [P] Create phase3-frontend README.md with setup instructions, ChatKit configuration, deployment guide
- [ ] T106 Deploy phase3-mcp-server to Railway and verify health endpoint
- [ ] T107 Deploy phase3-backend to Railway and verify health endpoint
- [ ] T108 Configure Railway environment variables for phase3-backend (DATABASE_URL, OPENAI_API_KEY, JWT_SECRET, MCP_SERVER_URL)
- [ ] T109 Configure Railway environment variables for phase3-mcp-server (PHASE2_BACKEND_URL, JWT_SECRET)
- [ ] T110 Deploy phase3-frontend to Vercel and verify build success
- [ ] T111 Configure Vercel environment variables for phase3-frontend (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET)

### Integration Testing & Validation

- [X] T112 Run all Phase 2 backend tests to verify backward compatibility (CRITICAL)
- [X] T113 Manual end-to-end test: Create task via chat, verify in Phase 2 UI
- [X] T114 Manual end-to-end test: List tasks via chat, compare with Phase 2 UI
- [X] T115 Manual end-to-end test: Complete task via chat, verify in Phase 2 UI
- [X] T116 Manual end-to-end test: Update task via chat, verify in Phase 2 UI
- [X] T117 Manual end-to-end test: Delete task via chat with confirmation, verify in Phase 2 UI
- [ ] T118 Test concurrent users (10+ simultaneous chat sessions) for conversation isolation
- [ ] T119 Test error scenarios: OpenAI down, phase2-backend down, invalid JWT, rate limiting
- [ ] T120 Test ambiguous commands and clarification prompts

### Documentation & Demo

- [ ] T121 [P] Update root README.md with Phase 3 architecture overview and service descriptions
- [ ] T122 [P] Create deployment guide with Railway + Vercel setup steps
- [ ] T123 [P] Document API contracts for chat endpoint and MCP tools
- [ ] T124 Record 2-3 minute demo video showing natural language task management (add, list, complete, update, delete)
- [ ] T125 Create Phase 3 retrospective documenting lessons learned, challenges, solutions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) OR sequentially in priority order
  - Each user story is independently testable after completion
- **Polish (Phase 8)**: Depends on desired user stories being complete (at minimum US1 for MVP)

### User Story Dependencies

- **User Story 1 (P1 - Add Task)**: Can start after Foundational - No dependencies on other stories ✅ MVP
- **User Story 2 (P2 - List Tasks)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P3 - Complete Task)**: Can start after Foundational - No dependencies, but US2 helpful for finding tasks
- **User Story 4 (P4 - Update Task)**: Can start after Foundational - No dependencies, but US2 helpful for finding tasks
- **User Story 5 (P5 - Delete Task)**: Can start after Foundational - No dependencies, but US2 helpful for finding tasks

**Note**: While US2-5 benefit from having task listing capability, they can all be tested independently by creating test tasks via Phase 2 UI or directly in database.

### Within Each User Story

1. MCP tool implementation (phase3-mcp-server)
2. OpenAI agent integration (phase3-backend)
3. Chat endpoint integration (phase3-backend)
4. Frontend updates (phase3-frontend) - only needed for US1 initial setup

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T004, T005, T006 (pyproject.toml / package.json initialization)
- T007, T008, T009 (.env.example files)
- T010, T011, T012 (deployment configs)

**Foundational Phase (Phase 2)**:
- T020, T021, T022, T023, T024 (phase3-backend foundation components)
- T032, T033, T034, T035, T036, T037 (phase3-frontend foundation components)

**User Stories**:
- All 5 user stories (Phases 3-7) can be developed in parallel by different team members after Phase 2 completes
- Within each story: MCP tool (T038-T041 for US1) can be developed independently from frontend components

**Polish Phase (Phase 8)**:
- T089-T094 (error handling tasks)
- T095-T098 (security tasks)
- T099-T102 (performance tasks)
- T103-T105 (documentation tasks)
- T121-T123 (additional documentation)

---

## Parallel Example: User Story 1 (Add Task)

```bash
# After Foundational phase completes, launch US1 components in parallel:

# Team Member A - MCP Tool
Task: "T038 Create phase3-mcp-server/app/tools/add_task.py with add_task MCP tool handler"
Task: "T039 Implement add_task tool to call phase2-backend POST /api/{user_id}/tasks"

# Team Member B - OpenAI Integration
Task: "T042 Define add_task MCP tool schema for OpenAI function calling"
Task: "T043 Implement MCP tool invocation flow for add_task"

# Team Member C - Chat Endpoint
Task: "T045 Create phase3-backend/app/routes/chat.py with POST /api/{user_id}/chat"
Task: "T046 Implement chat endpoint flow: validate JWT, conversation management"

# After individual components ready, integrate:
Task: "T047 Integrate OpenAI Agents SDK call in chat endpoint with add_task tool"
Task: "T048 Store assistant response message after tool execution"

# Frontend (depends on backend being ready):
Task: "T050 Create phase3-frontend/components/ChatKitWrapper.tsx"
Task: "T052 Create phase3-frontend/app/chat/page.tsx"
```

---

## Parallel Example: Multiple User Stories

```bash
# After Foundational phase completes, develop stories in parallel:

# Team Member A - US1 (Priority 1)
Phase 3: User Story 1 - Add Task (T038-T054)

# Team Member B - US2 (Priority 2)
Phase 4: User Story 2 - List Tasks (T055-T062)

# Team Member C - US3 (Priority 3)
Phase 5: User Story 3 - Complete Task (T063-T071)

# Each developer works on their story independently
# Stories can be merged and deployed as they complete
# No blocking dependencies between stories
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**Fastest path to demonstrable value**:

1. Complete **Phase 1: Setup** (T001-T014) - ~1-2 hours
2. Complete **Phase 2: Foundational** (T015-T037) - ~4-6 hours
3. Complete **Phase 3: User Story 1** (T038-T054) - ~6-8 hours
4. **STOP and VALIDATE**: Test US1 independently
   - User can add tasks via chat: "Add a task to buy milk"
   - Task appears in Phase 2 UI
   - User receives confirmation in chat
5. Deploy to Railway/Vercel if ready
6. Record demo video showing task creation via chat

**Total MVP time**: ~12-16 hours (1-2 days for single developer)

### Incremental Delivery (Recommended)

**Build value incrementally, validating each story**:

1. **Week 1**: Complete Setup + Foundational (Phase 1-2) → Foundation ready
2. **Week 2**: Add User Story 1 (Phase 3) → Test independently → Deploy/Demo **MVP!**
3. **Week 3**: Add User Story 2 (Phase 4) → Test independently → Deploy/Demo
4. **Week 4**: Add User Stories 3-5 (Phases 5-7) → Test independently → Deploy/Demo
5. **Week 5**: Polish phase (Phase 8) → Production-ready

Each story adds value without breaking previous stories. Can stop after any phase and have working system.

### Parallel Team Strategy

**With 3+ developers, maximize throughput**:

1. **Day 1-2**: Entire team completes Setup + Foundational together (Phase 1-2)
2. **Day 3+**: Once Foundational is done:
   - **Developer A**: User Story 1 (Phase 3) - Add Task
   - **Developer B**: User Story 2 (Phase 4) - List Tasks
   - **Developer C**: User Story 3 (Phase 5) - Complete Task
   - **Developer D**: User Story 4 & 5 (Phase 6-7) - Update & Delete
3. **Final Integration**: Team merges stories, validates independently, then together
4. **Polish**: Team collaborates on Phase 8 polish tasks

**Total parallel time**: ~3-5 days with 3-4 developers

---

## Critical Path Analysis

**Blocking Tasks** (must complete before anything else):
- T001-T014: Setup phase (sequential setup of all 3 services)
- T015-T037: Foundational phase (database, core infrastructure)

**Critical for MVP (User Story 1)**:
- T015-T017: Database migrations (blocks conversation storage)
- T018-T024: phase3-backend foundation (blocks chat endpoint)
- T025-T028: phase3-mcp-server foundation (blocks MCP tools)
- T029-T031: AI integration foundation (blocks OpenAI agent)
- T032-T037: phase3-frontend foundation (blocks chat UI)
- T038-T054: User Story 1 implementation (creates MVP)

**Critical for Production**:
- T089-T094: Error handling (prevents poor UX)
- T095-T098: Security hardening (prevents vulnerabilities)
- T106-T111: Deployment (makes system accessible)
- T112: Phase 2 backward compatibility test (CRITICAL - prevents regression)

**Deferrable** (nice-to-have, can add later):
- T099-T102: Performance optimization (can optimize after launch)
- T121-T125: Documentation (can improve iteratively)
- User Stories 4-5 (Update/Delete) - can ship MVP without these

---

## Task Count Summary

**Total Tasks**: 125 tasks

**By Phase**:
- Phase 1 (Setup): 14 tasks
- Phase 2 (Foundational): 23 tasks
- Phase 3 (US1 - Add Task): 17 tasks ← MVP
- Phase 4 (US2 - List Tasks): 8 tasks
- Phase 5 (US3 - Complete Task): 9 tasks
- Phase 6 (US4 - Update Task): 8 tasks
- Phase 7 (US5 - Delete Task): 9 tasks
- Phase 8 (Polish): 37 tasks

**By User Story**:
- US1 (Add Task): 17 tasks - MVP critical
- US2 (List Tasks): 8 tasks
- US3 (Complete Task): 9 tasks
- US4 (Update Task): 8 tasks
- US5 (Delete Task): 9 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phase

**MVP Scope** (Setup + Foundational + US1 + Essential Polish):
- Phase 1: 14 tasks
- Phase 2: 23 tasks
- Phase 3 (US1): 17 tasks
- Phase 8 (Essential polish): ~20 tasks (deployment, error handling, backward compatibility)
- **Total for MVP**: ~74 tasks

---

## Notes

- **[P] tasks** = different files, no dependencies within phase - can run in parallel
- **[Story] label** maps task to specific user story for traceability and independent testing
- **Phase 2 must remain unchanged** - all Phase 2 tests must pass before deployment (T112 critical!)
- Each user story should be independently completable and testable
- Stop at any checkpoint to validate story independently
- Avoid cross-story dependencies that break independence
- Commit after each logical group of tasks
- Tests are OPTIONAL - not included since not explicitly requested in spec
- Prefer incremental delivery over big-bang integration
