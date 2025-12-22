# Phase 3 Frontend - AI Chatbot Interface

Next.js 16 frontend application that provides a natural language chat interface for todo management. Built with React 19, Better-Auth, and Tailwind CSS.

## Overview

This application provides a conversational interface where users can manage their todos using natural language. It integrates with the Phase 3 backend (OpenAI agent) to enable commands like "Add a task to buy groceries" or "Show me my incomplete tasks".

## Architecture

```
┌─────────────────┐
│   User Browser  │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 3 Frontend│ (This Application)
│  (Next.js 16)   │
│                 │
│  - Chat UI      │
│  - Better-Auth  │
│  - AuthGuard    │
└────────┬────────┘
         │ POST /api/{user_id}/chat
         ▼
┌─────────────────┐
│ Phase 3 Backend │
│  (OpenAI Agent) │
│                 │
│  - NLP          │
│  - Conversation │
│  - MCP Tools    │
└─────────────────┘
```

## Features

- **Chat Interface**: Clean, responsive chat UI for natural language interactions
- **Better-Auth Integration**: Secure authentication with JWT sessions
- **Protected Routes**: AuthGuard component for route protection
- **Real-time Updates**: Instant feedback on task operations
- **Loading States**: Smooth loading indicators during API calls
- **Error Handling**: User-friendly error messages
- **Responsive Design**: Mobile-first Tailwind CSS styling
- **Type Safety**: Full TypeScript support with strict mode

## Prerequisites

- **Node.js**: 18.0.0 or higher
- **npm**: 9.0.0 or higher
- **Phase 3 Backend**: Must be running (port 8001 by default)
- **Database**: Neon PostgreSQL (shared with Phase 2)
- **Better-Auth Secret**: Must match JWT_SECRET from backend services

## Installation

### 1. Navigate to directory

```bash
cd hackathon-todo/phase3-frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure environment variables

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```bash
# Database Configuration (same as Phase 2)
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Better-Auth Configuration (MUST match backend JWT_SECRET)
BETTER_AUTH_SECRET=<same-as-jwt-secret>
BETTER_AUTH_URL=http://localhost:3001

# Backend URLs
NEXT_PUBLIC_BACKEND_URL=http://localhost:8001
NEXT_PUBLIC_PHASE2_BACKEND_URL=http://localhost:8000
```

**CRITICAL**: `BETTER_AUTH_SECRET` must be **identical** to `JWT_SECRET` from Phase 2 and Phase 3 backends.

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will start on `http://localhost:3001`.

### Production Build

```bash
npm run build
npm start
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## Application Structure

```
phase3-frontend/
├── app/
│   ├── layout.tsx              # Root layout with Better-Auth provider
│   ├── globals.css             # Global styles
│   ├── chat/
│   │   └── page.tsx            # Main chat interface page
│   ├── login/
│   │   └── page.tsx            # Login page
│   ├── signup/
│   │   └── page.tsx            # Signup page
│   └── api/
│       └── auth/
│           └── [...all]/route.ts  # Better-Auth API routes
├── components/
│   ├── ChatInterface.tsx       # Main chat component
│   ├── ChatMessage.tsx         # Message bubble component
│   ├── AuthGuard.tsx           # Route protection wrapper
│   └── LoadingSpinner.tsx      # Loading indicator
├── lib/
│   ├── auth.ts                 # Better-Auth configuration
│   ├── auth-client.ts          # Client-side auth utilities
│   ├── types.ts                # TypeScript interfaces
│   └── api.ts                  # API client for backend
├── public/                     # Static assets
├── .env.local.example          # Environment template
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript configuration
├── tailwind.config.ts          # Tailwind CSS configuration
├── vercel.json                 # Vercel deployment config
└── README.md                   # This file
```

## Key Components

### ChatInterface

Main chat component that handles user input and displays conversation history.

**Location**: `components/ChatInterface.tsx`

**Features**:
- Message input with send button
- Scrollable message history
- Loading states during API calls
- Error handling and display
- Auto-scroll to latest message

**Usage**:
```tsx
import ChatInterface from '@/components/ChatInterface';

<ChatInterface userId={userId} />
```

### ChatMessage

Individual message bubble component for user and assistant messages.

**Location**: `components/ChatMessage.tsx`

**Features**:
- Different styling for user vs assistant messages
- Timestamp display
- Markdown support (optional)
- Tool call indicators

**Props**:
```tsx
{
  role: 'user' | 'assistant',
  content: string,
  timestamp: string
}
```

### AuthGuard

Wrapper component that protects routes requiring authentication.

**Location**: `components/AuthGuard.tsx`

**Features**:
- Checks Better-Auth session
- Redirects to login if unauthenticated
- Shows loading state during auth check
- Passes user data to children

**Usage**:
```tsx
<AuthGuard>
  <ProtectedComponent />
