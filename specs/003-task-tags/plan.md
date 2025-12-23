# Implementation Plan: Task Tags/Categories

**Branch**: `003-task-tags` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-task-tags/spec.md`

## Summary

Add tags/categories feature to allow users to categorize tasks with labels (e.g., "work", "home", "urgent"). Users can filter tasks by one or more tags using AND logic. Tags are stored as PostgreSQL TEXT[] arrays with validation enforcing max 10 tags per task, 1-50 characters each, lowercase alphanumeric + hyphens only. Implementation includes tag autocomplete, tag filtering in both Phase2 (web UI) and Phase3 (chatbot), and a GET /api/tasks/tags endpoint for retrieving unique user tags.

**Technical Approach**: Extend existing Task model with TEXT[] array column, add GIN index for fast containment queries, implement Pydantic validators for tag normalization and validation, create frontend TagSelector component with autocomplete, and enable Phase3 chatbot integration through existing REST API.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI (backend), SQLModel (ORM), PostgreSQL (Neon), Next.js 16 (frontend), Better-Auth (authentication)
**Storage**: PostgreSQL with TEXT[] array column for tags, GIN index for containment queries
**Testing**: pytest (backend), Jest/React Testing Library (frontend), Playwright (E2E)
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Web (frontend + backend)
**Performance Goals**: Tag autocomplete <300ms, tag filtering <1s with 1000+ tasks, tag list endpoint <500ms
**Constraints**: Max 10 tags per task, 1-50 chars each, lowercase alphanumeric + hyphens only, user isolation
**Scale/Scope**: Expected 10-50 unique tags per user, 100+ tags total, 1000+ tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Technology Stack Compliance (Section 6.1)
- **FastAPI (Python 3.13)**: ✅ Backend uses FastAPI
- **PostgreSQL (Neon)**: ✅ Database uses PostgreSQL on Neon
- **Next.js 16 App Router**: ✅ Frontend uses Next.js 16
- **Better-Auth**: ✅ Authentication via Better-Auth
- **JWT**: ✅ Backend validates JWT tokens

### ✅ Full-Stack Separation (Section 5.1)
- **Backend**: Changes to `/backend/` (models, routes, services, migrations)
- **Frontend**: Changes to `/frontend/` (components, types, API client)
- **Database**: Changes to PostgreSQL schema (new column + index)
- **Separation maintained**: ✅ No logic crossover

### ✅ Single Source of Truth (Section 5.2)
- **PostgreSQL is sole data store**: ✅ Tags stored in `tasks.tags` column
- **No duplication**: ✅ Tags computed from tasks, not stored separately
- **Better-Auth handles users**: ✅ No changes to user storage

### ✅ Stateless Backend (Section 5.3)
- **JWT for identity**: ✅ No session state stored
- **Horizontally scalable**: ✅ Tag queries use database indexes, no in-memory caching required

### ✅ Layered Backend Architecture (Section 5.4)
- **Routes**: `backend/routes/tasks.py` - New GET /api/tasks/tags endpoint, update existing endpoints
- **Models**: `backend/models/task.py` - Add tags field with Pydantic validators
- **Services**: `backend/services/task_service.py` - Tag filtering logic, tag list query
- **DB**: `backend/db.py` - No changes (existing session management)
- **Migrations**: `backend/migrations/005_add_tags_to_tasks.sql` - New migration

### ✅ Forward Compatibility (Section 5.6)
- **Phase 3 MCP tools**: ✅ Can call existing REST API with tags parameter
- **Phase 3 Chatbot**: ✅ Natural language parsing in Phase3, calls Phase2 API
- **API stability**: ✅ No breaking changes to existing endpoints
- **Modular backend**: ✅ Tag logic isolated in service layer

### ✅ Security Constraints (Section 6.2)
- **JWT validation**: ✅ All endpoints require authentication
- **User isolation**: ✅ Tags scoped per user (inherited from `task.user_id`)
- **No data leakage**: ✅ GET /api/tasks/tags filtered by authenticated user

### ✅ Performance Constraints (Section 6.3)
- **Indexed queries**: ✅ GIN index on `tags` column for fast containment queries
- **1000+ tasks**: ✅ GIN index provides O(log n) performance

### ✅ Testing Requirements (Section 7.2)
- **Backend tests**: Unit tests for validators, integration tests for endpoints
- **Frontend tests**: Component tests for TagSelector, E2E tests for tag workflows
- **Integration tests**: End-to-end tag creation, filtering, autocomplete

### ✅ User Experience Requirements (Section 7.3)
- **Clean UI**: TagSelector component with autocomplete, tag chips/badges
- **Responsive**: Works on desktop and mobile
- **Error messages**: Clear validation errors for invalid tags

### **Gate Result**: ✅ ALL CHECKS PASSED - No violations

## Project Structure

### Documentation (this feature)

```text
specs/003-task-tags/
├── spec.md                  # Feature specification (WHAT/WHY)
├── plan.md                  # This file (HOW - implementation plan)
├── research.md              # Phase 0 - Technical decisions and research
├── data-model.md            # Phase 1 - Entity definitions and database schema
├── quickstart.md            # Phase 1 - Manual test scenarios
├── contracts/               # Phase 1 - API contracts
│   └── openapi-tags.yaml    # OpenAPI spec for tag endpoints
├── checklists/              # Quality validation
│   └── requirements.md      # Specification quality checklist
└── tasks.md                 # Phase 2 - NOT created yet (run /sp.tasks)
```

### Source Code (repository root)

```text
# Backend (Phase2)
backend/
├── models/
│   ├── task.py              # MODIFY: Add tags field with validators
│   └── enums.py             # No changes
├── routes/
│   └── tasks.py             # MODIFY: Add GET /tags endpoint, update list endpoint
├── services/
│   └── task_service.py      # MODIFY: Add tag filtering, tag list query
├── db.py                    # No changes
└── migrations/
    └── 005_add_tags_to_tasks.sql  # NEW: Add tags column + GIN index

