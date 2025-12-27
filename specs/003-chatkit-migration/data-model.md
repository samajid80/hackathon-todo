# Data Model: ChatKit Migration

**Feature**: 003-chatkit-migration
**Date**: 2025-12-26

---

## Overview

The ChatKit migration maintains existing PostgreSQL schema for conversations and messages with one minor addition to support session mapping. No changes to tasks or users tables (Phase 2 preservation).

---

## Entity Definitions

### 1. Conversation

**Purpose**: Represents a chat session between user and AI assistant, scoped to login session lifecycle (24-hour JWT duration).

**Attributes**:
- `id` (UUID, PK): Unique conversation identifier
- `user_id` (TEXT, FK → users.id): Owner of the conversation
- `session_id` (TEXT, NULLABLE): ChatKit session ID for mapping (NEW)
- `created_at` (TIMESTAMP WITH TIME ZONE): When conversation started
- `updated_at` (TIMESTAMP WITH TIME ZONE): Last message timestamp

**Relationships**:
- `user_id` → `users.id` (many-to-one, CASCADE DELETE)
- Has many `messages` (one-to-many)

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `(user_id, created_at DESC)` - List user's recent conversations
- INDEX on `session_id` - Map ChatKit sessions to conversations (NEW)

**Validation Rules**:
- `user_id` must exist in users table
- `session_id` unique when not null
- `updated_at` >= `created_at`

**State Transitions**:
- Created: When user sends first message in new session
- Updated: On every new message
- Deleted: When user's JWT session expires (24 hours) or user account deleted

**Lifecycle**:
- Lifespan: Duration of login session (max 24 hours per Better-Auth JWT)
- Cleared on: Logout, session expiry, account deletion
- Not migrated from custom implementation (clean slate approach)

---

### 2. Message

**Purpose**: Individual chat messages within a conversation (user input or assistant response).

**Attributes**:
- `id` (UUID, PK): Unique message identifier
- `user_id` (TEXT, FK → users.id): Message owner (for user isolation)
- `conversation_id` (UUID, FK → conversations.id): Parent conversation
- `role` (VARCHAR(20), CHECK): Message sender ("user", "assistant", "system")
- `content` (TEXT): Message text content
- `created_at` (TIMESTAMP WITH TIME ZONE): When message was sent/received

**Relationships**:
- `user_id` → `users.id` (many-to-one, CASCADE DELETE)
- `conversation_id` → `conversations.id` (many-to-one, CASCADE DELETE)

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `(conversation_id, created_at ASC)` - Fetch conversation history in chronological order
- INDEX on `(user_id, created_at DESC)` - List user's recent messages across conversations

**Validation Rules**:
- `role` IN ('user', 'assistant', 'system')
- `content` NOT NULL, length > 0
- `user_id` matches conversation's user_id (data integrity)
- `conversation_id` must exist

**Immutability**:
- Messages are append-only (no updates or deletes except cascade)
- Conversation history is immutable once created

---

### 3. Task (Phase 2 - Unchanged)

**Purpose**: User's todo items (managed by Phase 2 backend, accessed via MCP tools).

**Attributes** (for reference only - no changes):
- `id` (UUID, PK)
- `user_id` (TEXT, FK → users.id)
- `title` (VARCHAR(200))
- `description` (TEXT)
- `completed` (BOOLEAN)
- `tags` (TEXT[]) - Array of tags
- `due_date` (DATE, NULLABLE)
- `priority` (VARCHAR(10), NULLABLE)
- `created_at` (TIMESTAMP WITH TIME ZONE)
- `updated_at` (TIMESTAMP WITH TIME ZONE)

**ChatKit Integration**:
- Accessed via MCP tools (add_task, list_tasks, etc.)
- Never accessed directly from phase3-backend
- MCP server calls Phase 2 backend REST API

---

### 4. User (Phase 2 - Unchanged)

**Purpose**: User accounts managed by Better-Auth.

**Attributes** (for reference only - no changes):
- `id` (TEXT, PK): Better-Auth user identifier
- `email` (TEXT, UNIQUE)
- `name` (TEXT)
- `created_at` (TIMESTAMP WITH TIME ZONE)
- Other Better-Auth fields...

**ChatKit Integration**:
- `user_id` extracted from JWT token via existing middleware
- Embedded in ChatKit session metadata for conversation scoping

---

## Database Schema Changes

### Migration Required

**Migration File**: `backend/migrations/006_add_session_id_to_conversations.sql`

```sql
-- Add session_id column to conversations table
ALTER TABLE conversations
ADD COLUMN session_id TEXT;

-- Create unique index for session mapping
CREATE UNIQUE INDEX idx_conversations_session_id
ON conversations(session_id)
WHERE session_id IS NOT NULL;

-- Add comment
COMMENT ON COLUMN conversations.session_id IS
'ChatKit session ID for mapping frontend sessions to database conversations';
```

**Rollback**:
```sql
DROP INDEX IF EXISTS idx_conversations_session_id;
ALTER TABLE conversations DROP COLUMN IF EXISTS session_id;
```

**Data Migration**:
- None required (clean slate approach)
- Existing conversations will be truncated: `TRUNCATE conversations CASCADE;`
- This also clears messages table due to CASCADE

