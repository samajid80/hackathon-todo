# Frontend Quick Start Guide

## Installation

```bash
cd /home/majid/projects/hackathon-todo/frontend
npm install
```

## Configuration

1. Copy environment template:
```bash
cp .env.local.example .env.local
```

2. Edit `.env.local` with your values:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-here
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

**IMPORTANT**: `BETTER_AUTH_SECRET` must match backend `JWT_SECRET`

## Running

```bash
# Development server
npm run dev

# Production build
npm run build
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

## Directory Structure

```
frontend/
├── app/                    # Next.js pages (App Router)
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Landing page
├── lib/                   # Utilities
│   ├── auth.ts           # Better-Auth config
│   └── api/
│       └── tasks.ts      # API client
├── types/
│   └── task.ts           # TypeScript types
├── styles/
│   └── globals.css       # Tailwind + custom styles
└── components/           # React components
    └── ui/               # Reusable UI components
```

## Usage Examples

### API Client

```typescript
import { getTasks, createTask, updateTask, deleteTask } from "@/lib/api/tasks";

// Get all tasks
const tasks = await getTasks();

// Filter by status
const pending = await getTasks({ status: "pending" });

// Sort by priority
const sorted = await getTasks(undefined, { sortBy: "priority", order: "desc" });

// Create task
const task = await createTask({
  title: "Buy groceries",
  priority: "high",
  due_date: "2025-12-15",
});

// Update task
await updateTask(task.id, { title: "Updated title" });

// Delete task
await deleteTask(task.id);
```

### Custom Tailwind Classes

```tsx
// Buttons
<button className="btn btn-primary">Primary</button>
<button className="btn btn-secondary">Secondary</button>
<button className="btn btn-danger">Delete</button>

// Inputs
<input type="text" className="input" />
<input type="text" className="input input-error" />

// Badges
<span className="badge badge-high">High</span>
<span className="badge badge-medium">Medium</span>
<span className="badge badge-low">Low</span>

// Cards
<div className="card">Card content</div>

// Loading
<div className="spinner w-6 h-6"></div>
```

### Responsive Design

```tsx
// Mobile-first grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Content */}
</div>

// Conditional display
<div className="hidden md:block">Desktop only</div>
<div className="block md:hidden">Mobile only</div>
```

## Breakpoints

- xs: 320px (mobile)
- sm: 640px (mobile landscape)
- md: 768px (tablet)
- lg: 1024px (desktop)
- xl: 1280px (large desktop)
- 2xl: 1536px (extra large)
- 3xl: 2560px (ultra wide)

## Next Steps

After installation:

1. **Verify TypeScript**: `npm run type-check`
2. **Verify Linting**: `npm run lint`
3. **Start Dev Server**: `npm run dev`
4. **Visit**: http://localhost:3000

Then proceed to implement:
- US1: Authentication (signup, login, logout)
- US2: Task creation and viewing
- US3: Filtering and sorting
- US4: Updating and completing
- US5: Deleting tasks

## Troubleshooting

**TypeScript errors?**
- Run `npm run type-check` to see details
- Ensure all imports use `@/` alias

**Cannot connect to API?**
- Verify backend is running at `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` in `.env.local`

**Auth not working?**
- Ensure `BETTER_AUTH_SECRET` matches backend `JWT_SECRET`
- Check database connection in `DATABASE_URL`

## Resources

- Next.js: https://nextjs.org/docs
- Better-Auth: https://better-auth.com/docs
- Tailwind: https://tailwindcss.com/docs
- TypeScript: https://www.typescriptlang.org/docs
