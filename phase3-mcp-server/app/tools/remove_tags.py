"""
MCP Tool: remove_tags

Removes tags from a task via natural language or explicit tag list.
"""

import logging
from typing import Any, Dict, List, Optional

from app.clients.phase2_client import Phase2Client
from app.schemas.tag_schemas import validate_tag
from app.tools.tag_extractor import TagExtractor
from app.utils.context_manager import CommandType, TaskContext
from app.utils.logging_config import log_low_confidence_extraction, log_tag_operation_error
from app.utils.retry import call_with_retry

logger = logging.getLogger("phase3_mcp_server.tags")


async def remove_tags(
    user_id: str,
    task_id: Optional[str] = None,
    remove_tags: Optional[List[str]] = None,
    remove_all: bool = False,
    natural_language_input: Optional[str] = None,
    context: Optional[TaskContext] = None,
    jwt_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Remove tags from a task.

    Args:
        user_id: User identifier
        task_id: Task identifier (UUID) - if None, uses context to resolve "this"
        remove_tags: List of tags to remove (optional)
        remove_all: If True, removes all tags from the task
        natural_language_input: Natural language input for tag extraction
        context: TaskContext instance for "this" resolution (optional)
        jwt_token: Optional JWT token for authentication

    Returns:
        Updated task object from Phase 2 backend

    Raises:
        ValueError: If no task_id and context cannot resolve "this"
        ValueError: If tag not found on task
        httpx.HTTPStatusError: If Phase 2 API request fails
    """
    # T049: Resolve task_id from context if not provided
    if task_id is None:
        if context is None or context.should_ask_clarification():
            raise ValueError(
                "No task specified. Please specify which task to remove tags from "
                "(e.g., 'remove tags from task abc123' or refer to a specific task first)."
            )
        task_id = context.resolve_this()

    # T043: Extract tags from natural language if provided
    tags_to_remove = remove_tags or []

    if natural_language_input:
        extractor = TagExtractor()
        extraction_result = extractor.extract_tags_for_removal(natural_language_input)

        # Check for "remove all tags" marker
        if "__ALL__" in extraction_result.tags:
            remove_all = True
        else:
            tags_to_remove = extraction_result.tags

        # Log low confidence extractions
        log_low_confidence_extraction(
            logger=logger,
            user_input=natural_language_input,
            extracted_tags=tags_to_remove,
            confidence=extraction_result.confidence,
            user_id=user_id,
        )

    # Fetch current task to get existing tags
    client = Phase2Client()
    try:
        current_task = await client.get_task(user_id=user_id, task_id=task_id, jwt_token=jwt_token)
        current_tags = current_task.get("tags", [])

        # T046: Handle "remove all tags"
        if remove_all:
            new_tags = []
        else:
            # T045: Remove specific tags
            new_tags = current_tags.copy()

            for tag in tags_to_remove:
                # Validate and normalize tag
                is_valid, normalized_tag = validate_tag(tag)
                if not is_valid:
                    raise ValueError(f"Invalid tag '{tag}': {normalized_tag}")

                # T047: Check if tag exists on task
                if normalized_tag not in new_tags:
                    raise ValueError(f"This task doesn't have the '{normalized_tag}' tag.")

                # Remove tag
                new_tags.remove(normalized_tag)

        # Update task with new tag list
        async def _update_task() -> Dict[str, Any]:
            return await client.update_task(
                user_id=user_id, task_id=task_id, tags=new_tags, jwt_token=jwt_token
            )

        result = await call_with_retry(_update_task)

        # Update context (preserve last_task_id for chained operations)
        if context is not None:
            context.update(CommandType.UPDATE_TASK, task_id)

        return result
    except Exception as e:
        log_tag_operation_error(
            logger=logger, operation="remove_tags", error=e, user_id=user_id, task_id=task_id
        )
        raise
    finally:
        await client.close()


# Tool metadata for MCP registration
TOOL_NAME = "remove_tags"
TOOL_DESCRIPTION = (
    "Remove tags from a task. Supports removing specific tags or all tags at once. "
    "Supports natural language (e.g., 'remove the urgent tag', 'remove all tags') and context resolution ('this')."
)
