# Implementation Plan: Migrate to OpenAI ChatKit

**Branch**: `003-chatkit-migration` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)

---

## Summary

Migrate Phase 3 chatbot from custom React chat implementation to official OpenAI ChatKit components (`@openai/chatkit-react` frontend, `openai-chatkit` backend). Replace custom ChatInterface/ChatMessage components with `<ChatKit>` component, and replace current `/api/chat` endpoint with ChatKitServer-based `/chatkit` endpoint. Maintain all existing functionality (task CRUD via MCP tools, conversation persistence, JWT authentication) while achieving hackathon compliance with ChatKit requirement.

**Migration Strategy**: Direct replacement (no feature flags per clarification)
**Data Strategy**: Clean slate - truncate conversations/messages tables before deployment
**Streaming**: Progressive JSON chunking (not SSE, per clarification)
**Session Scope**: Login session lifecycle (24-hour JWT duration, per clarification)

---

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x / Node 24+ (frontend)
**Primary Dependencies**:
- Frontend: @openai/chatkit-react (1.x+), Next.js 16, React 19, Better-Auth 1.4.6
- Backend: openai-chatkit (latest), FastAPI, SQLModel, OpenAI Agents SDK
**Storage**: PostgreSQL on Neon (shared database, add session_id column to conversations)
**Testing**: pytest (backend unit/integration), manual E2E (comprehensive per clarification)
**Target Platform**: Railway (backend services), Vercel (frontend), Neon PostgreSQL
**Project Type**: Web application (multi-service: phase3-frontend, phase3-backend)
**Performance Goals**: <5s response time for all operations, 100+ concurrent users
**Constraints**:
- MUST use official ChatKit packages (no custom implementations)
- MUST NOT modify Phase 2 backend or tasks/users tables
- MUST preserve existing MCP server integration
- MUST maintain conversation persistence in PostgreSQL
**Scale/Scope**: 3 backend services, 1 frontend, ~10-15 file modifications, 5 new files

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Three-Service Architecture (Section 2.1)

**Compliance**: PASS

- phase2-backend: **Unchanged** (no code modifications)
- phase3-backend: **Modified** (replace /api/chat with /chatkit endpoint, add ChatKitServer)
- phase3-mcp-server: **Unchanged** (existing MCP tools continue working)

**Rationale**: Migration only affects phase3-backend; Phase 2 remains completely untouched.

### ✅ Stateless Architecture (Section 2.2)

**Compliance**: PASS

- ChatKitServer fetches conversation history from PostgreSQL per request (no in-memory sessions)
- Session mapping via database (conversations.session_id column)
- No server-side state beyond what's in database

**Rationale**: ChatKit session IDs stored in database for stateless conversation retrieval.

### ✅ Single Source of Truth (Section 2.3)

**Compliance**: PASS

- Tasks: phase2-backend remains authoritative (MCP tools still call Phase 2 REST API)
- Conversations: phase3-backend owns (unchanged ownership)
- Database is only persistent store

**Rationale**: No changes to task operation flow (MCP → Phase 2 backend).

### ✅ Backward Compatibility (Section 2.4)

**Compliance**: PASS

- Phase 2 backend code: **Zero changes**
- Phase 2 endpoints: **Zero modifications**
- Phase 2 frontend: **Continues working**
- Database schema: **Only adds session_id column to conversations table (no changes to tasks/users)**

**Rationale**: Migration confined to phase3-frontend and phase3-backend; Phase 2 untouched.

### ✅ Separation of Concerns (Section 2.5)

**Compliance**: PASS

- phase2-backend: Still exclusively handles task CRUD
- phase3-backend: Still exclusively handles chat endpoint (now via ChatKitServer)
- phase3-mcp-server: Still exclusively provides MCP tools

**Rationale**: ChatKit migration doesn't change service boundaries.

### ✅ Technology Stack (Section 3)

**Compliance**: PASS with ADDITIONS

