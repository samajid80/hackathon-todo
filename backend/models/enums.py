"""Enum definitions for task priority and status."""

from enum import Enum


class Priority(str, Enum):
    """Task priority levels.

    Inherits from str to ensure proper serialization in FastAPI/Pydantic.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    """Task completion status.

    Inherits from str to ensure proper serialization in FastAPI/Pydantic.
    """

    PENDING = "pending"
    COMPLETED = "completed"


class TaskStatusFilter(str, Enum):
    """Task status filter options for API query parameters.

    Used in GET /api/tasks endpoint to filter tasks by status.
    'overdue' is a computed filter: pending tasks with due_date < today.
    """

    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class TaskSortBy(str, Enum):
    """Task sort field options for API query parameters.

    Used in GET /api/tasks endpoint to sort tasks.
    """

    DUE_DATE = "due_date"
    PRIORITY = "priority"
    STATUS = "status"
    CREATED_AT = "created_at"


class SortOrder(str, Enum):
    """Sort order options for API query parameters.

    Used in GET /api/tasks endpoint to specify ascending or descending order.
    """

    ASC = "asc"
    DESC = "desc"
