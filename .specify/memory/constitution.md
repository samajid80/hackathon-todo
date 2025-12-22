<!--
Sync Impact Report
==================
Version Change: 2.0.0 → 3.0.0 (MAJOR)
Ratification Date: 2025-12-09 (original Phase 1), 2025-12-10 (Phase 2)
Last Amended: 2025-12-20 (Phase 3 transition)

MAJOR VERSION BUMP RATIONALE:
This is a backward-incompatible constitutional change representing Phase 3 architecture:

Breaking Changes:
- Introduced three-service architecture (phase2-backend, phase3-backend, phase3-mcp-server)
- Added OpenAI Agents SDK and MCP Server as core technologies
- New database schema (conversations, messages tables)
- New chat endpoint and conversation history requirements
- Added stateless architecture constraints for Phase 3 services
- Added forward compatibility requirements for Phase 4 (Kubernetes)

Modified Principles:
- "Technology Stack" → EXPANDED (added OpenAI Agents SDK, MCP Server, ChatKit)
- "Full-Stack Separation" → EXPANDED (now includes 3 backend services + 2 frontends)
- "Single Source of Truth" → UPDATED (clarified service ownership boundaries)
- "Stateless Backend" → CLARIFIED (applies differently to phase2 vs phase3)
- "Forward Compatibility" → UPDATED (now targets Phase 4: Kubernetes)

Added Sections:
- Section 2.1: Three-Service Architecture (CRITICAL)
- Section 2.3: Single Source of Truth (expanded with service boundaries)
- Section 2.4: Backward Compatibility (CRITICAL - preserves Phase 2)
- Section 2.5: Separation of Concerns (service-specific responsibilities)
- Section 4: Database Schema (new Phase 3 tables)
- Section 5: MCP Tools Specification (5 required tools)
- Section 6: Non-Functional Requirements (performance, security, quality, UX)
- Section 7: Constraints & Non-Goals (explicit Phase 3 scope)
- Section 8: Service Communication Flow (architecture diagram)
- Section 9: Deployment Strategy (Railway + Vercel details)
- Section 10: Forward Compatibility (Phase 4 preparation)
- Section 11: Success Criteria (Phase 3 completion checklist)

Preserved from Phase 2:
- All Phase 2 backend code and endpoints remain unchanged
- Phase 2 frontend continues working
- Phase 2 database schema (users, tasks tables) unchanged
- Phase 2 deployment remains active

