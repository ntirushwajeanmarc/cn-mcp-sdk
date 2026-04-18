"""Scheduled task example using the current scheduler API."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    print("Existing scheduled tasks:")
    tasks = client.tool_call("time_scheduled_tasks")
    print(f"  Found {len(tasks)} task(s)")

    print("\nCreating a scheduled task...")
    task = client.tool_call(
        "time_schedule",
        payload={"action": "send_reminder", "message": "Check build status"},
        in_seconds=300,
    )
    print(f"✓ Task created: {task['task_id']}")
    print(f"  Run at: {task['run_at']}")

    print("\nListing via tool_call...")
    tasks = client.tool_call("time_scheduled_tasks")
    print(f"✓ Found {len(tasks)} task(s)")

    print("\nCancelling the task...")
    cancelled = client.tool_call("time_cancel", task_id=task["task_id"])
    print(f"✓ Cancelled: {cancelled['status']}")

finally:
    client.close()
