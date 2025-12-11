# Technology Research: Phase 2 Full-Stack Todo Web Application

**Feature**: 002-fullstack-web-app
**Date**: 2025-12-11
**Phase**: 0 (Research & Technology Validation)

## Overview

This document consolidates research findings for all technology integration questions identified in the implementation plan. Each research area documents the decision made, rationale, alternatives considered, and implementation patterns.

---

## R1: Better-Auth JWT Integration with FastAPI

### Decision
Use Better-Auth to generate JWTs in Next.js frontend with HS256 algorithm, sharing a secret key with FastAPI backend for validation.

### Configuration Approach

**Better-Auth (Frontend)**:
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  jwt: {
    enabled: true,
    algorithm: "HS256",
    secret: process.env.JWT_SECRET!, // Shared with backend
    expiresIn: "24h"
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 86400 // 24 hours
    }
  }
});
```

**FastAPI JWT Middleware (Backend)**:
```python
# auth/jwt_middleware.py
from jose import JWTError, jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Validate JWT and extract user_id."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")  # Better-Auth uses 'sub' for user_id
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "email": payload.get("email")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### JWT Payload Structure
Better-Auth generates JWTs with these standard claims:
- `sub`: user_id (UUID)
- `email`: user email
- `iat`: issued at timestamp
- `exp`: expiration timestamp
- `jti`: JWT ID (unique identifier)

### Shared Secret Management
Store JWT secret in environment variables:
- Frontend: `.env.local` → `JWT_SECRET=<same-secret>`
- Backend: `.env` → `JWT_SECRET=<same-secret>`

Generate secret with: `openssl rand -hex 32`

### Rationale
- Better-Auth provides built-in JWT generation with minimal configuration
- HS256 is sufficient for this use case (frontend and backend controlled by same org)
- Shared secret approach is simpler than RS256 (public/private key pairs)
- Standard JWT claims ensure compatibility with FastAPI

### Alternatives Considered
1. **Auth.js (NextAuth)**: More complex configuration, less explicit JWT control
2. **Custom JWT generation**: Requires implementing full auth flow, unnecessary complexity
3. **RS256 with key pairs**: Overkill for monolithic deployment, adds key management complexity

### Documentation References
- Better-Auth JWT: https://better-auth.com/docs/concepts/jwt
- Python JOSE: https://python-jose.readthedocs.io/en/latest/

---

## R2: SQLModel with Neon PostgreSQL

### Decision
Use SQLModel for ORM with Alembic for migrations, connecting to Neon PostgreSQL with async SQLAlchemy.

### Database Connection Pattern

**Connection String Format**:
```
postgresql://[user]:[password]@[endpoint]/[database]?sslmode=require
```

**Database Configuration (Backend)**:
```python
# db.py
from sqlmodel import create_engine, SQLModel, Session
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine for Neon
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Connection pool size
    max_overflow=10  # Max overflow connections
)

def init_db():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session():
    """Provide a transactional scope for database operations."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

### SQLModel Model Pattern

**Task Model**:
```python
# models/task.py
from sqlmodel import SQLModel, Field
from datetime import datetime, date
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Status(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Task(SQLModel, table=True):
    """Task ORM model."""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.PENDING, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Composite index for efficient filtered queries
    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
        Index("idx_user_due_date", "user_id", "due_date"),
    )
