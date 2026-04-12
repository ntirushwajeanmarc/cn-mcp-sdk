# CircuitNotion MCP SDK

Python SDK for the CircuitNotion MCP server.

## Installation

```bash
pip install cn-mcp
```

## Quick Start

```python
from cn_mcp import MCPClient

client = MCPClient(api_key="your-api-key")

session = client.sessions.create()
workspace = client.bind_session(session["session_id"])

file_resp = client.files.write(
    session_id=session["session_id"],
    path="output/hello.txt",
    content="Hello, World!",
)
print(file_resp["download_url"])

result = workspace.tool_call("terminal_exec", cmd="echo hello")
print(result["stdout"])

devices = client.devices.list()
print(devices)

client.sessions.dispose(session["session_id"])
```

For agentic workflows, `bind_session()` keeps session-backed tools aligned with
the published MCP metadata without manually injecting `session_id`.

## Dynamic Tool Calling

The SDK now reads the live tool contract from the server, so `list_tools()` and
`tool_call()` stay aligned with the deployed MCP.

```python
from cn_mcp import MCPClient

client = MCPClient(api_key="your-api-key")

print(client.list_tools())

result = client.tool_call("device_set_state", device_name="kitchen", state="on")
print(result)
```

Use `get_tools()` or `get_tool_schema("tool_name")` if you want the full
published metadata from `/mcp/tools`.

## Main APIs

### Sessions

```python
session = client.sessions.create()
sessions = client.sessions.list()
client.sessions.dispose(session["session_id"])
```

### Files

```python
file_resp = client.files.write(session["session_id"], "reports/out.zip", b"zip bytes")
files = client.files.list(session["session_id"])
content = client.files.download(file_resp["file_id"])
client.files.delete(file_resp["file_id"])
```

`download_url` values returned by the server are concrete absolute URLs when the
server knows its public base URL from the request.

### Terminal

```python
result = client.terminal.execute(
    session_id=session["session_id"],
    command="python --version",
    timeout_minutes=5,
    output_limit_kb=1024,
)
```

### Search

```python
results = client.search.web("CircuitNotion")
print(results["organic_results"])
```

### Devices

```python
devices = client.devices.list()
result = client.devices.set_state(device_name="living room light", state="off")
```

### Scheduler

```python
task = client.scheduler.schedule(payload={"message": "follow up"}, in_seconds=300)
tasks = client.scheduler.list()
client.scheduler.cancel(task["task_id"])
```

### Database

```python
rows = client.db.query(
    session_id=session["session_id"],
    sql="SELECT name FROM sqlite_master WHERE type = ?",
    params=["table"],
)

client.db.execute(
    session_id=session["session_id"],
    sql="CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, body TEXT)",
)
```
