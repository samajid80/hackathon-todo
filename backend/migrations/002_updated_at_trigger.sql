-- Migration 002: Create updated_at trigger
-- Date: 2025-12-11
-- Description: Create trigger to automatically update the updated_at timestamp on task modifications

-- Create the trigger function that updates the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger on the tasks table
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Note: Better-Auth manages the users table and triggers
-- This script only handles the tasks table triggers
