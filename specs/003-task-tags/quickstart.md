# Quickstart: Task Tags/Categories Testing

**Feature**: 003-task-tags
**Date**: 2025-12-23
**Purpose**: Manual test scenarios and acceptance criteria for validating task tags implementation

## Prerequisites

1. **Backend Running**:
   ```bash
   cd backend
   uvicorn backend.main:app --reload --port 8000
   ```

2. **Frontend Running**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Database Migrated**:
   ```bash
   psql "$DATABASE_URL" < backend/migrations/005_add_tags_to_tasks.sql
   ```

4. **Test User Account**:
   - Email: `test@example.com`
   - Password: `testpassword123`

## Test Scenarios

### Scenario 1: Create Task with Tags (P1)

**Objective**: Verify users can add tags when creating a task

**Steps**:
1. Navigate to http://localhost:3000/tasks
2. Click "Create New Task" button
3. Enter title: "Complete project proposal"
4. In tag input, type "work" and press Enter
5. Type "urgent" and press Enter
6. Click "Create Task"

**Expected Result**:
- ✅ Task appears in task list
- ✅ Task card displays two tags: "work" and "urgent"
- ✅ Tags are displayed as styled badges/chips
- ✅ Network request shows tags: `["work", "urgent"]`

**API Validation**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project proposal",
    "tags": ["work", "urgent"]
  }'
```

**Expected Response**:
```json
{
  "id": "...",
  "title": "Complete project proposal",
  "tags": ["work", "urgent"],
  ...
}
```

---

### Scenario 2: Tag Autocomplete (P1)

**Objective**: Verify tag autocomplete suggests previously used tags

**Setup**:
- Create task with tags: ["work", "personal", "shopping"]

**Steps**:
1. Click "Create New Task"
2. Start typing "wo" in tag input
3. Observe autocomplete dropdown

**Expected Result**:
- ✅ Dropdown appears showing "work"
- ✅ Suggestions update as you type
- ✅ Selecting suggestion adds tag
- ✅ Already-selected tags don't appear in suggestions
- ✅ Autocomplete appears within 300ms

**Advanced Test**:
- Type "p" → Should show "personal"
- Add "personal" → Start typing "p" again
- Should NOT show "personal" (already selected)

---

### Scenario 3: Tag Validation (P1)

**Objective**: Verify tag validation rules are enforced

**Test Cases**:

| Input | Expected Behavior |
|-------|------------------|
| "Work" | ✅ Accepted, converted to "work" |
| "  urgent  " | ✅ Accepted, trimmed to "urgent" |
| "work@home" | ❌ Error: "Tags can only contain lowercase letters, numbers, and hyphens" |
| "URGENT!!!" | ❌ Error: "Tags can only contain lowercase letters, numbers, and hyphens" |
| "" (empty) | ❌ Ignored or error: "Tag cannot be empty" |
| "a" | ✅ Accepted (1 char is valid) |
| "a".repeat(51) | ❌ Error: "Tag must be 1-50 characters long" |
| Add 11th tag | ❌ Error: "Maximum 10 tags allowed per task" |

**Steps**:
1. Create task
2. Try each invalid input above
3. Verify error message appears
4. Verify tag is NOT added

**API Validation**:
```bash
# Test invalid characters
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "tags": ["urgent!!!"]}'

# Expected: 400 Bad Request with validation error
```

---

### Scenario 4: Filter Tasks by Single Tag (P2)

**Objective**: Verify filtering tasks by one tag

**Setup**:
- Create 3 tasks:
  1. "Task 1" with tags: ["work"]
  2. "Task 2" with tags: ["personal"]
  3. "Task 3" with tags: ["work", "urgent"]

**Steps**:
1. Navigate to task list
2. Select "work" tag filter
3. Observe task list

**Expected Result**:
- ✅ Only Task 1 and Task 3 visible
- ✅ Task 2 (personal) is hidden
- ✅ Filter UI shows "work" as active filter
- ✅ Results appear within 1 second

**API Validation**:
```bash
curl http://localhost:8000/api/tasks?tags=work \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response**:
```json
{
  "items": [
    {"title": "Task 1", "tags": ["work"]},
    {"title": "Task 3", "tags": ["work", "urgent"]}
  ],
  "total": 2,
  ...
}
```

