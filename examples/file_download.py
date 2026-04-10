"""Example: Download a file using the MCP SDK."""

from cn_mcp import MCPClient

# Replace with your actual API key
API_KEY = "your-api-key-here"

client = MCPClient(api_key="")

try:
    # 1. List sessions
    sessions = client.tool_call("session_list")
    if not sessions:
        print("No sessions found. Please create a session and upload files first.")
        exit(1)
    session_id = sessions[0]["session_id"]
    print(f"Using session: {session_id}")

    # 2. List files in the session
    files = client.tool_call("file_list", session_id=session_id)
    if not files:
        print("No files found in the session.")
        exit(1)
    file_info = files[0]
    file_id = file_info["file_id"]
    file_name = file_info.get("name", "downloaded_file")
    print(f"Downloading file: {file_name} (ID: {file_id})")

    # 3. Download the file
    result = client.tool_call("file_download", file_id=file_id)
    content = result.get("content")
    if content is None:
        print("Failed to download file content.")
        exit(1)

    # 4. Save to disk
    with open(file_name, "wb") as f:
        if isinstance(content, str):
            f.write(content.encode())
        else:
            f.write(content)
    print(f"File saved as: {file_name}")

except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
