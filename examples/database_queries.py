"""Database operations example for session-backed SQLite."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    session = client.tool_call("session_create")
    session_id = session["session_id"]
    client.set_default_session(session_id)

    print("Creating a table...")
    created = client.tool_call(
        "db_execute",
        sql="CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, body TEXT)",
    )
    print(created)

    print("\nInserting a row...")
    inserted = client.tool_call(
        "db_execute",
        sql="INSERT INTO notes (body) VALUES (?)",
        params=["Remember to ship the SDK update"],
    )
    print(inserted)

    print("\nQuerying rows...")
    rows = client.tool_call(
        "db_query",
        sql="SELECT id, body FROM notes",
    )
    print(rows)

    client.tool_call("session_dispose", session_id=session_id)
    client.clear_default_session()

finally:
    client.close()
