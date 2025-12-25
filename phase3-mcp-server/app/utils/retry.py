"""Retry logic utility for HTTP requests.

This module provides exponential backoff with single retry for handling transient
failures. Research documented in specs/001-phase3-task-tags/research.md Section 4.
"""

import asyncio
import logging
from typing import Any, Callable, TypeVar

import httpx

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryError(Exception):
    """Exception raised when retry attempts are exhausted."""

    pass


async def call_with_retry(
    func: Callable[..., T],
    *args: Any,
    retry_delay: float = 2.0,
    **kwargs: Any,
) -> T:
    """Call async function with single retry on failure.

    Strategy:
        - Single retry after 2 seconds
        - Catches transient failures (network, timeout, 5xx errors)
        - Does NOT retry on validation errors (4xx except 429)

    Args:
        func: Async function to call
        *args: Positional arguments for func
        retry_delay: Delay in seconds before retry (default: 2.0)
        **kwargs: Keyword arguments for func

    Returns:
        Result from function call

    Raises:
        RetryError: If both attempts fail
        HTTPException: For non-retryable errors (400, 401, 403, 404)
    """
    try:
        return await func(*args, **kwargs)
    except httpx.RequestError as e:
        # Network/connection errors - retry
        logger.warning(f"Request failed: {e}. Retrying after {retry_delay}s...")
        await asyncio.sleep(retry_delay)

        try:
            return await func(*args, **kwargs)
        except Exception as retry_error:
            logger.error(f"Retry failed: {retry_error}")
            raise RetryError(
                "Unable to complete operation after retry. Please try again."
            ) from retry_error
    except httpx.HTTPStatusError as e:
        # HTTP errors
        if e.response.status_code >= 500:
            # 5xx errors - retry
            logger.warning(
                f"Server error {e.response.status_code}: {e}. Retrying after {retry_delay}s..."
            )
            await asyncio.sleep(retry_delay)

            try:
                return await func(*args, **kwargs)
            except Exception as retry_error:
                logger.error(f"Retry failed: {retry_error}")
                raise RetryError(
                    "Unable to complete operation after retry. Please try again."
                ) from retry_error
        elif e.response.status_code == 429:
            # Rate limit - retry
            logger.warning(f"Rate limited. Retrying after {retry_delay}s...")
            await asyncio.sleep(retry_delay)

            try:
                return await func(*args, **kwargs)
            except Exception as retry_error:
                logger.error(f"Retry failed: {retry_error}")
                raise RetryError("Rate limited. Please try again later.") from retry_error
        else:
            # 4xx errors (except 429) - don't retry
            logger.error(f"Client error {e.response.status_code}: {e}")
            raise
