---
id: "0003"
title: phase3-task-tags-plan
stage: plan
date: 2025-12-24
surface: claude-code
model: claude-sonnet-4-5
feature: 001-phase3-task-tags
branch: 001-phase3-task-tags
user: majid
command: /sp.plan
labels: [planning, phase3, tags, architecture]
links:
  spec: specs/001-phase3-task-tags/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/001-phase3-task-tags/plan.md
    action: created
    lines: 182
  - path: specs/001-phase3-task-tags/research.md
    action: created
    lines: 310
  - path: specs/001-phase3-task-tags/data-model.md
    action: created
    lines: 408
  - path: specs/001-phase3-task-tags/contracts/mcp-tag-tools.yaml
    action: created
    lines: 296
  - path: specs/001-phase3-task-tags/quickstart.md
    action: created
    lines: 339
  - path: CLAUDE.md
    action: modified
    lines: N/A
tests:
  - type: constitution-check
    status: PASS
    gates: [three-service-architecture, stateless-architecture, single-source-of-truth, backward-compatibility, separation-of-concerns]
---

## Prompt

/sp.plan

Execute the implementation planning workflow using the plan template to generate design artifacts for feature 001-phase3-task-tags (Adding tags to Tasks in Phase 3).

User context: Feature specification completed and clarified. All [NEEDS CLARIFICATION] markers resolved with user-selected answers. Ready to generate implementation plan, research artifacts, data models, and contracts.

## Response snapshot

Generated comprehensive implementation plan for Phase 3 task tags integration:

**Planning Artifacts Created**:
1. **plan.md** - Implementation roadmap with:
   - Technical Context (Python 3.13, TypeScript 5.x, Next.js 16, MCP SDK, FastAPI, OpenAI Agents SDK)
   - Constitution Check: ✅ PASS (all 5 gates satisfied, zero violations)
   - Project Structure (phase3-frontend, phase3-backend, phase3-mcp-server modifications)
   - Performance Goals (tag display <500ms, filtering <1s, cache <100ms)
   - Constraints (zero Phase 2 backend changes, use existing endpoints)

2. **research.md** - Technical decisions covering:
   - NLP tag extraction patterns (pattern matching + Agent SDK confidence)
   - Caching strategy (60s TTL in-memory with smart invalidation)
   - Task context retention (SDK-managed with reset triggers)
   - Retry and error handling (single retry after 2s)
   - Logging approach (selective: errors + confidence <70%)
   - Frontend tag display (Tailwind CSS pill badges with truncation)

3. **data-model.md** - Data structures and flows:
   - Task entity (extended from Phase 2 with tags field)
   - TagCache (Phase 3 backend, 60s expiration)
   - TaskContext (MCP server session state)
   - TagExtractionResult (NLP output structure)
   - Data flow diagrams for display, filtering, caching
   - Validation rules and state transitions

4. **contracts/mcp-tag-tools.yaml** - MCP tool schemas:
   - Modified tools: list_tasks, add_task, update_task (added tags parameters)
   - New tool: list_tags (with caching specification)
   - NLP extraction patterns with confidence scores
   - Validation rules and error codes
   - HTTP mappings to Phase 2 backend endpoints

5. **quickstart.md** - Manual test scenarios:
   - 5 primary scenarios (P1-P5) covering all user stories
   - 20+ test cases with expected results
   - Edge case testing (ambiguous NLP, invalid formats, many tags, backend unavailability)
   - Performance benchmarks
   - Logging verification examples
   - Acceptance criteria checklist

**Key Technical Decisions**:
- Zero modifications to Phase 2 backend (read-only constraint)
- Phase 3 backend caches tag lists (60s TTL, per-user, in-memory)
- MCP server handles NLP tag extraction (70% confidence threshold)
- Task context managed by OpenAI Agents SDK (resets on task-related commands)
- Single retry after 2s for failed operations
- Selective logging (errors + low-confidence only)
- Tailwind CSS pill badges for tag display (max 5 shown, "...+N more" for overflow)

**Constitution Compliance**:
- ✅ Three-Service Architecture: phase3-frontend, phase3-backend, phase3-mcp-server (phase2-backend unchanged)
- ✅ Stateless Architecture: In-memory cache is per-instance (no server affinity)
- ✅ Single Source of Truth: Phase 2 backend authoritative for all task data
- ✅ Backward Compatibility: Zero Phase 2 code changes
- ✅ Separation of Concerns: Clear service boundaries

**Agent Context Updated**: Added Phase 3 tag integration to CLAUDE.md

## Outcome

- ✅ Impact: Completed Phase 0 (Research) and Phase 1 (Design & Contracts) of planning workflow. Generated 5 comprehensive planning artifacts (plan.md, research.md, data-model.md, contracts/mcp-tag-tools.yaml, quickstart.md). Constitution check PASSED with zero violations. Ready for Phase 2 (Task Decomposition via /sp.tasks).
- 🧪 Tests: Constitution check validated compliance with all 5 architectural gates (three-service, stateless, single-source-of-truth, backward-compatibility, separation-of-concerns). No test suite required at planning stage.
- 📁 Files: Created 5 new files (plan.md, research.md, data-model.md, contracts/mcp-tag-tools.yaml, quickstart.md), modified 1 file (CLAUDE.md for agent context)
- 🔁 Next prompts: Run /sp.tasks to generate dependency-ordered implementation tasks from design artifacts. Then /sp.implement to execute the tasks.
- 🧠 Reflection: Planning workflow executed smoothly. All technical unknowns resolved through research phase. Constitution compliance verified upfront prevents rework. Multi-service architecture complexity well-documented with clear service boundaries. Comprehensive test scenarios in quickstart.md enable validation before implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Workflow completed without errors. Warning about multiple '001' prefixed spec directories is expected (001-console-todo-app, 001-ui-redesign, 001-phase3-task-tags are separate features).
- Graders run and results (PASS/FAIL): Constitution check: PASS (all 5 gates). Specification quality checklist (from previous phase): PASS (all items).
- Prompt variant (if applicable): N/A (standard /sp.plan workflow)
- Next experiment (smallest change to try): N/A (planning phase successful, proceed to task decomposition)
