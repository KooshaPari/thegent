"""WP-10001: ConfigProvider protocol and implementations for Control Plane Phase 1.

Hardening (AUDIT-N+86 — SOTA pass-70)
--------------------------------------
Contract surface asserted by
``tests/test_unit_audit_n86_config_provider_hardening.py``
(``FR-GOV-CFG-001..015``).

# @trace AUDIT-N+86
"""

from typing import Any, Protocol, runtime_checkable

from thegent.config import ThegentSettings

__all__ = [
    "ConfigProvider",
    "EnvConfigProvider",
    "get_config_provider",
]


@runtime_checkable
class ConfigProvider(Protocol):
    """Protocol for configuration resolution with override semantics."""

    def resolve(
        self,
        tenant_id: str | None = None,
        session_id: str | None = None,
        request_overrides: dict[str, Any] | None = None,
        keys: list[str] | None = None,
    ) -> dict[str, Any]:
        """Resolve config for a given context.

        Resolution order: request_overrides -> session -> tenant -> stamp -> global.
        """
        ...

    def get_tenant_config(self, tenant_id: str) -> dict[str, Any] | None:
        """Fetch raw configuration for a specific tenant."""
        ...


class EnvConfigProvider:
    """Standard implementation using local ThegentSettings (env vars).

    Ignores tenant/session isolation; merges request overrides onto base settings.
    """

    def resolve(
        self,
        tenant_id: str | None = None,
        session_id: str | None = None,
        request_overrides: dict[str, Any] | None = None,
        keys: list[str] | None = None,
    ) -> dict[str, Any]:
        settings = ThegentSettings()
        # Filter keys if requested
        base = {k: getattr(settings, k) for k in keys if hasattr(settings, k)} if keys else settings.model_dump()

        # Merge overrides
        if request_overrides:
            base.update(request_overrides)

        return base

    def get_tenant_config(self, tenant_id: str) -> dict[str, Any] | None:
        """Env provider does not support multi-tenancy yet."""
        return None


def get_config_provider() -> ConfigProvider:
    """Factory to get the active config provider based on settings."""
    settings = ThegentSettings()
    cp_url = settings.control_plane_url
    if cp_url:
        # Avoid circular import if/when ControlPlaneConfigProvider is added
        from thegent.governance.config_provider_cp import ControlPlaneConfigProvider

        return ControlPlaneConfigProvider(cp_url)

    return EnvConfigProvider()
