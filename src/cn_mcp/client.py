"""CircuitNotion MCP SDK - Main client module."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx

from .errors import MCPAuthError, MCPError, MCPNotFoundError
from .modules.auth import AuthClient
from .modules.database import DatabaseClient
from .modules.devices import DevicesClient
from .modules.files import FilesClient
from .modules.scheduler import SchedulerClient
from .modules.search import SearchClient
from .modules.sessions import SessionsClient
from .modules.terminal import TerminalClient


class MCPClient:
    """Main client for interacting with the CircuitNotion MCP Server."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        """Initialize MCP client.

        Args:
            api_key: API key for authentication. If not provided, uses MCP_API_KEY env var.
            base_url: Base URL of MCP server. If not provided, uses MCP_BASE_URL env var.
            timeout: Request timeout in seconds (default: 30).
            verify_ssl: Whether to verify SSL certificates (default: True).

        Raises:
            MCPAuthError: If no API key is provided.
        """
        self.api_key = api_key or os.getenv("MCP_API_KEY")
        if not self.api_key:
            raise MCPAuthError("API key not provided. Set MCP_API_KEY env var or pass api_key parameter.")

        self.base_url = (base_url or os.getenv("MCP_BASE_URL", "https://mcp.circuitnotion.com")).rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Create HTTP client with default headers
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"X-API-Key": self.api_key},
            timeout=timeout,
            verify=verify_ssl,
        )

        # Initialize sub-clients
        self.auth = AuthClient(self._client)
        self.sessions = SessionsClient(self._client)
        self.files = FilesClient(self._client)
        self.terminal = TerminalClient(self._client)
        self.search = SearchClient(self._client)
        self.scheduler = SchedulerClient(self._client)
        self.devices = DevicesClient(self._client)
        self.db = DatabaseClient(self._client)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the HTTP client connection."""
        self._client.close()

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Make an HTTP request to the MCP server.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to httpx

        Returns:
            Response JSON as dictionary

        Raises:
            MCPAuthError: If authentication fails (401/403)
            MCPNotFoundError: If resource not found (404)
            MCPError: For other errors
        """
        url = endpoint if endpoint.startswith("/") else f"/{endpoint}"

        try:
            resp = self._client.request(method, url, **kwargs)

            if resp.status_code == 401 or resp.status_code == 403:
                raise MCPAuthError(f"Authentication failed: {resp.text}")

            if resp.status_code == 404:
                raise MCPNotFoundError(f"Resource not found: {resp.text}")

            if resp.status_code >= 400:
                raise MCPError(f"API error ({resp.status_code}): {resp.text}")

            if resp.status_code == 204:
                return {}

            return resp.json()

        except httpx.HTTPError as e:
            raise MCPError(f"Request failed: {e}")


__all__ = [
    "MCPClient",
]
