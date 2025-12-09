"""Task service with business logic for task operations."""

from typing import List, Optional, Tuple

from ..domain.task import Task
from ..domain.enums import Priority, Status
from ..domain.exceptions import ValidationError, TaskNotFoundError
from ..storage.repository import InMemoryTaskRepository


class TaskService:
    """Business logic service for task operations."""

    def __init__(self, repository: InMemoryTaskRepository) -> None:
        """Initialize service with a repository."""
        self.repository = repository

    def create_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
    ) -> Tuple[bool, str, Optional[Task]]:
        """Create a new task. Returns (success, message, task)."""
        try:
            task = Task(
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
            )
            self.repository.add(task)
            return (True, f"Task created with ID: {task.id[:8]}", task)
        except ValidationError as e:
            return (False, str(e), None)

    def list_tasks(
        self,
        filter_status: Optional[Status] = None,
        filter_priority: Optional[Priority] = None,
        filter_overdue: bool = False,
        sort_by: Optional[str] = None,
    ) -> List[Task]:
        """List tasks with optional filtering and sorting."""
        tasks = self.repository.list_all()

        # Apply filters
        if filter_status is not None:
            tasks = [t for t in tasks if t.status == filter_status]

        if filter_priority is not None:
            tasks = [t for t in tasks if t.priority == filter_priority]

        if filter_overdue:
            tasks = [t for t in tasks if t.is_overdue]

        # Apply sorting
        if sort_by == "priority":
            tasks.sort(key=lambda t: t.priority)
        elif sort_by == "due_date":
            tasks.sort(key=lambda t: (t.due_date is None, t.due_date or ""))
        elif sort_by == "status":
            tasks.sort(key=lambda t: t.status.value)

        return tasks

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[Priority] = None,
    ) -> Tuple[bool, str, Optional[Task]]:
        """Update task fields. Returns (success, message, task)."""
        try:
            task = self.repository.get(task_id)

            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if due_date is not None:
                task.due_date = due_date
            if priority is not None:
                task.priority = priority

            # Re-validate task after updates
            task._validate_title()
            task._validate_description()
            task._validate_due_date()

            task.mark_updated()
            self.repository.update(task)
            return (True, "Task updated successfully", task)
        except TaskNotFoundError:
            return (False, "Task not found", None)
        except ValidationError as e:
            return (False, str(e), None)

    def complete_task(self, task_id: str) -> Tuple[bool, str, Optional[Task]]:
        """Mark a task as completed. Returns (success, message, task)."""
        try:
            task = self.repository.get(task_id)
            if task.status == Status.COMPLETED:
                return (True, "Task is already completed", task)

            task.status = Status.COMPLETED
            task.mark_updated()
            self.repository.update(task)
            return (True, "Task marked as completed", task)
        except TaskNotFoundError:
            return (False, "Task not found", None)

    def delete_task(self, task_id: str) -> Tuple[bool, str, None]:
        """Delete a task by ID. Returns (success, message, None)."""
        try:
            self.repository.delete(task_id)
            return (True, "Task deleted successfully", None)
        except TaskNotFoundError:
            return (False, "Task not found", None)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID. Returns None if not found."""
        try:
            return self.repository.get(task_id)
        except TaskNotFoundError:
            return None

    def get_task_by_partial_id(self, partial_id: str) -> Optional[Task]:
        """Get a task by partial ID (e.g., first 8 chars). Returns None if not found."""
        try:
            return self.repository.get_by_partial_id(partial_id)
        except TaskNotFoundError:
            return None
