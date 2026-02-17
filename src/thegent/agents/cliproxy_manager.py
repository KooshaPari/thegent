"""CLIProxyAPIPlus lifecycle: config generation and proxy process management.

Unified login flow: open URL + prompt for API key for all providers. Preflight check for
existing credentials. Setup uses the same flow.
Provider/model definitions from internal JSON (no factory config dependency).
"""

import json
import logging
import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Any

import httpx
import yaml

from thegent.config import ThegentSettings

# Lazy imports for better startup performance
def _get_settings():
    from thegent.config import ThegentSettings
    return ThegentSettings()

def _get_yaml():
    import yaml
    return yaml

def _get_httpx():
    import httpx
    return httpx

_CLIPROXY_DATA_DIR = Path(__file__).parent / "cliproxy_data"

_PROXY_READY_TIMEOUT = 5


def _load_json(name: str) -> dict[str, Any]:
    """Load JSON from cliproxy_data. Returns {} on missing/invalid."""
    path = _CLIPROXY_DATA_DIR / name
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _get_provider_definitions() -> dict[str, Any]:
    """Load provider definitions from internal JSON."""
    return _load_json("provider_definitions.json")


def _get_model_definitions() -> dict[str, Any]:
    """Load model definitions (common aliases) from internal JSON."""
    return _load_json("model_definitions.json")
_PROXY_CHECK_TIMEOUT = 2
_CLIPROXY_NOT_FOUND_MSG = (
    "cli-proxy-api-plus not found. Install from "
    "https://github.com/router-for-me/CLIProxyAPIPlus/releases "
    "(e.g. CLIProxyAPIPlus_*_darwin_arm64.tar.gz -> extract to ~/.local/bin). "
    "Or set THGENT_CLIPROXY_BINARY=/path/to/cli-proxy-api-plus"
)


def _resolve_binary(settings: "ThegentSettings") -> str:
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


def _get_claude_aliases(model: str) -> list[dict[str, str]]:
    """Get standard aliases for a given underlying model.

    Per z.ai and MiniMax docs: provider-native names (MiniMax-M2.5, glm-5, GLM-5)
    work without any Claude ID mapping. Include provider name as alias.
    """
    common = [
        "sonnet", "haiku", "opus", 
        "claude-sonnet-4.5", "claude-haiku-4.5", "claude-opus-4.6",
        "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022", "claude-3-opus-20240229",
        "composer-1.5", "composer-1.5-high", "composer-1.5-spark",
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"
    ]
    out = [{"name": model, "alias": model}]
    for a in common:
        out.append({"name": model, "alias": a})
    return out


def _build_provider_login_config() -> dict[str, dict[str, Any]]:
    """Build PROVIDER_LOGIN_CONFIG from internal provider_definitions.json."""
    defs_ = _get_provider_definitions()
    out: dict[str, dict[str, Any]] = {}
    for name, cfg in defs_.items():
        if not isinstance(cfg, dict) or "login" not in cfg:
            continue
        login = cfg.get("login", {})
        base_url = cfg.get("base_url", "")
        if cfg.get("base_url_env"):
            base_url = os.environ.get(cfg["base_url_env"], base_url)
        out[name] = {
            "url": login.get("url", ""),
            "base_url": base_url,
            "display_name": login.get("display_name", name),
            "model": cfg.get("model", name),
            "instructions": login.get("instructions", []),
        }
    return out


# API-key-only providers (no OAuth available). Others use OAuth via _LOGIN_FLAGS.
PROVIDER_LOGIN_CONFIG: dict[str, dict[str, Any]] = _build_provider_login_config()


def _has_provider_credentials(config: dict[str, Any], provider: str) -> bool:
    """Check if provider already has credentials in cliproxy config."""
    compat = config.get("openai-compatibility")
    if not isinstance(compat, list):
        return False
    for entry in compat:
        if not isinstance(entry, dict):
            continue
        if entry.get("name", "").lower() == provider.lower():
            keys = entry.get("api-key-entries") or entry.get("api-key")
            if keys and isinstance(keys, list) and keys:
                return any((k.get("api-key") or "").strip() for k in keys if isinstance(k, dict))
            if isinstance(keys, str) and keys.strip():
                return True
    return False


# OAuth credential file prefixes in ~/.cli-proxy-api (CLIProxyAPIPlus naming)
_OAUTH_AUTH_PREFIXES: dict[str, list[str]] = {
    "claude": ["claude-"],
    "codex": ["codex-"],
    "gemini": ["gemini-"],  # also *@*-*.json (email-projectId) checked below
    "antigravity": ["antigravity-"],
    "copilot": ["github-", "copilot-"],
    "kilo": ["kilo-"],
    "glm": ["iflow-"],
    "iflow": ["iflow-"],
    "kiro": ["kiro-"],
    "roo": ["roo-"],
    "qwen": ["qwen-"],
    "kimi": ["kimi-"],
}


