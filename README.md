# CircuitNotion MCP SDK

Python SDK for the CircuitNotion MCP server.

## Installation

```bash
pip install cn-mcp
```

For local development against a local MCP server:

```bash
export MCP_API_KEY="your-api-key"
export MCP_BASE_URL="http://localhost:8000"
```

## Quick Start (`tool_call` only)

```python
from cn_mcp import MCPClient

mcp = MCPClient(api_key="your-api-key")

session = mcp.tool_call("session_create")
session_id = session["session_id"]

try:
    run = mcp.tool_call(
        "terminal_exec",
        session_id=session_id,
        cmd="echo hello",
        timeout_minutes=60,
    )
    print(run["stdout"])

    zipped = mcp.tool_call("file_zip_session", session_id=session_id)
    print(zipped["download_url"])
finally:
    mcp.tool_call("session_dispose", session_id=session_id)
    mcp.close()
```

## Tool-Call Examples

### Files

```python
import base64

payload = base64.b64encode(b"hello").decode("utf-8")
written = mcp.tool_call(
    "file_write",
    session_id=session_id,
    path="reports/out.txt",
    content_base64=payload,
)
files = mcp.tool_call("file_list", session_id=session_id)
binary = mcp.tool_call("file_download", file_id=written["file_id"])
mcp.tool_call("file_delete", file_id=written["file_id"])
```

### Devices

```python
devices = mcp.tool_call("device_list")
result = mcp.tool_call("device_set_state", device_name="living room light", state="off")
```

### Search

```python
results = mcp.tool_call("web_search", query="CircuitNotion")
print(results.get("organic_results", []))
```

### Scheduler

```python
task = mcp.tool_call("time_schedule", payload={"message": "follow up"}, in_seconds=300)
tasks = mcp.tool_call("time_scheduled_tasks")
mcp.tool_call("time_cancel", task_id=task["task_id"])
```

### Database

```python
rows = mcp.tool_call(
    "db_query",
    session_id=session_id,
    sql="SELECT name FROM sqlite_master WHERE type = ?",
    params=["table"],
)

mcp.tool_call(
    "db_execute",
    session_id=session_id,
    sql="INSERT INTO notes (body) VALUES (?)",
    params=["hello"],
)
```

## Timeout Note

The SDK defaults to an agent-friendly HTTP timeout and automatically extends
timeout behavior for long-running tools such as `terminal_exec`.