- Frontend (Phase 3): **ChatKit added** (OpenAI ChatKit + Next.js 16+)
- Backend (All): **ChatKit Python SDK added** (openai-chatkit package)
- All other technologies unchanged

**Rationale**: ChatKit is official OpenAI package, aligns with OpenAI Agents SDK already in use.

### ✅ Database Schema (Section 4)

**Compliance**: PASS with MINOR ADDITION

- Existing tables: **Unchanged** (users, tasks from Phase 2)
- New column: **conversations.session_id TEXT** (for ChatKit session mapping)
- Migration: **Additive only** (no alterations or deletions)

**Rationale**: Per clarification, schema modifications allowed for conversations/messages tables only.

### ✅ MCP Tools Specification (Section 5)

**Compliance**: PASS

- All 5 tools unchanged (add_task, list_tasks, complete_task, delete_task, update_task)
- MCP server unchanged
- Tool contracts unchanged

**Rationale**: ChatKit backend calls same MCP tools via existing MCPClient.

### ✅ Non-Functional Requirements (Section 6)

**Compliance**: PASS

- Performance: <5s response maintained (FR-022)
- Security: JWT validation preserved (FR-011), user isolation maintained (FR-020)
- Quality: Comprehensive E2E testing required (per clarification)
- UX: Conversational responses preserved (natural language → MCP tools)

**Rationale**: ChatKit enhances UX while maintaining performance/security standards.

### ✅ Constraints & Non-Goals (Section 7)

**Compliance**: PASS

- ❌ NO changes to phase2-backend: **Preserved**
- ❌ NO direct database access from MCP server: **Preserved**
- ✅ MUST use OpenAI Agents SDK: **Still used** (ChatKitServer integrates with it)
- ✅ MUST use Official MCP SDK: **Unchanged**

**Rationale**: ChatKit migration doesn't violate any constraints.

---

## Project Structure

### Documentation (this feature)

```
specs/003-chatkit-migration/
├── spec.md                # Feature specification (already created)
├── plan.md                # This file (implementation plan)
├── research.md            # Phase 0 research (created)
├── data-model.md          # Phase 1 data model (created)
├── quickstart.md          # Phase 1 testing guide (created)
├── contracts/             # Phase 1 API contracts
│   └── chatkit-api.yaml   # OpenAPI spec for /chatkit endpoints (created)
└── tasks.md               # Phase 2 (created by /sp.tasks, not /sp.plan)
```

### Source Code (repository root)

**Phase 3 Frontend** (`/phase3-frontend/`):
```
phase3-frontend/
├── app/
│   └── chat/
│       └── page.tsx                      # [MODIFY] Replace ChatInterface with ChatKit component
├── components/
│   ├── ChatInterface.tsx                 # [DELETE] Remove custom implementation
│   ├── ChatMessage.tsx                   # [DELETE] Remove custom implementation
│   ├── TagBadge.tsx                      # [PRESERVE] May be used in custom widgets
│   └── LoadingSpinner.tsx                # [PRESERVE] Used elsewhere
├── lib/
│   ├── api.ts                            # [MODIFY] Add getChatKitSession() function
│   ├── auth.ts                           # [PRESERVE] Unchanged
│   └── auth-client.ts                    # [PRESERVE] Unchanged
└── package.json                          # [MODIFY] Add @openai/chatkit-react dependency
```

