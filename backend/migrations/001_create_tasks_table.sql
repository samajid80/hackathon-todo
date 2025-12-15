-- Migration 001: Create tasks table with indexes
-- Date: 2025-12-11
-- Description: Create the tasks table with all fields, constraints, and indexes for Phase 2

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL CHECK (LENGTH(title) > 0),
    description VARCHAR(2000),
    due_date DATE,
    priority VARCHAR(10) NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high')),
    status VARCHAR(10) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'completed')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
-- Index for user-scoped queries (most common)
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

-- Index for due date sorting and overdue filtering
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);

-- Composite index for user-scoped filtered queries (e.g., user's pending tasks)
CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status);

-- Composite index for user-scoped sorted queries (e.g., user's tasks by due date)
CREATE INDEX IF NOT EXISTS idx_tasks_user_due_date ON tasks(user_id, due_date);

-- Create trigger for automatic updated_at timestamp
-- This trigger function will be created in migration 002
-- For now, applications are responsible for updating updated_at

COMMENT ON TABLE tasks IS 'Task management table for Phase 2 full-stack todo application';
COMMENT ON COLUMN tasks.user_id IS 'Owner of the task (references users table)';
COMMENT ON COLUMN tasks.title IS 'Task title (required, max 200 chars)';
COMMENT ON COLUMN tasks.description IS 'Task description (optional, max 2000 chars)';
COMMENT ON COLUMN tasks.due_date IS 'Task deadline in ISO 8601 format';
COMMENT ON COLUMN tasks.priority IS 'Priority level: low, medium, high';
COMMENT ON COLUMN tasks.status IS 'Status: pending, completed';
COMMENT ON COLUMN tasks.created_at IS 'When the task was created';
COMMENT ON COLUMN tasks.updated_at IS 'When the task was last modified';
