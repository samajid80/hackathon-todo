"""Schema definitions for MCP server."""

from .tag_schemas import TagExtractionResult, validate_tag, validate_tags

__all__ = ["TagExtractionResult", "validate_tag", "validate_tags"]
