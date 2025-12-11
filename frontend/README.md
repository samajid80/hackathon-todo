# Hackathon Todo - Frontend

This is the frontend application for the Hackathon Todo full-stack web application, built with Next.js 16, React 19, Better-Auth, and Tailwind CSS.

## Technology Stack

- **Framework**: Next.js 16 (App Router)
- **UI Library**: React 19
- **Authentication**: Better-Auth with JWT
- **Styling**: Tailwind CSS 3.4
- **Language**: TypeScript 5.6
- **Package Manager**: npm

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Landing page
│   ├── login/              # Login page (US1)
│   ├── signup/             # Signup page (US1)
│   └── tasks/              # Task management pages (US2-US5)
├── components/             # Reusable React components
│   └── ui/                 # UI components (buttons, inputs, etc.)
├── lib/                    # Utility libraries
│   ├── auth.ts             # Better-Auth configuration
│   └── api/                # API client functions
│       └── tasks.ts        # Task API client
├── styles/                 # Global styles
│   └── globals.css         # Tailwind CSS and custom styles
├── types/                  # TypeScript type definitions
│   └── task.ts             # Task entity types
└── tests/                  # Test files
    ├── unit/               # Unit tests
    └── e2e/                # End-to-end tests
```

## Prerequisites

Before running the frontend, ensure you have:

1. **Node.js 24+** installed
2. **Backend API** running at `http://localhost:8000` (see `../backend/README.md`)
3. **Neon PostgreSQL database** configured (for Better-Auth user storage)

## Environment Setup

### Environment Variables

Copy the environment template:
```bash
cp .env.local.example .env.local
```

Configure the following environment variables in `.env.local`:

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API URL (use HTTPS in production) |
| `BETTER_AUTH_SECRET` | Yes | `openssl rand -base64 32` | Secret for JWT signing (MUST match backend JWT_SECRET) |
| `BETTER_AUTH_URL` | No | `http://localhost:3000` | Frontend URL (for Better-Auth callbacks) |
| `DATABASE_URL` | Yes | `postgresql://user:pass@host.neon.tech/db?sslmode=require` | Neon PostgreSQL for user storage |

**Environment Variable Setup Instructions**:

1. **Copy example file**:
   ```bash
   cp .env.local.example .env.local
   ```

2. **Set NEXT_PUBLIC_API_URL**:
   ```env
   # Development
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # Production
   NEXT_PUBLIC_API_URL=https://api.your-domain.com
   ```

3. **Generate BETTER_AUTH_SECRET** (MUST match backend):
   ```bash
   # Generate the same secret as backend JWT_SECRET
   openssl rand -base64 32
   ```
   Copy this value to both frontend `BETTER_AUTH_SECRET` and backend `JWT_SECRET`.

4. **Set BETTER_AUTH_URL**:
   ```env
   # Development
   BETTER_AUTH_URL=http://localhost:3000

   # Production
   BETTER_AUTH_URL=https://your-domain.com
   ```

5. **Set DATABASE_URL** (same as backend):
   ```env
   DATABASE_URL=postgresql://username:password@host.neon.tech/dbname?sslmode=require
   ```

**Example `.env.local` file**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx1234yzab5678
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:password@host.neon.tech/database?sslmode=require
```

**IMPORTANT Security Notes**:
- The `BETTER_AUTH_SECRET` MUST be the same as the backend `JWT_SECRET`
- Use a strong secret key in production (generate with `openssl rand -base64 32`)
- The `DATABASE_URL` should point to the same Neon PostgreSQL database as the backend
- NEVER commit `.env.local` file to version control!

## Installation

Install dependencies:

```bash
npm install
```

## Running the Application

### Development Mode

Start the development server:

```bash
npm run dev
```

The application will be available at **http://localhost:3000**

### Production Build

Build the application for production:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

## Development Workflow

### Type Checking

Run TypeScript type checking:

```bash
npm run type-check
```

### Linting

Run ESLint to check code quality:

```bash
npm run lint
```

### Testing

**Unit Tests** (to be added in US1-US5):
```bash
npm run test
```

**End-to-End Tests** (to be added in Phase 7):
```bash
npm run test:e2e
```

## API Integration

The frontend communicates with the FastAPI backend through the API client in `lib/api/tasks.ts`.

### Authentication Flow

1. User signs up or logs in via Better-Auth
2. Better-Auth issues a JWT token stored in cookies
3. All API requests automatically include the JWT in the `Authorization` header
4. Backend validates the JWT and extracts the user ID

### API Client Usage

Example of using the API client:

```typescript
import { getTasks, createTask, updateTask, deleteTask } from "@/lib/api/tasks";

