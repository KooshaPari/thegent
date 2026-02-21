#!/usr/bin/env python3
"""Start process-compose with lightweight preflight and hold-if-running behavior."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx


def _resolve_uv_bin() -> str:
    preferred = Path("/opt/homebrew/bin/uv")
    if preferred.exists():
        return str(preferred)
    return shutil.which("uv") or "uv"


def _http_ok(url: str, timeout: float = 1.5) -> bool:
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return True
    except Exception:
        return False


def _run_checked(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=str(cwd), check=False)
    if result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(cmd)}")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    os.chdir(repo_root)

    if not shutil.which("process-compose"):
        print("process-compose is required but not installed.", file=sys.stderr)
        return 1

    # Preflight: cliproxy build/config parity with task flow.
    uv_bin = _resolve_uv_bin()

    if (repo_root.parent / "cliproxyapi-plusplus").exists():
        _run_checked(["task", "cliproxy:build"], repo_root)
    _run_checked([uv_bin, "run", "thegent", "cliproxy", "ensure-config"], repo_root)

    mcp_url = "http://127.0.0.1:3847/health"
    proxy_url = "http://127.0.0.1:8317/v1/models"
    mcp_up = _http_ok(mcp_url)
    proxy_up = _http_ok(proxy_url)

    # Hold-if-running: avoid duplicate stack bring-up when services are already healthy.
    args = sys.argv[1:] if len(sys.argv) > 1 else ["up"]
    if mcp_up and proxy_up and "up" in args:
        print("thegent services already healthy; skipping duplicate process-compose up.")
        return 0

    # If MCP is up but proxy is not, give bundled startup a short window before starting a second stack.
    if mcp_up and not proxy_up:
        for _ in range(6):
            time.sleep(0.5)
            if _http_ok(proxy_url):
                print("proxy became healthy via existing MCP bundle; skipping duplicate process-compose up.")
                return 0

    os.execvp("process-compose", ["process-compose", *args])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
