# Technology Research: JWT Authentication Security Fix

**Feature**: 001-jwt-auth-fix
**Date**: 2025-12-16
**Phase**: Implementation (Research & Technology Validation)

---

## R1: python-jose Library JWT Decode Capabilities

### Decision
Use `python-jose`'s `jwt.decode()` function with default verification enabled (verify=True) to validate JWT tokens with HS256 signature verification and automatic expiration checking.

### Implementation Pattern

**Basic JWT Decode with Verification**:
```python
from jose import jwt, JWTError

# Decode JWT with full verification
try:
    payload = jwt.decode(
        token,
        secret_key,
        algorithms=['HS256']
    )
    # token is valid, payload contains claims
except JWTError as e:
    # Token is invalid, expired, or tampered
    pass
```

**Detailed Decode with Explicit Options**:
```python
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

decoded = jwt.decode(
    token,
    'secret',
    algorithms=['HS256'],
    options={
        'verify_signature': True,      # Verify HMAC signature (default: True)
        'verify_exp': True,            # Verify expiration claim (default: True)
        'verify_nbf': True,            # Verify not-before claim (default: True)
        'verify_iat': True,            # Verify issued-at claim (default: True)
        'verify_aud': False,           # Don't verify audience (default: False)
        'require_exp': True,           # Require exp claim to be present
        'require_iat': True,           # Require iat claim to be present
        'leeway': 10                   # 10 seconds leeway for time-based claims
    }
)
```

**Error Handling Specifics**:
```python
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
except ExpiredSignatureError:
    # Token exp claim is in the past
    print("Token has expired")
except JWTClaimsError as e:
    # Claims validation failed (e.g., missing required claim)
    print(f"Invalid claims: {e}")
except JWTError as e:
    # General JWT error (signature invalid, malformed, etc.)
    print(f"JWT validation failed: {e}")
```

### Key Findings from Documentation

**python-jose API Signature** (from Context7):
```python
jwt.decode(
    token: str,
    key: str | bytes | dict | list,
    algorithms: list[str],
    options: dict | None = None,
    audience: str | None = None,
    issuer: str | None = None,
    subject: str | None = None
) -> dict
```

**Default Verification Behavior**:
- **verify_signature**: `True` by default - HMAC signature is ALWAYS verified with provided key
- **verify_exp**: `True` by default - Expiration time (`exp` claim) is automatically checked
- **verify_nbf**: `True` by default - Not-before time (`nbf` claim) is checked if present
- **verify_iat**: `True` by default - Issued-at time (`iat` claim) is validated
- **leeway**: `0` by default - No time tolerance for expiration checks
- **require_exp**: `False` by default - `exp` claim is optional (but should be required)

**HS256 Signature Verification**:
- python-jose fully supports HS256 (HMAC with SHA-256)
- Signature is verified using constant-time comparison (timing attack resistant)
- If signature doesn't match, raises `JWTError` immediately
- Algorithm MUST be in `algorithms` list to be accepted (prevents algorithm confusion attacks)

**Expiration Validation Details**:
- Automatically validates `exp` claim against current UTC timestamp
- If `exp` is in the past, raises `ExpiredSignatureError` (subclass of `JWTClaimsError`)
- Applies `leeway` to allow for clock skew (default 0, should use 10-30 seconds in production)
- Returns without raising if `exp` is missing (unless `require_exp=True`)

**Version Info**:
- python-jose version with HS256 support: **All versions** (library has always supported HS256)
- Current stable version: **3.3.0** or later
- Context7 benchmark score: **80.95** (High reputation, 53 code snippets)

### Exception Hierarchy

```python
from jose.exceptions import JWTError, JWTClaimsError, ExpiredSignatureError

# Exception hierarchy:
JWTError (base exception)
├── JWTClaimsError
│   └── ExpiredSignatureError
└── (other JWT errors)

# Usage pattern:
try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
except ExpiredSignatureError:
    # Handle expired token specifically
    pass
except JWTClaimsError as e:
    # Handle other claims validation errors
    pass
except JWTError as e:
    # Handle general JWT errors (signature invalid, malformed, etc.)
    pass
```

