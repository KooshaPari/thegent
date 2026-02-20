"""ConfigProvider abstraction for control plane integration.

Phase 1: EnvConfigProvider wraps ThegentSettings.
Phase 2+: ControlPlaneConfigProvider connects to CP when THGENT_CONTROL_PLANE_URL set.

Resolution order: request_overrides → session → tenant → stamp → global.
"""

import os
from pathlib import Path
from typing import Any, Protocol

from thegent.config import ThegentSettings

# Import path utilities for normalized path handling
try:
    # When running as installed package
    from scripts.path_utils import normalize_path, path_to_str
except ImportError:
    # Fallback for development environments
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
    from path_utils import normalize_path, path_to_str

# Keys resolvable via ConfigProvider (subset of ThegentSettings used by run/bg)
_RESOLVE_KEYS = [
    "default_timeout",
    "default_timeout_claude",
    "default_timeout_free",
    "max_idle_seconds",
    "max_wall_time",
    "session_dir",
    "max_concurrency",
    "load_spike_threshold",
    "load_surge_threshold",
]


def _settings_to_dict(keys: list[str] | None) -> dict[str, Any]:
    """Extract config dict from ThegentSettings. Paths become str via path_utils."""
    s = ThegentSettings()
    klist = keys or _RESOLVE_KEYS
    out: dict[str, Any] = {}
    for k in klist:
        if hasattr(s, k):
            v = getattr(s, k)
            if hasattr(v, "expanduser"):
                # Use normalize_path and path_to_str for consistent handling
                normalized = normalize_path(v) if v else None
                out[k] = path_to_str(normalized)
            else:
                out[k] = v
    return out


def _resolve_tenant_from_cwd(cwd: Path | None = None) -> str:
    """Read .thegent/tenant or pyproject.toml [tool.thegent.tenant]. Default 'default'."""
    start_path = cwd or Path.cwd()
    # Try .thegent/tenant first
    target = start_path / ".thegent" / "tenant"
    if target.exists():
        try:
            return target.read_text(encoding="utf-8").strip() or "default"
        except Exception:
            pass

    # Try pyproject.toml
    pyproject = start_path / "pyproject.toml"
    if pyproject.exists():
        try:
            import tomllib

            with open(pyproject, "rb") as f:
                data = tomllib.load(f)
                tenant = data.get("tool", {}).get("thegent", {}).get("tenant")
                if tenant:
                    return str(tenant)
        except Exception:
            pass

    return "default"


class ConfigProvider(Protocol):
    """Protocol for config resolution with full override semantics."""

    def resolve(
        self,
        tenant_id: str | None = None,
        session_id: str | None = None,
        request_overrides: dict[str, Any] | None = None,
        keys: list[str] | None = None,
    ) -> dict[str, Any]: ...

    def get_tenant_config(self, tenant_id: str) -> dict[str, Any] | None: ...


class EnvConfigProvider:
    """Reads from ThegentSettings (env). Ignores tenant; merges request_overrides."""

    def resolve(
        self,
        tenant_id: str | None = None,
        session_id: str | None = None,
        request_overrides: dict[str, Any] | None = None,
        keys: list[str] | None = None,
    ) -> dict[str, Any]:
        from opentelemetry import trace

        tracer = trace.get_tracer("thegent.config_provider")
        with tracer.start_as_current_span("config.resolve") as span:
            span.set_attribute("thegent.config.source", "env")
            span.set_attribute("thegent.tenant_id", tenant_id or "default")
            base = _settings_to_dict(keys)
            overrides = request_overrides or {}
            return {**base, **overrides}

    def get_tenant_config(self, tenant_id: str) -> dict[str, Any] | None:
        return None


def get_config_provider() -> ConfigProvider:
    """Returns ConfigProvider. Phase 1: always EnvConfigProvider."""
    settings = ThegentSettings()
    url = settings.control_plane_url
    if url and url != "http://127.0.0.1:3848":  # Only use CP if explicitly configured
        try:
            from thegent.control_plane.client import ControlPlaneConfigProvider

            return ControlPlaneConfigProvider(url)
        except ImportError:
            pass
    return EnvConfigProvider()
