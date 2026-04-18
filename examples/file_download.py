"""Example: write a file, then download it through the SDK."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    client.set_default_session(session_id)

    file_resp = client.tool_call(
        "file_write",
        path="output/report.txt",
        content_base64="UmVwb3J0IGNvbnRlbnQ=",
    )
    print(f"File written: {file_resp['file_id']}")
    print(f"Download URL: {file_resp['download_url']}")

    result = client.tool_call("file_download", file_id=file_resp["file_id"])
    content = result.get("content", b"")
    with open("downloaded_report.txt", "wb") as handle:
        handle.write(content if isinstance(content, bytes) else content.encode())
    print("Saved as downloaded_report.txt")

finally:
    if "session_id" in locals():
        client.tool_call("session_dispose", session_id=session_id)
        client.clear_default_session()
    client.close()
