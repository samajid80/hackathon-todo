"""
PostgreSQL implementation of ChatKit Store using existing database schema.

Maps ChatKit concepts to our database:
- Thread → Conversation (with session_id)
- ThreadItem → Message
- Context → UserContext (user_id)
"""

from typing import Optional
from datetime import datetime, timezone
from uuid import UUID

from chatkit.store import Store, NotFoundError
from chatkit.types import (
    Page,
    ThreadItem,
    ThreadMetadata,
    Attachment,
    UserMessageItem,
    AssistantMessageItem,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models.chat import Conversation, Message
from app.db import get_session


class UserContext:
    """Context object containing user_id and JWT token for data isolation and authentication."""

    def __init__(self, user_id: str, jwt_token: Optional[str] = None):
        self.user_id = user_id
        self.jwt_token = jwt_token


class PostgreSQLStore(Store[UserContext]):
    """
    ChatKit Store implementation using PostgreSQL.

    Maps ChatKit Threads to Conversations and ThreadItems to Messages.
    """

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    def generate_thread_id(self, context: UserContext) -> str:
        """Generate thread ID - we'll use conversation UUID format."""
        import uuid
        return f"thr_{uuid.uuid4().hex[:16]}"

    async def load_thread(self, thread_id: str, context: UserContext) -> ThreadMetadata:
        """Load thread metadata from conversations table."""
        # Map thread_id to conversation session_id or id
        statement = select(Conversation).where(
            Conversation.session_id == thread_id,
            Conversation.user_id == context.user_id
        )
        result = await self.session.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise NotFoundError(f"Thread {thread_id} not found")

        return ThreadMetadata(
            id=thread_id,
            title=None,  # We don't store titles
            created_at=conversation.created_at,
            metadata={"conversation_id": str(conversation.id)}
        )

    async def save_thread(self, thread: ThreadMetadata, context: UserContext) -> None:
        """Save thread metadata to conversations table."""
        # Check if conversation exists
        statement = select(Conversation).where(
            Conversation.session_id == thread.id,
            Conversation.user_id == context.user_id
        )
        result = await self.session.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            # Create new conversation
            conversation = Conversation(
                user_id=context.user_id,
                session_id=thread.id,
                created_at=thread.created_at,
                updated_at=datetime.now(timezone.utc)
            )
            self.session.add(conversation)
        else:
            # Update existing
            conversation.updated_at = datetime.now(timezone.utc)
            self.session.add(conversation)

        await self.session.flush()

    async def load_thread_items(
        self,
        thread_id: str,
        after: Optional[str],
        limit: int,
        order: str,
        context: UserContext,
    ) -> Page[ThreadItem]:
        """Load thread items (messages) with pagination."""
        # Get conversation first
        statement = select(Conversation).where(
            Conversation.session_id == thread_id,
            Conversation.user_id == context.user_id
        )
        result = await self.session.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            return Page(data=[], has_next_page=False)

        # Load messages
        query = select(Message).where(
            Message.conversation_id == conversation.id,
            Message.user_id == context.user_id
        )

        if order == "asc":
            query = query.order_by(Message.created_at.asc())
        else:
            query = query.order_by(Message.created_at.desc())

        query = query.limit(limit + 1)  # +1 to check has_next_page

        result = await self.session.execute(query)
        messages = list(result.scalars().all())

        has_next = len(messages) > limit
        if has_next:
            messages = messages[:limit]

        # Convert messages to ThreadItems
        items: list[ThreadItem] = []
        for msg in messages:
            if msg.role == "user":
                from chatkit.types import UserMessageTextContent, InferenceOptions
                items.append(UserMessageItem(
                    id=f"msg_{str(msg.id)[:16]}",
                    thread_id=thread_id,
                    created_at=msg.created_at,
                    content=[UserMessageTextContent(type="input_text", text=msg.content)],
                    inference_options=InferenceOptions()
                ))
            elif msg.role == "assistant":
                from chatkit.types import AssistantMessageContent
                items.append(AssistantMessageItem(
                    id=f"msg_{str(msg.id)[:16]}",
                    thread_id=thread_id,
                    created_at=msg.created_at,
                    content=[AssistantMessageContent(type="output_text", text=msg.content)]
                ))

        return Page(data=items, has_next_page=has_next)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: UserContext
    ) -> None:
        """Add a new item to a thread."""
        # Get conversation
        statement = select(Conversation).where(
            Conversation.session_id == thread_id,
            Conversation.user_id == context.user_id
        )
        result = await self.session.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise NotFoundError(f"Thread {thread_id} not found")

        # Extract content
        content_text = ""
        if isinstance(item, (UserMessageItem, AssistantMessageItem)):
            if item.content:
                for part in item.content:
                    # Handle both object attributes and dict access
                    if hasattr(part, 'text'):
                        content_text = part.text
                        break
                    elif isinstance(part, dict) and part.get("text"):
                        content_text = part.get("text", "")
                        break

        # Determine role
        role = "user" if isinstance(item, UserMessageItem) else "assistant"

        # Create message
        message = Message(
            user_id=context.user_id,
            conversation_id=conversation.id,
            role=role,
            content=content_text,
            created_at=item.created_at if hasattr(item, 'created_at') else datetime.now(timezone.utc)
        )
        self.session.add(message)
        await self.session.flush()

    async def save_item(
        self, thread_id: str, item: ThreadItem, context: UserContext
    ) -> None:
        """Update an existing thread item."""
        # For simplicity, messages are immutable in our system
        # This is a no-op for now
        pass

    async def load_item(
        self, thread_id: str, item_id: str, context: UserContext
    ) -> ThreadItem:
        """Load a specific thread item."""
        raise NotImplementedError("load_item not needed for our use case")

    async def delete_thread(self, thread_id: str, context: UserContext) -> None:
        """Delete a thread and all its items."""
        statement = select(Conversation).where(
            Conversation.session_id == thread_id,
            Conversation.user_id == context.user_id
        )
        result = await self.session.execute(statement)
        conversation = result.scalar_one_or_none()

        if conversation:
            await self.session.delete(conversation)
            await self.session.flush()

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: UserContext
    ) -> None:
        """Delete a specific thread item."""
        # Messages are immutable in our system
        raise NotImplementedError("Cannot delete individual messages")

    async def load_threads(
        self,
        limit: int,
        after: Optional[str],
        order: str,
        context: UserContext,
    ) -> Page[ThreadMetadata]:
        """Load user's threads with pagination."""
        query = select(Conversation).where(
            Conversation.user_id == context.user_id
        )

        if order == "asc":
            query = query.order_by(Conversation.created_at.asc())
        else:
            query = query.order_by(Conversation.created_at.desc())

        query = query.limit(limit + 1)

        result = await self.session.execute(query)
        conversations = list(result.scalars().all())

        has_next = len(conversations) > limit
        if has_next:
            conversations = conversations[:limit]

        threads = [
            ThreadMetadata(
                id=conv.session_id or f"thr_{str(conv.id)[:16]}",
                title=None,
                created_at=conv.created_at,
                metadata={"conversation_id": str(conv.id)}
            )
            for conv in conversations
        ]

        return Page(data=threads, has_next_page=has_next)

    # Attachment methods (not used in our case)
    async def save_attachment(self, attachment: Attachment, context: UserContext) -> None:
        """Not implemented - we don't support attachments."""
        raise NotImplementedError("Attachments not supported")

    async def load_attachment(self, attachment_id: str, context: UserContext) -> Attachment:
        """Not implemented - we don't support attachments."""
        raise NotImplementedError("Attachments not supported")

    async def delete_attachment(self, attachment_id: str, context: UserContext) -> None:
        """Not implemented - we don't support attachments."""
        raise NotImplementedError("Attachments not supported")
