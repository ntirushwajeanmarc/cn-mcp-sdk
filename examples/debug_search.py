"""Debug web search response structure."""

import json

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    print("Available tools:")
    print(client.list_tools())
    print("\nTesting web search response structure...\n")

    direct = client.search.web(query="Python tutorial")
    print("Direct method type:", type(direct))
    print(json.dumps(direct, indent=2, default=str)[:600])

    print("\nUsing tool_call...\n")
    dynamic = client.tool_call("web_search", query="Python tutorial")
    print("tool_call type:", type(dynamic))
    print(json.dumps(dynamic, indent=2, default=str)[:600])

finally:
    client.close()
