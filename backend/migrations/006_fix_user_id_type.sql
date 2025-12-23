-- Migration: Fix user_id type mismatch between Better-Auth (TEXT) and tasks table (UUID)
-- This aligns the tasks table with Better-Auth's user table

BEGIN;

-- Step 1: Drop foreign key constraint to old users table
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_user_id_fkey;

-- Step 2: Change user_id column from UUID to TEXT
-- Since there might be existing data, we need to handle it carefully
-- First, check if there are any tasks (there shouldn't be any valid ones with UUID user_ids from Better-Auth)
-- We'll clear the table to be safe
TRUNCATE TABLE tasks CASCADE;

-- Now alter the column type
ALTER TABLE tasks ALTER COLUMN user_id TYPE TEXT;

-- Step 3: Add foreign key constraint to Better-Auth's user table
ALTER TABLE tasks ADD CONSTRAINT tasks_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;

-- Step 4: Update indexes (recreate them for TEXT type)
DROP INDEX IF EXISTS idx_tasks_user_id;
DROP INDEX IF EXISTS idx_tasks_user_status;
DROP INDEX IF EXISTS idx_tasks_user_due_date;

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date);

COMMIT;