**Phase 3 Backend** (`/phase3-backend/app/`):
```
phase3-backend/app/
├── chatkit/
│   ├── __init__.py                       # [NEW] Package init
│   ├── server.py                         # [NEW] TodoChatKitServer class
│   └── tools.py                          # [NEW] ChatKit tool definitions (wraps MCP client)
├── routes/
│   ├── chat.py                           # [DELETE] Remove old /api/chat endpoint
│   └── chatkit.py                        # [NEW] /api/chatkit/session and /chatkit endpoints
├── agents/
│   ├── openai_agent.py                   # [PRESERVE] May reuse parts for ChatKitServer
│   └── mcp_client.py                     # [PRESERVE] Unchanged, reused by ChatKit tools
├── auth/
│   └── jwt_middleware.py                 # [PRESERVE] Unchanged, reused for /chatkit/session
├── models/
│   └── chat.py                           # [MODIFY] Add session_id field to Conversation model
├── main.py                               # [MODIFY] Register new chatkit routes, remove old chat routes
└── requirements.txt                      # [MODIFY] Add openai-chatkit dependency
```

**Database Migrations** (`/backend/migrations/`):
```
backend/migrations/
└── 006_add_session_id_to_conversations.sql  # [NEW] Add session_id column
```

**Phase 3 MCP Server** (unchanged):
```
phase3-mcp-server/
└── (no changes)
```

**Structure Decision**: Multi-service web application (phase3-frontend + phase3-backend). Migration confined to phase3 services, preserving phase2 and mcp-server unchanged.

---

## Complexity Tracking

*No constitution violations detected. This section intentionally left empty.*

---

## Architecture Decisions

### 1. Data Flow: Frontend → Backend → MCP → Phase 2

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (Next.js + React 19)                                   │
│                                                                  │
│ 1. User Authentication (Better-Auth)                            │
│    │ Login → JWT token → Cached (5min TTL)                      │
│    │                                                             │
│ 2. ChatKit Session Initialization                               │
│    │ useChatKit({                                                │
│    │   api: {                                                    │
│    │     async getClientSecret() {                              │
│    │       jwt = await getAuthToken()                           │
│    │       POST /api/chatkit/session + Bearer {jwt}             │
│    │       return client_secret                                 │
│    │     }                                                       │
│    │   }                                                         │
│    │ })                                                          │
│    │                                                             │
│ 3. Chat Interaction                                             │
│    <ChatKit control={control} className="..." />                │
│    User sends message → ChatKit handles protocol                │
│                                                                  │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ POST /chatkit
             │ { session_id, messages: [...] }
             │
┌────────────▼────────────────────────────────────────────────────┐
│ BACKEND (FastAPI + ChatKitServer)                               │
│                                                                  │
│ 4. ChatKitServer.respond()                                      │
│    │                                                             │
│    ├─ Extract user_id from session metadata                     │
│    ├─ Get/create conversation via session_id mapping            │
│    ├─ Fetch conversation history (last 20 messages from DB)     │
│    │                                                             │
│    ├─ Call OpenAI Agents SDK                                    │
│    │  openai.chat.completions.create(                           │
│    │    messages=[...history, new_message],                     │
│    │    tools=[add_task, list_tasks, ...],                      │
│    │    stream=True  # Progressive JSON                         │
│    │  )                                                          │
│    │                                                             │
│    ├─ For each tool_call in response:                           │
│    │  │                                                          │
│    │  └─ Execute MCP Tool ────────────┐                         │
│    │                                    │                        │
│    ├─ Save user + assistant messages   │                        │
│    │  to PostgreSQL                    │                        │
│    │                                    │                        │
│    └─ Return Turn(message=...,         │                        │
│                   is_partial=True/False)│                        │
│                                         │                        │
└─────────────────────────────────────────┼────────────────────────┘
                                          │
                                          │ HTTP POST
                                          │ /mcp
                                          │
┌─────────────────────────────────────────▼────────────────────────┐
│ MCP SERVER (MCP Tools)                                           │
│                                                                   │
│ 5. Execute Tool (e.g., add_task)                                 │
│    │                                                              │
│    ├─ Extract parameters                                         │
│    ├─ Call Phase2Client ──────────────┐                          │
│    └─ Return result                   │                          │
│                                        │                          │
└────────────────────────────────────────┼──────────────────────────┘
                                         │
                                         │ HTTP POST
                                         │ /api/{user_id}/tasks
                                         │
