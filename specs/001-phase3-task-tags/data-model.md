# Data Model: Phase 3 Task Tags Integration

**Feature**: 001-phase3-task-tags
**Date**: 2025-12-24
**Purpose**: Define data structures, state models, and contracts for tag integration in Phase 3 components

## 1. Entity Overview

### 1.1 Task (Extended from Phase 2)

**Source**: Phase 2 backend (authoritative, read-only from Phase 3 perspective)

**Attributes**:
- `id` (UUID) - Task identifier
- `user_id` (UUID) - Owner identifier
- `title` (string, 1-200 chars) - Task title
- `description` (string, 0-2000 chars) - Task description
- `due_date` (date, nullable) - Optional deadline
- `priority` (enum: low/medium/high) - Priority level
- `status` (enum: pending/completed) - Completion status
- **`tags`** (string[], 0-10 items) - **TAG FIELD** (Phase 2 already has this)
- `created_at` (timestamp) - Creation time
- `updated_at` (timestamp) - Last modification time

**Tag Field Validation** (enforced by Phase 2 backend):
- Array length: 0-10 items
- Each tag: 1-50 characters
- Format: `^[a-z0-9-]+$` (lowercase alphanumeric + hyphens)
- Automatic normalization: trim whitespace, convert to lowercase
- Automatic deduplication: no duplicate tags within task

**Phase 3 Usage**:
- Frontend: Display tags as badges in ChatMessage component
- MCP Server: Extract tags from NLP, pass to Phase 2 backend
- Phase 3 Backend: No direct manipulation (proxy only)

---

### 1.2 TagCache (Phase 3 Backend Only)

**Purpose**: Temporary in-memory cache for user tag lists

**Attributes**:
- `user_id` (string) - Cache key
- `tags` (string[]) - List of unique tags (alphabetically sorted)
- `expires_at` (timestamp) - Expiration time (60 seconds from fetch)

**Lifecycle**:
- **Creation**: On first `GET /api/tasks/tags` request for user
- **Update**: Overwrite on cache miss or expiration
- **Invalidation**: On task create/update/delete with tags
- **Expiration**: 60 seconds after last fetch

**Cache Behavior**:
```python
class TagCache:
    def __init__(self):
        self._cache: dict[str, dict] = {}

    def get(self, user_id: str) -> list[str] | None:
        entry = self._cache.get(user_id)
        if entry and entry["expires_at"] > now():
            return entry["tags"]
        return None

    def set(self, user_id: str, tags: list[str]):
        self._cache[user_id] = {
            "tags": sorted(tags),  # Always alphabetically sorted
            "expires_at": now() + timedelta(seconds=60)
        }

    def invalidate(self, user_id: str):
        self._cache.pop(user_id, None)
```

**Stateless Consideration**:
- Cache is per-instance (each Phase 3 backend instance has own cache)
- No shared cache (no Redis/Memcached required)
- Cache misses are acceptable (just slower, not broken)
- Horizontal scaling: each instance caches independently

---

### 1.3 TaskContext (MCP Server Session State)

**Purpose**: Track last-referenced task for "this" resolution

**Attributes**:
- `last_task_id` (UUID, nullable) - Most recently mentioned task
- `last_command_type` (enum) - Type of last command executed

**Command Types**:
- `list_tasks` - Show tasks (resets context)
- `filter_tasks` - Show filtered tasks (resets context)
- `create_task` - Add new task (resets context)
- `update_task` - Modify task (preserves context)
- `delete_task` - Remove task (preserves context)
- `complete_task` - Toggle completion (preserves context)

**Context Resolution**:
```python
class TaskContext:
    def __init__(self):
        self.last_task_id: str | None = None
        self.last_command_type: str | None = None

    def update(self, command_type: str, task_id: str | None = None):
        # Reset context on task-related commands
        if command_type in ["list_tasks", "filter_tasks", "create_task"]:
            self.last_task_id = None
        elif task_id:
            self.last_task_id = task_id
        self.last_command_type = command_type

    def resolve_this(self) -> str | None:
        """Get task_id for 'this' references"""
        return self.last_task_id

    def should_ask_clarification(self) -> bool:
        """Check if 'this' reference is ambiguous"""
        return self.last_task_id is None
```

**Managed By**: OpenAI Agents SDK session state (not manually stored)

---

### 1.4 TagExtractionResult (MCP Server Internal)

**Purpose**: Structured output from NLP tag extraction

