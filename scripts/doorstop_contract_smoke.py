#!/usr/bin/env python3
"""Fail-fast Doorstop requirements integration contract smoke check.

Required env:
- THEGENT_ENABLE_DOORSTOP=1
- DOORSTOP_PROJECT_DIR (optional, defaults to ./requirements)
"""

from __future__ import annotations

import json
import os
import sys


def main() -> int:
    enabled = os.getenv("THEGENT_ENABLE_DOORSTOP", "").lower()
    if enabled not in ("1", "true", "yes"):
        raise RuntimeError(f"THEGENT_ENABLE_DOORSTOP is not set, got: {enabled}")

    # Check if doorstop is installed
    import subprocess
    try:
        result = subprocess.run(
            ["doorstop", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            raise RuntimeError(f"doorstop --version failed: {result.stderr}")

        version = result.stdout.strip() or result.stderr.strip()

    except FileNotFoundError:
        raise RuntimeError("doorstop CLI not found - install doorstop")
    except subprocess.TimeoutExpired:
        raise RuntimeError("doorstop --version timed out")

    print(json.dumps({
        "ok": True,
        "target": "doorstop",
        "version": version,
        "status": "available"
    }))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "target": "doorstop", "error": str(exc)}))
        raise
