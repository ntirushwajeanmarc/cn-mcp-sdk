"""Terminal module."""

from __future__ import annotations

from typing import Any

import httpx


class TerminalClient:
    """Client for terminal operations."""

    def __init__(self, client: httpx.Client):
        """Initialize terminal client.

        Args:
            client: HTTP client instance
        """
        self._client = client

    def execute(
        self,
        session_id: str,
        command: str,
        timeout_minutes: int = 5,
        output_limit_kb: int = 4096,
    ) -> dict[str, Any]:
        """Execute a terminal command in a session.

        Args:
            session_id: Session ID
            command: Shell command to execute
            timeout_minutes: Command timeout in minutes (default: 5, max: 60)
            output_limit_kb: Output size limit in KB (default: 4096, max: 4096)

        Returns:
            Execution result with exit_code, output, duration_seconds
        """
        resp = self._client.post(
            "/terminal/exec",
            json={
                "session_id": session_id,
                "command": command,
                "timeout_minutes": timeout_minutes,
                "output_limit_kb": output_limit_kb,
            },
        )
        return resp.json()


__all__ = ["TerminalClient"]
