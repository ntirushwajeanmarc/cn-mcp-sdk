"""Web search example."""

from cn_mcp import MCPClient

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

try:
    # Creating a session is optional for search
    session = client.sessions.create()
    session_id = session["session_id"]
    print(f"Session: {session_id}\n")

    # Basic search query
    print("Searching: 'Python asyncio tutorial'")
    results = client.search.web(query="Python asyncio tutorial")
    print(f"Found {len(results)} results\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Domain: {result.get('domain', 'N/A')}")
        print()

    # Search with location
    print("\nSearching: 'best restaurants' in San Francisco")
    results = client.search.web(
        query="best restaurants",
        location="San Francisco",
        num_results=5,
    )
    print(f"Found {len(results)} results\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        if "description" in result:
            print(f"   Description: {result['description'][:100]}...")
        print()

    # Search with specific result count
    print("\nSearching: 'FastAPI documentation' (top 3 results)")
    results = client.search.web(
        query="FastAPI documentation",
        num_results=3,
    )

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}\n")

    # Store search results in a file
    print("Storing search results in session file...")
    import json
    results = client.search.web(query="PostgreSQL async drivers")
    
    client.files.write(
        session_id=session_id,
        path="/output/search_results.json",
        content=json.dumps(results, indent=2),
    )
    print("✓ Results saved to search_results.json")

    client.sessions.dispose(session_id)

finally:
    client.close()
