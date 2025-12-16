# Implementation Plan: JWT Authentication Security Fix

**Branch**: `001-jwt-auth-fix` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-jwt-auth-fix/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix critical JWT authentication vulnerabilities in the FastAPI backend by implementing proper token verification, expiration checking, and signature validation. The current implementation uses `jwt.get_unverified_claims()` which bypasses ALL security checks, allowing attackers to forge tokens, use expired tokens, and tamper with token claims. This fix will replace the insecure code with proper `jwt.decode()` verification using the shared JWT_SECRET, enabling cryptographic signature validation and expiration enforcement to pass all 11 failing security tests.

## Technical Context

**Language/Version**: Python 3.13 (backend only - no frontend changes required)
**Primary Dependencies**: python-jose[cryptography] (already installed), FastAPI security module
**Storage**: N/A (no data model changes)
**Testing**: pytest, pytest-asyncio (existing test suite with 11 failing tests)
**Target Platform**: Linux server (FastAPI backend on port 8000)
**Project Type**: Web backend (FastAPI only - frontend unchanged)
**Performance Goals**: Token verification under 50ms per request (HS256 symmetric key validation)
**Constraints**: Must maintain compatibility with Better-Auth frontend JWT format; zero breaking changes to API endpoints
**Scale/Scope**: Single file change (`backend/auth/jwt_middleware.py`), affects all authenticated endpoints system-wide

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase 2 Constitution Compliance

✅ **Section 3.1 (Authentication)**: Fix maintains JWT validation requirements
- Current violation: JWT signature not validated (security vulnerability)
- Fix: Implement proper signature validation using shared JWT_SECRET
- Result: Enforces "Validate signature + expiry" requirement from constitution

✅ **Section 3.4 (Backend Requirements)**: Authentication handling compliance
- Current violation: "Accept JWT from Better-Auth" - accepted but not validated
- Fix: "Validate signature + expiry" - now properly validated
- Result: "Reject if user_id mismatches token" - already enforced, security improved

✅ **Section 5.3 (Stateless Backend)**: No changes to stateless architecture
- Backend remains stateless (JWT-based identity)
- No session state introduced
- Horizontally scalable design maintained

✅ **Section 5.4 (Layered Backend Architecture)**: Single file in auth layer
- Change isolated to `backend/auth/jwt_middleware.py`
- No changes to routes, models, services, or db layers
- Maintains clear separation of concerns

✅ **Section 6.1 (Technology Stack)**: No new dependencies
- Uses existing python-jose[cryptography] library
- Compatible with Python 3.13
- No framework changes

✅ **Section 6.2 (Security Constraints)**: **PRIMARY GOAL OF THIS FIX**
- **Current violation**: "JWT signature must be validated using shared secret" - NOT ENFORCED
- **Current violation**: Users CAN potentially access other users' tasks with forged tokens
- **Current violation**: Sensitive token information leaked in debug logs
- **Fix**: Enables all three security guarantees
- **Result**: CRITICAL SECURITY FIX - closes authentication bypass vulnerability

✅ **Section 6.3 (Performance Constraints)**: No impact on database queries
- Token verification adds <50ms overhead (negligible)
- No changes to indexing or query patterns
- Performance requirement maintained

✅ **Section 7.2 (Testing Requirements)**: Test coverage improved
- 11 existing security tests currently failing
- Fix will make all tests pass (100% security test coverage)
- No new tests required (comprehensive coverage already exists)

### Constitution Violations: NONE

This fix **resolves** existing constitutional violations (Section 6.2 security constraints) without introducing new violations.

**Pre-Research Gate**: ✅ PASS (security fix, no architectural changes)

## Project Structure

### Documentation (this feature)

```text
specs/001-jwt-auth-fix/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan output)
├── research.md          # Phase 0 output - library verification
├── quickstart.md        # Phase 1 output - test scenarios
└── checklists/
    └── requirements.md  # Validation checklist (completed)
```

**Note**: No `data-model.md` or `contracts/` needed - this is a security fix with no data/API changes.

### Source Code (repository root)

