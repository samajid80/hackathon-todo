# Research: ChatKit Migration Technical Investigation

**Feature**: 003-chatkit-migration
**Date**: 2025-12-26
**Purpose**: Resolve technical unknowns for migrating custom chat implementation to OpenAI ChatKit

---

## 1. ChatKit Frontend Integration (@openai/chatkit-react)

### Decision: Use @openai/chatkit-react with useChatKit hook pattern

**Installation**:
```bash
npm install @openai/chatkit-react
```

**Core Integration Pattern**:
```jsx
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function ChatPage() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        // Fetch session token from backend
        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${jwtToken}` // Pass Better-Auth JWT
          },
        });
        const { client_secret } = await res.json();
        return client_secret;
      },
    },
  });

  return <ChatKit control={control} className="h-[600px] w-full" />;
}
```

**Key Findings**:
- ChatKit component is a web component wrapped by React bindings
- Requires loading ChatKit.js from CDN: `https://cdn.platform.openai.com/deployments/chatkit/chatkit.js`
- Authentication handled via `getClientSecret` callback that fetches session tokens from backend
- Component accepts className prop for styling integration with Tailwind CSS
- useChatKit hook returns control object for managing chat state

**Rationale**:
- Official OpenAI package ensures compatibility and support
- Hook pattern aligns with existing React 19 patterns in Phase 3
- getClientSecret callback provides clean integration point for Better-Auth JWT tokens

**Alternatives Considered**:
- Custom implementation: Rejected due to spec requirement for official ChatKit package
- Alternative chat libraries: Rejected - hackathon requires OpenAI ChatKit specifically

---

## 2. ChatKit Backend Integration (chatkit-python)

### Decision: Use ChatKitServer base class with respond method

**Installation**:
```bash
pip install openai-chatkit
```

**Core Server Pattern**:
```python
from openai_chatkit import ChatKitServer, Message, Turn

class TodoChatKitServer(ChatKitServer):
    async def respond(self, messages: list[Message]) -> Turn:
        # 1. Extract user message
        user_message = messages[-1].content

        # 2. Get conversation history from database
        conversation_id = self.get_conversation_id_from_session()
        history = await fetch_conversation_history(conversation_id)

        # 3. Call OpenAI with tools
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[...history, {"role": "user", "content": user_message}],
            tools=self.get_mcp_tools()
        )

        # 4. Execute tool calls via MCP client
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                result = await self.mcp_client.invoke_tool(
                    tool_call.function.name,
                    json.loads(tool_call.function.arguments)
                )

        # 5. Save conversation to database
        await save_messages(conversation_id, user_message, response.message)

        # 6. Return Turn with assistant message
        return Turn(message=response.choices[0].message.content)

# FastAPI integration
from fastapi import FastAPI

app = FastAPI()
server = TodoChatKitServer()

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    return await server.handle_request(request)
```

**Key Findings**:
- ChatKitServer provides base class with respond method as main extension point
- Integration with FastAPI via handle_request method
- Supports async operations for database and API calls
- Turn object represents response with optional widgets and streaming
- Session management handled internally by ChatKitServer

**Rationale**:
- Minimal refactoring from current OpenAI Agents SDK implementation
- respond method maps cleanly to existing chat endpoint logic
- Built-in session handling simplifies conversation persistence
- Tool calling pattern compatible with existing MCP client

**Alternatives Considered**:
- Custom FastAPI endpoint calling OpenAI directly: Rejected - loses ChatKit session management and widget support
- Modifying existing /api/chat endpoint: Rejected - ChatKit requires specific protocol not compatible with current implementation

---

## 3. Authentication Integration

### Decision: Pass JWT token through getClientSecret callback, validate on backend

