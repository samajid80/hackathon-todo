"""User SQLModel definition.

Note: This model is primarily for reference and testing. In production,
the users table is managed by Better-Auth on the frontend. The backend
only receives user_id from validated JWT tokens.

This model exists to:
1. Allow SQLModel to create the users table in test environments
2. Satisfy foreign key constraints from tasks.user_id
3. Provide type safety when working with user data
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User ORM model for database table.

    Represents the users table managed by Better-Auth. This model
    is included for testing and foreign key constraints but is NOT
    directly manipulated by the FastAPI backend.
    """

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    password: str = Field(max_length=255, nullable=False)  # Hashed by Better-Auth
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
