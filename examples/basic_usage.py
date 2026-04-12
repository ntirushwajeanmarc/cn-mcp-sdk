"""Basic usage example for the current cn-mcp SDK."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    print("Available tools:")
    for tool_name in client.list_tools():
        print(f"  - {tool_name}")

    print("\nCreating session...")
    session = client.sessions.create()
    session_id = session["session_id"]
    workspace = client.bind_session(session_id)
    print(f"✓ Session created: {session_id}")

    print("\nWriting file...")
    file_resp = workspace.tool_call(
        "file_write",
        path="output/hello.txt",
        content_base64="SGVsbG8sIFdvcmxkIQ==",
    )
    print(f"✓ File written: {file_resp['file_id']}")
    print(f"  Download URL: {file_resp['download_url']}")

    print("\nListing files...")
    files = workspace.tool_call("file_list")
    for file_info in files:
        print(f"  - {file_info['path']} ({file_info['bytes']} bytes)")

    print("\nDownloading file...")
    downloaded = client.tool_call("file_download", file_id=file_resp["file_id"])
    print(f"✓ Downloaded content type: {downloaded['content_type']}")

    print("\nCache stats:")
    stats = client.auth.cache_stats()
    print(f"  Size: {stats['size']}/{stats['max_size']}")
    print(f"  TTL: {stats['ttl_seconds']}s")

    print("\nDisposing session...")
    workspace.dispose()
    print("✓ Session disposed")

finally:
    client.close()
