# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **full-stack todo application** project built using the **Spec-Driven Development (SDD)** methodology with SpecKit Plus framework. The project emphasizes specification-first development with architectural decision tracking and prompt history preservation.

Always use context7 when code generation, setup or configuration steps, or library/API documentation is needed. This means automatically using the Context7 MCP tools to resolve library id and get library docs without explicit requests.

### Project Structure

- `backend/` - FastAPI backend (Python 3.13+) with JWT auth and PostgreSQL
- `frontend/` - Next.js 16 frontend with Better-Auth and React 19
- `database/` - PostgreSQL schema and migrations
- `phase1/` - Legacy Python console implementation (reference only)
- `.specify/` - SpecKit Plus framework (templates, scripts, memory)
- `.claude/` - Custom slash commands and agents
- `specs/` - Feature specifications (created per feature)
- `history/` - Prompt History Records (PHR) and Architecture Decision Records (ADR)

## Development Commands

### Backend (FastAPI + Python 3.13)

**Install dependencies**:
```bash
cd backend
uv pip install -e ".[test,dev]"
# or with pip:
pip install -e ".[test,dev]"
```

**Run development server**:
```bash
cd backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Run tests**:
```bash
cd backend
# All tests
python3.13 -m pytest tests/ -v

# With coverage
python3.13 -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Specific test file
python3.13 -m pytest tests/test_auth.py -v
python3.13 -m pytest tests/test_task_service.py -v
python3.13 -m pytest tests/test_task_routes.py -v
python3.13 -m pytest tests/test_integration.py -v
```

**Linting and type checking**:
```bash
cd backend
ruff check . --fix
ruff format .
mypy . --strict
```

### Frontend (Next.js 16 + React 19)

**Install dependencies**:
```bash
cd frontend
npm install
```

**Run development server**:
```bash
cd frontend
npm run dev
# Opens on http://localhost:3000
```

**Build and type checking**:
```bash
cd frontend
npm run build
npm run type-check
npm run lint
```

### Database (PostgreSQL on Neon)

**Environment setup**:
```bash
# Backend
cd backend
cp .env.example .env
echo "JWT_SECRET=$(openssl rand -base64 32)" >> .env
# Add DATABASE_URL from Neon dashboard

# Frontend
cd frontend
cp .env.local.example .env.local
# Copy same JWT_SECRET to BETTER_AUTH_SECRET
# Add DATABASE_URL
```

**Run migrations**:
```bash
# Using psql (recommended)
psql "$DATABASE_URL" < backend/migrations/000_create_users_table.sql
psql "$DATABASE_URL" < backend/migrations/001_create_tasks_table.sql
psql "$DATABASE_URL" < backend/migrations/002_updated_at_trigger.sql

