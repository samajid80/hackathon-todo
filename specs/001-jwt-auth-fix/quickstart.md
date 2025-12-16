# Quickstart Guide: JWT Authentication Security Fix Testing

**Feature**: JWT Authentication Security Fix
**Branch**: `001-jwt-auth-fix`
**Purpose**: Validate that JWT token verification correctly rejects invalid, expired, and tampered tokens

---

## Prerequisites

1. **Backend Environment Setup**:
   ```bash
   cd backend
   source .venv/bin/activate  # or your virtual environment
   ```

2. **Environment Variables Configured**:
   ```bash
   # backend/.env must contain:
   JWT_SECRET=<32+ character secret>
   JWT_ALGORITHM=HS256
   ```

3. **Dependencies Installed**:
   ```bash
   pip install -e ".[test,dev]"
   # Ensures python-jose[cryptography], pytest, etc. are available
   ```

---

## Test Scenarios

### Scenario 1: Valid Token Acceptance

**Purpose**: Verify that properly signed, non-expired tokens are accepted

**Test Command**:
```bash
pytest backend/tests/test_auth.py::test_get_current_user_with_valid_token -v
```

**Expected Behavior**:
- ✅ Token is decoded successfully
- ✅ user_id is extracted from 'sub' claim
- ✅ Email is extracted from 'email' claim
- ✅ CurrentUser object returned with correct attributes
- ✅ No exceptions raised

**Success Criteria**:
- Test passes (PASSED status)
- `current_user.user_id` matches test fixture UUID
- `current_user.email` equals "test@example.com"

**What This Tests**:
- `jwt.decode()` successfully verifies signature using JWT_SECRET
- HS256 algorithm validation works correctly
- Token expiration is in the future (not expired)
- Required claims ('sub', 'email', 'exp') are present

---

### Scenario 2: Expired Token Rejection

**Purpose**: Verify that expired tokens are rejected with 401 Unauthorized

**Test Command**:
```bash
pytest backend/tests/test_auth.py::test_get_current_user_with_expired_token -v
```

**Expected Behavior**:
- ❌ Token decode raises `ExpiredSignatureError`
- ❌ Exception caught and converted to HTTPException
- ❌ Status code 401 returned
- ❌ Detail message: "Could not validate credentials"

**Success Criteria**:
- Test passes (PASSED status)
- HTTPException raised with status_code=401
- Error detail contains "Could not validate credentials"
- Token with past 'exp' claim is rejected

**What This Tests**:
- `jwt.decode()` checks 'exp' claim against current time
- Expiration validation happens automatically (verify_exp=True)
- ExpiredSignatureError is caught by JWTError exception handler
- Users cannot use tokens after expiration

**Manual Verification** (optional):
```python
from datetime import datetime, timedelta
from jose import jwt

# Create expired token
expired_payload = {
    "sub": "test-user-id",
    "exp": datetime.utcnow() - timedelta(hours=1)  # 1 hour ago
}
expired_token = jwt.encode(expired_payload, "test-secret", algorithm="HS256")

# Attempt to decode (should raise ExpiredSignatureError)
try:
    jwt.decode(expired_token, "test-secret", algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    print("✅ Expired token correctly rejected")
```

---

### Scenario 3: Invalid Signature Rejection

**Purpose**: Verify that tokens signed with wrong secret are rejected

**Test Command**:
```bash
pytest backend/tests/test_auth.py::test_get_current_user_with_invalid_token -v
```

**Expected Behavior**:
- ❌ Token decode raises `JWTError` (signature verification failure)
- ❌ Exception caught and converted to HTTPException
- ❌ Status code 401 returned
- ❌ Detail message: "Could not validate credentials"

**Success Criteria**:
- Test passes (PASSED status)
- Malformed token "invalid.token.here" is rejected
- HTTPException raised with status_code=401
- Signature validation prevents acceptance

**What This Tests**:
- `jwt.decode()` verifies HMAC signature using JWT_SECRET
- Tokens not signed with correct secret are rejected
- Prevents forged tokens from being accepted
- Cryptographic integrity validation works

**Manual Verification** (optional):
```python
from jose import jwt

# Create token with WRONG secret
payload = {"sub": "attacker", "exp": datetime.utcnow() + timedelta(hours=1)}
forged_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

# Attempt to decode with CORRECT secret (should fail)
try:
    jwt.decode(forged_token, "correct-secret", algorithms=["HS256"])
except jwt.JWTError:
    print("✅ Forged token correctly rejected")
```

---

### Scenario 4: Missing User ID Claim Rejection

**Purpose**: Verify that tokens without user identification are rejected

**Test Command**:
```bash
pytest backend/tests/test_auth.py::test_get_current_user_with_missing_user_id -v
```

