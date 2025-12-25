# Implementation Plan: Phase 3 Task Tags Integration

**Branch**: `001-phase3-task-tags` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase3-task-tags/spec.md`

## Summary

Integrate Phase 2's existing task tags functionality into Phase 3's chat interface by enhancing three components: the Next.js chat frontend to display tags as visual badges, the MCP server to interpret natural language tag commands and extract tag parameters, and the Phase 3 backend proxy to cache tag lists and forward requests to Phase 2's backend. This leverages all existing Phase 2 backend endpoints (GET /api/tasks/tags, GET /api/tasks?tags=X) without any backend code modifications, ensuring zero risk to production systems while enabling conversational tag management through the chatbot.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x + Next.js 16 (App Router) + React 19
- MCP Server: Python 3.13+
- Phase 3 Backend: Python 3.13+

**Primary Dependencies**:
- Frontend: Tailwind CSS, OpenAI ChatKit (existing)
- MCP Server: Official MCP SDK (Python), httpx for HTTP client
- Phase 3 Backend: FastAPI, httpx for proxying

**Storage**:
- PostgreSQL (Neon) - Phase 2 already has tags column (TEXT[] array) in tasks table
- Phase 3 backend: In-memory cache for tag lists (60-second TTL, per-user)

**Testing**:
- Frontend: TypeScript type checking, ESLint, manual chat testing
- MCP Server: pytest with mocked Phase 2 backend responses
- Phase 3 Backend: pytest with cache validation, proxy behavior tests

**Target Platform**:
- Frontend: Vercel (phase3-frontend deployment)
- MCP Server: Railway
- Phase 3 Backend: Railway

**Project Type**: Web application (multi-service: phase3-frontend, phase3-backend, phase3-mcp-server)

**Performance Goals**:
- Tag display: <500ms latency for rendering tags in chat messages
- Tag filtering: <1s response time for filtered task lists (up to 1000 tasks)
- Tag list retrieval: <100ms for cached responses, <500ms cache miss
- MCP tag extraction: 90% accuracy, 85% command interpretation success rate

**Constraints**:
- NO modifications to Phase 2 backend code (backend/ directory is read-only)
- MUST use existing Phase 2 endpoints: GET /api/tasks/tags, GET /api/tasks?tags=X, POST/PUT /api/tasks
- MCP server confidence threshold: 70% (ask for clarification below this)
- Context retention: "this" references valid until next task-related command
- Retry strategy: Single retry after 2 seconds for failed operations
- Caching: 60-second TTL with invalidation on tag operations
- Logging: Selective (errors + confidence <70% only)

**Scale/Scope**:
- Support up to 100 unique tags per user
- Handle tasks with up to 10 tags each (Phase 2 validation enforced)
- MCP server should ask for clarification <15% of the time
- Tag operations must work within existing chat conversation flow

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Three-Service Architecture (Section 2.1)
✅ **COMPLIANT**: This feature modifies only Phase 3 components:
- phase3-frontend: Tag display in ChatMessage component
- phase3-mcp-server: Tag extraction from natural language, tag-related tool calls
- phase3-backend: Tag list caching and proxy logic

❌ **NO CHANGES** to phase2-backend (requirement explicitly preserved)

### Stateless Architecture (Section 2.2)
✅ **COMPLIANT**:
- phase3-backend: Tag list cache is stateless (keyed by user_id, no server affinity required)
- phase3-mcp-server: No state (task context managed by OpenAI Agents SDK session)
- Cache invalidation triggers on tag operations (no manual cache management)

### Single Source of Truth (Section 2.3)
✅ **COMPLIANT**:
- Phase 2 backend remains authoritative for all task data including tags
- MCP server calls Phase 2 backend HTTP APIs (GET /api/tasks/tags, GET /api/tasks?tags=X)
- NO direct database access from Phase 3 components
- Tag validation enforced by Phase 2 backend (max 10 tags, 1-50 chars, format ^[a-z0-9-]+$)

### Backward Compatibility (Section 2.4)
✅ **COMPLIANT**:
- Phase 2 backend code: ZERO changes (feature already implemented in Phase 2)
- Phase 2 endpoints: ZERO modifications (using existing tag endpoints as-is)
- Phase 2 frontend: Unaffected (separate deployment, no shared code)
- Database schema: NO CHANGES (tags column already exists in tasks table)

### Separation of Concerns (Section 2.5)
✅ **COMPLIANT**:
- **phase3-frontend**: Tag display in chat UI, tag badge components
- **phase3-backend**: Tag list caching (60s TTL), proxy forwarding to Phase 2
- **phase3-mcp-server**: NLP tag extraction, tag parameter validation, HTTP calls to Phase 2 backend

**GATE STATUS**: ✅ **PASS** - All constitutional principles satisfied, zero violations

## Project Structure

### Documentation (this feature)

```text
specs/001-phase3-task-tags/
├── spec.md              # Feature specification (already created)
├── plan.md              # This file (/sp.plan output)
├── research.md          # Phase 0 output (NLP patterns, caching strategies)
├── data-model.md        # Phase 1 output (Tag display model, Context state model)
├── quickstart.md        # Phase 1 output (Manual test scenarios)
├── contracts/           # Phase 1 output (MCP tool schemas for tags)
│   └── mcp-tag-tools.yaml
└── checklists/          # Specification quality checklist (already exists)
    └── requirements.md
