"""Debug web search response structure."""

from cn_mcp import MCPClient
import json

client = MCPClient(api_key="your-api-key")

try:
    # List available tools
    print("Available tools:")
    tools = client.list_tools()
    print(f"  {tools}\n")

    print("Testing web search API response structure...\n")

    # Using direct method
    response = client.search.web(query="Python tutorial")
    print("Direct method - Response type:", type(response))
    print("Response content:")
    print(json.dumps(response, indent=2, default=str)[:500])

    # Using tool_call
    print("\n\nUsing tool_call...\n")
    response = client.tool_call("web_search", query="Python tutorial")
    print("tool_call - Response type:", type(response))
    print("Response content:")
    print(json.dumps(response, indent=2, default=str)[:500])

finally:
    client.close()
