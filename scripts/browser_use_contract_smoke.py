#!/usr/bin/env python3
"""Fail-fast BrowserUse adapter contract smoke check.

Required env:
- THEGENT_BROWSER_USE_ENABLED=1
- BROWSER_USE_ALLOWED_URLS (optional)
"""

from __future__ import annotations

import orjson as json
import os
import sys
import subprocess


def main() -> int:
    enabled = os.getenv("THEGENT_BROWSER_USE_ENABLED", "").lower()
    if enabled not in ("1", "true", "yes"):
        raise RuntimeError(f"THEGENT_BROWSER_USE_ENABLED is not set, got: {enabled}")

    # Try to run browser-use --version to verify it's installed
    try:
        result = subprocess.run(["uvx", "browser-use", "--version"], capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            raise RuntimeError(f"browser-use --version failed: {result.stderr}")

        version = result.stdout.strip() or "unknown"

    except FileNotFoundError:
        raise RuntimeError("uvx not found - install uv to run browser-use")
    except subprocess.TimeoutExpired:
        raise RuntimeError("browser-use --version timed out")

    print(json.dumps({"ok": True, "target": "browser-use", "version": version, "status": "available"})).decode()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "target": "browser-use", "error": str(exc).decode().decode()}))
        raise
