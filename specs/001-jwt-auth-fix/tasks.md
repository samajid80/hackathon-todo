# Tasks: JWT Authentication Security Fix

**Input**: Design documents from `/specs/001-jwt-auth-fix/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, quickstart.md

**Tests**: Security tests already exist in `backend/tests/test_auth.py` - this fix aims to make 11 failing tests pass.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. All three user stories (US1, US2, US3) are P1 priority and can be addressed together as they all involve the same code fix.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` for FastAPI backend
- All tasks are backend-only - no frontend changes required
- Primary file: `backend/auth/jwt_middleware.py`
- Test file: `backend/tests/test_auth.py`

---

## Phase 1: Setup (Preparation)

**Purpose**: Verify prerequisites and understand current implementation

- [ ] T001 Verify python-jose[cryptography] is installed in backend environment
- [ ] T002 Review current implementation in backend/auth/jwt_middleware.py:60-130
- [ ] T003 Review failing test cases in backend/tests/test_auth.py
- [ ] T004 Verify JWT_SECRET environment variable is configured in backend/.env
- [ ] T005 Verify JWT_ALGORITHM is set to HS256 in backend/.env or code

---

## Phase 2: User Story 1 - Secure Token Validation (Priority: P1)

**Goal**: Implement proper JWT signature verification to prevent unauthorized access via forged or tampered tokens

**Independent Test**: Send various invalid tokens (tampered signature, modified payload, wrong signing key) to any protected endpoint and verify all are rejected with 401 Unauthorized. Success means signature verification is cryptographically enforced.

### Implementation for User Story 1

- [ ] T006 [US1] Replace jwt.get_unverified_claims() with jwt.decode() in backend/auth/jwt_middleware.py:100-106
- [ ] T007 [US1] Configure jwt.decode() to use JWT_SECRET from environment in backend/auth/jwt_middleware.py:100-106
- [ ] T008 [US1] Configure jwt.decode() to use algorithms=[JWT_ALGORITHM] in backend/auth/jwt_middleware.py:100-106
- [ ] T009 [US1] Verify JWTError exception handling catches signature validation failures in backend/auth/jwt_middleware.py:125-129
- [ ] T010 [US1] Test with valid token to ensure signature verification passes
- [ ] T011 [US1] Test with tampered token to ensure signature verification fails with 401
- [ ] T012 [US1] Test with wrong-secret token to ensure signature mismatch is detected

**Checkpoint**: Signature verification is working - all tokens must be cryptographically valid to proceed

---

## Phase 3: User Story 2 - Token Expiration Enforcement (Priority: P1)

**Goal**: Ensure expired tokens are rejected immediately to limit the window of exploitation for leaked tokens

**Independent Test**: Create tokens with past expiration dates and verify they are rejected with 401. Create tokens with future expiration dates and verify they are accepted. Success means time-bound security is enforced.

### Implementation for User Story 2

- [ ] T013 [US2] Verify jwt.decode() has verify_exp enabled (default: True) in backend/auth/jwt_middleware.py:100-106
- [ ] T014 [US2] Ensure ExpiredSignatureError is caught by existing JWTError handler in backend/auth/jwt_middleware.py:125-129
- [ ] T015 [US2] Test with expired token to ensure it's rejected with 401 Unauthorized
- [ ] T016 [US2] Test with future-expiration token to ensure it's accepted
- [ ] T017 [US2] Test with missing 'exp' claim to verify behavior (should reject if require_exp is set)

**Checkpoint**: Expiration enforcement is working - only non-expired tokens are accepted

---

## Phase 4: User Story 3 - Signature Verification (Priority: P1)

**Goal**: Cryptographically verify token signatures to ensure tokens were issued by the authentication service and haven't been tampered with

**Independent Test**: Create tokens signed with different keys and verify only tokens signed with the correct JWT_SECRET are accepted. Success means cryptographic integrity is guaranteed for all authenticated requests.

### Implementation for User Story 3

