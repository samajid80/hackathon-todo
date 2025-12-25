# Feature Specification: Phase 3 Task Tags Integration

**Feature Branch**: `001-phase3-task-tags`
**Created**: 2025-12-24
**Status**: Draft
**Input**: User description: "I want to add feature to phase3 of the project. The feature is 'Adding tags to Tasks'. i have already implemented in phase 2 of the project which means the database already had the required changes and 'backend' folder also had the changes, You have to focus only on phase3-frontend, phase3-mcp-server and phase3-backend.. It means 'backend' endpoints already had the changes which is used by phase3-mcp-server"

## Clarifications

### Session 2025-12-24

- Q: How long should the chatbot remember which task "this" refers to when a user says "tag this with urgent"? → A: Until the next task-related command (e.g., "show tasks", "create task") resets context
- Q: At what confidence level should the MCP server ask for clarification vs. automatically executing a tag-related command? → A: Ask when confidence < 70%
- Q: Should the system automatically retry failed tag operations, and if so, how many times? → A: Retry once after 2 seconds
- Q: Should the Phase 3 backend cache the user's tag list (GET /api/tasks/tags), and if so, for how long? → A: Cache for 60 seconds
- Q: Should the system log tag-related operations for monitoring and debugging purposes? → A: Log errors and low-confidence interpretations only (selective logging)

## User Scenarios & Testing

### User Story 1 - Chat Interface Tag Display (Priority: P1)

As a user of the Phase 3 chat interface, I want to see tags displayed on tasks in the chat interface so that I can quickly understand the category and context of each task shown by the chatbot.

**Why this priority**: This is the foundation of tag visibility in Phase 3. Without displaying tags, users won't know that tag information exists, making all other tag features invisible and unusable.

**Independent Test**: Can be fully tested by having the chatbot list tasks and verifying that tags appear alongside each task in the chat messages. Delivers immediate value by providing task context at a glance.

**Acceptance Scenarios**:

1. **Given** I ask the chatbot "show me my tasks", **When** the chatbot displays my task list, **Then** each task shows its tags (if any) as visual badges or labels
2. **Given** I ask for details about a specific task, **When** the chatbot shows the task details, **Then** the task's tags are clearly displayed
3. **Given** a task has no tags, **When** the chatbot displays that task, **Then** no tag section is shown (or shows "No tags")
4. **Given** a task has multiple tags like "work", "urgent", and "meeting", **When** the chatbot displays the task, **Then** all three tags are visible and distinguishable

---

### User Story 2 - Natural Language Tag Filtering (Priority: P2)

As a user, I want to filter tasks by tags using natural language commands (e.g., "show me all work tasks" or "list my urgent tasks") so that I can focus on specific categories of tasks through conversational interaction.

**Why this priority**: Tag filtering is the primary use case for tags. This enables users to leverage the existing backend tag functionality through the chat interface, making task organization more intuitive.

**Independent Test**: Can be tested by issuing various natural language commands for tag filtering and verifying the chatbot returns only tasks matching the specified tags. Delivers value by enabling focused task views.

**Acceptance Scenarios**:

1. **Given** I have tasks tagged with "work", "home", and "urgent", **When** I say "show me my work tasks", **Then** the chatbot displays only tasks tagged with "work"
2. **Given** I have tasks with multiple tags, **When** I say "show me urgent work tasks", **Then** the chatbot displays only tasks that have BOTH "urgent" and "work" tags
3. **Given** I say "show me tasks tagged home", **When** the chatbot processes my request, **Then** it displays tasks with the "home" tag
4. **Given** I filter by a tag that doesn't exist on any task, **When** the chatbot processes the request, **Then** it responds with a message like "No tasks found with tag 'shopping'"
5. **Given** I want to see all tasks again, **When** I say "show all tasks" or "clear filters", **Then** the chatbot displays all my tasks regardless of tags

---

### User Story 3 - Add Tags via Natural Language (Priority: P3)

As a user, I want to add tags to tasks using natural language commands (e.g., "add a task to buy groceries tagged with home" or "tag this task with urgent") so that I can categorize tasks conversationally during creation or editing.

**Why this priority**: This enables users to create tagged tasks without leaving the chat interface. It builds on the core display and filtering functionality and makes the chat interface feature-complete for tag management.

**Independent Test**: Can be tested by creating or editing tasks with tag-related commands and verifying the tags are persisted and displayed. Delivers value by enabling complete tag workflow in chat.

**Acceptance Scenarios**:

