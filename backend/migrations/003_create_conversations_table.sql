-- Migration: 003_create_conversations_table.sql
-- Purpose: Create conversations table for Phase 3 chatbot
-- Author: Phase 3 Implementation
-- Date: 2025-12-20

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Foreign key to users table (managed by Better Auth)
    CONSTRAINT fk_conversations_user FOREIGN KEY (user_id)
        REFERENCES "user"(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_created
    ON conversations(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_updated
    ON conversations(updated_at DESC);

-- Create trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_conversations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER conversations_updated_at_trigger
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_conversations_updated_at();

-- Add comments for documentation
COMMENT ON TABLE conversations IS 'Chat conversations between users and AI assistant for Phase 3';
COMMENT ON COLUMN conversations.id IS 'Unique conversation identifier (UUID)';
COMMENT ON COLUMN conversations.user_id IS 'Reference to user from Better Auth user table';
COMMENT ON COLUMN conversations.created_at IS 'Conversation creation timestamp';
COMMENT ON COLUMN conversations.updated_at IS 'Last message timestamp (auto-updated)';