### Rationale
- python-jose is battle-tested and widely used in production Python applications
- HS256 verification is cryptographically sound for symmetric key scenarios
- Default behavior is secure (verification enabled by default)
- Expiration is checked automatically without extra code
- Clear exception hierarchy allows specific error handling
- Algorithm restriction prevents algorithm confusion attacks

### Alternatives Considered
1. **PyJWT**: Also supports HS256, but python-jose has better integration with FastAPI/Starlette
2. **authlib**: More heavyweight, includes OIDC support (overkill for this use case)
3. **Custom verification**: Never implement cryptography yourself - use trusted libraries

### Documentation References
- python-jose GitHub: https://github.com/mpdavis/python-jose
- python-jose JWT API: https://python-jose.readthedocs.io/en/latest/jws/api.html
- Context7 Documentation: https://context7.com/mpdavis/python-jose/llms.txt

---

## R2: Better-Auth JWT Token Format

### Decision
Better-Auth generates JWT tokens with HS256 algorithm by default, using the `sub` (subject) claim as the primary user identifier, with standard OIDC/JWT claims.

### Token Structure and Claims

**Better-Auth Default JWT Payload** (from Context7 documentation):
```json
{
  "sub": "user_uuid_string",
  "email": "user@example.com",
  "iat": 1702756800,
  "exp": 1702843200,
  "jti": "unique_jwt_id",
  "aud": "https://example.com",
  "iss": "https://example.com"
}
```

**Standard Claims Documentation** (from Context7):
```typescript
// From Better-Auth JWT plugin configuration
jwt({
  jwt: {
    issuer: "https://example.com",           // iss claim
    audience: "https://example.com",         // aud claim
    expirationTime: "1h",                    // exp claim (duration)
    getSubject: (session) => {
      // by default the subject is the user id
      return session.user.email  // or session.user.id
    }
  }
})
```

**Default User ID Claim**:
- **Primary claim**: `sub` - Contains user ID (follows OIDC specification)
- **Type**: String (UUID format from Neon PostgreSQL)
- **Always present**: Yes, required for user identification
- **Custom payload option**: Can be customized via `definePayload` function

**Other Standard Claims**:
- `email`: User's email address
- `iat`: Issued-at timestamp (seconds since epoch)
- `exp`: Expiration timestamp (seconds since epoch)
- `aud`: Audience (typically the application URL)
- `iss`: Issuer (typically the auth service URL)
- `jti`: JWT ID (unique identifier for the token)

### Better-Auth Configuration Defaults

**JWT Algorithm**:
- Default: **HS256** (symmetric HMAC with SHA-256)
- Uses `BETTER_AUTH_SECRET` environment variable
- `BETTER_AUTH_SECRET` must match backend `JWT_SECRET`

**Token Expiration**:
- Default: **24 hours** (or configured via `expirationTime`)
- Expiration time is stored in `exp` claim (UNIX timestamp)
- Frontend should refresh before expiration

**Session Configuration**:
```typescript
session: {
  expiresIn: 60 * 60 * 24,              // 24 hours in seconds
  updateAge: 60 * 60,                   // Update session every hour
  cookieCache: {
    enabled: true,
    maxAge: 60 * 60 * 24                // Match token expiration
  }
}
```

### Token Verification Strategy

**Backend Verification Pattern** (from Context7):
```typescript
// From Better-Auth JWT plugin documentation
async function validateToken(token: string) {
  try {
    const storedJWKS = {
      keys: [{
        // JWKS key data
      }]
    };
    const JWKS = createLocalJWKSet({
      keys: storedJWKS.data?.keys!,
    })
    const { payload } = await jwtVerify(token, JWKS, {
      issuer: 'http://localhost:3000',
      audience: 'http://localhost:3000',
    })
    return payload
  } catch (error) {
    console.error('Token validation failed:', error)
    throw error
  }
}
```

