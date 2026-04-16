"""Search module."""

from __future__ import annotations

from typing import Any

import httpx
from ._request import request_json


class SearchClient:
    """Client for search operations."""

    def __init__(self, client: httpx.Client):
        """Initialize search client.

        Args:
            client: HTTP client instance
        """
        self._client = client

    def web(
        self,
        query: str,
        location: str | None = None,
        num_results: int = 10,
    ) -> dict[str, Any]:
        """Search the web using SerpAPI.

        Args:
            query: Search query string
            location: Location for localized search (optional)
            num_results: Number of results (default: 10)

        Returns:
            Search response with organic_results, related_questions, ai_summary
        """
        payload = {
            "query": query,
            "num": num_results,
        }
        if location:
            payload["location"] = location

        return request_json(self._client, "POST", "/search", json=payload)


__all__ = ["SearchClient"]
