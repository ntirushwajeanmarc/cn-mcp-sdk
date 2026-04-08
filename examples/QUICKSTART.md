# Quick Start Guide

## Installation

```bash
pip install cn-mcp
```

## Usage

### 1. Basic Setup
```python
from cn_mcp import MCPClient

# Create a client (uses https://mcp.circuitnotion.com by default)
client = MCPClient(api_key="your-api-key")
```

### 2. Create a Session
```python
session = client.sessions.create()
session_id = session["session_id"]
print(f"Session ID: {session_id}")
```

### 3. List Devices
```python
devices = client.devices.list(session_id=session_id)
for device in devices:
    print(f"{device['name']}: {device['type']}")
```

### 4. Execute Commands
```python
result = client.terminal.execute(
    cmd="ls -la",
    session_id=session_id
)
print(result["output"])
```

### 5. Manage Files
```python
# Write a file
client.files.write(
    session_id=session_id,
    path="/output/data.json",
    content='{"key": "value"}'
)

# Read a file
content = client.files.download_text(file_id)
print(content)

# List files
files = client.files.list(session_id=session_id)
```

### 6. Schedule Tasks
```python
task = client.scheduler.schedule(
    payload={"action": "backup"},
    in_seconds=60,
    session_id=session_id
)
print(f"Task scheduled: {task['task_id']}")
```

### 7. Close Session
```python
client.sessions.dispose(session_id)
client.close()
```

## Running the Examples

```bash
cd examples

# Quick start
python quick_start.py

# Basic usage
python basic_usage.py

# Device control
python device_control.py

# Advanced patterns
python advanced_patterns.py
```

## Configuration

**Environment Variables:**
```bash
export MCP_API_KEY=your-api-key
export MCP_BASE_URL=https://mcp.circuitnotion.com  # optional, default
export MCP_TIMEOUT=30                               # optional
export MCP_VERIFY_SSL=true                          # optional
```

**Or pass directly:**
```python
client = MCPClient(
    api_key="your-api-key",
    base_url="https://mcp.circuitnotion.com",
    timeout=30,
    verify_ssl=True
)
```

## Error Handling

```python
from cn_mcp import MCPClient, MCPAuthError, MCPNotFoundError, MCPError

try:
    client = MCPClient(api_key="invalid-key")
except MCPAuthError as e:
    print(f"Auth failed: {e}")
except MCPNotFoundError as e:
    print(f"Resource not found: {e}")
except MCPError as e:
    print(f"API error: {e}")
```

## Documentation

- [Full API Documentation](https://github.com/ntirushwajeanmarc/cn-mcp-sdk#readme)
- [PyPI Package](https://pypi.org/project/cn-mcp/)
