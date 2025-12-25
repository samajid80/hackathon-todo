# Quickstart: Phase 3 Task Tags Integration

**Feature**: 001-phase3-task-tags
**Date**: 2025-12-24
**Purpose**: Manual testing scenarios for tag functionality in Phase 3 chatbot

## Prerequisites

1. Phase 2 backend running with tag support (already implemented)
2. Phase 3 backend deployed with cache service
3. Phase 3 MCP server deployed with tag tools
4. Phase 3 frontend deployed with tag display components
5. Test user account with JWT token

## Test Environment Setup

### 1. Verify Phase 2 Backend Endpoints

```bash
# Test GET /api/tasks/tags (should return empty array initially)
curl -H "Authorization: Bearer $JWT_TOKEN" \
  https://phase2-backend.railway.app/api/tasks/tags

# Expected: []

# Test GET /api/tasks with tags parameter
curl -H "Authorization: Bearer $JWT_TOKEN" \
  "https://phase2-backend.railway.app/api/tasks?tags=work"

# Expected: [] (no tasks with "work" tag yet)
```

### 2. Create Test Data (Phase 2 Backend)

```bash
# Create task with tags via Phase 2 API
curl -X POST -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "tags": ["home", "shopping"]}' \
  https://phase2-backend.railway.app/api/tasks

# Create task with work tag
curl -X POST -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Prepare presentation", "tags": ["work", "urgent"]}' \
  https://phase2-backend.railway.app/api/tasks

# Create task with no tags
curl -X POST -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Read book"}' \
  https://phase2-backend.railway.app/api/tasks

# Verify tags endpoint now returns tags
curl -H "Authorization: Bearer $JWT_TOKEN" \
  https://phase2-backend.railway.app/api/tasks/tags

# Expected: ["home", "shopping", "urgent", "work"]
```

## Manual Test Scenarios

### Scenario 1: Tag Display (P1 - User Story 1)

**Purpose**: Verify tags are displayed in chat interface

**Steps**:
1. Open Phase 3 frontend: https://hackathon-todo-phase3.vercel.app
2. Log in with test account
3. In chat, type: "show me my tasks"
4. Observe task list response

**Expected Results**:
- ✅ Each task displays its tags as colored badges
- ✅ "Buy groceries" shows [home] [shopping] badges
- ✅ "Prepare presentation" shows [work] [urgent] badges
- ✅ "Read book" shows no tag section (or "No tags")
- ✅ Tags are visually distinguished from task content
- ✅ Tags render within 500ms of message loading

**Acceptance**: All checkboxes pass

---

### Scenario 2: Natural Language Tag Filtering (P2 - User Story 2)

**Purpose**: Verify tag filtering via natural language commands

**Test Cases**:

#### 2A: Filter by single tag (explicit)
- **Input**: "show me tasks tagged with work"
- **Expected**: Returns "Prepare presentation" only
- **Verification**: No "Buy groceries" or "Read book" in results

#### 2B: Filter by single tag (implicit)
- **Input**: "show my work tasks"
- **Expected**: Returns "Prepare presentation" only
- **Verification**: System infers "work" tag from "work tasks"

#### 2C: Filter by multiple tags (AND logic)
- **Input**: "show me urgent work tasks"
- **Expected**: Returns "Prepare presentation" only
- **Verification**: Task must have BOTH "urgent" AND "work" tags

#### 2D: Filter by non-existent tag
- **Input**: "show tasks tagged with personal"
- **Expected**: "No tasks found with tag 'personal'"
- **Verification**: Friendly error message, not technical error

#### 2E: Clear filter
- **Input**: "show all tasks"
- **Expected**: Returns all 3 tasks (with and without tags)
- **Verification**: Tag filter is cleared

**Acceptance**: All test cases pass, response time <1s

---

### Scenario 3: Add Tags via Natural Language (P3 - User Story 3)

**Purpose**: Verify tag addition through chat commands

**Test Cases**:

#### 3A: Create task with tags (explicit)
- **Input**: "add a task to call dentist tagged with personal and health"
- **Expected**: Task created with tags ["personal", "health"]
- **Verification**: Confirmation message shows tags, task list displays badges

#### 3B: Add tag to existing task (context)
- **Setup**: Say "show my tasks", then user sees "Buy groceries"
- **Input**: "tag the first one with urgent"
- **Expected**: "Buy groceries" now has tags ["home", "shopping", "urgent"]
- **Verification**: Updated task shows all 3 tags

#### 3C: Add tag using "this" reference
- **Setup**: Say "show my tasks", then user sees task list
- **Input**: "tag this with important" (referring to last task)
- **Expected**: Last task gets "important" tag
- **Verification**: Context resolution works correctly

#### 3D: Context reset after list command
- **Setup**: User views a task, then says "show all tasks"
- **Input**: "tag this with urgent"
- **Expected**: Chatbot asks "Which task would you like to tag?"
- **Verification**: Context was reset by "show all tasks" command

#### 3E: Exceed tag limit
- **Setup**: Create task with 10 tags already
- **Input**: "add tag eleventh to this task"
- **Expected**: Error "Maximum 10 tags allowed per task"
- **Verification**: Validation enforced, user-friendly message

**Acceptance**: All test cases pass

---

### Scenario 4: View User's Tags (P4 - User Story 4)

**Purpose**: Verify tag list retrieval

**Test Cases**:

