"""
MCP Tool: update_task

Updates task fields including title, description, due date, priority, and tags.
Supports natural language tag extraction and tag merging.
"""

import logging
from typing import Any, Dict, List, Optional

from app.clients.phase2_client import Phase2Client
from app.schemas.tag_schemas import validate_tags
from app.tools.tag_extractor import TagExtractor
from app.utils.context_manager import TaskContext
from app.utils.logging_config import log_low_confidence_extraction, log_tag_operation_error
from app.utils.retry import call_with_retry

logger = logging.getLogger("phase3_mcp_server.tags")


async def update_task(
    user_id: str,
    task_id: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    add_tags: Optional[List[str]] = None,
    natural_language_input: Optional[str] = None,
    context: Optional[TaskContext] = None,
    jwt_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update task fields with optional tag extraction and context resolution.

    Args:
        user_id: User identifier
        task_id: Task identifier (UUID) - if None, uses context to resolve "this"
        title: New task title (optional, 1-200 characters)
        description: New task description (optional, 0-2000 characters)
        due_date: New due date in ISO 8601 format YYYY-MM-DD (optional)
        priority: New priority level - "low", "medium", or "high" (optional)
        tags: Replace all tags with this list (optional)
        add_tags: Add these tags to existing tags (optional, merges with current tags)
        natural_language_input: Natural language input for tag extraction
        context: TaskContext instance for "this" resolution (optional)
        jwt_token: Optional JWT token for authentication

    Returns:
        Updated task object from Phase 2 backend

    Raises:
        ValueError: If no task_id and context cannot resolve "this"
        ValueError: If no fields are provided for update
        ValueError: If tag validation fails
        httpx.HTTPStatusError: If Phase 2 API request fails
    """
    # T031: Resolve task_id from context if not provided
    if task_id is None:
        if context is None or context.should_ask_clarification():
            raise ValueError(
                "No task specified. Please specify which task to update "
                "(e.g., 'update task abc123' or refer to a specific task first)."
            )
        task_id = context.resolve_this()

    # T030: Extract tags from natural language if provided
    extracted_tags = add_tags or []

    if natural_language_input:
        extractor = TagExtractor()
        # Use tag_extractor patterns for update (reuse creation patterns)
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

    # Determine final tags list
    final_tags: Optional[List[str]] = None

    if tags is not None:
        # Replace all tags
        final_tags = tags
    elif extracted_tags:
        # Merge with existing tags (fetch current task first)
        client = Phase2Client()
        try:
            current_task = await client.get_task(user_id=user_id, task_id=task_id, jwt_token=jwt_token)
            current_tags = current_task.get("tags", [])
            # Merge: current + new (deduplicated)
            final_tags = list(set(current_tags + extracted_tags))
        except Exception as e:
            log_tag_operation_error(
                logger=logger, operation="fetch_current_tags", error=e, user_id=user_id, task_id=task_id
            )
            raise
        finally:
            await client.close()

    # Validate tags if provided
    if final_tags is not None:
        valid_tags, invalid_tags = validate_tags(final_tags)

        if invalid_tags:
            raise ValueError(
                f"Invalid tag(s): {', '.join(invalid_tags)}. "
                "Tags can only contain lowercase letters, numbers, and hyphens (1-50 chars)."
            )

        if len(valid_tags) > 10:
            raise ValueError(
                f"Maximum 10 tags allowed per task. You would have {len(valid_tags)} tags."
            )

        final_tags = valid_tags

    # Ensure at least one field is being updated
    if all(field is None for field in [title, description, due_date, priority, final_tags]):
        raise ValueError("At least one field must be provided for update")

    # Update task with retry logic
    client = Phase2Client()
    try:

        async def _update_task() -> Dict[str, Any]:
            return await client.update_task(
                user_id=user_id,
                task_id=task_id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                tags=final_tags,
                jwt_token=jwt_token,
            )

        result = await call_with_retry(_update_task)

        # T032: Update context (preserve last_task_id for chained operations)
        if context is not None:
            from app.utils.context_manager import CommandType

            context.update(CommandType.UPDATE_TASK, task_id)

        return result
    except Exception as e:
        log_tag_operation_error(
            logger=logger, operation="update_task", error=e, user_id=user_id, task_id=task_id
        )
        raise
    finally:
        await client.close()


# Tool metadata for MCP registration
TOOL_NAME = "update_task"
TOOL_DESCRIPTION = (
    "Update task fields including title, description, due date, priority, and tags. "
    "Supports natural language tag extraction (e.g., 'tag this with urgent') and context resolution ('this')."
)
