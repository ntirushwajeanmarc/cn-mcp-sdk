"""Terminal command execution example."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    print(f"Session: {session_id}\n")

    print("Executing 'ls -la'...")
    result = client.tool_call("terminal_exec", session_id=session_id, cmd="ls -la")
    print(f"Exit code: {result['exit_code']}")
    print(f"Stdout:\n{result['stdout']}")
    if result["stderr"]:
        print(f"Stderr:\n{result['stderr']}")
    print()

    print("Executing 'echo hello'...")
    result = client.tool_call(
        "terminal_exec",
        session_id=session_id,
        cmd="echo hello",
        timeout_minutes=2,
    )
    print(f"Exit code: {result['exit_code']}")
    print(f"Output: {result['stdout']}{result['stderr']}\n")

    print("Executing pwd...")
    result = client.tool_call("terminal_exec", session_id=session_id, cmd="pwd")
    print(f"✓ {result['stdout'].strip()}\n")

    client.tool_call("session_dispose", session_id=session_id)

finally:
    client.close()
