# Implementation Plan: Natural Language Chatbot for Todo Management

**Branch**: `002-chatbot-interface` | **Date**: 2025-12-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-chatbot-interface/spec.md`

**Note**: This plan defines HOW to implement Phase 3 chatbot while preserving Phase 2 completely unchanged.

## Summary

Build an AI-powered conversational interface for todo management using OpenAI Agents SDK and MCP Server architecture. Users can create, list, update, complete, and delete tasks through natural language commands. The system integrates with existing Phase 2 backend via HTTP APIs while maintaining complete backward compatibility.

**Key Innovation**: Three-service architecture separates concerns (phase2-backend for tasks, phase3-backend for chat, phase3-mcp-server for tool orchestration) to enable zero-risk Phase 3 deployment.

## Technical Context

**Language/Version**: Python 3.13+ (all backend services), TypeScript 5.0+ / Node 24+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.122.0+, OpenAI Python SDK 2.11.0+, OpenAI Agents SDK 0.6.4+, Official MCP SDK (Python)
- Frontend: Next.js 16.0.3+, React 19+, OpenAI ChatKit React, Better-Auth
**Storage**: Neon PostgreSQL (shared across all services) with SQLModel ORM
**Testing**: pytest (backend), pytest-asyncio (async tests), Jest/React Testing Library (frontend)
**Target Platform**:
- Backend: Railway (3 services: phase2-backend, phase3-backend, phase3-mcp-server)
- Frontend: Vercel (2 deployments: phase2-frontend, phase3-frontend)
**Project Type**: Web - Multi-service distributed system
**Performance Goals**:
- Chat response latency: < 5 seconds (95th percentile)
- MCP tool execution: < 2 seconds (typical)
- Database queries: Properly indexed for user_id, created_at lookups
- Handle 100 concurrent users with isolated conversations
**Constraints**:
- ZERO changes to phase2-backend code or endpoints
- NO direct database access from phase3-mcp-server (HTTP only)
- Stateless architecture (no in-memory sessions, enables horizontal scaling)
- OpenAI rate limits (use exponential backoff)
- Cost-effective OpenAI API usage
**Scale/Scope**:
- 100+ concurrent users
- 5 MCP tools (add, list, complete, delete, update)
- Conversation history persisted per user
- 3 backend services + 2 frontend applications

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Three-Service Architecture (Section 2.1)
- **Compliance**: Implements phase2-backend (unchanged), phase3-backend (new chat endpoint), phase3-mcp-server (new MCP tools)
- **Verification**: No code changes to phase2-backend/, new directories for phase3-backend/ and phase3-mcp-server/

### ✅ Stateless Architecture (Section 2.2)
- **Compliance**: phase3-backend fetches conversation history from DB per request, no in-memory sessions
- **Verification**: All conversation state in PostgreSQL, JWT-only auth (no session stores)

### ✅ Single Source of Truth (Section 2.3)
- **Compliance**: phase2-backend authoritative for tasks, phase3-mcp-server calls phase2-backend APIs via HTTP
- **Verification**: No task logic duplication, MCP tools use httpx to call REST endpoints

### ✅ Backward Compatibility (Section 2.4 - CRITICAL)
- **Compliance**: Zero changes to phase2-backend code, Phase 2 frontend continues working
- **Verification**: All Phase 2 tests continue passing, database only adds new tables (conversations, messages)

### ✅ Separation of Concerns (Section 2.5)
- **Compliance**:
  - phase2-backend: Task CRUD only (unchanged)
  - phase3-backend: Chat endpoint only, conversation history, OpenAI integration
  - phase3-mcp-server: 5 MCP tools calling phase2-backend APIs
- **Verification**: Clear service boundaries, no logic overlap

### ✅ Technology Stack (Section 3)
- **Compliance**: Python 3.13+ FastAPI for all backends, OpenAI Agents SDK 0.6.4+, Official MCP SDK, Next.js 16+ for frontends
- **Verification**: pyproject.toml files specify exact versions, uv package manager

### ✅ Database Schema (Section 4)
- **Compliance**: Only adds new tables (conversations, messages), no alterations to existing users or tasks tables
- **Verification**: Migration files only contain CREATE TABLE statements, proper indexes on user_id and created_at

### ✅ MCP Tools Specification (Section 5)
- **Compliance**: Exactly 5 tools (add_task, list_tasks, complete_task, delete_task, update_task) with specified contracts
- **Verification**: Each tool implemented as async function calling phase2-backend REST API

### ✅ Non-Functional Requirements (Section 6)
- **Performance**: Chat < 5s, MCP tools < 2s, proper indexes
- **Security**: JWT validation, user isolation, environment variables for secrets
- **Quality**: Phase 2 tests pass, new tests for chat and MCP
- **UX**: Conversational responses, clarifications, friendly errors

### ✅ Constraints & Non-Goals (Section 7)
- **Compliance**: No phase2-backend changes, no direct DB access from MCP server, OpenAI Agents SDK (not custom prompts)
- **Out of Scope**: Voice, multi-language, Docker/Kubernetes (Phase 4), streaming responses

**GATE STATUS**: ✅ PASS - All constitutional requirements met

## Project Structure

### Documentation (this feature)

```text
specs/002-chatbot-interface/
├── spec.md              # Feature specification (WHAT to build)
├── plan.md              # This file - Architecture plan (HOW to build)
├── research.md          # Phase 0 output - Technology research and decisions
├── data-model.md        # Phase 1 output - Database schema and entity design
├── quickstart.md        # Phase 1 output - Test scenarios and acceptance criteria
├── contracts/           # Phase 1 output - API contracts (OpenAPI schemas)
│   ├── chat-api.yaml    # phase3-backend chat endpoint contract
│   └── mcp-tools.yaml   # MCP server tool contracts
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Phase 2 (Existing - NO CHANGES)
backend/                          # phase2-backend (FastAPI)
├── main.py                       # [UNCHANGED] FastAPI app, CORS, routes
├── db.py                         # [UNCHANGED] Database connection
├── models/                       # [UNCHANGED] Task, User SQLModels
├── routes/                       # [UNCHANGED] /api/tasks endpoints
├── services/                     # [UNCHANGED] Task business logic
├── auth/                         # [UNCHANGED] JWT middleware, rate limiting
├── tests/                        # [UNCHANGED] All Phase 2 tests MUST PASS
└── migrations/                   # [EXTEND ONLY] Add 003_conversations.sql, 004_messages.sql

