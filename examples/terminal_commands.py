"""Terminal command execution example."""

from cn_mcp import MCPClient

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

try:
    # Create a session
    session = client.sessions.create()
    session_id = session["session_id"]
    print(f"Session: {session_id}\n")

    # Execute a simple command
    print("Executing 'ls -la'...")
    result = client.terminal.execute(
        command="ls -la",
        session_id=session_id,
    )
    print(f"Return code: {result['exit_code']}")
    print(f"Output:\n{result['output']}\n")

    # Execute with timeout
    print("Executing 'curl https://api.github.com' with 2 minute timeout...")
    result = client.terminal.execute(
        command="curl https://api.github.com",
        session_id=session_id,
        timeout_minutes=2,
    )
    print(f"Return code: {result['exit_code']}")
    print(f"Output (first 500 chars):\n{result['output'][:500]}\n")

    # Get terminal stats
    print("Terminal stats:")
    stats = client.terminal.get_stats(session_id)
    print(f"  Active sessions: {stats['active_sessions']}")
    print(f"  Total commands: {stats['total_commands']}")
    print(f"  Uptime: {stats['uptime_seconds']}s")

    # Execute with output limit
    print("\nExecuting 'find /' with 100KB output limit...")
    result = client.terminal.execute(
        command="find /",
        session_id=session_id,
        output_limit_kb=100,
    )
    print(f"Return code: {result['exit_code']}")
    print(f"Output size (truncated): {len(result['output'])} chars")

    client.sessions.dispose(session_id)

finally:
    client.close()
