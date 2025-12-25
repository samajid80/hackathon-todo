"""
Chat service for managing conversations and messages.

Provides CRUD operations for conversations and message history.
"""

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.models.chat import Conversation, Message
from app.db import get_session


class ChatService:
    """Service for managing chat conversations and messages."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    async def get_or_create_conversation(self, user_id: str, conversation_id: Optional[UUID] = None) -> Conversation:
        """
        Get existing conversation or create new one for user.

        Args:
            user_id: User identifier from JWT
            conversation_id: Optional conversation ID to retrieve

        Returns:
            Conversation object (existing or newly created)
        """
        if conversation_id:
            # Try to get existing conversation
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            result = await self.session.execute(statement)
            conversation = result.scalar_one_or_none()

            if conversation:
                # Update timestamp
                conversation.updated_at = datetime.now(timezone.utc)
                self.session.add(conversation)
                return conversation

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        await self.session.flush()  # Get conversation.id
        return conversation

    async def save_message(
        self,
        user_id: str,
        conversation_id: UUID,
        role: str,
        content: str
    ) -> Message:
        """
        Save a message to the conversation.

        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            role: Message role ('user', 'assistant', 'system')
            content: Message content

        Returns:
            Created Message object
        """
        message = Message(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_message_history(
        self,
        conversation_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Message]:
        """
        Retrieve message history for a conversation.

        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of messages to retrieve (default: 20)
            offset: Number of messages to skip (for pagination)

        Returns:
            List of Message objects ordered by created_at ASC
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        messages = result.scalars().all()
        return list(messages)

    async def get_conversation(self, conversation_id: UUID, user_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation by ID.

        Args:
            conversation_id: Conversation identifier
            user_id: User identifier (for authorization)

        Returns:
            Conversation object or None if not found/unauthorized
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_conversations(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Conversation]:
        """
        List all conversations for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of conversations to retrieve
            offset: Number of conversations to skip

        Returns:
            List of Conversation objects ordered by updated_at DESC
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        conversations = result.scalars().all()
        return list(conversations)

    async def delete_conversation(self, conversation_id: UUID, user_id: str) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: Conversation identifier
            user_id: User identifier (for authorization)

        Returns:
            True if deleted, False if not found/unauthorized
        """
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.commit()
        return True


# Standalone helper functions for route handlers
async def get_or_create_conversation(
    user_id: str,
    conversation_id: Optional[str] = None
) -> Conversation:
    """
    Get or create conversation (standalone function for routes).

    Args:
        user_id: User identifier
        conversation_id: Optional conversation ID string

    Returns:
        Conversation object
    """
    async for session in get_session():
        service = ChatService(session)
        conv_uuid = UUID(conversation_id) if conversation_id else None
        conversation = await service.get_or_create_conversation(user_id, conv_uuid)
        await session.commit()
        return conversation


async def save_message(
    user_id: str,
    conversation_id: str,
    role: str,
    content: str
) -> Message:
    """
    Save a message (standalone function for routes).

    Args:
        user_id: User identifier
        conversation_id: Conversation ID string
        role: Message role
        content: Message content

    Returns:
        Created Message object
    """
    async for session in get_session():
        service = ChatService(session)
        message = await service.save_message(
            user_id,
            UUID(conversation_id),
            role,
            content
        )
        await session.commit()
        return message


async def get_message_history(
    conversation_id: str,
    limit: int = 20
) -> List[Message]:
    """
    Get message history (standalone function for routes).

    Args:
        conversation_id: Conversation ID string
        limit: Maximum messages to retrieve

    Returns:
        List of Message objects
    """
    async for session in get_session():
        service = ChatService(session)
        messages = await service.get_message_history(UUID(conversation_id), limit)
        return messages


async def list_user_conversations(user_id: str) -> List[Conversation]:
    """
    List user conversations (standalone function for routes).

    Args:
        user_id: User identifier

    Returns:
        List of Conversation objects
    """
    async for session in get_session():
        service = ChatService(session)
        conversations = await service.list_conversations(user_id)
        return conversations


async def delete_user_conversation(user_id: str, conversation_id: str) -> bool:
    """
    Delete a conversation (standalone function for routes).

    Args:
        user_id: User identifier
        conversation_id: Conversation ID string

    Returns:
        True if deleted, False otherwise

    Raises:
        Exception if conversation not found
    """
    async for session in get_session():
        service = ChatService(session)
        deleted = await service.delete_conversation(UUID(conversation_id), user_id)
        if not deleted:
            raise Exception("Conversation not found or unauthorized")
        return deleted
