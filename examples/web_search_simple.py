"""
Simple Web Search Example

This is the easiest way to use the web search feature.
"""

from cn_mcp import MCPClient

# Initialize client
client = MCPClient(api_key="93622f50-6ab5-4d30-967e-1248e1a373e6")

try:
    # Simple search
    print("Searching for 'Python tutorial'...\n")
    results = client.tool_call("web_search", query="what is the current weather in kigali?")

    # Handle response (could be dict or list)
    if isinstance(results, dict):
        # Dict response with organic_results
        for i, result in enumerate(results.get('organic_results', [])[:5], 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   {result.get('link', 'N/A')}\n")
    else:
        # List response
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   {result.get('link', 'N/A')}\n")

finally:
    client.close()
