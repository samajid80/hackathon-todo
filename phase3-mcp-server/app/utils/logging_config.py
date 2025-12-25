"""Selective logging configuration for tag operations.

This module configures logging to capture only:
    - Errors (for debugging)
    - Low confidence tag extraction (<70%)

As specified in specs/001-phase3-task-tags/research.md Section 5.
"""

import logging
import sys
from typing import Optional


def configure_tag_logging(
    log_level: str = "INFO", log_file: Optional[str] = None
) -> logging.Logger:
    """Configure selective logging for tag operations.

    Logging Strategy:
        - Errors: Always logged (for debugging)
        - Low confidence (<70%): Logged for NLP model improvement
        - Successful operations: NOT logged (reduce log volume)

    Args:
        log_level: Logging level (default: INFO)
        log_file: Optional log file path (default: stdout only)

    Returns:
        Configured logger for tag operations
    """
    logger = logging.getLogger("phase3_mcp_server.tags")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_low_confidence_extraction(
    logger: logging.Logger,
    user_input: str,
    extracted_tags: list[str],
    confidence: float,
    user_id: str,
) -> None:
    """Log low-confidence tag extraction for analysis.

    Args:
        logger: Logger instance
        user_input: Original user message
        extracted_tags: List of extracted tags
        confidence: Extraction confidence (0.0-1.0)
        user_id: User identifier
    """
    if confidence < 0.70:
        logger.info(
            f"Low confidence tag extraction: confidence={confidence:.2f}, "
            f"user_id={user_id}, input='{user_input}', tags={extracted_tags}"
        )


def log_tag_operation_error(
    logger: logging.Logger,
    operation: str,
    error: Exception,
    user_id: str,
    task_id: Optional[str] = None,
) -> None:
    """Log tag operation error for debugging.

    Args:
        logger: Logger instance
        operation: Operation name (e.g., "add_tag", "list_tags")
        error: Exception that occurred
        user_id: User identifier
        task_id: Optional task identifier
    """
    context = f"user_id={user_id}"
    if task_id:
        context += f", task_id={task_id}"

    logger.error(f"Tag operation failed: operation={operation}, {context}, error={str(error)}")
