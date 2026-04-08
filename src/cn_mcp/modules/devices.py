"""Devices module."""

from __future__ import annotations

from typing import Any

import httpx


class DevicesClient:
    """Client for device control operations."""

    def __init__(self, client: httpx.Client):
        """Initialize devices client.

        Args:
            client: HTTP client instance
        """
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        """List available devices.

        Returns:
            List of device objects
        """
        resp = self._client.get("/devices/list")
        return resp.json()

    def set_state(
        self,
        device_id: str,
        action: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute an action on a device (turn on/off, set state, etc.).

        Args:
            device_id: Device ID
            action: Action to execute (e.g., 'turn_on', 'turn_off')
            parameters: Optional action parameters

        Returns:
            Device action result
        """
        resp = self._client.post(
            "/devices/set_state",
            json={
                "device_id": device_id,
                "action": action,
                "parameters": parameters or {},
            },
        )
        return resp.json()


__all__ = ["DevicesClient"]
