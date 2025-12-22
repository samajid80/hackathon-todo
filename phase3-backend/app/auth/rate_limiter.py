"""Rate limiting for chat API endpoints (T090).

This module implements rate limiting to prevent abuse:
- Excessive API usage
- Resource exhaustion
- OpenAI API quota exhaustion

Rate limits are enforced using an in-memory store for development.
For production, consider using Redis for distributed rate limiting.
"""

import logging
import time
from collections import defaultdict

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter using sliding window algorithm.

    Tracks requests per user within a time window.
    For production, replace with Redis-based implementation for:
    - Distributed rate limiting across multiple servers
    - Persistence across server restarts
    - Better performance at scale
    """

    def __init__(self):
        """Initialize rate limiter with in-memory storage."""
        # Storage: {identifier: [(timestamp1, count1), (timestamp2, count2), ...]}
        self._requests: dict[str, list[tuple[float, int]]] = defaultdict(list)

    def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """Check if request is allowed under rate limit.

        Args:
            identifier: Unique identifier (user_id)
            max_requests: Maximum number of requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
            - is_allowed: True if request is allowed, False otherwise
            - retry_after_seconds: Seconds to wait before retry (0 if allowed)

        Example:
            allowed, retry = limiter.is_allowed("user:123", 10, 60)
            if not allowed:
                print(f"Rate limit exceeded. Retry after {retry} seconds")
        """
        now = time.time()
        window_start = now - window_seconds

        # Clean up old entries outside the window
        self._requests[identifier] = [
            (ts, count)
            for ts, count in self._requests[identifier]
            if ts > window_start
        ]

        # Calculate total requests in current window
        total_requests = sum(count for _, count in self._requests[identifier])

        if total_requests >= max_requests:
            # Calculate retry_after based on oldest request
            if self._requests[identifier]:
                oldest_timestamp = self._requests[identifier][0][0]
                retry_after = int(oldest_timestamp + window_seconds - now)
                return False, max(1, retry_after)  # At least 1 second
            return False, window_seconds

        # Add current request
        self._requests[identifier].append((now, 1))
        return True, 0

    def cleanup_old_entries(self, max_age_seconds: int = 7200):
        """Clean up entries older than max_age to prevent memory leaks.

        Args:
            max_age_seconds: Maximum age of entries to keep (default 2 hours)

        Note:
            Call this periodically (e.g., via background task) to prevent
            unbounded memory growth in long-running applications.
        """
        now = time.time()
        cutoff = now - max_age_seconds

        # Remove entries older than cutoff
        for identifier in list(self._requests.keys()):
            self._requests[identifier] = [
                (ts, count)
                for ts, count in self._requests[identifier]
                if ts > cutoff
            ]
            # Remove identifier if no entries remain
            if not self._requests[identifier]:
                del self._requests[identifier]


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance.

    Returns:
        RateLimiter: Shared rate limiter instance
    """
    return _rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting chat API endpoints (T090).

    Rate Limits:
        - /api/chat: 10 requests per minute per user (prevents API abuse)

    Response:
        - HTTP 429 Too Many Requests with Retry-After header
        - Logged at INFO level (not WARN to avoid spam)

    Example:
        app.add_middleware(RateLimitMiddleware)
    """

    def __init__(self, app):
        """Initialize middleware with rate limiter."""
        super().__init__(app)
        self.limiter = get_rate_limiter()

    async def dispatch(self, request: Request, call_next):
        """Process request and enforce rate limits."""
        path = request.url.path

        # Define rate limits for different endpoints
        rate_limit_config = self._get_rate_limit_config(path)

        if rate_limit_config is None:
            # No rate limit for this endpoint
            return await call_next(request)

        max_requests, window_seconds = rate_limit_config

        # Get user_id from request state (set by JWT middleware)
        user_id = getattr(request.state, "user_id", None)

        if not user_id:
            # No user_id means JWT middleware hasn't run yet
            # Skip rate limiting for unauthenticated requests
            # (they'll be rejected by JWT middleware anyway)
            return await call_next(request)

        identifier = f"user:{user_id}"

        # Check rate limit
        allowed, retry_after = self.limiter.is_allowed(
            identifier=identifier,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )

        if not allowed:
            # Log rate limit violation (INFO level to avoid spam)
            logger.info(
                f"Rate limit exceeded for user {user_id} on {path}. "
                f"Retry after {retry_after} seconds."
            )

            # Return 429 Too Many Requests with Retry-After header
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Retry after {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

        # Request allowed, proceed
        return await call_next(request)

    def _get_rate_limit_config(self, path: str) -> tuple[int, int] | None:
        """Get rate limit configuration for endpoint.

        Args:
            path: Request path

        Returns:
            Tuple of (max_requests, window_seconds) or None
            - max_requests: Maximum requests allowed in window
            - window_seconds: Time window in seconds

        Rate Limit Configuration:
            - Chat endpoint: 10 requests/minute per user (T090)
        """
        # Chat endpoint: Rate limit by user
        if path == "/api/chat":
            # 10 requests per minute (60 seconds) per user
            return (10, 60)

        # No rate limit for other endpoints
        return None
