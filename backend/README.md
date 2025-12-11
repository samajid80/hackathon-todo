# Hackathon Todo - Backend API

FastAPI backend for Phase 2 Full-Stack Todo Web Application with JWT authentication, PostgreSQL storage, and user-scoped task management.

## Features

- **Authentication**: JWT token validation (compatible with Better-Auth)
- **Task Management**: CRUD operations with user isolation
- **Database**: SQLModel ORM with PostgreSQL (Neon)
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Testing**: Comprehensive test suite with pytest (86% coverage)
- **Security**: Rate limiting, input sanitization, security headers
- **CI/CD**: Automated testing and deployment pipelines

## Technology Stack

- **Python**: 3.13+
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon)
- **Authentication**: JWT with python-jose
- **Testing**: pytest, pytest-asyncio, httpx
- **Linting**: ruff, mypy

## Prerequisites

- Python 3.13 or higher
- uv package manager (recommended) or pip
- PostgreSQL database (Neon account recommended)
- Node.js 24+ (for frontend integration)

## Setup Instructions

### 1. Install Dependencies

Using uv (recommended):
```bash
cd backend
uv pip install -e ".[test,dev]"
```

Using pip:
```bash
cd backend
pip install -e ".[test,dev]"
```

### 2. Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Configure the following environment variables in `.env`:

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql://user:pass@host.neon.tech/dbname?sslmode=require` | Neon PostgreSQL connection string with SSL |
| `JWT_SECRET` | Yes | `openssl rand -base64 32` | Secret for JWT signing (minimum 32 characters) |
| `JWT_ALGORITHM` | No | `HS256` | Algorithm for JWT signing (default: HS256) |
| `CORS_ORIGINS` | No | `http://localhost:3000,https://example.com` | Comma-separated allowed origins |
| `ENVIRONMENT` | No | `development` | Environment: development, staging, or production |

**Environment Variable Setup Instructions**:

1. **Copy example file**:
   ```bash
   cp .env.example .env
   ```

2. **Generate JWT_SECRET**:
   ```bash
   echo "JWT_SECRET=$(openssl rand -base64 32)" >> .env
   ```