</AuthGuard>
```

### LoadingSpinner

Simple loading indicator component.

**Location**: `components/LoadingSpinner.tsx`

## Pages

### Chat Page (`/chat`)

Main application page with chat interface.

**Features**:
- Protected route (requires authentication)
- Real-time chat with AI assistant
- Conversation history
- Natural language task management

**Access**: Navigate to `http://localhost:3001/chat` after login

### Login Page (`/login`)

User authentication page.

**Features**:
- Email/password login
- Better-Auth integration
- Redirect to chat after successful login
- Link to signup page

**Access**: `http://localhost:3001/login`

### Signup Page (`/signup`)

User registration page.

**Features**:
- Email/password signup
- Better-Auth integration
- Automatic login after registration
- Redirect to chat page

**Access**: `http://localhost:3001/signup`

## API Integration

### Backend API Client

**Location**: `lib/api.ts`

```typescript
import { sendChatMessage } from '@/lib/api';

const response = await sendChatMessage(userId, "Add a task to buy groceries");
```

**Functions**:
- `sendChatMessage(userId: string, message: string)`: Sends message to Phase 3 backend

**Error Handling**:
- Network errors
- Authentication errors (401)
- Rate limiting (429)
- Server errors (500)

### Better-Auth Configuration

**Location**: `lib/auth.ts`

**Features**:
- Database session storage
- PostgreSQL adapter (Kysely)
- JWT token generation
- Session management

**Client Usage**:
```typescript
import { authClient } from '@/lib/auth-client';

// Sign in
await authClient.signIn.email({
  email: 'user@example.com',
  password: 'password'
});

// Sign out
await authClient.signOut();

// Get session
const session = await authClient.getSession();
```

## User Flow

### 1. Authentication

```
User visits /chat
  ↓
AuthGuard checks session
  ↓
No session → Redirect to /login
  ↓
User enters credentials
  ↓
Better-Auth validates
  ↓
JWT token generated
  ↓
Redirect to /chat
```

### 2. Chat Interaction

```
User types message in chat input
  ↓
Click send or press Enter
  ↓
Message sent to Phase 3 backend with JWT
  ↓
Backend processes with OpenAI agent
  ↓
Agent calls MCP tools as needed
  ↓
Response returned to frontend
  ↓
Message displayed in chat UI
```

### 3. Task Operations

**Add Task**:
```
User: "Add a task to buy groceries"
  ↓
Assistant: "I've added 'buy groceries' to your tasks"
```

**List Tasks**:
```
User: "What are my tasks?"
  ↓
Assistant: "You have 3 tasks:
1. Buy groceries (incomplete)
2. Review report (incomplete)
3. Call dentist (completed)"
```

**Complete Task**:
```
User: "I finished buying groceries"
  ↓
Assistant: "Great! I've marked 'buy groceries' as complete"
```

## Development

### Adding a New Component

1. Create component in `components/`:

```tsx
// components/MyComponent.tsx
export default function MyComponent() {
  return <div>My Component</div>;
}
```

2. Import and use:

```tsx
import MyComponent from '@/components/MyComponent';
```

### Adding a New Page

1. Create route in `app/`:

```tsx
// app/my-page/page.tsx
export default function MyPage() {
  return <div>My Page</div>;
}
```

2. Access at `http://localhost:3001/my-page`

### Styling with Tailwind

Use Tailwind utility classes:

```tsx
<div className="flex items-center justify-center p-4 bg-blue-500 text-white rounded-lg">
  Hello World
</div>
```

Configure Tailwind in `tailwind.config.ts`.

## Deployment

### Vercel Deployment

This application is optimized for Vercel deployment.

#### 1. Install Vercel CLI

```bash
npm install -g vercel
```

#### 2. Login to Vercel

```bash
vercel login
```

#### 3. Set Environment Variables

In Vercel dashboard, add:
- `DATABASE_URL` (from Neon PostgreSQL)
- `BETTER_AUTH_SECRET` (same as backend JWT_SECRET)
- `BETTER_AUTH_URL` (your Vercel domain)
- `NEXT_PUBLIC_BACKEND_URL` (deployed Phase 3 backend URL)
- `NEXT_PUBLIC_PHASE2_BACKEND_URL` (deployed Phase 2 backend URL)

