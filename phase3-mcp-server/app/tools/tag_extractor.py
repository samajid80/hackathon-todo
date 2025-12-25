"""NLP-based tag extraction utility.

This module provides pattern matching and context-aware extraction for tags
from natural language user messages. Research design documented in
specs/001-phase3-task-tags/research.md Section 1.
"""

import re

from ..schemas.tag_schemas import TagExtractionResult, TagSource, validate_tags


class TagExtractor:
    """Extract tags from natural language using pattern matching."""

    # Explicit tag addition patterns
    EXPLICIT_ADD_PATTERNS = [
        r"tagged with\s+(.+)",
        r"tag(?:s)?:\s*(.+)",
        r"with tags?\s+(.+)",
        r"tag this with\s+(.+)",
        r"add tags?\s+(.+)",
    ]

    # Explicit tag filtering patterns
    EXPLICIT_FILTER_PATTERNS = [
        r"show\s+(?:me\s+)?tasks?\s+tagged\s+with\s+(.+)",
        r"list\s+(?:my\s+)?(.+)\s+tasks?",
        r"show\s+(?:my\s+)?(.+)\s+tasks?",
        r"tasks?\s+tagged\s+with\s+(.+)",
        r"my\s+(.+)\s+tasks?",
    ]

    # Tag listing patterns
    LIST_TAGS_PATTERNS = [
        r"what tags do I have",
        r"list my tags",
        r"show (?:all )?(?:my )?tags",
        r"what are my tags",
    ]

    # Tag removal patterns
    REMOVE_TAG_PATTERNS = [
        r"remove\s+(?:the\s+)?(.+)\s+tag",
        r"untag\s+(?:this from\s+)?(.+)",
        r"delete\s+tag\s+(.+)",
        r"remove all tags",
    ]

    # Stop words to exclude from tag extraction
    STOP_WORDS = {
        "the",
        "a",
        "an",
        "this",
        "that",
        "from",
        "to",
        "and",
        "or",
        "with",
        "tagged",
        "tag",
        "tags",
    }

    def extract_tags_for_creation(self, message: str) -> TagExtractionResult:
        """Extract tags from task creation command.

        Args:
            message: User message (e.g., "add task buy milk tagged with home")

        Returns:
            TagExtractionResult with extracted tags and confidence
        """
        message_lower = message.lower()

        # Try explicit patterns first
        for pattern in self.EXPLICIT_ADD_PATTERNS:
            match = re.search(pattern, message_lower)
            if match:
                tag_string = match.group(1)
                tags = self._parse_tag_string(tag_string)
                valid_tags, _ = validate_tags(tags)

                confidence = self._calculate_confidence(
                    pattern_matched=True, tag_count=len(valid_tags)
                )

                return TagExtractionResult(
                    tags=valid_tags,
                    confidence=confidence,
                    source=TagSource.EXPLICIT,
                    raw_input=message,
                )

        # No tags found
        return TagExtractionResult(
            tags=[], confidence=1.0, source=TagSource.EXPLICIT, raw_input=message
        )

    def extract_tags_for_filtering(self, message: str) -> TagExtractionResult:
        """Extract tags from filtering command.

        Args:
            message: User message (e.g., "show me work tasks")

        Returns:
            TagExtractionResult with extracted tags and confidence
        """
        message_lower = message.lower()

        # Try explicit filter patterns
        for pattern in self.EXPLICIT_FILTER_PATTERNS:
            match = re.search(pattern, message_lower)
            if match:
                tag_string = match.group(1)
                tags = self._parse_tag_string(tag_string)
                valid_tags, _ = validate_tags(tags)

                # Determine source based on pattern
                if "tagged with" in message_lower:
                    source = TagSource.EXPLICIT
                    confidence = 0.95
                else:
                    source = TagSource.IMPLICIT
                    confidence = self._calculate_confidence(
                        pattern_matched=True, tag_count=len(valid_tags)
                    )

                return TagExtractionResult(
                    tags=valid_tags,
                    confidence=confidence,
                    source=source,
                    raw_input=message,
                )

        # No tags found
        return TagExtractionResult(
            tags=[], confidence=0.5, source=TagSource.IMPLICIT, raw_input=message
        )

    def extract_tags_for_removal(self, message: str) -> TagExtractionResult:
        """Extract tags from removal command.

        Args:
            message: User message (e.g., "remove the urgent tag")

        Returns:
            TagExtractionResult with extracted tags and confidence
        """
        message_lower = message.lower()

        # Check for "remove all tags"
        if "remove all tags" in message_lower or "delete all tags" in message_lower:
            return TagExtractionResult(
                tags=["__ALL__"],  # Special marker for remove all
                confidence=1.0,
                source=TagSource.EXPLICIT,
                raw_input=message,
            )

        # Try removal patterns
        for pattern in self.REMOVE_TAG_PATTERNS:
            match = re.search(pattern, message_lower)
            if match:
                tag_string = match.group(1)
                tags = self._parse_tag_string(tag_string)
                valid_tags, _ = validate_tags(tags)

                confidence = self._calculate_confidence(
                    pattern_matched=True, tag_count=len(valid_tags)
                )

                return TagExtractionResult(
                    tags=valid_tags,
                    confidence=confidence,
                    source=TagSource.EXPLICIT,
                    raw_input=message,
                )

        # No tags found
        return TagExtractionResult(
            tags=[], confidence=0.5, source=TagSource.EXPLICIT, raw_input=message
        )

    def is_list_tags_command(self, message: str) -> bool:
        """Check if message is a tag listing command.

        Args:
            message: User message

        Returns:
            True if message matches tag listing patterns
        """
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in self.LIST_TAGS_PATTERNS)

    def _parse_tag_string(self, tag_string: str) -> list[str]:
        """Parse tag string into list of tags.

        Args:
            tag_string: String containing tags (e.g., "work, urgent" or "work and urgent")

        Returns:
            List of normalized tag strings
        """
        # Split on commas or "and"
        tags = re.split(r",\s*|\s+and\s+", tag_string)

        # Clean up tags: remove stop words, trim whitespace
        cleaned_tags = []
        for tag in tags:
            words = tag.split()
            filtered_words = [w for w in words if w not in self.STOP_WORDS]
            if filtered_words:
                cleaned_tag = "-".join(filtered_words)  # Join multi-word tags with hyphen
                cleaned_tags.append(cleaned_tag)

        return cleaned_tags

    def _calculate_confidence(self, pattern_matched: bool, tag_count: int) -> float:
        """Calculate extraction confidence.

        Args:
            pattern_matched: Whether a pattern was successfully matched
            tag_count: Number of tags extracted

        Returns:
            Confidence score between 0.0 and 1.0
        """
        base = 0.5
        if pattern_matched:
            base = 0.9
        if tag_count > 0:
            base += 0.1 * min(tag_count, 3)
        return min(base, 1.0)