┌────────────────────────────────────────▼──────────────────────────┐
│ PHASE 2 BACKEND (FastAPI)                                        │
│                                                                   │
│ 6. Task CRUD Operation                                           │
│    │ Validate JWT                                                │
│    │ Execute database operation (INSERT/UPDATE/DELETE)           │
│    └─ Return task object                                         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

**Key Points**:
- JWT token obtained once, cached 5min, passed to /chatkit/session endpoint
- ChatKit session created with user_id in metadata
- ChatKitServer extracts user_id from session for all operations
- Conversation history fetched from PostgreSQL (stateless)
- MCP tools unchanged, still call Phase 2 backend

---

### 2. Streaming Approach: Progressive JSON

**Decision**: Use ChatKit's Turn objects with `is_partial=True` for incremental updates

**Implementation**:
```python
async def respond(self, messages: list[Message]) -> AsyncGenerator[Turn, None]:
    # ... setup ...

    stream = await self.openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=openai_messages,
        tools=self.mcp_tools,
        stream=True
    )

    full_content = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            full_content += chunk.choices[0].delta.content
            yield Turn(message=full_content, is_partial=True)

    # Final turn
    await self.save_message(conversation_id, "assistant", full_content)
    yield Turn(message=full_content, is_partial=False)
```

**Rationale**: Per clarification, progressive JSON chosen over SSE for better HTTP compatibility and simpler implementation.

---

### 3. Authentication Token Passing

**Frontend**:
```typescript
const { control } = useChatKit({
  api: {
    async getClientSecret() {
      const jwt = await getAuthToken(); // Existing function with 5min cache
      const res = await fetch('/api/chatkit/session', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${jwt}` }
      });
      return (await res.json()).client_secret;
    }
  }
});
```

**Backend**:
```python
@app.post("/api/chatkit/session")
async def create_chatkit_session(
    current_user: CurrentUser = Depends(get_current_user)  # Existing JWT middleware
):
    session = await chatkit_server.create_session(
        metadata={"user_id": current_user.user_id}
    )
    return {"client_secret": session.client_secret}

class TodoChatKitServer(ChatKitServer):
    def get_user_id(self) -> str:
        return self.session.metadata["user_id"]
```

**Rationale**: Reuses existing JWT middleware (zero changes to auth logic), embeds user_id in ChatKit session for stateless access.

---

### 4. Tool Integration Pattern

**ChatKit Tools → MCP Client Wrapper**:
```python
from openai_chatkit import Tool

class TodoChatKitServer(ChatKitServer):
    def __init__(self, mcp_client: MCPClient):
        super().__init__()
        self.mcp_client = mcp_client

    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name="add_task",
                description="Create a new task",
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["title"]
                },
                handler=self._handle_add_task
            ),
            # ... (list_tasks, complete_task, update_task, delete_task)
        ]

    async def _handle_add_task(self, title: str, description: str = "") -> dict:
        user_id = self.get_user_id()
        return await self.mcp_client.add_task(
            user_id=user_id,
            title=title,
            description=description
        )
```

**Rationale**: ChatKit Tool objects map to existing MCP client methods, preserving MCP server unchanged.

---

### 5. Conversation Persistence Strategy

**Database Mapping**:
- Add `session_id TEXT` column to conversations table
- On first message: `INSERT INTO conversations (user_id, session_id) VALUES (...)`
- On subsequent messages: `SELECT conversation_id FROM conversations WHERE session_id = ?`
- Fetch history: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC LIMIT 20`

**Session Lifecycle**:
- ChatKit session ID stored in conversations.session_id
- When JWT expires (24h), new login creates new ChatKit session → new conversation
- Aligns with clarification: "Login session lifecycle"

**Clean Slate Migration**:
```sql
-- Run before deployment
TRUNCATE conversations CASCADE; -- Also clears messages due to CASCADE
```

**Rationale**: Minimal schema change, aligns with clarification requirements.

