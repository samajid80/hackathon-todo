# Research: Task Tags/Categories Implementation

**Feature**: 003-task-tags
**Date**: 2025-12-23
**Purpose**: Document technical decisions and research findings for task tags implementation

## 1. Tag Storage Strategy

### Decision
Store tags as **PostgreSQL TEXT[] array** in the `tasks` table.

### Rationale
1. **Simplicity**: Single column, no JOINs required for tag queries
2. **Performance**: GIN indexes on arrays provide fast containment queries
3. **Scale**: Appropriate for moderate tag counts (<100 unique tags per user)
4. **PostgreSQL native**: TEXT[] is a first-class type with excellent operator support
5. **Alignment with spec**: User explicitly specified TEXT[] array storage

### Alternatives Considered

**Option A: Junction Table (many-to-many)**
```sql
CREATE TABLE task_tags (
  task_id UUID REFERENCES tasks(id),
  tag_name VARCHAR(50),
  PRIMARY KEY (task_id, tag_name)
);
```
- ❌ More complex queries (requires JOINs)
- ❌ Additional table to maintain
- ❌ Higher query latency for tag filtering
- ✅ Better for very large tag counts (>1000 unique tags)
- ✅ Easier to add tag metadata (e.g., color, description)

**Rejected because**: Adds unnecessary complexity for expected scale (10-50 tags per user). Array approach is simpler and sufficient.

**Option B: JSONB Column**
```sql
tags JSONB DEFAULT '[]'::jsonb
```
- ✅ Flexible schema (can add tag metadata later)
- ❌ Slower containment queries than TEXT[]
- ❌ More complex validation logic
- ❌ Less intuitive for simple tag lists

**Rejected because**: TEXT[] has better performance for containment queries and simpler validation.

### Migration Path
If tag count grows beyond expectations (>100 unique tags), migrate to junction table:
1. Create `task_tags` table
2. Populate from existing `tasks.tags` array
3. Add foreign key constraint
4. Update application code
5. Drop `tasks.tags` column

## 2. Tag Indexing Strategy

### Decision
Use **GIN (Generalized Inverted Index)** on the `tags` column.

### Rationale
1. **Optimized for arrays**: GIN indexes excel at containment queries (`@>`, `&&` operators)
2. **Fast filtering**: Enables efficient `WHERE tags @> ARRAY['work']` queries
3. **PostgreSQL recommendation**: Official documentation recommends GIN for array indexing
4. **Query patterns**: Tag filtering is a primary use case (P2 user story)

### Index Command
```sql
CREATE INDEX idx_tasks_tags ON tasks USING GIN (tags);
```

### Query Performance
- **Containment check** (`WHERE tags @> ARRAY['work']`): O(log n) with GIN index
- **Overlap check** (`WHERE tags && ARRAY['work', 'urgent']`): O(log n) with GIN index
- **Without index**: O(n) sequential scan

### Alternatives Considered

**Option A: B-Tree Index**
```sql
CREATE INDEX idx_tasks_tags ON tasks (tags);
```
- ❌ Not optimized for array containment queries
- ❌ Slower for `@>` and `&&` operators
- ✅ Faster for exact array equality (`=`)

**Rejected because**: Containment queries are the primary use case, not equality checks.

**Option B: No Index**
- ❌ Slow queries for users with many tasks (>100)
- ❌ Sequential scans on every tag filter
- ✅ No index maintenance overhead

**Rejected because**: Tag filtering is a P2 user story; performance is critical.

## 3. Tag Validation Approach

### Decision
Implement validation in **Pydantic field validators** (backend) with regex pattern matching.

### Rationale
1. **Single point of validation**: Centralized in `TaskBase` model
2. **Automatic enforcement**: Pydantic validates on deserialization
3. **Clear error messages**: ValidationError automatically returns 422 with details
4. **Reusable**: Same validator for create and update operations

### Validation Rules
```python
@field_validator("tags")
@classmethod
def validate_tags(cls, v: list[str]) -> list[str]:
    # Max 10 tags per task
    if len(v) > 10:
        raise ValueError("Maximum 10 tags allowed per task")

    # Normalize and validate each tag
    validated_tags = []
    for tag in v:
        tag = tag.strip().lower()  # Trim and lowercase

        # Length check
        if len(tag) < 1 or len(tag) > 50:
            raise ValueError(f"Tag must be 1-50 characters, got: {tag}")

        # Format check (alphanumeric + hyphens only)
        if not re.match(r'^[a-z0-9-]+$', tag):
            raise ValueError(f"Tag must contain only lowercase letters, numbers, and hyphens: {tag}")

        validated_tags.append(tag)

    # Deduplicate
    return list(dict.fromkeys(validated_tags))
```

