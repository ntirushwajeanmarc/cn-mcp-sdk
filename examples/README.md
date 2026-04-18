# CN MCP SDK Examples

These examples use `mcp.tool_call(...)` style for agent-oriented integration.

## Highlights

- Use `mcp.tool_call(...)` for all MCP actions.
- For workspace tools, create a session first and pass `session_id`.
- Dispose sessions at the end with `session_dispose`.

## Examples

### `quick_start.py`
Small end-to-end example covering:
- session creation
- file write via `file_write`
- terminal execution via `terminal_exec`
- cleanup via `session_dispose`

### `terminal_commands.py`
Shows `terminal_exec` patterns with explicit `session_id`.

### `device_control.py`
Uses `device_list` and `device_set_state`.

### `scheduled_tasks.py`
Uses `time_schedule`, `time_scheduled_tasks`, and `time_cancel`.

### `error_handling.py`
Shows recommended exception handling with:
- `MCPAuthError`
- `MCPNotFoundError`
- `MCPError`

### `agentic_use.py`
Experimental autonomous orchestration example that combines an LLM and MCP
tools. It is intentionally advanced and should be treated as a lab/demo script,
not a production-ready agent runner.
