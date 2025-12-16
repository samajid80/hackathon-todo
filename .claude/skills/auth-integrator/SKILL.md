---
name: auth-integrator
description: Integrate Better Auth with JWT for secure user sessions and API protection in full-stack apps. Uses Better Auth MCP server when available for schema inspection, configuration validation, and code generation. Use when implementing authentication, securing APIs, or setting up user session management in Next.js + FastAPI applications.
version: 2.0
---

# Auth Integrator Skill

## Overview
This skill configures Better Auth in the Next.js frontend and implements JWT verification in the FastAPI backend. It ensures all API requests are filtered by authenticated user_id, using a shared secret for signing/verification.

**MCP Enhancement**: When Better Auth MCP server is available, this skill leverages it to:
- Inspect Better Auth schemas and configuration
- Validate authentication setup
- Generate type-safe code based on your Better Auth configuration
- Ensure consistency between frontend and backend implementations

## Workflow

### Step 1: Check MCP Availability and Gather Context

**Check for Better Auth MCP tools:**
```
Check if Better Auth MCP server is available by looking for tools like:
- better_auth_get_config
- better_auth_list_providers
- better_auth_validate_schema
```

**If Better Auth MCP is available:**
1. Use MCP tools to inspect existing Better Auth configuration
2. Retrieve current provider setup and session configuration
3. Get schema information for database models

**If Better Auth MCP is NOT available:**
1. Parse the authentication spec manually (e.g., @specs/features/authentication.md)
2. Use default Better Auth patterns
3. Proceed with standard implementation

**Gather project context:**
- Locate spec file: @specs/features/authentication.md or similar
- Identify project structure: /frontend and /backend directories
- Check existing auth files: /frontend/lib/auth.ts, /backend/routes/auth.py

### Step 2: Design Authentication Flow

Based on requirements (from MCP or spec), determine:
1. **Authentication methods**: Email/password, OAuth providers, magic links?
2. **Session strategy**: JWT, database sessions, or hybrid?
3. **Token handling**: Where tokens are stored (cookies, localStorage, headers)?
4. **Protected resources**: Which API endpoints need authentication?

**Create implementation plan:**
```markdown
Example plan:
- Frontend: Better Auth with email/password + Google OAuth
- Token: JWT in httpOnly cookie
- Backend: JWT verification middleware
- Protected: /api/tasks, /api/profile
- Public: /api/health, /api/auth/*
```

### Step 3: Generate Frontend Configuration

**Location**: `/frontend/lib/auth.ts` (or `/frontend/lib/auth-client.ts`)

**Using Better Auth MCP** (if available):
```
Use better_auth_generate_config tool to create configuration based on:
- Selected providers
- Session strategy
- Database schema
```

**Manual approach** (if MCP unavailable):
```typescript
// Generate Better Auth configuration
import { betterAuth } from "better-auth"
import { nextCookies } from "better-auth/next-js"

export const auth = betterAuth({
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL,
  },
  emailAndPassword: {
    enabled: true,
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },
  secret: process.env.BETTER_AUTH_SECRET,
  plugins: [nextCookies()],
})
```

**Key elements to include:**
1. Import necessary Better Auth modules
2. Configure database connection
3. Set up authentication providers
4. Configure session management
5. Reference BETTER_AUTH_SECRET from environment
6. Add plugins (e.g., nextCookies for Next.js)

**Client-side setup** (`/frontend/lib/auth-client.ts`):
```typescript
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000",
})

export const { signIn, signUp, signOut, useSession } = authClient
```

### Step 4: Implement API Token Injection

**Location**: `/frontend/lib/api-client.ts` or API utility

**Generate fetch wrapper that automatically includes JWT:**
```typescript
async function authenticatedFetch(url: string, options: RequestInit = {}) {
  const session = await auth.api.getSession()
  
  if (!session?.token) {
    throw new Error("No authentication token available")
  }

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${session.token}`,
    },
  })
}
```

**Or for axios users:**
```typescript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
})

apiClient.interceptors.request.use(async (config) => {
  const session = await auth.api.getSession()
  if (session?.token) {
    config.headers.Authorization = `Bearer ${session.token}`
  }
  return config
})
```

### Step 5: Generate Backend JWT Verification

**Location**: `/backend/middleware/auth.py` or `/backend/dependencies/auth.py`

**Core JWT verification function:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """
    Verify JWT token and extract user_id
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        return {"user_id": user_id, "payload": payload}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user_id(auth_data: dict = Depends(verify_token)) -> str:
    """
    Extract user_id from verified token
    """
    return auth_data["user_id"]
```

**Add to requirements** (`/backend/pyproject.toml` or `/backend/requirements.txt`):
```toml
dependencies = [
    "fastapi",
    "python-jose[cryptography]",
    "python-multipart",
]
```

### Step 6: Secure API Endpoints

**Pattern for protected endpoints:**

**Before** (unsecured):
```python
@router.get("/tasks")
async def get_tasks(db: Session = Depends(get_db)):
    tasks = db.exec(select(Task)).all()
    return tasks
```