**Attributes**:
- `tags` (string[]) - Extracted tag names
- `confidence` (float, 0.0-1.0) - Extraction confidence
- `source` (enum: explicit/implicit) - How tags were extracted
- `raw_input` (string) - Original user message

**Source Types**:
- `explicit`: User explicitly mentioned tags ("tagged with work")
- `implicit`: Inferred from context ("show work tasks" → filter by "work")

**Confidence Calculation**:
```python
def calculate_confidence(pattern_match: bool, keyword_count: int) -> float:
    base = 0.5
    if pattern_match:  # Matched "tagged with" or similar
        base = 0.9
    if keyword_count > 0:  # Found tag-related keywords
        base += 0.1 * min(keyword_count, 3)
    return min(base, 1.0)
```

**Validation**:
```python
def validate_tags(tags: list[str]) -> tuple[list[str], list[str]]:
    """Returns (valid_tags, invalid_tags)"""
    valid = []
    invalid = []
    for tag in tags:
        tag = tag.strip().lower()
        if len(tag) < 1 or len(tag) > 50:
            invalid.append(tag)
        elif not re.match(r'^[a-z0-9-]+$', tag):
            invalid.append(tag)
        else:
            valid.append(tag)
    return valid, invalid
```

---

## 2. Data Flow Diagrams

### 2.1 Tag Display Flow (Frontend)

```
Phase 2 Backend
  ↓ (Task object with tags: ["work", "urgent"])
Phase 3 Backend (proxy)
  ↓ (Forwards task object unchanged)
OpenAI Agents SDK
  ↓ (Formats response with task data)
Phase 3 Frontend
  ├─→ ChatMessage component
  │     ├─→ Parse task data from message
  │     └─→ Render TagBadge for each tag
  └─→ Display: [work] [urgent] badges
```

**Frontend Types**:
```typescript
// lib/types.ts
interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  priority: "low" | "medium" | "high";
  status: "pending" | "completed";
  tags: string[];  // NEW: Tag array
  created_at: string;
  updated_at: string;
}

interface ChatMessageData {
  role: "user" | "assistant" | "system";
  content: string;
  tasks?: Task[];  // Structured task data in message
}
```

---

### 2.2 Tag Filtering Flow (NLP → MCP → Phase 2)

```
User Input: "show me work tasks"
  ↓
Phase 3 Frontend
  ↓ POST /api/{user_id}/chat
Phase 3 Backend
  ↓ Call OpenAI Agents SDK
OpenAI Agents SDK
  ├─→ Intent: list_tasks
  ├─→ Confidence: 0.92 (high)
  └─→ Request MCP tool: list_tasks
        ↓
Phase 3 MCP Server
  ├─→ Extract tag: "work" (from "work tasks")
  ├─→ Validate format: ✅ valid
  └─→ HTTP GET to Phase 2 Backend
        ↓ GET /api/tasks?tags=work
Phase 2 Backend
  ├─→ Filter tasks WHERE tags @> ARRAY['work']
  └─→ Return: [{task1}, {task2}, ...]
        ↓
MCP Server
  └─→ Return tool result to Agent SDK
        ↓
Agent SDK
  └─→ Format response: "Here are your work tasks: ..."
        ↓
Frontend
  └─→ Display tasks with [work] badge
```

**MCP Tool Schema** (see contracts/mcp-tag-tools.yaml for full spec):
```python
# list_tasks tool with tags parameter
{
    "name": "list_tasks",
    "description": "List user's tasks with optional tag filtering",
    "parameters": {
        "user_id": {"type": "string", "required": True},
        "tags": {"type": "array", "items": {"type": "string"}, "required": False}
    }
}
```

---

### 2.3 Tag List Caching Flow (Phase 3 Backend)

```
User Input: "what tags do I have?"
  ↓
MCP Server
  └─→ Call list_tags tool
        ↓
Phase 3 Backend
  ├─→ Check cache for user_id
  │     ├─→ HIT: Return cached tags (50-100ms)
  │     └─→ MISS: Proceed to Phase 2
  ├─→ HTTP GET to Phase 2 Backend
  │     ↓ GET /api/tasks/tags
  │     ↓ Phase 2 returns: ["home", "urgent", "work"]
  ├─→ Cache tags (60s TTL)
  └─→ Return to MCP Server
        ↓
Agent SDK
  └─→ Format response: "You have 3 tags: home, urgent, work"
```