```

### Alembic Migration Setup

**Initialize Alembic**:
```bash
cd backend
alembic init migrations
```

**Alembic Configuration** (`alembic.ini`):
```ini
sqlalchemy.url = ${DATABASE_URL}
```

**Generate Migration**:
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Neon-Specific Considerations
- SSL required: Add `?sslmode=require` to connection string
- Connection pooling: Use `pool_pre_ping=True` for serverless architecture
- Branching: Use Neon branches for testing migrations before production

### Rationale
- SQLModel combines SQLAlchemy ORM with Pydantic models → single source of truth
- Automatic validation from Pydantic reduces errors
- FastAPI natively supports Pydantic, seamless integration
- Alembic provides robust migration management
- Neon's serverless architecture eliminates database management overhead

### Alternatives Considered
1. **Pure SQLAlchemy + separate Pydantic**: More boilerplate, duplicate definitions
2. **Django ORM**: Requires Django framework, overkill for FastAPI
3. **Tortoise ORM**: Async-first but less mature than SQLAlchemy

### Documentation References
- SQLModel: https://sqlmodel.tiangolo.com
- Alembic: https://alembic.sqlalchemy.org/en/latest/
- Neon Connection: https://neon.tech/docs/connect/connect-from-any-app

---

## R3: Next.js 16 App Router with Better-Auth

### Decision
Use Next.js 16 App Router with Better-Auth for authentication, implementing route protection via middleware and server components.

### Protected Route Pattern

**Middleware Approach** (`middleware.ts`):
```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { auth } from './lib/auth';

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({ headers: request.headers });

  // Protect /tasks routes
  if (request.nextUrl.pathname.startsWith('/tasks')) {
    if (!session) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  // Redirect authenticated users away from login/signup
  if (['/login', '/signup'].includes(request.nextUrl.pathname)) {
    if (session) {
      return NextResponse.redirect(new URL('/tasks', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/tasks/:path*', '/login', '/signup'],
};
```

**Server Component Auth Check**:
```typescript
// app/tasks/page.tsx
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function TasksPage() {
  const session = await auth.api.getSession({ headers: headers() });

  if (!session) {
    redirect('/login');
  }

  return (
    <div>
      {/* Task list UI */}
    </div>
  );
}
```

### Session Management

**Better-Auth Configuration**:
```typescript
// lib/auth.ts
export const auth = betterAuth({
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL!
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Phase 2: Disabled for simplicity
  },
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60, // Update session every hour
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24
    }
  }
});
```

**Session Storage**:
- Better-Auth uses HTTP-only cookies for session management
- JWT stored in cookie, automatically sent with requests
- No localStorage needed (more secure)

### Redirect Logic
1. Unauthenticated users accessing `/tasks/*` → redirect to `/login`
2. Authenticated users accessing `/login` or `/signup` → redirect to `/tasks`
3. Root `/` → redirect to `/tasks` (protected) or `/login` (unauthenticated)

### Rationale
- App Router middleware provides centralized route protection
- Server components enable auth checks before page render
- Better-Auth handles session lifecycle automatically
- Cookie-based session is more secure than localStorage
- Middleware runs at edge, fast redirects

### Alternatives Considered
1. **Client-side route guards**: Less secure, SEO issues, flash of unauthenticated content
2. **Higher-order components**: More boilerplate than middleware
3. **Auth.js (NextAuth)**: More complex setup, less control over JWT

### Documentation References
- Next.js Middleware: https://nextjs.org/docs/app/building-your-application/routing/middleware
- Better-Auth Next.js: https://better-auth.com/docs/integrations/next-js

---

## R4: CORS Configuration for FastAPI + Next.js

### Decision
Configure FastAPI CORS middleware with environment-specific allowed origins, supporting credentials for JWT authentication.

### CORS Configuration Pattern

**FastAPI Setup** (`main.py`):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Todo API", version="1.0.0")

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Frontend URLs
    allow_credentials=True,  # Required for cookies/Authorization headers
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)
```

**Environment Variables**:
- Development: `CORS_ORIGINS=http://localhost:3000`
- Production: `CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`

### Preflight Request Handling
- FastAPI automatically handles OPTIONS requests for CORS preflight
- Middleware validates Origin header against allowed origins
- Credentials flag enables Authorization header in cross-origin requests

### Security Considerations
1. **Never use `allow_origins=["*"]` with `allow_credentials=True`** → security risk
2. Always specify exact origins in production
3. Use environment variables for origin configuration
4. Limit `allow_methods` to only required HTTP methods
5. Consider rate limiting to prevent abuse

### Development vs Production
```python
# Development
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Production
CORS_ORIGINS=https://app.example.com,https://www.app.example.com
```

### Rationale
- FastAPI CORS middleware handles all preflight complexity
- Environment-based configuration supports dev/staging/prod
- Credentials support required for JWT in Authorization header
- Wildcard origins disabled for security
- Max-age caching reduces preflight request overhead

### Alternatives Considered
1. **Nginx reverse proxy CORS**: Adds infrastructure complexity, not needed for development
2. **No CORS (same-origin deployment)**: Not flexible for modern frontend/backend separation
3. **Manual CORS headers**: Error-prone, FastAPI middleware handles it correctly

### Documentation References
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
- MDN CORS: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

## R5: Frontend State Management for Tasks

### Decision
Use direct API calls with React Server Components and client-side state for optimistic updates, avoiding complex state management libraries.

### Implementation Pattern

**API Client** (`lib/api/tasks.ts`):
```typescript
import { auth } from '../auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getAuthHeaders() {
  const session = await auth.api.getSession();
  if (!session?.jwt) throw new Error('Not authenticated');

  return {
    'Authorization': `Bearer ${session.jwt}`,
    'Content-Type': 'application/json',
  };
}

export const tasksApi = {
  async getTasks(filters?: { status?: string; sort_by?: string }) {
    const headers = await getAuthHeaders();
    const params = new URLSearchParams(filters);
    const response = await fetch(`${API_BASE}/api/tasks?${params}`, { headers });
    if (!response.ok) throw new Error('Failed to fetch tasks');
    return response.json();
  },

  async createTask(data: TaskCreate) {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE}/api/tasks`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create task');
    return response.json();
  },

  async updateTask(id: string, data: TaskUpdate) {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE}/api/tasks/${id}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update task');
    return response.json();
  },

  async deleteTask(id: string) {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE}/api/tasks/${id}`, {
      method: 'DELETE',
      headers,
    });
    if (!response.ok) throw new Error('Failed to delete task');
  },

  async completeTask(id: string) {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE}/api/tasks/${id}/complete`, {
      method: 'PATCH',
      headers,
    });
    if (!response.ok) throw new Error('Failed to complete task');
    return response.json();
  },
};
```

**Server Component Pattern** (for initial data):
```typescript
// app/tasks/page.tsx (Server Component)
import { tasksApi } from '@/lib/api/tasks';

export default async function TasksPage() {
  const tasks = await tasksApi.getTasks();

  return <TaskList initialTasks={tasks} />;
}
```

**Client Component with Optimistic Updates**:
```typescript
'use client';
import { useState, useTransition } from 'react';

export function TaskList({ initialTasks }) {
  const [tasks, setTasks] = useState(initialTasks);
  const [isPending, startTransition] = useTransition();

  const handleComplete = async (id: string) => {
    // Optimistic update
    setTasks(prev => prev.map(t => t.id === id ? {...t, status: 'completed'} : t));

    startTransition(async () => {
      try {
        await tasksApi.completeTask(id);
        // Optionally revalidate from server
      } catch (error) {
        // Rollback on error
        setTasks(initialTasks);
        alert('Failed to complete task');
      }
    });
  };

  return (/* UI */);
}
```

### Error Handling Strategy
1. **Network errors**: Show toast notification, allow retry
2. **401 Unauthorized**: Redirect to login
3. **403 Forbidden**: Show "Access denied" message
4. **404 Not Found**: Show "Task not found" message
5. **500 Server Error**: Show generic error message, log to monitoring

### Loading States
- Use React `useTransition` for non-blocking UI updates
- Show loading spinners for initial page load
- Use optimistic updates for instant feedback
- Disable buttons during mutations to prevent double-submit

### Caching Strategy
- Server Components fetch fresh data on navigation
- Use Next.js `revalidatePath` after mutations
- No complex client-side cache needed
- Browser cache headers from FastAPI for GET requests

### Rationale
- Next.js 16 App Router handles data fetching efficiently with Server Components
- React 19 transitions provide built-in optimistic updates
- Direct API calls simpler than Redux/Zustand for this scale
- Server Components reduce client bundle size
- No stale data issues with fresh fetches on navigation

### Alternatives Considered
1. **React Query/TanStack Query**: Excellent caching but adds complexity and bundle size
2. **Zustand**: Good for complex state but overkill for simple CRUD
3. **Redux Toolkit**: Too much boilerplate for this app
4. **Context API**: Performance issues with frequent updates

### Documentation References
- Next.js Data Fetching: https://nextjs.org/docs/app/building-your-application/data-fetching
- React Transitions: https://react.dev/reference/react/useTransition

---

## R6: Responsive UI with Tailwind CSS

### Decision
Use Tailwind CSS mobile-first approach with card layout for mobile and table layout for desktop, leveraging Tailwind's responsive utilities.

### Responsive Layout Pattern

**Breakpoint Strategy**:
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',   // Mobile landscape
      'md': '768px',   // Tablet
      'lg': '1024px',  // Desktop
      'xl': '1280px',  // Large desktop
      '2xl': '1536px', // Extra large
    }
  }
}
```

