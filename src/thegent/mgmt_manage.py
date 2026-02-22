"""Management commands for agent self-service: ensure proxy, verify Codex+CLIProxy."""

from __future__ import annotations

import os
import shutil
import subprocess
import time

from thegent.config import ThegentSettings


def _proxy_base_url(settings: ThegentSettings) -> str:
    return f"http://127.0.0.1:{settings.cliproxy_port}/v1"


def _is_proxy_reachable(base_url: str, timeout: float = 2.0) -> bool:
    """Check if proxy is reachable (GET /v1/models)."""
    import httpx

    try:
        # WP-Y15: Disable trust_env to ensure we reach 127.0.0.1 even if system proxy is set.
        with httpx.Client(trust_env=False) as client:
            url = base_url.rstrip("/")
            if not url.endswith("/v1"):
                url = f"{url}/v1"
            url = f"{url}/models"
            resp = client.get(
                url,
                headers={"Authorization": "Bearer sk-dummy"},
                timeout=timeout,
            )
            return resp.is_success
    except Exception:
        return False


def ensure_proxy(timeout_sec: float = 30.0) -> tuple[bool, str]:
    """Ensure MCP + proxy are running. Starts via process-compose if needed.

    Returns (success, message).
    """
    settings = ThegentSettings()
    base_url = _proxy_base_url(settings)

    if _is_proxy_reachable(base_url):
        return True, f"Proxy already running at {base_url}"

    from thegent.mcp.manage import mcp_up

    ok, msg = mcp_up()
    if not ok:
        return False, f"Failed to start MCP+proxy: {msg}"

    # Poll for proxy readiness
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if _is_proxy_reachable(base_url):
            return True, f"Proxy ready at {base_url}"
        time.sleep(1.0)

    return False, f"Proxy did not become ready within {timeout_sec}s"


def verify_codex_cliproxy(
    model: str = "minimax-m2.5",
    prompt: str = "echo hello",
    timeout_sec: float = 90.0,
) -> tuple[bool, str]:
    """Verify Codex works with CLIProxy adapter.

    1. Ensures proxy is up (mcp up if needed)
    2. Runs `codex exec` against proxy
    3. Returns (success, message)

    Requires: codex CLI installed (npm i -g @openai/codex).
    """
    ok, msg = ensure_proxy(timeout_sec=30.0)
    if not ok:
        return False, msg

    settings = ThegentSettings()
    base_url = _proxy_base_url(settings)

    codex = shutil.which("codex")
    if not codex:
        return False, "codex CLI not found. Install: npm i -g @openai/codex"

    env = os.environ.copy()
    env["OPENAI_BASE_URL"] = base_url
    env["OPENAI_API_KEY"] = "sk-dummy"

    result = subprocess.run(
        [
            codex,
            "exec",
            prompt,
            "--model",
            model,
            "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        check=False,
    )

    if result.returncode == 0:
        return True, "Codex+CLIProxy verification passed"
    err = (result.stderr or result.stdout or "").strip()
    return False, f"Codex exec failed (exit {result.returncode}): {err[:500]}"