frontend/                         # phase2-frontend (Next.js 16)
├── app/                          # [UNCHANGED] Pages, layouts
├── components/                   # [UNCHANGED] UI components
├── lib/                          # [UNCHANGED] API client, auth
└── [ALL FILES UNCHANGED]

# Phase 3 (New Services)
phase3-backend/                   # NEW - Chat service
├── app/
│   ├── main.py                   # FastAPI app, CORS for phase3-frontend
│   ├── config.py                 # Environment variables (DATABASE_URL, OPENAI_API_KEY, JWT_SECRET)
│   ├── db.py                     # Database session (async SQLModel)
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py               # Conversation, Message SQLModels
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py               # POST /api/{user_id}/chat endpoint
│   │   └── health.py             # Health check endpoints
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── openai_agent.py       # OpenAI Agents SDK integration
│   │   └── mcp_client.py         # HTTP client for phase3-mcp-server
│   └── services/
│       ├── __init__.py
│       └── chat_service.py       # Conversation CRUD, message persistence
├── tests/
│   ├── test_chat_endpoint.py    # Chat API tests
│   ├── test_openai_agent.py     # Agent tests (mocked OpenAI)
│   ├── test_mcp_client.py       # MCP client tests
│   └── test_chat_service.py     # Service layer tests
├── pyproject.toml                # Dependencies: fastapi, openai, openai-agents, sqlmodel, httpx
├── .env.example
├── README.md
└── railway.json                  # Railway deployment config