#### 4A: List all tags
- **Input**: "what tags do I have?"
- **Expected**: "You have 6 tags: health, home, personal, shopping, urgent, work"
- **Verification**: Alphabetically sorted, all unique tags listed

#### 4B: Cache performance
- **Setup**: Run "what tags do I have?" twice within 60 seconds
- **Expected**: Second request returns <100ms (cached)
- **Verification**: Check Phase 3 backend logs for cache hit

#### 4C: Cache invalidation
- **Setup**: Run "what tags do I have?", then add task with new tag "fitness"
- **Input**: "what tags do I have?"
- **Expected**: List now includes "fitness"
- **Verification**: Cache was invalidated on tag operation

#### 4D: No tags scenario
- **Setup**: Delete all tasks with tags
- **Input**: "list my tags"
- **Expected**: "You haven't created any tags yet"
- **Verification**: Empty state handled gracefully

**Acceptance**: All test cases pass, cache hit <100ms

---

### Scenario 5: Remove Tags (P5 - User Story 5)

**Purpose**: Verify tag removal through chat

**Test Cases**:

#### 5A: Remove single tag
- **Setup**: "Prepare presentation" has ["work", "urgent"]
- **Input**: "remove the urgent tag from this task"
- **Expected**: Task now has only ["work"]
- **Verification**: "urgent" removed, "work" preserved

#### 5B: Remove all tags
- **Input**: "remove all tags from this task"
- **Expected**: Task has no tags (empty array)
- **Verification**: All tags removed, no badges displayed

#### 5C: Remove non-existent tag
- **Input**: "remove the personal tag from this task"
- **Expected**: "This task doesn't have the 'personal' tag"
- **Verification**: Error message is user-friendly

**Acceptance**: All test cases pass

---

## Edge Case Testing

### Edge Case 1: Ambiguous Natural Language

**Input**: "show me tagged tasks"
**Expected**: Chatbot asks "Which tag would you like to filter by?"
**Verification**: Low confidence triggers clarification (<70%)

---

### Edge Case 2: Invalid Tag Format

**Input**: "add task tagged with URGENT!!!"
**Expected**: Error "Tags can only contain lowercase letters, numbers, and hyphens"
**Verification**: MCP server validates before calling Phase 2

---

### Edge Case 3: Many Tags Display

**Setup**: Create task with 8 tags
**Input**: "show my tasks"
**Expected**: First 5 tags shown as badges, "...+3 more" text
**Verification**: UI handles many tags gracefully, no layout break

---

### Edge Case 4: Backend Unavailable

**Setup**: Stop Phase 2 backend temporarily
**Input**: "what tags do I have?"
**Expected**: Loading indicator shows, retries after 2s, then error "Unable to load task tags. Please try again."
**Verification**: Retry logic works, user-friendly error shown

---

### Edge Case 5: Slow Network (Retry Logic)

**Setup**: Simulate slow network (e.g., browser devtools throttling)
**Input**: "add task tagged with slow"
**Expected**: Loading indicator shows, operation completes after retry
**Verification**: Single retry after 2s works correctly

---

## Performance Benchmarks

### Tag Display Performance (SC-001)
- **Metric**: Time to render tags in chat message
- **Target**: <500ms
- **Test**: Measure time from API response to tag badges visible
- **Tool**: Browser Performance tab

### Tag Filtering Performance (SC-003)
- **Metric**: Response time for filtered task list
- **Target**: <1s for 1000 tasks
- **Test**: Create 1000 test tasks, filter by tag, measure response
- **Tool**: curl with timing (-w "%{time_total}")

### Tag List Retrieval (SC-008)
- **Metric**: Response time for "what tags do I have?"
- **Target**: <100ms cached, <500ms cache miss
- **Test**: Run command twice, measure both times
- **Tool**: Phase 3 backend logs with timing

### MCP Extraction Accuracy (SC-002, SC-005)
- **Metric**: Command interpretation success rate
- **Target**: 85% success, 90% tag extraction accuracy
- **Test**: 100 natural language commands, count successes
- **Tool**: Manual testing with diverse phrasing

---

## Logging Verification

### Low-Confidence Logging (FR-026)

**Test**: Say ambiguous command "show tagged stuff"
**Expected Log**:
```json
{
  "level": "info",
  "message": "Low confidence tag extraction",
  "user_input": "show tagged stuff",
  "extracted_tags": [],
  "confidence": 0.45,
  "user_id": "user-uuid"
}
```

### Error Logging (FR-036)

**Test**: Stop Phase 2 backend, try tag operation
**Expected Log**:
```json
{
  "level": "error",
  "message": "Failed to fetch tags from Phase 2",
  "user_id": "user-uuid",
  "error": "Connection refused",
  "phase2_endpoint": "https://phase2-backend.railway.app"
}
```

---

## Acceptance Criteria Checklist

**Before marking feature complete, verify**:

- [ ] All P1 scenarios pass (Tag Display)
- [ ] All P2 scenarios pass (Tag Filtering)
- [ ] All P3 scenarios pass (Add Tags)
- [ ] All P4 scenarios pass (View Tags)
- [ ] All P5 scenarios pass (Remove Tags)
- [ ] All edge cases handled gracefully
- [ ] Performance benchmarks meet targets
- [ ] Logging works as specified
- [ ] Zero modifications to Phase 2 backend code
- [ ] Phase 2 tests still pass (backward compatibility)

**Quickstart Complete**: All manual test scenarios documented and ready for execution.
