# Quick Start Guide

## Installation

```bash
pip install cn-mcp
```

## Basic Setup

```python
from cn_mcp import MCPClient

client = MCPClient(api_key="your-api-key")
```

## Create a Session Workspace

```python
session = client.sessions.create()
workspace = client.bind_session(session["session_id"])
print(workspace.session_id)
```

Or use automatic cleanup:

```python
with client.session() as workspace:
    print(workspace.session_id)
```

## Discover the Live Tool Contract

```python
for tool in client.get_tools():
    print(tool["name"], tool["endpoint"], tool.get("requires_session"))
```

## Execute Commands

```python
result = workspace.tool_call("terminal_exec", cmd="ls -la")
print(result["stdout"])
```

## Manage Files

```python
file_resp = workspace.tool_call(
    "file_write",
    path="output/data.txt",
    content_base64="SGVsbG8=",
)

print(file_resp["download_url"])

files = workspace.tool_call("file_list")
binary = client.tool_call("file_download", file_id=file_resp["file_id"])
```

## Devices

```python
devices = client.devices.list()
if devices:
    client.devices.set_state(device_name=devices[0]["name"], state="on")
```

## Database

```python
client.db.execute(
    session_id=workspace.session_id,
    # db.execute supports INSERT/UPDATE/DELETE statements.
    # This example assumes a `notes` table already exists.
    sql="INSERT INTO notes (body) VALUES (?)",
    params=["hello"],
)

rows = client.db.query(
    session_id=workspace.session_id,
    sql="SELECT * FROM notes",
)
```

## Scheduler

```python
task = client.scheduler.schedule(payload={"action": "backup"}, in_seconds=60)
print(task["task_id"])
```

## Cleanup

```python
workspace.dispose()
client.close()
```
