#!/usr/bin/env python3
"""Fail-fast NATS event bus integration contract smoke check.

Required env:
- NATS_SERVERS (comma-separated URLs)
- THEGENT_EVENT_BUS=nats
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


async def _check_nats() -> dict:
    """Check NATS connection."""
    try:
        import nats

        servers = _require_env("NATS_SERVERS")
        server_list = [s.strip() for s in servers.split(",")]

        nc = await nats.connect(
            server_list,
            max_reconnect_attempts=2,
            reconnect_time_wait=1,
        )

        # Publish a ping to verify connection
        await nc.publish("thegent.health.check", b"ping")
        await nc.flush()

        await nc.close()

        return {"ok": True, "target": "nats", "servers": server_list, "status": "connected"}

    except ImportError:
        return {"ok": False, "target": "nats", "error": "nats-py not installed"}
    except Exception as exc:
        return {"ok": False, "target": "nats", "error": str(exc)}


def main() -> int:
    event_bus = os.getenv("THEGENT_EVENT_BUS", "").lower()
    if event_bus != "nats":
        raise RuntimeError(f"THEGENT_EVENT_BUS is not 'nats', got: {event_bus}")

    import asyncio
    result = asyncio.run(_check_nats())

<<<<<<< HEAD
    print(json.dumps(result).decode().decode())
=======
    print(json.dumps(result))
>>>>>>> fix/ci-remove-macos

    if not result.get("ok"):
        raise RuntimeError(f"NATS health check failed: {result.get('error')}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 -- spike contract must fail loudly with explicit reason
        print(json.dumps({"ok": False, "target": "nats", "error": str(exc).decode().decode()}))
        raise
