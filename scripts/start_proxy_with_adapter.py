#!/usr/bin/env python3
"""Start CLIProxyAPIPlus behind the adapter (Responses API + WebSocket support).

Adapter listens on THGENT_CLIPROXY_PORT (8317), proxies to real proxy on port+1 (8318).
Usage: thegent mcp up (adapter enabled by default; set THGENT_CLIPROXY_ADAPTER=0 for direct proxy)
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import yaml
from thegent.agents.cliproxy_manager import _ensure_config, _resolve_binary
from thegent.config import ThegentSettings


def main() -> int:
    settings = ThegentSettings()
    port = settings.cliproxy_port
    backend_port = port + 1
    backend_url = f"http://127.0.0.1:{backend_port}/v1"

    config_path = _ensure_config(settings)
    # Backend needs its own port; create temp config with backend_port
    import tempfile
    raw = yaml.safe_load(config_path.read_text()) or {}
    backend_config = dict(raw)
    backend_config["port"] = backend_port
    tmp_config = Path(tempfile.gettempdir()) / f"thegent-cliproxy-{backend_port}.yaml"
    tmp_config.write_text(yaml.dump(backend_config, default_flow_style=False, sort_keys=False))
    config_path = tmp_config

    binary = _resolve_binary(settings)
    if not Path(binary).exists():
        alt = Path.cwd().parent / "CLIProxyAPIPlus-fork" / "cli-proxy-api-plus"
        if alt.exists():
            binary = str(alt)

    if not Path(binary).exists() and "/" not in binary:
        for segment in os.environ.get("PATH", "").split(":"):
            candidate = Path(segment) / binary
            if candidate.exists():
                binary = str(candidate)
                break

    if not Path(binary).exists():
        print("CLIProxyAPIPlus binary not found.", file=sys.stderr)
        return 1

    # Start real proxy on backend_port
    env = os.environ.copy()
    env["THGENT_CLIPROXY_PORT"] = str(backend_port)
    args = [binary, "-config", str(config_path)]
    
    # Capture stderr if debug is enabled to help diagnose startup failures
    stderr_target = None
    if os.environ.get("THGENT_DEBUG") == "1":
        stderr_target = subprocess.PIPE

    proc = subprocess.Popen(
        args,
        env=env,
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=stderr_target,
        start_new_session=True,
        text=True if stderr_target else False,
    )

    # Wait for backend
    backend_ready = False
    for _ in range(30):  # Increase from 20 to 30 (15s total)
        time.sleep(0.5)
        try:
            import urllib.request
            req = urllib.request.Request(f"http://127.0.0.1:{backend_port}/v1/models", method="GET")
            with urllib.request.urlopen(req, timeout=2) as _:
                backend_ready = True
                break
        except Exception:
            if proc.poll() is not None:
                if stderr_target:
                    out, err = proc.communicate()
                    print(f"CLIProxyAPIPlus backend failed to start (exit {proc.returncode}).\nStderr: {err}", file=sys.stderr)
                return 1
    
    if not backend_ready:
        print(f"CLIProxyAPIPlus backend (port {backend_port}) never became ready.", file=sys.stderr)
        proc.kill()
        return 1

    # Start adapter
    from thegent.cliproxy_adapter import create_adapter_app
    import uvicorn

    app = create_adapter_app(backend_url)
    log_level = "debug" if os.environ.get("THGENT_DEBUG") == "1" else "info"
    uvicorn.run(app, host="127.0.0.1", port=port, log_level=log_level)
    proc.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
