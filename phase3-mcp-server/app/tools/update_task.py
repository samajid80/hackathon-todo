"""
MCP Tool: update_task

Updates task title and/or description.
"""

from typing import Dict, Any, Optional
from app.clients.phase2_client import Phase2Client


async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    jwt_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update task fields.

    Args:
        user_id: User identifier
        task_id: Task identifier (UUID)
        title: New task title (optional, 1-200 characters)
        description: New task description (optional, 0-2000 characters)
        due_date: New due date in ISO 8601 format YYYY-MM-DD (optional, e.g., "2025-12-26")
        priority: New priority level - "low", "medium", or "high" (optional)
        jwt_token: Optional JWT token for authentication

    Returns:
        Updated task object from Phase 2 backend

    Raises:
        httpx.HTTPStatusError: If Phase 2 API request fails
        ValueError: If no fields are provided for update
    """
    if all(field is None for field in [title, description, due_date, priority]):
        raise ValueError("At least one field must be provided for update")

    client = Phase2Client()
    try:
        result = await client.update_task(
            user_id=user_id,
            task_id=task_id,
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
TOOL_NAME = "update_task"
TOOL_DESCRIPTION = "Update task fields including title, description, due date, and priority"
