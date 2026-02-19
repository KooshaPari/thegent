"""ConfigProvider abstraction for control plane integration.

Phase 1: EnvConfigProvider wraps ThegentSettings.
Phase 2+: ControlPlaneConfigProvider connects to CP when THGENT_CONTROL_PLANE_URL set.

Resolution order: request_overrides → session → tenant → stamp → global.
"""

import os
from typing import Any, Protocol

from thegent.config import ThegentSettings

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
    """Extract config dict from ThegentSettings. Paths become str."""
    s = ThegentSettings()
    klist = keys or _RESOLVE_KEYS
    out: dict[str, Any] = {}
    for k in klist:
        if hasattr(s, k):
            v = getattr(s, k)
            if hasattr(v, "expanduser"):
                out[k] = str(v.expanduser().resolve()) if v else None
            else:
                out[k] = v
    return out


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
        base = _settings_to_dict(keys)
        overrides = request_overrides or {}
        return {**base, **overrides}

    def get_tenant_config(self, tenant_id: str) -> dict[str, Any] | None:
        return None


def get_config_provider() -> ConfigProvider:
    """Returns ConfigProvider. Phase 1: always EnvConfigProvider."""
    url = os.environ.get("THGENT_CONTROL_PLANE_URL")
    if url:
        try:
            from thegent.control_plane.client import ControlPlaneConfigProvider

            return ControlPlaneConfigProvider(url)
        except ImportError:
            pass
    return EnvConfigProvider()