### Alternatives Considered

**Option A: Database CHECK Constraint**
```sql
ALTER TABLE tasks ADD CONSTRAINT check_tags
CHECK (array_length(tags, 1) <= 10);
```
- ✅ Enforced at database level
- ❌ Limited validation capabilities (no regex in CHECK)
- ❌ Poor error messages ("constraint violation")
- ❌ Cannot normalize (trim, lowercase) automatically

**Rejected because**: Pydantic provides better UX with clear error messages and automatic normalization.

**Option B: Frontend-Only Validation**
- ❌ Not secure (can be bypassed)
- ❌ No protection for API clients (Phase3 chatbot)
- ✅ Better UX (instant feedback)

**Rejected because**: Backend validation is mandatory for security; frontend validation is additive.

## 4. Tag Autocomplete Implementation

### Decision
Use **GET /api/tasks/tags** endpoint with client-side filtering and debouncing.

### Rationale
1. **Simple API**: Returns all user tags, sorted alphabetically
2. **Client-side filtering**: Reduces server load, instant results
3. **Debouncing**: Prevents excessive API calls (300ms threshold)
4. **Cache-friendly**: Tag list changes infrequently, can cache in React state

### API Endpoint
```python
@router.get("/tasks/tags", response_model=list[str])
async def list_tags(current_user: CurrentUserDep, session: Session):
    """Get all unique tags used by the authenticated user."""
    query = text("""
        SELECT DISTINCT unnest(tags) as tag
        FROM tasks
        WHERE user_id = :user_id
        ORDER BY tag
    """)
    result = session.exec(query, {"user_id": current_user.user_id})
    return [row[0] for row in result]
```

### Frontend Implementation
```typescript
const [allTags, setAllTags] = useState<string[]>([]);
const [filteredTags, setFilteredTags] = useState<string[]>([]);

// Load all tags on mount
useEffect(() => {
  getUserTags().then(setAllTags);
}, []);

// Filter tags based on input (debounced)
const debouncedFilter = useMemo(
  () => debounce((input: string) => {
    if (!input) {
      setFilteredTags([]);
      return;
    }
    const filtered = allTags.filter(tag =>
      tag.includes(input.toLowerCase()) && !selectedTags.includes(tag)
    );
    setFilteredTags(filtered);
  }, 300),
  [allTags, selectedTags]
);
```

### Alternatives Considered

**Option A: Server-Side Filtering**
```python
@router.get("/tasks/tags", response_model=list[str])
async def list_tags(current_user, session, q: str | None = None):
    # Filter tags matching query
```
- ❌ More server load (one request per keystroke)
- ❌ Higher latency (network round-trip)
- ✅ Works for very large tag lists (>1000 tags)

**Rejected because**: Expected tag count is small (10-50 per user); client-side filtering is faster.

**Option B: Fuzzy Search (Levenshtein Distance)**
- ✅ Better typo tolerance
- ❌ More complex implementation
- ❌ Unnecessary for short tag names

**Rejected because**: Simple substring matching is sufficient for short tags.

## 5. Tag Filtering Query Strategy

### Decision
Use **PostgreSQL array containment operator** (`@>`) with AND logic for multiple tags.

### Rationale
1. **Array native**: `@>` operator is optimized for GIN indexes
2. **AND semantics**: Matches spec requirement ("task must have ALL specified tags")
3. **Composable**: Easy to combine with other filters (status, due_date)
4. **Performant**: O(log n) with GIN index

### Query Implementation
```python
def get_user_tasks(session, user_id, tags: list[str] | None = None):
    statement = select(Task).where(Task.user_id == user_id)

    # Apply tag filter (AND logic)
    if tags:
        for tag in tags:
            statement = statement.where(Task.tags.contains([tag]))

    return session.exec(statement).all()
```

### SQL Output
```sql
-- Single tag
SELECT * FROM tasks WHERE user_id = 'abc' AND tags @> ARRAY['work'];

-- Multiple tags (AND logic)
SELECT * FROM tasks WHERE user_id = 'abc'
  AND tags @> ARRAY['work']
  AND tags @> ARRAY['urgent'];
```

### Alternatives Considered

**Option A: OR Logic**
```sql
WHERE user_id = 'abc' AND tags && ARRAY['work', 'urgent']
```
- ❌ Doesn't match spec (spec requires AND logic)
- ✅ Simpler query (single operator)

**Rejected because**: Spec explicitly requires "task must have ALL specified tags".

