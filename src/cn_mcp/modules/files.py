"""Files module."""

from __future__ import annotations

import base64
from typing import Any

import httpx


class FilesClient:
    """Client for file operations."""

    def __init__(self, client: httpx.Client):
        """Initialize files client.

        Args:
            client: HTTP client instance
        """
        self._client = client
        # Store base_url for constructing full download URLs
        self._base_url = str(client.base_url).rstrip("/")

    def write(
        self,
        session_id: str,
        path: str,
        content: str | bytes,
    ) -> dict[str, Any]:
        """Write a file to a session.

        Args:
            session_id: Session ID
            path: File path relative to session root
            content: File content (str or bytes)

        Returns:
            File metadata with file_id, path, bytes, download_url (fully qualified)
        """
        if isinstance(content, str):
            content = content.encode("utf-8")

        content_b64 = base64.b64encode(content).decode("utf-8")

        resp = self._client.post(
            "/files/write",
            json={
                "session_id": session_id,
                "path": path,
                "content_base64": content_b64,
            },
        )
        result = resp.json()
        # Patch download_url to be fully qualified
        if "download_url" in result:
            result["download_url"] = self._base_url + result["download_url"]
        return result

    def list(self, session_id: str) -> list[dict[str, Any]]:
        """List files in a session.

        Args:
            session_id: Session ID

        Returns:
            List of file metadata
        """
        resp = self._client.get("/files/list", params={"session_id": session_id})
        return resp.json()

    def download(self, file_id: str) -> bytes:
        """Download a file by ID.

        Args:
            file_id: File ID

        Returns:
            File content as bytes
        """
        resp = self._client.get(f"/files/download/{file_id}")
        return resp.content

    def download_text(self, file_id: str, encoding: str = "utf-8") -> str:
        """Download a file as text.

        Args:
            file_id: File ID
            encoding: Text encoding (default: utf-8)

        Returns:
            File content as string
        """
        return self.download(file_id).decode(encoding)

    def delete(self, file_id: str) -> None:
        """Delete a file.

        Args:
            file_id: File ID to delete
        """
        self._client.delete(f"/files/{file_id}")


__all__ = ["FilesClient"]
