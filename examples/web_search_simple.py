"""Simple web search example."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    print("Searching for current weather in Kigali...\n")
    results = client.tool_call("web_search", query="current weather in Kigali")

    for index, result in enumerate(results.get("organic_results", [])[:5], 1):
        print(f"{index}. {result.get('title', 'N/A')}")
        print(f"   {result.get('link', 'N/A')}\n")

finally:
    client.close()