**After** (secured with user filtering):
```python
@router.get("/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Filter tasks by authenticated user
    tasks = db.exec(select(Task).where(Task.user_id == user_id)).all()
    return tasks
```

**For all routes that need protection:**
1. Add `user_id: str = Depends(get_current_user_id)` parameter
2. Filter database queries by `user_id`
3. Validate ownership before updates/deletes

**Example secured CRUD operations:**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

router = APIRouter()

@router.post("/tasks")
async def create_task(
    task: TaskCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    db_task = Task(**task.dict(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
```

### Step 7: Environment Configuration

**Update `.env.example`:**
```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Update `.env`** (create if missing):
```bash
BETTER_AUTH_SECRET=$(openssl rand -hex 32)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**For Docker setup** (`docker-compose.yml`):
```yaml
services:
  frontend:
    environment:
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - NEXT_PUBLIC_API_URL=http://backend:8000
    
  backend:
    environment:
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - DATABASE_URL=${DATABASE_URL}
```

### Step 8: Add Error Handling

**Frontend error handling:**
```typescript
// In your API client
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      await authClient.signOut()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

**Backend error responses:**
```python
# Already included in verify_token function above
# Returns HTTP 401 for invalid/expired tokens
# Returns HTTP 403 for unauthorized access to resources
```

## MCP Tool Usage Guide

When Better Auth MCP server is available, use these tools strategically:

### Configuration Inspection
```
Tool: better_auth_get_config
Use when: Starting implementation or debugging config issues
Returns: Current Better Auth configuration, providers, plugins
```

### Schema Validation
```
Tool: better_auth_validate_schema
Use when: Ensuring database schema matches Better Auth requirements
Returns: Validation results, missing tables/columns
```

### Provider Information
```
Tool: better_auth_list_providers
Use when: Setting up OAuth or external auth providers
Returns: Available providers and their configuration options
```

### Code Generation
```
Tool: better_auth_generate_types
Use when: Creating TypeScript types for frontend
Returns: Type definitions based on your schema
```

## Output Checklist

Ensure the following files are created/updated:

**Frontend:**
- [ ] `/frontend/lib/auth.ts` - Better Auth server configuration
- [ ] `/frontend/lib/auth-client.ts` - Client-side auth hooks
- [ ] `/frontend/lib/api-client.ts` - API wrapper with auth headers
- [ ] `/frontend/package.json` - Add better-auth dependency
- [ ] `/frontend/.env.example` - Document required env vars

**Backend:**
- [ ] `/backend/middleware/auth.py` or `/backend/dependencies/auth.py` - JWT verification
- [ ] `/backend/routes/*.py` - Update routes with authentication
- [ ] `/backend/pyproject.toml` or `requirements.txt` - Add python-jose
- [ ] `/backend/.env.example` - Document BETTER_AUTH_SECRET

**Root:**
- [ ] `.env.example` - Shared environment variables
- [ ] `docker-compose.yml` - Update with secrets (if using Docker)
- [ ] `README.md` - Add auth setup instructions

## Testing Recommendations

After implementation, suggest these tests:

1. **Token Generation Test**: Verify JWT is created on login
2. **Token Verification Test**: Confirm backend can decode tokens
3. **Protected Endpoint Test**: Ensure 401 without token, 200 with valid token
4. **User Isolation Test**: Verify users only see their own data
5. **Token Expiration Test**: Check expired tokens are rejected

**Create test script** (`/backend/tests/test_auth.py`):
```python
import pytest
from fastapi.testclient import TestClient
from jose import jwt
import os

def test_protected_endpoint_without_token(client: TestClient):
    response = client.get("/api/tasks")
    assert response.status_code == 401

def test_protected_endpoint_with_valid_token(client: TestClient):
    token = jwt.encode(
        {"sub": "test-user-id"},
        os.getenv("BETTER_AUTH_SECRET"),
        algorithm="HS256"
    )
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_user_data_isolation(client: TestClient):
    # Test that user A cannot access user B's data
    pass
```

## Common Issues & Solutions

### Issue: "No authentication token available"
**Solution**: Ensure user is logged in and session is valid. Check browser cookies/localStorage.

### Issue: "Could not validate credentials" 
**Solution**: Verify BETTER_AUTH_SECRET matches between frontend and backend.

### Issue: CORS errors on auth endpoints
**Solution**: Add CORS middleware in FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Token not included in requests
**Solution**: Check that API client is using the authenticated fetch wrapper or axios interceptor.

## Dependencies

**Frontend:**
```json
{
  "dependencies": {
    "better-auth": "^1.0.0",
    "next": "^14.0.0"
  }
}
```

**Backend:**
```toml
dependencies = [
    "fastapi>=0.109.0",
    "python-jose[cryptography]>=3.3.0",
    "sqlmodel>=0.0.14"
]
```

## Additional Resources

When MCP server is unavailable, refer to:
- Better Auth docs: https://better-auth.com
- FastAPI security: https://fastapi.tiangolo.com/tutorial/security/
- JWT.io for token debugging

## Examples

See `references/examples.md` for complete working examples of common authentication patterns.
