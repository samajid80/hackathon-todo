"""
MCP Tool: complete_task

Marks a task as complete or incomplete.
"""

from typing import Dict, Any, Optional
from app.clients.phase2_client import Phase2Client


async def complete_task(
    user_id: str,
    task_id: str,
    completed: bool,
    jwt_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark a task as complete or incomplete.

    Args:
        user_id: User identifier
        task_id: Task identifier (UUID)
        completed: Completion status (true = complete, false = incomplete)
        jwt_token: Optional JWT token for authentication

    Returns:
        Updated task object from Phase 2 backend

    Raises:
        httpx.HTTPStatusError: If Phase 2 API request fails
    """
    client = Phase2Client()
    try:
        result = await client.complete_task(
            user_id=user_id,
            task_id=task_id,
            completed=completed,
            jwt_token=jwt_token
        )
        return result
    finally:
        await client.close()


# Tool metadata for MCP registration
TOOL_NAME = "complete_task"
TOOL_DESCRIPTION = "Mark a task as complete or incomplete"