**Expected Behavior**:
- ✅ Token signature and expiration are valid
- ❌ User ID extraction fails (no 'sub', 'user_id', or 'id' claim)
- ❌ HTTPException raised with status_code=401
- ❌ Detail message: "Could not validate credentials"

**Success Criteria**:
- Test passes (PASSED status)
- Token is cryptographically valid but missing required claims
- Application-level validation rejects tokens without user_id
- HTTPException raised after successful decode

**What This Tests**:
- JWT verification succeeds (signature + expiration valid)
- Application-level claim validation happens AFTER JWT validation
- System requires specific claims ('sub', 'user_id', or 'id') for authentication
- Defense in depth: cryptographic validation + business logic validation

**Token Structure** (from test):
```python
payload = {
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(hours=1)
    # NOTE: Missing 'sub', 'user_id', and 'id' claims
}
```

---

### Scenario 5: Invalid UUID Format Rejection

**Purpose**: Verify that tokens with non-UUID user_id are rejected

**Test Command**:
```bash
pytest backend/tests/test_auth.py::test_get_current_user_with_invalid_user_id_format -v
```

**Expected Behavior**:
- ✅ Token signature and expiration are valid
- ✅ 'sub' claim is present
- ❌ 'sub' value is not a valid UUID ("not-a-valid-uuid")
- ❌ HTTPException raised with status_code=401

**Success Criteria**:
- Test passes (PASSED status)
- Token with invalid UUID format is rejected
- UUID validation happens at application level
- System enforces data format constraints

**What This Tests**:
- Tokens with malformed user IDs are rejected
- Application validates claim values, not just presence
- Type safety for user_id (must be UUID-compatible string)
- Prevents injection attacks via malformed identifiers

**Token Structure** (from test):
```python
payload = {
    "sub": "not-a-valid-uuid",  # Invalid UUID format
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(hours=1)
}
```

---

### Scenario 6: User ID Extraction from 'sub' Claim

**Purpose**: Verify that user_id is correctly extracted from 'sub' claim (Better-Auth standard)

**Test Command**:
```bash
pytest backend/tests/test_auth.py::test_get_current_user_extracts_from_sub_claim -v
```

**Expected Behavior**:
- ✅ Token is valid and verified
- ✅ user_id extracted from 'sub' claim
- ✅ CurrentUser object created with correct user_id

**Success Criteria**:
- Test passes (PASSED status)
- `current_user.user_id` equals the UUID from 'sub' claim
- Better-Auth standard claim format supported

**What This Tests**:
- Primary claim source for user identification
- OpenID Connect compliance ('sub' is standard user ID claim)
- Better-Auth token compatibility

---

### Scenario 7: User ID Extraction from 'user_id' Claim (Fallback)

**Purpose**: Verify that system falls back to 'user_id' claim if 'sub' is absent

**Test Command**:
```bash
pytest backend/tests/test_auth.py::test_get_current_user_extracts_from_user_id_claim -v
```

**Expected Behavior**:
- ✅ Token is valid and verified
- ✅ No 'sub' claim present
- ✅ user_id extracted from 'user_id' claim (fallback)
- ✅ CurrentUser object created with correct user_id

**Success Criteria**:
- Test passes (PASSED status)
- System handles alternative claim names
- Backward compatibility maintained

**What This Tests**:
- Fallback claim resolution logic
- Support for non-standard token formats
- Graceful handling of missing primary claims

---

## Running All Security Tests

**Command**:
```bash
pytest backend/tests/test_auth.py -v
```

**Expected Output**:
```
test_get_current_user_with_valid_token PASSED
test_get_current_user_with_expired_token PASSED
test_get_current_user_with_invalid_token PASSED
test_get_current_user_with_missing_user_id PASSED
test_get_current_user_with_invalid_user_id_format PASSED
test_get_current_user_extracts_from_sub_claim PASSED
test_get_current_user_extracts_from_user_id_claim PASSED
[Additional 4 tests from test run] PASSED

======================== 11 passed in X.XXs ========================
```

**Success Criteria**:
- ✅ All 11 tests pass
- ✅ No failures, errors, or warnings
- ✅ Test execution completes in reasonable time (<5 seconds)

---

## Integration Testing

### End-to-End Authentication Flow

**Purpose**: Verify JWT authentication works with actual API endpoints

**Setup**:
1. Start backend server:
   ```bash
   cd backend
   uvicorn backend.main:app --reload --port 8000
   ```

2. Start frontend (in separate terminal):
   ```bash
   cd frontend
   npm run dev
   ```

**Test Steps**:

1. **Login via Frontend**:
   - Navigate to http://localhost:3000/login
   - Enter test credentials
   - Verify redirect to tasks page

