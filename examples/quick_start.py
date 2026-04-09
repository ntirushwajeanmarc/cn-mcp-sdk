"""
Quick Start Example for cn-mcp SDK

Installation:
    pip install cn-mcp

Usage:
    python quick_start.py
"""

from cn_mcp import MCPClient

# Initialize the client with your API key
# Default server: https://mcp.circuitnotion.com
client = MCPClient(api_key="")

try:
    # List available tools
    print("Available tools:")
    tools = client.list_tools()
    print(f"  {tools}\n")

    # Create a session
    print("Creating session...")
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    print(f"✓ Session created: {session_id}\n")

    # List available devices
    print("Fetching devices...")
    devices = client.tool_call("device_list")
    print(f"✓ Found {len(devices)} device(s)")

    if devices:
        for device in devices[:3]:  # Show first 3
            print(f"  - {device.get('name', 'Unknown')}: {device.get('type', 'unknown')}")
    print()

    # Write a file to the session
    print("Writing file...")
    file_resp = client.tool_call(
        "file_write",
        session_id=session_id,
        path="/output/hello.txt",
        content="Hello from cn-mcp SDK!"
    )
    print(f"✓ File written: {file_resp['file_id']}\n")

    # List files in session using dynamic tool calling
    print("Session files (using tool_call):")
    files = client.tool_call("file_list", session_id=session_id)
    for f in files:
        print(f"  - {f['path']} ({f['bytes']} bytes)")
    print()

    # Clean up
    print("Disposing session...")
    client.tool_call("session_dispose", session_id=session_id)
    print("✓ Done!")

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
