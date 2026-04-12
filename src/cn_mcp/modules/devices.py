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
        device_name: str,
        state: str,
    ) -> dict[str, Any]:
        """Set a device on or off by its friendly name.

        Args:
            device_name: Friendly device name (for example ``kitchen``)
            state: Desired state (``on`` or ``off``)

        Returns:
            Device action result
        """
        resp = self._client.post(
            "/devices/set_state",
            json={
                "device_name": device_name,
                "state": state,
            },
        )
        return resp.json()


__all__ = ["DevicesClient"]
