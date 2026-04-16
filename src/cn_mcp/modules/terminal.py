"""Terminal module."""

from __future__ import annotations

from typing import Any

import httpx
from ._request import request_json


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
        output_limit_kb: int = 256,
    ) -> dict[str, Any]:
        """Execute a terminal command in a session.

        Args:
            session_id: Session ID
            command: Shell command to execute
            timeout_minutes: Command timeout in minutes (default: 5, max: 60)
            output_limit_kb: Output size limit in KB (default: 256, max: 4096)

        Returns:
            Execution result with exit_code, stdout, stderr, duration_ms, truncated
        """
        result = request_json(
            self._client,
            "POST",
            "/terminal/exec",
            json={
                "session_id": session_id,
                "cmd": command,
                "timeout_minutes": timeout_minutes,
                "max_output_kb": output_limit_kb,
            },
        )
        # Normalize response to provide unified 'output' field combining stdout and stderr
        if "stdout" in result:
            result["output"] = result.get("stdout", "") + result.get("stderr", "")
        return result


__all__ = ["TerminalClient"]