- [ ] T018 [US3] Verify jwt.decode() uses verify_signature=True (default) in backend/auth/jwt_middleware.py:100-106
- [ ] T019 [US3] Verify algorithm restriction is enforced (algorithms parameter) in backend/auth/jwt_middleware.py:100-106
- [ ] T020 [US3] Test with correctly-signed token to ensure verification passes
- [ ] T021 [US3] Test with incorrectly-signed token to ensure verification fails
- [ ] T022 [US3] Test with corrupted signature to ensure detection and rejection
- [ ] T023 [US3] Verify JWT_SECRET environment variable is correctly loaded at startup

**Checkpoint**: Signature verification is complete - cryptographic integrity is enforced

---

## Phase 5: Security & Cleanup

**Purpose**: Remove debug logging that leaks sensitive information and ensure secure implementation

- [ ] T024 Remove or sanitize debug print statement at backend/auth/jwt_middleware.py:93 (leaks token)
- [ ] T025 Remove or sanitize debug print statement at backend/auth/jwt_middleware.py:98 (leaks secret)
- [ ] T026 Remove or sanitize debug print statement at backend/auth/jwt_middleware.py:101 (debug message)
- [ ] T027 Remove or sanitize debug print statement at backend/auth/jwt_middleware.py:103 (leaks unverified payload)
- [ ] T028 Remove or sanitize debug print statement at backend/auth/jwt_middleware.py:109 (leaks decoded payload)
- [ ] T029 Remove or sanitize debug print statement at backend/auth/jwt_middleware.py:117 (leaks user_id)
- [ ] T030 Keep error diagnostic logs at backend/auth/jwt_middleware.py:114,125-129 (safe for debugging)
- [ ] T031 Remove TODO comment about EdDSA/JWKS at backend/auth/jwt_middleware.py:105 (HS256 is correct approach)

**Checkpoint**: No sensitive information is logged - security best practices followed

---

## Phase 6: Testing & Validation

**Purpose**: Verify all 11 failing tests now pass and no regressions introduced

- [ ] T032 Run pytest backend/tests/test_auth.py::test_get_current_user_with_valid_token -v (expect PASS)
- [ ] T033 Run pytest backend/tests/test_auth.py::test_get_current_user_with_expired_token -v (expect PASS - was FAILING)
- [ ] T034 Run pytest backend/tests/test_auth.py::test_get_current_user_with_invalid_token -v (expect PASS - was FAILING)
- [ ] T035 Run pytest backend/tests/test_auth.py::test_get_current_user_with_missing_user_id -v (expect PASS)
- [ ] T036 Run pytest backend/tests/test_auth.py::test_get_current_user_with_invalid_user_id_format -v (expect PASS)
- [ ] T037 Run pytest backend/tests/test_auth.py::test_get_current_user_extracts_from_sub_claim -v (expect PASS - was FAILING)
- [ ] T038 Run pytest backend/tests/test_auth.py::test_get_current_user_extracts_from_user_id_claim -v (expect PASS - was FAILING)
- [ ] T039 Run full test suite: pytest backend/tests/test_auth.py -v (all 11 tests must PASS)
- [ ] T040 Run backend integration tests: pytest backend/tests/test_integration.py -v (verify no regressions)
- [ ] T041 Run backend task route tests: pytest backend/tests/test_task_routes.py -v (verify JWT auth works)
- [ ] T042 Run full backend test suite: pytest backend/tests/ -v --cov=backend (verify overall health)

**Checkpoint**: All tests pass - security vulnerabilities fixed without breaking existing functionality

---

## Phase 7: Manual Verification & Performance

**Purpose**: Validate end-to-end authentication flow and performance requirements

- [ ] T043 Start backend server and verify startup (no JWT_SECRET errors)
- [ ] T044 Test valid token against protected endpoint (POST /api/tasks) - expect 200 OK
- [ ] T045 Test expired token against protected endpoint - expect 401 Unauthorized
- [ ] T046 Test forged token (wrong secret) against protected endpoint - expect 401 Unauthorized
- [ ] T047 Test tampered token (modified payload) against protected endpoint - expect 401 Unauthorized
- [ ] T048 Benchmark token verification performance (should be <50ms, typically <10ms for HS256)
- [ ] T049 Test frontend integration: login → create task → logout (end-to-end flow)

**Checkpoint**: Production-ready - all security requirements met, performance acceptable

---

## Phase 8: Documentation & Code Review

**Purpose**: Update documentation and prepare for deployment

