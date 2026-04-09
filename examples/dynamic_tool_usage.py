"""
Dynamic Tool Calling Example

This example shows how to use tool_call() and list_tools() for AI agent integration.

Usage:
    python dynamic_tool_usage.py
"""

import json
from cn_mcp import MCPClient

client = MCPClient(api_key="your-api-key")

try:
    # List all available tools
    print("=" * 50)
    print("AVAILABLE TOOLS")
    print("=" * 50)
    tools = client.list_tools()
    for tool in tools:
        print(f"  - {tool}")

    # Example 1: Direct tool calling
    print("\n" + "=" * 50)
    print("EXAMPLE 1: Direct tool_call() usage")
    print("=" * 50)

    print("\n1. List devices:")
    result = client.tool_call("device_list")
    print(f"   Found {len(result)} device(s)")

    print("\n2. Web search:")
    result = client.tool_call("web_search", query="Python programming")
    print(f"   Found {len(result)} results")

    # Example 2: AI Agent integration
    print("\n" + "=" * 50)
    print("EXAMPLE 2: AI Agent Integration")
    print("=" * 50)

    # This simulates an AI response
    ai_responses = [
        '{"tool": "session_create", "arguments": {}}',
        '{"tool": "file_write", "arguments": {"session_id": "SESSION_ID", "path": "/test.txt", "content": "Hello"}}',
        '{"tool": "file_list", "arguments": {"session_id": "SESSION_ID"}}',
    ]

    # Create a session first for file operations
    session = client.sessions.create()
    session_id = session["session_id"]

    for ai_response in ai_responses:
        response_data = json.loads(ai_response)
        tool_name = response_data["tool"]
        args = response_data["arguments"]

        # Replace placeholder with actual session_id
        if "SESSION_ID" in str(args):
            args = {k: session_id if v == "SESSION_ID" else v for k, v in args.items()}

        print(f"\nExecuting: {tool_name}")
        print(f"  Arguments: {args}")

        result = client.tool_call(tool_name, **args)
        print(f"  Result: {type(result).__name__}")

    # Clean up
    client.sessions.dispose(session_id)

    # Example 3: Building a prompt for AI agents
    print("\n" + "=" * 50)
    print("EXAMPLE 3: AI Prompt Template")
    print("=" * 50)

    prompt = f"""
You are an AI assistant with access to tools.

If a tool is needed, respond ONLY in JSON:

{{
  "tool": "tool_name",
  "arguments": {{}}
}}

Available tools: {client.list_tools()}
"""

    print(prompt)

    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
