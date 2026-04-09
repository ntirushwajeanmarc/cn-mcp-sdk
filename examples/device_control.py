"""Device control example."""

from cn_mcp import MCPClient
import json

client = MCPClient(api_key="your-api-key")

try:
    # List available tools
    print("Available tools:")
    tools = client.list_tools()
    for tool in tools:
        print(f"  - {tool}")
    print()

    # List available devices
    print("Available devices:")
    devices = client.tool_call("device_list")
    for device in devices:
        print(f"  - {device.get('name', 'Unknown')} ({device.get('device_id', 'N/A')})")
        print(f"    Type: {device.get('type', 'unknown')}")
        print(f"    Status: {device.get('status', 'unknown')}")
    print()

    # Set state on a specific device
    if devices:
        device_id = devices[0].get("device_id")
        print(f"Turning on {device_id}...")
        result = client.tool_call(
            "device_set_state",
            device_id=device_id,
            action="turn_on",
            parameters={"mode": "auto"},
        )
        print(f"✓ Action executed: {result}\n")

    # Dynamic tool calling
    print("Using tool_call for device control...")
    result = client.tool_call("device_set_state", device_id=device_id, action="turn_off")
    print(f"✓ Device turned off via tool_call\n")

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
