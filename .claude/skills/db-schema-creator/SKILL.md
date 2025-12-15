---
name: db-schema-creator
description: Create and validate SQLModel schemas from database specs for Neon PostgreSQL integration, including tables, relationships, and indexes.
version: 1.0
---

# DB Schema Creator Skill

## Overview
This skill generates Python SQLModel classes (e.g., for tasks and users tables) based on database specs, ensuring proper fields, constraints, foreign keys, and indexes for Phase 2 persistent storage and multi-user filtering.

## Instructions
1. Parse the database spec (e.g., @specs/database/schema.md) for tables, fields, types, and relationships.
2. Generate SQLModel models:
   - Use SQLModel for ORM (e.g., class Task(SQLModel, table=True)).
   - Include fields like id: int (primary key), user_id: str (foreign key), title: str, completed: bool (default False).
   - Add metadata: __tablename__, indexes (e.g., for user_id, completed).
3. Handle relationships: e.g., Foreign key from tasks to users.
4. Suggest connection setup in /backend/db.py (using DATABASE_URL env var).
5. Validate output: Use script to check for required fields, nullables, and best practices from @resources/schema-reference.md.
6. Output the full models file, ready for /backend/models/, and migration suggestions (e.g., SQLModel.metadata.create_all).

## Inputs
- Spec reference: e.g., @specs/database/schema.md
- Optional: Existing models paths for updates (e.g., /backend/models/user.py)

## Outputs
- Generated Python file (e.g., models/task.py)
- Validation report from script
- Env var suggestions (e.g., DATABASE_URL for Neon)

## Examples
### Example 1: Basic Task Table
Input Spec: "Tasks table with id, title, description, completed, user_id foreign key."
Output: Task class with fields, index on completed.

### Example 2: User Table Integration
Input Spec: "Users table managed by Better Auth: id, email, name, created_at."
Output: User class with relationship to tasks.

## Dependencies
- Backend: sqlmodel, psycopg2 (add to pyproject.toml if missing).

## Testing
Run the included script schema-validator.py with generated code snippet to check validity.