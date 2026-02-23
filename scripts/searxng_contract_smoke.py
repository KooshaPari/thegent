#!/usr/bin/env python3
"""Fail-fast SearXNG search integration contract smoke check.

Required env:
- THEGENT_ENABLE_SEARXNG=1
- SEARXNG_URL (optional, defaults to http://localhost:8888)
"""

from __future__ import annotations

import json
import os
import sys


def main() -> int:
    enabled = os.getenv("THEGENT_ENABLE_SEARXNG", "").lower()
    if enabled not in ("1", "true", "yes"):
        raise RuntimeError(f"THEGENT_ENABLE_SEARXNG is not set, got: {enabled}")

    server_url = os.getenv("SEARXNG_URL", "http://localhost:8888").rstrip("/")
    
    # Try health endpoint first
    try:
        import httpx
        import asyncio
        
        async def check():
            async with httpx.AsyncClient() as client:
                # Try health or search endpoint
                for endpoint in ["/health", "/"]:
                    try:
                        response = await client.get(
                            f"{server_url}{endpoint}",
                            timeout=5
                        )
                        if response.status_code == 200:
                            return 200
                    except Exception:
                        continue
                return 503
        
        status = asyncio.run(check())
        
        if status != 200:
            raise RuntimeError(f"SearXNG health check returned non-200 status: {status}")
            
    except ImportError:
        import urllib.request
        url = f"{server_url}/search"
        # Just check if URL is reachable
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.getcode()
            if status not in (200, 400):  # 400 is OK - means server is up
                raise RuntimeError(f"SearXNG check returned status: {status}")

    print(json.dumps({"ok": True, "target": "searxng", "url": server_url, "status": status}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "target": "searxng", "error": str(exc)}))
        raise
