---
id: 0003
title: ChatKit Migration Planning Session
stage: plan
date: 2025-12-26
surface: terminal
model: claude-sonnet-4-5
feature: 003-chatkit-migration
branch: main
user: majid
command: /sp.plan
labels: [planning, architecture, chatkit, migration]
links:
  spec: specs/003-chatkit-migration/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  created:
    - specs/003-chatkit-migration/plan.md
    - specs/003-chatkit-migration/research.md
    - specs/003-chatkit-migration/data-model.md
    - specs/003-chatkit-migration/contracts/chatkit-api.yaml
    - specs/003-chatkit-migration/quickstart.md
  modified: []
  deleted: []
tests:
  unit: []
  integration: []
  e2e:
    - Test Scenario 1: User Authentication Flow (P2)
    - Test Scenario 2: Create Task via Natural Language (P1)
    - Test Scenario 3: List Tasks (P1)
    - Test Scenario 4: Complete Task (P1)
    - Test Scenario 5: Conversation History Persistence (P3)
    - Test Scenario 6: Update Task (P1)
    - Test Scenario 7: Delete Task with Confirmation (P1)
    - Test Scenario 8: MCP Tag Extraction (P4)
    - Test Scenario 9: Error Handling (Preservation)
    - Test Scenario 10: Concurrent Users (SC-010)
    - Test Scenario 11: Custom Theming (SC-007)
    - Test Scenario 12: Regression Testing (SC-008)
---

## Prompt

Plan the implementation of migrating Phase 3 chatbot interface from custom implementation to OpenAI ChatKit for hackathon compliance.

### Specification Reference

Feature: 003-chatkit-migration
Spec file: specs/003-chatkit-migration/spec.md

### Current Implementation (To Be Replaced)

**Phase 3 Frontend** (phase3-frontend/):
- Custom `<ChatInterface>` component with message history display
- Custom `<ChatMessage>` component for rendering user/assistant messages
- `/app/chat/page.tsx` - Chat page using custom components

**Phase 3 Backend** (phase3-backend/):
- Custom `/api/chat` endpoint handling OpenAI API calls directly
- Custom conversation management and message persistence
- Direct OpenAI API integration with streaming

**Phase 3 MCP Server** (phase3-mcp-server/):
- MCP tools for task operations (add_task, list_tasks, complete_task, update_task, delete_task)
- Integrated with Phase 2 backend for task persistence

### Migration Requirements

**Replace Custom Implementation With**:

**Frontend**:
- `@openai/chatkit-react` package
- `<ChatKit>` component from official library
- `useChatKit()` hook for session management

**Backend**:
- `openai-chatkit` (chatkit-python) package
- `ChatKitServer` base class implementation
- `/chatkit` endpoint following ChatKit protocol
- `/api/chatkit/session` endpoint for session creation with JWT

**Preserve**:
- All existing MCP tool functionality (5 task operations)
- Better-Auth JWT authentication (24-hour sessions)
- Conversation history persistence (PostgreSQL)
- User isolation and data scoping
- Phase 2 backward compatibility (zero changes to phase2-backend)

### Key Questions to Address in Plan

1. **Architecture**: How do the three services (phase2-backend, phase3-backend, phase3-mcp-server) interact after migration?
2. **Authentication Flow**: How does JWT token flow through ChatKit session creation?
3. **Streaming**: How does Progressive JSON streaming work with ChatKit?
4. **Conversation Persistence**: How does ChatKit session mapping work with PostgreSQL conversations table?
5. **MCP Integration**: How do ChatKit tools connect to existing MCP client?
6. **Database Migration**: What changes needed for session_id mapping?
7. **Testing Strategy**: How to validate all 12 test scenarios?
8. **Deployment**: What's the rollout strategy?

### Expected Deliverables

1. **Research Document** (research.md):
   - Verify ChatKit packages exist and are production-ready
   - Document streaming mechanisms
   - Investigate authentication integration patterns
   - Research MCP tool integration with ChatKit

