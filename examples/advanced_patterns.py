"""Advanced tool_call-only usage patterns."""

import base64
import json
from datetime import datetime, timezone

from cn_mcp import MCPClient


client = MCPClient(api_key="your-api-key")

print("=" * 60)
print("EXAMPLE 1: default session binding")
print("=" * 60)

session = client.tool_call("session_create")
session_id = session["session_id"]
client.set_default_session(session_id)

try:
    result = client.tool_call("terminal_exec", cmd="pwd")
    print(result["stdout"].strip())

    print("\n" + "=" * 60)
    print("EXAMPLE 2: bulk file operations")
    print("=" * 60)

    files_to_write = {
        "output/config.json": json.dumps({"timeout": 60, "retries": 3}, indent=2),
        "output/readme.txt": "This is a sample README file.",
        "output/log.txt": "2026-01-01 10:00:00 - Application started",
    }

    for path, content in files_to_write.items():
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        client.tool_call("file_write", path=path, content_base64=encoded)
        print(f"✓ {path}")

    files = client.tool_call("file_list")
    print(f"\nStored {len(files)} files")

    metadata = {
        "written_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }
    metadata_b64 = base64.b64encode(json.dumps(metadata, indent=2).encode("utf-8")).decode("utf-8")
    client.tool_call("file_write", path="output/metadata.json", content_base64=metadata_b64)
    print("✓ Metadata saved")

finally:
    client.tool_call("session_dispose", session_id=session_id)
    client.clear_default_session()
    client.close()
