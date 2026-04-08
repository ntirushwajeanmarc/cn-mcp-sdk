"""Sessions module."""

from __future__ import annotations

from typing import Any, Optional

import httpx


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
        resp = self._client.post("/sessions")
        return resp.json()

    def list(self) -> list[dict[str, Any]]:
        """List all active sessions for current user.

        Returns:
            List of session objects
        """
        resp = self._client.get("/sessions")
        return resp.json()

    def dispose(self, session_id: str) -> dict[str, Any]:
        """Dispose a session (stop and clean up).

        Args:
            session_id: Session ID to dispose

        Returns:
            Disposed session data
        """
        resp = self._client.post(f"/sessions/{session_id}/dispose")
        return resp.json()


__all__ = ["SessionsClient"]
