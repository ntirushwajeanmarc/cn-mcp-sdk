from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest

SDK_SRC = Path(__file__).resolve().parents[1] / "src"
if str(SDK_SRC) not in sys.path:
    sys.path.insert(0, str(SDK_SRC))

from cn_mcp import MCPAuthError, MCPClient, MCPNotFoundError  # noqa: E402


def _client_with_transport(transport: httpx.MockTransport) -> MCPClient:
    client = MCPClient(api_key="test-key", base_url="https://mcp.example.com")
    client._client = httpx.Client(
        base_url=client.base_url,
        headers={"X-API-Key": client.api_key},
        transport=transport,
    )
    client.auth._client = client._client
    client.sessions._client = client._client
    client.files._client = client._client
    return client


def test_module_sessions_raises_auth_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/sessions"
        return httpx.Response(401, text="invalid token")

    client = _client_with_transport(httpx.MockTransport(handler))
    with pytest.raises(MCPAuthError):
        client.sessions.list()


def test_module_files_download_raises_not_found() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/files/download/missing"
        return httpx.Response(404, text="missing")

    client = _client_with_transport(httpx.MockTransport(handler))
    with pytest.raises(MCPNotFoundError):
        client.files.download("missing")


def test_auth_logout_handles_204() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/auth/logout"
        return httpx.Response(204)

    client = _client_with_transport(httpx.MockTransport(handler))
    client.auth.logout()
