"""Device control example."""

from cn_mcp import MCPClient
import json

# Initialize client (uses https://mcp.circuitnotion.com by default)
client = MCPClient(api_key="your-api-key")

try:
    # Create a session
    session = client.sessions.create()
    session_id = session["session_id"]
    print(f"Session: {session_id}\n")

    # List available devices
    print("Available devices:")
    devices = client.devices.list()
    for device in devices:
        print(f"  - {device['device_id']}")
        print(f"    Type: {device['type']}")
        print(f"    Status: {device['status']}")
        print(f"    Location: {device.get('location', 'N/A')}")
        print()

    # Set state on a specific device
    if devices:
        device_id = devices[0]["device_id"]
        print(f"Turning on {device_id}...")
        result = client.devices.set_state(
            device_id=device_id,
            action="turn_on",
            parameters={"mode": "auto"},
        )
        print(f"✓ Action executed: {result['action']}")
        print(f"  Response: {json.dumps(result, indent=2)}\n")

        # Execute another action
        print(f"Setting brightness on {device_id}...")
        result2 = client.devices.set_state(
            device_id=device_id,
            action="set_brightness",
            parameters={"level": 75},
        )
        print(f"✓ Action executed: {result2['action']}")
        print(f"  Response: {json.dumps(result2, indent=2)}\n")

    client.sessions.dispose(session_id)

finally:
    client.close()
