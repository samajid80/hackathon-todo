"""In-memory task repository."""

from typing import Dict, List

from ..domain.task import Task
from ..domain.exceptions import TaskNotFoundError


class InMemoryTaskRepository:
    """In-memory storage for tasks using a dictionary."""

    def __init__(self) -> None:
        """Initialize empty repository."""
        self._tasks: Dict[str, Task] = {}

    def add(self, task: Task) -> None:
        """Add a task to the repository."""
        self._tasks[task.id] = task

    def get(self, task_id: str) -> Task:
        """Get a task by ID. Raises TaskNotFoundError if not found."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return self._tasks[task_id]

    def get_by_partial_id(self, partial_id: str) -> Task:
        """Get a task by partial ID (e.g., first 8 chars of UUID).

        Raises TaskNotFoundError if not found or if multiple matches exist.
        """
        # First try exact match
        if partial_id in self._tasks:
            return self._tasks[partial_id]

        # Then try partial match
        matches = [task for task_id, task in self._tasks.items()
                   if task_id.startswith(partial_id)]

        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise TaskNotFoundError(
                f"Multiple tasks found with ID starting with: {partial_id}"
            )
        else:
            raise TaskNotFoundError(f"Task not found: {partial_id}")

    def update(self, task: Task) -> None:
        """Update an existing task. Raises TaskNotFoundError if not found."""
        if task.id not in self._tasks:
            raise TaskNotFoundError(f"Task not found: {task.id}")
        self._tasks[task.id] = task

    def delete(self, task_id: str) -> None:
        """Delete a task by ID. Raises TaskNotFoundError if not found."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        del self._tasks[task_id]

    def list_all(self) -> List[Task]:
        """Return all tasks."""
        return list(self._tasks.values())

    def exists(self, task_id: str) -> bool:
        """Check if a task exists."""
        return task_id in self._tasks
