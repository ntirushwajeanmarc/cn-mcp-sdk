"""Authentication and cache stats module."""

from __future__ import annotations

from typing import Any

import httpx
from ._request import request_json


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
        return request_json(self._client, "GET", "/auth/cache/stats")

    def logout(self) -> None:
        """Logout and evict current API key from cache."""
        request_json(self._client, "POST", "/auth/logout")


__all__ = ["AuthClient"]
