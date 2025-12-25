"""Tag validation schemas and extraction result models.

This module provides validation for tag format and extraction result structures
as defined in specs/001-phase3-task-tags/data-model.md.
"""

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class TagSource(str, Enum):
    """Source of tag extraction."""

    EXPLICIT = "explicit"  # User explicitly mentioned tags ("tagged with work")
    IMPLICIT = "implicit"  # Inferred from context ("work tasks" → filter by "work")


class TagExtractionResult(BaseModel):
    """Structured output from NLP tag extraction.

    Attributes:
        tags: List of extracted tag names
        confidence: Extraction confidence (0.0-1.0)
        source: How tags were extracted (explicit/implicit)
        raw_input: Original user message
    """

    tags: list[str]
    confidence: float
    source: TagSource
    raw_input: str

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0.0 and 1.0."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tag_list(cls, v: list[str]) -> list[str]:
        """Validate each tag in the list."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return v


def validate_tag(tag: str) -> tuple[bool, str]:
    """Validate a single tag against Phase 2 backend rules.

    Args:
        tag: Tag string to validate

    Returns:
        Tuple of (is_valid, normalized_tag_or_error_message)

    Validation Rules (from Phase 2 backend):
        - Length: 1-50 characters
        - Format: ^[a-z0-9-]+$ (lowercase alphanumeric + hyphens)
        - Automatic normalization: trim whitespace, convert to lowercase
    """
    # Normalize: trim and lowercase
    tag = tag.strip().lower()

    # Check length
    if len(tag) < 1:
        return False, "Tag cannot be empty"
    if len(tag) > 50:
        return False, "Tag must be 1-50 characters"

    # Check format
    if not re.match(r"^[a-z0-9-]+$", tag):
        return False, "Tags can only contain lowercase letters, numbers, and hyphens"

    return True, tag


def validate_tags(tags: list[str]) -> tuple[list[str], list[str]]:
    """Validate a list of tags.

    Args:
        tags: List of tag strings to validate

    Returns:
        Tuple of (valid_tags, invalid_tags)
        - valid_tags: Normalized valid tags
        - invalid_tags: Tags that failed validation
    """
    valid = []
    invalid = []

    for tag in tags:
        is_valid, result = validate_tag(tag)
        if is_valid:
            valid.append(result)
        else:
            invalid.append(tag)

    # Check count limit
    if len(valid) > 10:
        # Move excess tags to invalid
        invalid.extend(valid[10:])
        valid = valid[:10]

    return valid, invalid
