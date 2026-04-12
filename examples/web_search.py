"""Web search example with the current normalized response shape."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    print("Available tools:")
    print(client.list_tools())

    print("\nSearching: Python asyncio tutorial")
    results = client.tool_call("web_search", query="Python asyncio tutorial")
    organic = results.get("organic_results", [])
    print(f"Found {len(organic)} result(s)\n")

    for index, result in enumerate(organic[:3], 1):
        print(f"{index}. {result.get('title', 'N/A')}")
        print(f"   {result.get('link', 'N/A')}")
        if result.get("snippet"):
            print(f"   {result['snippet'][:120]}...")
        print()

    if results.get("ai_summary"):
        print("AI summary:")
        print(results["ai_summary"][:300])

finally:
    client.close()
