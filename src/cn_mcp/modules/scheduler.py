"""Scheduler module."""

from __future__ import annotations

from typing import Any

import httpx
from ._request import request_json, request_list


class SchedulerClient:
    """Client for scheduler operations."""

    def __init__(self, client: httpx.Client):
        """Initialize scheduler client.

        Args:
            client: HTTP client instance
        """
        self._client = client

    def schedule(
        self,
        payload: dict[str, Any],
        in_seconds: int | None = None,
        run_at: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Schedule a task.

        Args:
            payload: Task payload (arbitrary JSON)
            in_seconds: Schedule for N seconds in the future (alternative to run_at)
            run_at: ISO timestamp to run at (alternative to in_seconds)
            session_id: Optional session context for the callback

        Returns:
            Scheduled task data with task_id, status, run_at
        """
        req_data: dict[str, Any] = {"payload": payload}
        if in_seconds is not None:
            req_data["in_seconds"] = in_seconds
        if run_at is not None:
            req_data["run_at"] = run_at
        if session_id is not None:
            req_data["session_id"] = session_id

        return request_json(self._client, "POST", "/scheduler/schedule", json=req_data)

    def list(self) -> list[dict[str, Any]]:
        """List all tasks for current user.

        Returns:
            List of task objects
        """
        return request_list(self._client, "GET", "/scheduler/tasks")

    def cancel(self, task_id: str) -> dict[str, Any]:
        """Cancel a task.

        Args:
            task_id: Task ID to cancel

        Returns:
            Cancelled task data
        """
        return request_json(self._client, "POST", f"/scheduler/tasks/{task_id}/cancel")


__all__ = ["SchedulerClient"]
