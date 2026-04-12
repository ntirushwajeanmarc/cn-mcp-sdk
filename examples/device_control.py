"""Device control example for the current device contract."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    print("Available devices:")
    devices = client.devices.list()
    for device in devices:
        print(f"  - {device['name']}")
        print(f"    Type: {device['type']}")
        print(f"    State: {device['state']}")

    if devices:
        target_name = devices[0]["name"]
        print(f"\nTurning on {target_name}...")
        result = client.devices.set_state(device_name=target_name, state="on")
        print(f"✓ Updated: {result}")

        print(f"\nTurning off {target_name} via dynamic tool call...")
        result = client.tool_call("device_set_state", device_name=target_name, state="off")
        print(f"✓ Updated: {result}")

finally:
    client.close()
