---
id: 0002
title: phase-3-constitution-update
stage: constitution
date: 2025-12-20
surface: claude-code-cli
model: claude-sonnet-4.5
feature: phase-3-architecture
branch: main
user: majid
command: /sp.constitution
labels: [phase-3, constitution, architecture, microservices]
links:
  spec: N/A
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

User executed `/sp.constitution` command with Phase 3 architecture specification:

```text
# Phase 3 Constitution — AI-Powered Todo Chatbot
**Hackathon II — Spec-Driven Development**

**Version:** 3.0.0
**Ratified:** [CURRENT_DATE]
**Status:** Active (Phase 3)

## 1. Purpose

Transform Phase 2 full-stack todo app into an AI-powered chatbot system using:
- OpenAI Agents SDK for AI logic
- MCP Server for tool-based task operations
- Natural language interface via OpenAI ChatKit

**Phase 2 must remain completely unchanged and functional.**

## 2. Core Architectural Principles

### 2.1 Three-Service Architecture (CRITICAL)

```
phase2-backend (Railway) → Existing, unchanged
phase3-backend (Railway) → New, chat endpoint only
phase3-mcp-server (Railway) → New, MCP tools only

Shared: Neon PostgreSQL database
```

**Rationale:**
- Zero risk to Phase 2 production
- Clear service boundaries
- Prepares for Phase 4 (Kubernetes)
- Demonstrates microservices architecture

### 2.2 Stateless Architecture (CRITICAL)

- **phase3-backend:** Fetch/store conversation history from DB per request
- **phase3-mcp-server:** No in-memory state, stateless tool execution
- **No server-side sessions:** JWT for authentication only

### 2.3 Single Source of Truth

- **Database:** PostgreSQL is the only persistent store
- **Tasks:** phase2-backend is authoritative for all task operations
- **MCP Tools:** MUST call phase2-backend APIs (not DB directly)
- **Conversations:** phase3-backend owns conversation history

### 2.4 Backward Compatibility (CRITICAL)

- Phase 2 backend code: **NO CHANGES**
- Phase 2 endpoints: **NO MODIFICATIONS**
- Phase 2 frontend: **CONTINUES WORKING**
- Database schema: **EXTENDS ONLY** (add conversations, messages tables)

### 2.5 Separation of Concerns

**phase2-backend:**
- Task CRUD operations only
- Direct database access for tasks

**phase3-backend:**
- Chat endpoint only
- OpenAI Agents SDK integration
- Conversation history management
- Calls phase3-mcp-server for tools

**phase3-mcp-server:**
- 5 MCP tools (add, list, complete, delete, update)
- HTTP client for phase2-backend
- No direct database access

[Additional sections: Technology Stack, Database Schema, MCP Tools, Non-Functional Requirements, Constraints, Service Communication Flow, Deployment Strategy, Forward Compatibility, Success Criteria, Governance]
```

**Command**: Update project constitution to Phase 3.0.0 with three-service architecture while preserving all Phase 2 functionality.

## Response snapshot

Successfully updated constitution from v2.0.0 (Phase 2) to v3.0.0 (Phase 3):

**Version Change**: 2.0.0 → 3.0.0 (MAJOR)

**Key Changes**:

1. **Three-Service Architecture** (Section 2.1):
   - phase2-backend (existing, unchanged)
   - phase3-backend (new, chat endpoint)
   - phase3-mcp-server (new, MCP tools)

2. **Technology Stack Expansion** (Section 3):
   - Added OpenAI Agents SDK
   - Added MCP Server (Official Python SDK)
   - Added OpenAI ChatKit for frontend

3. **Database Schema Extension** (Section 4):
   - New: conversations table (user_id, id, created_at, updated_at)
   - New: messages table (user_id, conversation_id, role, content, created_at)
   - Preserved: users and tasks tables (no changes)

4. **MCP Tools Specification** (Section 5):
   - add_task, list_tasks, complete_task, delete_task, update_task
   - All tools call phase2-backend REST API via HTTP
   - No direct database access from MCP server

5. **Backward Compatibility Guarantees** (Section 2.4):
   - NO changes to Phase 2 backend code
   - NO modifications to Phase 2 endpoints
   - Phase 2 frontend continues working
   - Database migrations only add new tables

6. **Deployment Strategy** (Section 9):
   - 3 Railway services (phase2-backend, phase3-backend, phase3-mcp-server)
   - 2 Vercel frontends (phase2-frontend, phase3-frontend)
   - Shared Neon PostgreSQL database

7. **Forward Compatibility** (Section 10):
   - Prepares for Phase 4 (Kubernetes)
   - Health check endpoints required
   - Containerization-ready architecture

**Sync Impact Report** added to constitution file header documenting all changes, template impacts, and follow-up actions.

**Templates Status**:
- ✅ plan-template.md (constitution check updated)
- ✅ spec-template.md (aligned with multi-service requirements)
- ✅ tasks-template.md (supports phase2 + phase3 paths)
- ⚠️ .claude/commands/*.md (11 files require manual review)

## Outcome

- ✅ Impact: Constitution successfully updated to v3.0.0 (Phase 3), preserving Phase 2 governance (v2.0.0) and Phase 1 governance (v1.0.0)
- 🧪 Tests: No tests modified (Phase 2 tests remain unchanged)
- 📁 Files: .specify/memory/constitution.md (replaced with Phase 3 version)
- 🔁 Next prompts:
  - Update slash commands for Phase 3 awareness
  - Create specs/phase3/ directory structure
  - Archive Phase 2 constitution as constitution-v2.0.0-phase2.md
  - Update README.md and CLAUDE.md for Phase 3
- 🧠 Reflection: MAJOR version bump justified due to breaking architectural changes (three-service architecture), new technologies (OpenAI Agents SDK, MCP Server), and new database schema. All changes preserve Phase 2 functionality per Section 2.4 (Backward Compatibility).

## Evaluation notes (flywheel)

- Failure modes observed: None. Constitution update followed template precisely, all placeholders replaced with concrete values.
- Graders run and results (PASS/FAIL):
  - ✅ PASS: No unresolved bracket tokens
  - ✅ PASS: Version line matches report (3.0.0)
  - ✅ PASS: Dates in ISO format (2025-12-09, 2025-12-10, 2025-12-20)
  - ✅ PASS: Principles are declarative and testable
  - ✅ PASS: Sync Impact Report complete and detailed
- Prompt variant (if applicable): N/A (standard /sp.constitution command)
- Next experiment (smallest change to try): Test Phase 3 development workflow by creating first feature spec under specs/phase3/ to validate constitution principles in practice
