# Authentication Integration Examples

## Example 1: Basic Email/Password Authentication

### Frontend Setup (`/frontend/lib/auth.ts`)

```typescript
import { betterAuth } from "better-auth"
import { nextCookies } from "better-auth/next-js"

export const auth = betterAuth({
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day (update session every day)
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  plugins: [nextCookies()],
})

export type Session = typeof auth.$Infer.Session
```

### Client Hooks (`/frontend/lib/auth-client.ts`)

```typescript
"use client"

import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000",
})

export const { 
  signIn, 
  signUp, 
  signOut, 
  useSession,
  useActiveOrganization,
} = authClient
```

### Backend Verification (`/backend/middleware/auth.py`)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from typing import Optional
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET environment variable not set")

ALGORITHM = "HS256"

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """Verify JWT token and extract claims"""
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
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "payload": payload
        }
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

async def get_current_user_id(auth_data: dict = Depends(verify_token)) -> str:
    """Extract user_id from verified token"""
    return auth_data["user_id"]

async def get_current_user(auth_data: dict = Depends(verify_token)) -> dict:
    """Get full user data from token"""
    return auth_data
```

### Protected Route (`/backend/routes/tasks.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..dependencies.auth import get_current_user_id
from ..db import get_session
from ..models import Task, TaskCreate, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/", response_model=List[Task])
async def get_tasks(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session)
):
    """Get all tasks for the authenticated user"""
    statement = select(Task).where(Task.user_id == user_id)
    tasks = db.exec(statement).all()
    return tasks

@router.post("/", response_model=Task)
async def create_task(
    task: TaskCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session)
):
    """Create a new task for the authenticated user"""
    db_task = Task(**task.model_dump(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session)
):
    """Update a task (only if owned by authenticated user)"""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session)
):
    """Delete a task (only if owned by authenticated user)"""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
```

---

## Example 2: OAuth + Email/Password

### Frontend with Google OAuth (`/frontend/lib/auth.ts`)

```typescript
import { betterAuth } from "better-auth"
import { nextCookies } from "better-auth/next-js"

export const auth = betterAuth({
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  plugins: [nextCookies()],
})
```

### Sign In Page (`/frontend/app/login/page.tsx`)

```tsx
"use client"

import { useState } from "react"
import { authClient } from "@/lib/auth-client"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    
    try {
      await authClient.signIn.email({
        email,
        password,
      })
      router.push("/dashboard")
    } catch (err) {
      setError("Invalid email or password")
    }
  }

  const handleGoogleSignIn = async () => {
    try {
      await authClient.signIn.social({
        provider: "google",
        callbackURL: "/dashboard",
      })
    } catch (err) {
      setError("Failed to sign in with Google")
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-8 p-8">
        <h2 className="text-2xl font-bold">Sign In</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}
        
        <form onSubmit={handleEmailSignIn} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border rounded"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border rounded"
            required
          />
          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          >
            Sign In with Email
          </button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="bg-white px-2 text-gray-500">Or continue with</span>
          </div>
        </div>

        <button
          onClick={handleGoogleSignIn}
          className="w-full bg-white border border-gray-300 py-2 rounded hover:bg-gray-50 flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            {/* Google icon SVG */}
          </svg>
          Sign in with Google
        </button>
      </div>
    </div>
  )
}
```

---

## Example 3: Authenticated API Client

### Axios Client with Auto-Retry (`/frontend/lib/api-client.ts`)

```typescript
import axios from 'axios'
import { authClient } from './auth-client'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const session = await authClient.useSession()
    if (session.data?.token) {
      config.headers.Authorization = `Bearer ${session.data.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for auth errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Try to refresh the session
        await authClient.session.refresh()
        
        // Retry the original request
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed, redirect to login
        await authClient.signOut()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // If 403, user doesn't have permission
    if (error.response?.status === 403) {
      console.error('Access denied:', error.response.data)
    }

    return Promise.reject(error)
  }
)

export default apiClient
```

### Usage in Components

```typescript
import apiClient from '@/lib/api-client'

async function fetchTasks() {
  try {
    const response = await apiClient.get('/api/tasks')
    return response.data
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
    throw error
  }
}

async function createTask(task: TaskCreate) {
  const response = await apiClient.post('/api/tasks', task)
  return response.data
}
```

---

## Example 4: Role-Based Access Control (RBAC)

### Enhanced Token with Roles

```python
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class TokenData(BaseModel):
    user_id: str
    email: str
    role: UserRole

async def verify_token_with_role(
    credentials: HTTPAuthCredentials = Depends(security)
) -> TokenData:
    """Verify token and extract user data including role"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        return TokenData(
            user_id=payload.get("sub"),
            email=payload.get("email"),
            role=UserRole(payload.get("role", "user"))
        )
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def require_role(required_role: UserRole):
    """Dependency to check if user has required role"""
    async def check_role(
        token_data: TokenData = Depends(verify_token_with_role)
    ) -> TokenData:
        role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.USER: 1,
            UserRole.ADMIN: 2,
        }
        
        if role_hierarchy[token_data.role] < role_hierarchy[required_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role"
            )
        return token_data
    
    return check_role
```

### Admin-Only Endpoint

```python
@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: TokenData = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_session)
):
    """Delete a user (admin only)"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted by admin {admin.user_id}"}
```

---

## Example 5: Using Better Auth MCP Server

### Checking MCP Availability

```typescript
// In your skill workflow, check if MCP tools are available
const mcpToolsAvailable = await checkForMCPTools([
  'better_auth_get_config',
  'better_auth_validate_schema',
])

if (mcpToolsAvailable) {
  // Use MCP to inspect current configuration
  const config = await useMCPTool('better_auth_get_config')
  console.log('Current Better Auth config:', config)
  
  // Generate code based on actual configuration
  const providers = config.socialProviders || {}
  // ... use provider info to generate appropriate code
} else {
  // Fall back to manual configuration
  console.log('Better Auth MCP not available, using default patterns')
}
```

### Validating Schema with MCP

```python
# After generating auth setup, validate with MCP
validation_result = await better_auth_mcp.validate_schema({
    "database_url": os.getenv("DATABASE_URL")
})

if not validation_result.valid:
    print("Schema issues found:")
    for issue in validation_result.issues:
        print(f"  - {issue.table}: {issue.message}")
```

---

## Example 6: Database Models

### User Model (`/backend/models/user.py`)

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "user"
    
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    email_verified: bool = Field(default=False)
    name: Optional[str] = None
    image: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Session(SQLModel, table=True):
    __tablename__ = "session"
    
    id: str = Field(primary_key=True)
    expires_at: datetime
    token: str = Field(unique=True, index=True)
    user_id: str = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Task Model with User Relationship

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    __tablename__ = "task"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
```

---

## Environment Variable Templates

### Frontend `.env.local`

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-at-least-32-characters-long
BETTER_AUTH_URL=http://localhost:3000

# OAuth Providers (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend `.env`

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp

# Better Auth (must match frontend)
BETTER_AUTH_SECRET=your-secret-key-at-least-32-characters-long

# Optional
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Generate Secret Script

```bash
#!/bin/bash
# generate-secret.sh

# Generate a secure random secret
SECRET=$(openssl rand -hex 32)

echo "Generated BETTER_AUTH_SECRET:"
echo "$SECRET"
echo ""
echo "Add this to both frontend and backend .env files:"
echo "BETTER_AUTH_SECRET=$SECRET"
```
