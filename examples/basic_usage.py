"""Basic usage example."""

from cn_mcp import MCPClient

# Initialize client with API key
client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

try:
    # Create a session
    print("Creating session...")
    session = client.sessions.create()
    session_id = session["session_id"]
    print(f"✓ Session created: {session_id}")

    # Write a file
    print("\nWriting file...")
    file_resp = client.files.write(
        session_id=session_id,
        path="/output/hello.txt",
        content="Hello, World!",
    )
    print(f"✓ File written: {file_resp['file_id']}")

    # List files
    print("\nListing files...")
    files = client.files.list(session_id=session_id)
    for f in files:
        print(f"  - {f['path']} ({f['bytes']} bytes)")

    # Download file
    print("\nDownloading file...")
    content = client.files.download_text(file_resp["file_id"])
    print(f"✓ Downloaded: {content}")

    # Get cache stats
    print("\nCache stats:")
    stats = client.auth.cache_stats()
    print(f"  Size: {stats['size']}/{stats['max_size']}")
    print(f"  TTL: {stats['ttl_seconds']}s")

    # List sessions
    print("\nActive sessions:")
    sessions = client.sessions.list()
    for s in sessions:
        print(f"  - {s['session_id']} (status: {s['status']})")

    # Dispose session
    print("\nDisposing session...")
    client.sessions.dispose(session_id)
    print("✓ Session disposed")

finally:
    client.close()