#### 4. Deploy

```bash
vercel --prod
```

Vercel will automatically detect Next.js and deploy with optimal settings.

#### 5. Verify Deployment

Visit your Vercel URL and test authentication and chat functionality.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | - | JWT secret (must match backend) |
| `BETTER_AUTH_URL` | Yes | - | Application URL |
| `NEXT_PUBLIC_BACKEND_URL` | Yes | - | Phase 3 backend API URL |
| `NEXT_PUBLIC_PHASE2_BACKEND_URL` | No | - | Phase 2 backend URL (reference) |

**Note**: Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

## Troubleshooting

### Build Errors

**Error**: `Module not found: Can't resolve '@/components/...'`

**Solution**: Check `tsconfig.json` has correct path aliases.

### Authentication Issues

**Error**: `Better-Auth session validation failed`

**Solution**:
- Verify `BETTER_AUTH_SECRET` matches backend `JWT_SECRET`
- Check database connectivity
- Clear browser cookies and retry

### API Connection Issues

**Error**: `Failed to fetch: Network request failed`

**Solution**:
- Verify Phase 3 backend is running
- Check `NEXT_PUBLIC_BACKEND_URL` in `.env.local`
- Ensure CORS is configured in backend

### Chat Not Working

**Error**: Messages not sending or receiving responses

**Solution**:
- Check browser console for errors
- Verify JWT token is valid (not expired)
- Ensure Phase 3 backend is accessible
- Check OpenAI API key is valid in backend

## Security Considerations

### JWT Tokens
- Stored in Better-Auth session (HTTP-only cookies)
- Never exposed to client-side JavaScript
- Automatically included in API requests

### Environment Variables
- Never commit `.env.local` to version control
- Use Vercel environment variables in production
- Rotate `BETTER_AUTH_SECRET` regularly

### CORS
- Backend must allow frontend origin
- Set `CORS_ORIGINS` in Phase 3 backend to include frontend URL

### Input Validation
- Message length validated client-side (1-2000 chars)
- Additional validation on backend
- XSS protection via React's default escaping

## Performance Optimization

### Next.js Features
- **Server Components**: Default rendering strategy
- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Use `next/image` for images
- **Font Optimization**: Use `next/font` for fonts

### Best Practices
- Use `loading.tsx` for route-level loading states
- Implement proper error boundaries
- Optimize bundle size with tree shaking
- Use React.memo for expensive components

## Testing

### Manual Testing

1. **Authentication Flow**:
   - Sign up new user
   - Sign in existing user
   - Verify session persistence
   - Test sign out

2. **Chat Functionality**:
   - Send message
   - Receive response
   - Verify task operations
   - Test error handling

3. **Protected Routes**:
   - Access `/chat` without auth (should redirect)
   - Access `/chat` with auth (should work)

### Automated Testing (Future)

Consider adding:
- **Jest**: Unit tests for components
- **React Testing Library**: Component integration tests
- **Playwright**: End-to-end tests
- **Cypress**: E2E and integration tests

## Dependencies

### Core Dependencies
- **Next.js 16**: React framework
- **React 19**: UI library
- **Better-Auth**: Authentication
- **Kysely**: Database query builder
- **pg**: PostgreSQL client
- **Tailwind CSS**: Utility-first CSS

### Development Dependencies
- **TypeScript 5**: Type safety
- **ESLint**: Code linting
- **PostCSS**: CSS processing
- **Autoprefixer**: CSS vendor prefixes

## Contributing

When contributing to this application:

1. **Follow React best practices**
2. **Use TypeScript** for all new code
3. **Style with Tailwind** utility classes
4. **Add proper types** to all components and functions
5. **Test authentication** flows before committing
6. **Update documentation** for new features

## Related Services

- **Phase 2 Frontend**: Original task management UI (`frontend/`)
- **Phase 3 Backend**: OpenAI agent orchestration (`phase3-backend/`)
- **Phase 3 MCP Server**: MCP tool server (`phase3-mcp-server/`)

## Support

For issues or questions:
1. Check this README
2. Review Next.js documentation: https://nextjs.org/docs
3. Review Better-Auth documentation: https://better-auth.com
4. Check the Phase 3 specification (`specs/002-chatbot-interface/`)

## Version History

- **1.0.0** (2024-01-15): Initial release
  - Chat interface with natural language support
  - Better-Auth authentication
  - Protected routes with AuthGuard
  - Responsive Tailwind styling
  - Full TypeScript support

## License

This project is part of the Hackathon Todo application.
