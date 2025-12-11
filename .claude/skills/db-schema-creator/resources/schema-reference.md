# SQLModel Schema Best Practices for Todo App

## General Guidelines
- Use SQLModel for models (from sqlmodel import SQLModel, Field, Relationship).
- Primary Key: id: int = Field(default=None, primary_key=True).
- Strings: title: str = Field(max_length=200).
- Booleans: completed: bool = Field(default=False).
- Timestamps: created_at: datetime = Field(default_factory=datetime.utcnow).
- Indexes: Use Index for filtering fields (e.g., Index("ix_tasks_user_id", "user_id")).
- Relationships: e.g., tasks: list["Task"] = Relationship(back_populates="user") in User model.
- Foreign Keys: user_id: str = Field(foreign_key="users.id").
- Neon Compat: Use postgresql dialect; env var DATABASE_URL.

## Example Patterns
### Task Model
from sqlmodel import SQLModel, Field, Index
from datetime import datetime

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    __table_args__ = (Index("ix_tasks_user_id", "user_id"), Index("ix_tasks_completed", "completed"))

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

### User Model
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    name: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)