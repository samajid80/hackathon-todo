-- Migration 000: Create users table (Better-Auth compatible)
-- Date: 2025-12-13
-- Description: Create users table to satisfy foreign key constraint from tasks table
-- Note: Better-Auth may also create this table. Using IF NOT EXISTS to avoid conflicts.

-- Create users table (compatible with Better-Auth schema)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Hashed by Better-Auth
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index for email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

COMMENT ON TABLE users IS 'User accounts managed by Better-Auth (frontend)';
COMMENT ON COLUMN users.email IS 'User email address (login credential)';
COMMENT ON COLUMN users.password IS 'Hashed password (bcrypt via Better-Auth)';
