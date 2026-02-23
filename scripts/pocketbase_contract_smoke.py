#!/usr/bin/env python3
"""Fail-fast PocketBase integration contract smoke check.

Required env:
- THEGENT_POCKETBASE_ENABLED=1
- POCKETBASE_HTTP_ADDR (optional, defaults to 127.0.0.1:8090)
"""

from __future__ import annotations

import json
import os
import sys


def main() -> int:
    enabled = os.getenv("THEGENT_POCKETBASE_ENABLED", "").lower()
    if enabled not in ("1", "true", "yes"):
        raise RuntimeError(f"THEGENT_POCKETBASE_ENABLED is not set, got: {enabled}")

    http_addr = os.getenv("POCKETBASE_HTTP_ADDR", "127.0.0.1:8090")
    base_url = f"http://{http_addr}"

    try:
        import httpx
        import asyncio

        async def check():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url}/api/health",
                    timeout=5
                )
                return response.status_code

        status = asyncio.run(check())

        if status != 200:
            raise RuntimeError(f"PocketBase health check returned non-200 status: {status}")

    except ImportError:
        import urllib.request
        url = f"{base_url}/api/health"
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.getcode()
            if status != 200:
                raise RuntimeError(f"PocketBase health check returned non-200 status: {status}")

    print(json.dumps({"ok": True, "target": "pocketbase", "url": base_url, "status": status}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "target": "pocketbase", "error": str(exc)}))
        raise
