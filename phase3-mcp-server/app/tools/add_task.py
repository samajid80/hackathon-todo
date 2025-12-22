"""
MCP Tool: add_task

Creates a new todo task via Phase 2 backend API.
"""

from typing import Dict, Any, Optional
from app.clients.phase2_client import Phase2Client


async def add_task(
    user_id: str,
    title: str,
    description: str = "",
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    jwt_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        user_id: User identifier
        title: Task title (required, 1-200 characters)
        description: Task description (optional, 0-2000 characters)
        due_date: Due date in ISO 8601 format YYYY-MM-DD (optional, e.g., "2025-12-26")
        priority: Priority level - "low", "medium", or "high" (optional, default: "medium")
        jwt_token: Optional JWT token for authentication

    Returns:
        Created task object from Phase 2 backend

    Raises:
        httpx.HTTPStatusError: If Phase 2 API request fails
    """
    client = Phase2Client()
    try:
        result = await client.create_task(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            jwt_token=jwt_token
        )
        return result
    finally:
        await client.close()


# Tool metadata for MCP registration
TOOL_NAME = "add_task"
TOOL_DESCRIPTION = "Create a new todo task with title, description, due date, and priority"