// Get all tasks
const tasks = await getTasks();

// Create a new task
const newTask = await createTask({
  title: "Buy groceries",
  priority: "high",
  due_date: "2025-12-15",
});

// Update a task
const updated = await updateTask(taskId, {
  title: "Updated title",
});

// Delete a task
await deleteTask(taskId);
```

## Security Features (Phase 7 - T157-T158)

### XSS Prevention (T157)

The frontend implements multiple layers of XSS protection:

**React Built-in Protection**:
- React automatically escapes all dynamic content by default
- Use `textContent` instead of `innerHTML` for user-generated content
- Never use `dangerouslySetInnerHTML` for untrusted content

**Example - Safe Rendering**:
```typescript
// Safe: React escapes by default
<h1>{task.title}</h1>

// Unsafe: Don't do this with user input
<div dangerouslySetInnerHTML={{ __html: task.description }} />
```

**Backend Validation**:
- All user inputs are validated and sanitized by the backend (T157)
- Title: Max 200 characters, whitespace stripped
- Description: Max 2000 characters, whitespace stripped
- Backend uses Pydantic validators to prevent injection attacks

**Best Practices**:
1. Always use React's JSX syntax for rendering user content
2. Never concatenate user input into HTML strings
3. Use TypeScript to enforce type safety
4. Validate inputs on both client and server
5. Trust the backend to sanitize data before storage

### Content Security Policy (CSP) Headers (T158)

The application uses strict CSP headers to prevent XSS and injection attacks:

**CSP Configuration** (in `next.config.js`):
```javascript
Content-Security-Policy:
  default-src 'self';                          // Only same-origin by default
  script-src 'self' 'unsafe-inline';           // Scripts from same origin + inline (Next.js requirement)
  style-src 'self' 'unsafe-inline';            // Styles from same origin + inline (Tailwind requirement)
  img-src 'self' data: https:;                 // Images from same origin, data URIs, HTTPS
  font-src 'self';                             // Fonts from same origin only
  connect-src 'self' http://localhost:8000;    // API connections (dev: localhost, prod: API domain)
  object-src 'none';                           // No Flash/plugins
  frame-src 'none';                            // No iframes
  base-uri 'self';                             // Restrict base tag
  form-action 'self';                          // Forms submit to same origin only
  frame-ancestors 'none';                      // Prevent embedding
```

**CSP Policy Explanation**:
- `default-src 'self'`: Only allow resources from same origin by default
- `script-src`: Allow scripts from same origin and inline (required for Next.js)
- `style-src`: Allow styles from same origin and inline (required for Tailwind CSS)
- `img-src`: Allow images from same origin, data URIs, and HTTPS CDNs
- `connect-src`: Allow API connections to backend server
- `object-src 'none'`: Block Flash and other plugins
- `frame-src 'none'`: Prevent iframe injection
- `frame-ancestors 'none'`: Prevent page from being embedded

**Additional Security Headers**:
```javascript
X-Frame-Options: DENY                        // Prevent clickjacking (legacy)
X-Content-Type-Options: nosniff             // Prevent MIME sniffing
Referrer-Policy: strict-origin-when-cross-origin  // Control referrer info
Permissions-Policy: camera=(), microphone=()  // Disable unnecessary features
```

**Production Deployment**:
For production, update CSP in `next.config.js`:
1. Replace `http://localhost:8000` with your production API domain
2. Remove `'unsafe-eval'` from script-src if possible
3. Consider using nonce-based CSP for stricter security
4. Enable `upgrade-insecure-requests` for automatic HTTP→HTTPS upgrade