**Frontend Flow**:
```typescript
// lib/api.ts - Updated getAuthToken function
async function getAuthToken(): Promise<string | null> {
  // Existing 5-minute cache logic
  if (cachedToken && Date.now() < cachedToken.expiry) {
    return cachedToken.token;
  }

  const response = await authClient.getSession({
    fetchOptions: {
      onSuccess: (ctx) => {
        const token = ctx.response.headers.get("set-auth-jwt");
        if (token) {
          cachedToken = { token, expiry: Date.now() + 5 * 60 * 1000 };
        }
      }
    }
  });

  return cachedToken?.token || null;
}

// ChatPage.tsx - Use in getClientSecret
const { control } = useChatKit({
  api: {
    async getClientSecret() {
      const jwt = await getAuthToken();
      const res = await fetch('/api/chatkit/session', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${jwt}`
        },
      });
      const { client_secret } = await res.json();
      return client_secret;
    },
  },
});
```

**Backend Flow**:
```python
from fastapi import Depends, HTTPException
from app.auth.jwt_middleware import get_current_user, CurrentUser

@app.post("/api/chatkit/session")
async def create_chatkit_session(
    current_user: CurrentUser = Depends(get_current_user)
):
    # Validate JWT using existing middleware
    # Create ChatKit session with user_id embedded
    session = await chatkit_server.create_session(user_id=current_user.user_id)
    return {"client_secret": session.client_secret}

class TodoChatKitServer(ChatKitServer):
    def get_user_id_from_session(self) -> str:
        # Extract user_id from ChatKit session metadata
        return self.session.metadata.get("user_id")

    async def respond(self, messages: list[Message]) -> Turn:
        user_id = self.get_user_id_from_session()
        # Use user_id for conversation scoping and MCP tool calls
```

**Key Findings**:
- Better-Auth JWT tokens can be passed via Authorization header to session creation endpoint
- ChatKit sessions support metadata storage for user_id
- Existing JWT middleware (get_current_user dependency) works unchanged
- Session tokens have separate lifecycle from JWT tokens

**Rationale**:
- Preserves existing authentication architecture
- No changes to Better-Auth or JWT validation logic
- User isolation maintained through session metadata
- Aligns with clarification: "Login session lifecycle (Better-Auth JWT session, 24-hour duration)"

**Alternatives Considered**:
- Custom headers on every ChatKit request: Rejected - ChatKit protocol doesn't support this
- Embedding JWT in ChatKit session: Rejected - security risk, ChatKit sessions may be long-lived

---

## 4. Conversation Persistence Strategy

### Decision: Map ChatKit sessions to PostgreSQL conversation_id, use existing tables

**Database Schema** (unchanged from current Phase 3):
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Integration Pattern**:
```python
class TodoChatKitServer(ChatKitServer):
    async def respond(self, messages: list[Message]) -> Turn:
        user_id = self.get_user_id_from_session()

        # Get or create conversation for this session
        chatkit_session_id = self.session.id
        conversation = await get_or_create_conversation(
            user_id=user_id,
            session_id=chatkit_session_id
        )

        # Fetch history from database
        db_messages = await fetch_messages(conversation.id, limit=20)

        # Call OpenAI with history
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in db_messages
        ] + [{"role": "user", "content": messages[-1].content}]

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            tools=self.mcp_tools
        )

        # Save both messages
        await save_message(conversation.id, user_id, "user", messages[-1].content)
        await save_message(conversation.id, user_id, "assistant", response.choices[0].message.content)

        return Turn(message=response.choices[0].message.content)
```

**Session-to-Conversation Mapping**:
- Add `session_id TEXT` column to conversations table (migration required)
- On first message from ChatKit session, create new conversation row
- Subsequent messages in same session reuse same conversation_id
- When JWT session expires (24 hours), ChatKit session also expires, clearing history

**Key Findings**:
- ChatKit session IDs can be stored in conversations table for mapping
- Existing message history logic works with minor modification
- No changes to messages table structure needed
- Aligns with clarification: "Start with clean slate - Clear/truncate conversations and messages tables"

**Rationale**:
- Minimal schema changes (only add session_id column)
- Preserves existing conversation history patterns
- Session expiry naturally aligns with JWT lifecycle
- Supports clarification requirement for login session scope

**Alternatives Considered**:
- ChatKit's built-in storage: Rejected - loses control over PostgreSQL persistence, doesn't support custom queries
- Separate ChatKit conversation table: Rejected - duplicates data model, complicates queries

---

## 5. Progressive JSON Streaming Implementation

### Decision: Use ChatKit's Turn with progressive content updates

**Backend Implementation**:
```python
from openai_chatkit import Turn, StreamingResponse

