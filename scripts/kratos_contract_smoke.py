#!/usr/bin/env python3
"""Fail-fast Kratos auth integration contract smoke check.

Required env:
- THEGENT_AUTH_PROVIDER=kratos
- KRATOS_PUBLIC_URL
"""

from __future__ import annotations

import json
import os
import sys


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    auth_provider = os.getenv("THEGENT_AUTH_PROVIDER", "").lower()
    if auth_provider != "kratos":
        raise RuntimeError(f"THEGENT_AUTH_PROVIDER is not 'kratos', got: {auth_provider}")

    public_url = _require_env("KRATOS_PUBLIC_URL")
    
    try:
        import httpx
        import asyncio
        
        async def check():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{public_url}/health/alive",
                    timeout=5
                )
                return response.status_code
        
        status = asyncio.run(check())
        
        if status != 200:
            raise RuntimeError(f"Kratos health check returned non-200 status: {status}")
            
    except ImportError:
        # Try urllib fallback
        import urllib.request
        url = f"{public_url}/health/alive"
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.getcode()
            if status != 200:
                raise RuntimeError(f"Kratos health check returned non-200 status: {status}")

    print(json.dumps({"ok": True, "target": "kratos", "url": public_url, "status": status}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "target": "kratos", "error": str(exc)}))
        raise
