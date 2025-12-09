# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **hackathon todo application** project built using the **Spec-Driven Development (SDD)** methodology with SpecKit Plus framework. The project emphasizes specification-first development with architectural decision tracking and prompt history preservation.

Always use context7 when I need code generation, setup or configuration steps, or
library/API documentation. This means you should automatically use the Context7 MCP
tools to resolve library id and get library docs without me having to explicitly ask.

### Project Structure

- `phase1/` - Python-based implementation (Python 3.13+)
  - Minimal starter code with virtual environment
  - Entry point: `phase1/main.py`
- `.specify/` - SpecKit Plus framework (templates, scripts, memory)
- `.claude/commands/` - Custom slash commands for SDD workflow
- `specs/` - Feature specifications (created per feature)
- `history/` - Prompt History Records (PHR) and Architecture Decision Records (ADR)

## Development Commands

### Running the Application

**Phase 1 (Python)**:
```bash
cd phase1
python main.py
# or use the provided script:
/home/majid/projects/hackathon-todo/scripts/run-phase1.sh
```

**Python Environment**:
- Python version: 3.13+ (see `phase1/.python-version`)
- Virtual environment: `phase1/.venv/`
- Package manager: uv (via `pyproject.toml`)

**Ubuntu 24.04 Setup Note**:
Ubuntu 24.04 ships with Python 3.12 by default. To use Python 3.13:
1. Install Python 3.13: `sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt install python3.13 python3.13-venv`
2. Recreate virtual environment with Python 3.13:
   ```bash
   cd phase1
   rm -rf .venv
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install uv  # or use system uv if available
   ```
3. Run application: `python3.13 main.py` or activate venv first: `source .venv/bin/activate && python main.py`

## Spec-Driven Development Workflow

This project uses a structured SDD workflow. You are an expert AI assistant specializing in this methodology. Your primary goal is to work with the architecture to build products systematically.

### Available Slash Commands

The project includes custom slash commands for the SDD workflow (all under `.claude/commands/`):

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

## SDD Methodology Guidelines

**Your Success is Measured By:**
- All outputs strictly follow user intent
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions
- All changes are small, testable, and reference code precisely

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Project Architecture

### Feature Development Structure

Each feature follows a consistent directory structure under `specs/<N>-<feature-name>/`:

- `spec.md` - Feature requirements (WHAT and WHY, no implementation details)
- `plan.md` - Architecture decisions and technical approach (HOW)
- `tasks.md` - Dependency-ordered implementation tasks
- `data-model.md` - Entity definitions and relationships (optional)
- `contracts/` - API contracts (OpenAPI/GraphQL schemas, optional)
- `research.md` - Research findings and decisions (optional)
- `quickstart.md` - Test scenarios and acceptance criteria (optional)
- `checklists/` - Quality and completeness validation checklists

### History Tracking

All under `history/`:

- `prompts/` - Prompt History Records organized by:
  - `constitution/` - Constitution-related prompts
  - `<feature-name>/` - Feature-specific prompts
  - `general/` - General development prompts
- `adr/` - Architecture Decision Records (numbered, with status tracking)

### Key Principles

The project constitution (`.specify/memory/constitution.md`) defines core principles. Currently it's a template - principles will be established during feature development. Typical SDD principles include:

- **Specification-first**: Define WHAT before HOW
- **Technology-agnostic specs**: No implementation details in specifications
- **Testable requirements**: Every requirement must be verifiable
- **Decision tracking**: Document significant architectural choices
- **Prompt history**: Preserve full context of all AI interactions

## Active Technologies
- Python 3.13 + Python standard library (uuid, datetime, enum); pytest, ruff, mypy for testing/quality only (001-console-todo-app)
- In-memory only (Python dict mapping UUID → Task object) (001-console-todo-app)

## Recent Changes
- 001-console-todo-app: Added Python 3.13 + Python standard library (uuid, datetime, enum); pytest, ruff, mypy for testing/quality only