class TodoChatKitServer(ChatKitServer):
    async def respond(self, messages: list[Message]) -> Turn:
        # ... (setup code)

        # Stream OpenAI response
        stream = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            tools=self.mcp_tools,
            stream=True  # Enable streaming
        )

        full_content = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                full_content += chunk.choices[0].delta.content
                # Yield progressive updates
                yield Turn(message=full_content, is_partial=True)

        # Final response
        await save_message(conversation.id, user_id, "assistant", full_content)
        yield Turn(message=full_content, is_partial=False)
```

**Frontend Handling**:
```jsx
// ChatKit component automatically handles streaming responses
// No custom code needed - progressive updates render incrementally
<ChatKit control={control} className="h-[600px] w-full" />
```

**Key Findings**:
- ChatKit supports progressive JSON via Turn objects with is_partial flag
- OpenAI streaming API compatible with ChatKit streaming pattern
- Frontend component handles progressive updates automatically
- Aligns with clarification: "Progressive JSON - Chunked JSON responses with incremental updates"

**Rationale**:
- Better UX than waiting for full response
- Compatible with existing OpenAI Agents SDK streaming
- No custom WebSocket/SSE implementation needed
- Matches clarification decision for progressive JSON

**Alternatives Considered**:
- Server-Sent Events (SSE): Rejected per clarification preference for progressive JSON
- WebSocket: Rejected - unnecessary complexity, not required by ChatKit

---

## 6. MCP Tool Integration with ChatKit

### Decision: Reuse existing MCP client, bind tools to ChatKitServer

**Tool Definition Pattern**:
```python
from openai_chatkit import Tool

class TodoChatKitServer(ChatKitServer):
    def __init__(self, mcp_client: MCPClient):
        super().__init__()
        self.mcp_client = mcp_client
        self.mcp_tools = self.create_mcp_tools()

    def create_mcp_tools(self) -> list[Tool]:
        """Define ChatKit tools that call MCP client"""
        return [
            Tool(
                name="add_task",
                description="Create a new task",
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                    },
                    "required": ["title"]
                },
                async def handler(title: str, description: str = "") -> dict:
                    user_id = self.get_user_id_from_session()
                    return await self.mcp_client.add_task(
                        user_id=user_id,
                        title=title,
                        description=description,
                        jwt_token=self.get_jwt_from_session()
                    )
            ),
            # ... (list_tasks, complete_task, update_task, delete_task)
        ]
```

**Key Findings**:
- ChatKit Tool objects map directly to existing MCP tool contracts
- Existing MCPClient (app/agents/mcp_client.py) can be reused unchanged
- Tools bound to ChatKitServer instance via closure (user_id, jwt_token access)
- Tool results automatically included in conversation context

**Rationale**:
- Zero changes to MCP server or Phase 2 backend
- Preserves existing MCP tool implementations
- Maintains stateless architecture (tools don't store state)
- Compatible with existing tag extraction logic

**Alternatives Considered**:
- OpenAI function calling directly: Rejected - loses MCP abstraction, would require duplicating tool logic
- Custom tool protocol: Rejected - ChatKit provides standard tool system

---

## 7. Widget Customization and Theming

### Decision: Use Tailwind classes + ChatKit theme configuration

**Theming Approach**:
```jsx
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function ChatPage() {
  const { control } = useChatKit({
    api: { getClientSecret },
    theme: {
      colors: {
        primary: '#2563eb',      // blue-600 (user messages)
        secondary: '#f3f4f6',    // gray-100 (assistant messages)
        text: '#111827',         // gray-900
        background: '#ffffff',
      },
      borderRadius: '0.5rem',    // Tailwind rounded-lg
    },
  });

  return (
    <ChatKit
      control={control}
      className="h-[600px] w-full rounded-lg shadow-lg bg-white"
    />
  );
}
```

**Custom Widget for Task Lists**:
```python
from openai_chatkit import Turn, Widget

