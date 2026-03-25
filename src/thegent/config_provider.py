from __future__ import annotations

"""ConfigProvider abstraction for control plane integration.

Phase 1: EnvConfigProvider wraps ThegentSettings.
Phase 2+: ControlPlaneConfigProvider connects to CP when THGENT_CONTROL_PLANE_URL set.

Resolution order: request_overrides → session → tenant → stamp → global.
"""

import logging
from typing import Any, Protocol

from thegent.config import ThegentSettings
from thegent.utils.path_utils import normalize_path, path_to_str

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

logger = logging.getLogger(__name__)
_last_provider_metadata: dict[str, Any] = {
    "source": "env",
    "degraded": False,
    "control_plane_configured": False,
    "dependency_missing": False,
    "error_type": None,
    "error_message": None,
}


def _attach_provider_metadata(provider: ConfigProvider, metadata: dict[str, Any]) -> ConfigProvider:
    try:
        provider_any: Any = provider
        provider_any.provider_metadata = dict(metadata)
    except AttributeError, TypeError:
        logger.debug("Failed to attach provider metadata to %s", type(provider).__name__, exc_info=True)
    return provider


def get_last_provider_metadata() -> dict[str, Any]:
    """Return metadata for the most recent provider selection."""
    return dict(_last_provider_metadata)


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
    global _last_provider_metadata
    settings = ThegentSettings()
    url = settings.control_plane_url
    if url and url != "http://127.0.0.1:3848":  # Only use CP if explicitly configured
        try:
            from thegent.control_plane.client import ControlPlaneConfigProvider

            metadata = {
                "source": "control_plane",
                "degraded": False,
                "control_plane_configured": True,
                "dependency_missing": False,
                "error_type": None,
                "error_message": None,
            }
            _last_provider_metadata = metadata
            return _attach_provider_metadata(ControlPlaneConfigProvider(url), metadata)
        except ImportError as exc:
            metadata = {
                "source": "env",
                "degraded": True,
                "control_plane_configured": True,
                "dependency_missing": True,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            _last_provider_metadata = metadata
            logger.warning(
                "Control-plane configured but provider import failed; using EnvConfigProvider: %s",
                exc,
            )
            return _attach_provider_metadata(EnvConfigProvider(), metadata)
    metadata = {
        "source": "env",
        "degraded": False,
        "control_plane_configured": False,
        "dependency_missing": False,
        "error_type": None,
        "error_message": None,
    }
    _last_provider_metadata = metadata
    return _attach_provider_metadata(EnvConfigProvider(), metadata)