1. **Given** I am creating a new task via chat, **When** I say "add a task to buy groceries tagged with home", **Then** the chatbot creates a task with title "buy groceries" and tag "home"
2. **Given** I am creating a task, **When** I say "create a task to prepare presentation tagged with work and urgent", **Then** the task is created with both "work" and "urgent" tags
3. **Given** I have an existing task displayed in chat, **When** I say "tag this with important", **Then** the chatbot adds the "important" tag to that task (context: "this" refers to the last task mentioned until the next task-related command)
4. **Given** I say "create a task to call dentist with tags personal and health", **When** the task is created, **Then** it has both "personal" and "health" tags
5. **Given** I try to add more than 10 tags to a task, **When** the chatbot processes my request, **Then** it responds with an error message about the maximum tag limit
6. **Given** I viewed a task, then issued a "show tasks" command, **When** I say "tag this with urgent", **Then** the chatbot asks which task I'm referring to (context was reset by the task-related command)

---

### User Story 4 - View User's Available Tags (Priority: P4)

As a user, I want to ask the chatbot "what tags do I have?" or "list my tags" so that I can discover what tag categories I've used and reuse them consistently across tasks.

**Why this priority**: This is a convenience feature that improves UX but isn't critical for core tag functionality. Users can still create and use tags without knowing the full list.

**Independent Test**: Can be tested by asking for the tag list and verifying the chatbot returns all unique tags the user has created. Delivers value by helping users maintain consistent tag naming.

**Acceptance Scenarios**:

1. **Given** I have created tasks with tags "work", "home", "urgent", and "personal", **When** I ask "what tags do I have?", **Then** the chatbot lists all four tags alphabetically
2. **Given** I have multiple tasks with the "work" tag, **When** I ask "list my tags", **Then** "work" appears only once in the list
3. **Given** I have no tasks with tags, **When** I ask "what tags do I have?", **Then** the chatbot responds with "You haven't created any tags yet"
4. **Given** I delete all tasks with a specific tag, **When** I ask "list my tags", **Then** that tag no longer appears in the list

---

### User Story 5 - Remove Tags via Natural Language (Priority: P5)

As a user, I want to remove tags from tasks using natural language commands (e.g., "remove the urgent tag from this task") so that I can update task categorization conversationally.

**Why this priority**: This completes the full CRUD cycle for tags in the chat interface. It's the lowest priority because users can always edit tasks to remove tags, but it improves the conversational experience.

**Independent Test**: Can be tested by removing tags via chat commands and verifying the tags are removed from tasks. Delivers value by enabling complete tag lifecycle management in chat.

**Acceptance Scenarios**:

1. **Given** I have a task displayed in chat with tags "work" and "urgent", **When** I say "remove the urgent tag", **Then** the task retains only the "work" tag
2. **Given** I have a task with multiple tags, **When** I say "remove all tags from this task", **Then** the task has no tags
3. **Given** I try to remove a tag that doesn't exist on a task, **When** the chatbot processes my request, **Then** it responds with a message like "This task doesn't have the 'urgent' tag"
4. **Given** I say "untag this task from work", **When** the chatbot processes the command, **Then** the "work" tag is removed from the task

---

### Edge Cases

- What happens when a user uses natural language that's ambiguous about tags (e.g., "show me tagged tasks")? (System should ask for clarification: "Which tag would you like to filter by?" or show all tasks with any tags)
- What happens when a user tries to add an invalid tag format via chat (e.g., "tag this with URGENT!!!")? (MCP server validates and returns error: "Tags can only contain lowercase letters, numbers, and hyphens")
- What happens when the chatbot displays a task list with many tags per task? (Frontend should display tags in a compact, scrollable format or truncate with "..." and show count)
- What happens when the backend API is unavailable when fetching tags? (System retries once after 2 seconds, then displays error message: "Unable to load task tags. Please try again.")
- What happens when a user says "show me work and home tasks" - does this mean AND or OR logic? (System uses AND logic by default, matching Phase 2 behavior: tasks must have BOTH tags)
- What happens when network latency is high and tag updates are slow? (Frontend shows loading indicator; system waits for response, retries once after 2 seconds if timeout, then displays success/failure feedback)
- What happens when a retry also fails after the 2-second delay? (Error message is shown to user with option to manually retry)
- What happens when a user asks for tags in different phrasings (e.g., "my labels", "my categories")? (Chatbot should recognize common synonyms for "tags" and handle appropriately)
- What happens when user says "tag this" but task context has been reset by a task-related command? (MCP server should ask for clarification: "Which task would you like to tag?")
- What happens when a user adds a new tag to a task, then immediately asks "what tags do I have?" - will they see the new tag? (Yes - cache is invalidated on tag operations, so the fresh list is fetched immediately)

## Requirements

### Functional Requirements

#### Phase 3 Frontend (Next.js Chat Interface)

