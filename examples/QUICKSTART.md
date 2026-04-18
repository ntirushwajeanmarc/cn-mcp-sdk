# Quick Start Guide

## Installation

```bash
pip install cn-mcp
```

## Basic Setup

```python
from cn_mcp import MCPClient

mcp = MCPClient(api_key="your-api-key")
```

## Create and Bind a Default Session

```python
session = mcp.tool_call("session_create")
session_id = session["session_id"]
mcp.set_default_session(session_id)
```

## Execute Commands

```python
result = mcp.tool_call("terminal_exec", cmd="ls -la")
print(result["stdout"])
```

## Manage Files

```python
file_resp = mcp.tool_call(
    "file_write",
    path="output/data.txt",
    content_base64="SGVsbG8=",
)

print(file_resp["download_url"])

files = mcp.tool_call("file_list")
binary = mcp.tool_call("file_download", file_id=file_resp["file_id"])
```

## Devices

```python
devices = mcp.tool_call("device_list")
if devices:
    mcp.tool_call("device_set_state", device_name=devices[0]["name"], state="on")
```

## Database

```python
mcp.tool_call(
    "db_execute",
    # db.execute supports INSERT/UPDATE/DELETE statements.
    # This example assumes a `notes` table already exists.
    sql="INSERT INTO notes (body) VALUES (?)",
    params=["hello"],
)

rows = mcp.tool_call("db_query", sql="SELECT * FROM notes")
```

## Scheduler

```python
task = mcp.tool_call("time_schedule", payload={"action": "backup"}, in_seconds=60)
print(task["task_id"])
```

## Cleanup

```python
mcp.tool_call("session_dispose", session_id=session_id)
mcp.clear_default_session()
mcp.close()
```
