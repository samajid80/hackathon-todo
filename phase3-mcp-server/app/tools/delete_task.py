"""
MCP Tool: delete_task

Permanently deletes a task.
"""

from typing import Dict, Any, Optional
from app.clients.phase2_client import Phase2Client


async def delete_task(
    user_id: str,
    task_id: str,
    jwt_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Permanently delete a task.

    Args:
        user_id: User identifier
        task_id: Task identifier (UUID)
        jwt_token: Optional JWT token for authentication

    Returns:
        Deletion confirmation from Phase 2 backend

    Raises:
        httpx.HTTPStatusError: If Phase 2 API request fails
    """
    client = Phase2Client()
    try:
        result = await client.delete_task(
            user_id=user_id,
            task_id=task_id,
            jwt_token=jwt_token
        )
        return result
    finally:
        await client.close()


# Tool metadata for MCP registration
TOOL_NAME = "delete_task"
TOOL_DESCRIPTION = "Permanently delete a task (use with confirmation)"