# Verify tables
psql "$DATABASE_URL" -c "\dt"
psql "$DATABASE_URL" -c "\d tasks"
```

**Important**: `JWT_SECRET` (backend) and `BETTER_AUTH_SECRET` (frontend) must be identical for authentication to work.

## Architecture Overview

### Full-Stack Architecture (Phase 2)

The application follows a three-tier architecture:

**Frontend (Next.js 16)**:
- `app/` - Next.js App Router pages (login, signup, tasks)
- `components/` - Reusable UI components (TaskCard, TaskFilters, StatusBadge, etc.)
- `lib/auth.ts` - Better-Auth configuration
- `lib/auth-client.ts` - Client-side auth utilities
- `lib/api/tasks.ts` - Backend API client

**Backend (FastAPI)**:
- `auth/jwt_middleware.py` - JWT validation and user extraction
- `auth/rate_limiter.py` - Rate limiting middleware
- `models/task.py` - SQLModel Task entity and Pydantic schemas
- `models/user.py` - User model (Better-Auth compatible)
- `routes/tasks.py` - RESTful task endpoints
- `services/task_service.py` - Business logic layer
- `db.py` - Database connection and session management

**Database (PostgreSQL)**:
- `users` table - Managed by Better-Auth
- `tasks` table - User-scoped tasks with composite indexes
- Automatic `updated_at` trigger

### Key Design Patterns

**Authentication Flow**:
1. User signs up/logs in via Next.js frontend (Better-Auth)
2. Better-Auth issues JWT with `user_id` claim
3. Frontend sends JWT in `Authorization: Bearer <token>` header
4. Backend validates JWT and extracts `user_id`
5. All queries filtered by `user_id` (data isolation)

**Data Isolation**:
- Every task is scoped to `user_id`
- Backend enforces user isolation in all queries
- User can only access their own tasks (403 if violation)

**API Layer**:
- RESTful endpoints: `GET /api/tasks`, `POST /api/tasks`, etc.
- Pagination, filtering, and sorting support
- Pydantic validation for request/response schemas

### Legacy Phase 1 (Console Application)

The `phase1/` directory contains the original console-based implementation:

**Run Phase 1**:
```bash
cd phase1
python3.13 -m src
# or: ./run.sh
```

**Test Phase 1**:
```bash
cd phase1
python3.13 -m pytest
python3.13 -m pytest --cov=src --cov-report=term-missing
```

**Architecture**: Clean layered design (domain → storage → services → commands)
- In-memory storage (dict-based)
- Console UI with menu-driven interface
- No authentication or persistence

Phase 1 remains for reference but Phase 2 is the active implementation.

## Spec-Driven Development Workflow

This project uses a structured SDD workflow with custom slash commands.

### Available Slash Commands

- `/sp.specify <description>` - Create feature specification from natural language
- `/sp.clarify` - Identify underspecified areas and ask targeted questions
- `/sp.plan` - Generate implementation plan with architecture decisions
- `/sp.tasks` - Generate dependency-ordered tasks from design artifacts
- `/sp.implement` - Execute the implementation plan
- `/sp.analyze` - Cross-artifact consistency analysis
- `/sp.adr <title>` - Create Architecture Decision Record
- `/sp.phr` - Create Prompt History Record
- `/sp.constitution` - Create/update project constitution
- `/sp.git.commit_pr` - Git workflow automation (commit and PR)
- `/sp.checklist` - Generate custom checklists

**Typical workflow**: `/sp.specify` → `/sp.clarify` → `/sp.plan` → `/sp.tasks` → `/sp.implement`

### SpecKit Plus Framework

The `.specify/` directory contains:
- **Templates** (`.specify/templates/`): Standardized formats for specs, plans, tasks, ADRs, PHRs
- **Scripts** (`.specify/scripts/bash/`): Shell utilities for feature creation, PHR/ADR generation
- **Memory** (`.specify/memory/constitution.md`): Project constitution defining principles and constraints

Key scripts:
- `create-new-feature.sh` - Initialize new feature directory
- `setup-plan.sh` - Set up planning artifacts
- `create-phr.sh` - Generate Prompt History Record
- `create-adr.sh` - Generate Architecture Decision Record
- `check-prerequisites.sh` - Validate environment

### Available Sub-Agents and Skills

**Sub-Agents** (`.claude/agents/`):
- **Backend Builder**: Orchestrates backend tasks (API, DB schemas, auth)
- **Frontend Composer**: Orchestrates frontend tasks (UI components, pages)

**Skills** (`.claude/skills/`):
- **Auth Integrator**: JWT/Better Auth setup
- **UI Component Builder**: Next.js components with Tailwind
- **DB Schema Creator**: SQLModel schemas
- **API Endpoint Generator**: FastAPI endpoints

## SDD Methodology Guidelines

**Core Guarantees**:
- Record every user input in a Prompt History Record (PHR) after every user message
- PHR routing under `history/prompts/`:
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: When architecturally significant decisions are detected, suggest documenting with `/sp.adr <title>`

**Development Policies**:
- Clarify and plan first - separate business understanding from technical plan
- Do not invent APIs, data, or contracts; ask targeted questions if missing
- Never hardcode secrets or tokens; use `.env` and document in `.env.example`
- Prefer smallest viable diff; do not refactor unrelated code
- Cite existing code with code references (`file:line`); propose new code in fenced blocks

**Execution Contract**:
1. Confirm surface and success criteria
2. List constraints, invariants, non-goals
3. Produce artifact with acceptance checks
4. Add follow-ups and risks (max 3 bullets)
5. Create PHR in appropriate subdirectory
6. Surface ADR suggestion if significant decision made

### Architecture Decision Records (ADR)

After design/architecture work, test for ADR significance:
- **Impact**: Long-term consequences? (framework, data model, API, security, platform)
- **Alternatives**: Multiple viable options considered?
- **Scope**: Cross-cutting and influences system design?

If ALL true, suggest:
```
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`
```

Wait for consent; never auto-create ADRs.

## Technology Stack

### Backend
- **Python**: 3.13+
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon)
- **Authentication**: JWT with python-jose
- **Testing**: pytest, pytest-asyncio, httpx
- **Linting**: ruff, mypy

### Frontend
- **Framework**: Next.js 16 (App Router)
- **React**: 19.0
- **Authentication**: Better-Auth
- **Styling**: Tailwind CSS
- **Database Client**: Kysely + pg
- **Testing**: ESLint, TypeScript

### Database
- **PostgreSQL**: Hosted on Neon (cloud)
- **Migrations**: SQL files in `backend/migrations/`
- **ORM**: SQLModel (backend), Kysely (frontend)

## Security Considerations

### Secrets Management

**CRITICAL**: Never commit `.env` or `.env.local` files to version control!

**Environment Variables**:

Backend (`.env`):
```env
DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname?sslmode=require
JWT_SECRET=<random-32-chars>  # openssl rand -base64 32
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

Frontend (`.env.local`):
```env
DATABASE_URL=<same-as-backend>
BETTER_AUTH_SECRET=<same-as-JWT_SECRET>
BETTER_AUTH_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

