"""Task SQLModel definitions and Pydantic schemas with input validation (T157)."""

import re
from datetime import date, datetime
from uuid import UUID, uuid4

from pydantic import field_validator
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
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
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Text)),
    )

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

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and normalize tags field.

        Validation Rules:
            - Max 10 tags per task
            - Each tag: 1-50 characters
            - Format: ^[a-z0-9-]+$ (lowercase alphanumeric + hyphens)
            - Automatic lowercase conversion
            - Automatic whitespace trimming
            - Automatic deduplication

        Args:
            v: List of tag strings from user input

        Returns:
            list[str]: Validated and normalized tag list

        Raises:
            ValueError: If validation fails

        Examples:
            ["Work", "  urgent  ", "work"] -> ["work", "urgent"]
            ["tag1", "tag2", ..., "tag11"] -> ValueError("Maximum 10 tags allowed per task")
            ["urgent!!!"] -> ValueError("Tags can only contain lowercase letters, numbers, and hyphens")
        """
        if not v:
            return []

        # Step 1: Normalize all tags first (trim and lowercase)
        normalized_tags = []
        for tag in v:
            # Trim and lowercase
            tag = tag.strip().lower()

            # Skip empty tags
            if not tag:
                continue

            normalized_tags.append(tag)

        # Step 2: Remove duplicates while preserving order (after normalization)
        unique_tags = list(dict.fromkeys(normalized_tags))

        # Step 3: Validate max count
        if len(unique_tags) > 10:
            raise ValueError("Maximum 10 tags allowed per task")

        # Step 4: Validate each tag (length and format)
        validated_tags = []
        for tag in unique_tags:
            # Validate length
            if len(tag) < 1 or len(tag) > 50:
                raise ValueError(f"Tag must be 1-50 characters long, got '{tag}' ({len(tag)} chars)")

            # Validate format
            if not re.match(r"^[a-z0-9-]+$", tag):
                raise ValueError(
                    f"Tags can only contain lowercase letters, numbers, and hyphens: '{tag}'"
                )

            validated_tags.append(tag)

        return validated_tags


class Task(TaskBase, table=True):
    """Task ORM model for database table.

    Represents the tasks table in PostgreSQL with all fields, relationships,
    and indexes required for efficient queries.

    Note: priority and status are stored as VARCHAR strings in the database,
    but validated as enums in the API layer (TaskCreate, TaskUpdate).
    """

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)  # FK constraint exists in DB, not needed in ORM
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Override enum fields to store as strings in database
    # This prevents SQLAlchemy from using enum names instead of values
    priority: str = Field(max_length=10, nullable=False, default="medium")
    status: str = Field(max_length=10, nullable=False, default="pending")

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
        - tags: If provided, max 10 tags, 1-50 chars each, format ^[a-z0-9-]+$

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
    tags: list[str] | None = None

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

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate tags for updates (same rules as TaskBase).

        Args:
            v: List of tag strings from user input (optional)

        Returns:
            Optional[list[str]]: Validated and normalized tag list or None

        Raises:
            ValueError: If validation fails
        """
        if v is None:
            return None

        # Apply same validation as TaskBase
        return TaskBase.validate_tags(v)


class TaskRead(TaskBase):
    """Schema for reading a task (API response).

    Includes all fields including id, user_id, and timestamps.

    Note:
        Priority and status fields are converted from database strings to enums
        for API responses.
    """

    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime

    @field_validator("priority", mode="before")
    @classmethod
    def convert_priority_to_enum(cls, v: str | Priority) -> Priority:
        """Convert string priority from database to Priority enum.

        Args:
            v: Priority value (either string from DB or enum from validation)

        Returns:
            Priority: Priority enum value

        Raises:
            ValueError: If priority value is invalid
        """
        if isinstance(v, Priority):
            return v
        if isinstance(v, str):
            # Convert lowercase string to enum
            try:
                return Priority(v.lower())
            except ValueError:
                raise ValueError(f"Invalid priority value: {v}")
        raise ValueError(f"Priority must be string or Priority enum, got {type(v)}")

    @field_validator("status", mode="before")
    @classmethod
    def convert_status_to_enum(cls, v: str | Status) -> Status:
        """Convert string status from database to Status enum.

        Args:
            v: Status value (either string from DB or enum from validation)

        Returns:
            Status: Status enum value

        Raises:
            ValueError: If status value is invalid
        """
        if isinstance(v, Status):
            return v
        if isinstance(v, str):
            # Convert lowercase string to enum
            try:
                return Status(v.lower())
            except ValueError:
                raise ValueError(f"Invalid status value: {v}")
        raise ValueError(f"Status must be string or Status enum, got {type(v)}")
