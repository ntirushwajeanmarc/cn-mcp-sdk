"""Database operations example for session-backed SQLite."""

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

try:
    session = client.sessions.create()
    workspace = client.bind_session(session["session_id"])

    print("Creating a table...")
    created = client.db.execute(
        session_id=workspace.session_id,
        sql="CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, body TEXT)",
    )
    print(created)

    print("\nInserting a row...")
    inserted = client.db.execute(
        session_id=workspace.session_id,
        sql="INSERT INTO notes (body) VALUES (?)",
        params=["Remember to ship the SDK update"],
    )
    print(inserted)

    print("\nQuerying rows...")
    rows = client.db.query(
        session_id=workspace.session_id,
        sql="SELECT id, body FROM notes",
    )
    print(rows)

    workspace.dispose()

finally:
    client.close()
