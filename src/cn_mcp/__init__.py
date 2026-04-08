"""CircuitNotion MCP SDK - Python SDK for the MCP Server."""

__version__ = "0.1.0"

from .client import MCPClient
from .errors import MCPAuthError, MCPError, MCPNotFoundError

__all__ = [
    "MCPClient",
    "MCPError",
    "MCPAuthError",
    "MCPNotFoundError",
]
