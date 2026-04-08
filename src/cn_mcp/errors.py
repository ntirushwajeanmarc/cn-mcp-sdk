"""CircuitNotion MCP SDK - Error classes."""


class MCPError(Exception):
    """Base exception for MCP SDK errors."""

    pass


class MCPAuthError(MCPError):
    """Raised when authentication fails."""

    pass


class MCPNotFoundError(MCPError):
    """Raised when a requested resource is not found."""

    pass


__all__ = [
    "MCPError",
    "MCPAuthError",
    "MCPNotFoundError",
]
