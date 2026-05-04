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

## Quick Start (`agent_call`)

```python
from cn_mcp import MCPClient

mcp = MCPClient(api_key="your-api-key")

session = mcp.agent_call("session_create")
session_id = session["session_id"]

try:
    run = mcp.agent_call(
        "terminal_exec",
        session_id=session_id,
        cmd="echo hello",
        timeout_minutes=60,
    )
    print(run["stdout"])

    zipped = mcp.agent_call("file_zip_session", session_id=session_id)
    print(zipped["download_url"])
finally:
    mcp.agent_call("session_dispose", session_id=session_id)
    mcp.close()
```

For one-off workspace operations, the server can create the session for you:

```python
run = mcp.agent_call(
    "terminal_exec",
    {"cmd": "python --version", "timeout_minutes": 2},
    auto_create_session=True,
)
```

## Tool-Call Examples

### Files

```python
import base64

payload = base64.b64encode(b"hello").decode("utf-8")
written = mcp.agent_call(
    "file_write",
    session_id=session_id,
    path="reports/out.txt",
    content_base64=payload,
)
files = mcp.agent_call("file_list", session_id=session_id)
mcp.agent_call("file_delete", file_id=written["file_id"])
```

`file_list` also discovers normal files created by terminal commands and
returns direct links for them.

Return `download_url` directly to users. It is a plain browser/download link
and remains usable after session cleanup.

### Devices

```python
devices = mcp.agent_call("device_list")
result = mcp.agent_call("device_set_state", device_name="living room light", state="off")
```

### Search

```python
results = mcp.agent_call("web_search", query="CircuitNotion")
print(results.get("organic_results", []))
```

### Scheduler

```python
task = mcp.agent_call("time_schedule", payload={"message": "follow up"}, in_seconds=300)
tasks = mcp.agent_call("time_scheduled_tasks")
mcp.agent_call("time_cancel", task_id=task["task_id"])
```

### Database

```python
rows = mcp.agent_call(
    "db_query",
    session_id=session_id,
    sql="SELECT name FROM sqlite_master WHERE type = ?",
    params=["table"],
)

mcp.agent_call(
    "db_execute",
    session_id=session_id,
    sql="INSERT INTO notes (body) VALUES (?)",
    params=["hello"],
)
```

## Timeout Note

The SDK defaults to an agent-friendly HTTP timeout and automatically extends
timeout behavior for long-running tools such as `terminal_exec`.