---

## Technology Choices

### Frontend Packages

| Package | Version | Purpose |
|---------|---------|---------|
| @openai/chatkit-react | ^1.0.0 | Official ChatKit React bindings |
| ChatKit.js (CDN) | Latest | Web component (loaded from https://cdn.platform.openai.com/deployments/chatkit/chatkit.js) |

**Installation**:
```bash
cd phase3-frontend
npm install @openai/chatkit-react
```

**package.json** modification:
```json
{
  "dependencies": {
    "@openai/chatkit-react": "^1.0.0",
    "next": "^16.0.0",
    "react": "^19.0.0"
  }
}
```

---

### Backend Packages

| Package | Version | Purpose |
|---------|---------|---------|
| openai-chatkit | latest | Official ChatKit Python SDK (ChatKitServer base class) |
| openai | ^1.0.0 | OpenAI API client (existing, for chat.completions) |

**Installation**:
```bash
cd phase3-backend
pip install openai-chatkit  # or uv pip install openai-chatkit
```

**requirements.txt** modification:
```txt
fastapi>=0.100.0
openai-chatkit>=1.0.0
openai>=1.0.0
sqlmodel>=0.0.14
```

---

### Environment Variables

**phase3-frontend/.env.local**:
```env
# Existing (unchanged)
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=<jwt-secret>
BETTER_AUTH_URL=http://localhost:3001

# New (if needed)
NEXT_PUBLIC_CHATKIT_CDN=https://cdn.platform.openai.com/deployments/chatkit/chatkit.js
```

**phase3-backend/.env**:
```env
# Existing (unchanged)
DATABASE_URL=postgresql://...
JWT_SECRET=<jwt-secret>
OPENAI_API_KEY=sk-...
MCP_SERVER_URL=http://localhost:8002
PHASE2_BACKEND_URL=http://localhost:8000

# No new variables needed (ChatKit uses existing OPENAI_API_KEY)
```

---

## Implementation Approach

### Phase 1: Backend ChatKit Server Setup

**Files to Create**:

1. **`phase3-backend/app/chatkit/__init__.py`**:
```python
from .server import TodoChatKitServer

__all__ = ["TodoChatKitServer"]
```

2. **`phase3-backend/app/chatkit/server.py`**:
```python
from openai_chatkit import ChatKitServer, Message, Turn
from app.agents.mcp_client import MCPClient
from app.services.chat_service import ChatService
from typing import AsyncGenerator

class TodoChatKitServer(ChatKitServer):
    def __init__(self, mcp_client: MCPClient, chat_service: ChatService):
        super().__init__()
        self.mcp_client = mcp_client
        self.chat_service = chat_service

    def get_user_id(self) -> str:
        return self.session.metadata.get("user_id")

    async def respond(self, messages: list[Message]) -> AsyncGenerator[Turn, None]:
        user_id = self.get_user_id()
        session_id = self.session.id

        # Get or create conversation
        conversation = await self.chat_service.get_or_create_conversation(
            user_id=user_id,
            session_id=session_id
        )

        # Fetch history
        history = await self.chat_service.get_message_history(
            conversation_id=conversation.id,
            limit=20
        )

        # Build OpenAI messages
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ] + [{"role": "user", "content": messages[-1].content}]

        # Call OpenAI with streaming
        stream = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            tools=self.get_tools(),
            stream=True
        )

        full_content = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                full_content += chunk.choices[0].delta.content
                yield Turn(message=full_content, is_partial=True)

        # Handle tool calls if present
        # ... (implement tool call handling)

        # Save messages
        await self.chat_service.save_message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=messages[-1].content
        )
        await self.chat_service.save_message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=full_content
        )

        yield Turn(message=full_content, is_partial=False)

    def get_tools(self) -> list[dict]:
        # Define 5 MCP tools (add_task, list_tasks, etc.)
        # ... (see research.md for full implementation)
        pass
```

3. **`phase3-backend/app/routes/chatkit.py`**:
```python
from fastapi import APIRouter, Depends, Request
from app.auth.jwt_middleware import get_current_user, CurrentUser
from app.chatkit.server import TodoChatKitServer
from app.agents.mcp_client import MCPClient
from app.services.chat_service import ChatService

router = APIRouter()
mcp_client = MCPClient()
chat_service = ChatService()
chatkit_server = TodoChatKitServer(mcp_client, chat_service)

@router.post("/api/chatkit/session")
async def create_chatkit_session(
    current_user: CurrentUser = Depends(get_current_user)
):
    session = await chatkit_server.create_session(
        metadata={"user_id": current_user.user_id}
    )
    return {"client_secret": session.client_secret}

@router.post("/chatkit")
async def handle_chatkit_message(request: Request):
    return await chatkit_server.handle_request(request)
```

**Files to Modify**:

4. **`phase3-backend/app/main.py`**:
```python
# Remove old chat routes
# from app.routes import chat  # DELETE THIS LINE

# Add new chatkit routes
from app.routes import chatkit

app.include_router(chatkit.router)
```

5. **`phase3-backend/app/models/chat.py`**:
```python
class Conversation(SQLModel, table=True):
    # ... existing fields ...
    session_id: Optional[str] = Field(default=None, unique=True)  # ADD THIS
```

**Files to Delete**:

6. **`phase3-backend/app/routes/chat.py`** - Remove old /api/chat endpoint

---

### Phase 2: Frontend ChatKit Component Integration

**Files to Create**:

1. **Add ChatKit script to `phase3-frontend/app/layout.tsx`**:
```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          async
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

**Files to Modify**:

2. **`phase3-frontend/app/chat/page.tsx`**:
```tsx
"use client";

import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { getAuthToken } from '@/lib/api';
import { AuthGuard } from '@/components/AuthGuard';
import { Navigation } from '@/components/Navigation';

export default function ChatPage() {
  const { control } = useChatKit({
    api: {
      async getClientSecret() {
        const jwt = await getAuthToken();
        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json'
          }
        });

        if (!res.ok) {
          throw new Error('Failed to create ChatKit session');
        }

        const data = await res.json();
        return data.client_secret;
      }
    },
    theme: {
      colors: {
        primary: '#2563eb',      // blue-600
        secondary: '#f3f4f6',    // gray-100
        text: '#111827',         // gray-900
        background: '#ffffff',
      },
      borderRadius: '0.5rem',
    }
  });

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Chat Assistant
          </h1>
          <p className="text-gray-600 mb-6">
            Manage your tasks using natural language
          </p>
          <ChatKit
            control={control}
            className="h-[600px] w-full rounded-lg shadow-lg bg-white"
          />
        </main>
      </div>
    </AuthGuard>
  );
}
```

3. **`phase3-frontend/lib/api.ts`**:
```typescript
// Keep existing getAuthToken function (unchanged)

