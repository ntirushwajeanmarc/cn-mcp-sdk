"""Advanced usage patterns for the current cn-mcp SDK."""

import json
from datetime import datetime

from cn_mcp import MCPClient


print("=" * 60)
print("EXAMPLE 1: context-managed session")
print("=" * 60)

with MCPClient(api_key="your-api-key") as client:
    with client.session() as workspace:
        print(f"Workspace session: {workspace.session_id}")
        result = workspace.tool_call("terminal_exec", cmd="pwd")
        print(result["output"].strip())

print("\n" + "=" * 60)
print("EXAMPLE 2: bulk file operations")
print("=" * 60)

client = MCPClient(api_key="your-api-key")
try:
    with client.session() as workspace:
        files_to_write = {
            "output/config.json": json.dumps({"timeout": 30, "retries": 3}, indent=2),
            "output/readme.txt": "This is a sample README file.",
            "output/log.txt": "2026-01-01 10:00:00 - Application started",
        }

        file_ids = {}
        for path, content in files_to_write.items():
            resp = client.files.write(session_id=workspace.session_id, path=path, content=content)
            file_ids[path] = resp["file_id"]
            print(f"✓ {path}")

        files = client.files.list(session_id=workspace.session_id)
        print(f"\nStored {len(files)} files")

        metadata = {
            "written_at": datetime.utcnow().isoformat(),
            "files": files,
        }
        client.files.write(
            session_id=workspace.session_id,
            path="output/metadata.json",
            content=json.dumps(metadata, indent=2),
        )
        print("✓ Metadata saved")

finally:
    client.close()