phase3-mcp-server/                # NEW - MCP tools service
├── app/
│   ├── main.py                   # FastAPI app exposing /mcp endpoint
│   ├── config.py                 # Environment variables (PHASE2_BACKEND_URL)
│   ├── server.py                 # MCP server setup (Official SDK)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── add_task.py           # MCP tool: add_task
│   │   ├── list_tasks.py         # MCP tool: list_tasks
│   │   ├── complete_task.py      # MCP tool: complete_task
│   │   ├── delete_task.py        # MCP tool: delete_task
│   │   └── update_task.py        # MCP tool: update_task
│   └── clients/
│       ├── __init__.py
│       └── phase2_client.py      # HTTP client for phase2-backend
├── tests/
│   ├── test_tools.py             # Tool tests (mocked phase2-backend)
│   └── test_phase2_client.py    # Phase2 client tests
├── pyproject.toml                # Dependencies: fastapi, mcp, httpx
├── .env.example
├── README.md
└── railway.json                  # Railway deployment config

phase3-frontend/                  # NEW - Chat UI
├── app/
│   ├── layout.tsx                # Root layout (Better-Auth provider)
│   ├── page.tsx                  # Landing page (redirect to /chat or /login)
│   ├── chat/
│   │   └── page.tsx              # Main chat page (ChatKit integration)
│   └── api/
│       └── chatkit/
│           └── session/
│               └── route.ts      # ChatKit session endpoint
├── components/
│   ├── ChatKitWrapper.tsx        # ChatKit React component wrapper
│   ├── AuthGuard.tsx             # Protected route wrapper
│   └── LoadingSpinner.tsx        # Loading state component
├── lib/
│   ├── auth.ts                   # Better-Auth config (same as phase2)
│   ├── api.ts                    # API client for phase3-backend
│   └── types.ts                  # TypeScript types
├── public/
├── package.json                  # Dependencies: next, react, @openai/chatkit-react, better-auth
├── tsconfig.json
├── next.config.js
├── .env.local.example
└── vercel.json                   # Vercel deployment config

database/
└── migrations/
    ├── 003_create_conversations_table.sql   # NEW - Phase 3 migration
    └── 004_create_messages_table.sql        # NEW - Phase 3 migration
