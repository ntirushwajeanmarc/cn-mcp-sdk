"""Quick start example for cn-mcp."""

import base64
from cn_mcp import MCPClient


client = MCPClient(api_key="fcc1c0f2-f024-4983-998e-71e16bcdcc5c")

try:
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    print(f"\nSession: {session_id}")

    devices = client.tool_call("device_list")
    print(f"\nDevices found: {len(devices)}")
    for device in devices[:3]:
        print(f"  - {device['name']} ({device['type']}, {device['state']})")

    content = base64.b64encode(b"Hello from cn-mcp SDK!").decode("utf-8")
    file_resp = client.tool_call(
        "file_write",
        session_id=session_id,
        path="output/hello.txt",
        content_base64=content,
    )
    print(f"\nFile written: {file_resp['file_id']}")
    print(f"Download URL: {file_resp['download_url']}")

    result = client.tool_call("terminal_exec", session_id=session_id, cmd="pwd")
    print(f"\nCurrent workspace:\n{result['stdout'].strip()}")

    client.tool_call("session_dispose", session_id=session_id)
    print("\nDone")

finally:
    client.close()