# Frontend (Phase2)
frontend/
├── app/
│   └── tasks/               # MODIFY: Update task pages to support tags
├── components/
│   ├── TagSelector.tsx      # NEW: Tag input with autocomplete
│   ├── TaskCard.tsx         # MODIFY: Display tags
│   ├── TaskForm.tsx         # MODIFY: Include TagSelector
│   └── TaskFilters.tsx      # MODIFY: Add tag filtering
├── lib/
│   └── api/
│       └── tasks.ts         # MODIFY: Add getUserTags(), update getTasks()
├── types/
│   └── task.ts              # MODIFY: Add tags: string[] to Task interface
└── hooks/
    └── useTags.ts           # NEW: Hook for tag autocomplete

# Phase3 (Chatbot) - NO CHANGES
# Phase3 uses Phase2 REST API - no code changes needed
```

**Structure Decision**: Web application (Option 2) - Backend and frontend are separate services. Backend handles data and business logic, frontend provides UI. Phase3 chatbot consumes Phase2 backend API via HTTP.

## Complexity Tracking

> **No violations to justify** - All constitution principles followed.

## Phase 0: Research (Completed)

**Status**: ✅ Complete

**Artifact**: [research.md](./research.md)

**Key Decisions**:
1. **Tag Storage**: PostgreSQL TEXT[] array (vs. junction table or JSONB)
2. **Indexing**: GIN index for containment queries
3. **Validation**: Pydantic field validators with regex
4. **Autocomplete**: Client-side filtering with debouncing
5. **Filtering**: Array `@>` operator with AND logic
6. **Phase3 Integration**: No Phase2 changes, chatbot calls REST API

## Phase 1: Design & Contracts (Completed)

**Status**: ✅ Complete

**Artifacts**:
- ✅ [data-model.md](./data-model.md) - Entity definitions, database schema, validation rules
- ✅ [contracts/openapi-tags.yaml](./contracts/openapi-tags.yaml) - API contract for tag endpoints
- ✅ [quickstart.md](./quickstart.md) - Manual test scenarios and acceptance criteria

**Data Model Summary**:
- **Task entity enhanced** with `tags TEXT[] NOT NULL DEFAULT '{}'`
- **GIN index** on `tags` column for fast containment queries
- **Validation**: Max 10 tags, 1-50 chars, lowercase alphanumeric + hyphens
- **Normalization**: Automatic lowercase, trim, deduplication

**API Contracts**:
- `GET /api/tasks/tags` - List all user tags (alphabetically sorted)
- `GET /api/tasks?tags=work` - Filter tasks by tag
- `GET /api/tasks?tags=work&tags=urgent` - Filter by multiple tags (AND logic)
- `POST /api/tasks` - Create task with tags
- `PUT /api/tasks/{id}` - Update task including tags

## Phase 2: Implementation Plan

### 2.1 Database Migration

**File**: `backend/migrations/005_add_tags_to_tasks.sql`

**Changes**:
1. Add `tags TEXT[] DEFAULT '{}' NOT NULL` column to `tasks` table
2. Create GIN index: `CREATE INDEX idx_tasks_tags ON tasks USING GIN (tags)`
3. Add check constraint: `array_length(tags, 1) <= 10`

**Rollback Plan**:
```sql
ALTER TABLE tasks DROP COLUMN tags;
DROP INDEX idx_tasks_tags;
```

**Testing**:
- Verify column exists: `\d tasks`
- Verify index exists: `\di`
- Insert test task with tags
- Query with tag filter: `WHERE tags @> ARRAY['work']`

### 2.2 Backend Implementation

#### 2.2.1 Models (`backend/models/task.py`)

**Changes**:
- Add `tags: list[str]` field to `TaskBase`
- Use `sa_column=Column(ARRAY(String))` for SQLModel
- Add `@field_validator("tags")` with validation logic:
  - Max 10 tags
  - 1-50 chars each
  - Regex: `^[a-z0-9-]+$`
  - Automatic lowercase + trim + deduplication

**Testing**:
- Unit test: `test_tag_validation_max_tags()`
- Unit test: `test_tag_normalization()`
- Unit test: `test_tag_format_validation()`

#### 2.2.2 Routes (`backend/routes/tasks.py`)

**Changes**:
1. **New endpoint**: `GET /api/tasks/tags`
   - Returns `list[str]` of unique user tags
   - Sorted alphabetically
   - Requires authentication

2. **Update endpoint**: `GET /api/tasks`
   - Add `tags: list[str] | None` query parameter
   - Pass to service layer for filtering

**Testing**:
- Integration test: `test_list_tags_endpoint()`
- Integration test: `test_filter_by_single_tag()`
- Integration test: `test_filter_by_multiple_tags()`

#### 2.2.3 Services (`backend/services/task_service.py`)

**Changes**:
1. **New function**: `get_user_tags(session, user_id) -> list[str]`
   - SQL: `SELECT DISTINCT unnest(tags) FROM tasks WHERE user_id = ?`
   - Order by tag alphabetically

2. **Update function**: `get_user_tasks(..., tags: list[str] | None = None)`
   - If tags provided, apply filter: `WHERE tags @> ARRAY[tag] for tag in tags`
   - Uses GIN index for performance

**Testing**:
- Unit test: `test_get_user_tags()`
- Unit test: `test_filter_tasks_by_tags_and_logic()`

### 2.3 Frontend Implementation

#### 2.3.1 Types (`frontend/types/task.ts`)

**Changes**:
- Add `tags: string[]` to `Task` interface
- Add `tags?: string[]` to `TaskCreate` interface
- Add `tags?: string[]` to `TaskUpdate` interface
- Add `tags?: string[]` to `TaskFilter` interface

#### 2.3.2 API Client (`frontend/lib/api/tasks.ts`)

**Changes**:
1. **New function**: `getUserTags(): Promise<string[]>`
   - Calls `GET /api/tasks/tags`

2. **Update function**: `getTasks(filter?: TaskFilter, ...)`
   - If `filter.tags`, append `?tags=work&tags=urgent` to query string

#### 2.3.3 Components

**New Component**: `frontend/components/TagSelector.tsx`
- Tag input with autocomplete
- Load user tags on mount via `getUserTags()`
- Client-side filtering (debounced 300ms)
- Add/remove tags
- Display selected tags as chips with remove button
- Max 10 tags validation

**Update Component**: `frontend/components/TaskCard.tsx`
- Display tags as styled badges below task title

**Update Component**: `frontend/components/TaskForm.tsx`
- Include `<TagSelector>` component
- Pass `selectedTags` and `onChange` handler

**Update Component**: `frontend/components/TaskFilters.tsx`
- Add tag filtering section
- Allow selecting multiple tags
- Show active tag filters
- Clear filter option

**Testing**:
- Component test: `TagSelector.test.tsx`
- Component test: `TaskCard.test.tsx` (with tags)
- E2E test: Create task with tags, verify display

#### 2.3.4 Hooks

**New Hook**: `frontend/hooks/useTags.ts`
- Fetch user tags on mount
- Cache in React state
- Provide filtered tags based on input
- Debounce filtering (300ms)

### 2.4 Phase3 Integration (No Changes)

**Status**: ✅ No Phase2 changes required

**Approach**:
- Phase3 chatbot parses natural language to extract tags
- Calls Phase2 REST API with tags parameter
- Example: "show me work tasks" → `GET /api/tasks?tags=work`

**Phase3 Implementation** (separate from this plan):
```python
# Phase3 MCP tool
@mcp.tool()
async def list_tasks(tags: list[str] | None = None):
    response = requests.get(
        f"{PHASE2_API_URL}/api/tasks",
        params={"tags": tags} if tags else {},
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    return response.json()
```

## Testing Strategy

### Unit Tests (Backend)

**File**: `backend/tests/test_task_service.py`

1. `test_tag_validation_max_tags()` - Reject 11+ tags
2. `test_tag_validation_length()` - Reject tags >50 chars
3. `test_tag_validation_format()` - Reject invalid characters
4. `test_tag_normalization()` - Lowercase + trim + dedup
5. `test_get_user_tags()` - Return unique tags, sorted
6. `test_filter_by_single_tag()` - Filter by one tag
7. `test_filter_by_multiple_tags()` - AND logic
8. `test_tag_isolation()` - User A can't see User B's tags

### Integration Tests (Backend)

**File**: `backend/tests/test_task_routes.py`

1. `test_create_task_with_tags()` - POST /api/tasks with tags
2. `test_list_tags_endpoint()` - GET /api/tasks/tags
3. `test_filter_tasks_by_tags()` - GET /api/tasks?tags=work
4. `test_update_task_tags()` - PUT /api/tasks/{id} with tags

### Component Tests (Frontend)

**File**: `frontend/components/__tests__/TagSelector.test.tsx`

1. Render tag selector
2. Add tag via input
3. Autocomplete suggestions
4. Remove tag
5. Max 10 tags validation

### E2E Tests (Frontend)

**File**: `frontend/tests/e2e/tags.spec.ts`

1. Create task with tags
2. Filter tasks by tag
3. Edit task to add/remove tags
4. Tag autocomplete works

## Performance Benchmarks

| Metric | Target | How to Verify |
|--------|--------|---------------|
| Tag autocomplete | <300ms | Frontend DevTools, measure debounce delay |
| Tag filtering | <1s (1000+ tasks) | Backend logs, SQL EXPLAIN ANALYZE |
| Tag list endpoint | <500ms | API response time in DevTools |
| GIN index usage | Always | EXPLAIN ANALYZE should show Index Scan |

**Verification Query**:
```sql
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'abc' AND tags @> ARRAY['work'];

-- Expected: "Index Scan using idx_tasks_tags"
```

## Deployment Plan

### Step 1: Database Migration
```bash
psql "$DATABASE_URL" < backend/migrations/005_add_tags_to_tasks.sql
```

### Step 2: Backend Deployment
- Deploy updated backend code
- Restart FastAPI server
- Verify GET /api/tasks/tags endpoint

### Step 3: Frontend Deployment
- Build frontend: `npm run build`
- Deploy to Vercel
- Verify TagSelector component renders

### Step 4: Smoke Tests
- Create task with tags
- Filter by tag
- Verify autocomplete

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| GIN index maintenance overhead | Low | Acceptable for read-heavy workload |
| Tag count exceeds 100 per user | Low | Monitor usage; migrate to junction table if needed |
| Autocomplete degrades with 1000+ tags | Very Low | Implement server-side filtering if needed |
| Users create conflicting tags | Medium | Validation normalizes to lowercase |

## Success Metrics

1. ✅ All 22 functional requirements met (from spec.md)
2. ✅ All 10 success criteria achieved (from spec.md)
3. ✅ All acceptance scenarios pass (from quickstart.md)
4. ✅ Performance targets met (<300ms autocomplete, <1s filtering, <500ms tag list)
5. ✅ 95%+ test coverage for new code
6. ✅ Zero breaking changes to existing API

## Next Steps

1. ✅ Research completed
2. ✅ Data model designed
3. ✅ API contracts defined
4. ✅ Test scenarios documented
5. ⏭️ **Run `/sp.tasks`** to generate implementation tasks
6. ⏭️ Run `/sp.implement` to execute tasks
7. ⏭️ Manual testing via quickstart.md
8. ⏭️ Deploy to production

## References

- Feature Spec: [spec.md](./spec.md)
- Research: [research.md](./research.md)
- Data Model: [data-model.md](./data-model.md)
- API Contracts: [contracts/openapi-tags.yaml](./contracts/openapi-tags.yaml)
- Test Scenarios: [quickstart.md](./quickstart.md)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
