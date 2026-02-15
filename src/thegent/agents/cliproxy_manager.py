"""CLIProxyAPIPlus lifecycle: config generation and proxy process management.

All providers (minimax, glm, antigravity, etc.) use CLIProxyAPIPlus native config and login.
GLM is via iFlow (thegent cliproxy login iflow). MiniMax uses minimax: block in config.
No factory config merge - wire providers the same way as other OAuth providers.
"""

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml

from thegent.config import ThegentSettings

_PROXY_READY_TIMEOUT = 5
_PROXY_CHECK_TIMEOUT = 2
_CLIPROXY_NOT_FOUND_MSG = (
    "cli-proxy-api-plus not found. Install from "
    "https://github.com/router-for-me/CLIProxyAPIPlus/releases "
    "(e.g. CLIProxyAPIPlus_*_darwin_arm64.tar.gz -> extract to ~/.local/bin). "
    "Or set THGENT_CLIPROXY_BINARY=/path/to/cli-proxy-api-plus"
)


def _resolve_binary(settings: ThegentSettings) -> str:
    """Resolve CLIProxyAPIPlus binary path. Prefers THGENT_CLIPROXY_BINARY env."""
    cmd = settings.cliproxy_binary
    env_val = os.environ.get("THGENT_CLIPROXY_BINARY")
    if env_val:
        expanded = str(Path(env_val).expanduser())
        if Path(expanded).exists():
            return expanded
        return env_val
    if "/" in cmd or "~" in cmd:
        expanded = str(Path(cmd).expanduser())
        if Path(expanded).exists():
            return expanded
    found = shutil.which(cmd)
    if found:
        return found
    local = Path.home() / ".local" / "bin" / cmd
    if local.exists():
        return str(local)
    return cmd


def _binary_available(binary: str) -> bool:
    """Check if binary path exists or is on PATH."""
    return Path(binary).exists() or shutil.which(binary) is not None


def _ensure_config(settings: ThegentSettings) -> Path:
    """Ensure cliproxy config exists; create minimal YAML if missing. No factory merge."""
    config_path = settings.cliproxy_config_path.expanduser().resolve()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    auth_dir = settings.cliproxy_auth_dir.expanduser().resolve()
    auth_dir.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        try:
            raw = yaml.safe_load(config_path.read_text())
            config: dict[str, Any] = dict(raw) if isinstance(raw, dict) else {}
        except Exception:
            config = {}
    else:
        config = {}

    config.setdefault("port", settings.cliproxy_port)
    config.setdefault("auth-dir", str(auth_dir))

    config_path.write_text(str(yaml.dump(config, default_flow_style=False, sort_keys=False)))
    return config_path


def _is_proxy_reachable(base_url: str) -> bool:
    """Check if proxy is reachable (GET /v1/models or /models)."""
    import urllib.request

    for path in ("/v1/models", "/models"):
        try:
            req = urllib.request.Request(
                f"{base_url.rstrip('/')}{path}",
                method="GET",
                headers={"Authorization": "Bearer sk-dummy"},
            )
            with urllib.request.urlopen(req, timeout=_PROXY_CHECK_TIMEOUT) as _:
                return True
        except Exception:
            continue
    return False


def _start_proxy_and_wait(
    binary: str, config_path: Path, base_url: str, settings: ThegentSettings
) -> subprocess.Popen[bytes]:
    """Start proxy process and wait for readiness. Returns proc or raises."""
    proc = subprocess.Popen(
        [binary, "-config", str(config_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
        env=os.environ.copy(),
    )
    for _ in range(_PROXY_READY_TIMEOUT * 2):
        time.sleep(0.5)
        if _is_proxy_reachable(base_url):
            return proc
        if proc.poll() is not None:
            raise RuntimeError(f"CLIProxyAPIPlus exited with code {proc.returncode}. Check config at {config_path}")
    proc.kill()
    raise RuntimeError(
        f"CLIProxyAPIPlus did not become ready within {_PROXY_READY_TIMEOUT}s. "
        f"Port {settings.cliproxy_port} may be in use."
    )


def ensure_proxy_running(settings: ThegentSettings) -> str:
    """
    Ensure CLIProxyAPIPlus is running. Start if not reachable.
    Returns base_url (e.g. http://127.0.0.1:8317/v1).
    """
    base_url = f"http://127.0.0.1:{settings.cliproxy_port}/v1"
    if _is_proxy_reachable(base_url):
        return base_url

    binary = _resolve_binary(settings)
    if not _binary_available(binary):
        raise FileNotFoundError(_CLIPROXY_NOT_FOUND_MSG)

    config_path = _ensure_config(settings)
    _start_proxy_and_wait(binary, config_path, base_url, settings)
    return base_url


def start_proxy_managed(settings: ThegentSettings) -> tuple[subprocess.Popen[bytes] | None, str]:
    """
    Start proxy and return (proc, base_url) for lifecycle management.
    Caller must terminate proc on shutdown. Skips if proxy already reachable (proc=None).
    """
    base_url = f"http://127.0.0.1:{settings.cliproxy_port}/v1"
    if _is_proxy_reachable(base_url):
        return (None, base_url)

    binary = _resolve_binary(settings)
    if not _binary_available(binary):
        raise FileNotFoundError(_CLIPROXY_NOT_FOUND_MSG)

    config_path = _ensure_config(settings)
    proc = _start_proxy_and_wait(binary, config_path, base_url, settings)
    return (proc, base_url)


# CLIProxyAPIPlus -login flags. GLM via iFlow; minimax prompts for api-key.
_LOGIN_FLAGS: dict[str, str] = {
    "claude": "-claude-login",
    "codex": "-codex-login",
    "gemini": "-login",
    "copilot": "-github-copilot-login",
    "antigravity": "-antigravity-login",
    "qwen": "-qwen-login",
    "iflow": "-iflow-login",
    "iflow-cookie": "-iflow-cookie",
    "glm": "-iflow-login",  # GLM is via iFlow channel
    "minimax": "-minimax-login",
    "kimi": "-kimi-login",
    "kiro": "-kiro-login",
    "kiro-google": "-kiro-google-login",
    "kiro-aws": "-kiro-aws-login",
    "kiro-aws-authcode": "-kiro-aws-authcode",
    "kiro-import": "-kiro-import",
    "roo": "-roo-login",
    "kilo": "-kilo-login",
}


def run_login(settings: ThegentSettings, provider: str) -> int:
    """
    Run login for provider. Returns exit code.
    All providers (including roo, kilo) use CLIProxyAPIPlus flags; logic lives in Go.
    """
    if provider not in _LOGIN_FLAGS:
        raise ValueError(f"Unknown provider: {provider}. Supported: {', '.join(sorted(_LOGIN_FLAGS))}")

    binary = _resolve_binary(settings)
    if not _binary_available(binary):
        raise FileNotFoundError(_CLIPROXY_NOT_FOUND_MSG)
    config_path = _ensure_config(settings)
    flag = _LOGIN_FLAGS[provider]
    proc = subprocess.run(
        [binary, "-config", str(config_path), flag],
        check=False,
        env=os.environ.copy(),
    )
    return proc.returncode
