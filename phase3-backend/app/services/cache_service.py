"""Cache service for tag lists with TTL and invalidation.

This module provides in-memory caching for user tag lists with 60-second TTL
and smart invalidation on tag operations. Design documented in
specs/001-phase3-task-tags/research.md Section 2.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional


class TagCache:
    """In-memory cache for user tag lists.

    Features:
        - Per-user keying (isolated by user_id)
        - 60-second TTL (time-to-live)
        - Smart invalidation on tag operations
        - Stateless design (per-instance cache, no shared state)

    Performance Targets:
        - Cache hit: <10ms (in-memory lookup)
        - Cache miss: ~200-500ms (HTTP call to Phase 2 backend)
        - Expected hit rate: ~80% (tags rarely change)

    Usage:
        cache = TagCache()
        tags = cache.get("user-123")  # Returns None if miss or expired
        cache.set("user-123", ["work", "home"])  # Cache for 60s
        cache.invalidate("user-123")  # Remove from cache
    """

    def __init__(self, ttl_seconds: int = 60) -> None:
        """Initialize empty cache.

        Args:
            ttl_seconds: Time-to-live for cache entries (default: 60)
        """
        self._cache: dict[str, dict] = {}
        self._ttl_seconds = ttl_seconds

    def get(self, user_id: str) -> Optional[list[str]]:
        """Get cached tags for user.

        Args:
            user_id: User identifier

        Returns:
            List of tags if cache hit and not expired, None otherwise
        """
        entry = self._cache.get(user_id)
        if entry and entry["expires_at"] > datetime.now(timezone.utc):
            return entry["tags"]
        return None

    def set(self, user_id: str, tags: list[str]) -> None:
        """Cache tags for user.

        Args:
            user_id: User identifier
            tags: List of tags to cache (will be alphabetically sorted)
        """
        self._cache[user_id] = {
            "tags": sorted(tags),  # Always alphabetically sorted
            "expires_at": datetime.now(timezone.utc) + timedelta(seconds=self._ttl_seconds),
        }

    def invalidate(self, user_id: str) -> None:
        """Invalidate cache for user.

        Args:
            user_id: User identifier
        """
        self._cache.pop(user_id, None)

    def clear_all(self) -> None:
        """Clear entire cache (for testing/debugging)."""
        self._cache.clear()

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache size and other metrics
        """
        return {
            "total_entries": len(self._cache),
            "ttl_seconds": self._ttl_seconds,
        }
