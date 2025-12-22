-- Migration: 004_create_messages_table.sql
-- Purpose: Create messages table for Phase 3 chatbot conversation history
-- Author: Phase 3 Implementation
-- Date: 2025-12-20

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Foreign keys
    CONSTRAINT fk_messages_user FOREIGN KEY (user_id)
        REFERENCES "user"(id) ON DELETE CASCADE,
    CONSTRAINT fk_messages_conversation FOREIGN KEY (conversation_id)
        REFERENCES conversations(id) ON DELETE CASCADE
);

-- Create indexes for performance (conversation history queries)
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
    ON messages(conversation_id, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_messages_user_created
    ON messages(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_messages_role
    ON messages(role);

-- Add comments for documentation
COMMENT ON TABLE messages IS 'Individual chat messages within conversations for Phase 3';
COMMENT ON COLUMN messages.id IS 'Unique message identifier (UUID)';
COMMENT ON COLUMN messages.user_id IS 'Reference to user from Better Auth user table';
COMMENT ON COLUMN messages.conversation_id IS 'Reference to parent conversation';
COMMENT ON COLUMN messages.role IS 'Message sender role: user, assistant, or system';
COMMENT ON COLUMN messages.content IS 'Message text content';
COMMENT ON COLUMN messages.created_at IS 'Message creation timestamp (immutable)';
