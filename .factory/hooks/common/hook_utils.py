#!/usr/bin/env python3
"""Shared utilities for Factory hooks - User Level."""

import orjson as json
import re
import sys
from typing import Any


def read_hook_input() -> dict[str, Any]:
    """Read and parse JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)


def output_json(data: dict[str, Any]) -> None:
    """Output JSON response to stdout."""


def block_with_reason(reason: str, hook_event: str | None = None) -> None:
    """Block operation with explanation."""
    if hook_event:
        output_json({"decision": "block", "reason": reason, "hookSpecificOutput": {"hookEventName": hook_event}})
    else:
        output_json({"decision": "block", "reason": reason})
    sys.exit(0)


def allow_with_message(message: str) -> None:
    """Allow operation with optional message."""
    output_json({"decision": "approve", "reason": message, "suppressOutput": True})
    sys.exit(0)


def check_for_secrets(content: str) -> list[str]:
    """Scan content for potential secrets - Universal patterns."""
    patterns = {
        "AWS Key": r"AKIA[0-9A-Z]{16}",
        "GitHub Token": r"gh[pousr]_[A-Za-z0-9_]{36,255}",
        "Generic API Key": r"(?i)api[_-]?key\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{32,})",
        "Password": r"(?i)password\s*[:=]\s*['\"]([^'\"]{8,})",
        "Secret": r"(?i)secret\s*[:=]\s*['\"]([^'\"]{16,})",
        "Token": r"(?i)token\s*[:=]\s*['\"]([a-zA-Z0-9_\-\.]{20,})",
        "Private Key": r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "JWT": r"eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*",
        "Slack Token": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
        "Google OAuth": r"ya29\.[0-9A-Za-z\-_]+",
        "Stripe Key": r"sk_live_[0-9a-zA-Z]{24}",
    }

    found = []
    for name, pattern in patterns.items():
        if re.search(pattern, content):
            found.append(name)
    return found


if __name__ == "__main__":
    # Self-test
    pass