- **FR-001**: Chat interface MUST display tags for each task shown in chatbot responses
- **FR-002**: Tags MUST be visually distinguished from task content (e.g., badges, pills, or colored labels)
- **FR-003**: Frontend MUST fetch and display user's available tags from the backend API when needed
- **FR-004**: Frontend MUST handle tag data in all task-related API responses (create, update, list, get)
- **FR-005**: Chat interface MUST display appropriate messages when tasks have no tags
- **FR-006**: Frontend MUST handle tag display gracefully when tasks have many tags (e.g., scrollable, truncated with count)
- **FR-007**: Frontend MUST show loading states when fetching or updating tags
- **FR-008**: Frontend MUST display error messages when tag operations fail
- **FR-009**: Frontend MUST retry failed tag-related API calls once after a 2-second delay before showing error to user

#### Phase 3 MCP Server (Natural Language Processing)

- **FR-010**: MCP server MUST interpret natural language commands for tag filtering (e.g., "show me work tasks")
- **FR-011**: MCP server MUST recognize various phrasings for tag filtering (e.g., "tasks tagged with X", "my X tasks", "show X tagged tasks")
- **FR-012**: MCP server MUST extract tag names from natural language commands for task creation (e.g., "tagged with work")
- **FR-013**: MCP server MUST support adding multiple tags in a single command (e.g., "tagged with work and urgent")
- **FR-014**: MCP server MUST interpret commands to add tags to existing tasks (e.g., "tag this with urgent")
- **FR-015**: MCP server MUST interpret commands to remove tags from tasks (e.g., "remove the urgent tag")
- **FR-016**: MCP server MUST interpret commands to list all user tags (e.g., "what tags do I have?", "list my tags")
- **FR-017**: MCP server MUST validate tag format before sending to backend API (lowercase, alphanumeric + hyphens, 1-50 chars)
- **FR-018**: MCP server MUST handle tag validation errors from backend and return user-friendly messages
- **FR-019**: MCP server MUST use AND logic when filtering by multiple tags (consistent with Phase 2)
- **FR-020**: MCP server MUST call backend GET /api/tasks/tags endpoint to retrieve user's tag list
- **FR-021**: MCP server MUST call backend GET /api/tasks?tags=X endpoint to filter tasks by tags
- **FR-022**: MCP server MUST send tags field when creating or updating tasks via backend API
- **FR-023**: MCP server MUST handle ambiguous tag-related commands by asking clarifying questions when confidence is below 70%
- **FR-024**: MCP server MUST maintain task context (for "this" references) until the next task-related command (show, list, create, filter) is issued
- **FR-025**: MCP server MUST retry failed backend API calls once after a 2-second delay before returning error to user
- **FR-026**: MCP server MUST log tag extraction errors and low-confidence interpretations (confidence <70%) for monitoring and model improvement

#### Phase 3 Backend (FastAPI Proxy/Adapter)

- **FR-027**: Phase 3 backend MUST proxy tag-related requests to the main backend (Phase 2)
- **FR-028**: Phase 3 backend MUST forward GET /api/tasks/tags requests to main backend
- **FR-029**: Phase 3 backend MUST forward GET /api/tasks?tags=X requests with tag parameters to main backend
- **FR-030**: Phase 3 backend MUST include tags field when forwarding task creation/update requests
- **FR-031**: Phase 3 backend MUST preserve tag validation errors from main backend and return them to MCP server
- **FR-032**: Phase 3 backend MUST maintain JWT authentication when proxying tag-related requests
- **FR-033**: Phase 3 backend MUST handle main backend errors gracefully and return appropriate error responses
- **FR-034**: Phase 3 backend MUST cache user tag lists (GET /api/tasks/tags responses) for 60 seconds per user
- **FR-035**: Phase 3 backend MUST invalidate cached tag list for a user when that user creates, updates, or deletes a task with tags
- **FR-036**: Phase 3 backend MUST log proxy errors and failed requests to main backend for monitoring and debugging

### Key Entities

- **Task (Enhanced)**: Existing entity from Phase 2 with tags support
  - **Tags**: Array of 0-10 tag names (lowercase alphanumeric + hyphens, 1-50 chars each)
  - **Relationships**: Tags are embedded in tasks as a PostgreSQL TEXT[] array
  - **Source**: Main backend (Phase 2) provides task data with tags

- **Chat Message**: Frontend representation of chatbot interactions
  - **Task Display**: Contains formatted task information including tags
  - **Tag Badges**: Visual components showing task tags
  - **Relationships**: Renders task data received from MCP server