def _has_oauth_credentials(settings: ThegentSettings, provider: str) -> bool:
    """Preflight: check if OAuth provider already has credentials in auth dir."""
    provider_lower = provider.lower()
    prefixes = _OAUTH_AUTH_PREFIXES.get(provider_lower)
    if not prefixes:
        return False
    auth_dir = settings.cliproxy_auth_dir.expanduser().resolve()
    if not auth_dir.exists():
        return False
    for f in auth_dir.iterdir():
        if not f.is_file() or not f.suffix == ".json":
            continue
        name = f.name
        for prefix in prefixes:
            if name.startswith(prefix):
                return True
        # Gemini: email-projectId.json (e.g. user@gmail.com-projectId.json)
        if provider_lower == "gemini" and "@" in name and name.endswith(".json"):
            return True
    return False


def _inject_api_key_into_cliproxy(config: dict[str, Any], provider: str, api_key: str, cfg: dict[str, Any]) -> None:
    """Add or update openai-compatibility entry with the given API key.
    Uses provider_definitions.json for model aliases when available."""
    compat = config.get("openai-compatibility")
    if not isinstance(compat, list):
        compat = []
        config["openai-compatibility"] = compat

    compat[:] = [c for c in compat if isinstance(c, dict) and c.get("name", "").lower() != provider.lower()]

    base_url = cfg.get("base_url", "").rstrip("/")
    model = cfg.get("model", cfg.get("display_name", provider))
    entries = [{"api-key": api_key}]

    defs_ = _get_provider_definitions()
    provider_def = defs_.get(provider) if isinstance(defs_.get(provider), dict) else {}
    extra_aliases = provider_def.get("extra_aliases", ["glm-5"] if provider in ("glm", "kilo") else [])

    models = [*_get_claude_aliases(model)]
    for alias in extra_aliases:
        models.append({"name": model, "alias": alias})

    compat.append(
        {
            "name": provider,
            "base-url": base_url,
            "api-key-entries": entries,
            "models": models,
        }
    )


def _inject_cursor_into_cliproxy(config: dict[str, Any], settings: ThegentSettings) -> None:
    """Inject cursor block when THGENT_CURSOR_API_URL and token are set (for dex composer).
    Skips if cursor block already exists (user config takes precedence).
    Aligns with CLIProxyAPIPlus CursorKey schema (internal/config/config.go):
    - token-file: when token is sk-... from cursor-api /build-key (direct use)
    - auth-token: when token is AUTH_TOKEN for zero-action (IDE + /tokens/add)
    """
    if "cursor" in config and config["cursor"]:
        return
    url = os.environ.get("THGENT_CURSOR_API_URL") or settings.cursor_api_url
    token = (os.environ.get("THGENT_CURSOR_API_TOKEN") or settings.cursor_api_token or "").strip()
    if not url or not token:
        return
    cursor_api_url = url.rstrip("/")
    if not cursor_api_url:
        cursor_api_url = "http://127.0.0.1:3000"

    # CLIProxyAPIPlus CursorKey: token-file (sk-... from /build-key) or auth-token (zero-action)
    entry: dict[str, Any] = {"cursor-api-url": cursor_api_url}
    if token.startswith("sk-"):
        # token-file flow: write sk-... to auth dir, proxy reads directly
        auth_dir = settings.cliproxy_auth_dir.expanduser().resolve()
        auth_dir.mkdir(parents=True, exist_ok=True)
        token_file = auth_dir / "cursor-session-token.txt"
        try:
            token_file.write_text(token, encoding="utf-8")
            token_file.chmod(0o600)
        except OSError:
            return
        entry["token-file"] = str(token_file)
    else:
        # auth-token flow: zero-action (IDE + /tokens/add)
        entry["auth-token"] = token

    config["cursor"] = [entry]


def _ensure_config(settings: ThegentSettings) -> Path:
    """Ensure cliproxy config exists; create minimal YAML if missing."""
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
    
    # WP-Y16: Ensure model aliases are up to date for existing providers
    if "openai-compatibility" in config:
        for p in config["openai-compatibility"]:
            # Try to get underlying model from 'model' or first item in 'models'
            model = p.get("model")
            if not model and p.get("models"):
                model = p["models"][0].get("name")
            if model:
                p["models"] = _get_claude_aliases(model)

    _inject_cursor_into_cliproxy(config, settings)

    yaml = _get_yaml()
    config_path.write_text(str(yaml.dump(config, default_flow_style=False, sort_keys=False)))
    return config_path