---

## Entity Relationships Diagram

```
┌─────────────┐
│   User      │
│ (Phase 2)   │
│             │
│ - id (PK)   │
│ - email     │
│ - name      │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼────────────┐
│  Conversation     │
│                   │
│ - id (PK)         │
│ - user_id (FK)    │
│ - session_id      │◄─── Maps to ChatKit session
│ - created_at      │
│ - updated_at      │
└──────┬────────────┘
       │
       │ 1:N
       │
┌──────▼────────────┐
│    Message        │
│                   │
│ - id (PK)         │
│ - user_id (FK)    │
│ - conversation_id │
│   (FK)            │
│ - role            │
│ - content         │
│ - created_at      │
└───────────────────┘

Note: User also has 1:N relationship with Task (Phase 2),
but Tasks are accessed via MCP tools, not directly.
```

---

## Data Access Patterns

### 1. Create Conversation

**Trigger**: User sends first message with new ChatKit session ID

**Query**:
```sql
INSERT INTO conversations (user_id, session_id, created_at, updated_at)
VALUES ($1, $2, NOW(), NOW())
RETURNING id;
```

**Authorization**: JWT token provides user_id

---

### 2. Get or Create Conversation by Session

**Trigger**: Every ChatKit message (respond method)

**Query**:
```sql
-- Try to find existing conversation
SELECT id, user_id, created_at, updated_at
FROM conversations
WHERE session_id = $1 AND user_id = $2;

-- If not found, create new
INSERT INTO conversations (user_id, session_id, created_at, updated_at)
VALUES ($2, $1, NOW(), NOW())
ON CONFLICT (session_id) DO UPDATE SET updated_at = NOW()
RETURNING id;
```

**Authorization**: Must match user_id from JWT session

---

### 3. Fetch Conversation History

**Trigger**: Before calling OpenAI (need context)

**Query**:
```sql
SELECT id, role, content, created_at
FROM messages
WHERE conversation_id = $1 AND user_id = $2
ORDER BY created_at ASC
LIMIT 20;
```

**Authorization**: user_id from JWT must match conversation owner

---

### 4. Save Message

**Trigger**: After user sends message, after assistant responds

**Query**:
```sql
INSERT INTO messages (user_id, conversation_id, role, content, created_at)
VALUES ($1, $2, $3, $4, NOW())
RETURNING id;
```

**Authorization**: user_id must match conversation owner

---

### 5. Clear Expired Conversations

**Trigger**: Cron job or manual cleanup (optional)

**Query**:
```sql
-- Delete conversations older than 24 hours
DELETE FROM conversations
WHERE updated_at < NOW() - INTERVAL '24 hours';

-- Messages deleted automatically via CASCADE
```

**Rationale**: Aligns with login session lifecycle (24-hour JWT duration)

---

## Data Isolation Rules

### User Scoping

**Rule**: All queries MUST filter by user_id extracted from JWT token

**Enforcement**:
1. JWT middleware extracts user_id before request handling
2. ChatKit session metadata stores user_id
3. All database queries include WHERE user_id = $1 clause
4. Foreign key constraints prevent cross-user data access

**Examples**:
```python
# CORRECT - User scoped
conversation = await db.fetchrow(
    "SELECT * FROM conversations WHERE id = $1 AND user_id = $2",
    conversation_id, user_id
)

# WRONG - No user scoping (security violation)
conversation = await db.fetchrow(
    "SELECT * FROM conversations WHERE id = $1",
    conversation_id
)
```

---

## Performance Considerations

### Index Usage

| Query Pattern | Index Used | Notes |
|---------------|------------|-------|
| List user conversations | `(user_id, created_at)` | Recent conversations first |
| Fetch conversation history | `(conversation_id, created_at)` | Chronological order |
| Map ChatKit session | `session_id` | Unique lookup |
| List user messages | `(user_id, created_at)` | Cross-conversation search |

### Query Limits

- Conversation history: Limit 20 messages (last 20 only)
- User conversation list: Limit 10 most recent
- Message content: Max 2000 characters (enforced at application layer)

### Connection Pooling

- FastAPI uses async SQLAlchemy with asyncpg
- Connection pool: min=5, max=20 (existing Phase 3 configuration)
- Shared with Phase 2 backend via Neon PostgreSQL

---

## Data Cleanup Strategy

### Session Expiry

**Trigger**: JWT session expires (24 hours)
**Action**: Conversation automatically becomes inaccessible (no deletion needed)
**Rationale**: Next login creates new session_id, new conversation

### Optional Cleanup Job

**Purpose**: Free database space from old conversations
**Frequency**: Daily at 2 AM UTC
**Logic**:
```sql
DELETE FROM conversations
WHERE updated_at < NOW() - INTERVAL '30 days';
```

**Consideration**: Not required for MVP, can defer to post-migration optimization

---

## Summary

| Entity | Changes | Migration Required |
|--------|---------|-------------------|
| User | None | No |
| Task | None | No |
| Conversation | Add session_id column | Yes (006_add_session_id.sql) |
| Message | None | No |

**Total Schema Impact**: Minimal - one new column, one new index
**Data Migration**: None (clean slate approach)
**Backward Compatibility**: Preserved (Phase 2 tables untouched)