- **MCP Command**: Natural language input from user
  - **Tag Extraction**: Identifies tag-related intent (filter, add, remove, list)
  - **Tag Parameters**: Extracted tag names from user input
  - **Validation**: Ensures tag format compliance before API calls

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can see tags displayed in the chat interface for all tasks within 500 milliseconds of task data loading
- **SC-002**: Natural language tag filtering commands (e.g., "show me work tasks") are correctly interpreted and executed with 85% or higher accuracy
- **SC-003**: Tag filtering via chat returns results in under 1 second for users with up to 1000 tasks
- **SC-004**: Users can create tasks with tags via natural language (e.g., "add task tagged with work") and tags are saved correctly 95% or more of the time
- **SC-005**: MCP server correctly extracts tag names from natural language commands with 90% or higher accuracy
- **SC-006**: Tag validation errors from backend are displayed to users with clear, actionable messages within 500 milliseconds
- **SC-007**: The chat interface remains responsive when displaying tasks with multiple tags (no UI lag or jank)
- **SC-008**: Users can view their full tag list via chat command ("what tags do I have?") with results returned in under 500 milliseconds (typically <100ms for cached responses)
- **SC-009**: Tag-related API calls through Phase 3 backend have less than 100ms additional latency compared to direct backend calls
- **SC-010**: Users report increased task organization efficiency - finding tagged tasks via chat is 30% faster than manual browsing (user survey)
- **SC-011**: MCP server asks for clarification on less than 15% of tag-related commands (indicating confidence threshold is appropriately calibrated)

## Assumptions

- Phase 2 backend API endpoints for tags are fully functional and tested (backend/routes/tasks.py confirms this)
- Phase 2 backend enforces all tag validation rules (max 10 tags, 1-50 chars, alphanumeric + hyphens)
- Phase 2 backend uses AND logic for multi-tag filtering (confirmed in backend API)
- Phase 3 frontend is a Next.js application with a chat interface component
- Phase 3 MCP server has natural language processing capabilities for interpreting user commands
- Phase 3 backend acts as a proxy/adapter to the main Phase 2 backend
- JWT authentication is already implemented and working across Phase 3 components
- Users are familiar with the concept of tags/labels for categorization
- Chat interface supports displaying formatted task information (not just plain text)
- MCP server can make authenticated HTTP requests to backend APIs
- Network connectivity between Phase 3 components is reliable

## Dependencies

- **Phase 2 Backend** (backend/): Provides tag functionality via REST API
  - GET /api/tasks/tags - List all user tags
  - GET /api/tasks?tags=X&tags=Y - Filter tasks by tags (AND logic)
  - POST /api/tasks - Create task with tags
  - PUT /api/tasks/{id} - Update task tags
- **PostgreSQL Database**: Stores task tags as TEXT[] array (already migrated in Phase 2)
- **Phase 3 Frontend**: Next.js chat interface with task display components
- **Phase 3 MCP Server**: Natural language processing for chatbot commands
- **Phase 3 Backend**: Proxy/adapter layer between MCP server and main backend
- **JWT Authentication**: Existing auth system for securing API calls

## Non-Goals

- Building new tag-related backend API endpoints (Phase 2 backend already provides all needed endpoints)
- Modifying database schema or migrations (Phase 2 already completed this)
- Implementing tag autocomplete in the chat interface (users type tags freely in natural language)
- Adding tag analytics or usage statistics in the chat interface
- Supporting tag renaming globally (this would require Phase 2 backend changes)
- Implementing tag color customization or visual styling beyond basic badges
- Creating a dedicated tag management UI (separate from chat commands)
- Supporting OR logic for multi-tag filtering (Phase 2 uses AND, must stay consistent)
- Building tag suggestions based on task content (AI-powered recommendations)
- Implementing bulk tag operations via chat (e.g., "tag all pending tasks with urgent")
- Creating tag hierarchies or tag categories
- Supporting tag sharing between users (tags remain user-private)
- Comprehensive logging of all tag operations (only errors and low-confidence cases are logged)

## Constraints

- **Phase 2 Backend API Contract**: Must use existing endpoints without modifications
- **Tag Validation Rules**: Must enforce Phase 2 rules (max 10 tags, 1-50 chars, format ^[a-z0-9-]+$)
- **AND Logic for Multi-Tag Filtering**: Must match Phase 2 behavior (task must have ALL specified tags)
- **JWT Authentication**: All API calls must include valid JWT tokens
- **User Isolation**: Tags are user-specific (inherited from task's user_id)
- **Natural Language Limitations**: MCP server interpretation accuracy depends on NLP model capabilities
- **No Database Direct Access**: Phase 3 components must go through backend APIs, not query database directly
- **Backward Compatibility**: Changes must not break existing Phase 3 chat functionality for non-tagged tasks
