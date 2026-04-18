"""Dynamic tool usage example driven by the live MCP tool catalog."""

import json
import base64

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    print("=" * 50)
    print("AVAILABLE TOOLS")
    print("=" * 50)
    tools = [
        "terminal_exec",
        "file_write",
        "file_list",
        "file_zip_session",
        "file_download",
        "file_delete",
        "db_query",
        "db_execute",
        "session_create",
        "session_list",
        "session_dispose",
        "device_list",
        "device_set_state",
        "web_search",
        "time_schedule",
        "time_scheduled_tasks",
        "time_cancel",
    ]
    for tool in tools:
        print(f"- {tool}")

    print("\n" + "=" * 50)
    print("EXAMPLE 1: direct dynamic calls")
    print("=" * 50)

    result = client.tool_call("web_search", query="Python programming")
    print(f"Search results: {len(result.get('organic_results', []))}")

    session = client.tool_call("session_create")
    session_id = session["session_id"]
    client.set_default_session(session_id)

    ai_responses = [
        json.dumps(
            {
                "tool": "file_write",
                "arguments": {
                    "path": "notes/todo.txt",
                    "content_base64": base64.b64encode(b"Hello").decode("utf-8"),
                },
            }
        ),
        '{"tool": "file_list", "arguments": {}}',
        '{"tool": "terminal_exec", "arguments": {"cmd": "ls -la"}}',
    ]

    print("\n" + "=" * 50)
    print("EXAMPLE 2: simulated agent responses")
    print("=" * 50)

    for raw in ai_responses:
        response = json.loads(raw)
        print(f"\nExecuting {response['tool']} with {response['arguments']}")
        result = client.tool_call(response["tool"], **response["arguments"])
        print(json.dumps(result, indent=2, default=str)[:400])

    client.tool_call("session_dispose", session_id=session_id)
    client.clear_default_session()

finally:
    client.close()
