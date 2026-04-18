from cn_mcp import MCPClient
import os
from dotenv import load_dotenv

load_dotenv()

mcp = MCPClient(
    api_key=os.getenv("MCP_API_KEY")
)

session = mcp.tool_call("session_create")
session_id = session["session_id"]
mcp.set_default_session(session_id)

try:
    result = mcp.tool_call("web_search", query="latest python release")
    print(result)

    command = mcp.tool_call("terminal_exec", cmd="ls -la")
    print(command)
finally:
    mcp.tool_call("session_dispose", session_id=session_id)
    mcp.clear_default_session()
    mcp.close()