---

### Scenario 5: Filter Tasks by Multiple Tags (AND Logic) (P2)

**Objective**: Verify filtering by multiple tags uses AND logic

**Setup**:
- Create 4 tasks:
  1. "Task A" with tags: ["work"]
  2. "Task B" with tags: ["urgent"]
  3. "Task C" with tags: ["work", "urgent"]
  4. "Task D" with tags: ["work", "personal"]

**Steps**:
1. Navigate to task list
2. Select "work" tag filter
3. Additionally select "urgent" tag filter
4. Observe task list

**Expected Result**:
- ✅ Only Task C visible (has BOTH "work" AND "urgent")
- ✅ Task A, B, D are hidden
- ✅ Filter UI shows both "work" and "urgent" as active
- ✅ Results appear within 1 second

**API Validation**:
```bash
curl "http://localhost:8000/api/tasks?tags=work&tags=urgent" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response**:
```json
{
  "items": [
    {"title": "Task C", "tags": ["work", "urgent"]}
  ],
  "total": 1,
  ...
}
```

---

### Scenario 6: Clear Tag Filter (P2)

**Objective**: Verify users can clear tag filters

**Setup**:
- Apply tag filter "work"
- Task list shows filtered results

**Steps**:
1. Click "Clear Filters" or remove "work" filter chip
2. Observe task list

**Expected Result**:
- ✅ All tasks visible again
- ✅ Filter UI shows no active filters
- ✅ URL updates to remove filter parameter

---

### Scenario 7: View All Used Tags (P3)

**Objective**: Verify users can see all unique tags they've used

**Setup**:
- Create tasks with tags: ["work", "personal", "urgent", "work", "shopping"]

**Steps**:
1. Navigate to tag list view or tag filter dropdown
2. Observe tag list

**Expected Result**:
- ✅ Tags appear: ["personal", "shopping", "urgent", "work"] (alphabetically sorted)
- ✅ Each tag appears only once (deduplicated)
- ✅ No tags from other users visible
- ✅ Tag list loads within 500ms

**API Validation**:
```bash
curl http://localhost:8000/api/tasks/tags \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response**:
```json
["personal", "shopping", "urgent", "work"]
```

---

### Scenario 8: Edit Task Tags (P1)

**Objective**: Verify users can add/remove tags from existing tasks

**Setup**:
- Create task "Test Task" with tags: ["work"]

**Steps**:
1. Click task to open detail/edit view
2. Add tag "urgent"
3. Remove tag "work"
4. Save changes

**Expected Result**:
- ✅ Task now has tags: ["urgent"]
- ✅ "work" tag no longer visible
- ✅ Changes persist after page refresh

**API Validation**:
```bash
curl -X PUT http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tags": ["urgent"]}'
```

---

### Scenario 9: Tag Normalization (P1)

**Objective**: Verify tags are automatically normalized

**Test Cases**:

| Input | Stored As | Displayed As |
|-------|-----------|--------------|
| "Work" | "work" | "work" |
| "URGENT" | "urgent" | "urgent" |
| "  home  " | "home" | "home" |
| ["Work", "work", "WORK"] | ["work"] | "work" (deduplicated) |

**Steps**:
1. Create task with tag "Work" (capital W)
2. Check task card
3. Check API response

**Expected Result**:
- ✅ Tag displayed as "work" (lowercase)
- ✅ API returns `["work"]`
- ✅ Duplicate "work" entries prevented

---

### Scenario 10: Empty Tag Filter (Edge Case) (P2)

**Objective**: Verify appropriate message when no tasks match filter

**Setup**:
- No tasks have tag "nonexistent"

**Steps**:
1. Filter by tag "nonexistent"
2. Observe task list

**Expected Result**:
- ✅ Empty state displayed
- ✅ Message: "No tasks found with tag 'nonexistent'"
- ✅ Option to clear filter visible
- ✅ No errors in console

---

### Scenario 11: Chatbot Tag Commands (P4)

**Objective**: Verify chatbot can interpret natural language tag commands

**Prerequisites**: Phase3 chatbot deployed