**For this project (FastAPI)**:
- Use `sub` claim as the primary user_id source
- Fallback to `user_id` claim if `sub` is missing (compatibility)
- Reject tokens missing `sub`/`user_id` claim
- Verify signature with shared `JWT_SECRET`
- Verify expiration with standard `exp` claim

### Test Fixture Validation

From conftest.py:
```python
payload = {
    "sub": str(test_user_id),           # Primary claim
    "user_id": str(test_user_id),       # Fallback claim
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(hours=1),  # Expires in 1 hour
    "iat": datetime.utcnow(),
}
```

This confirms:
- Better-Auth uses `sub` as primary identifier
- Tokens include both `sub` and `user_id` for compatibility
- Tokens have `exp` claim for expiration validation
- Tokens have `iat` claim for issue-at validation

### Rationale
- **HS256 with shared secret**: Simpler than RS256 for monolithic deployments
- **Standard claims**: Follows RFC 7519 (JWT) and OpenID Connect specifications
- **Token expiration**: Time-bound access keys limit leaked token impact
- **Automatic Better-Auth handling**: No need to manually create tokens

### Alternatives Considered
1. **RS256 with JWKS**: Overkill for this project, adds key management complexity
2. **Custom claim structure**: Non-standard claims complicate integration
3. **No expiration**: Dangerous security practice, leaked tokens become permanent backdoors

### Documentation References
- Better-Auth JWT Plugin: https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/plugins/jwt.mdx
- JWT RFC 7519: https://tools.ietf.org/html/rfc7519
- OpenID Connect Core: https://openid.net/specs/openid-connect-core-1_0.html
- Context7 Better-Auth: https://better-auth.com/docs/concepts/jwt

---

## R3: JWTError Exception Hierarchy

### Decision
Use exception hierarchy provided by python-jose to handle JWT validation failures with specific error recovery logic for different failure modes.

### Exception Hierarchy and Usage

**Complete Exception Structure**:
```python
from jose import JWTError
from jose.exceptions import JWTClaimsError, ExpiredSignatureError

# Base exception type
JWTError
├── JWTClaimsError (claim validation failed)
│   ├── ExpiredSignatureError (exp claim in past)
│   ├── JWTClaimsError (other claim issues - missing required claim, etc.)
│   └── (other claim-specific errors)
└── (signature/parsing errors for malformed tokens)
```

### Error Handling by Failure Mode

**1. Expired Token** → `ExpiredSignatureError`:
```python
try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
except ExpiredSignatureError:
    # Token exp claim is in the past
    raise HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
```

**2. Invalid Signature** → `JWTError` (base):
```python
try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
except JWTError:
    # Signature verification failed (wrong secret, tampered payload, etc.)
    raise HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
```

**3. Missing Required Claim** → `JWTClaimsError`:
```python
try:
    payload = jwt.decode(
        token,
        secret,
        algorithms=['HS256'],
        options={'require_exp': True}
    )
except JWTClaimsError:
    # Required exp claim is missing
    raise HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
```

**4. Malformed Token** → `JWTError`:
```python
try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
except JWTError:
    # Token doesn't follow JWT format (not 3 dot-separated parts, invalid base64, etc.)
    raise HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
```

**5. Unsupported Algorithm** → `JWTError`:
```python
try:
    # Token uses RS256 but we only accept HS256
    payload = jwt.decode(token, secret, algorithms=['HS256'])
except JWTError:
    # Algorithm not in allowed list
    raise HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
```

### Best Practices for Exception Handling

**Specific Catch (Recommended)**:
```python
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
except ExpiredSignatureError:
    # Handle expired token
    logging.warning(f"Expired token rejected")
except JWTClaimsError as e:
    # Handle claim validation errors
    logging.warning(f"Invalid JWT claims: {e}")
except JWTError as e:
    # Handle signature/parsing errors
    logging.warning(f"Invalid JWT: {e}")
```