**Requirements**:
- `JWT_SECRET` must be at least 32 random characters
- `BETTER_AUTH_SECRET` must match `JWT_SECRET` exactly
- Never commit secrets to git (`.gitignore` includes `.env*`)
- Verify with: `git log -p -- .env`

### Security Features

**Rate Limiting** (T156):
- `/api/auth/signup`: 5 req/hour per IP
- `/api/auth/login`: 5 req/hour per IP
- `/api/tasks`: 100 req/hour per user
- Returns HTTP 429 with `Retry-After` header

**Input Validation** (T157):
- Pydantic validators on all inputs
- Field constraints: `title` (1-200 chars), `description` (0-2000 chars)
- SQL injection protection (SQLModel parameterized queries)

**Security Headers** (T159):
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (production only)
- `Referrer-Policy: strict-origin-when-cross-origin`

## API Endpoints

All task endpoints require JWT authentication via `Authorization: Bearer <token>` header.

**Task Management**:
- `POST /api/tasks` - Create new task
- `GET /api/tasks` - List all user's tasks (with filters/sorts/pagination)
- `GET /api/tasks/{task_id}` - Get single task
- `PUT /api/tasks/{task_id}` - Update task
- `PATCH /api/tasks/{task_id}/complete` - Mark task completed
- `DELETE /api/tasks/{task_id}` - Delete task

**Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- See `API_DOCUMENTATION.md` for examples

## Feature Development Structure

Each feature follows a consistent directory structure under `specs/<N>-<feature-name>/`:

- `spec.md` - Feature requirements (WHAT and WHY)
- `plan.md` - Architecture decisions and technical approach (HOW)
- `tasks.md` - Dependency-ordered implementation tasks
- `data-model.md` - Entity definitions and relationships (optional)
- `contracts/` - API contracts (OpenAPI/GraphQL schemas, optional)
- `research.md` - Research findings (optional)
- `quickstart.md` - Test scenarios and acceptance criteria (optional)
- `checklists/` - Quality validation checklists

### History Tracking

All under `history/`:
- `prompts/` - Prompt History Records organized by constitution, feature, or general
- `adr/` - Architecture Decision Records (numbered, with status tracking)

## Common Development Tasks

### Starting Full-Stack Development

**Terminal 1 - Backend**:
```bash
cd backend
source .venv/bin/activate  # if using venv
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

**Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Running All Tests

**Backend**:
```bash
cd backend
python3.13 -m pytest tests/ -v --cov=. --cov-report=term-missing
ruff check .
mypy . --strict
```

**Frontend**:
```bash
cd frontend
npm run type-check
npm run lint
npm run build
```

### Troubleshooting

**Database Connection Issues**:
```
ValueError: DATABASE_URL environment variable is not set
```
Solution: Copy `.env.example` to `.env` and configure `DATABASE_URL` from Neon dashboard

**JWT Validation Errors**:
```
HTTPException: Could not validate credentials
```
Solution: Ensure `JWT_SECRET` (backend) matches `BETTER_AUTH_SECRET` (frontend)

**CORS Errors**:
```
Access to fetch blocked by CORS policy
```
Solution: Verify `CORS_ORIGINS` in backend `.env` includes frontend URL

**Rate Limit Errors**:
```
HTTPException: 429 Too Many Requests
```
Solution: Wait for retry period indicated in `Retry-After` header

## Ubuntu 24.04 Setup Notes

Ubuntu 24.04 ships with Python 3.12 by default. To use Python 3.13:

```bash
# Install Python 3.13
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.13 python3.13-venv

# Create virtual environment
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[test,dev]"
```

## CI/CD Pipeline

**Workflows**:
- `.github/workflows/ci.yml` - CI on push/PR (tests, linting, type checking)
- `.github/workflows/deploy.yml` - CD on push to main (deployment to Render/Vercel)

**Jobs**:
- Backend tests (pytest, coverage, ruff, mypy)
- Frontend tests (ESLint, TypeScript, build)
- Security checks (safety, npm audit, secret scanning)
- Deployment (Render for backend, Vercel for frontend)
- Smoke tests (health checks after deployment)

## Project Constitution

The project constitution (`.specify/memory/constitution.md`) defines core principles for Phase 2:

**Key Principles**:
- **Specification-first**: Define WHAT before HOW
- **Technology-agnostic specs**: No implementation details in specifications
- **Testable requirements**: Every requirement must be verifiable
- **Decision tracking**: Document significant architectural choices
- **Prompt history**: Preserve full context of all AI interactions
- **Full-stack separation**: Frontend, backend, and database are clearly separated
- **Authentication required**: All task operations require authenticated user
- **User isolation**: Tasks are scoped per user with strict access controls

**Phase 2 Requirements**:
- Frontend: Next.js 16 + Better-Auth
- Backend: FastAPI + JWT authentication
- Database: Neon PostgreSQL
- Architecture: Full-stack separation (frontend/, backend/, database/)
