"""Terminal command execution example."""

from cn_mcp import MCPClient

# Initialize client (uses https://mcp.circuitnotion.com by default)
client = MCPClient(api_key="93622f50-6ab5-4d30-967e-1248e1a373e6")

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