```text
backend/
├── auth/
│   ├── jwt_middleware.py    # TARGET FILE - security fix applied here
│   └── rate_limiter.py      # No changes
├── routes/
│   └── tasks.py             # No changes (uses jwt_middleware via dependency)
├── models/
│   ├── task.py              # No changes
│   └── user.py              # No changes
├── services/
│   └── task_service.py      # No changes
├── main.py                  # No changes
└── db.py                    # No changes

backend/tests/
├── test_auth.py             # TARGET FILE - 11 failing tests here
├── test_task_routes.py      # May indirectly pass after fix
├── test_task_service.py     # No changes expected
├── test_integration.py      # May indirectly pass after fix
└── conftest.py              # Test fixtures (test_jwt_token, expired_jwt_token)

frontend/                    # NO CHANGES - frontend unaffected
```

**Structure Decision**: This is a backend-only security fix in the existing FastAPI web application architecture. Single file modification to `backend/auth/jwt_middleware.py` with validation via `backend/tests/test_auth.py`. Frontend (Next.js) continues issuing tokens via Better-Auth unchanged.

## Complexity Tracking

> **No Constitution Violations** - This section is empty because all constitution checks passed.

---

## Phase 0: Research & Validation

### Research Questions

1. **python-jose Library Capabilities**
   - Question: Does python-jose support HS256 signature verification with expiration checking?
   - Context: Current code has TODO comment suggesting EdDSA/JWKS needed, but system uses HS256
   - Research needed: Verify `jwt.decode()` API and default verification behavior

2. **Better-Auth Token Format Compatibility**
   - Question: What claims does Better-Auth include in JWT tokens ('sub' vs 'user_id' vs 'id')?
   - Context: Code checks multiple claim names for user_id extraction
   - Research needed: Document which claim is primary and verify compatibility

3. **JWTError Exception Types**
   - Question: What specific exceptions does python-jose raise for expired vs invalid signature?
   - Context: Need to handle expiration and signature errors correctly
   - Research needed: Document exception hierarchy for proper error handling

### Research Output

See [research.md](./research.md) for detailed findings.

---

## Phase 1: Design Artifacts

### Data Model

**N/A** - No data model changes. This fix modifies authentication middleware only.

### API Contracts

**N/A** - No API contract changes. All endpoints remain unchanged:
- Request format: Same (Authorization: Bearer <token>)
- Response format: Same (401 Unauthorized for invalid tokens)
- Error messages: Same ("Could not validate credentials")

### Test Scenarios

See [quickstart.md](./quickstart.md) for:
- Valid token acceptance test
- Expired token rejection test
- Invalid signature rejection test
- Tampered payload rejection test
- Missing claims rejection test

### Agent Context Update

Agent context will be updated after Phase 1 completion to include:
- JWT security best practices
- python-jose verification patterns
- Token validation error handling

---

## Phase 2: Implementation Design

### Core Logic Change

**File**: `backend/auth/jwt_middleware.py`
**Function**: `get_current_user()` (lines 60-130)

**Current Implementation** (INSECURE):
```python
# Lines 100-106
unverified_payload = jwt.get_unverified_claims(token)
payload = unverified_payload  # NO VALIDATION!
```

**Proposed Implementation** (SECURE):
```python
# Replace lines 100-106 with:
payload = jwt.decode(
    token=token,
    key=jwt_secret,
    algorithms=[jwt_algorithm]
)
```

**Changes**:
1. Remove `jwt.get_unverified_claims()` call (line 102)
2. Remove debug print statements (lines 101, 103)
3. Replace with `jwt.decode()` with verification enabled (default)
4. Keep existing exception handling (JWTError already catches ExpiredSignatureError)

### Exception Handling

**Current**: Catches generic `JWTError`
**After Fix**: Same exception handling, but now includes:
- `ExpiredSignatureError` (subclass of JWTError) - expired tokens
- `JWTClaimsError` (subclass of JWTError) - invalid claims
- `JWTError` (base class) - signature validation failures, malformed tokens

**No code changes needed** - existing `except JWTError` catches all validation failures.

### Debug Logging Cleanup

**Security Requirement**: Remove debug print statements that leak sensitive information

