"""Scheduled tasks example."""

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

    # List scheduled jobs
    print("Scheduled jobs:")
    jobs = client.tool_call("scheduler_list")
    print(f"  Found {len(jobs)} jobs\n")

    # Create a scheduled job
    print("Creating scheduled job...")
    job = client.tool_call(
        "scheduler_create",
        schedule="0 * * * *",
        command="echo 'hourly task'",
        session_id="session-123",
    )
    print(f"✓ Job created: {job.get('job_id')}\n")

    # Dynamic tool calling
    print("Using tool_call to list jobs...")
    jobs = client.tool_call("scheduler_list")
    print(f"✓ Found {len(jobs)} jobs via tool_call\n")

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
