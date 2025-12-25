# Research: Phase 3 Task Tags Integration

**Feature**: 001-phase3-task-tags
**Date**: 2025-12-24
**Purpose**: Research NLP patterns, caching strategies, and integration approaches for tag functionality in Phase 3 chatbot

## 1. NLP Tag Extraction Patterns

### Decision: Pattern matching + context-aware extraction

**Rationale**:
- OpenAI Agents SDK handles intent recognition (confidence scoring built-in)
- Pattern matching for explicit tag syntax ("tagged with X", "tags: X, Y")
- Context extraction for implicit mentions ("work tasks" → filter by "work" tag)
- Confidence threshold integration (clarify when <70%)

**Patterns to Support**:
```python
# Explicit tag addition
"add task buy milk tagged with home"
"create task tagged with work and urgent"
"tag this with important"

# Explicit tag filtering
"show me tasks tagged with work"
"list my urgent tasks"
"show work tasks"

# Explicit tag listing
"what tags do I have?"
"list my tags"
"show all my tags"

# Explicit tag removal
"remove the urgent tag from this task"
"untag this from work"
"remove all tags"
```

**Extraction Strategy**:
1. Agent SDK identifies intent (add_task, list_tasks, update_task)
2. Extract tags from common patterns:
   - `"tagged with"` → capture following words until stop word
   - `"tag(s): X, Y, Z"` → split on commas
   - `"{tag} tasks"` → infer tag filter from adjective
3. Normalize: lowercase, trim whitespace, validate format
4. Confidence check: If <70%, ask clarifying question

**Alternatives Considered**:
- LLM-based extraction (e.g., GPT-4 for each command): Too slow, unnecessary cost
- Regex-only extraction: Too rigid, misses contextual variations
- **Rejected because**: Pattern matching + Agent SDK confidence strikes optimal balance

---

## 2. Caching Strategy for Tag Lists

### Decision: In-memory TTL cache with smart invalidation

**Rationale**:
- Tag lists change infrequently (only on tag operations)
- 60-second TTL balances freshness with performance
- Per-user keying prevents cross-user contamination
- Smart invalidation on create/update/delete operations

**Cache Implementation**:
```python
# Simple dict-based cache in Phase 3 backend
cache = {
    "user_id": {
        "tags": ["work", "home", "urgent"],
        "expires_at": timestamp + 60
    }
}

# Cache operations:
def get_cached_tags(user_id: str) -> list[str] | None:
    entry = cache.get(user_id)
    if entry and entry["expires_at"] > now():
        return entry["tags"]
    return None

def set_cached_tags(user_id: str, tags: list[str]):
    cache[user_id] = {
        "tags": tags,
        "expires_at": now() + 60
    }

def invalidate_cache(user_id: str):
    cache.pop(user_id, None)
```

**Invalidation Triggers**:
- POST /api/tasks (if tags field present) → invalidate
- PUT /api/tasks/{id} (if tags field present) → invalidate
- DELETE /api/tasks/{id} → invalidate (task may have had tags)
- Cache miss → fetch from Phase 2 backend, cache result

**Performance Impact**:
- Cache hit: <10ms (in-memory lookup)
- Cache miss: ~200-500ms (HTTP call to Phase 2 backend)
- Expected hit rate: ~80% (tag lists rarely change)

**Alternatives Considered**:
- Redis cache: Adds infrastructure complexity, overkill for 60s TTL
- No caching: Poor UX for "what tags do I have?" queries
- Longer TTL (5+ minutes): Stale data when user adds new tag
- **Rejected because**: Simple in-memory cache is stateless-compatible (per-instance cache is acceptable)

---

## 3. Task Context Retention

### Decision: Session-based context managed by OpenAI Agents SDK

**Rationale**:
- OpenAI Agents SDK maintains conversation context automatically
- "this" references stored in agent session state
- Reset context on task-related commands (show, list, create, filter)
- No manual state management required in MCP server

**Context Management**:
```python
# Pseudocode for context retention
class TaskContext:
    last_task_id: str | None = None
    last_command_type: str | None = None

    def update(self, command_type: str, task_id: str | None):
        # Reset context if task-related command
        if command_type in ["list_tasks", "create_task", "filter_tasks"]:
            self.last_task_id = None
        else:
            self.last_task_id = task_id
        self.last_command_type = command_type

    def resolve_this(self) -> str | None:
        return self.last_task_id
```

**Context Reset Triggers**:
- `"show my tasks"` → list_tasks → reset context
- `"create task X"` → create_task → reset context
- `"show work tasks"` → filter_tasks → reset context
- `"tag this"` → NO reset, uses last_task_id

**Alternatives Considered**:
- Manual context in MCP server: Violates stateless architecture
- Expire context after 5 minutes: Too aggressive, breaks chained operations
- Never expire context: Risk of stale references (user forgot what "this" means)
- **Rejected because**: SDK-managed context with command-based reset is simplest and most reliable