**Generic Catch (Simpler)**:
```python
from jose import jwt, JWTError

try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
except JWTError as e:
    # All JWT validation errors
    raise HTTPException(status_code=401, detail="Could not validate credentials")
```

### Exception Properties

**All exceptions inherit from JWTError**:
```python
try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
except JWTError as e:
    # Exception properties:
    error_type = type(e).__name__        # 'ExpiredSignatureError', 'JWTError', etc.
    error_message = str(e)               # Detailed error message
    # All are subclasses of JWTError, so catch them with `except JWTError:`
```

### Testing Exception Behavior

From test_auth.py patterns:
```python
def test_get_current_user_with_expired_token(expired_jwt_token: str):
    """Expired token should raise HTTPException with 401."""
    credentials = MockCredentials(expired_jwt_token)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail
```

This shows:
- Expired tokens raise HTTPException (wrapped by get_current_user)
- Invalid tokens raise HTTPException
- Status code is always 401 for any JWT validation failure
- Error message is generic for security (no info leakage)

### Rationale
- **ExpiredSignatureError**: Specific exception for expired tokens (semantic clarity)
- **JWTClaimsError**: Specific exception for claim validation failures
- **JWTError**: Base class catches all JWT-related errors
- **Fail-secure**: All failures result in 401, no fallback to unverified claims
- **No information leakage**: Generic error messages don't reveal token structure

### Alternatives Considered
1. **Catch generic Exception**: Catches too much, hides bugs
2. **No exception handling**: Unverified tokens would crash the app
3. **Custom exception wrapper**: Unnecessary, python-jose exceptions are sufficient

### Documentation References
- python-jose Exceptions: https://github.com/mpdavis/python-jose/blob/master/jose/exceptions.py
- python-jose Error Handling: https://github.com/mpdavis/python-jose/blob/master/docs/jws/index.md
- RFC 7519 Error Claims: https://tools.ietf.org/html/rfc7519#section-3.1

---

## R4: Shared Secret Management for HS256

### Decision
Share the same 32+ character cryptographic secret between Better-Auth (frontend) and FastAPI (backend) via environment variables for HS256 symmetric key signing and verification.

### Configuration Pattern

**Backend (.env)**:
```bash
JWT_SECRET=<32+ random bytes in base64 or hex>
JWT_ALGORITHM=HS256
```

**Frontend (.env.local)**:
```bash
BETTER_AUTH_SECRET=<same value as JWT_SECRET>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Generation Command**:
```bash
# Generate 32 random bytes (256 bits) encoded as base64
openssl rand -base64 32

# Or as hex (64 hex chars = 32 bytes)
openssl rand -hex 32
```

**Example value**:
```
Base64: TkFHbk1aS3kxODhyVDBQSE5LUkVGKzRXL2pFUVNXOFU=
Hex:    1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
```

### Secret Validation

**Minimum Requirements**:
- Length: **32+ bytes** (256+ bits recommended)
- Entropy: Random, not predictable
- Encoding: Base64, hex, or plain string (python-jose accepts all)
- Uniqueness: Different per environment (dev, staging, production)

**From backend code** (jwt_middleware.py line 15-30):
```python
def get_jwt_secret() -> str:
    """Get JWT secret from environment, with validation."""
    secret = os.getenv("JWT_SECRET", "")
    if not secret:
        raise ValueError(
            "JWT_SECRET environment variable is not set. "
            "Please configure it in .env file or environment. "
            "It must match the BETTER_AUTH_SECRET in the frontend."
        )
    return secret
```

### Verification During Development

**Check if secrets match**:
```bash
# Backend
echo $JWT_SECRET
# Output: TkFHbk1aS3kxODhyVDBQSE5LUkVGKzRXL2pFUVNXOFU=

# Frontend (in different terminal)
echo $BETTER_AUTH_SECRET
# Output: TkFHbk1aS3kxODhyVDBQSE5LUkVGKzRXL2pFUVNXOFU=
# ✓ Secrets match
```

**Test token validation**:
```bash
# Create token with secret X on frontend
# Try to verify with secret X on backend
# Result: Success (secrets match)

