#!/usr/bin/env python3
"""Orjson Migration Script for thegent.

This script helps migrate from json to orjson in thegent codebase.
Usage: python scripts/migrate_to_orjson.py [--dry-run]

Note: orjson.dumps returns bytes, not str. Replace:
  - json.dumps(x) -> orjson.dumps(x).decode()
  - json.loads(x) -> orjson.loads(x)
"""

import subprocess
import sys
from pathlib import Path

# Files with most json usage (priority order)
HIGH_PRIORITY_FILES = [
    ("src/thegent/mcp/tools/modes.py", 39),
    ("src/thegent/execution.py", 37),
    ("src/thegent/cliproxy_adapter.py", 22),
    ("src/thegent/mcp/tools/seeds.py", 19),
    ("src/thegent/mesh/consensus.py", 15),
    ("src/thegent/mcp/server/tools_provider_models.py", 14),
    ("src/thegent/mcp/manage.py", 14),
    ("src/thegent/mcp/server/tools_sessions.py", 13),
    ("src/thegent/integrations/workstream_autosync.py", 12),
    ("src/thegent/cli/apps/project.py", 12),
]

MEDIUM_PRIORITY_FILES = [
    ("src/thegent/mcp/tools/elicitation.py", 11),
    ("src/thegent/cli/commands/session_cmds.py", 11),
    ("src/thegent/mcp/server_execution_tools.py", 10),
    ("src/thegent/infra/ipc.py", 10),
    ("src/thegent/governance/compliance.py", 10),
]

def check_orjson_installed():
    """Check if orjson is installed."""
    try:
        import orjson
        return True
    except ImportError:
        return False

def get_files_needing_migration():
    """Find all files importing json."""
    result = subprocess.run(
        ["rg", "import json", "--type", "py", "src/thegent", "-l"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split("\n")

def main():
    if not check_orjson_installed():
        print("ERROR: orjson not installed. Run: pip install orjson")
        sys.exit(1)
    
    print("=== ORJSON MIGRATION PLAN ===\n")
    print(f"Total files importing json: {len(get_files_needing_migration())}")
    print("\n--- HIGH PRIORITY (30+ usages) ---")
    for f, count in HIGH_PRIORITY_FILES:
        print(f"  {f}: {count} uses")
    
    print("\n--- MEDIUM PRIORITY (10-30 usages) ---")
    for f, count in MEDIUM_PRIORITY_FILES:
        print(f"  {f}: {count} uses")
    
    print("\n--- MIGRATION STEPS ---")
    print("1. Replace 'import json' with:")
    print("   try:")
    print("       import orjson")
    print("       JSON = orjson")
    print("   except ImportError:")
    print("       import json")
    print("       JSON = json")
    print("")
    print("2. Replace json.dumps(x):")
    print("   - JSON.dumps(x) -> JSON.dumps(x).decode() if str needed")
    print("   - json.dumps(x) -> orjson.dumps(x) if bytes OK")
    print("")
    print("3. Replace json.loads(x):")
    print("   - JSON.loads(x) works for both str and bytes")
    print("")
    print("4. Replace json.load(f) / json.dump(d, f):")
    print("   - Need wrapper: load(f) -> orjson.loads(f.read())")
    print("")

if __name__ == "__main__":
    main()