```

### Source Code (repository root)

```text
phase3-frontend/
├── components/
│   ├── ChatMessage.tsx      # MODIFY: Add tag badge rendering
│   ├── ChatInterface.tsx    # MODIFY: Pass tag data to ChatMessage
│   └── TagBadge.tsx         # CREATE: Reusable tag badge component
├── lib/
│   ├── types.ts             # MODIFY: Add tag fields to Task interface
│   └── api.ts               # MODIFY: Handle tag data in API responses
└── app/chat/
    └── page.tsx             # INSPECT: Ensure ChatInterface receives tag data

phase3-backend/
├── app/
│   ├── services/
│   │   └── cache_service.py  # CREATE: Tag list caching logic (60s TTL)
│   ├── routes/
│   │   └── proxy.py          # MODIFY: Add tag list caching + invalidation
│   └── utils/
│       └── http_client.py    # MODIFY: Forward tag query parameters
└── tests/
    └── test_tag_caching.py   # CREATE: Cache behavior tests

phase3-mcp-server/
├── app/
│   ├── tools/
│   │   ├── list_tasks.py     # MODIFY: Add tags parameter support
│   │   ├── add_task.py       # MODIFY: Extract tags from NLP
│   │   ├── update_task.py    # MODIFY: Extract tags from NLP
│   │   ├── list_tags.py      # CREATE: New tool for "what tags do I have?"
│   │   └── tag_extractor.py  # CREATE: NLP tag extraction utility
│   ├── schemas/
│   │   └── tag_schemas.py    # CREATE: Tag validation schemas
│   └── utils/
│       └── context_manager.py # CREATE: Task context retention logic
└── tests/
    ├── test_tag_extraction.py # CREATE: NLP extraction tests
    └── test_tag_tools.py      # CREATE: Tag tool behavior tests

backend/  # Phase 2 - READ ONLY, NO CHANGES
├── routes/
│   └── tasks.py              # REFERENCE: Existing tag endpoints
└── models/
    └── task.py               # REFERENCE: Tag validation rules
```

**Structure Decision**: This is a multi-service web application following Phase 3 architecture. The feature spans all three Phase 3 services (frontend, backend proxy, MCP server) but makes ZERO changes to Phase 2 backend. Each service has clear boundaries:
- Frontend: UI rendering of tags
- MCP Server: Natural language understanding + tag extraction
- Phase 3 Backend: Caching + proxying to Phase 2

## Complexity Tracking

> **No constitutional violations requiring justification**

All complexity is inherent to the Phase 3 architecture (established by constitution v3.0.0):
- Three-service architecture: Constitutional requirement (Section 2.1)
- Caching in Phase 3 backend: Performance optimization within constitutional boundaries
- NLP tag extraction in MCP server: Core responsibility of MCP server (Section 2.5)
- No database direct access: Constitutional constraint (Section 2.3)

---

**Next Phases**: Phase 0 (Research) → Phase 1 (Design & Contracts) → Phase 2 (Tasks via /sp.tasks)