```

**Structure Decision**: Multi-service web architecture chosen to satisfy Phase 3 constitution requirements:
- **phase2-backend**: Unchanged, continues serving Phase 2 frontend
- **phase3-backend**: New service for chat endpoint and conversation management
- **phase3-mcp-server**: New service implementing MCP tools that call phase2-backend
- **phase3-frontend**: New Next.js application with ChatKit UI
- **Shared database**: All services connect to same Neon PostgreSQL instance

This structure enables zero-risk Phase 3 deployment while preparing for Phase 4 (Kubernetes) with separated, stateless services.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations. This plan fully complies with Phase 3 constitution v3.0.0.

---

# Phase 0: Research & Unknowns Resolution

*Output: research.md*

## Research Tasks

All technical decisions are well-defined in the constitution and specification. Research phase will focus on:

### 1. OpenAI Agents SDK Integration Patterns
**Research Question**: How to integrate OpenAI Agents SDK with MCP tools in Python FastAPI?

**Scope**:
- Official OpenAI Agents SDK documentation for Python
- Agent creation with custom system prompts
- Tool registration and function calling patterns
- Error handling and rate limiting strategies
- Best practices for conversation history management

**Output**: Code patterns for agent initialization, tool registration, and conversation flow

### 2. Official MCP SDK Usage (Python)
**Research Question**: How to implement MCP server using Official MCP SDK in Python?

**Scope**:
- Official MCP SDK installation via `uv add mcp`
- Server initialization and tool registration
- HTTP endpoint exposure patterns with FastAPI
- Tool parameter validation and response formatting
- Integration with OpenAI function calling

**Output**: Code patterns for MCP server setup, tool handlers, and FastAPI integration

### 3. OpenAI ChatKit React Integration
**Research Question**: How to integrate ChatKit React components with Next.js 16 and Better-Auth?

**Scope**:
- ChatKit React component installation and setup
- Session management with client secrets
- API endpoint requirements for ChatKit
- Styling and theming options
- Integration with existing Better-Auth authentication

**Output**: Component patterns for ChatKit wrapper, session endpoint, and auth integration

### 4. Conversation History Storage Patterns
**Research Question**: What database schema optimizes conversation history retrieval?

**Scope**:
- Conversation vs Message table design
- Index strategies for user_id and created_at queries
- Pagination patterns for large conversation histories
- Retention policies and cleanup strategies

**Output**: Schema design with performance-optimized indexes

### 5. Phase2 Backend API Integration
**Research Question**: What are the exact REST API contracts for phase2-backend?

**Scope**:
- Document existing phase2-backend endpoints (GET/POST/PUT/PATCH/DELETE /api/{user_id}/tasks)
- Request/response schemas for each endpoint
- Error handling patterns and status codes
- JWT authentication header requirements

**Output**: OpenAPI documentation for phase2-backend integration

**NEEDS CLARIFICATION ITEMS**: None - all technical context is specified in constitution and spec.

---

# Phase 1: Design & Contracts

*Outputs: data-model.md, contracts/, quickstart.md*

## Data Model Design

### New Entities (Phase 3)

**Conversation**:
- Purpose: Represents a chat session between user and chatbot
- Fields:
  - id (UUID, PK)
  - user_id (UUID, FK to users, NOT NULL)
  - created_at (TIMESTAMP, DEFAULT NOW())
  - updated_at (TIMESTAMP, DEFAULT NOW())
- Indexes:
  - PRIMARY KEY (id)
  - INDEX idx_conversations_user_created ON (user_id, created_at DESC)
- Relationships:
  - Has many messages (1:N)
  - Belongs to user (N:1)
- Constraints:
  - User isolation enforced via user_id FK
  - Soft delete not required (permanent retention)

**Message**:
- Purpose: Individual chat message within a conversation
- Fields:
  - id (UUID, PK)
  - user_id (UUID, FK to users, NOT NULL)
  - conversation_id (UUID, FK to conversations, NOT NULL)
  - role (VARCHAR(20), NOT NULL) - enum: "user" | "assistant" | "system"
  - content (TEXT, NOT NULL)
  - created_at (TIMESTAMP, DEFAULT NOW())
- Indexes:
  - PRIMARY KEY (id)
  - INDEX idx_messages_conversation_created ON (conversation_id, created_at ASC)
  - INDEX idx_messages_user_created ON (user_id, created_at DESC)
- Relationships:
  - Belongs to conversation (N:1)
  - Belongs to user (N:1)
- Constraints:
  - User isolation enforced via user_id FK
  - role must be 'user', 'assistant', or 'system'
  - content max length validated in application layer (OpenAI limits)

### Existing Entities (Phase 2 - Reference Only)

**Task** (NO CHANGES):
- Defined in backend/models/task.py
- Fields: id, user_id, title, description, completed, created_at, updated_at
- Managed exclusively by phase2-backend

**User** (NO CHANGES):
- Managed by Better-Auth
- Referenced by user_id in conversations and messages

## API Contracts

### Chat API (phase3-backend)

**Endpoint**: `POST /api/{user_id}/chat`

**Request**:
```json
{
  "message": "string (required, 1-2000 chars)",
  "conversation_id": "uuid (optional, if continuing existing conversation)"
}
```

**Response** (Success - 200):
```json
{
  "conversation_id": "uuid",
  "message": "string (assistant response)",
  "timestamp": "ISO 8601 timestamp",
  "tool_calls": [
    {
      "tool": "string (e.g., 'add_task')",
      "parameters": { "user_id": "uuid", "title": "string" },
      "result": { "task_id": "uuid", "status": "created" }
    }
  ]
}
```

**Response** (Error - 400):
```json
{
  "error": {
    "code": "INVALID_MESSAGE",
    "message": "Message too long (max 2000 chars)",
    "user_message": "Your message is too long. Please keep it under 2000 characters."
  }
}
```

**Response** (Error - 429):
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests",
    "user_message": "Please wait a moment before sending another message.",
    "retry_after": 30
  }
}
```

