"""CLIProxyAPIPlus lifecycle: config generation and proxy process management.

DEPRECATED: This module is a thin shim for backward compatibility.
New code should use the decomposed modules:
- thegent.use_cases.manage_cliproxy — Business logic (provider config, credentials)
- thegent.use_cases.manage_cliproxy_runtime — Process management (binary resolution,
  reachability, subprocess startup, port-based termination)
- thegent.use_cases.manage_cliproxy_metrics — Per-provider metrics + status memo
- thegent.ports.driven.cliproxy — Port interfaces
- thegent.adapters.driven.cliproxy_http — HTTP client adapter
"""CLIProxyAPIPlus lifecycle manager.

Re-exports the public process management surface from
:mod:`thegent.use_cases.manage_cliproxy_runtime` and keeps the legacy
config / ensure_proxy_running implementation here for back-compat.

See `manage_cliproxy_runtime` for the binary resolution, reachability
checks, adapter detection, and process orchestration primitives.

L1 Architecture guardrail (see `tests/unit/architecture/`): keep this
file under 350 lines and CC ≤ 15 per function. Configuration patching
and process orchestration now live in focused use_case modules.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings
from thegent.use_cases.manage_cliproxy_runtime import (
    _adapter_script_path,
    _binary_available,
    _is_adapter_fallback_allowed,
    _is_adapter_running,
    _is_proxy_reachable,
    _resolve_binary,
    _start_proxy_and_wait,
    _start_raw_proxy,
    ensure_proxy_running,
)

__all__ = [
    "ensure_proxy_running",
    "_resolve_binary",
    "_binary_available",
    "_is_proxy_reachable",
    "_is_adapter_running",
    "_adapter_script_path",
    "_is_adapter_fallback_allowed",
    "_start_raw_proxy",
    "_start_proxy_and_wait",
]

# Re-exported below: ensure_responses_adapter_config, _ensure_config,
# _patch_provider_aliases, _mask_sensitive, _safe_get_api_key, model_aliases.
# These remain in this module for backward-compat with downstream callers.
# Back-compat re-exports from the runtime cluster. The un-prefixed names
# are the public API of ``manage_cliproxy_runtime``; the underscore
# aliases preserve the legacy convention used by tests and in-package
# callers.
from thegent.use_cases.manage_cliproxy_runtime import (  # noqa: F401 — re-export
    _CLIPROXY_NOT_FOUND_MSG,
    _PROXY_CHECK_TIMEOUT,
    _PROXY_READY_TIMEOUT,
    _adapter_script_path,
    _binary_available,
    _is_adapter_fallback_allowed,
    _is_adapter_running,
    _is_proxy_reachable,
    _resolve_binary,
    _start_proxy_and_wait,
    _start_raw_proxy,
    adapter_script_path,
    binary_available,
    ensure_proxy_running,
    is_adapter_fallback_allowed,
    is_adapter_running,
    is_proxy_reachable,
    kill_proxy,
    resolve_binary,
    start_proxy_managed,
)

# Import decomposed modules
from thegent.use_cases.manage_cliproxy import (
    ProviderConfigManager,
    CredentialsResolver,
    ProxyHealthChecker,
)

_LOG = logging.getLogger(__name__)

_CLIPROXY_DATA_DIR = Path(__file__).parent / "cliproxy_data"

# _PROXY_READY_TIMEOUT is re-exported from manage_cliproxy_runtime above.
# The legacy module-level constant is retained as an alias for any test that
# patches ``thegent.agents.cliproxy_manager._PROXY_READY_TIMEOUT``.
_LAST_PROVIDER_METRICS_STATUS: dict[str, Any] = {"status": "not_requested", "metrics": None}


class ProviderDefinitionsLoadError(ValueError):
    """Typed validation error for provider definition JSON loading."""

    def __init__(self, name: str, reason: str, *, path: Path, cause: Exception | None = None) -> None:
        self.name = name
        self.reason = reason
        self.path = path
        self.cause = cause
        message = f"{name}: {reason} ({path})"
        super().__init__(message)


