"""Database query example."""

from cn_mcp import MCPClient

# Initialize client (uses https://mcp.circuitnotion.com by default)
client = MCPClient(api_key="your-api-key")

try:
    # Create a session
    session = client.sessions.create()
    session_id = session["session_id"]
    print(f"Session: {session_id}\n")

    # Read-only query example
    print("Executing read-only query...")
    results = client.database.query(
        sql="SELECT user_id, email, created_at FROM users WHERE status = $1",
        params=["active"],
        limit=10,
    )
    print(f"Found {len(results)} active users:\n")
    for row in results:
        print(f"  User ID: {row.get('user_id')}")
        print(f"  Email: {row.get('email')}")
        print(f"  Created: {row.get('created_at')}")
        print()

    # Query with multiple parameters
    print("Querying devices by location...")
    results = client.database.query(
        sql="""
            SELECT device_id, name, location, status 
            FROM devices 
            WHERE location = $1 AND status = $2 
            ORDER BY name
        """,
        params=["office", "online"],
        limit=20,
    )
    print(f"Found {len(results)} devices:")
    for row in results:
        print(f"  - {row.get('name')} ({row.get('device_id')})")
        print(f"    Location: {row.get('location')}, Status: {row.get('status')}")
    print()

    # Write operation example
    print("Executing write operation (insert)...")
    insert_result = client.database.execute(
        sql="""
            INSERT INTO audit_logs (user_id, action, resource, session_id, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            RETURNING log_id
        """,
        params=["user123", "device_control", "device_456", session_id],
    )
    print(f"✓ Inserted log ID: {insert_result}")
    print()

    # Update operation example
    print("Executing write operation (update)...")
    update_result = client.database.execute(
        sql="""
            UPDATE devices 
            SET last_accessed = NOW(), access_count = access_count + 1
            WHERE device_id = $1
        """,
        params=["device_456"],
    )
    print(f"✓ Updated {update_result} records")
    print()

    # Complex query with joins
    print("Complex query with joins...")
    results = client.database.query(
        sql="""
            SELECT 
                u.user_id,
                u.email,
                COUNT(d.device_id) as device_count,
                MAX(d.last_accessed) as last_device_access
            FROM users u
            LEFT JOIN user_devices ud ON u.user_id = ud.user_id
            LEFT JOIN devices d ON ud.device_id = d.device_id
            WHERE u.status = $1
            GROUP BY u.user_id, u.email
            HAVING COUNT(d.device_id) > 0
            ORDER BY device_count DESC
        """,
        params=["active"],
        limit=5,
    )
    print(f"Found {len(results)} active users with devices:")
    for row in results:
        print(f"  User: {row.get('email')}")
        print(f"  Devices: {row.get('device_count')}")
        print(f"  Last access: {row.get('last_device_access')}")
        print()

    # Error handling for write operations
    print("Attempting write with validation...")
    try:
        result = client.database.execute(
            sql="UPDATE non_existent_table SET col = $1",
            params=["value"],
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"✗ Error (expected): {e}")

    client.sessions.dispose(session_id)

finally:
    client.close()