**Testing CSP**:
- Open browser DevTools → Console
- Look for CSP violation warnings
- Adjust CSP directives as needed for legitimate resources
- Use [CSP Evaluator](https://csp-evaluator.withgoogle.com/) to test policy

## Styling with Tailwind CSS

### Custom Classes

The project includes custom utility classes in `styles/globals.css`:

- **Buttons**: `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`
- **Inputs**: `.input`, `.input-error`
- **Badges**: `.badge`, `.badge-low`, `.badge-medium`, `.badge-high`
- **Cards**: `.card`
- **Loading**: `.spinner`

### Responsive Design

The application uses a mobile-first approach with the following breakpoints:

- **xs**: 320px (mobile)
- **sm**: 640px (mobile landscape)
- **md**: 768px (tablet)
- **lg**: 1024px (desktop)
- **xl**: 1280px (large desktop)
- **2xl**: 1536px (extra large desktop)
- **3xl**: 2560px (ultra wide)

Example usage:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Responsive grid layout */}
</div>
```

## Features by User Story

### Phase 1: Setup (Current)
- [x] Next.js 16 project initialized
- [x] Tailwind CSS configured
- [x] Better-Auth setup
- [x] API client created
- [x] TypeScript types defined
- [x] Root layout and landing page
- [x] Security headers and CSP (T158)

### US1: Authentication (To be implemented)
- [ ] Signup page
- [ ] Login page
- [ ] Logout functionality
- [ ] Protected routes
- [ ] Session management

### US2: Create and View Tasks (To be implemented)
- [ ] Task list page
- [ ] Task creation form
- [ ] Task card component
- [ ] Empty state handling

### US3: Filter and Sort Tasks (To be implemented)
- [ ] Filter controls (pending, completed, overdue)
- [ ] Sort controls (priority, due date, status)
- [ ] Overdue indicators

### US4: Update and Complete Tasks (To be implemented)
- [ ] Task edit page
- [ ] Mark complete functionality
- [ ] Optimistic UI updates

### US5: Delete Tasks (To be implemented)
- [ ] Delete confirmation dialog
- [ ] Delete functionality

## Troubleshooting

### Issue: "Cannot connect to backend API"

**Solution**: Ensure the backend is running at `http://localhost:8000` and `NEXT_PUBLIC_API_URL` is set correctly in `.env.local`.

### Issue: "Authentication not working"

**Solution**: Verify that `BETTER_AUTH_SECRET` matches the backend `JWT_SECRET` exactly.

### Issue: "Database connection error"

**Solution**: Check that `DATABASE_URL` points to the correct Neon PostgreSQL database and SSL is enabled.

### Issue: "TypeScript errors"

**Solution**: Run `npm run type-check` to identify type errors. Ensure all imports use the `@/` alias for absolute paths.

### Issue: "CSP violations in browser console" (T158)

**Solution**:
1. Check browser DevTools → Console for CSP violation warnings
2. Identify the blocked resource (script, style, image, etc.)
3. If resource is legitimate, update CSP in `next.config.js`
4. For production, ensure API domain is whitelisted in `connect-src`
5. Test with [CSP Evaluator](https://csp-evaluator.withgoogle.com/)

### Issue: "Environment variables not loading"

**Solution**:
1. Ensure file is named `.env.local` (not `.env`)
2. Variables for client-side must start with `NEXT_PUBLIC_`
3. Restart dev server after changing environment variables
4. Check for syntax errors in `.env.local`

## Deployment

For deployment instructions, see [DEPLOY.md](DEPLOY.md).

## Contributing

When implementing new features:

1. Follow the existing file structure
2. Use TypeScript for all new files
3. Apply Tailwind CSS classes (no inline styles)
4. Add proper TypeScript types for all props and state
5. Include error handling in API calls
6. Test responsive design at multiple breakpoints
7. Add accessibility attributes (ARIA labels, focus states)
8. Ensure all user inputs are properly escaped (XSS prevention)
9. Follow CSP policy - avoid inline scripts and styles where possible

## Next Steps

After Phase 1 setup is complete, the following user stories will be implemented:

1. **US1**: User authentication (signup, login, logout)
2. **US2**: Task creation and viewing
3. **US3**: Task filtering and sorting
4. **US4**: Task updating and completion
5. **US5**: Task deletion

Each user story will add new pages, components, and API integrations to this frontend application.

## Resources

- **Next.js Documentation**: https://nextjs.org/docs
- **Better-Auth Documentation**: https://better-auth.com/docs
- **Tailwind CSS Documentation**: https://tailwindcss.com/docs
- **TypeScript Documentation**: https://www.typescriptlang.org/docs
- **React 19 Documentation**: https://react.dev
- **OWASP XSS Prevention**: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- **CSP Reference**: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP

## License

This project is part of a hackathon and is for educational purposes.
