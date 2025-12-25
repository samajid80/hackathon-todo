"""
MCP Tool: list_tags

Lists all unique tags for a user via Phase 2 backend.
"""

import logging
from typing import Any, Dict, List, Optional

from app.clients.phase2_client import Phase2Client
from app.utils.logging_config import log_tag_operation_error
from app.utils.retry import call_with_retry

logger = logging.getLogger("phase3_mcp_server.tags")


async def list_tags(user_id: str, jwt_token: Optional[str] = None) -> Dict[str, Any]:
    """
    List all unique tags for the user.

    Args:
        user_id: User identifier
        jwt_token: Optional JWT token for authentication

    Returns:
        Dictionary with tags list and user-friendly message

    Raises:
        httpx.HTTPStatusError: If Phase 2 API request fails
    """
    client = Phase2Client()
    try:

        async def _fetch_tags() -> List[str]:
            return await client.list_tags(user_id=user_id, jwt_token=jwt_token)

        tags = await call_with_retry(_fetch_tags)

        # T040: Format response with alphabetically sorted tags
        tags_sorted = sorted(tags)

        # T041: Handle empty tag list
        if not tags_sorted:
            return {"tags": [], "message": "You haven't created any tags yet."}

        # Format user-friendly message
        tag_count = len(tags_sorted)
        tags_display = ", ".join(tags_sorted)

        return {
            "tags": tags_sorted,
            "count": tag_count,
            "message": f"You have {tag_count} tag{'s' if tag_count != 1 else ''}: {tags_display}",
        }
    except Exception as e:
        log_tag_operation_error(logger=logger, operation="list_tags", error=e, user_id=user_id)
        raise
    finally:
        await client.close()


# Tool metadata for MCP registration
TOOL_NAME = "list_tags"
TOOL_DESCRIPTION = (
    "List all unique tags for the user. Returns tags in alphabetical order. "
    "Useful for discovering available tags (e.g., 'what tags do I have?')."
)
