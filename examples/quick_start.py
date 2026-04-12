"""Quick start example for cn-mcp."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    print("Available tools:")
    print(client.list_tools())

    session = client.sessions.create()
    workspace = client.bind_session(session["session_id"])
    print(f"\nSession: {workspace.session_id}")

    devices = client.devices.list()
    print(f"\nDevices found: {len(devices)}")
    for device in devices[:3]:
        print(f"  - {device['name']} ({device['type']}, {device['state']})")

    file_resp = client.files.write(
        session_id=workspace.session_id,
        path="output/hello.txt",
        content="Hello from cn-mcp SDK!",
    )
    print(f"\nFile written: {file_resp['file_id']}")
    print(f"Download URL: {file_resp['download_url']}")

    result = workspace.tool_call("terminal_exec", cmd="pwd")
    print(f"\nCurrent workspace:\n{result['output'].strip()}")

    workspace.dispose()
    print("\nDone")

finally:
    client.close()