**Test Cases**:

| Command | Expected Action |
|---------|----------------|
| "show me all work tasks" | Filter tasks by "work" tag |
| "add a task to buy groceries tagged with home" | Create task with "home" tag |
| "show me urgent and work tasks" | Filter by both "urgent" and "work" (AND) |
| "add the tag urgent to this task" | Add "urgent" tag to current task |

**Steps**:
1. Open chatbot interface
2. Send command: "show me all work tasks"
3. Observe response

**Expected Result**:
- ✅ Chatbot displays tasks with "work" tag
- ✅ Response indicates filter applied
- ✅ 90%+ accuracy in tag interpretation

---

## Performance Tests

### Test 1: Tag Autocomplete Latency

**Objective**: Verify autocomplete appears within 300ms

**Setup**:
- Create 50 tasks with various tags (10-20 unique tags)

**Steps**:
1. Open network DevTools
2. Start typing in tag input
3. Measure time to autocomplete appearance

**Expected Result**:
- ✅ Autocomplete suggestions appear <300ms
- ✅ Filtering is instant (client-side)

---

### Test 2: Tag Filtering Performance

**Objective**: Verify filtering is fast even with many tasks

**Setup**:
- Create 1000 tasks with various tags

**Steps**:
1. Open network DevTools
2. Apply tag filter "work"
3. Measure API response time

**Expected Result**:
- ✅ Results appear within 1 second
- ✅ API response <500ms
- ✅ GIN index used (check EXPLAIN ANALYZE)

**Database Verification**:
```sql
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'xyz' AND tags @> ARRAY['work'];

-- Expected: "Index Scan using idx_tasks_tags"
```

---

### Test 3: Tag List Endpoint Performance

**Objective**: Verify tag list endpoint is fast

**Setup**:
- Create 100 tasks with 50 unique tags

**Steps**:
1. Call GET /api/tasks/tags
2. Measure response time

**Expected Result**:
- ✅ Response time <500ms
- ✅ Tags sorted alphabetically
- ✅ Deduplicated correctly

---

## Acceptance Checklist

### P1 - Add Tags to Tasks

- [ ] Can create task with tags
- [ ] Can edit task to add tags
- [ ] Can edit task to remove tags
- [ ] Tag autocomplete works
- [ ] Tags normalized to lowercase
- [ ] Whitespace trimmed
- [ ] Duplicates removed automatically
- [ ] Max 10 tags enforced
- [ ] Tag format validated (alphanumeric + hyphens)
- [ ] Error messages clear and actionable

### P2 - Filter Tasks by Tags

- [ ] Can filter by single tag
- [ ] Can filter by multiple tags (AND logic)
- [ ] Can clear tag filters
- [ ] Filtering results <1 second
- [ ] Empty state shown when no matches
- [ ] Filter combines with status/sorting

### P3 - View All Used Tags

- [ ] Tag list shows unique tags
- [ ] Tags sorted alphabetically
- [ ] Tag list updates when tags added/removed
- [ ] Tag list scoped per user (no other users' tags)
- [ ] Tag list loads <500ms

### P4 - Chatbot Integration

- [ ] Chatbot interprets "show me work tasks"
- [ ] Chatbot interprets "add task tagged with X"
- [ ] Chatbot interprets multiple tag filters
- [ ] 90%+ interpretation accuracy

## Troubleshooting

### Issue: Tags not saving

**Check**:
1. Verify migration ran: `SELECT column_name FROM information_schema.columns WHERE table_name = 'tasks' AND column_name = 'tags';`
2. Check backend logs for validation errors
3. Verify JWT token includes user_id

### Issue: Tag autocomplete not working

**Check**:
1. Verify GET /api/tasks/tags endpoint returns tags
2. Check browser console for JavaScript errors
3. Verify debounce function working

### Issue: Tag filtering slow

**Check**:
1. Verify GIN index exists: `\d tasks` in psql
2. Run EXPLAIN ANALYZE on query
3. Check task count (should be <10,000 for good performance)

## Next Steps

After manual testing:
1. Write automated tests based on scenarios above
2. Run performance benchmarks
3. Document any issues found
4. Update implementation if needed
