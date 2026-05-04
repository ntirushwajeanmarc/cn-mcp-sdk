from cn_mcp import MCPClient
import os
from dotenv import load_dotenv

load_dotenv()

mcp = MCPClient(
    api_key=os.getenv("MCP_API_KEY")
)
tools = mcp.list_tools()
print(tools)
session = mcp.tool_call("session_create")
session_id = session["session_id"]
mcp.set_default_session(session_id)


