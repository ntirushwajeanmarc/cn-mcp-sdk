"""Terminal command execution example."""

from cn_mcp import MCPClient

client = MCPClient(api_key="93622f50-6ab5-4d30-967e-1248e1a373e6")

try:
    # List available tools
    print("Available tools:")
    tools = client.list_tools()
    print(f"  {tools}\n")

    # Create a session
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    print(f"Session: {session_id}\n")

    # Execute a simple command
    print("Executing 'ls -la'...")
    result = client.tool_call(
        "terminal_exec",
        session_id=session_id,
        command="ls -la",
    )
    print(f"Exit code: {result['exit_code']}")
    print(f"Output:\n{result['output']}\n")

    # Execute with timeout
    print("Executing 'echo hello'...")
    result = client.tool_call(
        "terminal_exec",
        session_id=session_id,
        command="echo hello",
        timeout_minutes=2,
    )
    print(f"Exit code: {result['exit_code']}")
    print(f"Output: {result['output']}\n")

    # Dynamic tool calling
    print("Using tool_call for terminal command...")
    result = client.tool_call("terminal_exec", session_id=session_id, command="pwd")
    print(f"✓ tool_call result: {result['output'].strip()}\n")

    client.tool_call("session_dispose", session_id=session_id)

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