**Authentication**: JWT token in `Authorization: Bearer <token>` header

**Rate Limiting**: 10 requests per minute per user

### MCP Tools API (phase3-mcp-server)

**Endpoint**: `POST /mcp`

**Request**:
```json
{
  "tool": "string (add_task|list_tasks|complete_task|delete_task|update_task)",
  "parameters": {
    "user_id": "uuid (required)",
    "...": "tool-specific parameters"
  }
}
```

**Tool: add_task**:
```json
{
  "tool": "add_task",
  "parameters": {
    "user_id": "uuid",
    "title": "string (required, 1-200 chars)",
    "description": "string (optional, 0-2000 chars)"
  }
}
```

**Response**:
```json
{
  "task_id": "uuid",
  "status": "created",
  "title": "string",
  "description": "string",
  "completed": false,
  "created_at": "ISO 8601"
}
```

**Tool: list_tasks**:
```json
{
  "tool": "list_tasks",
  "parameters": {
    "user_id": "uuid",
    "completed": "boolean (optional)"
  }
}
```

**Response**:
```json
{
  "tasks": [
    {
      "task_id": "uuid",
      "title": "string",
      "description": "string",
      "completed": false,
      "created_at": "ISO 8601",
      "updated_at": "ISO 8601"
    }
  ],
  "count": 5
}
```

**Tool: complete_task**:
```json
{
  "tool": "complete_task",
  "parameters": {
    "user_id": "uuid",
    "task_id": "uuid",
    "completed": true
  }
}
```

**Response**:
```json
{
  "task_id": "uuid",
  "status": "updated",
  "completed": true,
  "updated_at": "ISO 8601"
}
```

**Tool: delete_task**:
```json
{
  "tool": "delete_task",
  "parameters": {
    "user_id": "uuid",
    "task_id": "uuid"
  }
}
```

**Response**:
```json
{
  "task_id": "uuid",
  "status": "deleted",
  "message": "Task deleted successfully"
}
```

**Tool: update_task**:
```json
{
  "tool": "update_task",
  "parameters": {
    "user_id": "uuid",
    "task_id": "uuid",
    "title": "string (optional, 1-200 chars)",
    "description": "string (optional, 0-2000 chars)"
  }
}
```

**Response**:
```json
{
  "task_id": "uuid",
  "status": "updated",
  "title": "string",
  "description": "string",
  "updated_at": "ISO 8601"
}
```

## Quickstart Test Scenarios

### Scenario 1: Add Task via Chat (P1)
**Given**: Authenticated user in chat interface
**When**: User sends "Add a task to buy groceries tomorrow"
**Then**:
- Task created in database via phase2-backend
- Conversation and messages stored in phase3-backend
- User receives confirmation: "I've added 'Buy groceries tomorrow' to your tasks."

**API Flow**:
1. `POST /api/{user_id}/chat` → phase3-backend
2. phase3-backend calls OpenAI Agents SDK
3. Agent invokes add_task MCP tool
4. phase3-mcp-server `POST /mcp` with tool=add_task
5. phase3-mcp-server calls `POST /api/{user_id}/tasks` → phase2-backend
6. phase2-backend creates task, returns task object
7. phase3-backend stores conversation and messages
8. phase3-backend returns response to frontend

### Scenario 2: List Tasks via Chat (P2)
**Given**: User has 5 existing tasks
**When**: User sends "What tasks do I have?"
**Then**:
- MCP tool list_tasks called
- All 5 tasks retrieved from phase2-backend
- User receives formatted list

**API Flow**:
1. `POST /api/{user_id}/chat` → phase3-backend
2. Agent invokes list_tasks MCP tool
3. phase3-mcp-server `GET /api/{user_id}/tasks` → phase2-backend
4. Tasks returned and formatted by agent
5. Response stored and returned to user

### Scenario 3: Complete Task via Chat (P3)
**Given**: User has task titled "Buy groceries"
**When**: User sends "I finished buying groceries"
**Then**:
- Agent identifies task by title
- complete_task MCP tool called
- Task status updated in phase2-backend
- User receives confirmation

