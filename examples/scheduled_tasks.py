"""Scheduled tasks example."""

from datetime import datetime, timedelta
from cn_mcp import MCPClient
import json

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

try:
    # Create a session
    session = client.sessions.create()
    session_id = session["session_id"]
    print(f"Session: {session_id}\n")

    # Schedule a task to run in 30 seconds
    print("Scheduling task to run in 30 seconds...")
    payload = {
        "action": "send_notification",
        "message": "This is a scheduled notification",
        "user_id": "user123",
    }
    
    task = client.scheduler.schedule(
        payload=payload,
        in_seconds=30,
        session_id=session_id,
    )
    task_id = task["task_id"]
    print(f"✓ Task scheduled: {task_id}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    print(f"  Scheduled for: {task['run_at']}\n")

    # Schedule a task for a specific datetime
    print("Scheduling task for 5 minutes from now...")
    future_time = datetime.utcnow() + timedelta(minutes=5)
    
    payload2 = {
        "action": "generate_report",
        "report_type": "daily",
        "format": "pdf",
    }
    
    task2 = client.scheduler.schedule(
        payload=payload2,
        run_at=future_time.isoformat(),
        session_id=session_id,
    )
    task_id2 = task2["task_id"]
    print(f"✓ Task scheduled: {task_id2}")
    print(f"  Run at: {task2['run_at']}\n")

    # List all scheduled tasks
    print("Active scheduled tasks:")
    tasks = client.scheduler.list()
    for t in tasks:
        print(f"  - {t['task_id']}")
        print(f"    Status: {t['status']}")
        print(f"    Run at: {t['run_at']}")
        print(f"    Payload: {json.dumps(t['payload'])}")
        print()

    # Cancel a specific task
    print(f"Canceling task {task_id}...")
    cancelled = client.scheduler.cancel(task_id)
    print(f"✓ Task cancelled: {cancelled['status']}\n")

    # Filter and display just the re
    print("Updated scheduled tasks:")
    remaining_tasks = client.scheduler.list()
    print(f"Total: {len(remaining_tasks)} remaining")
    for t in remaining_tasks:
        print(f"  - {t['task_id']} ({t['status']})")

    client.sessions.dispose(session_id)

finally:
    client.close()
