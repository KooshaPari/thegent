#!/usr/bin/env python3
"""Fail-fast Graphiti integration contract smoke check.

Required env:
- GRAPHITI_SERVER_URL
- GRAPHITI_API_KEY (optional)
"""

from __future__ import annotations

import orjson as json
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
    server_url = _require_env("GRAPHITI_SERVER_URL").rstrip("/")
    api_key = os.getenv("GRAPHITI_API_KEY", "")

    url = f"{server_url}/health"

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=5) as response:
            status = response.getcode()
            body = response.read(1024).decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Graphiti health check failed: {exc}") from exc

    if status != 200:
        raise RuntimeError(f"Graphiti health check returned non-200 status: {status}")

    print(json.dumps({"ok": True, "target": "graphiti", "url": url, "status": status, "body": body[:120]}).decode().decode())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 -- spike contract must fail loudly with explicit reason
        print(json.dumps({"ok": False, "target": "graphiti", "error": str(exc).decode().decode()}))
        raise