def _load_json(name: str) -> dict[str, Any]:
    """Load and validate JSON object from cliproxy_data.

    Raises ProviderDefinitionsLoadError on missing file, invalid JSON, I/O errors,
    and non-object JSON payloads.
    """
    path = _CLIPROXY_DATA_DIR / name
    if not path.exists():
        raise ProviderDefinitionsLoadError(name, "missing_file", path=path)
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ProviderDefinitionsLoadError(name, "invalid_json", path=path, cause=exc) from exc
    except OSError as exc:
        raise ProviderDefinitionsLoadError(name, "read_error", path=path, cause=exc) from exc

    if not isinstance(data, dict):
        raise ProviderDefinitionsLoadError(name, "invalid_shape", path=path)
    return data


def _get_provider_definitions() -> dict[str, Any]:
    """Load provider definitions from internal JSON."""
    try:
        return _load_json("provider_definitions.json")
    except ProviderDefinitionsLoadError as exc:
        _LOG.warning(
            "provider_definitions_load_failed",
            extra={
                "file": exc.name,
                "reason": exc.reason,
                "path": str(exc.path),
                "cause": str(exc.cause) if exc.cause else "",
            },
        )
        return {}


_PROXY_CHECK_TIMEOUT = 2


def _get_claude_aliases(model: str) -> list[dict[str, str]]:
    """Get standard aliases for a given underlying model.

    Per z.ai and MiniMax docs: provider-native names (MiniMax-M2.5, glm-5, GLM-5)
    work without any Claude ID mapping. Include provider name as alias.
    """
    common = [
        "sonnet",
        "haiku",
        "opus",
        "claude-sonnet-4.5",
        "claude-haiku-4.5",
        "claude-opus-4.6",
        "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "composer-1.5",
        "composer-1.5-high",
        "composer-1.5-spark",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
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

# Provider -> (base_url_patterns, model_patterns) for factory config lookup
_FACTORY_PROVIDER_PATTERNS: dict[str, tuple[list[str], list[str]]] = {
    "minimax": (["minimax"], ["minimax"]),
    "nim": (["nvidia"], ["nvidia", "nim"]),
    "openrouter": (["openrouter"], ["openrouter"]),
    "zen": (["opencode"], ["opencode", "zen"]),
    "qwen": (["dashscope", "aliyuncs"], ["qwen"]),
    "roo": (["roo.ai"], ["roo"]),
    "kimi": (["moonshot.cn"], ["kimi"]),
}

_DUMMY_KEYS = frozenset({"dummy-not-used", "dummy", ""})


def _get_factory_api_key(provider: str) -> tuple[str | None, str]:
    """Look up API key in ~/.factory/config.json and ~/.factory/settings.json.
    Returns (api_key, source_path) or (None, ""). Skips dummy/empty keys."""
    provider_lower = provider.lower()
    patterns = _FACTORY_PROVIDER_PATTERNS.get(provider_lower)
    if not patterns:
        return None, ""

    base_patterns, model_patterns = patterns

    def _matches(entry: dict[str, Any], base_key: str, model_key: str, api_key: str) -> bool:
        base_val = (entry.get(base_key) or "").lower()
        model_val = (entry.get(model_key) or "").lower()
        key_val = (entry.get(api_key) or "").strip()
        if not key_val or key_val.lower() in _DUMMY_KEYS:
            return False
        return any(p in base_val for p in base_patterns) or any(p in model_val for p in model_patterns)

    factory_dir = Path.home() / ".factory"
    for name, base_key, model_key, api_key in [
        ("config.json", "base_url", "model", "api_key"),
        ("settings.json", "baseUrl", "model", "apiKey"),
    ]:
        path = factory_dir / name
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        models_key = "custom_models" if name == "config.json" else "customModels"
        entries = data.get(models_key) if isinstance(data, dict) else []
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if _matches(entry, base_key, model_key, api_key):
                key = (entry.get(api_key) or "").strip()
                if key and key.lower() not in _DUMMY_KEYS:
                    return key, str(path)
    return None, ""


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
    # Kiro: also check ~/.kiro/kiro-auth-token.json (from Kiro IDE or kiro-import)
    if provider_lower == "kiro":
        kiro_token = Path("~/.kiro/kiro-auth-token.json").expanduser().resolve()
        if kiro_token.exists():
            return True
    auth_dir = settings.cliproxy_auth_dir.expanduser().resolve()
    if not auth_dir.exists():
        return False
    for f in auth_dir.iterdir():
        if not f.is_file() or f.suffix != ".json":
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
    Uses provider_definitions.json for model aliases when available.
    Claude and Codex are OAuth-only; no-op for them."""
    if provider.lower() in OAUTH_ONLY_PROVIDERS:
        return
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

    # For provider-native models (MiniMax-M2.5, GLM-5), use provider-specific aliases
    if provider.lower() == "minimax" and "MiniMax" in model:
        # MiniMax uses provider-native name: MiniMax-M2.5
        models = [
            {"name": "MiniMax-M2.5", "alias": "MiniMax-M2.5"},
            {"name": "MiniMax-M2.5", "alias": "minimax-m2.5"},
        ]
    elif provider.lower() in ("glm", "kilo") and ("GLM" in model or "glm" in model.lower()):
        # GLM/Kilo use provider-native names
        models = [
            {"name": model, "alias": model},
            {"name": model, "alias": model.lower()},
        ]
        for alias in extra_aliases:
            models.append({"name": model, "alias": alias})
    else:
        # Claude-compatible models use Claude aliases
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
    if config.get("cursor"):
        return
    url = settings.cursor_api_url
    token = (settings.cursor_api_token or "").strip()
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


def _inject_kiro_into_cliproxy(config: dict[str, Any], settings: ThegentSettings) -> None:
    """Inject kiro block when ~/.kiro/kiro-auth-token.json exists (from Kiro IDE or kiro-import).
    Skips if kiro block already exists. Ensures token persists across config rewrites."""
    if config.get("kiro"):
        return
    kiro_token = Path("~/.kiro/kiro-auth-token.json").expanduser().resolve()
    if not kiro_token.exists():
        return
    config["kiro"] = [{"token-file": str(kiro_token)}]


def _ensure_config(settings: ThegentSettings) -> Path:
    """Ensure cliproxy config exists; create minimal YAML if missing."""
    config_path = settings.cliproxy_config_path.expanduser().resolve()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    auth_dir = settings.cliproxy_auth_dir.expanduser().resolve()
    auth_dir.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        try:
            raw = yaml_load(config_path)
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
            # Fix MiniMax base-url: api.minimax.chat -> api.minimax.io (correct international API)
            name = (p.get("name") or "").lower()
            if name == "minimax":
                base = (p.get("base-url") or "").strip()
                if "api.minimax.chat" in base:
                    p["base-url"] = base.replace("api.minimax.chat", "api.minimax.io")
                # Ensure MiniMax-M2.5 model is properly configured with aliases
                models_list = p.get("models", [])
                if not any(m.get("name") == "MiniMax-M2.5" for m in models_list):
                    models_list.append({"name": "MiniMax-M2.5", "alias": "MiniMax-M2.5"})
                    models_list.append({"name": "MiniMax-M2.5", "alias": "minimax-m2.5"})
                    p["models"] = models_list
            elif name == "glm":
                # Ensure GLM-5 model is properly configured with aliases
                models_list = p.get("models", [])
                if not any(m.get("name") == "GLM-5" or m.get("alias") == "glm-5" for m in models_list):
                    models_list.append({"name": "GLM-5", "alias": "GLM-5"})
                    models_list.append({"name": "GLM-5", "alias": "glm-5"})
                    models_list.append({"name": "GLM-5", "alias": "z-ai/glm-5"})
                    p["models"] = models_list
            elif name == "kilo":
                # Ensure kilo-default model is properly configured
                models_list = p.get("models", [])
                if not any(m.get("alias") == "kilo-default" for m in models_list):
                    model_name = p.get("model") or "kilo-default"
                    models_list.append({"name": model_name, "alias": "kilo-default"})
                    p["models"] = models_list
            elif name == "roo":
                # Ensure roo-default model is properly configured
                models_list = p.get("models", [])
                if not any(m.get("alias") == "roo-default" for m in models_list):
                    model_name = p.get("model") or "roo-default"
                    models_list.append({"name": model_name, "alias": "roo-default"})
                    p["models"] = models_list
            # Try to get underlying model from 'model' or first item in 'models'
            model = p.get("model")
            if not model and p.get("models"):
                model = p["models"][0].get("name")
            if model:
                # Only use Claude aliases for Claude-compatible models
                # For provider-native models (MiniMax-M2.5, GLM-5), use provider-specific aliases
                if name == "minimax" and "MiniMax" in model:
                    # MiniMax models use provider-native names
                    if not p.get("models"):
                        p["models"] = [
                            {"name": "MiniMax-M2.5", "alias": "MiniMax-M2.5"},
                            {"name": "MiniMax-M2.5", "alias": "minimax-m2.5"},
                        ]
                elif name in ("glm", "kilo") and ("GLM" in model or "glm" in model.lower()):
                    # GLM models use provider-native names
                    if not p.get("models"):
                        p["models"] = [
                            {"name": model, "alias": model},
                            {"name": model, "alias": model.lower()},
                        ]
                else:
                    p["models"] = _get_claude_aliases(model)

    _inject_cursor_into_cliproxy(config, settings)
    _inject_kiro_into_cliproxy(config, settings)

    config_path.write_text(yaml_dumps(config))
    return config_path


def ensure_proxy_running(settings: ThegentSettings) -> str:
    """
    Ensure CLIProxyAPIPlus is running. Start if not reachable.
    Returns base_url (e.g. http://127.0.0.1:8317/v1).
    Supports adapter (Responses API) if THGENT_CLIPROXY_ADAPTER=1.

    Uses shared MCP server (system-wide) if available.
    """
    port = settings.cliproxy_port
    use_adapter = settings.cliproxy_adapter and os.environ.get("THGENT_TESTING") != "1"
    fallback_allowed = _is_adapter_fallback_allowed()
    base_url = f"http://127.0.0.1:{port}/v1"
    if _is_proxy_reachable(base_url):
        # When adapter is requested, enforce adapter semantics and fail closed.
        if use_adapter:
            if _is_adapter_running(base_url):
                return base_url
            kill_proxy(settings)
        else:
            return base_url

    binary = _resolve_binary(settings)
    if not _binary_available(binary):
        raise FileNotFoundError(_CLIPROXY_NOT_FOUND_MSG)

    if use_adapter:
        # Start using the adapter script; no silent fallback to raw proxy.
        from thegent.utils import get_resource_path

        script_path = get_resource_path("scripts/start_proxy_with_adapter.py")
        if not script_path.exists():
            if fallback_allowed:
                _LOG.warning(
                    "CLIProxy adapter launcher missing; using raw proxy mode for compatibility. "
                    "Set THGENT_CLIPROXY_STRICT_ADAPTER=1 to fail hard."
                )
                return _start_raw_proxy(settings, base_url)
            raise RuntimeError(
                "CLIProxy adapter is enabled but adapter launcher is missing. "
                "Expected scripts/start_proxy_with_adapter.py in thegent resources."
            )

        import subprocess

        env = os.environ.copy()
        # If we're installed, we might not need to set PYTHONPATH
        # but for dev mode it's crucial.
        from thegent.utils import is_dev_mode

        if is_dev_mode():
            env["PYTHONPATH"] = str(script_path.parents[1] / "src")

        env.setdefault("THGENT_CLIPROXY_ADAPTER", "1")
        subprocess.Popen(
            [sys.executable, str(script_path)],
            env=env,
            cwd=str(script_path.parents[1]),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        # Wait for adapter and verify it's actually the adapter surface.
        for _ in range(_PROXY_READY_TIMEOUT * 4):
            time.sleep(0.5)
            if _is_proxy_reachable(base_url) and _is_adapter_running(base_url):
                return base_url

        if fallback_allowed:
            _LOG.warning(
                "CLIProxy adapter failed to expose /v1/responses; using raw proxy mode for compatibility. "
                "Set THGENT_CLIPROXY_STRICT_ADAPTER=1 to fail hard."
            )
            return _start_raw_proxy(settings, base_url)
        raise RuntimeError(
            f"CLIProxy adapter is enabled, but /v1/responses adapter surface did not become ready at {base_url}."
        )

    config_path = _ensure_config(settings)

    _start_proxy_and_wait(binary, config_path, base_url, settings, use_adapter=False)
    return base_url


def start_proxy_managed(settings: ThegentSettings) -> tuple[subprocess.Popen[bytes] | None, str]:
    """
    Start proxy and return (proc, base_url) for lifecycle management.
    Caller must terminate proc on shutdown. Skips if proxy already reachable (proc=None).
    Uses adapter (Responses API + WebSocket /v1/responses) when THGENT_CLIPROXY_ADAPTER=1.
    """
    base_url = f"http://127.0.0.1:{settings.cliproxy_port}/v1"
    if _is_proxy_reachable(base_url):
        if settings.cliproxy_adapter and not _is_adapter_running(base_url):
            kill_proxy(settings)
        else:
            return (None, base_url)

    binary = _resolve_binary(settings)
    if not _binary_available(binary):
        raise FileNotFoundError(_CLIPROXY_NOT_FOUND_MSG)

    config_path = _ensure_config(settings)
    use_adapter = settings.cliproxy_adapter
    strict_adapter = os.environ.get("THGENT_CLIPROXY_STRICT_ADAPTER", "").lower() in {"1", "true", "yes", "on"}
    try:
        proc = _start_proxy_and_wait(binary, config_path, base_url, settings, use_adapter=use_adapter)
    except RuntimeError as exc:
        if use_adapter and not strict_adapter:
            _LOG.warning("Adapter startup failed; falling back to raw proxy mode: %s", exc)
            kill_proxy(settings)
            proc = _start_proxy_and_wait(binary, config_path, base_url, settings, use_adapter=False)
        else:
            raise
    return (proc, base_url)


def fetch_provider_metrics(settings: ThegentSettings | None = None) -> dict[str, dict] | None:
    """Fetch per-provider metrics from CLIProxyAPIPlus GET /v1/metrics/providers."""
    global _LAST_PROVIDER_METRICS_STATUS  # noqa: PLW0603
    settings = settings or ThegentSettings()
    url = f"http://127.0.0.1:{settings.cliproxy_port}/v1/metrics/providers"
    try:
        resp = httpx.get(url, timeout=2)
    except httpx.TimeoutException as exc:
        _LAST_PROVIDER_METRICS_STATUS = {
            "status": "timeout",
            "metrics": None,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }
        return None
    except httpx.NetworkError as exc:
        _LAST_PROVIDER_METRICS_STATUS = {
            "status": "network_error",
            "metrics": None,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }
        return None
    except httpx.HTTPError as exc:
        _LAST_PROVIDER_METRICS_STATUS = {
            "status": "http_error",
            "metrics": None,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }
        return None

    if not resp.is_success:
        _LAST_PROVIDER_METRICS_STATUS = {
            "status": "endpoint_unavailable",
            "metrics": None,
            "http_status": resp.status_code,
        }
        return None

    try:
        data = resp.json()
    except json.JSONDecodeError as exc:
        _LAST_PROVIDER_METRICS_STATUS = {
            "status": "invalid_json",
            "metrics": None,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }
        return None

    if isinstance(data, dict):
        _LAST_PROVIDER_METRICS_STATUS = {
            "status": "ok",
            "metrics": data,
            "provider_count": len(data),
        }
        return data

    _LAST_PROVIDER_METRICS_STATUS = {
        "status": "invalid_payload_shape",
        "metrics": None,
        "payload_type": type(data).__name__,
    }
    return None


def get_last_provider_metrics_status() -> dict[str, Any]:
    """Return status metadata from the latest provider metrics fetch."""
    return dict(_LAST_PROVIDER_METRICS_STATUS)


def kill_proxy(settings: ThegentSettings) -> bool:
    """
    Kill proxy process listening on cliproxy_port. Returns True if a process was killed.
    Uses lsof to find PIDs by port; works regardless of how proxy was started.
    """
    try:
        result = run_subprocess_optimized(
            ["lsof", "-ti", f":{settings.cliproxy_port}"],
            capture_output=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0 or not result.stdout:
            return False
        stdout_text = (
            result.stdout if isinstance(result.stdout, str) else result.stdout.decode("utf-8", errors="replace")
        )
        if not stdout_text.strip():
            return False
        pids = [p.strip() for p in stdout_text.strip().split("\n") if p.strip()]
        for pid in pids:
            run_subprocess_optimized(["kill", "-9", pid], capture_output=True, timeout=2, check=False)
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
    run_subprocess_optimized(["launchctl", "unload", str(plist_path)], check=False, capture_output=True)
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
    run_subprocess_optimized(["launchctl", "load", str(plist_path)], capture_output=True, check=True)
    return True, "Started"


def proxy_service_stop() -> tuple[bool, str]:
    """Stop proxy launchd service."""
    import platform

    if platform.system() != "Darwin":
        return False, "launchd only on macOS"
    plist_path = _proxy_plist_path()
    if not plist_path.exists():
        return False, "Service not installed"
    run_subprocess_optimized(["launchctl", "unload", str(plist_path)], check=False, capture_output=True)
    return True, "Stopped"


def run_login_unified(
    settings: ThegentSettings, provider: str, prompt_func=None, skip_if_configured: bool = True
) -> int:
    """
    Unified login: open URL + prompt for API key. Preflight check for existing credentials.
    Returns 0 on success, 1 on skip/cancel, 2 on error.
    """
    provider_lower = provider.lower()
    if provider_lower not in PROVIDER_LOGIN_CONFIG:
        raise ValueError(f"Unknown provider: {provider}. Supported: {', '.join(sorted(PROVIDER_LOGIN_CONFIG))}")

    config_path = _ensure_config(settings)
    raw = yaml_load(config_path) if config_path.exists() else {}
    config: dict[str, Any] = dict(raw) if isinstance(raw, dict) else {}

    cfg = PROVIDER_LOGIN_CONFIG[provider_lower]
    if skip_if_configured and _has_provider_credentials(config, provider_lower):
        _LOG.info("Skipping login for provider=%s since credentials already exist in cliproxy config.", provider_lower)
        return 0  # Already configured

    url = cfg.get("url", "")
    display_name = cfg.get("display_name", provider)
    instructions = cfg.get("instructions", [])

    prompt_fn = prompt_func or input
    key: str | None = None

    # Check factory config for existing API key (DX-015: Check before opening browser)
    factory_key, factory_path = _get_factory_api_key(provider_lower)
    if factory_key and factory_path:
        if skip_if_configured:
            # Auto-use if not in force mode (user request: once found shouldnt ask again)
            key = factory_key
            _LOG.info("Using API key for %s from factory config at %s.", display_name, factory_path)
        else:
            # Force mode: still ask, but before opening browser
            try:
                resp = prompt_fn(f"  Found {display_name} API key in {factory_path}. Use it? [Y/n]: ").strip().lower()
            except Exception as exc:
                _LOG.error("Failed to read factory-key confirmation for %s: %s", provider_lower, exc)
                return 2
            if resp in ("", "y", "yes"):
                key = factory_key
                _LOG.info("Using factory API key for %s after confirmation.", display_name)
            else:
                _LOG.info("Skipping factory API key for %s after user declined confirmation.", display_name)

    if not key:
        # Print instructions
        if instructions:
            _LOG.info("Login instructions for %s:", display_name)
            for idx, _line in enumerate(instructions, start=1):
                _LOG.info("%d) %s", idx, _line)
        else:
            _LOG.debug("No login instructions configured for %s.", display_name)
        # ONLY open browser if no key found/accepted (user request: opens browser before i press y)
        try:
            if url:
                if not webbrowser.open(url):
                    _LOG.warning("Browser failed to open login URL for %s: %s", display_name, url)
            else:
                _LOG.warning("No login URL configured for %s, proceeding to manual key entry.", display_name)
        except Exception as exc:
            _LOG.warning("Could not open browser for %s login URL %s: %s", display_name, url, exc)

        try:
            key = prompt_fn(f"Enter {display_name} API key (or press Enter to skip): ").strip()
        except Exception as exc:
            _LOG.error("Failed to read API key input for %s: %s", display_name, exc)
            return 2

    if not key:
        _LOG.info("No API key provided for %s; returning skip.", display_name)
        return 1

    try:
        _inject_api_key_into_cliproxy(config, provider_lower, key, cfg)
        config_path.write_text(yaml_dumps(config, default_flow_style=False, sort_keys=False))
    except Exception as exc:
        _LOG.error("Failed to persist API key for %s to %s: %s", display_name, config_path, exc)
        return 2

    # WP-Y13: Auto-restart proxy to "hot-reload" the new API key
    if kill_proxy(settings):
        _LOG.info("Restarting cliproxy after updating API key for %s.", display_name)
        try:
            base_url = ensure_proxy_running(settings)
            _LOG.debug("cliproxy ready at %s", base_url)
        except Exception as exc:
            _LOG.error("Failed to restart cliproxy after login for %s: %s", display_name, exc)
            return 2
    else:
        _LOG.info("cliproxy not running; skipping restart for %s.", display_name)

    return 0


# CLIProxyAPIPlus -login flags (OAuth providers). Prefer OAuth over API key where available.
_LOGIN_FLAGS: dict[str, str] = {
    "claude": "-claude-login",
    "codex": "-codex-login",
    "gemini": "-login",
    "minimax": "-minimax-login",
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


def run_login(
    settings: ThegentSettings,
    provider: str,
    prompt_func=None,
    force: bool = False,
    login_timeout: int | None = None,
) -> int:
    """
    Run login for provider. Returns exit code.
    Prefers OAuth via CLIProxy for providers that support it.
    Falls back to API-key flow for providers without OAuth (minimax, nim).
    Preflight: skips OAuth flow if already configured (unless force=True).
    DX-015: Checks for factory keys before opening browser or prompting.
    """
    provider_lower = provider.lower()

    # CLIP-BUG-08: Qwen OAuth endpoint is unstable in current CLIProxy builds.
    # Use the API-key login flow until upstream OAuth is fixed.
    if provider_lower == "qwen":
        return run_login_unified(settings, provider_lower, prompt_func=prompt_func, skip_if_configured=not force)

    # Preflight factory-key fast path only for non-OAuth providers.
    if provider_lower not in OAUTH_ONLY_PROVIDERS and provider_lower not in _LOGIN_FLAGS:
        factory_key, _ = _get_factory_api_key(provider_lower)
        if factory_key and not force:
            # If a key exists in factory config, use the API-key flow (run_login_unified)
            # which we've updated to auto-use if skip_if_configured is True.
            return run_login_unified(settings, provider_lower, prompt_func=prompt_func, skip_if_configured=True)

    # Prefer OAuth when available
    if provider_lower in _LOGIN_FLAGS:
        # Preflight: skip if already configured (unless force)
        if not force and os.environ.get("THGENT_TESTING") != "1" and _has_oauth_credentials(settings, provider_lower):
            return 0
        binary = _resolve_binary(settings)
        if not _binary_available(binary):
            raise FileNotFoundError(_CLIPROXY_NOT_FOUND_MSG)
        config_path = _ensure_config(settings)
        flag = _LOGIN_FLAGS[provider_lower]
        timeout_seconds = (
            login_timeout if login_timeout is not None else int(os.environ.get("THGENT_LOGIN_TIMEOUT", "120"))
        )
        requires_interactive_stdio = provider_lower == "minimax"
        if requires_interactive_stdio and not sys.stdin.isatty():
            _LOG.error(
                "Provider %s login requires an interactive terminal. "
                "Use `thegent setup --minimax-key <KEY>` for non-interactive setup.",
                provider_lower,
            )
            return 2
        run_kwargs: dict[str, Any] = {
            "check": False,
            "env": os.environ.copy(),
            "timeout": timeout_seconds,
            "close_fds": True,
        }
        if requires_interactive_stdio:
            run_kwargs["stdin"] = sys.stdin
            run_kwargs["stdout"] = sys.stdout
            run_kwargs["stderr"] = sys.stderr
        else:
            run_kwargs["capture_output"] = True
            run_kwargs["text"] = True
        try:
            proc = shim_run(
                [binary, "-config", str(config_path), flag],
                **run_kwargs,
            )
            return proc.returncode
        except subprocess.TimeoutExpired:
            _LOG.warning("Login timed out for provider=%s after %ss", provider_lower, timeout_seconds)
            return 124

    # API-key-only providers
    if provider_lower in PROVIDER_LOGIN_CONFIG:
        return run_login_unified(settings, provider_lower, prompt_func=prompt_func, skip_if_configured=not force)

    raise ValueError(
        f"Unknown provider: {provider}. Supported: {', '.join(sorted(set(PROVIDER_LOGIN_CONFIG) | set(_LOGIN_FLAGS)))}"
    )
