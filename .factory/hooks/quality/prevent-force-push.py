#!/usr/bin/env python3
"""Prevent accidental git force pushes - User Level Global Hook."""

import orjson as json
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name")
    if tool_name != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")

    if not command:
        sys.exit(0)

    # Check for force push patterns
    if "git push" in command and ("--force" in command or "-f" in command):
        sys.exit(0)

    # Allow operation
    sys.exit(0)


if __name__ == "__main__":
    main()
