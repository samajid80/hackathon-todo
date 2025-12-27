# Quickstart: ChatKit Migration Testing

**Feature**: 003-chatkit-migration
**Purpose**: Manual testing scenarios for validating ChatKit integration

---

## Prerequisites

### Environment Setup

1. **Backend Running**:
   ```bash
   cd phase3-backend
   source .venv/bin/activate  # or use uv
   uvicorn app.main:app --reload --port 8001
   ```

2. **Frontend Running**:
   ```bash
   cd phase3-frontend
   npm run dev
   # Opens on http://localhost:3001
   ```

3. **Phase 2 Backend Running** (for MCP tools):
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

4. **MCP Server Running**:
   ```bash
   cd phase3-mcp-server
   python -m app.main
   # Runs on http://localhost:8002
   ```

5. **Environment Variables Configured**:
   - `OPENAI_API_KEY` set in phase3-backend/.env
   - `DATABASE_URL` pointing to Neon PostgreSQL
   - `JWT_SECRET` matching across all services

---

## Test Scenario 1: User Authentication Flow (P2)

**Objective**: Verify JWT token integration with ChatKit session creation

### Steps

1. Navigate to http://localhost:3001
2. Click "Sign Up" or "Login"
3. Enter credentials (test@example.com / password123)
4. Verify redirect to chat page

### Expected Results

✅ Better-Auth JWT token issued (check browser DevTools → Application → Cookies → `phase3-hackathon-todo.session-token`)
✅ Chat page loads without errors
✅ ChatKit component renders (chat interface visible)

### Failure Scenarios

❌ 401 Unauthorized: JWT token not generated
❌ 403 Forbidden: JWT secret mismatch between services
❌ ChatKit not loading: Check browser console for CDN script errors

---

## Test Scenario 2: Create Task via Natural Language (P1)

**Objective**: Verify ChatKit → OpenAI → MCP → Phase 2 API flow

### Steps

1. In chat interface, type: `"Add a task to buy groceries tomorrow"`
2. Press Send
3. Wait for assistant response

### Expected Results

✅ User message appears in chat (blue bubble, right-aligned)
✅ Assistant response appears within 5 seconds (gray bubble, left-aligned)
✅ Response confirms task creation: "Task 'buy groceries' created successfully with due date [tomorrow's date]"
✅ Database check:
   ```sql
   SELECT * FROM tasks WHERE title = 'buy groceries' ORDER BY created_at DESC LIMIT 1;
   ```
   Should return the created task with tomorrow's due_date

### Progressive Streaming Check

- Watch for incremental text appearing (not all at once)
- Partial responses should render progressively

### Failure Scenarios

❌ No response after 10 seconds: Check OpenAI API key, rate limits
❌ Error "Could not create task": Check MCP server logs, Phase 2 backend connectivity
❌ Task not in database: Check user_id isolation, MCP tool HTTP calls

---

## Test Scenario 3: List Tasks (P1)

**Objective**: Verify task retrieval and display

### Steps

1. Create 3 tasks first:
   - "Buy groceries"
   - "Call mom"
   - "Finish report"
2. In chat, type: `"What are my tasks?"`
3. Wait for response

### Expected Results

✅ Assistant lists all 3 tasks
✅ Custom widget displays tasks (if implemented)
✅ Response includes task titles and statuses

### Alternative Queries to Test

- "Show my incomplete tasks"
- "What's on my todo list?"
- "List my pending tasks"

All should return same result

### Failure Scenarios

❌ Shows other users' tasks: User isolation broken
❌ Empty list with tasks in DB: MCP client not filtering by user_id
❌ Timeout: Check Phase 2 backend `/api/{user_id}/tasks` endpoint

---

## Test Scenario 4: Complete Task (P1)

**Objective**: Verify task status updates

### Steps

1. List tasks to see available tasks
2. Type: `"Mark 'buy groceries' as done"`
3. Wait for confirmation
4. Type: `"Show my completed tasks"`

### Expected Results

✅ Assistant confirms: "Task 'buy groceries' marked as completed"
✅ Task appears in completed list
✅ Database check:
   ```sql
   SELECT completed FROM tasks WHERE title = 'buy groceries';
   ```
   Should return `true`