def _is_proxy_reachable(base_url: str) -> bool:
    """Check if proxy is reachable (GET /v1/models or /models)."""
    # If base_url already ends in /v1, don't duplicate it.
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        paths = ("/models", "/")
    else:
        paths = ("/v1/models", "/models", "/")
        
    for path in paths:
        try:
            resp = httpx.get(
                f"{base}{path}",
                headers={"Authorization": "Bearer sk-dummy"},
                timeout=_PROXY_CHECK_TIMEOUT,
            )
            if resp.is_success:
                return True
        except Exception:
            continue
    return False


def _adapter_script_path() -> Path | None:
    """Path to start_proxy_with_adapter.py if available (when running from source)."""
    try:
        import thegent
        root = Path(thegent.__file__).resolve().parent.parent.parent
        script = root / "scripts" / "start_proxy_with_adapter.py"
        return script if script.exists() else None
    except Exception:
        return None


def _start_proxy_and_wait(
    binary: str, config_path: Path, base_url: str, settings: ThegentSettings, use_adapter: bool = False
) -> subprocess.Popen[bytes]:
    """Start proxy process and wait for readiness. Returns proc or raises."""
    script = _adapter_script_path()
    if use_adapter and script is not None:
        import sys
        env = os.environ.copy()
        env.setdefault("THGENT_CLIPROXY_PORT", str(settings.cliproxy_port))
        
        # Capture stderr if debug is enabled to help diagnose startup failures
        stderr_target = None
        if os.environ.get("THGENT_DEBUG") == "1":
            stderr_target = subprocess.PIPE

        proc = subprocess.Popen(
            [sys.executable, str(script)],
            cwd=str(script.parent.parent),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=stderr_target,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            text=True if stderr_target else False,
        )
    else:
        args = [binary, "-config", str(config_path)]
        if os.environ.get("THGENT_DEBUG") == "1":
            args.append("-debug")
        
        stderr_target = None
        if os.environ.get("THGENT_DEBUG") == "1":
            stderr_target = subprocess.PIPE

        proc = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=stderr_target,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            env=os.environ.copy(),
            text=True if stderr_target else False,
        )
    
    # Ready timeout: adapter script has its own internal timeouts, so we should be slightly longer
    wait_iterations = _PROXY_READY_TIMEOUT * 4  # ~10s total
    for _ in range(wait_iterations):
        time.sleep(0.5)
        if _is_proxy_reachable(base_url):
            return proc
        if proc.poll() is not None:
            err_msg = ""
            if stderr_target:
                _, err = proc.communicate()
                err_msg = f"\nStderr: {err}"
            
            hint = ""
            if use_adapter:
                hint = "\nHint: Try THGENT_CLIPROXY_ADAPTER=0 for direct proxy without adapter."
            
            raise RuntimeError(
                f"CLIProxyAPIPlus exited with code {proc.returncode}. "
                f"Check config at {config_path}.{err_msg}{hint}\n"
                "Run with THGENT_DEBUG=1 for detailed logs."
            )
    
    proc.kill()
    raise RuntimeError(
        f"CLIProxyAPIPlus did not become ready within {wait_iterations * 0.5}s. "
        f"Port {settings.cliproxy_port} may be in use."
    )