// No additional changes needed - ChatKit session handled in page.tsx
```

4. **`phase3-frontend/package.json`**:
```json
{
  "dependencies": {
    "@openai/chatkit-react": "^1.0.0",
    "next": "^16.0.0",
    "react": "^19.0.0",
    "better-auth": "^1.4.6"
    // ... other deps
  }
}
```

**Files to Delete**:

5. **`phase3-frontend/components/ChatInterface.tsx`** - Remove custom chat UI
6. **`phase3-frontend/components/ChatMessage.tsx`** - Remove custom message rendering

---

### Phase 3: Database Migration

**Files to Create**:

1. **`backend/migrations/006_add_session_id_to_conversations.sql`**:
```sql
-- Add session_id column for ChatKit session mapping
ALTER TABLE conversations
ADD COLUMN session_id TEXT;

-- Create unique index
CREATE UNIQUE INDEX idx_conversations_session_id
ON conversations(session_id)
WHERE session_id IS NOT NULL;

-- Add comment
COMMENT ON COLUMN conversations.session_id IS
'ChatKit session ID for mapping frontend sessions to database conversations';
```

**Deployment Steps**:
```bash
# Apply migration
psql "$DATABASE_URL" < backend/migrations/006_add_session_id_to_conversations.sql

# Clear existing data (clean slate per clarification)
psql "$DATABASE_URL" -c "TRUNCATE conversations CASCADE;"
```

---

### Phase 4: Testing & Validation

**Testing Strategy** (per clarification: comprehensive E2E):

1. **Functional Tests** (all user stories P1-P4):
   - Create task: "Add task to buy groceries tomorrow"
   - List tasks: "What are my tasks?"
   - Complete task: "Mark 'buy groceries' as done"
   - Update task: "Change deadline to next Friday"
   - Delete task: "Delete the task about X"
   - Authentication: Login, logout, session expiry
   - Conversation persistence: Refresh page, verify history

2. **Edge Case Tests**:
   - Network failures
   - OpenAI API errors
   - Database write failures
   - Rate limiting
   - Invalid task references

3. **Performance Tests**:
   - Response time <5s for all operations
   - 100+ concurrent users (load testing)
   - Progressive JSON streaming (verify incremental rendering)

4. **Security Tests**:
   - JWT validation
   - User isolation (cannot access others' conversations/tasks)
   - Rate limiting enforcement

5. **Regression Tests**:
   - Phase 2 frontend still works
   - Phase 2 backend endpoints unchanged
   - No breaking changes to task API

**Test Execution** (see quickstart.md for detailed test scenarios).

---

### Phase 5: Deployment

**Steps**:
1. ✅ Backend: `git add`, `git commit`, `git push` → Railway auto-deploys phase3-backend
2. ✅ Frontend: `git push` → Vercel auto-deploys phase3-frontend
3. ✅ Database: Run migration SQL via Neon dashboard or psql
4. ✅ Verify: Test all critical paths in production

**Rollback Plan** (if needed):
```bash
# Revert migration commits
git revert HEAD~3..HEAD
git push

