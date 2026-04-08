"""Authentication and cache stats module."""

from __future__ import annotations

from typing import Any

import httpx


class AuthClient:
    """Client for authentication and cache statistics."""

    def __init__(self, client: httpx.Client):
        """Initialize auth client.

        Args:
            client: HTTP client instance
        """
        self._client = client

    def cache_stats(self) -> dict[str, Any]:
        """Get API key cache statistics.

        Returns:
            Cache stats with size, max_size, ttl_seconds, negative_ttl_seconds
        """
        resp = self._client.get("/auth/cache-stats")
        return resp.json()

    def logout(self) -> None:
        """Logout and evict current API key from cache."""
        self._client.post("/auth/logout")


__all__ = ["AuthClient"]
