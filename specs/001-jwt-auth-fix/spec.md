# Feature Specification: JWT Authentication Security Fix

**Feature Branch**: `001-jwt-auth-fix`
**Created**: 2025-12-16
**Status**: Draft
**Input**: User description: "Fix JWT authentication vulnerabilities in backend - implement proper token verification, expiration checking, and signature validation to resolve 11 failing security tests"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Token Validation (Priority: P1)

As a system administrator, I need the backend to properly validate JWT tokens to prevent unauthorized access to protected resources. The system must reject expired tokens, tampered tokens, and tokens with invalid signatures.

**Why this priority**: This is the most critical security vulnerability. Without proper token verification, attackers can forge tokens, use expired tokens, or modify token claims to gain unauthorized access to any user's data.

**Independent Test**: Can be fully tested by sending various invalid tokens (expired, tampered signature, modified payload) to any protected endpoint and verifying that all requests are rejected with 401 Unauthorized responses. Delivers immediate security improvement by closing authentication bypass vulnerabilities.

**Acceptance Scenarios**:

1. **Given** a user has a valid JWT token, **When** the token is sent to a protected endpoint, **Then** the request succeeds and the correct user_id is extracted
2. **Given** a user has an expired JWT token, **When** the token is sent to a protected endpoint, **Then** the request is rejected with 401 Unauthorized and error message "Could not validate credentials"
3. **Given** an attacker modifies the payload of a valid JWT token, **When** the tampered token is sent to a protected endpoint, **Then** the request is rejected due to signature validation failure
4. **Given** an attacker creates a token with a different signing key, **When** the token is sent to a protected endpoint, **Then** the request is rejected due to signature mismatch

---

### User Story 2 - Token Expiration Enforcement (Priority: P1)

As a security engineer, I need the system to reject expired tokens immediately to ensure that stolen or leaked tokens have a limited window of exploitation.

