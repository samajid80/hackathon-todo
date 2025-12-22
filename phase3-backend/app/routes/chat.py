"""
Chat API endpoints for Phase 3 Backend.

Handles natural language conversation with AI assistant.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from app.auth.jwt_middleware import CurrentUser, get_current_user
from app.schemas.errors import ErrorResponse, ErrorCode
from app.utils.sanitization import sanitize_message, validate_conversation_id
from app.services.chat_service import (
    ChatService,
    list_user_conversations,
    delete_user_conversation,
)
from app.agents.openai_agent import run_agent
from app.agents.mcp_client import MCPClient


router = APIRouter(prefix="/api", tags=["Chat"])


# Request/Response Models
class SendMessageRequest(BaseModel):
    """Request to send a message to the AI assistant."""

    conversation_id: Optional[str] = Field(
        None,
        description="Existing conversation ID, or None to create new conversation"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message to the assistant"
    )


class MessageResponse(BaseModel):
    """Message object in response."""

    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


class SendMessageResponse(BaseModel):
    """Response after sending a message."""

    conversation_id: str
    user_message: MessageResponse
    assistant_message: MessageResponse
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ConversationHistoryResponse(BaseModel):
    """Response with conversation history."""

    conversation_id: str
    messages: List[MessageResponse]


class ConversationListItem(BaseModel):
    """Single conversation in list."""

    id: str
    created_at: str
    updated_at: str


class ConversationListResponse(BaseModel):
    """Response with list of conversations."""

    conversations: List[ConversationListItem]


from sqlmodel.ext.asyncio.session import AsyncSession
from app.db import get_session

@router.post("/chat", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    http_request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    """
    Send a message to the AI assistant and get a response.

    Flow:
    1. Get or create conversation
    2. Save user message
    3. Get conversation history (last 20 messages)
    4. Call OpenAI agent with history and MCP tools
    5. Save assistant response
    6. Return both messages with tool calls log

    Args:
        request: User message and optional conversation_id
        current_user: Authenticated user from JWT

    Returns:
        User message, assistant response, and tool calls

    Raises:
        HTTPException: 500 if agent or database operations fail
    """
    try:
        import time
        from uuid import UUID
        start_time = time.time()

        # Create ChatService with the injected session
        chat_service = ChatService(session)

        # Step 0: Validate and sanitize input (T097)
        sanitized_message = sanitize_message(request.message)

        if not sanitized_message:
            raise ValueError("Message cannot be empty after sanitization")

        # Validate conversation ID format if provided
        validated_conversation_id = validate_conversation_id(request.conversation_id)

        # Step 1: Get or create conversation
        t1 = time.time()
        conv_uuid = UUID(validated_conversation_id) if validated_conversation_id else None
        conversation = await chat_service.get_or_create_conversation(
            user_id=current_user.user_id,
            conversation_id=conv_uuid
        )
        conversation_id = str(conversation.id)
        print(f"[Performance] Get/create conversation: {(time.time() - t1)*1000:.0f}ms")

        # Step 2: Save user message (with sanitized content)
        t2 = time.time()
        user_message = await chat_service.save_message(
            user_id=current_user.user_id,
            conversation_id=conversation.id,
            role="user",
            content=sanitized_message
        )
        print(f"[Performance] Save user message: {(time.time() - t2)*1000:.0f}ms")

        # Step 3: Get conversation history for context (last 20 messages)
        t3 = time.time()
        history = await chat_service.get_message_history(conversation.id, limit=20)
        print(f"[Performance] Get message history: {(time.time() - t3)*1000:.0f}ms")

        # Convert history to OpenAI format (exclude system messages)
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in history
            if msg.role in ["user", "assistant"]
        ]

        # Extract JWT token from Authorization header
        jwt_token = None
        if authorization and authorization.startswith("Bearer "):
            jwt_token = authorization.replace("Bearer ", "")

        # Step 4: Call OpenAI agent with MCP client
        t4 = time.time()
        mcp_client = MCPClient()
        try:
            print(f"[Performance] Calling OpenAI agent with model gpt-4o-mini...")
            assistant_content, tool_calls_log = await run_agent(
                messages=messages,
                user_id=current_user.user_id,
                mcp_client=mcp_client,
                jwt_token=jwt_token
            )
            print(f"[Performance] OpenAI agent call: {(time.time() - t4)*1000:.0f}ms")
        finally:
            await mcp_client.close()

        # Step 5: Save assistant response
        t5 = time.time()
        assistant_message = await chat_service.save_message(
            user_id=current_user.user_id,
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_content
        )
        print(f"[Performance] Save assistant message: {(time.time() - t5)*1000:.0f}ms")

        # Step 6: Commit all changes in a single transaction
        t6 = time.time()
        await session.commit()
        print(f"[Performance] Database commit: {(time.time() - t6)*1000:.0f}ms")
        print(f"[Performance] TOTAL request time: {(time.time() - start_time)*1000:.0f}ms")

        # Step 6: Return response
        return SendMessageResponse(
            conversation_id=conversation_id,
            user_message=MessageResponse(
                id=str(user_message.id),
                conversation_id=conversation_id,
                role=user_message.role,
                content=user_message.content,
                created_at=user_message.created_at.isoformat(),
            ),
            assistant_message=MessageResponse(
                id=str(assistant_message.id),
                conversation_id=conversation_id,
                role=assistant_message.role,
                content=assistant_message.content,
                created_at=assistant_message.created_at.isoformat(),
                tool_calls=tool_calls_log if tool_calls_log else None,
            ),
            tool_calls=tool_calls_log if tool_calls_log else None,
        )

    except ValueError as e:
        # Handle errors from agent (OpenAI API, MCP server, etc.)
        error_message = str(e)
        print(f"[Chat API] ValueError: {error_message}")

        # Determine error code based on message content
        if "OpenAI API rate limit" in error_message or "Rate limit" in error_message:
            code = ErrorCode.OPENAI_RATE_LIMIT
            message = "The AI service is currently experiencing high demand. Please try again in a moment."
        elif "Unable to connect to OpenAI" in error_message or "Connection error" in error_message:
            code = ErrorCode.OPENAI_CONNECTION_ERROR
            message = "Unable to reach the AI service. Please check your connection and try again."
        elif "OpenAI API is experiencing issues" in error_message:
            code = ErrorCode.OPENAI_UNAVAILABLE
            message = "The AI service is temporarily unavailable. Please try again later."
        elif "MCP tool" in error_message:
            code = ErrorCode.MCP_TOOL_ERROR
            message = f"An error occurred while processing your request: {error_message}"
        else:
            code = ErrorCode.INTERNAL_SERVER_ERROR
            message = "An unexpected error occurred. Please try again."

        # Generate request ID for debugging
        request_id = str(uuid4())[:8]

        error_response = ErrorResponse.create(
            code=code,
            message=message,
            request_id=request_id,
            details={"original_error": error_message}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )

    except HTTPException:
        # Re-raise HTTP exceptions (auth errors, rate limit, etc.)
        raise

    except Exception as e:
        # Catch-all for unexpected errors
        print(f"[Chat API] Unexpected error: {type(e).__name__}: {str(e)}")
        request_id = str(uuid4())[:8]

        error_response = ErrorResponse.create(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while processing your message. Please try again.",
            request_id=request_id,
            details={"error_type": type(e).__name__}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get conversation history by ID.

    Args:
        conversation_id: Conversation UUID
        current_user: Authenticated user from JWT

    Returns:
        Conversation history with all messages

    Raises:
        HTTPException: 404 if conversation not found or not owned by user
    """
    try:
        messages = await get_message_history(conversation_id)

        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=[
                MessageResponse(
                    id=str(msg.id),
                    conversation_id=conversation_id,
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at.isoformat(),
                )
                for msg in messages
            ],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation not found: {str(e)}"
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    List all conversations for the authenticated user.

    Args:
        current_user: Authenticated user from JWT

    Returns:
        List of user's conversations

    Raises:
        HTTPException: 500 if database query fails
    """
    try:
        conversations = await list_user_conversations(current_user.user_id)

        return ConversationListResponse(
            conversations=[
                ConversationListItem(
                    id=str(conv.id),
                    created_at=conv.created_at.isoformat(),
                    updated_at=conv.updated_at.isoformat(),
                )
                for conv in conversations
            ]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list conversations: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Delete a conversation and all its messages.

    Args:
        conversation_id: Conversation UUID
        current_user: Authenticated user from JWT

    Raises:
        HTTPException: 404 if conversation not found or not owned by user
    """
    try:
        await delete_user_conversation(
            user_id=current_user.user_id,
            conversation_id=conversation_id
        )
        return None

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation not found: {str(e)}"
        )