**Mobile-First Task List**:
```tsx
// components/TaskList.tsx
export function TaskList({ tasks }) {
  return (
    <div>
      {/* Mobile: Cards (default) */}
      <div className="block md:hidden space-y-4">
        {tasks.map(task => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>

      {/* Desktop: Table (md and up) */}
      <div className="hidden md:block">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Priority
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Due Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {tasks.map(task => (
              <TaskRow key={task.id} task={task} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

**Mobile Task Card**:
```tsx
export function TaskCard({ task }) {
  return (
    <div className="bg-white shadow rounded-lg p-4 border-l-4 border-blue-500">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-medium text-lg truncate flex-1">{task.title}</h3>
        <PriorityBadge priority={task.priority} />
      </div>

      {task.description && (
        <p className="text-gray-600 text-sm mb-2 line-clamp-2">
          {task.description}
        </p>
      )}

      <div className="flex justify-between items-center text-sm">
        <span className={`px-2 py-1 rounded ${statusColors[task.status]}`}>
          {task.status}
        </span>
        {task.due_date && (
          <span className="text-gray-500">{formatDate(task.due_date)}</span>
        )}
      </div>

      <div className="mt-3 flex gap-2">
        <button className="flex-1 text-sm px-3 py-2 bg-blue-500 text-white rounded">
          Edit
        </button>
        <button className="flex-1 text-sm px-3 py-2 bg-green-500 text-white rounded">
          Complete
        </button>
        <button className="px-3 py-2 bg-red-500 text-white rounded">
          Delete
        </button>
      </div>
    </div>
  );
}
```

### Component Library Choice
Use **headlessui** for accessible components without opinionated styling:
- Accessible dialogs (delete confirmation)
- Dropdown menus (filters, sorts)
- Transitions and animations
- Integrates perfectly with Tailwind

```bash
npm install @headlessui/react @heroicons/react
```

### Visual Indicators

**Priority Colors**:
```tsx
const priorityColors = {
  low: 'bg-gray-100 text-gray-800',
  medium: 'bg-blue-100 text-blue-800',
  high: 'bg-red-100 text-red-800',
};
```

**Status Colors**:
```tsx
const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
};
```

**Overdue Indicator**:
```tsx
function TaskCard({ task }) {
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status === 'pending';

  return (
    <div className={`
      bg-white shadow rounded-lg p-4 border-l-4
      ${isOverdue ? 'border-red-500' : 'border-blue-500'}
    `}>
      {isOverdue && (
        <div className="mb-2 flex items-center text-red-600 text-sm">
          <ExclamationIcon className="h-4 w-4 mr-1" />
          Overdue
        </div>
      )}
      {/* Rest of card */}
    </div>
  );
}
```

### Rationale
- Tailwind utility-first approach reduces CSS complexity
- Mobile-first design ensures usability on smallest screens
- Card layout better for touch targets on mobile
- Table layout efficient for data density on desktop
- headlessui provides accessibility without CSS conflicts
- Responsive utilities make breakpoint management simple

### Alternatives Considered
1. **Material-UI**: Heavy bundle, opinionated styling, hard to customize
2. **shadcn/ui**: Excellent but requires copy-paste, prefer npm install
3. **DaisyUI**: Pre-built components but less flexible than headlessui
4. **Custom CSS**: More work, Tailwind faster for prototyping

### Documentation References
- Tailwind Responsive Design: https://tailwindcss.com/docs/responsive-design
- Headless UI: https://headlessui.com
- Heroicons: https://heroicons.com

---

## Summary of Decisions

| Research Area | Decision | Key Rationale |
|---------------|----------|---------------|
| Authentication | Better-Auth with HS256 JWT | Simple JWT generation, FastAPI compatibility |
| Database | SQLModel + Alembic + Neon PostgreSQL | Single source of truth, FastAPI integration |
| Frontend Routing | Next.js 16 App Router + middleware | Centralized auth, server components |
| CORS | FastAPI middleware with env-based origins | Security, flexibility, credential support |
| State Management | Direct API calls + Server Components | Simplicity, reduced bundle size |
| UI Framework | Tailwind CSS + headlessui | Mobile-first, accessible, customizable |

All technology choices prioritize simplicity, type safety, and developer experience while meeting Phase 2 constitution requirements.
