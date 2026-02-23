#!/usr/bin/env python3
"""Fail-fast LMCache integration contract smoke check.

Required env:
- LMCACHE_ENABLED=1
- LMCACHE_SERVER_URL or LMCACHE_BACKEND=redis
"""

from __future__ import annotations

import orjson as json
import os
import sys


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def _check_lmcache() -> dict:
    """Check LMCache connection."""
    enabled = os.getenv("LMCACHE_ENABLED", "").lower()
    if enabled not in ("1", "true", "yes"):
        return {"ok": False, "target": "lmcache", "error": "LMCACHE_ENABLED not set"}

    backend = os.getenv("LMCACHE_BACKEND", "redis")

    if backend == "redis":
        return await _check_redis()
    if backend == "http":
        return await _check_http()
    return {"ok": False, "target": "lmcache", "error": f"Unknown backend: {backend}"}


async def _check_redis() -> dict:
    """Check Redis backend."""
    try:
        import redis

        host = os.getenv("LMCACHE_REDIS_HOST", "localhost")
        port = int(os.getenv("LMCACHE_REDIS_PORT", "6379"))
        db = int(os.getenv("LMCACHE_REDIS_DB", "0"))
        password = os.getenv("LMCACHE_REDIS_PASSWORD", None) or None

        r = redis.Redis(host=host, port=port, db=db, password=password, socket_timeout=5)
        r.ping()

        return {"ok": True, "target": "lmcache", "backend": "redis", "status": "connected"}

    except ImportError:
        return {"ok": False, "target": "lmcache", "error": "redis-py not installed"}
    except Exception as exc:
        return {"ok": False, "target": "lmcache", "error": str(exc)}


async def _check_http() -> dict:
    """Check HTTP backend."""
    server_url = os.getenv("LMCACHE_SERVER_URL", "http://localhost:8080").rstrip("/")
    url = f"{server_url}/health"

    try:
        import urllib.request
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=5) as response:
            status = response.getcode()
            body = response.read(512).decode("utf-8", errors="replace")

        return {"ok": True, "target": "lmcache", "backend": "http", "status": status, "body": body[:120]}

    except Exception as exc:
        return {"ok": False, "target": "lmcache", "error": str(exc)}


def main() -> int:
    import asyncio
    result = asyncio.run(_check_lmcache())

<<<<<<< HEAD
    print(json.dumps(result).decode().decode())
=======
    print(json.dumps(result))
>>>>>>> fix/ci-remove-macos

    if not result.get("ok"):
        raise RuntimeError(f"LMCache health check failed: {result.get('error')}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 -- spike contract must fail loudly with explicit reason
        print(json.dumps({"ok": False, "target": "lmcache", "error": str(exc).decode().decode()}))
        raise
