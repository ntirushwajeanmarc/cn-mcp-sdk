"""Sessions module."""

from __future__ import annotations

from typing import Any

import httpx
from ._request import request_json, request_list


class SessionsClient:
    """Client for session management."""

    def __init__(self, client: httpx.Client):
        """Initialize sessions client.

        Args:
            client: HTTP client instance
        """
        self._client = client

    def create(self) -> dict[str, Any]:
        """Create a new session.

        Returns:
            Session data with session_id, user_id, created_at, last_seen_at, status
        """
        return request_json(self._client, "POST", "/sessions")

    def list(self) -> list[dict[str, Any]]:
        """List all active sessions for current user.

        Returns:
            List of session objects
        """
        return request_list(self._client, "GET", "/sessions")

    def dispose(self, session_id: str) -> dict[str, Any]:
        """Dispose a session (stop and clean up).

        Args:
            session_id: Session ID to dispose

        Returns:
            Disposed session data
        """
        return request_json(self._client, "POST", f"/sessions/{session_id}/dispose")


__all__ = ["SessionsClient"]
