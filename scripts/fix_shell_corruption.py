#!/usr/bin/env python3
"""Fix shell corruption and CLIProxyAPI config issues.
Run this from a CLEAN terminal (not the corrupted one)."""

import shutil
import subprocess
import sys
from pathlib import Path

# Add src to path
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from thegent.agents.cliproxy_manager import _ensure_config
from thegent.config import ThegentSettings


def main() -> int:
    print("=== Shell Corruption Fix ===")
    print()

    # 1. Ensure CLIProxyAPI config exists
    print("1. Ensuring CLIProxyAPI config exists...")
    try:
        settings = ThegentSettings()
        config_path = _ensure_config(settings)
        print(f"   ✓ Config ensured: {config_path}")
    except Exception as e:
        print(f"   ✗ Failed to ensure config: {e}")
        return 1

    # 2. Fix fork config if fork binary exists
    print()
    print("2. Checking for CLIProxyAPIPlus-fork...")
    fork_bin = ROOT.parent / "CLIProxyAPIPlus-fork" / "cli-proxy-api-plus"
    fork_config = ROOT.parent / "CLIProxyAPIPlus-fork" / "config.yaml"

    if fork_bin.exists():
        print(f"   Found fork binary: {fork_bin}")
        if not fork_config.exists():
            print("   Creating fork config from thegent config...")
            fork_config.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(config_path, fork_config)
            print(f"   ✓ Created: {fork_config}")
        else:
            print("   ✓ Fork config already exists")
    else:
        print("   No fork binary found (skipping)")

    # 3. Stop any running CLIProxyAPI processes
    print()
    print("3. Stopping any running CLIProxyAPI processes...")
    try:
        # Try to stop via thegent
        result = subprocess.run(
            ["python", "-m", "thegent.main", "mcp", "down"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print("   ✓ Stopped via thegent mcp down")
        else:
            print(f"   (thegent mcp down returned {result.returncode})")
    except Exception as e:
        print(f"   (Could not stop via thegent: {e})")

    # Try to kill any cli-proxy-api-plus processes
    try:
        result = subprocess.run(
            ["pkill", "-f", "cli-proxy-api-plus"],
            capture_output=True,
            timeout=5,
        )
        if result.returncode == 0:
            print("   ✓ Killed cli-proxy-api-plus processes")
        else:
            print("   (No cli-proxy-api-plus processes found)")
    except Exception as e:
        print(f"   (Could not kill processes: {e})")

    # 4. Check for problematic shell hooks
    print()
    print("4. Checking shell configuration...")
    shell_configs = [
        Path.home() / ".zshrc",
        Path.home() / ".zshenv",
        Path.home() / ".zprofile",
    ]

    problematic_patterns = [
        "eval.*ls",
        "eval.*\\$(ls)",
        "eval.*`ls`",
    ]

    found_issues = False
    for config_file in shell_configs:
        if config_file.exists():
            content = config_file.read_text()
            for pattern in problematic_patterns:
                import re

                if re.search(pattern, content):
                    print(f"   ⚠️  Found problematic pattern in {config_file}: {pattern}")
                    found_issues = True

    if not found_issues:
        print("   ✓ No problematic patterns found in shell configs")

    # 5. Provide instructions
    print()
    print("=== Next Steps ===")
    print()
    print("1. Open a NEW terminal (don't use the corrupted one)")
    print()
    print("2. Test that commands work:")
    print("   echo 'test' > /tmp/test_fix.txt")
    print("   cat /tmp/test_fix.txt")
    print()
    print("3. If shell is still corrupted, reset hooks:")
    print("   unset precmd_functions chpwd_functions PROMPT_COMMAND")
    print("   unset -f precmd chpwd")
    print()
    print("4. Restart thegent MCP:")
    print("   python -m thegent.main mcp up")
    print()
    print("5. If issue persists, check Codex MCP config:")
    print("   python -m thegent.main mcp fix codex")
    print()
    print("Done!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
