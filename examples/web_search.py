"""Web search example with advanced features."""

from cn_mcp import MCPClient
import json

client = MCPClient(api_key="your-api-key")

try:
    session = client.sessions.create()
    session_id = session["session_id"]
    print(f"Session: {session_id}\n")

    # Basic search
    print("Searching: 'Python asyncio tutorial'")
    results = client.search.web(query="Python asyncio tutorial")
    
    # Handle both dict and list responses
    if isinstance(results, dict):
        # Dict response (has organic_results, query, etc.)
        print(f"Found {len(results.get('organic_results', []))} results\n")
        for i, result in enumerate(results.get('organic_results', [])[:3], 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   {result.get('link', 'N/A')}")
            if result.get('snippet'):
                print(f"   {result['snippet'][:100]}...")
            print()
    else:
        # List response
        print(f"Found {len(results)} results\n")
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   {result.get('link', 'N/A')}\n")

    # Search with location
    print("\nSearching: 'best restaurants' in San Francisco")
    response = client.search.web(
        query="best restaurants",
        location="San Francisco",
        num_results=5,
    )
    
    if isinstance(response, dict):
        for i, result in enumerate(response.get('organic_results', [])[:3], 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   {result.get('link', 'N/A')}\n")
    else:
        for i, result in enumerate(response[:3], 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   {result.get('link', 'N/A')}\n")

    # Store results to file
    print("Storing search results in session file...")
    search_results = client.search.web(query="PostgreSQL async drivers")
    
    client.files.write(
        session_id=session_id,
        path="/output/search_results.json",
        content=json.dumps(search_results if isinstance(search_results, dict) else {"results": search_results}, indent=2),
    )
    print("✓ Results saved to search_results.json")

    client.sessions.dispose(session_id)

finally:
    client.close()