def ensure_proxy_running(settings: ThegentSettings) -> str:
    """
    Ensure CLIProxyAPIPlus is running. Start if not reachable.
    Returns base_url (e.g. http://127.0.0.1:8317/v1).
    Supports adapter (Responses API) if THGENT_CLIPROXY_ADAPTER=1.
    """
    port = settings.cliproxy_port
    use_adapter = (
        os.environ.get("THGENT_CLIPROXY_ADAPTER") == "1"
        or (os.environ.get("THGENT_CLIPROXY_ADAPTER") is None and settings.cliproxy_adapter)
    )
    base_url = f"http://127.0.0.1:{port}/v1"
    if _is_proxy_reachable(base_url):
        return base_url

    if use_adapter:
        # Try to start using the adapter script
        script_path = Path(__file__).resolve().parents[3] / "scripts" / "start_proxy_with_adapter.py"
        if script_path.exists():
            import subprocess
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])
            env.setdefault("THGENT_CLIPROXY_ADAPTER", "1")
            subprocess.Popen(
                [sys.executable, str(script_path)],
                env=env,
                cwd=str(script_path.parent.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            # Wait for adapter
            for _ in range(_PROXY_READY_TIMEOUT * 4):  # Increase wait for adapter
                time.sleep(0.5)
                if _is_proxy_reachable(base_url):
                    return base_url
            # Fallback to direct binary if adapter fails to start

    binary = _resolve_binary(settings)
    if not _binary_available(binary):
        raise FileNotFoundError(_CLIPROXY_NOT_FOUND_MSG)

    config_path = _ensure_config(settings)
    
    # Fallback path: if we tried adapter and it failed, _start_proxy_and_wait will try direct
    # unless we explicitly tell it to use adapter. 
    # Here we call it without use_adapter=True to ensure a working direct proxy fallback.
    _start_proxy_and_wait(binary, config_path, base_url, settings, use_adapter=False)
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


def fetch_provider_metrics(settings: ThegentSettings | None = None) -> dict[str, dict] | None:
    """Fetch per-provider metrics from CLIProxyAPIPlus GET /v1/metrics/providers."""
    settings = settings or ThegentSettings()
    url = f"http://127.0.0.1:{settings.cliproxy_port}/v1/metrics/providers"
    try:
        resp = httpx.get(url, timeout=2)
        if not resp.is_success:
            return None
        data = resp.json()
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def kill_proxy(settings: ThegentSettings) -> bool:
    """
    Kill proxy process listening on cliproxy_port. Returns True if a process was killed.
    Uses lsof to find PIDs by port; works regardless of how proxy was started.
    """
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{settings.cliproxy_port}"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return False
        pids = [p.strip() for p in result.stdout.strip().split("\n") if p.strip()]
        for pid in pids:
            subprocess.run(["kill", "-9", pid], capture_output=True, timeout=2, check=False)
        return bool(pids)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


# --- LaunchAgent service (macOS) ---

_PROXY_PLIST_LABEL = "com.thegent.cliproxy"


def _proxy_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{_PROXY_PLIST_LABEL}.plist"


def proxy_service_install(settings: ThegentSettings) -> tuple[bool, str]:
    """Install proxy as launchd service (macOS). Runs at login, restarts on crash."""
    import platform

    if platform.system() != "Darwin":
        return False, "launchd only supported on macOS. Use systemd on Linux."
    binary = _resolve_binary(settings)
    if not _binary_available(binary):
        return False, _CLIPROXY_NOT_FOUND_MSG
    config_path = _ensure_config(settings)
    plist_path = _proxy_plist_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    log_dir = Path.home() / ".cache" / "thegent"
    log_dir.mkdir(parents=True, exist_ok=True)
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>Label</key>
<string>{_PROXY_PLIST_LABEL}</string>
<key>ProgramArguments</key>
<array>
<string>{binary}</string>
<string>-config</string>
<string>{config_path}</string>
</array>
<key>RunAtLoad</key>
<true/>
<key>KeepAlive</key>
<true/>
<key>StandardOutPath</key>
<string>{log_dir}/cliproxy.log</string>
<key>StandardErrorPath</key>
<string>{log_dir}/cliproxy.err</string>
</dict>
</plist>
"""
    plist_path.write_text(plist)
    return True, f"Installed to {plist_path}. Run: thegent cliproxy service start"


def proxy_service_uninstall() -> tuple[bool, str]:
    """Remove proxy launchd service."""
    import platform

    if platform.system() != "Darwin":
        return False, "launchd only on macOS"
    plist_path = _proxy_plist_path()
    subprocess.run(["launchctl", "unload", str(plist_path)], check=False, capture_output=True)
    if plist_path.exists():
        plist_path.unlink()
    return True, "Uninstalled"


def proxy_service_start() -> tuple[bool, str]:
    """Start proxy launchd service."""
    import platform

    if platform.system() != "Darwin":
        return False, "launchd only on macOS"
    plist_path = _proxy_plist_path()
    if not plist_path.exists():
        return False, "Service not installed. Run: thegent cliproxy service install"
    subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True, check=True)
    return True, "Started"


def proxy_service_stop() -> tuple[bool, str]:
    """Stop proxy launchd service."""
    import platform

    if platform.system() != "Darwin":
        return False, "launchd only on macOS"
    plist_path = _proxy_plist_path()
    if not plist_path.exists():
        return False, "Service not installed"
    subprocess.run(["launchctl", "unload", str(plist_path)], check=False, capture_output=True)
    return True, "Stopped"


def run_login_unified(settings: ThegentSettings, provider: str, prompt_func=None, skip_if_configured: bool = True) -> int:
    """
    Unified login: open URL + prompt for API key. Preflight check for existing credentials.
    Returns 0 on success, 1 on skip/cancel, 2 on error.
    """
    provider_lower = provider.lower()
    if provider_lower not in PROVIDER_LOGIN_CONFIG:
        raise ValueError(
            f"Unknown provider: {provider}. Supported: {', '.join(sorted(PROVIDER_LOGIN_CONFIG))}"
        )

    config_path = _ensure_config(settings)
    raw = yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
    config: dict[str, Any] = dict(raw) if isinstance(raw, dict) else {}

    cfg = PROVIDER_LOGIN_CONFIG[provider_lower]
    if skip_if_configured and _has_provider_credentials(config, provider_lower):
        print(f"  {cfg.get('display_name', provider)} already configured. Run with --force to re-enter key.")
        return 0  # Already configured

    url = cfg.get("url", "")
    display_name = cfg.get("display_name", provider)
    instructions = cfg.get("instructions", [])

    # Print instructions
    for line in instructions:
        print(f"  {line}")
    print(f"  Opening: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        print(f"  Could not open browser. Visit: {url}")

    prompt_fn = prompt_func or input
    key = prompt_fn(f"Enter {display_name} API key (or press Enter to skip): ").strip()
    if not key:
        return 1

    _inject_api_key_into_cliproxy(config, provider_lower, key, cfg)
    yaml = _get_yaml()
    config_path.write_text(str(yaml.dump(config, default_flow_style=False, sort_keys=False)))
    print(f"  Saved API key for {display_name}.")

    # WP-Y13: Auto-restart proxy to "hot-reload" the new API key
    if kill_proxy(settings):
        print("  Proxy was running; restarting to pick up new key...")
        try:
            base_url = ensure_proxy_running(settings)
            print(f"  Proxy restarted successfully at {base_url}")
        except Exception as e:
            print(f"  Warning: Proxy restart failed: {e}")
            print(f"  Manually start with: thegent cliproxy start")
    else:
        print("  Proxy is not currently running. Use 'thegent cliproxy start' to start it.")

    return 0


# CLIProxyAPIPlus -login flags (OAuth providers). Prefer OAuth over API key where available.
_LOGIN_FLAGS: dict[str, str] = {
    "claude": "-claude-login",
    "codex": "-codex-login",
    "gemini": "-login",
    "qwen": "-qwen-login",
    "glm": "-iflow-login",
    "iflow": "-iflow-login",
    "iflow-cookie": "-iflow-cookie",
    "kimi": "-kimi-login",
    "roo": "-roo-login",
    "kilo": "-kilo-login",
    "copilot": "-github-copilot-login",
    "antigravity": "-antigravity-login",
    "kiro": "-kiro-login",
    "kiro-google": "-kiro-google-login",
    "kiro-aws": "-kiro-aws-login",
    "kiro-aws-authcode": "-kiro-aws-authcode",
    "kiro-import": "-kiro-import",
}


def run_login(settings: ThegentSettings, provider: str, prompt_func=None, force: bool = False) -> int:
    """
    Run login for provider. Returns exit code.
    Prefers OAuth via CLIProxy for providers that support it.
    Falls back to API-key flow for providers without OAuth (minimax, nim).
    Preflight: skips OAuth flow if already configured (unless force=True).
    """
    provider_lower = provider.lower()

    # Prefer OAuth when available
    if provider_lower in _LOGIN_FLAGS:
        # Preflight: skip if already configured (unless force)
        if not force and _has_oauth_credentials(settings, provider_lower):
            display = PROVIDER_LOGIN_CONFIG.get(provider_lower, {}).get("display_name", provider_lower.replace("-", " ").title())
            print(f"  {display} already configured. Run with --force to re-authenticate.")
            return 0
        binary = _resolve_binary(settings)
        if not _binary_available(binary):
            raise FileNotFoundError(_CLIPROXY_NOT_FOUND_MSG)
        config_path = _ensure_config(settings)
        flag = _LOGIN_FLAGS[provider_lower]
        proc = subprocess.run(
            [binary, "-config", str(config_path), flag],
            check=False,
            env=os.environ.copy(),
        )
        return proc.returncode

    # API-key-only providers
    if provider_lower in PROVIDER_LOGIN_CONFIG:
        return run_login_unified(
            settings, provider_lower, prompt_func=prompt_func, skip_if_configured=not force
        )

    raise ValueError(
        f"Unknown provider: {provider}. Supported: "
        f"{', '.join(sorted(set(PROVIDER_LOGIN_CONFIG) | set(_LOGIN_FLAGS)))}"
    )
