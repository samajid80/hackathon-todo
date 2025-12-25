"""Task context manager for tracking last-referenced task.

This module manages conversation context to resolve "this" references in commands.
Design documented in specs/001-phase3-task-tags/data-model.md Section 1.3.
"""

from enum import Enum
from typing import Optional


class CommandType(str, Enum):
    """Types of commands that affect context."""

    LIST_TASKS = "list_tasks"  # Resets context
    FILTER_TASKS = "filter_tasks"  # Resets context
    CREATE_TASK = "create_task"  # Resets context
    UPDATE_TASK = "update_task"  # Preserves context
    DELETE_TASK = "delete_task"  # Preserves context
    COMPLETE_TASK = "complete_task"  # Preserves context


class TaskContext:
    """Manages task context for resolving 'this' references.

    Context Reset Rules:
        - list_tasks: Resets context (viewing multiple tasks)
        - filter_tasks: Resets context (viewing filtered tasks)
        - create_task: Resets context (new task created)

    Context Preservation Rules:
        - update_task: Preserves context (still working with same task)
        - delete_task: Preserves context (confirmation workflow)
        - complete_task: Preserves context (toggling completion)

    Usage:
        context = TaskContext()
        context.update(CommandType.LIST_TASKS)  # Resets last_task_id
        context.update(CommandType.UPDATE_TASK, "task-uuid")  # Sets last_task_id
        task_id = context.resolve_this()  # Returns "task-uuid" or None
    """

    def __init__(self) -> None:
        """Initialize empty context."""
        self.last_task_id: Optional[str] = None
        self.last_command_type: Optional[CommandType] = None

    def update(self, command_type: CommandType, task_id: Optional[str] = None) -> None:
        """Update context based on command type and task ID.

        Args:
            command_type: Type of command being executed
            task_id: Task ID (optional, only for task-specific commands)
        """
        # Reset context for task-related navigation commands
        if command_type in [
            CommandType.LIST_TASKS,
            CommandType.FILTER_TASKS,
            CommandType.CREATE_TASK,
        ]:
            self.last_task_id = None
        elif task_id:
            # Preserve/update context for task modification commands
            self.last_task_id = task_id

        self.last_command_type = command_type

    def resolve_this(self) -> Optional[str]:
        """Resolve 'this' reference to a task ID.

        Returns:
            Task ID if available, None if context is empty or ambiguous
        """
        return self.last_task_id

    def should_ask_clarification(self) -> bool:
        """Check if 'this' reference is ambiguous.

        Returns:
            True if no task is in context (need to ask user for clarification)
        """
        return self.last_task_id is None

    def reset(self) -> None:
        """Explicitly reset all context."""
        self.last_task_id = None
        self.last_command_type = None
