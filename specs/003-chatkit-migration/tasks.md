# Tasks: ChatKit Migration

**Input**: Design documents from `/specs/003-chatkit-migration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Per specification requirements, comprehensive E2E testing is required before deployment. Implementation tasks include setup for these tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Multi-service web app**: `phase3-frontend/`, `phase3-backend/`, `backend/migrations/`
- Frontend: Next.js 16 + React 19 + ChatKit
- Backend: FastAPI + ChatKit Python SDK

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and package installation

- [X] T001 Install @openai/chatkit-react package in phase3-frontend/package.json
- [X] T002 Install openai-chatkit package in phase3-backend/requirements.txt
- [X] T003 [P] Add ChatKit CDN script to phase3-frontend/app/layout.tsx head section
- [X] T004 [P] Create phase3-backend/app/chatkit/ package directory with __init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create database migration file backend/migrations/006_add_session_id_to_conversations.sql
- [X] T006 Apply database migration to add session_id column to conversations table
- [X] T007 Update Conversation model in phase3-backend/app/models/chat.py to include session_id field
- [X] T008 Create ChatKitServer base implementation in phase3-backend/app/chatkit/server.py
- [X] T009 Create MCP tools wrapper module in phase3-backend/app/chatkit/tools.py
- [X] T010 Create /api/chatkit/session endpoint in phase3-backend/app/routes/chatkit.py
- [X] T011 Create /chatkit POST endpoint in phase3-backend/app/routes/chatkit.py
- [X] T012 Update phase3-backend/app/main.py to register chatkit routes and remove old chat routes
- [X] T013 Delete old chat route file phase3-backend/app/routes/chat.py
- [X] T014 [P] Update phase3-frontend/lib/api.ts to add getChatKitSession function

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Manage Tasks via ChatKit Interface (Priority: P1) 🎯 MVP

**Goal**: Enable all task management operations (create, list, complete, update, delete) through official ChatKit component, maintaining identical functionality to custom implementation

**Independent Test**: Open the app, send messages like "Add task to buy groceries", "Show my tasks", "Mark 'buy groceries' as done", verify all operations work identically to previous custom implementation

### Implementation for User Story 1

- [X] T015 [P] [US1] Implement add_task tool definition in phase3-backend/app/chatkit/tools.py
- [X] T016 [P] [US1] Implement list_tasks tool definition in phase3-backend/app/chatkit/tools.py
- [X] T017 [P] [US1] Implement complete_task tool definition in phase3-backend/app/chatkit/tools.py
- [X] T018 [P] [US1] Implement update_task tool definition in phase3-backend/app/chatkit/tools.py
- [X] T019 [P] [US1] Implement delete_task tool definition in phase3-backend/app/chatkit/tools.py
- [X] T020 [US1] Bind MCP tools to TodoChatKitServer in phase3-backend/app/chatkit/server.py
- [X] T021 [US1] Implement respond() method with OpenAI chat.completions streaming in phase3-backend/app/chatkit/server.py
- [X] T022 [US1] Implement progressive JSON streaming with Turn objects (is_partial=True) in respond() method
- [X] T023 [US1] Add tool call handling and execution in respond() method
- [ ] T024 [US1] Replace ChatInterface with ChatKit component in phase3-frontend/app/chat/page.tsx
- [ ] T025 [US1] Configure useChatKit hook with getClientSecret callback in phase3-frontend/app/chat/page.tsx
- [ ] T026 [US1] Delete custom ChatInterface component file phase3-frontend/components/ChatInterface.tsx
- [ ] T027 [US1] Delete custom ChatMessage component file phase3-frontend/components/ChatMessage.tsx
- [ ] T028 [US1] Apply custom theming to ChatKit component matching Phase 3 design (Tailwind colors)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - all task operations work through ChatKit

---

## Phase 4: User Story 2 - Seamless Authentication with ChatKit (Priority: P2)

**Goal**: Enable automatic authentication through Better-Auth JWT without additional login steps or token management

**Independent Test**: Log in through Better-Auth, access ChatKit interface, verify JWT token correctly passed to backend allowing access to user-specific tasks

### Implementation for User Story 2

- [ ] T029 [US2] Implement JWT validation in /api/chatkit/session endpoint using existing get_current_user dependency
- [ ] T030 [US2] Create ChatKit session with user_id embedded in metadata in /api/chatkit/session endpoint
- [ ] T031 [US2] Implement get_user_id_from_session() method in TodoChatKitServer class
- [ ] T032 [US2] Add user_id extraction and scoping in respond() method for all MCP tool calls
- [ ] T033 [US2] Test session expiry handling - verify re-authentication prompt when JWT expires
- [ ] T034 [US2] Test unauthenticated access - verify redirect to login page for /chat route

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - authentication seamlessly integrates with task operations

---

## Phase 5: User Story 3 - Persistent Conversation History (Priority: P3)

**Goal**: Preserve conversation history across page refreshes within login session scope (24-hour JWT duration)

**Independent Test**: Start a conversation, create tasks, refresh browser, verify previous messages and context still visible in ChatKit while login session is active

### Implementation for User Story 3

- [ ] T035 [US3] Implement get_or_create_conversation() method in ChatService using session_id mapping
- [ ] T036 [US3] Implement fetch_message_history() method in ChatService to retrieve last 20 messages
- [ ] T037 [US3] Add conversation history retrieval in respond() method before calling OpenAI
- [ ] T038 [US3] Implement save_message() calls in respond() method for both user and assistant messages
- [ ] T039 [US3] Test conversation persistence - verify history survives page refresh within same login session
- [ ] T040 [US3] Test session boundary - verify new login session creates new conversation (no history from previous session)
- [ ] T041 [US3] Test JWT expiry - verify conversation history not displayed after 24-hour JWT expiry and re-authentication

**Checkpoint**: All user stories 1-3 should now be independently functional - conversation history persists appropriately

---

## Phase 6: User Story 4 - MCP Tool Integration with ChatKit (Priority: P4)

**Goal**: Continue using MCP tools for intelligent tag extraction when users create or update tasks through ChatKit

**Independent Test**: Create task with implied tags (e.g., "Add task to meet with marketing team about Q1 campaign"), verify tags like "work", "marketing", "planning" automatically extracted

### Implementation for User Story 4

- [ ] T042 [US4] Verify MCP client integration in TodoChatKitServer constructor (reuse existing MCPClient)
- [ ] T043 [US4] Test tag extraction - create task with context clues, verify MCP server extracts relevant tags
- [ ] T044 [US4] Test MCP server unavailable scenario - verify task creation succeeds without tags with graceful message
- [ ] T045 [US4] Test tag filtering - verify "Show tasks tagged 'urgent'" correctly filters and displays tasks

**Checkpoint**: All user stories should now be independently functional - MCP integration enhances task operations

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and comprehensive testing

### Error Handling & Edge Cases

- [ ] T046 [P] Add error handling for ChatKit frontend-backend connection failures
- [ ] T047 [P] Add handling for OpenAI API rate limits and failures
- [ ] T048 [P] Add handling for database write failures with transaction rollbacks
- [ ] T049 [P] Add validation for very long conversations exceeding ChatKit message limits
- [ ] T050 [P] Add handling for rapid multiple messages before first response completes

### Performance Testing

- [ ] T051 Test response time under normal load - verify <5 seconds for all operations
- [ ] T052 Test concurrent users - verify system handles 100+ simultaneous users
- [ ] T053 Test progressive JSON delivery - verify incremental rendering works properly
- [ ] T054 Test database query performance for conversation history retrieval

### Security Testing

- [ ] T055 [P] Test JWT token validation enforcement on all endpoints
- [ ] T056 [P] Test user isolation - verify users cannot access others' conversations/tasks
- [ ] T057 [P] Test rate limiting enforcement on ChatKit endpoints
- [ ] T058 [P] Test input validation and XSS prevention
- [ ] T059 [P] Verify CORS and security headers configuration

### Regression Testing

- [ ] T060 Test Phase 2 frontend - verify task management still works at http://localhost:3000
- [ ] T061 Test Phase 2 backend endpoints - verify no breaking changes to /api/tasks
- [ ] T062 Verify no modifications to tasks or users table schemas

### Compatibility & Deployment

- [ ] T063 [P] Test browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] T064 Clear conversations and messages tables before deployment (clean slate approach)
- [ ] T065 Run all 12 test scenarios from quickstart.md
- [ ] T066 Verify all 10 success criteria from spec.md (SC-001 through SC-010)
- [ ] T067 [P] Update environment variables documentation in README
- [ ] T068 Deploy to Railway (backend) and Vercel (frontend)
- [ ] T069 Run smoke tests in production environment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for testing task operations with auth
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 for creating conversation data to persist
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on US1 for task creation to test tag extraction

### Within Each User Story

- Tool definitions (T015-T019) can run in parallel within US1
- Models/services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004)
- All tool definitions in US1 marked [P] can run in parallel (T015-T019)
- All error handling tasks marked [P] can run in parallel (T046-T050)
- All security testing tasks marked [P] can run in parallel (T055-T059)
- Different user stories cannot easily run in parallel due to dependencies on US1 functionality

---

## Parallel Example: User Story 1 Tool Definitions

```bash
# Launch all MCP tool definitions for User Story 1 together:
Task T015: "Implement add_task tool definition in phase3-backend/app/chatkit/tools.py"
Task T016: "Implement list_tasks tool definition in phase3-backend/app/chatkit/tools.py"
Task T017: "Implement complete_task tool definition in phase3-backend/app/chatkit/tools.py"
Task T018: "Implement update_task tool definition in phase3-backend/app/chatkit/tools.py"
Task T019: "Implement delete_task tool definition in phase3-backend/app/chatkit/tools.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Run basic E2E tests for task operations
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP with all task operations!)
3. Add User Story 2 → Test independently → Deploy/Demo (Now with seamless auth!)
4. Add User Story 3 → Test independently → Deploy/Demo (Now with conversation persistence!)
5. Add User Story 4 → Test independently → Deploy/Demo (Now with intelligent tag extraction!)
6. Complete Phase 7 → Comprehensive testing → Final deployment

