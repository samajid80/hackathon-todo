"""
MCP Tool: add_task

Creates a new todo task via Phase 2 backend API with tag extraction support.
"""

import logging
from typing import Any, Dict, List, Optional

from app.clients.phase2_client import Phase2Client
from app.schemas.tag_schemas import validate_tags
from app.tools.tag_extractor import TagExtractor
from app.utils.logging_config import log_low_confidence_extraction, log_tag_operation_error
from app.utils.retry import call_with_retry

logger = logging.getLogger("phase3_mcp_server.tags")


async def add_task(
    user_id: str,
    title: str,
    description: str = "",
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    natural_language_input: Optional[str] = None,
    jwt_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new task for the user with optional tag extraction from natural language.

    Args:
        user_id: User identifier
        title: Task title (required, 1-200 characters)
        description: Task description (optional, 0-2000 characters)
        due_date: Due date in ISO 8601 format YYYY-MM-DD (optional, e.g., "2025-12-26")
        priority: Priority level - "low", "medium", or "high" (optional, default: "medium")
        tags: Optional explicit list of tags
        natural_language_input: Optional natural language input for tag extraction
        jwt_token: Optional JWT token for authentication

    Returns:
        Created task object from Phase 2 backend

    Raises:
        ValueError: If tag validation fails (count >10, invalid format)
        httpx.HTTPStatusError: If Phase 2 API request fails
    """
    # T029: Extract tags from natural language if provided
    extracted_tags = tags or []

    if natural_language_input:
        extractor = TagExtractor()
        extraction_result = extractor.extract_tags_for_creation(natural_language_input)
        extracted_tags = extraction_result.tags

        # Log low confidence extractions
        log_low_confidence_extraction(
            logger=logger,
            user_input=natural_language_input,
            extracted_tags=extracted_tags,
            confidence=extraction_result.confidence,
            user_id=user_id,
        )

    # T033 & T034: Validate tags (count and format)
    if extracted_tags:
        valid_tags, invalid_tags = validate_tags(extracted_tags)

        if invalid_tags:
            raise ValueError(
                f"Invalid tag(s): {', '.join(invalid_tags)}. "
                "Tags can only contain lowercase letters, numbers, and hyphens (1-50 chars)."
            )

        if len(valid_tags) > 10:
            raise ValueError(
                f"Maximum 10 tags allowed per task. You provided {len(valid_tags)} tags."
            )

        extracted_tags = valid_tags

    # Create task with retry logic
    client = Phase2Client()
    try:

        async def _create_task() -> Dict[str, Any]:
            return await client.create_task(
                user_id=user_id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                tags=extracted_tags if extracted_tags else None,
                jwt_token=jwt_token,
            )

        result = await call_with_retry(_create_task)
        return result
    except Exception as e:
        log_tag_operation_error(logger=logger, operation="add_task", error=e, user_id=user_id)
        raise
    finally:
        await client.close()


# Tool metadata for MCP registration
TOOL_NAME = "add_task"
TOOL_DESCRIPTION = (
    "Create a new todo task with title, description, due date, priority, and optional tags. "
    "Supports natural language tag extraction (e.g., 'buy groceries tagged with home')."
)
