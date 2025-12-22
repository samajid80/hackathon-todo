"""
Message sanitization utilities (T097).

Prevents XSS, injection attacks, and other security issues.
"""

import html
import re
from typing import Optional


def sanitize_message(message: str) -> str:
    """
    Sanitize user message before storing in database.

    Removes/escapes potentially dangerous content while preserving
    legitimate text and formatting.

    Args:
        message: Raw user message

    Returns:
        Sanitized message safe for storage and display

    Security measures:
        - HTML entity encoding to prevent XSS
        - Remove null bytes
        - Normalize whitespace
        - Strip leading/trailing whitespace
        - Remove control characters (except newlines and tabs)
    """
    if not message:
        return ""

    # Remove null bytes (common injection technique)
    sanitized = message.replace("\x00", "")

    # Remove other control characters except newline and tab
    # Keep: \n (newline), \r (carriage return), \t (tab)
    # Remove: Other control chars (0x00-0x1F except \n, \r, \t)
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)

    # HTML escape to prevent XSS
    # This converts <, >, &, ', " to HTML entities
    sanitized = html.escape(sanitized, quote=True)

    # Normalize excessive whitespace
    # Replace multiple spaces with single space
    sanitized = re.sub(r' {2,}', ' ', sanitized)

    # Normalize line breaks (convert CRLF to LF)
    sanitized = sanitized.replace('\r\n', '\n').replace('\r', '\n')

    # Remove excessive line breaks (more than 3 consecutive)
    sanitized = re.sub(r'\n{4,}', '\n\n\n', sanitized)

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    return sanitized


def validate_conversation_id(conversation_id: Optional[str]) -> Optional[str]:
    """
    Validate conversation ID format.

    Args:
        conversation_id: UUID string or None

    Returns:
        Validated conversation ID or None

    Raises:
        ValueError: If conversation ID format is invalid
    """
    if conversation_id is None:
        return None

    # UUID format validation (loose check)
    # Format: 8-4-4-4-12 hex digits
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

    if not re.match(uuid_pattern, conversation_id.lower()):
        raise ValueError(f"Invalid conversation ID format: {conversation_id}")

    return conversation_id.lower()


def sanitize_task_title(title: str) -> str:
    """
    Sanitize task title (more restrictive than message).

    Args:
        title: Task title

    Returns:
        Sanitized title

    Note:
        Titles don't allow newlines or tabs.
    """
    if not title:
        return ""

    # Remove ALL control characters (including newlines and tabs)
    sanitized = re.sub(r'[\x00-\x1F\x7F]', '', title)

    # HTML escape
    sanitized = html.escape(sanitized, quote=True)

    # Normalize whitespace
    sanitized = re.sub(r' {2,}', ' ', sanitized)

    # Strip
    sanitized = sanitized.strip()

    return sanitized
