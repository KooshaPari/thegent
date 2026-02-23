#!/usr/bin/env python3
"""Fail-fast Context7 integration contract smoke check.

Required env:
- CONTEXT7_BASE_URL
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    base_url = _require_env("CONTEXT7_BASE_URL").rstrip("/")
    url = f"{base_url}/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.getcode()
            body = response.read(1024).decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Context7 health check failed: {exc}") from exc

    if status != 200:
        raise RuntimeError(f"Context7 health check returned non-200 status: {status}")

    print(json.dumps({"ok": True, "target": "context7", "url": url, "status": status, "body": body[:120]}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 -- spike contract must fail loudly with explicit reason
        print(json.dumps({"ok": False, "target": "context7", "error": str(exc)}))
        raise
