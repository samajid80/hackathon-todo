"""
Standardized error response schemas (T092).

Provides consistent error formatting across all API endpoints.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str
    message: str
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response format.

    Used across all API endpoints for consistent error handling.

    Example:
        {
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again in 30 seconds.",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "abc123",
                "details": {
                    "retry_after": 30,
                    "limit": 10,
                    "window": "1 minute"
                }
            }
        }
    """

    error: Dict[str, Any]

    @classmethod
    def create(
        cls,
        code: str,
        message: str,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "ErrorResponse":
        """Create a standardized error response.

        Args:
            code: Error code (e.g., "RATE_LIMIT_EXCEEDED", "OPENAI_API_ERROR")
            message: Human-readable error message
            request_id: Optional request identifier for debugging
            details: Optional additional error details

        Returns:
            ErrorResponse with standardized structure
        """
        error_data = {
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        if request_id:
            error_data["request_id"] = request_id

        if details:
            error_data["details"] = details

        return cls(error=error_data)


# Error code constants
class ErrorCode:
    """Standard error codes used across the application."""

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # OpenAI API
    OPENAI_API_ERROR = "OPENAI_API_ERROR"
    OPENAI_RATE_LIMIT = "OPENAI_RATE_LIMIT"
    OPENAI_CONNECTION_ERROR = "OPENAI_CONNECTION_ERROR"
    OPENAI_UNAVAILABLE = "OPENAI_UNAVAILABLE"

    # MCP Server
    MCP_SERVER_ERROR = "MCP_SERVER_ERROR"
    MCP_SERVER_UNAVAILABLE = "MCP_SERVER_UNAVAILABLE"
    MCP_TOOL_ERROR = "MCP_TOOL_ERROR"

    # Phase 2 Backend
    PHASE2_BACKEND_UNAVAILABLE = "PHASE2_BACKEND_UNAVAILABLE"
    PHASE2_BACKEND_ERROR = "PHASE2_BACKEND_ERROR"

    # Authentication
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"

    # Database
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_UNAVAILABLE = "DATABASE_UNAVAILABLE"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"

    # General
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    BAD_REQUEST = "BAD_REQUEST"