### Failure Scenarios

❌ "Task not found": Check task title matching logic
❌ Multiple tasks matched: Ambiguity resolution should trigger

---

## Test Scenario 5: Conversation History Persistence (P3)

**Objective**: Verify session-scoped conversation history

### Steps

1. Send message: "Add task to water plants"
2. Wait for response
3. Refresh browser (F5)
4. Verify chat history still visible
5. Send message: "What did I just add?"

### Expected Results

✅ Previous messages visible after refresh
✅ Assistant remembers context: "You added a task to water plants"
✅ Database check:
   ```sql
   SELECT * FROM conversations WHERE user_id = '[test-user-id]' ORDER BY updated_at DESC LIMIT 1;
   SELECT * FROM messages WHERE conversation_id = '[conversation-id]' ORDER BY created_at ASC;
   ```
   Should show both user and assistant messages

### Session Expiry Test

1. Logout (clears JWT session)
2. Login again
3. Open chat

Expected: No previous conversation history (clean slate)

---

## Test Scenario 6: Update Task (P1)

**Objective**: Verify task modification

### Steps

1. Create task: "Review proposal"
2. Update: "Change the deadline for 'review proposal' to next Friday"
3. Verify update

### Expected Results

✅ Assistant confirms update
✅ Database shows updated due_date

---

## Test Scenario 7: Delete Task with Confirmation (P1)

**Objective**: Verify deletion requires confirmation

### Steps

1. Create task: "Delete this task"
2. Type: "Delete the task about 'delete this task'"
3. Wait for confirmation prompt
4. Respond: "Yes, delete it"
5. Verify deletion

### Expected Results

✅ Assistant asks for confirmation first
✅ After confirming, task is deleted
✅ Database shows task removed

### Test Cancellation

Repeat but respond "No" to confirmation
Expected: Task NOT deleted

---

## Test Scenario 8: MCP Tag Extraction (P4)

**Objective**: Verify intelligent tag extraction

### Steps

1. Type: "Add task to meet with marketing team about Q1 campaign"
2. Wait for response
3. Check task tags

### Expected Results

✅ Task created with relevant tags: ["work", "marketing", "planning"]
✅ Database:
   ```sql
   SELECT tags FROM tasks WHERE title ILIKE '%marketing%' ORDER BY created_at DESC LIMIT 1;
   ```
   Should return array with extracted tags

### Graceful Degradation Test

Stop MCP server, create task
Expected: Task created without tags, no error to user

---

## Test Scenario 9: Error Handling (Preservation)

**Objective**: Verify graceful error messages

### Test Cases

1. **OpenAI API Failure**: Disconnect internet, send message
   Expected: "I'm having trouble connecting. Please try again."

2. **Invalid Task Reference**: "Complete task XYZ123"
   Expected: "I couldn't find a task with that description. Could you be more specific?"

3. **Rate Limit**: Send 10 messages rapidly
   Expected: "You're sending messages too quickly. Please wait a moment."

---

## Test Scenario 10: Concurrent Users (SC-010)

**Objective**: Verify 100+ concurrent user support

### Steps

1. Open 3 browser windows (incognito for different sessions)
2. Login with different users in each
3. Send messages simultaneously from all windows

### Expected Results

✅ Each user sees only their own conversation
✅ No message cross-contamination
✅ All responses complete within 5 seconds

### Load Testing (Optional)

Use tool like k6 or locust to simulate 100 concurrent users

---

## Test Scenario 11: Custom Theming (SC-007)

**Objective**: Verify ChatKit matches Phase 3 design

### Visual Checks

