"""Rate limiting middleware for API endpoints (T156).

This module implements rate limiting to prevent abuse and attacks:
- Brute force attacks on auth endpoints
- Account enumeration attempts
- Data scraping attacks

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

    Tracks requests per identifier (IP or user) within a time window.
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
            identifier: Unique identifier (IP address or user_id)
            max_requests: Maximum number of requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
            - is_allowed: True if request is allowed, False otherwise
            - retry_after_seconds: Seconds to wait before retry (0 if allowed)

        Example:
            allowed, retry = limiter.is_allowed("192.168.1.1", 5, 3600)
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
    """FastAPI middleware for rate limiting API endpoints (T156).

    Rate Limits:
        - /api/auth/signup: 5 requests per hour per IP (prevents account enumeration)
        - /api/auth/login: 5 requests per hour per IP (prevents brute force)
        - /api/tasks: 100 requests per hour per user (prevents data scraping)
        - /api/tasks/{id}/*: 100 requests per hour per user

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

        max_requests, window_seconds, identifier_type = rate_limit_config

        # Get identifier (IP or user_id)
        identifier = self._get_identifier(request, identifier_type)

        # Check rate limit
        allowed, retry_after = self.limiter.is_allowed(
            identifier=identifier,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )

        if not allowed:
            # Log rate limit violation (INFO level to avoid spam)
            logger.info(
                f"Rate limit exceeded for {identifier_type}={identifier} on {path}. "
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

    def _get_rate_limit_config(self, path: str) -> tuple[int, int, str] | None:
        """Get rate limit configuration for endpoint.

        Args:
            path: Request path

        Returns:
            Tuple of (max_requests, window_seconds, identifier_type) or None
            - max_requests: Maximum requests allowed in window
            - window_seconds: Time window in seconds
            - identifier_type: "ip" or "user" (how to identify requester)

        Rate Limit Configuration:
            - Auth endpoints: 5 requests/hour per IP
            - Task endpoints: 100 requests/hour per user
        """
        # Auth endpoints: Rate limit by IP address
        if path in ["/api/auth/signup", "/api/auth/login"]:
            # 5 requests per hour (3600 seconds) per IP
            return (5, 3600, "ip")

        # Task endpoints: Rate limit by user (from JWT)
        if path.startswith("/api/tasks"):
            # 100 requests per hour per user
            return (100, 3600, "user")

        # No rate limit for other endpoints
        return None

    def _get_identifier(self, request: Request, identifier_type: str) -> str:
        """Get identifier for rate limiting.

        Args:
            request: FastAPI request object
            identifier_type: "ip" or "user"

        Returns:
            str: Identifier (IP address or user_id)

        Note:
            For "user" type, we extract user_id from state (set by JWT middleware).
            If user_id is not available, we fall back to IP address.
        """
        if identifier_type == "ip":
            # Get client IP (handle proxies with X-Forwarded-For)
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                # Take first IP in chain (original client)
                return forwarded_for.split(",")[0].strip()
            return request.client.host if request.client else "unknown"

        elif identifier_type == "user":
            # Get user_id from request state (set by JWT middleware)
            # Fall back to IP if user_id not available (e.g., unauthenticated)
            user_id = getattr(request.state, "user_id", None)
            if user_id:
                return f"user:{user_id}"
            # Fallback to IP for unauthenticated requests
            return self._get_identifier(request, "ip")

        # Default to IP
        return self._get_identifier(request, "ip")
