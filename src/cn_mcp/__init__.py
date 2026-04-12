"""CircuitNotion MCP SDK - Python SDK for the MCP Server."""

__version__ = "0.3.0"

from .client import BoundSessionClient, MCPClient
from .errors import MCPAuthError, MCPError, MCPNotFoundError

__all__ = [
    "MCPClient",
    "BoundSessionClient",
    "MCPError",
    "MCPAuthError",
    "MCPNotFoundError",
]
