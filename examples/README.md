# CN MCP SDK Examples

This directory contains practical examples demonstrating how to use the CN MCP SDK for various tasks.

## Available Examples

### 1. `basic_usage.py` - Getting Started
Learn the fundamentals of using the SDK:
- Creating and disposing sessions
- Writing and downloading files
- Listing files in a session
- Accessing cache statistics

**Run it:**
```bash
python examples/basic_usage.py
```

**Key APIs:**
- `client.sessions.create()` - Create a new session
- `client.files.write()` - Write a file
- `client.files.list()` - List files in a session
- `client.files.download_text()` - Download file content
- `client.auth.cache_stats()` - Get cache statistics

---

### 2. `terminal_commands.py` - Terminal Execution
Execute shell commands and capture output:
- Simple command execution
- Commands with timeouts
- Output size limiting
- Terminal statistics

**Run it:**
```bash
python examples/terminal_commands.py
```

**Key APIs:**
- `client.terminal.execute()` - Execute a shell command
- `client.terminal.get_stats()` - Get terminal statistics

**Parameters:**
- `timeout_minutes` - Limit execution time
- `output_limit_kb` - Limit output capture size

---

### 3. `web_search.py` - Web Search
Perform web searches and store results:
- Basic text search
- Location-based search
- Limiting result count
- Storing search results as files

**Run it:**
```bash
python examples/web_search.py
```

**Key APIs:**
- `client.search.web()` - Perform a web search
- Search parameters: `query`, `location`, `num_results`

---

### 4. `scheduled_tasks.py` - Task Scheduling
Schedule tasks for future execution:
- Schedule task to run after delay
- Schedule task for specific datetime
- List scheduled tasks
- Cancel tasks

**Run it:**
```bash
python examples/scheduled_tasks.py
```

**Key APIs:**
- `client.scheduler.schedule()` - Create a scheduled task
  - Use `in_seconds` for delay-based scheduling
  - Use `run_at` for specific datetime scheduling
- `client.scheduler.list()` - List all tasks
- `client.scheduler.cancel()` - Cancel a task

---

### 5. `device_control.py` - IoT Device Management
Control and monitor IoT devices:
- List available devices
- Get device status
- Execute device actions
- Monitor device metrics

**Run it:**
```bash
python examples/device_control.py
```

**Key APIs:**
- `client.devices.list()` - List all devices
- `client.devices.get_status()` - Get device status and metrics
- `client.devices.execute()` - Execute an action on a device

---

### 6. `database_queries.py` - Database Operations
Perform read and write database operations:
- Read-only SELECT queries
- Query with parameters
- Insert and update operations
- Complex joins

**Run it:**
```bash
python examples/database_queries.py
```

**Key APIs:**
- `client.database.query()` - Read-only database queries
- `client.database.execute()` - Execute write operations
- Parameters: `sql`, `params`, `limit`

**Important:**
- Use `$1, $2, ...` syntax for parameters (PostgreSQL style)
- `query()` is read-only; use `execute()` for writes
- NEVER pass user input directly to SQL - always use parameters

---

### 7. `error_handling.py` - Error Handling Patterns
Learn proper error handling:
- Authentication errors
- Not found errors
- General API errors
- Connection errors
- Error recovery patterns

**Run it:**
```bash
python examples/error_handling.py
```

**Exception Types:**
- `MCPAuthError` - Authentication/authorization failures
- `MCPNotFoundError` - Resource not found
- `MCPError` - General API errors

---

### 8. `advanced_patterns.py` - Advanced Techniques
Master advanced SDK usage:
- Context manager pattern for resource cleanup
- Using environment variables for configuration
- Bulk file operations
- Chaining multiple operations
- Complex workflow scheduling

**Run it:**
```bash
python examples/advanced_patterns.py
```

**Patterns Covered:**
- Context manager: `with MCPClient(...) as client:`
- Environment variables: `MCP_API_KEY`, `MCP_BASE_URL`
- Batch operations for efficiency
- Operation chaining and composition
- Workflow definition and scheduling

---

## Setup Instructions

### Prerequisites
```bash
# Install the SDK
pip install cn-mcp

# Or install from source
pip install -e .
```

### Configuration

**Option 1: Command Line Arguments**
```python
from cn_mcp_sdk import MCPClient

client = MCPClient(
    api_key="your-api-key",
    base_url="http://localhost:8000",
    timeout=30,
)
```

**Option 2: Environment Variables**
```bash
export MCP_API_KEY="your-api-key"
export MCP_BASE_URL="http://localhost:8000"
export MCP_TIMEOUT="30"
export MCP_VERIFY_SSL="true"
```

Then use:
```python
from cn_mcp_sdk import MCPClient

client = MCPClient()  # Reads from environment
```

### Running Examples

```bash
# Run a specific example
python examples/basic_usage.py

# Run all examples
for example in examples/*.py; do
    echo "Running $example..."
    python "$example"
done
```

---

## Common Patterns

### Pattern 1: Session Management
```python
with MCPClient(api_key="key", base_url="http://localhost:8000") as client:
    session = client.sessions.create()
    session_id = session["session_id"]
    
    # Do work...
    
    client.sessions.dispose(session_id)
```

### Pattern 2: Error Handling
```python
from cn_mcp_sdk import MCPClient, MCPAuthError, MCPNotFoundError, MCPError

try:
    # Your code here
    pass
except MCPAuthError:
    print("Invalid API key")
except MCPNotFoundError:
    print("Resource not found")
except MCPError as e:
    print(f"API error: {e}")
```

### Pattern 3: File Operations
```python
# Write
client.files.write(
    session_id=session_id,
    path="/output/data.json",
    content=json.dumps(data),
)

# List
files = client.files.list(session_id=session_id)

# Download
content = client.files.download_text(file_id)
```

### Pattern 4: Database Queries
```python
# Read-only query with parameters
results = client.database.query(
    sql="SELECT * FROM users WHERE status = $1",
    params=["active"],
    limit=10,
)

# Write operation
client.database.execute(
    sql="INSERT INTO logs (message) VALUES ($1)",
    params=["Operation completed"],
)
```

---

## Troubleshooting

**Connection Refused**
- Verify MCP server is running on the correct host/port
- Check `MCP_BASE_URL` environment variable

**Authentication Failed**
- Verify API key is correct
- Check API key hasn't expired in the database
- Ensure `X-API-Key` header is being sent

**Resource Not Found**
- Verify session/file/device IDs are correct
- Check resource hasn't been deleted
- Ensure user has access to the resource

**Timeout**
- Increase `timeout` parameter
- Check network connectivity
- Verify server performance

---

## Additional Resources

- [SDK Documentation](../README.md)
- [API Reference](../README.md#api-reference)
- [Error Handling Guide](../README.md#error-handling)
- [Configuration Guide](../README.md#configuration)

---

## Tips for Best Practices

1. **Always use sessions** - Sessions provide isolation and resource tracking
2. **Handle errors gracefully** - Use try/except blocks for all API calls
3. **Use context managers** - Ensures proper cleanup: `with MCPClient(...) as client:`
4. **Batch operations** - Group related operations to reduce overhead
5. **Use parameters** - Always use parameterized queries (`$1, $2, ...`)
6. **Monitor resources** - Check cache stats and session limits
7. **Implement timeouts** - Prevent hanging operations
8. **Log operations** - Track important actions for debugging

---

## Contributing

Found issues or have improvements? Open an issue or submit a pull request!

