# Feature Specification: Task Tags/Categories

**Feature Branch**: `003-task-tags`
**Created**: 2025-12-23
**Status**: Draft
**Input**: User description: "Add tags/categories feature to allow users to assign labels like 'work', 'home', 'urgent' to tasks. Users should be able to filter tasks by one or more tags. Store tags as PostgreSQL TEXT[] array in tasks table with validation: max 10 tags per task, each tag 1-50 characters, lowercase, alphanumeric + hyphens only. Add GET /api/tasks/tags endpoint to list all unique tags used by the user. Update GET /api/tasks endpoint to support tags query parameter for filtering (AND logic - task must have ALL specified tags). Frontend should have TagSelector component with autocomplete showing existing tags, tag display on task cards, and tag filtering in TaskFilters component. Phase3 chatbot should automatically support natural language commands like 'show me all work tasks' or 'add a task tagged with personal'."

## User Scenarios & Testing

### User Story 1 - Add Tags to Tasks (Priority: P1)

As a user, I want to categorize my tasks with tags (like "work", "home", "urgent") so that I can organize tasks by context and quickly find related tasks.

**Why this priority**: This is the foundation of the feature - without the ability to add tags, no other functionality works. It delivers immediate value by allowing users to organize their tasks.

**Independent Test**: Can be fully tested by creating a new task with tags and verifying the tags are saved and displayed on the task card. Delivers immediate organizational value even without filtering.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I add tags "work" and "urgent" to the task, **Then** the task is saved with both tags and displays them on the task card
2. **Given** I am editing an existing task, **When** I add the tag "home", **Then** the tag is added to the task and persisted
3. **Given** I am editing a task with existing tags, **When** I remove a tag, **Then** the tag is removed from the task and no longer displayed
4. **Given** I have previously used tags like "work" and "personal", **When** I start typing a tag name, **Then** I see suggestions for existing tags that match my input
5. **Given** I am adding tags to a task, **When** I type a tag name, **Then** the system automatically converts it to lowercase for consistency

---

### User Story 2 - Filter Tasks by Tags (Priority: P2)

As a user, I want to filter my task list by one or more tags so that I can focus on tasks in a specific category or context (e.g., all "work" tasks, or tasks that are both "urgent" and "home").

**Why this priority**: Filtering is the primary use case for tags - it allows users to quickly narrow down their task list. This must work after tag creation is stable.

**Independent Test**: Can be tested by creating tasks with various tags and verifying that filtering by single or multiple tags returns only matching tasks. Delivers value by enabling focused task views.

**Acceptance Scenarios**:

1. **Given** I have tasks tagged with "work", "home", and "urgent", **When** I filter by "work", **Then** I see only tasks tagged with "work"
2. **Given** I have tasks with multiple tags, **When** I filter by both "work" AND "urgent", **Then** I see only tasks that have BOTH tags
3. **Given** I have filtered tasks by "work", **When** I clear the filter, **Then** I see all my tasks again
4. **Given** I have no tasks matching a tag filter, **When** I apply the filter, **Then** I see an empty list with a message indicating no matches
5. **Given** I am viewing filtered tasks, **When** I create a new task with the active filter tags, **Then** the new task appears in the filtered view

---

### User Story 3 - View All Used Tags (Priority: P3)

As a user, I want to see a list of all tags I've used across my tasks so that I can discover what categories I've created and reuse them consistently.

**Why this priority**: This is a convenience feature that improves UX but isn't critical for core functionality. Users can still manually type tag names without this feature.

**Independent Test**: Can be tested by creating tasks with various tags and verifying the tag list displays all unique tags. Delivers value by helping users maintain consistent tag naming.

**Acceptance Scenarios**:

1. **Given** I have created tasks with tags "work", "home", and "urgent", **When** I view my tag list, **Then** I see all three tags listed alphabetically
2. **Given** I have tasks with duplicate tags (e.g., multiple tasks tagged "work"), **When** I view my tag list, **Then** each tag appears only once
3. **Given** I delete all tasks with a specific tag, **When** I view my tag list, **Then** that tag no longer appears in the list
4. **Given** I have used a tag and then removed it from all tasks, **When** I view my tag list, **Then** the tag no longer appears

---

### User Story 4 - Natural Language Tag Commands (Priority: P4)

As a user of the chatbot interface, I want to use natural language to add tags and filter by tags (e.g., "show me all work tasks" or "add a task tagged with personal") so that I can manage tagged tasks conversationally.

**Why this priority**: This enhances the chatbot experience but depends on the core tag functionality being stable. It's an additive feature for Phase3 users only.

**Independent Test**: Can be tested by issuing natural language commands to the chatbot and verifying it correctly interprets tag-related requests. Delivers value by making tag management more intuitive for chatbot users.

**Acceptance Scenarios**:

1. **Given** I am chatting with the bot, **When** I say "show me all work tasks", **Then** the bot displays tasks filtered by the "work" tag
2. **Given** I am creating a task via chat, **When** I say "add a task to buy groceries tagged with home", **Then** the bot creates a task with the "home" tag
3. **Given** I am chatting with the bot, **When** I say "show me urgent and work tasks", **Then** the bot displays tasks that have both "urgent" and "work" tags
4. **Given** I am editing a task via chat, **When** I say "add the tag urgent to this task", **Then** the bot adds the "urgent" tag to the current task

---

### Edge Cases

