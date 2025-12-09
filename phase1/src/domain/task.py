"""Task domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

from .enums import Priority, Status
from .exceptions import ValidationError


@dataclass
class Task:
    """Represents a todo task with metadata for tracking work items."""

    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        """Validate task fields after initialization."""
        self._validate_title()
        self._validate_description()
        self._validate_due_date()

    def _validate_title(self) -> None:
        """Validate title field (required, 1-200 chars)."""
        if not self.title or len(self.title) < 1:
            raise ValidationError("Title is required")
        if len(self.title) > 200:
            raise ValidationError("Title must be 200 characters or less")

    def _validate_description(self) -> None:
        """Validate description field (optional, up to 2000 chars)."""
        if len(self.description) > 2000:
            raise ValidationError("Description must be 2000 characters or less")

    def _validate_due_date(self) -> None:
        """Validate due_date field (optional, ISO 8601 format YYYY-MM-DD)."""
        if self.due_date and not self._is_valid_iso_date(self.due_date):
            raise ValidationError("Date must be in ISO format YYYY-MM-DD")

    @staticmethod
    def _is_valid_iso_date(date_str: str) -> bool:
        """Check if date string is valid ISO 8601 format (YYYY-MM-DD)."""
        try:
            datetime.fromisoformat(date_str)
            return True
        except ValueError:
            return False

    def mark_updated(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now().isoformat()

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue (past due date and still pending)."""
        if not self.due_date or self.status == Status.COMPLETED:
            return False
        return self.due_date < datetime.now().date().isoformat()
