"""Search module."""

from __future__ import annotations

from typing import Any

import httpx


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
    ) -> list[dict[str, Any]]:
        """Search the web using SerpAPI.

        Args:
            query: Search query string
            location: Location for localized search (optional)
            num_results: Number of results (default: 10)

        Returns:
            List of search results with title, url, snippet, position
        """
        params = {
            "q": query,
            "num": num_results,
        }
        if location:
            params["location"] = location

        resp = self._client.get("/search/web", params=params)
        return resp.json()


__all__ = ["SearchClient"]