**Cache Invalidation**:
```
User adds tag: "add task tagged with personal"
  ↓
MCP Server: add_task tool
  ├─→ HTTP POST /api/tasks (tags: ["personal"])
  ├─→ Phase 2 creates task with new tag
  └─→ Phase 3 Backend detects tag in request
        ↓
Phase 3 Backend
  └─→ Invalidate cache for user_id
        (Next "what tags?" query will fetch fresh list)
```

---

## 3. State Transitions

### 3.1 Task Context Lifecycle

```
[No Context]
  ↓ User: "show my tasks"
  ↓ list_tasks command
[Context Reset: last_task_id = None]
  ↓ User views task list
  ↓ User: "tag the first one with urgent"
  ↓ Agent identifies task #1
[Context Set: last_task_id = task_1_uuid]
  ↓ User: "remove the urgent tag"
  ↓ update_task using last_task_id
[Context Preserved: last_task_id = task_1_uuid]
  ↓ User: "show all tasks"
  ↓ list_tasks command
[Context Reset: last_task_id = None]
```

**Trigger Summary**:
- Set context: update_task, delete_task, complete_task (when task_id known)
- Reset context: list_tasks, filter_tasks, create_task
- Clarify context: "this" reference when last_task_id = None

---

### 3.2 Cache Lifecycle

```
[Empty Cache]
  ↓ GET /api/tasks/tags (user_A)
  ↓ Fetch from Phase 2: ["work", "home"]
[Cached: user_A → ["work", "home"], expires: T+60s]
  ↓ Wait 30s
  ↓ GET /api/tasks/tags (user_A)
[Cache Hit: Return ["work", "home"] (<10ms)]
  ↓ POST /api/tasks (user_A, tags: ["urgent"])
[Cache Invalidated: user_A removed]
  ↓ GET /api/tasks/tags (user_A)
  ↓ Cache Miss → Fetch from Phase 2
[Cached: user_A → ["home", "urgent", "work"], expires: T+60s]
```

---

## 4. Validation Rules

### 4.1 Tag Format Validation (Client-Side MCP Server)

| Rule | Constraint | Action |
|------|-----------|--------|
| Length | 1-50 characters | Reject if <1 or >50 |
| Format | `^[a-z0-9-]+$` | Reject if invalid chars |
| Case | Lowercase only | Auto-convert to lowercase |
| Whitespace | Trimmed | Auto-trim leading/trailing |
| Count | Max 10 tags per task | Reject if >10 |

**Validation Flow**:
```python
def validate_tag(tag: str) -> tuple[bool, str]:
    tag = tag.strip().lower()
    if len(tag) < 1:
        return False, "Tag cannot be empty"
    if len(tag) > 50:
        return False, "Tag must be 1-50 characters"
    if not re.match(r'^[a-z0-9-]+$', tag):
        return False, "Tags can only contain lowercase letters, numbers, and hyphens"
    return True, tag
```

**Note**: Final validation enforced by Phase 2 backend (MCP server pre-validates to avoid round-trip)

---

## 5. API Contracts

See [contracts/mcp-tag-tools.yaml](./contracts/mcp-tag-tools.yaml) for full MCP tool schemas.

**Summary**:
- `list_tasks(user_id, tags?)` - Filter tasks by tags (AND logic)
- `add_task(user_id, title, tags?)` - Create task with tags
- `update_task(user_id, task_id, tags?)` - Update task tags
- `list_tags(user_id)` - Get user's unique tags
- `add_tag_to_task(user_id, task_id, tag)` - Add single tag (optional enhancement)
- `remove_tag_from_task(user_id, task_id, tag)` - Remove single tag (optional enhancement)

---

## 6. Data Model Summary

| Entity | Owner | Lifecycle | Persistence |
|--------|-------|-----------|-------------|
| Task (with tags) | Phase 2 Backend | Authoritative | PostgreSQL (tasks table) |
| TagCache | Phase 3 Backend | Ephemeral (60s TTL) | In-memory (per-instance) |
| TaskContext | OpenAI Agents SDK | Session-scoped | Agent session state |
| TagExtractionResult | MCP Server | Request-scoped | Transient (not persisted) |

**Key Design Principles**:
- Phase 2 backend is single source of truth for tags
- Phase 3 components never directly modify database
- All tag operations go through Phase 2 REST APIs
- Caching is optimization, not requirement (system works without it)
- Context is managed by Agent SDK, not manually stored

**Data Model Complete**: Ready for contract generation (contracts/).
