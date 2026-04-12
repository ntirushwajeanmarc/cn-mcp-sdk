"""Dynamic tool usage example driven by the live MCP tool catalog."""

import json

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    print("=" * 50)
    print("AVAILABLE TOOLS")
    print("=" * 50)
    for tool in client.get_tools():
        print(f"- {tool['name']}")
        print(f"  endpoint: {tool['endpoint']}")
        print(f"  requires_session: {tool.get('requires_session', False)}")

    print("\n" + "=" * 50)
    print("EXAMPLE 1: direct dynamic calls")
    print("=" * 50)

    result = client.tool_call("web_search", query="Python programming")
    print(f"Search results: {len(result.get('organic_results', []))}")

    session = client.sessions.create()
    workspace = client.bind_session(session["session_id"])

    ai_responses = [
        '{"tool": "file_write", "arguments": {"path": "notes/todo.txt", "content_base64": "SGVsbG8="}}',
        '{"tool": "file_list", "arguments": {}}',
        '{"tool": "terminal_exec", "arguments": {"cmd": "find . -maxdepth 2 -type f"}}',
    ]

    print("\n" + "=" * 50)
    print("EXAMPLE 2: simulated agent responses")
    print("=" * 50)

    for raw in ai_responses:
        response = json.loads(raw)
        print(f"\nExecuting {response['tool']} with {response['arguments']}")
        result = workspace.tool_call(response["tool"], **response["arguments"])
        print(json.dumps(result, indent=2, default=str)[:400])

    workspace.dispose()

finally:
    client.close()
