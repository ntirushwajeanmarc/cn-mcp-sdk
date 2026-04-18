"""Minimal file creation example."""

import base64
from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    client.set_default_session(session_id)

    file_resp = client.tool_call(
        "file_write",
        path="hello.txt",
        content_base64=base64.b64encode(b"Hello from cn-mcp SDK!\n").decode("utf-8"),
    )
    print("Response:", file_resp)
    print(f"✓ File written: {file_resp['file_id']}")
    print(f"✓ Download URL: {file_resp['download_url']}")

finally:
    if "session_id" in locals():
        client.tool_call("session_dispose", session_id=session_id)
        client.clear_default_session()
    client.close()
