"""Custom exceptions for the domain layer."""


class ValidationError(Exception):
    """Raised when task field validation fails."""

    pass


class TaskNotFoundError(Exception):
    """Raised when task is not found in repository."""

    pass