---

## 4. Retry and Error Handling

### Decision: Exponential backoff with single retry

**Rationale**:
- Most failures are transient (network glitches, temporary backend unavailability)
- Single retry after 2 seconds catches ~95% of transient failures
- User sees loading indicator, minimal perceived latency
- Graceful degradation with user-friendly error messages

**Retry Strategy**:
```python
async def call_with_retry(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except httpx.RequestError as e:
        # Wait 2 seconds, retry once
        await asyncio.sleep(2)
        try:
            return await func(*args, **kwargs)
        except Exception as retry_error:
            # Log error, return friendly message
            logger.error(f"Retry failed: {retry_error}")
            raise UserFacingError("Unable to complete operation. Please try again.")
```

**Error Handling Patterns**:
- Network timeout: Retry after 2s, show "Loading..." indicator
- 400 Bad Request (validation error): NO retry, show validation message from Phase 2
- 401 Unauthorized: NO retry, redirect to login
- 500 Server Error: Retry after 2s, fallback to generic error
- Retry failure: Show "Unable to load. Try again" with manual retry button

**Alternatives Considered**:
- No retries: Poor UX for transient failures
- Multiple retries (3x with backoff): Excessive latency for user
- Infinite retries: Risk of hanging operations
- **Rejected because**: Single 2-second retry balances reliability and responsiveness

---

## 5. Logging and Observability

### Decision: Selective logging (errors + low-confidence cases)

**Rationale**:
- Log volume reduction (avoid logging every successful tag operation)
- Critical insights: errors (for debugging) + low-confidence (for NLP model improvement)
- Supports 85% accuracy target (can analyze logged low-confidence cases)
- Minimal performance overhead

**Logging Strategy**:
```python
# MCP Server logging
if confidence < 0.70:
    logger.info(
        "Low confidence tag extraction",
        extra={
            "user_input": message,
            "extracted_tags": tags,
            "confidence": confidence,
            "user_id": user_id
        }
    )

# Phase 3 Backend logging
try:
    tags = await fetch_tags_from_phase2(user_id)
except Exception as e:
    logger.error(
        "Failed to fetch tags from Phase 2",
        extra={
            "user_id": user_id,
            "error": str(e),
            "phase2_endpoint": PHASE2_BACKEND_URL
        }
    )
```

**Metrics to Track**:
- Tag extraction confidence distribution (histogram)
- Clarification rate (should be <15% per SC-011)
- Cache hit rate (should be ~80%)
- Proxy error rate (should be <1%)

**Alternatives Considered**:
- Log everything: Log bloat, performance overhead, expensive in production
- Log nothing: No visibility into NLP accuracy or errors
- Log only errors: Misses low-confidence cases (can't improve NLP)
- **Rejected because**: Selective logging provides essential observability without overhead

---

## 6. Frontend Tag Display

### Decision: Tailwind CSS pill badges with truncation

**Rationale**:
- Tailwind CSS already used in Phase 3 frontend
- Pill badges are industry-standard pattern (GitHub, Jira, Trello)
- Truncation with "...+N more" handles tasks with many tags
- Maintains consistent chat interface aesthetics

**Tag Badge Component**:
```tsx
// components/TagBadge.tsx
interface TagBadgeProps {
  tag: string;
  size?: "sm" | "md";
}

export function TagBadge({ tag, size = "sm" }: TagBadgeProps) {
  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-sm"
  };

  return (
    <span className={`
      inline-flex items-center rounded-full
      bg-blue-100 text-blue-800
      font-medium ${sizeClasses[size]}
    `}>
      {tag}
    </span>
  );
}
```

**Tag Display Logic**:
- Show first 5 tags as badges
- If more than 5 tags: "...+N more" text
- Clicking "...+N more" expands to show all (optional enhancement)
- Empty tags array: no tag section (cleaner UI)

**Alternatives Considered**:
- Custom SVG icons: Unnecessary complexity
- Colored tags based on name: Adds color decision logic, inconsistent UX
- Scrollable tag list: Poor mobile UX
- **Rejected because**: Simple pill badges with truncation is proven pattern

---

## Summary Table

| Topic | Decision | Key Benefit | Trade-off |
|-------|----------|-------------|-----------|
| NLP Extraction | Pattern matching + Agent SDK | Optimal accuracy/speed balance | Some edge cases may need clarification |
| Caching | 60s TTL in-memory cache | 80% hit rate, <100ms response | Stale data up to 60s (acceptable) |
| Context | SDK-managed with reset triggers | Stateless, reliable | "this" expires on task commands |
| Retry | Single retry after 2s | 95% transient failure recovery | 2s perceived latency on failures |
| Logging | Errors + confidence <70% | Essential visibility, low overhead | Can't audit all successful operations |
| Frontend | Tailwind pill badges | Consistent, proven pattern | Limited customization |

**Research Complete**: All technical unknowns resolved, ready for design phase.
