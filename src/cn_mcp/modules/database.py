"""Database module."""

from __future__ import annotations

from typing import Any

import httpx
from ._request import request_json


class DatabaseClient:
    """Client for database operations."""

    def __init__(self, client: httpx.Client):
        """Initialize database client.

        Args:
            client: HTTP client instance
        """
        self._client = client

    def query(
        self,
        session_id: str,
        sql: str,
        params: list[Any] | None = None,
        limit: int = 200,
    ) -> dict[str, Any]:
        """Execute a read-only query.

        Args:
            session_id: Session ID
            sql: SQL query (SELECT only)
            params: Query parameters
            limit: Result limit (default: 200, max: 10000)

        Returns:
            Query result with columns and rows
        """
        return request_json(
            self._client,
            "POST",
            "/db/query",
            json={
                "session_id": session_id,
                "sql": sql,
                "params": params or [],
                "limit": limit,
            },
        )

    def execute(
        self,
        session_id: str,
        sql: str,
        params: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a write operation (INSERT, UPDATE, DELETE, etc.).

        Args:
            session_id: Session ID
            sql: SQL statement
            params: Query parameters

        Returns:
            Execution result with changes count
        """
        return request_json(
            self._client,
            "POST",
            "/db/execute",
            json={
                "session_id": session_id,
                "sql": sql,
                "params": params or [],
            },
        )


__all__ = ["DatabaseClient"]
