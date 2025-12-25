"""
SQLModel definitions for Phase 3 chat functionality.

Defines Conversation and Message models for chatbot conversation history.
"""

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, DateTime
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4


class Conversation(SQLModel, table=True):
    """
    Represents a chat conversation between a user and the AI assistant.

    Each conversation contains multiple messages and belongs to a single user.
    """

    __tablename__ = "conversations"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)  # No FK - Better Auth manages users table
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """
    Represents an individual message within a conversation.

    Messages can be from the user, assistant (AI), or system.
    """

    __tablename__ = "messages"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)  # No FK - Better Auth manages users table
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # 'user', 'assistant', or 'system'
    content: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Add a task to buy groceries",
            }
        }


# Pydantic models for API requests/responses
class MessageCreate(SQLModel):
    """Schema for creating a new message."""

    message: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None


class MessageResponse(SQLModel):
    """Schema for message API responses."""

    conversation_id: UUID
    message: str
    timestamp: datetime
    tool_calls: Optional[List[dict]] = None


class ConversationResponse(SQLModel):
    """Schema for conversation API responses."""

    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
