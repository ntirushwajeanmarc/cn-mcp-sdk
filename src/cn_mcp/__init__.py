"""CircuitNotion MCP SDK - Python SDK for the MCP Server."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cn-mcp")
except PackageNotFoundError:
    __version__ = "0.3.1"

from .client import BoundSessionClient, MCPClient
from .errors import MCPAuthError, MCPError, MCPNotFoundError

__all__ = [
    "MCPClient",
    "BoundSessionClient",
    "MCPError",
    "MCPAuthError",
    "MCPNotFoundError",
]
