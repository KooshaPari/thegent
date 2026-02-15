#!/usr/bin/env python3
"""Universal secret detection for any project - User Level Global Hook."""

import sys
from pathlib import Path

# Add common utilities to path
sys.path.insert(0, str(Path.home() / ".factory" / "hooks" / "common"))
from hook_utils import block_with_reason, check_for_secrets, read_hook_input


def main() -> None:
    data = read_hook_input()

    tool_name = data.get("tool_name")
    if tool_name not in ["Write", "Edit"]:
        sys.exit(0)  # Not applicable

    tool_input = data.get("tool_input", {})
    content = tool_input.get("content") or tool_input.get("new_str", "")

    if not content:
        sys.exit(0)

    # Check for secrets
    secrets_found = check_for_secrets(content)

    if secrets_found:
        block_with_reason(
            f"🔒 Universal Security Policy: Content contains potential secrets:\n"
            f"   {', '.join(secrets_found)}\n\n"
            f"Please use environment variables or secure secret management.\n"
            f"For project-specific secrets, use gitignored config files.",
            "PreToolUse",
        )

    # Allow operation
    sys.exit(0)


if __name__ == "__main__":
    main()