### Scenario 4: Error Handling - Ambiguous Command
**Given**: User has multiple tasks with similar titles
**When**: User sends "Complete the grocery task"
**Then**:
- Agent identifies ambiguity
- No tool called
- Agent asks clarification: "I found 2 tasks related to groceries. Which one did you complete? 'Buy groceries' or 'Put away groceries'?"

### Scenario 5: Error Handling - AI Service Unavailable
**Given**: OpenAI API is down
**When**: User sends any message
**Then**:
- Error caught in phase3-backend
- User receives friendly error: "I'm having trouble processing your message right now. Please try again in a moment."
- Conversation still stored (user message recorded)

---

# Architecture Diagrams

## High-Level Service Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Client Layer                        │
├─────────────────────────────────────────────────────┤
│  phase2-frontend        │  phase3-frontend          │
│  (Next.js 16)           │  (Next.js 16 + ChatKit)   │
│  Vercel                 │  Vercel                   │
│  Port: 3000             │  Port: 3000               │
└──────────┬──────────────┴──────────┬────────────────┘
           │                         │
           │ HTTPS                   │ HTTPS
           ▼                         ▼
┌──────────────────┐      ┌─────────────────────────┐
│  phase2-backend  │      │  phase3-backend         │
│  FastAPI         │      │  FastAPI                │
│  Railway         │      │  Railway                │
│  Port: 8000      │      │  Port: 8001             │
│  [UNCHANGED]     │      │  [NEW]                  │
└──────────┬───────┘      └─────────┬───────────────┘
           │                        │
           │                        │ HTTPS
           │                        ▼
           │              ┌─────────────────────────┐
           │              │  phase3-mcp-server      │
           │              │  FastAPI + MCP SDK      │
           │              │  Railway                │
           │              │  Port: 8002             │
           │              │  [NEW]                  │
           │              └─────────┬───────────────┘
           │                        │
           │◄───────────────────────┘ HTTPS (REST API calls)
           │
           ▼
┌─────────────────────────────────────────────────────┐
│              Neon PostgreSQL (Shared)                │
│  - users (Phase 2 - Better-Auth managed)            │
│  - tasks (Phase 2 - phase2-backend manages)         │
│  - conversations (Phase 3 - phase3-backend manages) │
│  - messages (Phase 3 - phase3-backend manages)      │
└─────────────────────────────────────────────────────┘
```

## Chat Request Flow

```
1. User types message in phase3-frontend
   ↓
2. Frontend calls POST /api/{user_id}/chat (phase3-backend)
   Headers: Authorization: Bearer <JWT>
   Body: { message: "add task buy milk" }
   ↓
3. phase3-backend receives request
   - Validates JWT (extract user_id)
   - Gets or creates conversation (DB query)
   - Fetches message history (DB query)
   - Stores user message (DB insert)
   ↓
4. phase3-backend calls OpenAI Agents SDK
   - Passes conversation history + user message
   - Agent analyzes intent
   - Agent decides to call MCP tool: add_task
   ↓
5. phase3-backend calls phase3-mcp-server
   - POST /mcp
   - Body: { tool: "add_task", parameters: { user_id, title: "buy milk" } }
   ↓
6. phase3-mcp-server executes tool
   - Validates parameters
   - Calls phase2-backend REST API
   - POST /api/{user_id}/tasks
   - Headers: Authorization: Bearer <JWT>
   - Body: { title: "buy milk", description: "" }
   ↓
7. phase2-backend processes request [UNCHANGED CODE]
   - Validates JWT
   - Creates task in database (INSERT INTO tasks)
   - Returns task object
   ↓
8. phase3-mcp-server receives task object
   - Formats response
   - Returns to phase3-backend
   ↓
9. phase3-backend receives tool result
   - OpenAI generates natural language response
   - Response: "I've added 'buy milk' to your tasks."
   ↓
10. phase3-backend stores assistant message (DB insert)
    - Stores in messages table
    ↓
