-- Migration 006: Add session_id column to conversations table for ChatKit session mapping
-- Feature: 003-chatkit-migration
-- Date: 2025-12-26

-- Add session_id column for ChatKit session mapping
ALTER TABLE conversations
ADD COLUMN session_id TEXT;

-- Create unique index for session mapping
CREATE UNIQUE INDEX idx_conversations_session_id
ON conversations(session_id)
WHERE session_id IS NOT NULL;

-- Add comment
COMMENT ON COLUMN conversations.session_id IS
'ChatKit session ID for mapping frontend sessions to database conversations. Linked to login session lifecycle (24-hour JWT duration).';
