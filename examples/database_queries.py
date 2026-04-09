"""Database query example."""

from cn_mcp import MCPClient

client = MCPClient(api_key="your-api-key")

try:
    # List available tools
    print("Available tools:")
    tools = client.list_tools()
    for tool in tools:
        print(f"  - {tool}")
    print()

    # Read-only query example
    print("Executing read-only query...")
    results = client.tool_call(
        "db_query",
        query="SELECT user_id, email FROM users WHERE status = $1",
        params=["active"],
    )
    print(f"Found {len(results)} active users\n")

    # Write operation example
    print("Executing write operation...")
    insert_result = client.tool_call(
        "db_execute",
        query="INSERT INTO audit_logs (action, created_at) VALUES ($1, NOW()) RETURNING id",
        params=["db_query_example"],
    )
    print(f"✓ Inserted log ID: {insert_result}\n")

    # Dynamic tool calling
    print("Using tool_call for database query...")
    results = client.tool_call("db_query", query="SELECT * FROM users LIMIT 5")
    print(f"✓ Found {len(results)} users via tool_call\n")

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
