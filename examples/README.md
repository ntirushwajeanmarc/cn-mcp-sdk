# CN MCP SDK Examples

These examples reflect the current `cn-mcp` SDK and the live MCP tool contract.

## Highlights

- Use `client.get_tools()` when you need full tool metadata.
- Use `client.tool_call()` for dynamic agent-style execution.
- Use `client.bind_session(session_id)` or `with client.session() as workspace:` for workspace-backed tools.
- Use the typed modules like `client.files`, `client.devices`, `client.scheduler`, and `client.db` for developer-friendly direct calls.

## Examples

### `quick_start.py`
Small end-to-end example covering:
- tool discovery
- session creation
- file write
- device listing
- terminal execution

### `basic_usage.py`
Shows:
- dynamic tool calls
- session-bound helper usage
- file download URLs
- auth cache stats

### `dynamic_tool_usage.py`
Best starting point for agent builders:
- reads live tool metadata
- shows `requires_session`
- executes simulated agent tool calls through a bound session

### `terminal_commands.py`
Shows both:
- `workspace.tool_call("terminal_exec", ...)`
- `client.terminal.execute(...)`

### `database_queries.py`
Uses the current session-backed SQLite API:
- `client.db.execute(...)`
- `client.db.query(...)`

### `device_control.py`
Uses the current device contract:
- `client.devices.list()`
- `client.devices.set_state(device_name=..., state=...)`

### `scheduled_tasks.py`
Uses the current scheduler contract:
- `client.scheduler.schedule(...)`
- `client.scheduler.list()`
- `client.scheduler.cancel(...)`

### `file_download.py`
Shows how to:
- write a file
- use the returned `download_url`
- download the binary content through the SDK

### `error_handling.py`
Shows recommended exception handling with:
- `MCPAuthError`
- `MCPNotFoundError`
- `MCPError`

### `advanced_patterns.py`
Shows:
- context-managed client usage
- context-managed session usage
- bulk operations with typed module APIs