# Try to verify with secret Y on backend
# Result: Failure - signature mismatch (secrets differ)
```

### Environment-Specific Configuration

**Development**:
```bash
# Can be simple for testing
JWT_SECRET=dev-secret-32-bytes-minimum-required-here
```

**Staging/Production**:
```bash
# Must be cryptographically random
JWT_SECRET=$(openssl rand -base64 32)
```

### Security Considerations

**DO:**
- Generate secrets cryptographically (use `openssl rand`)
- Store in `.env` file (add to `.gitignore`)
- Use same secret for frontend and backend
- Rotate secrets periodically in production
- Use different secrets per environment

**DON'T:**
- Commit `.env` files to version control
- Use weak passwords or predictable secrets
- Hardcode secrets in source code
- Reuse secrets across environments
- Share secrets in unencrypted channels

### From Spec Notes

Per spec.md (Assumptions section, line 109):
> "The JWT_SECRET environment variable is shared between the frontend (Better-Auth) and backend and is at least 32 characters"

This confirms the architectural decision is already documented.

### Rationale
- **Symmetric key simplicity**: HS256 needs shared secret, no key pair distribution
- **Single secret source**: Easier to rotate and audit
- **Environment variables**: Standard practice for secrets in web apps
- **Minimum 32 bytes**: 256-bit keys provide strong cryptographic guarantees
- **Validation on startup**: Fail fast if secrets aren't configured

### Alternatives Considered
1. **RS256 with JWKS**: Asymmetric keys (public/private) - overkill for monolithic deployment
2. **Separate secrets per service**: More complex key management without added security benefit
3. **Hardcoded secrets**: Never acceptable for production
4. **Single secret in code**: Code review/version control vulnerability

### Documentation References
- OpenSSL rand: https://www.openssl.org/docs/man1.1.1/man1/rand.html
- JWT Secret Best Practices: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- Better-Auth Configuration: https://better-auth.com/docs/installation

---

## R5: Signature Verification Algorithm Support

### Decision
Use HS256 (HMAC with SHA-256) algorithm for symmetric key signing and verification, which is fully supported by python-jose and required by Better-Auth for this project architecture.

### Algorithm Specifications

**HS256 Details**:
- **Name**: HMAC with SHA-256
- **Key type**: Shared symmetric secret (not public/private)
- **Key size**: 32+ bytes (256+ bits)
- **Signature size**: 32 bytes (256 bits)
- **Speed**: Very fast (HMAC is efficient)
- **Security level**: 256-bit (strong)

**python-jose Support**:
```python
from jose import jwt

# HS256 is fully supported
payload = jwt.decode(
    token,
    secret_key,
    algorithms=['HS256']  # HS256 is accepted
)

# Encoding with HS256
token = jwt.encode(
    payload,
    secret_key,
    algorithm='HS256'  # HS256 generates HMAC signature
)
```

**Alternative Algorithms** (for reference):
```python
# Other symmetric algorithms (less commonly used)
jwt.decode(token, secret, algorithms=['HS256', 'HS384', 'HS512'])

# Asymmetric algorithms (not used in this project)
jwt.decode(token, public_key, algorithms=['RS256', 'RS384', 'RS512'])  # RSA
jwt.decode(token, public_key, algorithms=['ES256', 'ES384', 'ES512'])  # ECDSA
jwt.decode(token, public_key, algorithms=['PS256', 'PS384', 'PS512'])  # RSA PSS
```

### Algorithm Selection Rationale

**Why HS256 for this project**:
1. **Monolithic deployment**: Frontend and backend in same organization
2. **Shared infrastructure**: Can safely share symmetric key
3. **Simplicity**: No key pair distribution complexity
4. **Performance**: HMAC is very fast (microseconds per verification)
5. **Battle-tested**: Standard algorithm, widely used

**Why not RS256**:
1. Adds key pair management (generate, distribute, rotate)
2. Requires JWKS endpoint for public key distribution
3. Slower than HS256 (RSA is computationally expensive)
4. Overkill for monolithic architecture
5. Only needed if third parties need to verify tokens

### Algorithm Configuration in python-jose

**Restrict to Specific Algorithm** (recommended):
```python
# Only accept HS256 (prevents algorithm confusion attacks)
payload = jwt.decode(token, secret, algorithms=['HS256'])

