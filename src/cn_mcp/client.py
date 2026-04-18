"""CircuitNotion MCP SDK - Main client module."""

from __future__ import annotations

import os
from types import TracebackType
from typing import Any, Optional, cast

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


def _matches_schema_type(value: Any, schema_type: str) -> bool:
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "boolean":
        return isinstance(value, bool)
    return True


class BoundSessionClient:
    """Session-bound wrapper for tools that operate on a workspace."""

    def __init__(self, client: "MCPClient", session_id: str, *, auto_dispose: bool = False):
        self._client = client
        self.session_id = session_id
        self._auto_dispose = auto_dispose

    def __enter__(self) -> "BoundSessionClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._auto_dispose:
            self.dispose()

    def dispose(self) -> dict[str, Any]:
        """Dispose the bound session."""
        return self._client.sessions.dispose(self.session_id)

    def get_tool_schema(self, tool_name: str, refresh: bool = False) -> dict[str, Any]:
        return self._client.get_tool_schema(tool_name, refresh=refresh)

    def list_tools(self, refresh: bool = False) -> list[str]:
        return self._client.list_tools(refresh=refresh)

    def tool_call(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        tool = self._client.get_tool_schema(tool_name)
        if tool.get("requires_session") and "session_id" not in kwargs:
            kwargs = {"session_id": self.session_id, **kwargs}
        return self._client.tool_call(tool_name, **kwargs)


class MCPClient:
    """Main client for interacting with the CircuitNotion MCP Server."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int | float | None = None,
        verify_ssl: bool = True,
    ):
        """Initialize MCP client.

        Args:
            api_key: API key for authentication. If not provided, uses MCP_API_KEY env var.
            base_url: Base URL of MCP server. If not provided, uses MCP_BASE_URL env var.
            timeout: Request timeout in seconds (default: 120).
            verify_ssl: Whether to verify SSL certificates (default: True).

        Raises:
            MCPAuthError: If no API key is provided.
        """
        self.api_key = api_key or os.getenv("MCP_API_KEY")
        if not self.api_key:
            raise MCPAuthError("API key not provided. Set MCP_API_KEY env var or pass api_key parameter.")

        resolved_base_url = base_url or os.getenv("MCP_BASE_URL") or "https://mcp.circuitnotion.com"
        self.base_url = resolved_base_url.rstrip("/")
        default_timeout = float(os.getenv("MCP_HTTP_TIMEOUT_SECONDS", "120"))
        self.timeout = float(timeout) if timeout is not None else default_timeout
        self._terminal_timeout_buffer_seconds = float(
            os.getenv("MCP_TERMINAL_HTTP_TIMEOUT_BUFFER_SECONDS", "30")
        )
        self.verify_ssl = verify_ssl

        # Create HTTP client with default headers
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"X-API-Key": self.api_key},
            timeout=self.timeout,
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
        self._tools_cache: dict[str, dict[str, Any]] = {}

    def __enter__(self) -> "MCPClient":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client connection."""
        self._client.close()

    def bind_session(self, session_id: str) -> BoundSessionClient:
        """Bind an existing session to a helper that auto-injects ``session_id``."""
        return BoundSessionClient(self, session_id)

    def session(self) -> BoundSessionClient:
        """Create and return a disposable bound session helper."""
        session_id = self.sessions.create()["session_id"]
        return BoundSessionClient(self, session_id, auto_dispose=True)

    def get_tools(self, refresh: bool = False) -> list[dict[str, Any]]:
        """Fetch tool metadata from the server.

        Args:
            refresh: When True, bypass the local tool cache.

        Returns:
            Tool metadata objects from ``GET /mcp/tools``.
        """
        if not refresh and self._tools_cache:
            return list(self._tools_cache.values())

        data = self._request("GET", "/mcp/tools")
        tools_raw = data.get("tools", [])
        if not isinstance(tools_raw, list):
            raise MCPError("Invalid tools response from server")
        tools = cast(list[dict[str, Any]], tools_raw)
        self._tools_cache = {tool["name"]: tool for tool in tools if "name" in tool}
        return tools

    def list_tools(self, refresh: bool = False) -> list[str]:
        """List tool names exposed by the server."""
        return [tool["name"] for tool in self.get_tools(refresh=refresh)]

    def get_tool_schema(self, tool_name: str, refresh: bool = False) -> dict[str, Any]:
        """Return one tool schema from the server."""
        if not refresh and tool_name in self._tools_cache:
            return self._tools_cache[tool_name]

        tool = self._request("GET", f"/mcp/tools/{tool_name}")
        self._tools_cache[tool_name] = tool
        return tool

    def tool_call(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        """Call a tool by name using the server's published tool contract.

        Args:
            tool_name: Tool name (e.g., "web_search", "device_list", "terminal_exec")
            **kwargs: Arguments to pass to the tool method

        Returns:
            Result from the tool method

        Raises:
            MCPError: If tool not found or call fails
        """
        tool = self.get_tool_schema(tool_name)
        endpoint = tool.get("endpoint")
        if not endpoint or " " not in endpoint:
            raise MCPError(f"Tool {tool_name!r} is missing a valid endpoint declaration")

        method, path = endpoint.split(" ", 1)
        path_only = path.split("?", 1)[0]
        path_params = set()

        while "{" in path_only and "}" in path_only:
            start = path_only.index("{")
            end = path_only.index("}", start)
            key = path_only[start + 1:end]
            if key not in kwargs:
                raise MCPError(f"Missing required path parameter: {key}")
            path_params.add(key)
            path_only = path_only[:start] + str(kwargs[key]) + path_only[end + 1:]

        remaining = {k: v for k, v in kwargs.items() if k not in path_params}
        self._validate_tool_arguments(tool_name, tool, remaining, path_params)
        request_timeout = self._request_timeout_for_tool(tool_name, tool, remaining)

        if method == "GET":
            return self._request("GET", path_only, params=remaining, timeout=request_timeout)
        if method == "DELETE":
            return self._request("DELETE", path_only, params=remaining, timeout=request_timeout)
        if method == "POST":
            return self._request("POST", path_only, json=remaining, timeout=request_timeout)

        raise MCPError(f"Unsupported tool HTTP method: {method}")

    def _request_timeout_for_tool(
        self,
        tool_name: str,
        tool_schema: dict[str, Any],
        arguments: dict[str, Any],
    ) -> float:
        timeout_seconds = self.timeout

        if tool_name == "terminal_exec":
            timeout_minutes = arguments.get("timeout_minutes")
            if not isinstance(timeout_minutes, int):
                input_schema = tool_schema.get("input_schema", {})
                properties = input_schema.get("properties", {}) if isinstance(input_schema, dict) else {}
                timeout_spec = properties.get("timeout_minutes", {}) if isinstance(properties, dict) else {}
                timeout_minutes = timeout_spec.get("default") if isinstance(timeout_spec, dict) else None
            if not isinstance(timeout_minutes, int):
                timeout_minutes = 60

            terminal_timeout = (timeout_minutes * 60) + self._terminal_timeout_buffer_seconds
            timeout_seconds = max(timeout_seconds, float(terminal_timeout))

        elif tool_name == "file_zip_session":
            timeout_seconds = max(timeout_seconds, 300.0)

        return timeout_seconds

    def _validate_tool_arguments(
        self,
        tool_name: str,
        tool: dict[str, Any],
        arguments: dict[str, Any],
        path_params: set[str],
    ) -> None:
        schema = tool.get("input_schema")
        if not isinstance(schema, dict):
            return

        properties = schema.get("properties", {})
        required = schema.get("required", [])
        missing = [name for name in required if name not in arguments and name not in path_params]
        if missing:
            raise MCPError(f"Tool {tool_name!r} is missing required arguments: {', '.join(missing)}")

        if not isinstance(properties, dict):
            return

        for name, value in arguments.items():
            spec = properties.get(name)
            if not isinstance(spec, dict):
                continue

            schema_type = spec.get("type")
            if isinstance(schema_type, str) and not _matches_schema_type(value, schema_type):
                raise MCPError(
                    f"Tool {tool_name!r} argument {name!r} must be of type {schema_type}"
                )

            enum_values = spec.get("enum")
            if isinstance(enum_values, list) and value not in enum_values:
                allowed = ", ".join(map(str, enum_values))
                raise MCPError(
                    f"Tool {tool_name!r} argument {name!r} must be one of: {allowed}"
                )

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
        **kwargs: Any,
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

            content_type = resp.headers.get("content-type", "").lower()
            if "application/json" in content_type:
                data = resp.json()
                if not isinstance(data, dict):
                    raise MCPError("Expected JSON object response")
                return cast(dict[str, Any], data)

            return {
                "content": resp.content,
                "content_type": content_type,
            }

        except httpx.HTTPError as e:
            raise MCPError(f"Request failed: {e}") from e


__all__ = [
    "MCPClient",
    "BoundSessionClient",
]
