"""Error handling example."""

from cn_mcp import MCPClient, MCPAuthError, MCPNotFoundError, MCPError

# Example 1: Authentication errors
print("=" * 60)
print("EXAMPLE 1: Authentication Errors")
print("=" * 60)

client = MCPClient(api_key="invalid-key")

try:
    sessions = client.tool_call("session_list")
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
    content = client.tool_call("file_download", file_id="non-existent-file-id")
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
    client.tool_call("session_dispose", session_id="non-existent-session-123")
except MCPNotFoundError as e:
    print(f"✗ Session not found: {e}")
except MCPError as e:
    print(f"✗ API error: {e}\n")

finally:
    client.close()

# Example 4: Connection errors
print("=" * 60)
print("EXAMPLE 4: Connection Errors")
print("=" * 60)

client = MCPClient(
    api_key="your-api-key",
    base_url="http://localhost:9999",
)

try:
    session = client.sessions.create()
except Exception as e:
    print(f"✗ Connection failed: {type(e).__name__}")
    print(f"  {e}\n")

finally:
    client.close()

# Example 5: Error handling with tool_call
print("=" * 60)
print("EXAMPLE 5: Error Handling with tool_call")
print("=" * 60)

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

try:
    # Invalid tool name
    result = client.tool_call("non_existent_tool", arg="value")
except MCPError as e:
    print(f"✗ Tool call error: {e}\n")

finally:
    client.close()

# Example 6: Proper error handling pattern
print("=" * 60)
print("EXAMPLE 6: Recommended Error Handling Pattern")
print("=" * 60)

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")

try:
    print("Creating session...")
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    print(f"✓ Session created: {session_id}\n")

    print("Writing file...")
    file_resp = client.tool_call(
        "file_write",
        session_id=session_id,
        path="/output/example.txt",
        content="Example content",
    )
    print(f"✓ File written: {file_resp['file_id']}\n")

    print("Disposing session...")
    client.tool_call("session_dispose", session_id=session_id)
    print("✓ Session disposed\n")

except MCPAuthError as e:
    print(f"✗ Authentication Error: {e}")
    print("  → Check your API key")

except MCPNotFoundError as e:
    print(f"✗ Resource Not Found: {e}")
    print("  → Verify session ID exists")

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
