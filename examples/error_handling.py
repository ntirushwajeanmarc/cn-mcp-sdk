"""Error handling examples for the current SDK exceptions."""

from cn_mcp import MCPAuthError, MCPClient, MCPError, MCPNotFoundError


print("=" * 60)
print("EXAMPLE 1: Authentication error")
print("=" * 60)

client = MCPClient(api_key="invalid-key", base_url="http://localhost:8000")
try:
    client.tool_call("session_list")
except MCPAuthError as exc:
    print(f"✗ Authentication failed: {exc}\n")
finally:
    client.close()

print("=" * 60)
print("EXAMPLE 2: Not found error")
print("=" * 60)

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")
try:
    client.tool_call("file_download", file_id="non-existent-file-id")
except MCPNotFoundError as exc:
    print(f"✗ Not found: {exc}\n")
finally:
    client.close()

print("=" * 60)
print("EXAMPLE 3: Validation / API errors")
print("=" * 60)

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")
try:
    client.tool_call("device_set_state", device_name="kitchen")
except MCPError as exc:
    print(f"✗ SDK/API error: {exc}\n")
finally:
    client.close()

print("=" * 60)
print("EXAMPLE 4: Recommended pattern")
print("=" * 60)

client = MCPClient(api_key="your-api-key", base_url="http://localhost:8000")
try:
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    print(f"✓ Session created: {session_id}")
    file_resp = client.tool_call(
        "file_write",
        session_id=session_id,
        path="output/example.txt",
        content_base64="RXhhbXBsZSBjb250ZW50",
    )
    print(f"✓ File written: {file_resp['file_id']}")
    client.tool_call("session_dispose", session_id=session_id)
except MCPAuthError as exc:
    print(f"✗ Authentication error: {exc}")
except MCPNotFoundError as exc:
    print(f"✗ Resource not found: {exc}")
except MCPError as exc:
    print(f"✗ API error: {exc}")