# Railway/Vercel will auto-deploy previous version
# Database rollback (if needed):
psql "$DATABASE_URL" -c "ALTER TABLE conversations DROP COLUMN session_id;"
```

---

## Risk Mitigation

### Potential Breaking Changes

| Risk | Impact | Mitigation |
|------|--------|------------|
| ChatKit CDN unavailable | ChatKit won't load | Fallback error message, monitor CDN status |
| ChatKit incompatible with React 19 | Frontend crashes | Test thoroughly in dev, check GitHub issues |
| Progressive JSON not working | Poor UX (wait for full response) | Test streaming early, fallback to non-streaming |
| Session mapping fails | Conversations lost/duplicated | Test session lifecycle thoroughly |
| MCP tools break | Task operations fail | Comprehensive integration tests |

### Fallback Strategies

1. **If ChatKit has critical bugs**:
   - Since not in production yet, pause migration
   - Report issue to OpenAI GitHub
   - Wait for fix or implement workaround

2. **If performance degrades**:
   - Profile ChatKitServer.respond() method
   - Optimize database queries (add indexes if needed)
   - Consider caching conversation history

3. **If authentication breaks**:
   - Verify JWT_SECRET matches across services
   - Check Better-Auth JWKS endpoint
   - Test token expiry edge cases

---

## Testing Strategy

### Unit Tests (Backend)

```bash
cd phase3-backend
pytest tests/chatkit/test_server.py -v
pytest tests/chatkit/test_tools.py -v
```

**Test Files to Create**:
- `tests/chatkit/test_server.py` - Test TodoChatKitServer.respond()
- `tests/chatkit/test_tools.py` - Test MCP tool wrappers

### Integration Tests (Full Stack)

**Manual E2E Testing** (see quickstart.md for 12 detailed test scenarios)

**Automated E2E** (optional):
```bash
cd phase3-frontend
npm run test:e2e  # Playwright or Cypress tests
```

### Load Testing

```bash
# Using k6 or locust to simulate 100+ concurrent users
k6 run tests/load/chatkit-concurrent.js
```

**Expected Results**:
- 95th percentile response time <5s
- No errors under 100 concurrent users
- Database connection pool doesn't exhaust

---

## Migration Path

### Step-by-Step Execution

**Phase 1: Backend Setup** (Estimated: 3-4 hours)
1. Install openai-chatkit package
2. Create app/chatkit/server.py (TodoChatKitServer)
3. Create app/chatkit/tools.py (MCP tool wrappers)
4. Create app/routes/chatkit.py (/chatkit endpoints)
5. Modify app/main.py (register new routes)
6. Modify app/models/chat.py (add session_id field)
7. Delete app/routes/chat.py
8. Test locally: `uvicorn app.main:app --reload`

**Phase 2: Frontend Setup** (Estimated: 2-3 hours)
1. Install @openai/chatkit-react
2. Add ChatKit CDN script to layout.tsx
3. Replace ChatInterface with ChatKit component in app/chat/page.tsx
4. Delete components/ChatInterface.tsx and ChatMessage.tsx
5. Test locally: `npm run dev`

**Phase 3: Database Migration** (Estimated: 30 minutes)
1. Create migration SQL file
2. Apply to local database first
3. Test conversation mapping
4. Apply to production database (Neon)
5. Truncate conversations/messages (clean slate)

**Phase 4: Integration Testing** (Estimated: 4-6 hours)
1. Test all 12 scenarios in quickstart.md
2. Test edge cases
3. Performance testing
4. Security testing
5. Regression testing (Phase 2)

**Phase 5: Deployment** (Estimated: 1 hour)
1. Commit and push to GitHub
2. Railway auto-deploys backend
3. Vercel auto-deploys frontend
4. Apply database migration to production
5. Smoke test in production
6. Monitor logs for errors

**Total Estimated Time**: 10-15 hours

---

## Success Criteria

From spec.md (all must pass):

- ✅ **SC-001**: ChatKit components render correctly
- ✅ **SC-002**: All task operations work (create, list, complete, update, delete)
- ✅ **SC-003**: Authentication integrates seamlessly (JWT → ChatKit session)
- ✅ **SC-004**: Conversation history persists across refreshes (session-scoped)
- ✅ **SC-005**: MCP tool integration works (tag extraction)
- ✅ **SC-006**: Progressive JSON streaming works
- ✅ **SC-007**: Custom theming matches Phase 3 design
- ✅ **SC-008**: No Phase 2 regressions
- ✅ **SC-009**: Same or better workflow time
- ✅ **SC-010**: 100+ concurrent users supported

**Verification**: Run all tests in quickstart.md, check all boxes.

---

## Next Steps

After planning phase (/sp.plan) completes:

1. **Run `/sp.tasks`** to generate dependency-ordered task breakdown
2. **Review plan.md** with team/user
3. **Begin implementation** following Phase 1-5 sequence
4. **Test continuously** (don't wait until end)
5. **Create PHR** after planning (track decision rationale)

---

## References

- [Research Document](./research.md) - Technical investigation findings
- [Data Model](./data-model.md) - Database schema and entities
- [Quickstart Guide](./quickstart.md) - Testing scenarios
- [API Contracts](./contracts/chatkit-api.yaml) - OpenAPI specification
- [Feature Specification](./spec.md) - Requirements and success criteria
- [Constitution (v3.0.0)](../../.specify/memory/constitution.md) - Architectural principles

**External Documentation**:
- [ChatKit Platform Docs](https://platform.openai.com/docs/guides/chatkit)
- [chatkit-python SDK](https://openai.github.io/chatkit-python/)
- [@openai/chatkit-react](https://openai.github.io/chatkit-js/)
