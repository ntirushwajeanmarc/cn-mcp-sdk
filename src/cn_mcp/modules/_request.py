"""Shared request helpers for module clients."""

from __future__ import annotations

from typing import Any, cast

import httpx

from ..errors import MCPAuthError, MCPError, MCPNotFoundError


def request_json(client: httpx.Client, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
    """Issue a request and return JSON payload with consistent SDK errors."""
    resp = _request(client, method, endpoint, **kwargs)
    if resp.status_code == 204:
        return {}
    data = resp.json()
    if not isinstance(data, dict):
        raise MCPError("Expected JSON object response")
    return cast(dict[str, Any], data)


def request_list(client: httpx.Client, method: str, endpoint: str, **kwargs: Any) -> list[dict[str, Any]]:
    """Issue a request and return a JSON list with consistent SDK errors."""
    resp = _request(client, method, endpoint, **kwargs)
    if resp.status_code == 204:
        return []
    data = resp.json()
    if not isinstance(data, list):
        raise MCPError("Expected JSON list response")
    return cast(list[dict[str, Any]], data)


def request_bytes(client: httpx.Client, method: str, endpoint: str, **kwargs: Any) -> bytes:
    """Issue a request and return raw response bytes with consistent SDK errors."""
    resp = _request(client, method, endpoint, **kwargs)
    return resp.content


def _request(client: httpx.Client, method: str, endpoint: str, **kwargs: Any) -> httpx.Response:
    url = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    try:
        resp = client.request(method, url, **kwargs)
        if resp.status_code in (401, 403):
            raise MCPAuthError(f"Authentication failed: {resp.text}")
        if resp.status_code == 404:
            raise MCPNotFoundError(f"Resource not found: {resp.text}")
        if resp.status_code >= 400:
            raise MCPError(f"API error ({resp.status_code}): {resp.text}")
        return resp
    except httpx.HTTPError as exc:
        raise MCPError(f"Request failed: {exc}") from exc