**Lines to Remove/Modify**:
- Line 93: `print(f"[JWT Debug] Received token...")`  - REMOVE (leaks token)
- Line 98: `print(f"[JWT Debug] Using secret...")`    - REMOVE (leaks secret)
- Line 101: `print(f"[JWT Debug] Attempting...")`     - REMOVE
- Line 103: `print(f"[JWT Debug] Unverified payload...")` - REMOVE (leaks claims)
- Line 109: `print(f"[JWT Debug] Decoded payload...")` - REMOVE (leaks claims)
- Line 114: `print(f"[JWT Debug] No 'sub'...")`       - KEEP (useful error diagnostic)
- Line 117: `print(f"[JWT Debug] Extracted user_id...")` - REMOVE (leaks user_id)
- Line 125-126: `print(f"[JWT Debug] JWTError...")`  - KEEP (error diagnostic)
- Line 128-129: `print(f"[JWT Debug] Unexpected...")` - KEEP (error diagnostic)

**Decision**: Remove token/secret/payload logging, keep error diagnostics for debugging.

### Testing Strategy

**Test Execution**:
1. Run `pytest backend/tests/test_auth.py -v` to verify all 11 tests pass
2. Run full backend test suite to ensure no regressions
3. Verify integration tests still pass (task routes with JWT authentication)

**Expected Results**:
- `test_get_current_user_with_valid_token` - PASS (was passing, still passes)
- `test_get_current_user_with_expired_token` - NOW PASSES (currently fails)
- `test_get_current_user_with_invalid_token` - NOW PASSES (currently fails)
- `test_get_current_user_with_missing_user_id` - PASS (already passes)
- `test_get_current_user_with_invalid_user_id_format` - PASS (already passes)
- `test_get_current_user_extracts_from_sub_claim` - NOW PASSES (currently fails)
- `test_get_current_user_extracts_from_user_id_claim` - NOW PASSES (currently fails)
- Additional 4 tests not visible in test file but failing in test run - NOW PASS

### Deployment Considerations

**Zero Downtime**: This fix is backward compatible
- Valid tokens continue working (now with verification)
- Invalid tokens now properly rejected (security improvement)
- No API endpoint changes
- No database migrations
- No frontend changes

**Rollout Strategy**:
1. Deploy backend with fix to staging
2. Run full test suite in staging
3. Verify frontend authentication still works
4. Deploy to production
5. Monitor for authentication errors (should decrease, not increase)

### Rollback Plan

If issues occur:
1. Revert `backend/auth/jwt_middleware.py` to previous version
2. Redeploy backend
3. System returns to insecure state (but functional)
4. Investigate token compatibility issues

**Risk**: LOW - python-jose is stable, HS256 is standard, Better-Auth tokens are compliant

---

## Phase 3: Code Organization

### File Modifications

**Single File Change**:
- `backend/auth/jwt_middleware.py` - Replace lines 93-117 with secure implementation

**No New Files**: All changes in existing file

**No Deletions**: No files removed

### Import Changes

**None Required** - All imports already present:
```python
from jose import JWTError, jwt  # Already imported
```

### Configuration Changes

**None Required** - Environment variables already configured:
- `JWT_SECRET` - Shared secret for HS256 verification
- `JWT_ALGORITHM` - Already set to "HS256"

---

## Phase 4: Validation & Acceptance

### Success Criteria Mapping

| Success Criterion | How Validated | Pass Condition |
|-------------------|---------------|----------------|
| SC-001: All 11 tests pass | Run pytest backend/tests/test_auth.py | 11/11 tests PASSED |
| SC-002: 0% false acceptance | Test with forged tokens | All rejected with 401 |
| SC-003: 100% expiration enforcement | Test with expired tokens | All rejected with 401 |
| SC-004: <50ms verification time | Benchmark jwt.decode() | p95 latency <50ms |
| SC-005: 100% tampered token rejection | Test with modified payloads | All rejected with 401 |
| SC-006: Consistent 401 responses | Test all failure modes | Always returns 401 |

### Test Coverage

**Unit Tests** (backend/tests/test_auth.py):
- Valid token acceptance ✅
- Expired token rejection ✅
- Invalid signature rejection ✅
- Missing user_id rejection ✅
- Invalid UUID format rejection ✅
- Multiple claim sources (sub, user_id, id) ✅

**Integration Tests** (backend/tests/test_integration.py):
- Task creation with valid JWT ✅
- Task access with expired JWT (401) ✅
- Task access with forged JWT (401) ✅