async def respond(self, messages: list[Message]) -> Turn:
    # After listing tasks via MCP
    tasks = await self.mcp_client.list_tasks(user_id, completed=False)

    # Create custom widget
    task_widget = Widget(
        type="list",
        data={
            "items": [
                {"title": task["title"], "status": "pending"}
                for task in tasks
            ]
        }
    )

    return Turn(
        message=f"You have {len(tasks)} pending tasks:",
        widgets=[task_widget]
    )
```

**Key Findings**:
- ChatKit supports theme object in useChatKit configuration
- Theme colors map to existing Tailwind color scheme
- Custom widgets can be returned in Turn objects for rich displays
- className prop allows Tailwind utility classes

**Rationale**:
- Maintains visual consistency with existing Phase 3 design
- Aligns with clarification: "Custom theming successfully applied - ChatKit interface matches existing Phase 3 design aesthetic"
- Widgets provide better UX for task lists vs plain text

**Alternatives Considered**:
- CSS file overrides: Rejected - theme configuration is cleaner
- Completely custom UI: Rejected - violates requirement to use ChatKit component

---

## 8. Migration Path and Testing Strategy

### Decision: Direct replacement with comprehensive E2E testing before deployment

**Migration Steps**:
1. Install npm/pip packages
2. Implement ChatKitServer in new file (app/chatkit/server.py)
3. Create /api/chatkit/session and /chatkit endpoints
4. Replace ChatInterface component with ChatKit component
5. Run comprehensive E2E tests
6. Remove custom chat implementation files
7. Clear conversations/messages tables (fresh start)
8. Deploy

**Testing Checklist** (per clarification):
- ✅ Functional: All user stories P1-P4 with acceptance scenarios
- ✅ Functional: All task operations (create, list, complete, update, delete)
- ✅ Functional: Authentication flows (login, logout, session expiry)
- ✅ Functional: Conversation history persistence across refreshes
- ✅ Functional: MCP tool integration and tag extraction
- ✅ Edge cases: Network failures, database failures, API failures
- ✅ Performance: <5s response time, 100+ concurrent users
- ✅ Security: JWT validation, user isolation, rate limiting
- ✅ Compatibility: Chrome, Firefox, Safari, Edge
- ✅ Regression: Phase 2 task management still works

**Key Findings**:
- Direct replacement simplifies deployment (no feature flags needed)
- Comprehensive testing required per clarification
- Clean slate approach means no data migration logic needed

**Rationale**:
- Aligns with clarification: "Direct replacement - Remove custom implementation and deploy ChatKit all at once"
- Testing scope matches clarification: "Comprehensive E2E testing"
- No production deployment yet, so rollback is git revert

**Alternatives Considered**:
- Feature flag: Rejected per clarification
- Gradual rollout: Rejected - not in production yet

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Frontend Package | @openai/chatkit-react with useChatKit hook | Official package, React 19 compatible |
| Backend Package | openai-chatkit with ChatKitServer base class | Official SDK, minimal refactoring |
| Streaming | Progressive JSON via Turn.is_partial | Clarification requirement |
| Authentication | JWT via getClientSecret callback | Preserves Better-Auth integration |
| Conversation Storage | PostgreSQL with session_id mapping | Minimal schema change |
| MCP Integration | Reuse existing MCPClient | Zero changes to MCP server |
| Theming | Tailwind + ChatKit theme config | Matches existing design |
| Migration | Direct replacement + E2E testing | Clarification requirement |

---

## Technology Versions

| Package | Version | Source |
|---------|---------|--------|
| @openai/chatkit-react | Latest (1.x+) | [npm](https://www.npmjs.com/package/@openai/chatkit-react) |
| openai-chatkit | Latest | [GitHub](https://github.com/openai/chatkit-python) |
| ChatKit.js (CDN) | Latest | https://cdn.platform.openai.com/deployments/chatkit/chatkit.js |

---

## Sources

- [ChatKit.js GitHub](https://github.com/openai/chatkit-js)
- [@openai/chatkit-react NPM](https://www.npmjs.com/package/@openai/chatkit-react)
- [ChatKit Python SDK](https://openai.github.io/chatkit-python/)
- [ChatKit Python GitHub](https://github.com/openai/chatkit-python)
- [OpenAI ChatKit Docs](https://platform.openai.com/docs/guides/chatkit)
