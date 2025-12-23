-- Migration 005: Add tags support to tasks table
-- Date: 2025-12-23
-- Description: Add tags column as TEXT array for task categorization

-- Add tags column (nullable initially for backward compatibility)
ALTER TABLE tasks
ADD COLUMN tags TEXT[] DEFAULT '{}' NOT NULL;

-- Create GIN index for efficient tag containment queries
CREATE INDEX idx_tasks_tags ON tasks USING GIN (tags);

-- Add check constraint for max 10 tags per task
ALTER TABLE tasks
ADD CONSTRAINT chk_max_tags CHECK (array_length(tags, 1) IS NULL OR array_length(tags, 1) <= 10);

-- Comment for documentation
COMMENT ON COLUMN tasks.tags IS 'Task category labels (max 10, lowercase alphanumeric + hyphens)';
