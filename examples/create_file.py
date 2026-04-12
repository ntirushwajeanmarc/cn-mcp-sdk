"""Minimal file creation example."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    with client.session() as workspace:
        file_resp = workspace.tool_call(
            "file_write",
            path="hello.txt",
            content_base64="SGVsbG8gZnJvbSBjbi1tY3AgU0RLISAK",
        )
        print("Response:", file_resp)
        print(f"✓ File written: {file_resp['file_id']}")
        print(f"✓ Download URL: {file_resp['download_url']}")

finally:
    client.close()
