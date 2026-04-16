"""Terminal command execution example."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    session = client.sessions.create()
    workspace = client.bind_session(session["session_id"])
    print(f"Session: {workspace.session_id}\n")

    print("Executing 'ls -la'...")
    result = workspace.tool_call("terminal_exec", cmd="ls -la")
    print(f"Exit code: {result['exit_code']}")
    print(f"Stdout:\n{result['stdout']}")
    if result["stderr"]:
        print(f"Stderr:\n{result['stderr']}")
    print()

    print("Executing 'echo hello'...")
    result = client.terminal.execute(
        session_id=workspace.session_id,
        command="echo hello",
        timeout_minutes=2,
    )
    print(f"Exit code: {result['exit_code']}")
    print(f"Output: {result['output']}\n")

    print("Using dynamic tool_call for pwd...")
    result = workspace.tool_call("terminal_exec", cmd="pwd")
    print(f"✓ {result['stdout'].strip()}\n")

    workspace.dispose()

finally:
    client.close()