✅ User messages: Blue background (#2563eb / blue-600)
✅ Assistant messages: Light gray background (#f3f4f6 / gray-100)
✅ Text: Dark gray (#111827 / gray-900)
✅ Rounded corners match Tailwind rounded-lg (0.5rem)
✅ Chat container height: 600px
✅ Overall aesthetic consistent with existing Phase 3 pages

---

## Test Scenario 12: Regression Testing (SC-008)

**Objective**: Ensure Phase 2 functionality unchanged

### Steps

1. Navigate to Phase 2 frontend (http://localhost:3000)
2. Login
3. Test all Phase 2 features:
   - Create task via form
   - Mark complete via checkbox
   - Filter by status
   - Delete task

### Expected Results

✅ All Phase 2 features work identically
✅ No errors in browser console or backend logs
✅ Database schema unchanged for tasks/users tables

---

## Performance Benchmarks

### Response Time (SC-009, FR-022)

Measure from send to first response character:

| Operation | Target | Acceptable |
|-----------|--------|------------|
| Simple query ("list tasks") | <2s | <5s |
| Task creation | <3s | <5s |
| Complex query with MCP tools | <4s | <5s |

### Database Query Performance

```sql
EXPLAIN ANALYZE
SELECT * FROM messages
WHERE conversation_id = '[uuid]' AND user_id = '[user-id]'
ORDER BY created_at ASC
LIMIT 20;
```

Expected: Index scan on `(conversation_id, created_at)`, <10ms execution

---

## Debugging Checklist

### ChatKit Component Not Loading

1. Check browser console for CDN script errors
2. Verify ChatKit.js loaded: `https://cdn.platform.openai.com/deployments/chatkit/chatkit.js`
3. Check React errors in console
4. Verify control object from useChatKit is not null

### Authentication Failures

1. Check JWT token in cookies
2. Verify `/api/chatkit/session` returns 200 with client_secret
3. Check phase3-backend logs for JWT validation errors
4. Verify JWT_SECRET matches across services

### No Response from Assistant

1. Check phase3-backend logs for OpenAI API errors
2. Verify OPENAI_API_KEY is set and valid
3. Check MCP server is running (http://localhost:8002/health)
4. Verify Phase 2 backend is running (http://localhost:8000/docs)

### Conversation History Not Persisting

1. Check database for conversation row with session_id
2. Verify messages are being saved
3. Check session_id mapping logic in ChatKitServer

---

## Success Criteria Validation

After completing all test scenarios, verify all success criteria from spec.md:

- [ ] **SC-001**: ChatKit components render correctly ✅
- [ ] **SC-002**: All task operations work ✅
- [ ] **SC-003**: Authentication integrates seamlessly ✅
- [ ] **SC-004**: Conversation history persists ✅
- [ ] **SC-005**: MCP tool integration works ✅
- [ ] **SC-006**: Progressive JSON streaming works ✅
- [ ] **SC-007**: Custom theming applied ✅
- [ ] **SC-008**: No Phase 2 regressions ✅
- [ ] **SC-009**: Same or better workflow time ✅
- [ ] **SC-010**: 100+ concurrent users supported ✅

---

## Automated Testing

### Unit Tests (Backend)

```bash
cd phase3-backend
pytest tests/test_chatkit_server.py -v
```

### Integration Tests (Full Stack)

```bash
cd phase3-frontend
npm run test:e2e
```

### Load Tests

```bash
# Using k6
k6 run tests/load/concurrent-users.js
```

---

## Cleanup After Testing

```sql
-- Clear test conversations
DELETE FROM conversations WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE 'test%@example.com'
);

-- Clear test tasks
DELETE FROM tasks WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE 'test%@example.com'
);
```

---

## Production Readiness Checklist

Before deploying to Railway/Vercel:

- [ ] All test scenarios pass
- [ ] Performance benchmarks met
- [ ] No console errors in browser
- [ ] No errors in backend logs
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] CORS settings correct
- [ ] Rate limiting tested
- [ ] Security headers verified
- [ ] OpenAI API budget set

---

## Support

**Issues During Testing**:
1. Check logs: `tail -f phase3-backend/logs/app.log`
2. Review database state: `psql $DATABASE_URL`
3. Verify service health endpoints
4. Check GitHub issues or documentation

**Questions**:
- OpenAI ChatKit Docs: https://platform.openai.com/docs/guides/chatkit
- chatkit-python SDK: https://openai.github.io/chatkit-python/
- @openai/chatkit-react: https://openai.github.io/chatkit-js/