- [ ] T050 Update code comments in backend/auth/jwt_middleware.py to reflect secure implementation
- [ ] T051 Verify implementation matches research.md recommendations
- [ ] T052 Verify implementation satisfies all requirements in spec.md
- [ ] T053 Add inline comments explaining jwt.decode() parameters if needed
- [ ] T054 Code review: verify no sensitive information in logs
- [ ] T055 Code review: verify exception handling is correct
- [ ] T056 Code review: verify no security vulnerabilities introduced

**Checkpoint**: Code is production-ready and documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Story 1 (Phase 2)**: Depends on Setup completion - signature verification is foundational
- **User Story 2 (Phase 3)**: Can proceed after US1 or in parallel (same code change enables both)
- **User Story 3 (Phase 4)**: Can proceed after US1 or in parallel (same code change enables both)
- **Security & Cleanup (Phase 5)**: Should proceed after US1/US2/US3 implementation
- **Testing (Phase 6)**: Depends on Phases 2-5 being complete
- **Manual Verification (Phase 7)**: Depends on Phase 6 passing
- **Documentation (Phase 8)**: Can proceed in parallel with testing or after

### User Story Dependencies

**IMPORTANT**: All three user stories (US1, US2, US3) are addressed by the SAME code change:
- Replacing `jwt.get_unverified_claims()` with `jwt.decode()` enables ALL THREE security guarantees simultaneously
- Signature verification (US1) + Expiration checking (US2) + Cryptographic integrity (US3) = ONE implementation

Therefore:
- **User Story 1 (P1)**: Start after Setup - Core implementation
- **User Story 2 (P1)**: Automatically satisfied by US1 implementation (jwt.decode validates expiration)
- **User Story 3 (P1)**: Automatically satisfied by US1 implementation (jwt.decode verifies signature)

### Task-Level Dependencies

- T006-T009 (jwt.decode implementation) are the core fix - all other tasks validate this change
- T010-T012 (US1 tests) can run after T006-T009
- T013-T017 (US2 tests) can run after T006-T009 (in parallel with T010-T012)
- T018-T023 (US3 tests) can run after T006-T009 (in parallel with T010-T017)
- T024-T031 (cleanup) can run after T006-T009 (in parallel with testing)
- T032-T042 (full test suite) must run after all implementation and cleanup
- T043-T049 (manual verification) must run after T032-T042 pass
- T050-T056 (documentation) can run in parallel with testing or after

### Parallel Opportunities

**After Setup (Phase 1)**:
- T006-T009 (core implementation) - sequential (same file, same function)

**After Core Implementation (T006-T009)**:
- T010-T012 (US1 validation) + T013-T017 (US2 validation) + T018-T023 (US3 validation) + T024-T031 (cleanup) - ALL can run in parallel (different test scenarios, same code)

**After Implementation & Cleanup**:
- T032-T042 (test suite) - sequential (must run tests one at a time)

**After Tests Pass**:
- T043-T049 (manual verification) - sequential (integration testing)

**Anytime After Implementation**:
- T050-T056 (documentation) - can run in parallel with testing

---

## Parallel Example: Post-Implementation Validation

```bash
# After completing T006-T009 (core jwt.decode implementation), launch all validation tasks:

# US1 Validation (signature verification)
Task: "Test with valid token to ensure signature verification passes"
Task: "Test with tampered token to ensure signature verification fails with 401"
Task: "Test with wrong-secret token to ensure signature mismatch is detected"

# US2 Validation (expiration enforcement) - in parallel
Task: "Test with expired token to ensure it's rejected with 401 Unauthorized"
Task: "Test with future-expiration token to ensure it's accepted"
Task: "Test with missing 'exp' claim to verify behavior"

# US3 Validation (cryptographic integrity) - in parallel
Task: "Test with correctly-signed token to ensure verification passes"
Task: "Test with incorrectly-signed token to ensure verification fails"
Task: "Test with corrupted signature to ensure detection and rejection"

# Cleanup - in parallel
Task: "Remove debug print statements that leak sensitive data"
Task: "Remove TODO comment about EdDSA/JWKS"
```

---

## Implementation Strategy

### Single-Fix Approach (Recommended)

This is a unique case where one code change fixes ALL three user stories:

1. **Complete Phase 1: Setup** (T001-T005)
2. **Implement Core Fix: Phase 2** (T006-T009)
   - Replace `jwt.get_unverified_claims()` with `jwt.decode()`
   - This SINGLE change enables signature verification + expiration checking + cryptographic integrity
3. **Validate All Three Stories: Phases 3-5** (T010-T031 in parallel)
   - Test US1: Signature verification works
   - Test US2: Expiration enforcement works
   - Test US3: Cryptographic integrity works
   - Clean up debug logs
4. **Run Full Test Suite: Phase 6** (T032-T042)
   - All 11 tests should now PASS
5. **Manual Verification: Phase 7** (T043-T049)
6. **Documentation: Phase 8** (T050-T056)

### Why This is Different from Typical Multi-Story Tasks

- Normally each user story requires separate implementation tasks
- In this case, the insecure code (`jwt.get_unverified_claims()`) disables ALL THREE security checks
- Replacing it with `jwt.decode()` enables ALL THREE security checks simultaneously
- Therefore, the three user stories are conceptually separate (for specification) but technically unified (for implementation)

---

## Success Criteria

### All 11 Security Tests Pass (SC-001)
- ✅ pytest backend/tests/test_auth.py shows 11 PASSED, 0 FAILED
- ✅ Test execution completes in <5 seconds
- ✅ No warnings or errors during test run

### Zero False Acceptance Rate (SC-002)
- ✅ All tokens with invalid signatures are rejected (T011, T012, T021)
- ✅ Manual testing confirms forged tokens return 401 (T046)
- ✅ Integration tests confirm authentication enforcement (T041)

### 100% Expiration Enforcement (SC-003)
- ✅ All expired tokens are rejected (T015, T033)
- ✅ Manual testing with expired tokens returns 401 (T045)
- ✅ Future-expiration tokens are accepted (T016)

### Performance Under 50ms (SC-004)
- ✅ Benchmark shows <50ms per verification (T048)
- ✅ Typically <10ms for HS256 (acceptable overhead)
- ✅ No noticeable performance degradation in integration tests

### 100% Tampered Token Rejection (SC-005)
- ✅ Modified payload tokens are rejected (T011, T022)
- ✅ Manual testing with tampered tokens returns 401 (T047)
- ✅ Signature verification detects any payload changes

### Consistent 401 Responses (SC-006)
- ✅ All authentication failures return 401 Unauthorized (T032-T041)
- ✅ Error message is consistent: "Could not validate credentials"
- ✅ No 500 errors or unhandled exceptions

---

## Notes

- **Single-file change**: Only `backend/auth/jwt_middleware.py` is modified
- **No frontend changes**: Better-Auth continues issuing tokens unchanged
- **No API changes**: All endpoints remain the same, just more secure
- **No database changes**: No migrations required
- **Backward compatible**: Valid tokens continue working (now with verification)
- **Security improvement**: Invalid tokens now properly rejected (was vulnerability)

**Key Implementation Detail**: The core fix (T006-T009) is just 4-6 lines of code:

```python
# BEFORE (INSECURE):
unverified_payload = jwt.get_unverified_claims(token)
payload = unverified_payload

# AFTER (SECURE):
payload = jwt.decode(
    token=token,
    key=jwt_secret,
    algorithms=[jwt_algorithm]
)
```

This simple change enables cryptographic signature verification AND expiration checking AND integrity validation - fixing all 11 failing tests and closing critical security vulnerabilities.

---

## Total Task Count

- **Setup**: 5 tasks (T001-T005)
- **User Story 1**: 7 tasks (T006-T012)
- **User Story 2**: 5 tasks (T013-T017)
- **User Story 3**: 6 tasks (T018-T023)
- **Security & Cleanup**: 8 tasks (T024-T031)
- **Testing**: 11 tasks (T032-T042)
- **Manual Verification**: 7 tasks (T043-T049)
- **Documentation**: 7 tasks (T050-T056)

**TOTAL**: 56 tasks

**Parallel Opportunities**:
- T010-T031 (22 tasks can run in parallel after core implementation)
- High parallelization potential for validation and cleanup phases

**MVP Scope**: Phases 1-6 (T001-T042) constitute the MVP - all security tests passing. Phases 7-8 are validation and polish.