**Option B: Exact Array Match**
```sql
WHERE user_id = 'abc' AND tags = ARRAY['work', 'urgent']
```
- ❌ Requires exact match (no additional tags allowed)
- ❌ Order-dependent

**Rejected because**: Too restrictive; users want "contains all" not "equals exactly".

## 6. Phase3 Chatbot Integration

### Decision
**No changes to Phase2 backend**; chatbot uses existing REST API.

### Rationale
1. **Separation of concerns**: Phase2 provides stable API, Phase3 consumes it
2. **Zero coupling**: Phase3 can be deployed/disabled independently
3. **Natural language parsing**: Handled in Phase3 backend, not Phase2
4. **Future-proof**: Phase2 API remains stable for other clients

### Phase3 Implementation Approach
```python
# Phase3 MCP tool: add_task
@mcp.tool()
async def add_task(title: str, tags: list[str] | None = None):
    """Create a task with optional tags."""
    response = requests.post(
        f"{PHASE2_API_URL}/api/tasks",
        json={"title": title, "tags": tags or []},
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    return response.json()
```

### Natural Language Parsing
```python
# Phase3 chatbot: parse user message
user_message = "add a task to buy groceries tagged with home"

# Extract tags from message
tags = extract_tags(user_message)  # ["home"]

# Call Phase2 API via MCP tool
await add_task(title="buy groceries", tags=tags)
```

### Alternatives Considered

**Option A: Extend Phase2 with NLP Endpoint**
```python
@router.post("/tasks/from-natural-language")
async def create_task_from_nl(message: str):
    # Parse message, extract title and tags
```
- ❌ Adds AI dependencies to Phase2
- ❌ Violates separation of concerns
- ❌ Makes Phase2 harder to maintain

**Rejected because**: Natural language processing belongs in Phase3, not Phase2.

## 7. Summary of Key Decisions

| Decision Point | Chosen Approach | Primary Rationale |
|----------------|-----------------|-------------------|
| **Storage** | PostgreSQL TEXT[] array | Simplicity, performance for moderate scale |
| **Indexing** | GIN index | Optimized for containment queries |
| **Validation** | Pydantic field validators | Centralized, clear error messages |
| **Autocomplete** | Client-side filtering | Low latency, low server load |
| **Filtering** | Array `@>` operator (AND logic) | Matches spec, performant |
| **Phase3 Integration** | No Phase2 changes | Separation of concerns, stability |

## 8. Risk Assessment

| Risk | Mitigation |
|------|-----------|
| **Tag count exceeds 100 per user** | Monitor usage; migrate to junction table if needed |
| **GIN index maintenance overhead** | Acceptable for read-heavy workload; tags change infrequently |
| **Tag autocomplete degrades with 1000+ tags** | Implement server-side filtering if needed (rare) |
| **Users create conflicting tags** (e.g., "work" vs "Work") | Validation normalizes to lowercase automatically |

## 9. Performance Targets

Based on success criteria from spec:

| Metric | Target | How Achieved |
|--------|--------|--------------|
| **Tag addition** | <10 seconds | Simple form input, <100ms API |
| **Autocomplete** | <300ms | Client-side filtering (instant) |
| **Tag filtering** | <1 second | GIN index on tags column |
| **Tag list retrieval** | <500ms | Simple UNNEST query with ORDER BY |

## 10. Testing Strategy

### Unit Tests
- Tag validation (max 10, length, format, deduplication)
- Lowercase normalization
- Whitespace trimming

### Integration Tests
- GET /api/tasks/tags returns sorted unique tags
- GET /api/tasks?tags=work filters correctly
- GET /api/tasks?tags=work&tags=urgent applies AND logic
- Tag filtering combines with status/sorting filters

### E2E Tests
- Create task with tags via UI
- Autocomplete shows matching tags
- Filter tasks by tags
- Remove tags from task

## 11. Documentation Requirements

### API Documentation
Update OpenAPI schema:
```yaml
components:
  schemas:
    Task:
      properties:
        tags:
          type: array
          items:
            type: string
            pattern: '^[a-z0-9-]{1,50}$'
          maxItems: 10
          description: Task category labels
```

### User Documentation
- How to add tags to tasks
- How to filter by tags
- Tag naming guidelines (lowercase, alphanumeric + hyphens)
- Tag limit (10 per task)

## 12. References

- PostgreSQL Array Documentation: https://www.postgresql.org/docs/current/arrays.html
- PostgreSQL GIN Indexes: https://www.postgresql.org/docs/current/gin-intro.html
- Pydantic Validators: https://docs.pydantic.dev/latest/concepts/validators/
- FastAPI Request Validation: https://fastapi.tiangolo.com/tutorial/body/