11. phase3-backend returns response to frontend
    Body: { conversation_id, message, timestamp, tool_calls }
    ↓
12. phase3-frontend displays message
    User sees: "I've added 'buy milk' to your tasks."
```

## MCP Tool Execution Flow

```
OpenAI Agent (in phase3-backend)
  ↓ Function call: add_task(user_id="u1", title="Buy milk")
  ↓
phase3-backend MCP Client (mcp_client.py)
  ↓ HTTP POST /mcp
  ↓ Body: { tool: "add_task", parameters: { user_id, title } }
  ↓
phase3-mcp-server (main.py)
  ↓ Route to /mcp endpoint
  ↓
MCP Server (server.py)
  ↓ Dispatch to add_task_handler
  ↓
add_task_handler (tools/add_task.py)
  ↓ Validate parameters (user_id, title)
  ↓
Phase2Client (clients/phase2_client.py)
  ↓ HTTP POST /api/{user_id}/tasks
  ↓ Headers: Authorization: Bearer <JWT>
  ↓ Body: { title, description }
  ↓
phase2-backend (routes/tasks.py) [UNCHANGED]
  ↓ Validate JWT
  ↓ Call task_service.create_task()
  ↓
TaskService (services/task_service.py) [UNCHANGED]
  ↓ Create SQLModel Task instance
  ↓ INSERT INTO tasks (user_id, title, description, completed)
  ↓
Database (PostgreSQL tasks table)
  ↓ Return task object (id, user_id, title, description, completed, timestamps)
  ↓
phase2-backend
  ↓ Return JSON response
  ↓
add_task_handler
  ↓ Format MCP response
  ↓ Return: { task_id, status: "created", title }
  ↓
phase3-mcp-server
  ↓ Return response
  ↓
phase3-backend MCP Client
  ↓ Return tool result to OpenAI Agent
  ↓
OpenAI Agent
  ↓ Generate natural language response
  ↓ "I've added 'Buy milk' to your tasks."
