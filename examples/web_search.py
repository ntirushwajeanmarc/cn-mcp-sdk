"""Web search example with advanced features."""

from cn_mcp import MCPClient
import json

client = MCPClient(api_key="your-api-key")

try:
    # List available tools
    print("Available tools:")
    tools = client.list_tools()
    print(f"  {tools}\n")

    # Basic search
    print("Searching: 'Python asyncio tutorial'")
    results = client.tool_call("web_search", query="Python asyncio tutorial")

    # Handle both dict and list responses
    if isinstance(results, dict):
        print(f"Found {len(results.get('organic_results', []))} results\n")
        for i, result in enumerate(results.get('organic_results', [])[:3], 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   {result.get('link', 'N/A')}")
            if result.get('snippet'):
                print(f"   {result['snippet'][:100]}...")
            print()
    else:
        print(f"Found {len(results)} results\n")
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   {result.get('link', 'N/A')}\n")

    # Dynamic tool calling
    print("Using tool_call for web search...")
    results = client.tool_call("web_search", query="Python best practices")
    if isinstance(results, dict):
        result_list = results.get('organic_results', [])
    else:
        result_list = results
    print(f"✓ tool_call found {len(result_list)} results\n")

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