2. **Data Model** (data-model.md):
   - Document session_id column addition to conversations table
   - Define session mapping logic
   - Specify data cleanup strategy

3. **API Contracts** (contracts/chatkit-api.yaml):
   - OpenAPI spec for `/api/chatkit/session` endpoint
   - Document ChatKit protocol messages
   - Define request/response schemas

4. **Testing Guide** (quickstart.md):
   - 12 detailed test scenarios covering all user stories
   - Performance benchmarks
   - Security validation steps
   - Regression testing checklist

5. **Implementation Plan** (plan.md):
   - Constitution compliance check
   - Architecture diagrams with data flow
   - Phase-by-phase implementation steps
   - Risk mitigation strategies
   - Time estimates per phase
   - Testing strategy

### Constraints from Clarification Session

- **Streaming**: Progressive JSON (Turn objects with is_partial flag)
- **Migration Strategy**: Direct replacement (no feature flags)
- **Session Scope**: Login session lifecycle (24-hour JWT duration)
- **Data Migration**: Clean slate approach - TRUNCATE conversations CASCADE
- **Schema Restriction**: Do NOT modify tasks or users tables, CAN modify conversations/messages tables
- **Testing Level**: Comprehensive E2E testing before deployment

### Success Criteria

- Plan passes constitution compliance check (all 8 sections)
- Architecture diagram shows clear data flow between services
- All 5 phases have actionable implementation steps
- Risk mitigation strategies address all major concerns
- Testing strategy covers all 12 test scenarios
- Time estimates realistic for 10-15 hour implementation

## Response snapshot

### Phase 0: Research (Completed)

Created `research.md` documenting 8 major technical decisions:

1. **ChatKit Package Verification**: Confirmed `@openai/chatkit-react` and `openai-chatkit` (chatkit-python) are real, official packages
2. **Progressive JSON Streaming**: Designed Turn-based streaming with `is_partial` flag
3. **Authentication Integration**: JWT token flow through ChatKit session metadata
4. **MCP Tool Integration**: ChatKit Tool wrappers calling existing MCPClient methods
5. **Conversation Persistence**: Session mapping via new `session_id` column
6. **Database Migration**: SQL for adding session_id with unique index
7. **Custom Widget Support**: Optional task list rendering in chat
8. **Error Handling**: Graceful degradation strategy

### Phase 1: Design Artifacts (Completed)

**data-model.md**:
- Added `session_id TEXT` column to conversations table
- Created unique index `idx_conversations_session_id`
- Documented data access patterns (5 key queries)
- Defined data isolation rules and performance considerations

**contracts/chatkit-api.yaml**:
- OpenAPI 3.1 spec with 2 main endpoints:
  - `POST /api/chatkit/session` - Session creation with JWT auth
  - `POST /chatkit` - ChatKit protocol message handling
- Complete request/response schemas with validation rules

**quickstart.md**:
- 12 detailed test scenarios covering:
  - Authentication flow (P2)
  - Task CRUD operations (P1)
  - Conversation persistence (P3)
  - MCP tag extraction (P4)
  - Error handling, concurrency, theming, regression
- Performance benchmarks (<5s response time)
- Production readiness checklist

### Phase 2: Implementation Plan (Completed)

**plan.md** - Comprehensive 1040-line implementation plan:

**Constitution Compliance Check**: PASS (all 8 sections)
- Three-Service Architecture: phase2 unchanged ✓
- Stateless Architecture: PostgreSQL-backed history ✓
- Single Source of Truth: phase2-backend authoritative ✓
- Backward Compatibility: Zero Phase 2 changes ✓
- All other sections: PASS ✓

**Architecture Decisions**:
```
Frontend Data Flow:
User Input → <ChatKit> → useChatKit() → /api/chatkit/session (JWT) → client_secret
         → ChatKit.js → POST /chatkit → ChatKitServer → OpenAI + MCP Tools

Backend Data Flow:
POST /chatkit → TodoChatKitServer.respond() → get_or_create_conversation()
            → fetch_history() → OpenAI API (streaming) → MCP Tools (task ops)
            → save_messages() → yield Turn(is_partial=True/False)

Database Data Flow:
ChatKit session_id → conversations.session_id → conversation_id
                  → messages (chronological history)
```