```

---

# Implementation Strategy

## Deployment Order

**Phase 3A: Infrastructure Setup**
1. Create database migrations (003_conversations.sql, 004_messages.sql)
2. Run migrations on Neon PostgreSQL
3. Verify Phase 2 continues working (run all Phase 2 tests)

**Phase 3B: MCP Server (Simplest First)**
1. Initialize phase3-mcp-server/ codebase
2. Set up pyproject.toml with dependencies (fastapi, mcp, httpx)
3. Implement Phase2Client (HTTP client for phase2-backend)
4. Implement all 5 MCP tools (add, list, complete, delete, update)
5. Write tests (mock phase2-backend responses)
6. Deploy to Railway
7. Test MCP endpoints with curl/Postman

**Phase 3C: Chat Backend**
1. Initialize phase3-backend/ codebase
2. Set up pyproject.toml with dependencies (fastapi, openai, openai-agents, sqlmodel)
3. Implement database models (Conversation, Message)
4. Implement OpenAI Agents SDK integration
5. Implement MCP client (HTTP client for phase3-mcp-server)
6. Implement chat endpoint (`POST /api/{user_id}/chat`)
7. Write tests (mock OpenAI and MCP server)
8. Deploy to Railway
9. Test chat endpoint with curl/Postman

**Phase 3D: Chat Frontend**
1. Initialize phase3-frontend/ codebase (Next.js 16 + TypeScript)
2. Set up package.json with dependencies (next, react, @openai/chatkit-react, better-auth)
3. Copy Better-Auth config from phase2-frontend
4. Implement ChatKit wrapper component
5. Implement chat page with ChatKit integration
6. Implement API client for phase3-backend
7. Test locally (npm run dev)
8. Deploy to Vercel
9. End-to-end testing

**Phase 3E: Integration & Testing**
1. Run all Phase 2 tests (must pass - verify backward compatibility)
2. Run all Phase 3 tests (chat endpoint, MCP tools)
3. Manual end-to-end testing (create/list/complete/delete/update via chat)
4. Performance testing (response times, concurrent users)
5. Security testing (JWT validation, user isolation)
6. Error handling testing (OpenAI down, phase2-backend down)

**Phase 3F: Documentation & Demo**
1. Update README.md with Phase 3 architecture
2. Create deployment guide (Railway + Vercel setup)
3. Update API documentation
4. Record demo video (2-3 minutes)
5. Write Phase 3 retrospective (lessons learned, ADRs)

## Risk Mitigation

**Risk 1: Phase 2 Regression**
- **Mitigation**: Zero code changes to phase2-backend/, run all Phase 2 tests before deployment
- **Rollback**: Phase 3 services can be stopped independently without affecting Phase 2

**Risk 2: OpenAI API Rate Limits**
- **Mitigation**: Implement exponential backoff, rate limiting (10 req/min per user), error handling
- **Fallback**: Graceful degradation with friendly error messages

**Risk 3: Database Performance**
- **Mitigation**: Proper indexes on user_id and created_at, connection pooling, query optimization
- **Monitoring**: Track query times, add indexes if slow

**Risk 4: MCP Integration Complexity**
- **Mitigation**: Start with simplest tool (add_task), use Official MCP SDK (not custom)
- **Testing**: Comprehensive unit tests with mocked responses

**Risk 5: ChatKit Integration Issues**
- **Mitigation**: Follow official ChatKit React documentation, test session management thoroughly
- **Fallback**: Can build custom chat UI if ChatKit problematic (not ideal but possible)

---

# Success Criteria

## Functional Requirements (from spec.md)
- ✅ FR-001: Natural language input accepted via chat interface
- ✅ FR-002: Task information extracted from natural language
- ✅ FR-003: Create tasks through conversational commands
- ✅ FR-004: List tasks through conversational queries
- ✅ FR-005: Complete tasks through conversational commands
- ✅ FR-006: Update tasks through conversational commands
- ✅ FR-007: Delete tasks with user confirmation
- ✅ FR-008: Friendly conversational responses
- ✅ FR-009: Clarifying questions for ambiguous intent
- ✅ FR-010: Graceful error handling
- ✅ FR-011: Conversation history persistence
- ✅ FR-012: User isolation enforcement
- ✅ FR-013: JWT authentication from Better-Auth
- ✅ FR-014: Integration with Phase 2 backend (no duplication)
- ✅ FR-015: Response < 5 seconds
- ✅ FR-016: Concurrent users supported
- ✅ FR-017: Graceful degradation if AI unavailable
- ✅ FR-018: Confirmation for destructive actions

## Technical Requirements
- ✅ All 5 MCP tools functional
- ✅ OpenAI Agents SDK integrated
- ✅ Conversation history persisted in database
- ✅ Three-service architecture deployed
- ✅ Stateless backend services
- ✅ Phase 2 tests continue passing
- ✅ Proper database indexes
- ✅ JWT authentication working

## Acceptance Criteria
- ✅ User can create task via "add task buy milk"
- ✅ User can list tasks via "what are my tasks?"
- ✅ User can complete task via "I finished buying groceries"
- ✅ User can update task via "change deadline to tomorrow"
- ✅ User can delete task via "delete the groceries task"
- ✅ System asks clarification for ambiguous commands
- ✅ System provides friendly error messages
- ✅ Phase 2 frontend and backend continue working unchanged
- ✅ Services deployed to Railway (3 backends) and Vercel (2 frontends)
- ✅ Demo video recorded showing natural language task management

---

# Next Steps

After plan approval:
1. **Run `/sp.tasks`** - Generate dependency-ordered implementation tasks
2. **Phase 0: Execute research** - Document OpenAI SDK, MCP SDK, ChatKit patterns
3. **Phase 1: Generate design artifacts** - data-model.md, contracts/, quickstart.md
4. **Phase 2: Implementation** - Follow deployment order (MCP server → chat backend → chat frontend)
5. **Phase 3: Testing & Deployment** - End-to-end testing, deploy to Railway/Vercel
6. **Phase 4: Documentation** - README updates, demo video, retrospective

**Ready to proceed with `/sp.tasks`?**
