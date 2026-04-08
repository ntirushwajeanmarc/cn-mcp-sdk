"""Debug web search response structure."""

from cn_mcp import MCPClient
import json

client = MCPClient(api_key="your-api-key")

try:
    print("Testing web search API response structure...\n")
    response = client.search.web(query="Python tutorial")
    
    print("Response type:", type(response))
    print("Response content:")
    print(json.dumps(response, indent=2, default=str)[:500])

finally:
    client.close()