**Manual Verification**:
- Frontend login → task CRUD operations (end-to-end flow)
- Expired session handling (user sees 401, redirected to login)

### Acceptance Checklist

- [ ] All 11 security tests in test_auth.py pass
- [ ] Full backend test suite passes (no regressions)
- [ ] Frontend authentication flow works (login → tasks → logout)
- [ ] Invalid tokens rejected with 401 (not 500 or accepted)
- [ ] Debug logs cleaned up (no token/secret/payload leakage)
- [ ] Code review completed (peer verification of security fix)
- [ ] Documentation updated (code comments reflect secure implementation)

---

## Post-Phase 1 Constitution Re-check

✅ **Section 6.2 (Security Constraints)**: NOW COMPLIANT
- JWT signature validation: ✅ ENABLED (was disabled)
- User isolation enforcement: ✅ IMPROVED (forged tokens now rejected)
- No sensitive log leakage: ✅ FIXED (debug prints removed)

✅ **All other sections**: STILL COMPLIANT (no architectural changes)

**Final Gate**: ✅ PASS - Ready for Phase 2 (tasks breakdown)

---

## Notes & Decisions

### Why HS256 Instead of EdDSA/JWKS?

The TODO comment in the current code suggests EdDSA or JWKS is needed, but this is incorrect for this system:

**Current System**:
- Better-Auth (frontend) issues JWT signed with `BETTER_AUTH_SECRET` using HS256
- Backend has same secret in `JWT_SECRET` environment variable
- Symmetric key authentication (shared secret) is appropriate for this architecture

**EdDSA/JWKS Use Case**:
- Asymmetric keys (public/private key pairs)
- Multi-tenant systems with external identity providers
- Token issuers and validators in different security domains

**Decision**: Use HS256 verification with shared secret (standard for Better-Auth + FastAPI integration)

### Why Not Upgrade python-jose?

**Current Version**: python-jose[cryptography] (exact version in requirements.txt)
**Latest Version**: 3.3.0 (supports all needed features)

**Decision**: No upgrade needed unless current version lacks `jwt.decode()` support. Verify in research phase.

### Why Remove Debug Logs?

**Security Risk**: Debug logs expose:
- Raw JWT tokens (can be replayed if leaked)
- JWT_SECRET (critical security credential)
- User claims (email, user_id - PII)

**Best Practice**: Production code should never log sensitive authentication data.

**Trade-off**: Debugging becomes harder, but security takes precedence.

**Mitigation**: Keep error-level logs for diagnostics (JWT validation failures) without exposing token contents.

### Alternative Approaches Considered

1. **Add JWKS endpoint**: Rejected (over-engineering, not needed for symmetric keys)
2. **Implement token caching**: Rejected (stateless backend principle, marginal performance gain)
3. **Add custom token validation**: Rejected (python-jose provides all needed functionality)
4. **Change to asymmetric keys**: Rejected (requires Better-Auth reconfiguration, breaking change)

**Selected Approach**: Minimal change - use python-jose's built-in verification with existing symmetric key setup.

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Better-Auth tokens incompatible with verification | Low | High | Research phase validates token format compatibility |
| Performance regression (slow verification) | Very Low | Medium | Benchmark in testing, HS256 is fast (<10ms typical) |
| Frontend breaks due to stricter validation | Low | Medium | Staging deployment with full E2E tests before production |
| python-jose missing features | Very Low | High | Research phase verifies library capabilities |
| Rollback needed due to unforeseen issues | Low | Low | Single file change, easy revert |

**Overall Risk**: LOW - Well-understood fix with comprehensive test coverage

---

## Timeline Estimate

**Research Phase**: 30 minutes
- Verify python-jose API
- Test token format compatibility
- Document exception types

**Implementation Phase**: 1 hour
- Modify jwt_middleware.py (15 mins)
- Remove debug logs (15 mins)
- Run tests and fix issues (30 mins)

**Validation Phase**: 30 minutes
- Full test suite execution
- Frontend integration testing
- Code review

**Total Estimated Time**: 2 hours (small, focused security fix)

---

**Plan Status**: READY FOR PHASE 0 (Research)
**Next Command**: Continue with research.md generation
