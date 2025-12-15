# Database Setup: Phase 2 Full-Stack Todo Application

This directory contains database migration scripts for the Phase 2 full-stack todo application. The database uses **Neon PostgreSQL**, a managed PostgreSQL hosting service.

## Prerequisites

- Neon account (free tier available at https://neon.tech)
- PostgreSQL 14+ (Neon provides this)
- Command-line access to psql or pgAdmin (optional, for manual queries)

## Database Setup Instructions

### Step 1: Create Neon Project

1. Go to https://neon.tech and sign up
2. Create a new project (choose free tier)
3. Copy the connection string provided
4. Format: `postgresql://user:password@host:5432/database`

### Step 2: Configure Backend

1. Copy the connection string from Neon
2. Update backend `.env` file:
   ```bash
   cp backend/.env.example backend/.env
   ```
3. Edit `backend/.env`:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```

### Step 3: Run Migrations

#### Option A: Using SQLAlchemy with FastAPI (Recommended)

The backend automatically creates tables on startup using SQLModel:

```bash
cd backend
python3.13 -m uvicorn main:app --reload
```

The application will:
1. Connect to Neon PostgreSQL
2. Create tables if they don't exist
3. Create indexes automatically
4. Create triggers via migration scripts

#### Option B: Manual Migration Using SQL

Run migrations directly on Neon:

1. Connect to your Neon database:
   ```bash
   psql postgresql://user:password@host:5432/database
   ```

2. Run migration 001 (create tables):
   ```bash
   \i backend/migrations/001_create_tasks_table.sql
   ```

3. Run migration 002 (create triggers):
   ```bash
   \i backend/migrations/002_updated_at_trigger.sql
   ```

### Step 4: Verify Database Setup

```bash
# Connect to database
psql postgresql://user:password@host:5432/database

# Check tables exist
\dt

# Should see:
#  - public | users | table | ...
#  - public | tasks | table | ...

# Check indexes exist
\di

# Should show: idx_tasks_user_id, idx_tasks_status, idx_tasks_due_date, etc.

# Check triggers exist
\dy

# Should show: update_tasks_updated_at
```

## Database Schema

### Users Table

Managed by Better-Auth. Fields:
- `id` (UUID): Primary key
- `email` (VARCHAR): Unique email address
- `password` (VARCHAR): Hashed password
- `created_at` (TIMESTAMP): Account creation
- `updated_at` (TIMESTAMP): Last modification

### Tasks Table

Managed by FastAPI backend. Fields:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to users
- `title` (VARCHAR): Task title (required)
- `description` (VARCHAR): Task description (optional)
- `due_date` (DATE): Task deadline (optional)
- `priority` (VARCHAR): low, medium, high (default: medium)
- `status` (VARCHAR): pending, completed (default: pending)
- `created_at` (TIMESTAMP): Creation timestamp
- `updated_at` (TIMESTAMP): Last modification timestamp

### Indexes

Performance-critical indexes:
- `idx_tasks_user_id`: For user-scoped queries
- `idx_tasks_status`: For status filtering
- `idx_tasks_due_date`: For due date sorting and overdue detection
- `idx_tasks_user_status`: Composite for filtered user queries
- `idx_tasks_user_due_date`: Composite for sorted user queries

### Constraints

- Foreign key: `tasks.user_id` → `users.id` (ON DELETE CASCADE)
- Check constraint: `title` NOT EMPTY
- Check constraint: `priority` IN ('low', 'medium', 'high')
- Check constraint: `status` IN ('pending', 'completed')
- Trigger: Auto-update `updated_at` on task modifications

## Development Workflow

### Local Testing (SQLite)

For development/testing without Neon:

```bash
# backend/.env for local testing
DATABASE_URL=sqlite:///./test.db
```

The backend will use SQLite instead of PostgreSQL.

### Production (Neon PostgreSQL)

```bash
# backend/.env for production
DATABASE_URL=postgresql://user:password@neon.host:5432/database
```

## Backup and Recovery

### Backup Database

Neon provides automated backups. To manually export data:

```bash
# Export schema
pg_dump postgresql://user:password@host:5432/database --schema-only > schema.sql

# Export all data
pg_dump postgresql://user:password@host:5432/database > full_backup.sql

# Restore data
psql postgresql://user:password@host:5432/database < full_backup.sql
```

## Troubleshooting

### Connection Refused

Check:
1. Neon project is active (check Neon dashboard)
2. Connection string is correct (copy from Neon dashboard)
3. IP whitelist allows your connection (Neon handles this automatically)

### Table Not Found

Verify migrations ran:
```bash
psql postgresql://user:password@host:5432/database
\dt
```

If tables don't exist, run migrations manually (see Step 3, Option B).

### Trigger Not Found

If `updated_at` not auto-updating:
```bash
psql postgresql://user:password@host:5432/database
\dy
```

If trigger missing, run migration 002 manually.

## Migration Management

### Adding New Migrations

1. Create new file: `backend/migrations/003_<description>.sql`
2. Follow numbering convention (001, 002, 003, ...)
3. Include comment at top with date and description
4. Run: `psql postgresql://user:password@host:5432/database < backend/migrations/003_<description>.sql`

### Migration Rollback

For SQLite or PostgreSQL, maintain rollback scripts:

```sql
-- backend/migrations/002_rollback.sql
DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
DROP FUNCTION IF EXISTS update_updated_at_column();
```

## References

- **Neon Documentation**: https://neon.tech/docs
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **SQLModel ORM**: https://sqlmodel.tiangolo.com
- **FastAPI Database Integration**: https://fastapi.tiangolo.com/advanced/sql-databases/
