"""Basic usage example."""

from cn_mcp import MCPClient

# Initialize client with API key (uses https://mcp.circuitnotion.com by default)
client = MCPClient(api_key="your-api-key")

try:
    # List available tools
    print("Available tools:")
    tools = client.list_tools()
    for tool in tools:
        print(f"  - {tool}")

    # Create a session
    print("\nCreating session...")
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    print(f"✓ Session created: {session_id}")

    # Write a file
    print("\nWriting file...")
    file_resp = client.tool_call(
        "file_write",
        session_id=session_id,
        path="/output/hello.txt",
        content="Hello, World!",
    )
    print(f"✓ File written: {file_resp['file_id']}")

    # List files
    print("\nListing files...")
    files = client.tool_call("file_list", session_id=session_id)
    for f in files:
        print(f"  - {f['path']} ({f['bytes']} bytes)")

    # Download file
    print("\nDownloading file...")
    content = client.tool_call("file_download", file_id=file_resp["file_id"])
    print(f"✓ Downloaded: {content}")

    # Get cache stats
    print("\nCache stats:")
    stats = client.tool_call("cache_stats")
    print(f"  Size: {stats['size']}/{stats['max_size']}")
    print(f"  TTL: {stats['ttl_seconds']}s")

    # List sessions
    print("\nActive sessions:")
    sessions = client.tool_call("session_list")
    for s in sessions:
        print(f"  - {s['session_id']} (status: {s['status']})")

    # Dynamic tool calling example
    print("\nDynamic tool calling:")
    result = client.tool_call("file_list", session_id=session_id)
    print(f"✓ Called tool_call('file_list'): {len(result)} files found")

    # Dispose session
    print("\nDisposing session...")
    client.tool_call("session_dispose", session_id=session_id)
    print("✓ Session disposed")

finally:
    client.close()