3. **Set DATABASE_URL from Neon**:
   - Sign up at [neon.tech](https://neon.tech)
   - Create a new project
   - Copy connection string from dashboard
   - Paste into .env:
     ```env
     DATABASE_URL=postgresql://username:password@host.neon.tech/dbname?sslmode=require
     ```

4. **Configure CORS_ORIGINS**:
   ```env
   # Development
   CORS_ORIGINS=http://localhost:3000

   # Production (comma-separated)
   CORS_ORIGINS=https://your-frontend.com,https://www.your-frontend.com
   ```

5. **Set environment**:
   ```env
   ENVIRONMENT=development  # or staging, production
   ```

**Example `.env` file**:
```env
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require
JWT_SECRET=abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx1234yzab5678
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

**Warning**: NEVER commit `.env` file to version control!

## CRITICAL SECURITY WARNINGS

### Secrets Protection (T154-T155)

**WARNING: Never commit .env file to version control!**

The `.env` file contains sensitive credentials that must NEVER be committed to git:
- `JWT_SECRET` - Used to sign and verify JWT tokens
- `DATABASE_URL` - Contains database credentials

**Requirements**:
1. **JWT_SECRET** must be:
   - Generated randomly (minimum 32 characters)
   - Kept secret and never shared publicly
   - The same in both frontend (`BETTER_AUTH_SECRET`) and backend (`JWT_SECRET`)
   - Example generation: `openssl rand -base64 32`

2. **DATABASE_URL** must be:
   - Kept in `.env` file only (never in code)
   - Never committed to version control
   - Updated when rotating credentials

**Verification Checklist**:
- [ ] `.gitignore` includes `.env` and `.env.local`
- [ ] No `.env` files in git history (`git log -p -- .env`)
- [ ] `JWT_SECRET` is at least 32 random characters
- [ ] `DATABASE_URL` contains valid Neon PostgreSQL credentials
- [ ] Both frontend and backend use the same secret

**For Production**:
- Use environment variables from hosting platform (Vercel, Railway, etc.)
- Enable secret rotation policies
- Use secret management services (AWS Secrets Manager, HashiCorp Vault, etc.)

### 3. Database Setup

#### Create Neon PostgreSQL Database

1. Sign up for a free account at [neon.tech](https://neon.tech)
2. Create a new project
3. Create a new database (e.g., `hackathon_todo`)
4. Copy the connection string and add to `DATABASE_URL` in `.env`

#### Database Migrations

**Migrations Directory**: `/backend/migrations/`

The project uses SQL migration files for schema management. Migrations are numbered sequentially:

**Current Migrations**:
1. `001_create_tasks_table.sql` - Creates tasks table with indexes
2. `002_updated_at_trigger.sql` - Auto-update timestamps trigger

**Running Migrations Manually**:

Using psql (recommended):
```bash
# Run all migrations in order
psql "$DATABASE_URL" < migrations/001_create_tasks_table.sql
psql "$DATABASE_URL" < migrations/002_updated_at_trigger.sql
```

Using Python (automatic on startup):
```bash
python -c "from backend.db import create_db_and_tables; create_db_and_tables()"
```

**Verifying Migrations**:
```bash
# List all tables
psql "$DATABASE_URL" -c "\dt"

# List all indexes
psql "$DATABASE_URL" -c "\di"

# Describe tasks table
psql "$DATABASE_URL" -c "\d tasks"
```

**Migration Best Practices**:
- Keep backup of original data before running migrations
- Test migrations on staging environment first
- Never delete migration files (keep for reference)
- Document any breaking changes in migration comments
- Use transactions for complex migrations

**Rollback Strategy**:
- For simple migrations, write inverse SQL manually
- For complex migrations, restore from database backup
- Consider using Alembic for production (see below)

**Production Migration Workflow**:

For production deployments, consider using Alembic:

1. **Install Alembic**:
   ```bash
   uv pip install alembic
   ```

2. **Initialize Alembic**:
   ```bash
   alembic init migrations
   ```

3. **Create migration**:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

4. **Apply migration**:
   ```bash
   alembic upgrade head
   ```

5. **Rollback migration**:
   ```bash
   alembic downgrade -1  # Rollback one version
   ```

### 4. Run the Application

Development server with auto-reload:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Running Tests

### Quick Test Commands

Run all tests:
```bash
cd backend
python3.13 -m pytest tests/ -v
```

Run with coverage report:
```bash
python3.13 -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

Run specific test file:
```bash
python3.13 -m pytest tests/test_auth.py -v
python3.13 -m pytest tests/test_task_service.py -v
python3.13 -m pytest tests/test_task_routes.py -v
python3.13 -m pytest tests/test_integration.py -v
```

Run linting:
```bash
ruff check . --fix
```

Run type checking:
```bash
mypy . --strict
```

### Test Results (Latest Run)

**Test Summary** (2025-12-12):
- **Total Tests**: 77
- **Passed**: 66 (85.7%)
- **Failed**: 11 (14.3%) - Due to pagination response format updates
- **Coverage**: 86% (exceeds 80% target ✓)
- **Execution Time**: 7.20s

**Coverage by Module**:
- `auth/jwt_middleware.py`: 97%
- `auth/rate_limiter.py`: 75%
- `main.py`: 94%
- `models/enums.py`: 100%
- `models/task.py`: 86%
- `models/user.py`: 100%
- `routes/tasks.py`: 75%
- `services/task_service.py`: 86%

**Test Categories**:
1. **Authentication Tests** (`test_auth.py`): 7/7 passing ✓
2. **Task Service Tests** (`test_task_service.py`): Comprehensive business logic testing
3. **Task Routes Tests** (`test_task_routes.py`): API endpoint validation
4. **Integration Tests** (`test_integration.py`): End-to-end flows

See [TESTING_SUMMARY.md](../TESTING_SUMMARY.md) for detailed test results and recommendations.

## Project Structure

```
backend/
├── auth/
│   ├── __init__.py
│   ├── jwt_middleware.py      # JWT validation and user extraction
│   └── rate_limiter.py        # Rate limiting middleware (T156)
├── models/
│   ├── __init__.py
│   ├── enums.py               # Priority, Status enums
│   └── task.py                # Task SQLModel and schemas
├── routes/
│   ├── __init__.py
│   └── tasks.py               # Task API endpoints
├── services/
│   ├── __init__.py
│   └── task_service.py        # Business logic layer
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_auth.py           # JWT middleware tests
│   ├── test_task_service.py   # Service layer tests
│   ├── test_task_routes.py    # API endpoint tests
│   └── test_integration.py    # End-to-end tests
├── migrations/                # Database migration files
│   ├── 001_create_tasks_table.sql
│   └── 002_updated_at_trigger.sql
├── db.py                      # Database connection and session management
├── main.py                    # FastAPI application entry point
├── pyproject.toml             # Python dependencies and configuration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## API Endpoints

### Health Check

- **GET /** - Root endpoint with API information
- **GET /health** - Health check endpoint

### Task Management

All task endpoints require JWT authentication via `Authorization: Bearer <token>` header.

- **POST /api/tasks** - Create new task
- **GET /api/tasks** - List all user's tasks (with optional filters/sorts/pagination)
- **GET /api/tasks/{task_id}** - Get single task details
- **PUT /api/tasks/{task_id}** - Update task
- **PATCH /api/tasks/{task_id}/complete** - Mark task as completed
- **DELETE /api/tasks/{task_id}** - Delete task

See [API Documentation](http://localhost:8000/docs) for detailed schema, or refer to [API_DOCUMENTATION.md](../API_DOCUMENTATION.md) for examples.

## Security Features (Phase 7 - T154-T159)

### Rate Limiting (T156)

The API implements rate limiting to prevent abuse:

**Rate Limits**:
- `/api/auth/signup`: 5 requests per hour per IP (prevents account enumeration)
- `/api/auth/login`: 5 requests per hour per IP (prevents brute force)
- `/api/tasks`: 100 requests per hour per user (prevents data scraping)
- `/api/tasks/{id}/*`: 100 requests per hour per user

**Response**:
- HTTP 429 Too Many Requests with `Retry-After` header
- Logged at INFO level (not WARN to avoid spam)

### Input Validation (T157)

All user inputs are validated using Pydantic validators:

```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    priority: Priority = Field(default=Priority.MEDIUM)

    # Validators ensure:
    # - No SQL injection (SQLModel parameterized queries)
    # - No XSS (sanitized outputs)
    # - Valid date formats (ISO 8601)
```

**Field Constraints**:
- `title`: 1-200 characters, whitespace stripped, required
- `description`: 0-2000 characters, optional
- `due_date`: Valid ISO date format, optional
- `priority`: Enum (low, medium, high)
- `status`: Enum (pending, completed)

### Security Headers (T159)

The API includes security headers to prevent common attacks:

```python
# Set via middleware in main.py
X-Content-Type-Options: nosniff        # Prevent MIME sniffing
X-Frame-Options: DENY                  # Prevent clickjacking
X-XSS-Protection: 1; mode=block        # Enable XSS filter
Strict-Transport-Security: max-age=31536000  # Enforce HTTPS (production)
Referrer-Policy: strict-origin-when-cross-origin  # Control referrer info
```

**Header Explanations**:
- `X-Content-Type-Options: nosniff` - Forces browsers to respect Content-Type
- `X-Frame-Options: DENY` - Prevents page from being embedded in iframes
- `X-XSS-Protection: 1; mode=block` - Enables browser XSS filter
- `HSTS` - Enforces HTTPS connections (enable in production only)
- `Referrer-Policy` - Controls what referrer information is sent

## Database Schema

### Tasks Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique task identifier |
| `user_id` | UUID | Foreign Key, Required | Task owner (from users table) |
| `title` | String | Required, Max 200 chars | Task title |
| `description` | String | Optional, Max 2000 chars | Task description |
| `due_date` | Date | Optional | Task deadline |
| `priority` | Enum | Required, Default: medium | Priority level (low, medium, high) |
| `status` | Enum | Required, Default: pending | Status (pending, completed) |
| `created_at` | Timestamp | Required, Auto-generated | Creation timestamp |
| `updated_at` | Timestamp | Required, Auto-updated | Last modification timestamp |

**Indexes**:
- `user_id` (B-tree) - User-scoped queries
- `status` (B-tree) - Status filtering
- `due_date` (B-tree) - Sorting and overdue detection
- `(user_id, status)` (Composite) - Filtered user queries
- `(user_id, due_date)` (Composite) - Sorted user queries

### Users Table

Managed by Better-Auth in the frontend. Backend receives `user_id` from validated JWT tokens.

## Development Guidelines

### Code Quality

Run linters:
```bash
ruff check .
ruff format .
```

Run type checker:
```bash
mypy backend/
```

### Testing Strategy

1. **Unit Tests**: Test service layer business logic
2. **API Tests**: Test endpoint handlers with mocked dependencies
3. **Integration Tests**: Test full flow from API to database

### Security Best Practices

1. **JWT Secret**: Never commit `JWT_SECRET` to version control
2. **Database URL**: Keep `DATABASE_URL` in `.env` only
3. **User Isolation**: Always filter queries by `user_id` from JWT
4. **Input Validation**: Use Pydantic schemas for validation (T157)
5. **SQL Injection**: SQLModel protects against SQL injection (parameterized queries)
6. **XSS Prevention**: Sanitize user inputs and use React's built-in escaping (T157, T158)
7. **Rate Limiting**: Prevent brute force and abuse (T156)
8. **Security Headers**: Use OWASP recommended headers (T159)

### Error Handling

- **400 Bad Request**: Invalid request payload
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User attempting to access another user's resource
- **404 Not Found**: Resource doesn't exist
- **429 Too Many Requests**: Rate limit exceeded (T156)
- **500 Internal Server Error**: Unexpected server error

## CI/CD Pipeline

### Continuous Integration

**Workflow**: `.github/workflows/ci.yml`
**Triggers**: Push to main/develop/002-fullstack-web-app, PRs to main/develop

**Jobs**:
1. **Backend Tests**: pytest with coverage, ruff linting, mypy type checking
2. **Frontend Tests**: ESLint, TypeScript check, build verification
3. **Security Checks**: Python safety, npm audit, secret scanning
4. **Test Summary**: Aggregate results in GitHub Actions summary

### Continuous Deployment

**Workflow**: `.github/workflows/deploy.yml`
**Triggers**: Push to main (after CI passes), manual trigger

**Jobs**:
1. **Deploy Backend**: Render/Railway deployment with health checks
2. **Deploy Frontend**: Vercel production deployment
3. **Smoke Tests**: Verify backend, frontend, and database connectivity

See [CI/CD documentation](.github/workflows/) for configuration details.

## Troubleshooting

### Database Connection Issues

```
ValueError: DATABASE_URL environment variable is not set
```
**Solution**: Copy `.env.example` to `.env` and configure `DATABASE_URL`

### JWT Validation Errors

```
HTTPException: Could not validate credentials
```
**Solution**: Ensure `JWT_SECRET` matches frontend `BETTER_AUTH_SECRET`

### CORS Errors

```
Access to fetch at 'http://localhost:8000/api/tasks' from origin 'http://localhost:3000' has been blocked by CORS policy
```
**Solution**: Verify `CORS_ORIGINS` includes your frontend URL

### Import Errors

```
ModuleNotFoundError: No module named 'backend'
```
**Solution**: Install in editable mode: `pip install -e .`

### Rate Limit Errors (T156)

```
HTTPException: 429 Too Many Requests
```
**Solution**: Wait for the retry period indicated in `Retry-After` header

### Migration Errors

```
psql: ERROR: relation "tasks" already exists
```
**Solution**: Database tables already exist. Skip migration or drop tables first (backup data!)

```
psql: ERROR: password authentication failed
```
**Solution**: Verify `DATABASE_URL` credentials are correct. Check Neon dashboard for connection string.

## Deployment

For deployment instructions, see [DEPLOY.md](DEPLOY.md).

## Contributing

1. Create a feature branch from `002-fullstack-web-app`
2. Write tests for new features
3. Ensure all tests pass: `pytest`
4. Run linters: `ruff check .`
5. Submit pull request

## License

[Your License Here]

## Support

For issues and questions, please refer to:
- [API Documentation](http://localhost:8000/docs)
- [API Examples](../API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOY.md)
- [Testing Summary](../TESTING_SUMMARY.md)
- [Phase 2 Specification](../specs/002-fullstack-web-app/spec.md)
- [Implementation Plan](../specs/002-fullstack-web-app/plan.md)