### Testing-First Strategy (Per Specification)

Per spec requirements, comprehensive E2E testing is mandatory before deployment:

1. Complete all implementation phases
2. Execute all edge case testing (T046-T050)
3. Execute all performance testing (T051-T054)
4. Execute all security testing (T055-T059)
5. Execute all regression testing (T060-T062)
6. Execute compatibility testing (T063)
7. Run all 12 quickstart.md scenarios (T065)
8. Verify all 10 success criteria (T066)
9. Only then proceed to deployment (T068)

---

## Migration Checklist

### Pre-Deployment

- [ ] All user stories (US1-US4) implemented and tested
- [ ] All edge cases handled
- [ ] Performance benchmarks met (<5s response time, 100+ concurrent users)
- [ ] Security validation complete (JWT, user isolation, rate limiting)
- [ ] No Phase 2 regressions detected
- [ ] Browser compatibility verified
- [ ] All 12 quickstart.md scenarios passed
- [ ] All 10 spec.md success criteria validated

### Deployment Steps

1. Commit all changes to 003-chatkit-migration branch
2. Push to GitHub
3. Apply database migration (T006)
4. Clear conversations/messages tables (T064 - clean slate)
5. Railway auto-deploys phase3-backend
6. Vercel auto-deploys phase3-frontend
7. Run smoke tests in production (T069)
8. Monitor logs for errors
9. Test critical paths with real users

### Rollback Plan (If Needed)

```bash
# Revert migration commits
git revert HEAD~10..HEAD
git push

# Railway/Vercel will auto-deploy previous version
# Database rollback:
psql "$DATABASE_URL" -c "DROP INDEX IF EXISTS idx_conversations_session_id;"
psql "$DATABASE_URL" -c "ALTER TABLE conversations DROP COLUMN IF EXISTS session_id;"
```

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable
- Testing is mandatory before deployment per spec requirements
- Direct replacement strategy - custom implementation fully removed
- Clean slate approach - existing conversation data cleared
- Session scope = login session lifecycle (24-hour JWT duration)
- Preserve Phase 2 functionality - zero changes to tasks/users tables