2. **Create Task with Valid JWT**:
   ```bash
   # Extract JWT from browser DevTools (Application → Local Storage)
   export TOKEN="<jwt-token-from-browser>"

   curl -X POST http://localhost:8000/api/tasks \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "Test Task", "description": "Security test"}'
   ```

   **Expected**: 200 OK, task created

3. **Attempt Task Access with Expired Token**:
   ```bash
   # Create expired token using python script
   python3 <<EOF
   from datetime import datetime, timedelta
   from jose import jwt
   import os

   secret = os.getenv('JWT_SECRET', 'test-secret')
   payload = {
       "sub": "fake-user-id",
       "exp": datetime.utcnow() - timedelta(hours=1)
   }
   expired = jwt.encode(payload, secret, algorithm="HS256")
   print(expired)
   EOF

   # Use expired token in request
   curl -X GET http://localhost:8000/api/tasks \
     -H "Authorization: Bearer <expired-token>"
   ```

   **Expected**: 401 Unauthorized, "Could not validate credentials"

4. **Attempt Task Access with Forged Token**:
   ```bash
   # Create token with wrong secret
   python3 <<EOF
   from datetime import datetime, timedelta
   from jose import jwt

   payload = {
       "sub": "attacker-id",
       "exp": datetime.utcnow() + timedelta(hours=1)
   }
   forged = jwt.encode(payload, "wrong-secret", algorithm="HS256")
   print(forged)
   EOF

   # Use forged token in request
   curl -X GET http://localhost:8000/api/tasks \
     -H "Authorization: Bearer <forged-token>"
   ```

   **Expected**: 401 Unauthorized, signature verification failure

---

## Performance Testing

**Purpose**: Verify token verification meets performance requirements (SC-004: <50ms per request)

**Benchmark Command**:
```bash
pytest backend/tests/test_auth.py::test_get_current_user_with_valid_token \
  --benchmark-only --benchmark-warmup=on
```

**Alternative - Manual Benchmark**:
```python
import time
from datetime import datetime, timedelta
from jose import jwt

# Setup
secret = "test-secret-32-characters-long"
payload = {
    "sub": "test-user-id",
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(hours=1)
}
token = jwt.encode(payload, secret, algorithm="HS256")

# Benchmark decode (1000 iterations)
start = time.time()
for _ in range(1000):
    jwt.decode(token, secret, algorithms=["HS256"])
end = time.time()

avg_time_ms = (end - start) / 1000 * 1000
print(f"Average decode time: {avg_time_ms:.2f}ms")

# Expected: <10ms per decode (well under 50ms requirement)
```

**Success Criteria**:
- ✅ Average verification time < 50ms (typically <10ms for HS256)
- ✅ p95 latency < 50ms
- ✅ No performance degradation compared to unverified claims

---

## Troubleshooting

### Issue: All tests fail with "JWT_SECRET not set"

**Cause**: Environment variable missing in test environment

**Solution**:
```bash
# Set JWT_SECRET for test session
export JWT_SECRET="test-secret-key-for-testing-only"
pytest backend/tests/test_auth.py -v
```

Or update `backend/tests/conftest.py` to set default for tests.

---

### Issue: Valid token test fails with "signature verification failed"

**Cause**: JWT_SECRET mismatch between token creation and verification

**Solution**:
```python
# Verify secret consistency in conftest.py
# Ensure test fixtures use same secret as jwt_middleware.py
```

---

### Issue: Expired token test passes but should fail

**Cause**: Token not actually expired (clock skew or future expiration)

**Solution**:
```python
# Check token payload in conftest.py
# Ensure exp is in the past:
"exp": datetime.utcnow() - timedelta(hours=1)  # Correct
# NOT:
"exp": datetime.utcnow() + timedelta(hours=1)  # Wrong (future)
```

---

### Issue: Integration tests fail but unit tests pass

**Cause**: Frontend and backend using different JWT secrets

**Solution**:
```bash
# Verify environment variables match
cat backend/.env | grep JWT_SECRET
cat frontend/.env.local | grep BETTER_AUTH_SECRET

# These MUST be identical
```

---

## Quick Validation Checklist

Before considering the fix complete, verify:

- [ ] All 11 tests in `test_auth.py` pass
- [ ] Full backend test suite passes (`pytest backend/tests/ -v`)
- [ ] Frontend login → task creation → logout works end-to-end
- [ ] Expired tokens rejected with 401 (not 500 or accepted)
- [ ] Forged tokens rejected with 401
- [ ] Performance: token verification < 50ms
- [ ] No debug logs leaking tokens/secrets/claims
- [ ] Code review completed
- [ ] Documentation updated (code comments, README if needed)

---

## References

- **Feature Spec**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Research**: [research.md](./research.md)
- **Source Code**: `backend/auth/jwt_middleware.py`
- **Test Suite**: `backend/tests/test_auth.py`
- **Test Fixtures**: `backend/tests/conftest.py`
