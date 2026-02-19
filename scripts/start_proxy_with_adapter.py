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

import httpx
import yaml

from thegent.agents.cliproxy_manager import _ensure_config, _resolve_binary
from thegent.config import ThegentSettings

ROOT = Path(__file__).resolve().parents[1]


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
            # Ensure config exists before using fork binary (fork looks for config.yaml in its dir)
            fork_config = alt.parent / "config.yaml"
            if not fork_config.exists() and config_path.exists():
                # Copy thegent config to fork location if fork binary is used
                import shutil

                shutil.copy2(config_path, fork_config)

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
    log_file = ROOT / ".process-compose" / "logs" / "proxy-backend.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # We always redirect to a file for better debugging
    backend_log = open(log_file, "a", buffering=1)

    proc = subprocess.Popen(
        args,
        env=env,
        cwd=str(ROOT),
        stdout=backend_log,
        stderr=backend_log,
        start_new_session=True,
        text=True,
    )

    # Wait for backend
    backend_ready = False
    for _ in range(30):  # Increase from 20 to 30 (15s total)
        time.sleep(0.5)
        try:
            with httpx.Client(timeout=2) as client:
                resp = client.get(f"http://127.0.0.1:{backend_port}/v1/models")
                resp.raise_for_status()
                backend_ready = True
                break
        except Exception:
            if proc.poll() is not None:
                if stderr_target:
                    _out, err = proc.communicate()
                    print(
                        f"CLIProxyAPIPlus backend failed to start (exit {proc.returncode}).\nStderr: {err}",
                        file=sys.stderr,
                    )
                return 1

    if not backend_ready:
        print(f"CLIProxyAPIPlus backend (port {backend_port}) never became ready.", file=sys.stderr)
        proc.kill()
        return 1

    # Start adapter
    import uvicorn

    from thegent.cliproxy_adapter import create_adapter_app

    log_level = "debug" if settings.debug else "info"
    reload = settings.reload

    if reload:
        # For reload, we must pass the app as an import string
        # create_adapter_app needs the backend_url, so we set it in env for the reload process
        if settings.cliproxy_backend_url:
            backend_url = settings.cliproxy_backend_url
        env["THGENT_CLIPROXY_BACKEND_URL"] = backend_url
        uvicorn.run(
            "thegent.cliproxy_adapter:create_adapter_app_reloading",
            host="127.0.0.1",
            port=port,
            log_level=log_level,
            reload=True,
            factory=True,
        )
    else:
        app = create_adapter_app(backend_url)
        uvicorn.run(app, host="127.0.0.1", port=port, log_level=log_level)

    proc.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