# This prevents attackers from forcing algorithm=none or RS256
```

**Algorithm Confusion Attack Prevention**:
```python
# VULNERABLE: Accepts any algorithm
# payload = jwt.decode(token, secret, algorithms=['HS256', 'RS256', 'none'])

# SECURE: Only accept expected algorithm
payload = jwt.decode(token, secret, algorithms=['HS256'])
```

### Verification Process with HS256

**How HS256 verification works** (from python-jose):
```
1. Split token into 3 parts: header.payload.signature
2. Decode header (base64url decode)
3. Verify algorithm in header is 'HS256'
4. Calculate HMAC-SHA256(header.payload, secret_key)
5. Compare calculated signature with received signature (constant-time)
6. If match, proceed; else raise JWTError
```

**Constant-time comparison**:
- python-jose uses timing-attack resistant comparison
- Prevents attackers from using timing differences to guess signatures
- Implemented correctly internally (no need to worry about this)

### Test Coverage for HS256

From conftest.py (line 133):
```python
return jwt.encode(payload, TEST_JWT_SECRET, algorithm=TEST_JWT_ALGORITHM)
```

Where `TEST_JWT_ALGORITHM = "HS256"` (line 28)

This confirms:
- Test fixtures generate HS256 tokens
- Backend configuration uses HS256
- Better-Auth (frontend) uses HS256

### Documentation References
- HMAC Specification: https://tools.ietf.org/html/rfc2104
- JWT Algorithms: https://tools.ietf.org/html/rfc7518#section-3.1
- python-jose Algorithm Support: https://github.com/mpdavis/python-jose#algorithms-supported
- Algorithm Confusion Attacks: https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/

---

## Summary of Findings

| Research Area | Decision | Implementation |
|---|---|---|
| **JWT Decode API** | Use `jwt.decode()` with default verify=True | Replace `get_unverified_claims()` with `decode()` |
| **Signature Verification** | HS256 with python-jose | Verify algorithm is in `['HS256']` list |
| **Expiration Checking** | Automatic with `exp` claim validation | Enabled by default in `jwt.decode()` |
| **Better-Auth Claims** | Use `sub` claim as primary user_id | Extract from `payload.get("sub")` |
| **Exception Handling** | Catch JWTError and subclasses | Handle ExpiredSignatureError separately if needed |
| **Shared Secret** | 32+ bytes in JWT_SECRET env var | Match between frontend and backend |

---

## Implementation Checklist

- [x] python-jose fully supports HS256 signature verification
- [x] Expiration is automatically validated when present in token
- [x] Better-Auth uses `sub` claim for user_id (standard practice)
- [x] JWTError exception hierarchy allows specific error handling
- [x] Shared secret must be 32+ bytes (cryptographically random)
- [x] Algorithm must be restricted to `['HS256']` to prevent attacks
- [x] Default behavior of `jwt.decode()` is secure (verify=True)

---

## References

**python-jose**:
- GitHub: https://github.com/mpdavis/python-jose
- Documentation: https://python-jose.readthedocs.io/
- Context7: https://context7.com/mpdavis/python-jose/llms.txt

**Better-Auth**:
- Official Site: https://better-auth.com
- JWT Plugin: https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/plugins/jwt.mdx
- Context7: https://better-auth.com/docs/concepts/jwt

**Standards & Security**:
- RFC 7519 (JWT): https://tools.ietf.org/html/rfc7519
- RFC 2104 (HMAC): https://tools.ietf.org/html/rfc2104
- OWASP JWT: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