- What happens when a user tries to add more than 10 tags to a single task? (System must reject and display error: "Maximum 10 tags allowed per task")
- What happens when a user tries to add a tag with invalid characters (e.g., "work@home" or "URGENT!!!")? (System must reject and display error: "Tags can only contain lowercase letters, numbers, and hyphens")
- What happens when a user tries to add a tag longer than 50 characters? (System must reject and display error: "Tag must be 1-50 characters long")
- What happens when a user tries to add a duplicate tag to the same task (e.g., "work" twice)? (System must deduplicate automatically and store only one instance)
- What happens when a user filters by a tag that doesn't exist? (System displays empty list with message "No tasks found with tag '[tagname]'")
- What happens when a user has thousands of unique tags? (System should still perform efficiently, though UX may degrade for tag autocomplete)
- What happens when a user adds whitespace around a tag (e.g., "  work  ")? (System must trim whitespace automatically)
- What happens when a user tries to add an empty tag? (System must reject and display error: "Tag cannot be empty")

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow users to assign zero or more tags to any task
- **FR-002**: System MUST enforce a maximum of 10 tags per task
- **FR-003**: System MUST validate tag format: 1-50 characters, lowercase letters, numbers, and hyphens only
- **FR-004**: System MUST automatically convert tags to lowercase for consistency
- **FR-005**: System MUST automatically trim leading and trailing whitespace from tags
- **FR-006**: System MUST deduplicate tags within a single task (same tag cannot appear twice)
- **FR-007**: System MUST persist tags with the task and retrieve them when displaying the task
- **FR-008**: System MUST display tags visually on task cards in the task list and task detail views
- **FR-009**: Users MUST be able to add tags when creating a new task
- **FR-010**: Users MUST be able to add, modify, or remove tags when editing an existing task
- **FR-011**: System MUST provide tag input suggestions based on previously used tags (autocomplete)
- **FR-012**: System MUST allow users to filter tasks by one or more tags
- **FR-013**: When filtering by multiple tags, system MUST use AND logic (task must have ALL specified tags)
- **FR-014**: System MUST provide an endpoint or interface to retrieve all unique tags used by the authenticated user
- **FR-015**: The list of user tags MUST be sorted alphabetically
- **FR-016**: System MUST remove a tag from the user's tag list when it's no longer used on any task
- **FR-017**: Tag filtering MUST be clearable to return to unfiltered view
- **FR-018**: System MUST display appropriate messages when no tasks match the selected tag filter
- **FR-019**: Chatbot interface MUST interpret natural language commands for tag filtering (e.g., "show me work tasks")
- **FR-020**: Chatbot interface MUST interpret natural language commands for adding tags to tasks (e.g., "tag this with urgent")
- **FR-021**: System MUST validate tags before saving and return clear error messages for invalid tags
- **FR-022**: System MUST maintain user isolation - users can only see and filter by their own tags

### Key Entities

- **Task Tag**: A label assigned to a task for categorization purposes
  - **Tag Name**: Lowercase alphanumeric string with hyphens (1-50 chars)
  - **Association**: Linked to one or more tasks
  - **Ownership**: Scoped to a specific user (no shared tags between users)

- **Task**: Existing entity enhanced with tag support
  - **Tags**: Collection of zero to ten tag names
  - **Relationships**: Each task can have multiple tags, each tag can be on multiple tasks (many-to-many conceptually)

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can add tags to a task in under 10 seconds (including autocomplete selection)
- **SC-002**: Tag autocomplete suggestions appear within 300 milliseconds of typing
- **SC-003**: Task filtering by tags returns results in under 1 second even with 1000+ tasks
- **SC-004**: 95% of tag input operations succeed on first attempt (invalid format errors under 5%)
- **SC-005**: Users can filter tasks by up to 5 tags simultaneously without performance degradation
- **SC-006**: Tag validation errors provide clear, actionable feedback to users
- **SC-007**: The tag list endpoint returns all user tags in under 500 milliseconds
- **SC-008**: System supports at least 100 unique tags per user without performance issues
- **SC-009**: Chatbot correctly interprets tag-related natural language commands with 90%+ accuracy
- **SC-010**: Task organization improves - users report finding tasks 40% faster using tag filters (user survey)

## Assumptions

- Users will create a moderate number of unique tags (expected: 10-50 tags per active user)
- Tag names will typically be short, common words (average: 5-10 characters)
- Most tasks will have 1-3 tags (rarely approaching the 10-tag limit)
- The existing task data model can be enhanced to include a tags field
- User authentication and authorization are already in place
- The chatbot interface (Phase3) can access the same backend API as the web interface
- Tag filtering will be a common operation (comparable frequency to status filtering)
- Database performance is sufficient to handle array-based tag storage and querying
- No need for hierarchical tags or tag relationships (flat tag structure)
- Tags are user-specific (no global/shared tag taxonomy)

## Dependencies

- Existing task management system (Phase2 backend and frontend)
- User authentication system (to scope tags per user)
- Database system capable of storing array/list data types
- Chatbot interface framework (Phase3) for natural language interpretation

## Non-Goals

- Tag sharing between users or teams (each user has their own private tag vocabulary)
- Tag hierarchies or categories (all tags are flat/equal)
- Tag analytics or insights (e.g., "most used tags", "tag trends")
- Tag renaming globally (if user wants to rename a tag, they must edit each task individually)
- Tag color customization or visual styling (tags use default system styling)
- Tag-based permissions or access control
- Bulk tag operations (e.g., "add tag 'urgent' to all pending tasks")
- Tag suggestions based on task content (AI-powered tag recommendations)
