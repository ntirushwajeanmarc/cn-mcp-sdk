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

    def execute(
        self,
        device_id: str,
        action: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute an action on a device.

        Args:
            device_id: Device ID
            action: Action to execute (e.g., 'turn_on', 'turn_off')
            parameters: Optional action parameters

        Returns:
            Device action result
        """
        resp = self._client.post(
            f"/devices/{device_id}/execute",
            json={
                "action": action,
                "parameters": parameters or {},
            },
        )
        return resp.json()

    def list(self) -> list[dict[str, Any]]:
        """List available devices.

        Returns:
            List of device objects
        """
        resp = self._client.get("/devices")
        return resp.json()

    def get_status(self, device_id: str) -> dict[str, Any]:
        """Get current device status.

        Args:
            device_id: Device ID

        Returns:
            Device status information
        """
        resp = self._client.get(f"/devices/{device_id}/status")
        return resp.json()


__all__ = ["DevicesClient"]