**Why this priority**: Tokens that never expire (or aren't checked for expiration) create a permanent backdoor. If a token is leaked, it can be used indefinitely to access user data. This is equally critical to signature validation.

**Independent Test**: Can be fully tested by creating tokens with past expiration dates and verifying they are rejected. Also test tokens with future expiration dates that should be accepted. Delivers time-bound security for all authentication sessions.

**Acceptance Scenarios**:

1. **Given** a JWT token with an expiration time in the past, **When** the token is sent to a protected endpoint, **Then** the system rejects it with "Token has expired" or similar error
2. **Given** a JWT token with an expiration time in the future, **When** the token is sent to a protected endpoint, **Then** the system accepts it and processes the request
3. **Given** a JWT token without an 'exp' claim, **When** the token is sent to a protected endpoint, **Then** the system rejects it for missing required expiration claim

---

### User Story 3 - Signature Verification (Priority: P1)

As a backend developer, I need the JWT middleware to cryptographically verify token signatures to ensure tokens were issued by our authentication service and haven't been tampered with.

**Why this priority**: Without signature verification, anyone can create fake tokens or modify existing ones. This is foundational to JWT security and must work correctly for the authentication system to be trustworthy.

**Independent Test**: Can be fully tested by creating tokens signed with different keys and verifying that only tokens signed with the correct secret are accepted. Delivers cryptographic integrity guarantees for all authenticated requests.

**Acceptance Scenarios**:

1. **Given** a JWT token signed with the correct secret key, **When** the token is verified, **Then** signature validation passes and claims are accessible
2. **Given** a JWT token signed with an incorrect secret key, **When** the token is verified, **Then** signature validation fails and request is rejected
3. **Given** a JWT token with a valid structure but corrupted signature, **When** the token is verified, **Then** the system detects the corruption and rejects the token
4. **Given** the JWT_SECRET environment variable is correctly configured, **When** tokens are validated, **Then** the system uses the correct algorithm (HS256) and secret for verification

---

### Edge Cases

- What happens when a token is valid but the user_id claim is missing? (System should reject with clear error)
- What happens when a token is valid but the user_id claim contains an invalid UUID format? (System should reject - already handled)
- What happens when JWT_SECRET environment variable is missing or empty? (System should fail fast with clear error message)
- What happens when a token uses an unsupported algorithm (e.g., RS256 instead of HS256)? (System should reject during verification)
- What happens when a token is structurally invalid (not three dot-separated parts)? (System should reject with parsing error)
- What happens when the token is completely malformed or random text? (System should reject gracefully without crashing)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate JWT token signatures using the configured JWT_SECRET and algorithm before accepting any token
- **FR-002**: System MUST reject tokens with invalid or tampered signatures, returning HTTP 401 Unauthorized
- **FR-003**: System MUST check token expiration claims ('exp') and reject expired tokens with HTTP 401 Unauthorized
- **FR-004**: System MUST use `jwt.decode()` with `verify=True` option instead of `jwt.get_unverified_claims()` for all token validation
- **FR-005**: System MUST verify that tokens contain required claims (sub/user_id/id for user identification, exp for expiration)
- **FR-006**: System MUST reject tokens missing required claims with HTTP 401 Unauthorized and descriptive error messages
- **FR-007**: System MUST use the HS256 algorithm (or configured JWT_ALGORITHM) consistently for token verification
- **FR-008**: System MUST validate tokens before extracting any claims or user information from them
- **FR-009**: System MUST handle token verification errors gracefully without exposing internal security details in error messages
- **FR-010**: System MUST ensure JWT_SECRET is configured and fail fast at startup if missing (already implemented)
- **FR-011**: System MUST pass all 11 security tests for JWT validation, expiration, and signature verification

### Key Entities

- **JWT Token**: Cryptographic token containing claims about authenticated user, signed with shared secret
  - Required claims: `sub`/`user_id`/`id` (user identifier), `exp` (expiration timestamp)
  - Optional claims: `email`, `iat` (issued at)
  - Must be signed with HS256 algorithm using JWT_SECRET

- **CurrentUser**: Represents authenticated user extracted from valid JWT token
  - Attributes: `user_id` (UUID string), `email` (optional string)
  - Only created after successful token verification

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 11 failing JWT authentication tests pass successfully (100% test pass rate)
- **SC-002**: Zero tokens with invalid signatures are accepted by the system (0% false acceptance rate)
- **SC-003**: All expired tokens are rejected immediately when presented to protected endpoints (100% expiration enforcement)
- **SC-004**: Token verification completes within acceptable time bounds (under 50ms per token for HS256 verification)
- **SC-005**: System rejects 100% of tampered or forged tokens through signature validation
- **SC-006**: Protected endpoints return consistent 401 Unauthorized responses for all authentication failures (invalid, expired, missing tokens)

## Assumptions *(optional)*

- The JWT_SECRET environment variable is shared between the frontend (Better-Auth) and backend and is at least 32 characters
- All tokens are signed using HS256 algorithm (symmetric signing with shared secret)
- Tokens are sent via HTTP Authorization header with "Bearer" scheme
- The frontend (Better-Auth) correctly sets the 'exp' claim on all issued tokens
- The python-jose library is already installed and supports HS256 signature verification
- Existing test fixtures (`test_jwt_token`, `expired_jwt_token`, `test_user_id`) provide valid test scenarios
- The current implementation uses `jwt.get_unverified_claims()` which bypasses all security checks

## Out of Scope *(optional)*

- Implementing asymmetric key verification (RS256, EdDSA) - current system uses HS256 symmetric keys
- Adding JWKS (JSON Web Key Set) endpoint support - not required for symmetric key validation
- Implementing token refresh mechanisms - handled by Better-Auth frontend
- Adding rate limiting for authentication failures - already exists in separate middleware
- Changing the token structure or claims - Better-Auth controls token format
- Supporting multiple signing algorithms simultaneously - system uses HS256 only
- Adding token revocation or blacklisting - out of scope for this security fix

## Dependencies *(optional)*

- **python-jose[cryptography]**: JWT library that provides `jwt.decode()` with signature verification
- **JWT_SECRET environment variable**: Must be configured in `.env` and match frontend BETTER_AUTH_SECRET
- **Better-Auth frontend**: Issues tokens that this backend validates - token format must remain compatible
- **Existing test suite**: 11 failing tests in `backend/tests/test_auth.py` that must pass after implementation
- **FastAPI security module**: HTTPBearer authentication scheme for extracting tokens from headers

## Security Considerations *(optional)*

### Critical Security Vulnerabilities Being Fixed

1. **No Signature Verification**: Current code uses `jwt.get_unverified_claims()` which accepts ANY token without validating the signature. An attacker can forge tokens with arbitrary claims.

2. **No Expiration Checking**: Expired tokens are currently accepted, meaning stolen tokens work indefinitely.

3. **No Integrity Validation**: Tampered tokens (modified payload) are accepted as long as they're structurally valid JSON.

### Security Guarantees After Fix

- **Cryptographic Integrity**: Only tokens signed with the correct JWT_SECRET will be accepted
- **Time-Bounded Access**: Tokens expire based on 'exp' claim and cannot be used after expiration
- **Tamper Detection**: Any modification to token payload will cause signature verification to fail
- **Fail-Secure Design**: All validation failures result in 401 rejection, not fallback to insecure mode

### Best Practices to Follow

- Always use `jwt.decode()` with `verify=True` (default) instead of `jwt.get_unverified_claims()`
- Validate both signature and expiration in a single operation using library defaults
- Use constant-time comparison for secrets to prevent timing attacks (handled by jose library)
- Never log token contents or secrets in production (remove debug print statements after fixing)
- Fail fast if JWT_SECRET is missing rather than falling back to insecure defaults

## Notes *(optional)*

### Current Implementation Issues

The current implementation in `backend/auth/jwt_middleware.py:100-106` has a critical security flaw:

```python
# Decode JWT without verification first to see payload
print(f"[JWT Debug] Attempting to decode token WITHOUT verification...")
unverified_payload = jwt.get_unverified_claims(token)
print(f"[JWT Debug] Unverified payload: {unverified_payload}")

# For now, use unverified payload (TODO: Add proper EdDSA verification with JWKS)
payload = unverified_payload
```

This code explicitly bypasses ALL security checks with the TODO comment suggesting EdDSA/JWKS is needed, but the system actually uses HS256 symmetric keys which are fully supported by python-jose.

### Test Coverage

The 11 failing tests likely include:
- Valid token acceptance (should pass once verification is enabled)
- Expired token rejection (currently fails - expired tokens accepted)
- Invalid signature rejection (currently fails - signatures not checked)
- Tampered payload rejection (currently fails - no integrity check)
- Missing user_id claim rejection (may pass - validated after extraction)
- Various token format validations

### Implementation Priority

Fix should be straightforward - replace `jwt.get_unverified_claims()` with `jwt.decode()` using proper parameters:
- `token`: The JWT string
- `key`: JWT_SECRET from environment
- `algorithms`: [JWT_ALGORITHM] (HS256)
- Ensure `verify=True` is set (or omitted since it's default)
- Handle JWTError exceptions for expired and invalid tokens

This single change should fix the majority of the 11 failing tests by enabling proper cryptographic validation.
