    
from cn_mcp import MCPClient

client = MCPClient(api_key="")
session = client.tool_call("session_create")
session_id = session["session_id"]
print(f"✓ Session created: {session_id}\n")
file_resp = client.tool_call(
        "file_write",
        session_id=session_id,
        path="hello.txt",
        content="Hello from cn-mcp SDK!"
    )
print("Response:", file_resp)
if "file_id" in file_resp:
    print(f"✓ File written: {file_resp['file_id']}\n")
    base_url = "https://mcp.circuitnotion.com"
    full_url = base_url.rstrip("/") + file_resp["download_url"]
    print(f"Download URL: {full_url}")
else:
    print("Error: 'file_id' not found in response. Full response above.")