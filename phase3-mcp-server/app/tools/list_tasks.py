"""
MCP Tool: list_tasks

Lists user's tasks with optional filtering by completion status.
"""

from typing import Dict, Any, List, Optional
from app.clients.phase2_client import Phase2Client


async def list_tasks(
    user_id: str,
    completed: Optional[bool] = None,
    jwt_token: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all tasks for the user, optionally filtered by completion status.

    Args:
        user_id: User identifier
        completed: Optional filter (true = completed only, false = incomplete only, None = all)
        jwt_token: Optional JWT token for authentication

    Returns:
        List of task objects from Phase 2 backend

    Raises:
        httpx.HTTPStatusError: If Phase 2 API request fails
    """
    client = Phase2Client()
    try:
        result = await client.list_tasks(
            user_id=user_id,
            completed=completed,
            jwt_token=jwt_token
        )
        return result
    finally:
        await client.close()


# Tool metadata for MCP registration
TOOL_NAME = "list_tasks"
TOOL_DESCRIPTION = "List user's tasks, optionally filtered by completion status"