Templates Requiring Updates:
- ✅ .specify/templates/plan-template.md (constitution check now includes 3-service architecture)
- ✅ .specify/templates/spec-template.md (aligned with multi-service requirements)
- ✅ .specify/templates/tasks-template.md (supports phase2 + phase3 service paths)
- ⚠️  .claude/commands/*.md (11 files may reference Phase 2 - require manual review)

Follow-up Actions Required:
- Update all slash commands to be Phase 3 aware
- Create specs/phase3/ directory for Phase 3 features
- Archive Phase 2 constitution as .specify/memory/constitution-v2.0.0-phase2.md
- Update README.md with Phase 3 architecture overview
- Update CLAUDE.md with Phase 3 development commands

Governance Note:
All Phase 3 work must comply with this updated constitution. Phase 2 work remains
governed by v2.0.0. Phase 1 work remains governed by v1.0.0 for historical reference.
-->

# Phase 3 Constitution — AI-Powered Todo Chatbot
**Hackathon II — Spec-Driven Development**

**Version:** 3.0.0
**Ratified:** 2025-12-09 (Phase 1 original)
**Last Amended:** 2025-12-20 (Phase 3 transition)
**Status:** Active (Phase 3)

---

## 1. Purpose

Transform Phase 2 full-stack todo app into an AI-powered chatbot system using:
- OpenAI Agents SDK for AI logic
- MCP Server for tool-based task operations
- Natural language interface via OpenAI ChatKit

**Phase 2 must remain completely unchanged and functional.**

This constitution establishes the architectural rules, constraints, and required behaviors for Phase 3 development while preserving all Phase 2 functionality.

---

## 2. Core Architectural Principles

### 2.1 Three-Service Architecture (CRITICAL)

Phase 3 introduces a three-service backend architecture:

```
phase2-backend (Railway) → Existing, unchanged, authoritative for tasks
phase3-backend (Railway) → New, chat endpoint only, conversation history
phase3-mcp-server (Railway) → New, MCP tools only, calls phase2-backend

Shared: Neon PostgreSQL database
```

**Rationale:**
- **Zero risk to Phase 2 production**: Existing backend remains untouched
- **Clear service boundaries**: Each service has a single responsibility
- **Prepares for Phase 4 (Kubernetes)**: Services already separated and containerization-ready
- **Demonstrates microservices architecture**: Production-grade distributed system patterns

**Rules:**
- phase2-backend: NO code changes, NO endpoint modifications, continues serving Phase 2 frontend
- phase3-backend: ONLY chat endpoint, conversation history management, OpenAI integration
- phase3-mcp-server: ONLY MCP tools, HTTP client for phase2-backend, NO direct database access

### 2.2 Stateless Architecture (CRITICAL)

All Phase 3 services must be stateless:

- **phase3-backend**: Fetch/store conversation history from database per request, no in-memory sessions
- **phase3-mcp-server**: No in-memory state, stateless tool execution, no caching
- **No server-side sessions**: JWT for authentication only (no session stores)

**Rationale:**
- Horizontal scalability for Phase 4 Kubernetes deployment
- Service restarts do not lose data
- Load balancing without sticky sessions
- Simplified deployment and operations

### 2.3 Single Source of Truth

Clear ownership boundaries for data and operations:

- **Database (PostgreSQL)**: Only persistent store, no file-based storage
- **Tasks**: phase2-backend is authoritative for all task CRUD operations
- **MCP Tools**: MUST call phase2-backend APIs via HTTP (not DB directly)
- **Conversations**: phase3-backend owns conversation history (conversations, messages tables)
- **Users**: Better-Auth manages user storage (unchanged from Phase 2)

**Rules:**
- No logic duplication across services
- No direct database access from phase3-mcp-server
- phase2-backend remains single source of truth for tasks
- phase3-backend does not implement task logic

### 2.4 Backward Compatibility (CRITICAL)

Phase 3 MUST preserve all Phase 2 functionality:

- **Phase 2 backend code**: NO CHANGES to existing codebase
- **Phase 2 endpoints**: NO MODIFICATIONS to existing REST API
- **Phase 2 frontend**: CONTINUES WORKING without changes
- **Database schema**: EXTENDS ONLY (add conversations, messages tables)

**Verification:**
- All Phase 2 tests must continue passing
- Phase 2 frontend deployment remains active
- No breaking changes to task API contracts
- Database migrations only add new tables (no alterations to users or tasks)

### 2.5 Separation of Concerns

**phase2-backend** (existing, unchanged):
- Task CRUD operations only
- Direct database access for tasks
- JWT validation for authentication
- Serves Phase 2 frontend exclusively

**phase3-backend** (new):
- Chat endpoint only (`POST /api/{user_id}/chat`)
- OpenAI Agents SDK integration
- Conversation history management (fetch/store from DB)
- Calls phase3-mcp-server for MCP tools
- No task logic implementation

**phase3-mcp-server** (new):
- 5 MCP tools (add, list, complete, delete, update)
- HTTP client for phase2-backend REST API
- No direct database access
- Stateless tool execution
- Returns structured JSON responses

---

## 3. Technology Stack (Non-Negotiable)

| Component | Technology | Version |
|-----------|------------|---------|
| Frontend (Phase 2) | Next.js + Better-Auth | 16+ |
| Frontend (Phase 3) | OpenAI ChatKit + Next.js | 16+ |
| Backend (All) | Python FastAPI | 3.13+ |
| AI Framework | OpenAI Agents SDK | Latest |
| MCP Server | Official MCP SDK (Python) | Latest |
| ORM | SQLModel | Latest |
| Database | Neon PostgreSQL (shared) | Latest |
| Auth | Better-Auth + JWT | Latest |
| Package Manager (Python) | uv | Latest |
| Package Manager (Node) | npm | 24+ |

**Constraints:**
- Python 3.13+ with uv for all backend services
- Node 24+ for all frontend applications
- No custom MCP implementations (must use official SDK)
- No custom prompt engineering (must use OpenAI Agents SDK)

---

## 4. Database Schema

### Existing (Phase 2 - Unchanged):
- `users` table (Better-Auth managed) - NO CHANGES
- `tasks` table - NO CHANGES
  - user_id (UUID, FK to users)
  - id (UUID, PK)
  - title (VARCHAR)
  - description (TEXT)
  - completed (BOOLEAN)
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)

### New (Phase 3):
- `conversations` table
  - id (UUID, PK)
  - user_id (UUID, FK to users)
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)
  - INDEX on (user_id, created_at)

- `messages` table
  - id (UUID, PK)
  - user_id (UUID, FK to users)
  - conversation_id (UUID, FK to conversations)
  - role (VARCHAR) - "user" | "assistant" | "system"
  - content (TEXT)
  - created_at (TIMESTAMP)
  - INDEX on (conversation_id, created_at)
  - INDEX on (user_id, created_at)

**Migration Rules:**
- Only ADD new tables (conversations, messages)
- NO alterations to existing tables
- NO deletions of existing columns
- Indexes required for query performance

---

## 5. MCP Tools Specification

The phase3-mcp-server MUST expose exactly 5 tools with the following contracts:

### 5.1 add_task
**Purpose**: Create new task
**Parameters**:
- `user_id` (str, required): User identifier
- `title` (str, required): Task title (1-200 chars)
- `description` (str, optional): Task description (0-2000 chars)
- `completed` (bool, optional): Initial completion status (default: false)

**Behavior**: HTTP POST to phase2-backend `/api/{user_id}/tasks`
**Returns**: Task object (id, user_id, title, description, completed, created_at, updated_at)

### 5.2 list_tasks
**Purpose**: Retrieve tasks with optional filtering
**Parameters**:
- `user_id` (str, required): User identifier
- `completed` (bool, optional): Filter by completion status

**Behavior**: HTTP GET to phase2-backend `/api/{user_id}/tasks?completed={status}`
**Returns**: Array of task objects

### 5.3 complete_task
**Purpose**: Toggle task completion status
**Parameters**:
- `user_id` (str, required): User identifier
- `task_id` (str, required): Task identifier
- `completed` (bool, required): New completion status

**Behavior**: HTTP PATCH to phase2-backend `/api/{user_id}/tasks/{task_id}/complete`
**Returns**: Updated task object

### 5.4 delete_task
**Purpose**: Remove task permanently
**Parameters**:
- `user_id` (str, required): User identifier
- `task_id` (str, required): Task identifier

**Behavior**: HTTP DELETE to phase2-backend `/api/{user_id}/tasks/{task_id}`
**Returns**: Success confirmation

### 5.5 update_task
**Purpose**: Modify task title or description
**Parameters**:
- `user_id` (str, required): User identifier
- `task_id` (str, required): Task identifier
- `title` (str, optional): New title (1-200 chars)
- `description` (str, optional): New description (0-2000 chars)

**Behavior**: HTTP PUT to phase2-backend `/api/{user_id}/tasks/{task_id}`
**Returns**: Updated task object

**Tool Implementation Rules:**
- All tools are stateless (no caching, no sessions)
- All tools call phase2-backend REST API via HTTP
- All tools validate user_id matches JWT token
- All tools return structured JSON responses
- No direct database access from MCP server

---

## 6. Non-Functional Requirements

### 6.1 Performance
- Chat response typical latency: < 5 seconds
- Database queries must use proper indexes (user_id, created_at)
- Handle OpenAI rate limits gracefully with exponential backoff
- MCP tool calls should complete within 2 seconds typical

### 6.2 Security
- JWT validation on all authenticated endpoints
- User isolation enforced (cannot access others' tasks or conversations)
- OpenAI API key in environment variables only (never hardcoded)
- No PII beyond task content sent to OpenAI
- All HTTP communication between services uses HTTPS in production
- Environment-based secrets management (Railway secrets)

### 6.3 Quality
- All Phase 2 tests continue passing (no regressions)
- New tests for chat endpoint (conversation creation, history retrieval)
- New tests for MCP tools (all 5 tools with success/error cases)
- Natural language command tests (e.g., "add task buy milk")
- Integration tests across all 3 services

### 6.4 User Experience
- Conversational, friendly AI responses
- Clear confirmation messages for actions ("Task 'buy milk' created successfully")
- Ask for clarification on ambiguous commands ("Did you mean complete task X or delete task X?")
- Graceful error handling (friendly messages, not technical stack traces)
- Preserve conversation context across messages

---

## 7. Constraints & Non-Goals

### Constraints:
- ❌ **NO changes** to phase2-backend code (zero modifications)
- ❌ **NO direct database access** from phase3-mcp-server (HTTP only)
- ❌ **NO shared code** between Phase 2 and Phase 3 services (separate codebases)
- ✅ **MUST use** OpenAI Agents SDK (not custom prompts or LangChain)
- ✅ **MUST use** Official MCP SDK (not custom implementation)
- ✅ **MUST preserve** all Phase 2 functionality

### Out of Scope (Phase 3):
- Voice commands (bonus feature, not required)
- Multi-language support (bonus feature, not required)
- Docker/Kubernetes deployment (Phase 4)
- Kafka/Dapr event streaming (Phase 5)
- Streaming chat responses (future enhancement)
- Task sharing between users
- Real-time collaboration

---

## 8. Service Communication Flow

```
User (Browser)
  ↓
phase3-frontend (ChatKit UI)
  ↓ POST /api/{user_id}/chat
  ↓ { message: "add task buy milk" }
  ↓
phase3-backend (FastAPI)
  ├─→ 1. Validate JWT token
  ├─→ 2. Fetch conversation history (PostgreSQL)
  ├─→ 3. Call OpenAI Agents SDK
  │     ↓ Agent determines tool needed
  │     ↓ Request MCP tool execution
  │     ↓
  ├─→ 4. Call phase3-mcp-server
  │     ↓
phase3-mcp-server (MCP Tools)
  ├─→ Tool: add_task(user_id, "buy milk")
  ├─→ HTTP POST → phase2-backend /api/{user_id}/tasks
  │     ↓
  │   phase2-backend (FastAPI)
  │     ├─→ Validate JWT
  │     ├─→ Insert task into PostgreSQL
  │     └─→ Return task object
  │     ↓
  └─→ Return tool result to phase3-backend
        ↓
phase3-backend
  ├─→ 5. Receive tool result from MCP
  ├─→ 6. OpenAI generates response
  ├─→ 7. Store user message + assistant response (PostgreSQL)
  └─→ 8. Return response to frontend
        ↓
phase3-frontend
  └─→ Display: "Task 'buy milk' created successfully!"
```

---

## 9. Deployment Strategy

### Backend Services (Railway):
1. **phase2-backend** - Railway (existing, no changes)
   - Endpoint: `https://phase2-backend.railway.app`
   - Environment: .env with DATABASE_URL, JWT_SECRET, CORS_ORIGINS

2. **phase3-backend** - Railway (new deployment)
   - Endpoint: `https://phase3-backend.railway.app`
   - Environment: .env with DATABASE_URL, JWT_SECRET, OPENAI_API_KEY, PHASE2_BACKEND_URL, MCP_SERVER_URL

3. **phase3-mcp-server** - Railway (new deployment)
   - Endpoint: `https://phase3-mcp-server.railway.app`
   - Environment: .env with PHASE2_BACKEND_URL

### Frontend Applications (Vercel):
1. **phase2-frontend** - Vercel (existing, no changes)
   - URL: `https://hackathon-todo-phase2.vercel.app`
   - Environment: .env.local with BACKEND_URL, BETTER_AUTH_SECRET

2. **phase3-frontend** - Vercel (new deployment)
   - URL: `https://hackathon-todo-phase3.vercel.app`
   - Environment: .env.local with PHASE3_BACKEND_URL, BETTER_AUTH_SECRET

### Database (Neon PostgreSQL):
- **Shared** by phase2-backend and phase3-backend
- Connection pooling configured
- SSL required for all connections
- Automated backups enabled

**Cost Estimate**: ~$15/month (3 Railway services, 2 Vercel deployments, Neon free tier)

---

## 10. Forward Compatibility (Phase 4 Prep)

Phase 3 architecture prepares for Phase 4 (Kubernetes):

**Required for Phase 4:**
- ✅ Services already separated (3 backend services)
- ✅ Stateless architecture (no shared memory)
- ⚠️ Health check endpoints required: `/health`, `/readiness` (add in Phase 3)
- ⚠️ Environment-based configuration (complete in Phase 3)
- ⚠️ No local file dependencies (verify in Phase 3)
- ⚠️ Containerization-ready (Dockerfile for each service in Phase 3)

**Phase 3 Deliverables for Phase 4:**
- Health check endpoints on all services
- Graceful shutdown handlers
- Resource limits documentation
- Deployment manifests (Kubernetes YAML templates)

---

## 11. Success Criteria

Phase 3 is complete when ALL criteria are met:

### Functional Requirements:
- ✅ Natural language commands work for all CRUD operations
  - "add task buy milk"
  - "show my tasks"
  - "mark task X as complete"
  - "delete task Y"
  - "update task Z to say ..."

### Technical Requirements:
- ✅ All 5 MCP tools functional (add, list, complete, delete, update)
- ✅ Conversation history persists correctly in database
- ✅ OpenAI Agents SDK integrated successfully
- ✅ JWT authentication working across all services

### Backward Compatibility:
- ✅ Phase 2 backend unchanged and passing all tests
- ✅ Phase 2 frontend continues working
- ✅ No breaking changes to existing APIs

### Deployment:
- ✅ 3 backend services deployed to Railway (phase2, phase3-backend, phase3-mcp)
- ✅ 2 frontend services deployed to Vercel (phase2-frontend, phase3-frontend)
- ✅ Services communicate correctly in production
- ✅ Environment variables configured correctly

### Documentation:
- ✅ Demo video recorded (2-3 minutes showing chatbot interaction)
- ✅ README updated with Phase 3 architecture
- ✅ API documentation updated
- ✅ Deployment guide written

---

## Governance

### Version Format

**Semantic Versioning**: MAJOR.MINOR.PATCH (e.g., 3.0.0)

- **MAJOR**: Backward-incompatible changes (phase transitions, removing/redefining core principles)
- **MINOR**: Backward-compatible additions (new sections, expanded guidance, new non-breaking requirements)
- **PATCH**: Clarifications, wording improvements, typo fixes, non-semantic refinements

### Amendment Procedure

1. **Document Proposal**: Create Architecture Decision Record (ADR) documenting proposed change
2. **Impact Analysis**: Evaluate impact on existing features, specifications, and deployments
3. **Validation**: Ensure no principle contradictions or conflicts with Phase 2/3 requirements
4. **Update Constitution**: Edit this file with changes, increment version, update amendment date
5. **Version Increment**:
   - MAJOR: Breaking change (requires feature rewrites, architectural refactoring, or phase transition)
   - MINOR: Additive change (new guidance, expanded principles, new services)
   - PATCH: Editorial change (clarifications, typos, wording improvements)
6. **Propagate Changes**: Update dependent templates (.specify/templates/) and documents
7. **Commit**: Commit constitution update with ADR reference and Sync Impact Report

### Compliance Requirements

- **Spec Compliance**: All Phase 3 feature specs MUST reference relevant constitution principles
- **Plan Gate**: Plan phase includes "Constitution Check" validating compliance (3-service architecture, statelessness, backward compatibility)
- **Violation Justification**: Any principle violation MUST be justified in plan with rationale
- **ADR for Significant Violations**: Architecturally significant violations require ADR documentation
- **Review Requirement**: No PR approval without constitution compliance verification
- **Testing Enforcement**: All Phase 2 tests must continue passing before Phase 3 merge

### Constitution Review

- **Phase Boundaries**: Constitution reviewed at end of each hackathon phase
- **Feature Milestones**: Review triggered after every 5 features or major architectural shift
- **Continuous Improvement**: Constitution evolves based on lessons learned
- **Stability Preference**: Avoid frequent changes; prefer stability over perfection

### Ratification

- **Current Version**: 3.0.0
- **Initial Ratification Date**: 2025-12-09 (v1.0.0 - Phase 1)
- **Phase 2 Transition**: 2025-12-10 (v2.0.0 - Full-Stack Web App)
- **Phase 3 Transition**: 2025-12-20 (v3.0.0 - AI Chatbot + MCP)
- **Status**: Active (Phase 3 only)

### Scope

This constitution applies **exclusively to Phase 3** (AI-Powered Todo Chatbot) of the hackathon project.

**Phase 1** (In-Memory Console App) remains governed by constitution v1.0.0 for historical reference.

**Phase 2** (Full-Stack Web App) remains governed by constitution v2.0.0. **CRITICAL**: Phase 2 code MUST NOT be modified during Phase 3 development.

**Future phases**:
- **Phase 4: Kubernetes** - Container orchestration, distributed systems, health checks, scalability
- **Phase 5: Cloud Deployment** - Production readiness, monitoring, observability, CI/CD

Each phase transition triggers a **MAJOR version bump** with new or redefined architectural principles.

---

## Notes for Claude Code

When generating code for Phase 3, validate against these checkpoints:

1. **Preservation Check**: Is this preserving Phase 2 completely unchanged?
2. **Architecture Check**: Does this follow the 3-service architecture (phase2-backend, phase3-backend, phase3-mcp-server)?
3. **MCP Check**: Are MCP tools calling phase2-backend APIs (not DB directly)?
4. **Statelessness Check**: Is this service stateless (no in-memory sessions or caching)?
5. **Specification Check**: Never make assumptions - refer to specs/phase3/ for details

**When in doubt**: Ask for clarification rather than making assumptions about Phase 3 behavior.

---

**Version**: 3.0.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-20
