"""
MCP Tool: list_tasks

Lists user's tasks with optional filtering by completion status and tags.
Supports natural language tag extraction for filtering.
"""

import logging
from typing import Any, Dict, List, Optional

from app.clients.phase2_client import Phase2Client
from app.tools.tag_extractor import TagExtractor
from app.utils.logging_config import log_low_confidence_extraction
from app.utils.retry import call_with_retry

logger = logging.getLogger("phase3_mcp_server.tags")


async def list_tasks(
    user_id: str,
    completed: Optional[bool] = None,
    tags: Optional[List[str]] = None,
    natural_language_filter: Optional[str] = None,
    jwt_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List all tasks for the user, optionally filtered by completion status and tags.

    Args:
        user_id: User identifier
        completed: Optional filter (true = completed only, false = incomplete only, None = all)
        tags: Optional explicit tag filter (AND logic: task must have all tags)
        natural_language_filter: Optional natural language filter (e.g., "show work tasks")
        jwt_token: Optional JWT token for authentication

    Returns:
        Dictionary with tasks list and metadata

    Raises:
        ValueError: If tag extraction confidence is too low (<70%)
        httpx.HTTPStatusError: If Phase 2 API request fails
    """
    # Extract tags from natural language if provided
    extracted_tags = tags or []
    extraction_confidence = 1.0

    if natural_language_filter:
        extractor = TagExtractor()
        extraction_result = extractor.extract_tags_for_filtering(natural_language_filter)
        extracted_tags = extraction_result.tags
        extraction_confidence = extraction_result.confidence

        # Log low confidence extractions
        log_low_confidence_extraction(
            logger=logger,
            user_input=natural_language_filter,
            extracted_tags=extracted_tags,
            confidence=extraction_confidence,
            user_id=user_id,
        )

        # T023: Ask for clarification if confidence is too low
        if extraction_confidence < 0.70:
            raise ValueError(
                f"Could not confidently extract tags from '{natural_language_filter}'. "
                f"Please be more specific (e.g., 'show tasks tagged with work')."
            )

    # Call Phase 2 backend with retry logic
    client = Phase2Client()
    try:

        async def _fetch_tasks() -> List[Dict[str, Any]]:
            return await client.list_tasks(
                user_id=user_id, completed=completed, tags=extracted_tags, jwt_token=jwt_token
            )

        tasks = await call_with_retry(_fetch_tasks)

        # T025: Handle "no tasks found" case
        if not tasks and extracted_tags:
            return {
                "tasks": [],
                "message": f"No tasks found with tag(s): {', '.join(extracted_tags)}",
                "tag_filter": extracted_tags,
            }

        return {
            "tasks": tasks,
            "message": f"Found {len(tasks)} task(s)",
            "tag_filter": extracted_tags if extracted_tags else None,
        }
    finally:
        await client.close()


# Tool metadata for MCP registration
TOOL_NAME = "list_tasks"
TOOL_DESCRIPTION = (
    "List user's tasks, optionally filtered by completion status and tags. "
    "Supports natural language filters like 'show work tasks' or 'my urgent tasks'."
)
