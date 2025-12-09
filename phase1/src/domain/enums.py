"""Enums for task priority and status."""

from enum import Enum


class Priority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """Convert string to Priority enum (case-insensitive)."""
        value_lower = value.lower()
        for priority in cls:
            if priority.value == value_lower:
                return priority
        raise ValueError(
            f"Invalid priority: {value}. Must be one of: low, medium, high"
        )

    def __lt__(self, other: object) -> bool:
        """Enable sorting: HIGH < MEDIUM < LOW (for descending sort)."""
        if not isinstance(other, Priority):
            return NotImplemented
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return order[self] < order[other]


class Status(str, Enum):
    """Task completion status."""

    PENDING = "pending"
    COMPLETED = "completed"

    @classmethod
    def from_string(cls, value: str) -> "Status":
        """Convert string to Status enum (case-insensitive)."""
        value_lower = value.lower()
        for status in cls:
            if status.value == value_lower:
                return status
        raise ValueError(f"Invalid status: {value}. Must be one of: pending, completed")
