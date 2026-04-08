"""Advanced usage patterns example."""

from cn_mcp import MCPClient
from pathlib import Path
import json
from datetime import datetime, timedelta

print("=" * 60)
print("EXAMPLE 1: Using Context Manager")
print("=" * 60)

# Context manager ensures proper cleanup
with MCPClient(api_key="your-api-key") as client:
    print("Client initialized with context manager")
    session = client.sessions.create()
    print(f"Session created: {session['session_id']}")
    # Client automatically closes when exiting the with block
print("Client closed automatically\n")

# Example 2: Batching operations with environment variables
print("=" * 60)
print("EXAMPLE 2: Using Environment Variables")
print("=" * 60)

# Set these environment variables before running:
# export MCP_API_KEY=your-api-key
# export MCP_BASE_URL=https://mcp.circuitnotion.com
# export MCP_TIMEOUT=30
# export MCP_VERIFY_SSL=true

# Client will automatically pick up these settings
client = MCPClient()

try:
    print("Client initialized from environment variables")
    session = client.sessions.create()
    print(f"Session: {session['session_id']}\n")
finally:
    client.close()

# Example 3: Bulk file operations
print("=" * 60)
print("EXAMPLE 3: Bulk File Operations")
print("=" * 60)

client = MCPClient(api_key="your-api-key")

try:
    session = client.sessions.create()
    session_id = session["session_id"]

    # Write multiple files
    files_to_write = {
        "/output/config.json": json.dumps({"timeout": 30, "retries": 3}, indent=2),
        "/output/readme.txt": "This is a sample README file.",
        "/output/log.txt": "2024-01-01 10:00:00 - Application started\n2024-01-01 10:00:05 - Connected to database",
    }

    print(f"Writing {len(files_to_write)} files...")
    file_ids = {}
    for path, content in files_to_write.items():
        resp = client.files.write(session_id=session_id, path=path, content=content)
        file_ids[path] = resp["file_id"]
        print(f"  ✓ {path}")

    # List all files
    print("\nListing files in session...")
    files = client.files.list(session_id=session_id)
    total_bytes = sum(f["bytes"] for f in files)
    print(f"  Total files: {len(files)}")
    print(f"  Total size: {total_bytes} bytes")

    # Read specific files
    print("\nReading files:")
    for path, file_id in file_ids.items():
        content = client.files.download_text(file_id)
        print(f"\n  {path}:")
        for line in content.split("\n")[:2]:  # Show first 2 lines
            print(f"    {line}")

    client.sessions.dispose(session_id)

finally:
    client.close()

# Example 4: Chaining operations
print("\n" + "=" * 60)
print("EXAMPLE 4: Chaining Operations")
print("=" * 60)

client = MCPClient(api_key="your-api-key")

try:
    # Create session -> Execute commands -> Store results -> Dispose
    session = client.sessions.create()
    session_id = session["session_id"]
    print(f"Session: {session_id}")

    # Execute multiple commands and collect results
    print("\nExecuting command sequence...")
    commands = [
        ("echo 'Starting process'", "start"),
        ("ls -la", "list_files"),
        ("pwd", "current_dir"),
    ]

    results = {}
    for cmd, name in commands:
        result = client.terminal.execute(cmd, session_id=session_id)
        results[name] = {
            "command": cmd,
            "exit_code": result["exit_code"],
            "output": result["output"][:100],  # First 100 chars
        }
        print(f"  {name}: exit_code {result['exit_code']}")

    # Store results
    client.files.write(
        session_id=session_id,
        path="/output/command_results.json",
        content=json.dumps(results, indent=2),
    )
    print("  Results saved to file")

    # List what was stored
    files = client.files.list(session_id=session_id)
    print(f"\nSession contains {len(files)} file(s)")

    client.sessions.dispose(session_id)

finally:
    client.close()

# Example 5: Scheduling with payload organization
print("\n" + "=" * 60)
print("EXAMPLE 5: Advanced Task Scheduling")
print("=" * 60)

client = MCPClient(api_key="your-api-key")

try:
    session = client.sessions.create()
    session_id = session["session_id"]

    # Define a workflow with multiple scheduled tasks
    workflow = {
        "name": "Daily Report Generation",
        "tasks": [
            {
                "name": "Collect Data",
                "delay": 60,  # 1 minute
                "payload": {
                    "action": "collect_metrics",
                    "metrics": ["cpu", "memory", "disk"],
                },
            },
            {
                "name": "Process Data",
                "delay": 180,  # 3 minutes
                "payload": {
                    "action": "process_data",
                    "algorithm": "moving_average",
                    "window": 10,
                },
            },
            {
                "name": "Generate Report",
                "delay": 300,  # 5 minutes
                "payload": {
                    "action": "generate_report",
                    "format": "pdf",
                    "include_charts": True,
                },
            },
        ],
    }

    print(f"Scheduling workflow: {workflow['name']}")
    scheduled_tasks = []

    for task_def in workflow["tasks"]:
        task = client.scheduler.schedule(
            payload=task_def["payload"],
            in_seconds=task_def["delay"],
            session_id=session_id,
        )
        scheduled_tasks.append(task)
        print(f"  ✓ {task_def['name']} - Task ID: {task['task_id']}")

    # Save workflow metadata
    workflow_metadata = {
        "workflow": workflow,
        "scheduled_at": datetime.utcnow().isoformat(),
        "task_ids": [t["task_id"] for t in scheduled_tasks],
    }

    client.files.write(
        session_id=session_id,
        path="/output/workflow_metadata.json",
        content=json.dumps(workflow_metadata, indent=2),
    )
    print("  Workflow metadata saved")

    client.sessions.dispose(session_id)

finally:
    client.close()

print("\n" + "=" * 60)
print("Advanced examples completed")
print("=" * 60)
