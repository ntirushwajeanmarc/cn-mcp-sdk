"""Device control example."""

from cn_mcp import MCPClient
import json

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

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

    # Get status of a specific device
    if devices:
        device_id = devices[0]["device_id"]
        print(f"Getting status of {device_id}...")
        status = client.devices.get_status(device_id)
        print(f"  Status: {status['status']}")
        print(f"  Last updated: {status['last_updated']}")
        print(f"  Metrics: {json.dumps(status.get('metrics', {}), indent=2)}\n")

        # Execute an action on a device
        print(f"Turning on {device_id}...")
        result = client.devices.execute(
            device_id=device_id,
            action="turn_on",
            parameters={"mode": "auto"},
        )
        print(f"✓ Action executed: {result['action']}")
        print(f"  Previous state: {result.get('previous_state')}")
        print(f"  New state: {result.get('new_state')}\n")

        # Execute another action
        print(f"Setting brightness on {device_id}...")
        result2 = client.devices.execute(
            device_id=device_id,
            action="set_brightness",
            parameters={"level": 75},
        )
        print(f"✓ Action executed: {result2['action']}")
        print(f"  Parameters: {json.dumps(result2.get('parameters', {}), indent=2)}\n")

        # Get updated status
        print(f"Updated status of {device_id}...")
        updated_status = client.devices.get_status(device_id)
        print(f"  Status: {updated_status['status']}")
        print(f"  Brightness: {updated_status.get('metrics', {}).get('brightness')}%")

    client.sessions.dispose(session_id)

finally:
    client.close()
