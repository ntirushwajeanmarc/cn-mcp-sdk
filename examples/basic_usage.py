"""Basic usage example for the current cn-mcp SDK."""

import base64
from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

try:
    print("\nCreating session...")
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    client.set_default_session(session_id)
    print(f"✓ Session created: {session_id}")

    print("\nWriting file...")
    file_resp = client.tool_call(
        "file_write",
        path="output/hello.txt",
        content_base64=base64.b64encode(b"Hello, World!").decode("utf-8"),
    )
    print(f"✓ File written: {file_resp['file_id']}")
    print(f"  Download URL: {file_resp['download_url']}")

    print("\nListing files...")
    files = client.tool_call("file_list")
    for file_info in files:
        print(f"  - {file_info['path']} ({file_info['bytes']} bytes)")

    print("\nDownloading file...")
    downloaded = client.tool_call("file_download", file_id=file_resp["file_id"])
    print(f"✓ Downloaded content type: {downloaded['content_type']}")

    print("\nDisposing session...")
    client.tool_call("session_dispose", session_id=session_id)
    client.clear_default_session()
    print("✓ Session disposed")

finally:
    client.close()
