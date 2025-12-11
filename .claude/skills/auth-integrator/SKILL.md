---
name: auth-integrator
description: Integrate Better Auth with JWT for secure user sessions and API protection in full-stack apps.
version: 1.0
---

# Auth Integrator Skill

## Overview
This skill configures Better Auth in the Next.js frontend and implements JWT verification in the FastAPI backend. It ensures all API requests are filtered by authenticated user_id, using a shared secret for signing/verification.

## Instructions
1. Parse the authentication spec (e.g., @specs/features/authentication.md) for requirements like signup/signin flows and token handling.
2. Generate frontend configuration:
   - Update /frontend/lib/auth.ts with Better Auth setup to issue JWT tokens on login.
   - Include session management and API header injection (Authorization: Bearer <token>).
3. Generate backend verification:
   - Add JWT dependency in /backend/routes/ (e.g., in tasks.py and auth.py).
   - Use PyJWT or fastapi_jwt_auth to verify tokens, extract user_id, and filter queries (e.g., SQLModel select where user_id == current_user.id).
4. Handle shared secret:
   - Reference environment variable BETTER_AUTH_SECRET (add to .env.example if missing).
   - Ensure both frontend and backend use the same secret.
5. Add error handling: Raise HTTP 401/403 for invalid/expired tokens.
6. Output generated code snippets or full files, ready for integration.

## Inputs
- Spec reference: e.g., @specs/features/authentication.md
- Optional: Existing code paths (e.g., /backend/db.py for user model)

## Outputs
- Updated /frontend/lib/auth.ts
- New/updated /backend/routes/auth.py (if needed)
- JWT verification functions in relevant routes (e.g., /backend/routes/tasks.py)
- Suggestions for docker-compose.yml or .env for secrets

## Examples
### Example 1: Basic Login Config
Input Spec: "Implement user signup/signin with JWT."
Output:
- Frontend: Better Auth config with JWT issuer.
- Backend: Dependency to get_current_user from token.

### Example 2: Secure API Endpoint
Input Spec: "Secure GET /api/tasks to return only user's tasks."
Output: Route handler with depends(get_current_user), query filtered by user.id.

## Dependencies
- Frontend: better-auth library (add to package.json if missing).
- Backend: fastapi, jose (for JWT), or similar (add to pyproject.toml).

## Testing
Run the included script jwt-verify-test.py with sample token to validate decoding.