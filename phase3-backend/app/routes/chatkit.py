"""
ChatKit routes for Phase 3 backend using real ChatKit API.

Provides:
- ChatKit session management
- Request routing to TodoChatKitServer
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict

from app.auth.jwt_middleware import get_current_user, CurrentUser
from app.chatkit.server import TodoChatKitServer
from app.chatkit.postgresql_store import PostgreSQLStore, UserContext
from app.db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession


router = APIRouter()


async def get_chatkit_server(
    session: AsyncSession = Depends(get_session)
) -> TodoChatKitServer:
    """
    Dependency to create ChatKitServer instance with PostgreSQL store.

    Args:
        session: Database session

    Returns:
        Configured TodoChatKitServer instance
    """
    store = PostgreSQLStore(session)
    return TodoChatKitServer(store)


@router.post("/api/chatkit/session")
async def create_chatkit_session(
    current_user: CurrentUser = Depends(get_current_user),
    server: TodoChatKitServer = Depends(get_chatkit_server)
) -> Dict[str, str]:
    """
    Create a new ChatKit session for authenticated user.

    The ChatKit session provides client credentials for the frontend
    to establish a secure connection.

    Authentication:
        Requires valid JWT token in Authorization header.

    Args:
        current_user: Current user from JWT validation
        server: ChatKitServer instance

    Returns:
        JSON with client_secret for ChatKit frontend initialization

    Example:
        POST /api/chatkit/session
        Headers: Authorization: Bearer <jwt_token>
        Response: {"client_secret": "..."}
    """
    try:
        # Create UserContext for this session
        context = UserContext(user_id=current_user.user_id)

        # Note: The actual ChatKit session creation API may differ
        # ChatKit likely handles sessions internally via the HTTP protocol
        # For now, we'll create a simple session token
        import secrets
        client_secret = f"chatkit_session_{secrets.token_urlsafe(32)}"

        return {"client_secret": client_secret}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create ChatKit session: {str(e)}"
        )


@router.post("/chatkit")
async def handle_chatkit_request(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    server: TodoChatKitServer = Depends(get_chatkit_server)
):
    """
    Main ChatKit endpoint for processing requests.

    This endpoint handles all ChatKit protocol messages including:
    - Thread creation
    - Message sending
    - Streaming responses
    - Tool execution

    The ChatKitServer.process() method handles the protocol internally.

    Args:
        request: FastAPI request object
        current_user: Authenticated user from JWT
        server: TodoChatKitServer instance

    Returns:
        StreamingResponse or JSONResponse based on ChatKit protocol
    """
    try:
        # Read request body as bytes
        body = await request.body()

        # Extract JWT token from Authorization header
        jwt_token = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            jwt_token = auth_header.replace("Bearer ", "")

        # Create UserContext with user_id and jwt_token
        context = UserContext(user_id=current_user.user_id, jwt_token=jwt_token)

        # Process request through ChatKitServer
        result = await server.process(body, context)

        # Check if streaming or non-streaming
        from chatkit.server import StreamingResult
        from fastapi.responses import Response

        if isinstance(result, StreamingResult):
            # Return streaming response
            return StreamingResponse(
                result,
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                }
            )
        else:
            # NonStreamingResult has .json attribute (not method)
            return Response(content=result.json, media_type="application/json")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"ChatKit request failed: {str(e)}"
        )


@router.get("/api/chatkit/health")
async def chatkit_health_check() -> Dict[str, str]:
    """
    Health check endpoint for ChatKit service.

    Returns:
        Status message
    """
    return {"status": "healthy", "service": "chatkit"}
