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


_TOOL_REGISTRY = {
    "web_search": ("search", "web", {"query": {"type": "string", "required": True}, "limit": {"type": "integer"}}),
    "device_list": ("devices", "list", {}),
    "device_set_state": ("devices", "set_state", {"device_id": {"type": "string", "required": True}, "action": {"type": "string", "required": True}, "parameters": {"type": "object"}}),
    "terminal_exec": ("terminal", "execute", {"session_id": {"type": "string", "required": True}, "command": {"type": "string", "required": True}, "timeout_minutes": {"type": "integer"}, "output_limit_kb": {"type": "integer"}}),
    "file_list": ("files", "list", {"session_id": {"type": "string", "required": True}}),
    "file_write": ("files", "write", {"session_id": {"type": "string", "required": True}, "path": {"type": "string", "required": True}, "content": {"type": "string", "required": True}}),
    "file_download": ("files", "download", {"file_id": {"type": "string", "required": True}}),
    "file_delete": ("files", "delete", {"file_id": {"type": "string", "required": True}}),
    "session_create": ("sessions", "create", {"name": {"type": "string"}, "template": {"type": "string"}, "timeout_minutes": {"type": "integer"}}),
    "session_list": ("sessions", "list", {}),
    "session_get": ("sessions", "get", {"session_id": {"type": "string", "required": True}}),
    "session_dispose": ("sessions", "dispose", {"session_id": {"type": "string", "required": True}}),
    "scheduler_list": ("scheduler", "list_jobs", {}),
    "scheduler_create": ("scheduler", "create_job", {"schedule": {"type": "string", "required": True}, "command": {"type": "string", "required": True}, "session_id": {"type": "string", "required": True}}),
    "scheduler_delete": ("scheduler", "delete_job", {"job_id": {"type": "string", "required": True}}),
    "db_query": ("db", "query", {"query": {"type": "string", "required": True}, "params": {"type": "object"}}),
    "db_execute": ("db", "execute", {"query": {"type": "string", "required": True}, "params": {"type": "object"}}),
    "cache_stats": ("auth", "cache_stats", {}),
    "cache_clear": ("auth", "clear_cache", {}),
}


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

    def list_tools(self) -> list[str]:
        """List all available tool names.

        Returns:
            List of tool names as strings
        """
        return list(_TOOL_REGISTRY.keys())

    def tool_call(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        """Call a tool by name dynamically.

        Args:
            tool_name: Tool name (e.g., "web_search", "device_list", "terminal_exec")
            **kwargs: Arguments to pass to the tool method

        Returns:
            Result from the tool method

        Raises:
            MCPError: If tool not found or call fails
        """
        if tool_name not in _TOOL_REGISTRY:
            available = ", ".join(_TOOL_REGISTRY.keys())
            raise MCPError(f"Unknown tool: {tool_name}. Available tools: {available}")

        module_name, method_name, _ = _TOOL_REGISTRY[tool_name]
        module = getattr(self, module_name)
        method = getattr(module, method_name)
        return method(**kwargs)

    def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        """Call a tool by name with arguments dictionary or kwargs.

        This method is compatible with the tool call pattern used by LLMs
        that return JSON with tool names and arguments.

        Args:
            tool_name: Tool name (e.g., "web_search", "device_list", "terminal_exec")
            arguments: Dictionary of arguments to pass to the tool method
            **kwargs: Alternative way to pass arguments as keyword arguments

        Returns:
            Result from the tool method

        Raises:
            MCPError: If tool not found or call fails

        Example:
            >>> mcp.call_tool("web_search", {"query": "python tutorials"})
            >>> mcp.call_tool("web_search", query="python tutorials")
        """
        if arguments is None:
            arguments = {}

        # Merge arguments dict with any additional kwargs
        if kwargs:
            arguments.update(kwargs)

        return self.tool_call(tool_name, **arguments)

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
