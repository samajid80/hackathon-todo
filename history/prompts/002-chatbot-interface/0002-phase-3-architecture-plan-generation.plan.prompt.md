---
id: 0002
title: Phase 3 Architecture Plan Generation
stage: plan
date: 2025-12-20
surface: cli
model: claude-sonnet-4.5
feature: 002-chatbot-interface
branch: 002-chatbot-interface
user: developer
command: /sp.plan
labels: [architecture, planning, phase3, chatbot, mcp-server]
links:
  spec: specs/002-chatbot-interface/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/002-chatbot-interface/plan.md
    status: created
    lines: 902
tests: []
---

## Prompt

Execute `/sp.plan` command to create comprehensive architecture plan for Phase 3 (Natural Language Chatbot for Todo Management).

**Context**:
- Feature: AI-powered conversational interface using OpenAI Agents SDK and MCP Server
- Constitution: v3.0.0 (Phase 3 transition)
- Requirements: Zero changes to phase2-backend, three-service architecture, stateless design
- Deployment: Railway (3 backends) + Vercel (2 frontends) + Neon PostgreSQL (shared)

**Goals**:
1. Define HOW to implement Phase 3 chatbot specification
2. Ensure constitutional compliance (backward compatibility, service separation)
3. Document architecture, data flows, API contracts, deployment strategy
4. Identify research tasks and design artifacts needed
5. Provide implementation roadmap with risk mitigation

## Response snapshot

Created comprehensive architecture plan at `specs/002-chatbot-interface/plan.md` (902 lines) covering:

**Technical Context**:
- Languages: Python 3.13+ (backends), TypeScript 5.0+ / Node 24+ (frontend)
- Key Dependencies: OpenAI Agents SDK 0.6.4+, Official MCP SDK, FastAPI 0.122.0+, Next.js 16+, OpenAI ChatKit React
- Architecture: Three-service distributed system (phase2-backend unchanged, phase3-backend for chat, phase3-mcp-server for tools)
- Performance: <5s chat response, <2s MCP tool execution, 100 concurrent users

**Constitutional Compliance** (✅ PASS):
- Three-service architecture preserves Phase 2 completely
- Stateless design (conversation history in DB, no in-memory sessions)
- Single source of truth (phase2-backend authoritative for tasks)
- Backward compatibility (zero code changes to existing services)
- Separation of concerns (chat, MCP tools, task management isolated)

**Project Structure**:
- **phase3-backend/**: Chat endpoint, OpenAI integration, conversation management
- **phase3-mcp-server/**: 5 MCP tools calling phase2-backend REST APIs
- **phase3-frontend/**: ChatKit UI with Better-Auth integration
- **database/migrations/**: New tables (conversations, messages) preserving existing schema

**Data Model**:
- Conversation: user_id, timestamps (indexed for performance)
- Message: conversation_id, role (user/assistant/system), content, timestamps
- Existing Task entity unchanged (managed by phase2-backend)

**API Contracts**:
- Chat API: `POST /api/{user_id}/chat` with JWT auth, rate limiting (10 req/min)
- MCP Tools: 5 endpoints (add_task, list_tasks, complete_task, delete_task, update_task)
- Error handling: Standardized format with user-friendly messages

**Architecture Diagrams**:
- High-level service architecture (3 backends + 2 frontends + shared DB)
- Chat request flow (12-step end-to-end)
- MCP tool execution flow (detailed call chain)

**Implementation Strategy**:
- Phase 3A: Database migrations, verify Phase 2 tests pass
- Phase 3B: MCP server (simplest first - 5 tools with mocked tests)
- Phase 3C: Chat backend (OpenAI integration, conversation persistence)
- Phase 3D: Chat frontend (ChatKit UI, Better-Auth reuse)
- Phase 3E: Integration testing (backward compatibility, performance, security)
- Phase 3F: Documentation and demo video

**Risk Mitigation**:
- Phase 2 regression: Zero code changes, rollback independence
- OpenAI rate limits: Exponential backoff, friendly errors
- Database performance: Proper indexes, connection pooling
- MCP complexity: Start simple, use official SDK
- ChatKit issues: Follow docs, custom UI fallback

**Phase 0 Research Tasks**:
1. OpenAI Agents SDK integration patterns
2. Official MCP SDK usage (Python)
3. ChatKit React integration with Next.js 16
4. Conversation history storage optimization
5. Phase2 backend REST API documentation

**Phase 1 Design Artifacts** (embedded in plan):
- data-model.md: Conversation, Message schemas with indexes
- contracts/: Chat API and MCP Tools OpenAPI specs
- quickstart.md: 5 test scenarios (add task, list, complete, error handling)

## Outcome

- ✅ Impact: Comprehensive architecture plan created for Phase 3 chatbot implementation, fully compliant with constitution v3.0.0
- 🧪 Tests: Plan includes testing strategy (Phase 2 regression tests, Phase 3 unit/integration tests, end-to-end scenarios)
- 📁 Files: Created `specs/002-chatbot-interface/plan.md` (902 lines)
- 🔁 Next prompts: `/sp.tasks` to generate dependency-ordered implementation tasks
- 🧠 Reflection: Plan successfully balances architectural rigor (three-service separation, stateless design) with practical implementation guidance (deployment order, risk mitigation). Research tasks are well-defined, design artifacts embedded inline for immediate reference.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan execution smooth, constitutional compliance verified
- Graders run and results (PASS/FAIL): Constitutional gate check PASS (all 9 sections compliant)
- Prompt variant (if applicable): N/A (standard /sp.plan workflow)
- Next experiment (smallest change to try): Consider splitting Phase 1 design artifacts into separate files (data-model.md, contracts/, quickstart.md) for better modularity in future iterations