**5 Implementation Phases** (10-15 hours total):

1. **Phase 1: Backend ChatKit Server Setup** (3-4 hours)
   - Create `TodoChatKitServer` class
   - Implement `respond()` method with streaming
   - Add session creation endpoint
   - Integrate MCP tools as ChatKit tools

2. **Phase 2: Frontend ChatKit Component** (2-3 hours)
   - Install `@openai/chatkit-react`
   - Replace custom components with `<ChatKit>`
   - Implement `useChatKit()` with JWT auth
   - Apply custom theming

3. **Phase 3: Database Migration** (30 minutes)
   - Run `006_add_session_id_to_conversations.sql`
   - Truncate conversations/messages (clean slate)

4. **Phase 4: Integration & Testing** (3-4 hours)
   - Execute all 12 test scenarios
   - Validate performance benchmarks
   - Security testing
   - Regression testing

5. **Phase 5: Deployment** (1-2 hours)
   - Deploy phase3-backend to Railway
   - Deploy phase3-frontend to Vercel
   - Smoke tests in production

**Risk Mitigation**:
- ChatKit CDN failure → Host ChatKit.js locally
- OpenAI API rate limits → Implement exponential backoff
- Conversation data loss → Database backups before TRUNCATE
- Performance degradation → Connection pooling tuning

**Testing Strategy**:
- 12 manual E2E scenarios (quickstart.md)
- Automated unit tests (pytest for backend)
- Load testing (k6 for 100+ concurrent users)
- Security validation (JWT verification, rate limiting)

## Outcome

- ✅ Impact: Complete migration plan created with 5 implementation phases, detailed architecture diagrams, and comprehensive testing strategy. All planning artifacts delivered (research.md, data-model.md, contracts/chatkit-api.yaml, quickstart.md, plan.md).

- 🧪 Tests: 12 detailed E2E test scenarios defined in quickstart.md covering all user stories (P1-P4), edge cases, performance benchmarks, security validation, and regression testing. Automated testing strategy documented.

- 📁 Files: Created 5 planning documents totaling ~2500 lines of comprehensive technical documentation. No code files modified (planning phase only).

- 🔁 Next prompts:
  1. Run `/sp.tasks` to generate dependency-ordered task breakdown from plan.md
  2. Begin Phase 1 implementation (Backend ChatKit Server Setup)
  3. Execute comprehensive testing per quickstart.md

- 🧠 Reflection: Planning session successfully addressed all unknowns from specification. Key achievements:
  - Verified ChatKit packages are production-ready
  - Designed Progressive JSON streaming architecture
  - Mapped JWT authentication through ChatKit sessions
  - Preserved all existing MCP tool functionality
  - Maintained Phase 2 backward compatibility (zero changes)
  - Clean slate migration approach simplifies data strategy
  - Direct replacement strategy reduces implementation complexity
  - Constitution compliance validated (all 8 sections PASS)

  Critical decisions documented:
  - No schema changes to tasks/users tables (per user constraint)
  - Session mapping via conversations.session_id column
  - Stateless backend with PostgreSQL-backed history
  - 24-hour conversation lifecycle (aligned with JWT expiry)
  - Comprehensive E2E testing before deployment

  Plan is ready for task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None during planning phase. WebFetch encountered 403 errors on some documentation sites but sufficient information was obtained from alternative sources (GitHub repositories, npm pages).

- Graders run and results (PASS/FAIL):
  - Constitution Compliance Check: PASS (all 8 sections)
  - Specification Validation: PASS (all requirements addressed)
  - Architecture Validation: PASS (three-service architecture preserved)
  - Testing Coverage: PASS (12 scenarios cover all user stories)

- Prompt variant (if applicable): Standard `/sp.plan` workflow with comprehensive context from previous clarification session

- Next experiment (smallest change to try): N/A - planning phase complete, ready for task generation (`/sp.tasks`) and implementation
