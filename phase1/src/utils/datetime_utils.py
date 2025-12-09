"""Datetime utility functions."""

from datetime import datetime


def is_valid_iso_date(date_str: str) -> bool:
    """Check if date string is valid ISO 8601 format (YYYY-MM-DD)."""
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def is_overdue(due_date: str) -> bool:
    """Check if a date is in the past."""
    if not due_date:
        return False
    try:
        return due_date < datetime.now().date().isoformat()
    except ValueError:
        return False
