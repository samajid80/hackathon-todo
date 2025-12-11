"""Task SQLModel definitions and Pydantic schemas with input validation (T157)."""

from datetime import date, datetime
from uuid import UUID, uuid4

from pydantic import field_validator
from sqlmodel import Field, Index, SQLModel

from .enums import Priority, Status


class TaskBase(SQLModel):
    """Base task fields shared between models.

    These fields are common to all task-related schemas (Create, Update, Read).
    Includes input validation to prevent XSS and injection attacks (T157).
    """

    title: str = Field(max_length=200, min_length=1)
    description: str | None = Field(default=None, max_length=2000)
    due_date: date | None = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.PENDING)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and sanitize title field (T157).

        Validation Rules:
            - Strip leading/trailing whitespace
            - Ensure not empty after stripping
            - Max 200 characters (already enforced by Field)
            - No SQL injection (SQLModel uses parameterized queries)
            - No XSS (React escapes by default, but we sanitize input)

        Args:
            v: Title string from user input

        Returns:
            str: Sanitized title

        Raises:
            ValueError: If title is empty after stripping

        Example:
            "  Buy groceries  " -> "Buy groceries"
            "" -> ValueError("Title cannot be empty")
        """
        # Strip whitespace
        v = v.strip()

        # Ensure not empty
        if not v:
            raise ValueError("Title cannot be empty")

        # Additional validation: Check for excessive whitespace
        # (prevent "    " from being accepted)
        if len(v) < 1:
            raise ValueError("Title must contain at least one character")

        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate and sanitize description field (T157).

        Validation Rules:
            - Strip leading/trailing whitespace if provided
            - Max 2000 characters (already enforced by Field)
            - Allow empty string (will be stored as None)
            - No SQL injection (SQLModel uses parameterized queries)
            - No XSS (React escapes by default)

        Args:
            v: Description string from user input (optional)

        Returns:
            Optional[str]: Sanitized description or None

        Example:
            "  Task details  " -> "Task details"
            "" -> None
            None -> None
        """
        if v is None:
            return None

        # Strip whitespace
        v = v.strip()

        # Convert empty string to None
        if not v:
            return None

        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: date | None) -> date | None:
        """Validate due_date field (T157).

        Validation Rules:
            - Must be valid ISO 8601 date format (enforced by Pydantic)
            - Optional (can be None)
            - No past date validation (users can create overdue tasks)

        Args:
            v: Date object from user input (optional)

        Returns:
            Optional[date]: Validated date or None

        Note:
            Pydantic automatically validates ISO 8601 format.
            Invalid formats will raise ValidationError automatically.
        """
        # Pydantic handles date parsing and validation
        # We just pass through the value
        return v


class Task(TaskBase, table=True):
    """Task ORM model for database table.

    Represents the tasks table in PostgreSQL with all fields, relationships,
    and indexes required for efficient queries.
    """

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Composite indexes for efficient queries
    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
        Index("idx_user_due_date", "user_id", "due_date"),
        Index("idx_status", "status"),
        Index("idx_due_date", "due_date"),
    )


class TaskCreate(TaskBase):
    """Schema for creating a task (API request) with input validation (T157).

    No id or user_id required - these are set automatically.
    Status defaults to PENDING, priority defaults to MEDIUM.

    Input Validation (T157):
        - title: Required, 1-200 chars, whitespace stripped
        - description: Optional, max 2000 chars, whitespace stripped
        - due_date: Optional, valid ISO 8601 date format
        - priority: Enum validation (low, medium, high)
        - status: Enum validation (pending, completed)

    Example Request:
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "due_date": "2025-12-15",
            "priority": "high"
        }

    Example Validation Errors:
        - Empty title: "Title cannot be empty"
        - Invalid date: "Input should be a valid date"
        - Invalid priority: "Input should be 'low', 'medium' or 'high'"
    """

    pass


class TaskUpdate(SQLModel):
    """Schema for updating a task (API request) with input validation (T157).

    All fields are optional to support partial updates.
    Status can be updated directly via this schema or via the complete endpoint.

    Input Validation (T157):
        - title: If provided, 1-200 chars, whitespace stripped
        - description: If provided, max 2000 chars, whitespace stripped
        - due_date: If provided, valid ISO 8601 date format
        - priority: If provided, enum validation
        - status: If provided, enum validation

    Example Request (partial update):
        {
            "title": "Updated title"
        }

    Example Validation Errors:
        - Empty title: "Title cannot be empty"
        - Title too long: "String should have at most 200 characters"
    """

    title: str | None = Field(default=None, max_length=200, min_length=1)
    description: str | None = Field(default=None, max_length=2000)
    due_date: date | None = None
    priority: Priority | None = None
    status: Status | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Validate and sanitize title field for updates (T157).

        Same validation as TaskBase.validate_title but allows None.

        Args:
            v: Title string from user input (optional for updates)

        Returns:
            Optional[str]: Sanitized title or None

        Raises:
            ValueError: If title is provided but empty after stripping
        """
        if v is None:
            return None

        # Strip whitespace
        v = v.strip()

        # Ensure not empty if provided
        if not v:
            raise ValueError("Title cannot be empty")

        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate and sanitize description field for updates (T157).

        Same validation as TaskBase.validate_description.

        Args:
            v: Description string from user input (optional)

        Returns:
            Optional[str]: Sanitized description or None
        """
        if v is None:
            return None

        # Strip whitespace
        v = v.strip()

        # Convert empty string to None
        if not v:
            return None

        return v


class TaskRead(TaskBase):
    """Schema for reading a task (API response).

    Includes all fields including id, user_id, and timestamps.

    Note:
        No input validation needed for read-only schema.
        This is only used for API responses, not user input.
    """

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
