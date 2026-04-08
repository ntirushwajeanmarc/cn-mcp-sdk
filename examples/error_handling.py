"""Error handling example."""

from cn_mcp import MCPClient, MCPAuthError, MCPNotFoundError, MCPError

# Example 1: Authentication errors
print("=" * 60)
print("EXAMPLE 1: Authentication Errors")
print("=" * 60)

client = MCPClient(api_key="invalid-key", base_url="http://localhost:8000")

try:
    sessions = client.sessions.list()
except MCPAuthError as e:
    print(f"✗ Authentication failed: {e}")
    print(f"  Status code: {e.status_code}")
    print(f"  Response: {e.response}\n")
except MCPError as e:
    print(f"✗ API error: {e}")

finally:
    client.close()

# Example 2: Not found errors
print("=" * 60)
print("EXAMPLE 2: Not Found Errors")
print("=" * 60)

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

try:
    # Try to download a file that doesn't exist
    content = client.files.download_text("non-existent-file-id")
except MCPNotFoundError as e:
    print(f"✗ Resource not found: {e}")
    print(f"  Status code: {e.status_code}")
except MCPError as e:
    print(f"✗ API error: {e}\n")

finally:
    client.close()

# Example 3: General API errors
print("=" * 60)
print("EXAMPLE 3: General API Errors")
print("=" * 60)

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

try:
    # Try to dispose a non-existent session
    client.sessions.dispose("non-existent-session-123")
except MCPNotFoundError as e:
    print(f"✗ Session not found: {e}")
except MCPError as e:
    print(f"✗ API error: {e}\n")

finally:
    client.close()

# Example 4: Connection errors (base URL unreachable)
print("=" * 60)
print("EXAMPLE 4: Connection Errors")
print("=" * 60)

client = MCPClient(
    api_key="your-api-key",
    base_url="http://localhost:9999",  # Wrong port
)

try:
    session = client.sessions.create()
except Exception as e:
    print(f"✗ Connection failed: {type(e).__name__}")
    print(f"  {e}\n")

finally:
    client.close()

# Example 5: Proper error handling pattern
print("=" * 60)
print("EXAMPLE 5: Recommended Error Handling Pattern")
print("=" * 60)

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

try:
    # Create a session
    print("Creating session...")
    session = client.sessions.create()
    session_id = session["session_id"]
    print(f"✓ Session created: {session_id}\n")

    print("Writing file...")
    file_resp = client.files.write(
        session_id=session_id,
        path="/output/example.txt",
        content="Example content",
    )
    print(f"✓ File written: {file_resp['file_id']}\n")

    print("Downloading file...")
    content = client.files.download_text(file_resp["file_id"])
    print(f"✓ Downloaded: {content}\n")

    print("Disposing session...")
    client.sessions.dispose(session_id)
    print("✓ Session disposed\n")

except MCPAuthError as e:
    print(f"✗ Authentication Error: {e}")
    print("  → Check your API key")
    print("  → Verify the API key hasn't expired")

except MCPNotFoundError as e:
    print(f"✗ Resource Not Found: {e}")
    print("  → Verify session ID exists")
    print("  → Verify file ID exists")

except MCPError as e:
    print(f"✗ API Error: {e}")
    print("  → Check server logs for details")

except Exception as e:
    print(f"✗ Unexpected Error: {e}")
    print(f"  Type: {type(e).__name__}")

finally:
    client.close()

print("\n" + "=" * 60)
print("Error handling examples completed")
print("=" * 60)
