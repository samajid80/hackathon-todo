-- Migration: 005_fix_tasks_user_id_type.sql
-- Purpose: Fix tasks.user_id from UUID to TEXT to match Better Auth user.id
-- Author: Phase 3 Bug Fix
-- Date: 2025-12-21

-- Step 1: Drop the existing foreign key constraint
ALTER TABLE tasks
DROP CONSTRAINT IF EXISTS tasks_user_id_fkey;

-- Step 2: Change user_id column type from UUID to TEXT
ALTER TABLE tasks
ALTER COLUMN user_id TYPE TEXT;

-- Step 3: Add new foreign key constraint referencing Better Auth user table
ALTER TABLE tasks
ADD CONSTRAINT tasks_user_id_fkey
FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;

-- Add comment
COMMENT ON COLUMN tasks.user_id IS 'Reference to user.id from Better Auth (TEXT type)';
