"""ProxyMetricsPort: Abstract protocol for fetching provider metrics.

This port breaks the circular dependency between thegent-core and
thegent-agents: core/models/ used to import directly from
phenotype_thegent_agents.agents.cliproxy_manager.  Now core defines this abstract
protocol; the concrete implementation lives in thegent-agents.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProxyMetricsPort(Protocol):
    """Port for fetching live provider metrics from a running proxy.

    Concrete implementations are registered at startup (e.g. by the CLI or
    agent package) and injected via the DI container or passed as an argument.
    """

    def fetch_provider_metrics(
        self,
        settings: Any | None = None,
    ) -> dict[str, dict[str, Any]] | None:
        """Return per-provider metric dicts, or None when the proxy is unreachable.

        Returns:
            Mapping of provider name -> metrics dict, or None on failure.
            Metric dict may contain keys like: tps_1m, latency_p50_ms,
            latency_p95_ms, success_rate, cost_per_1k, cost_per_1k_input,
            cost_per_1k_output.
        """
        ...

    def ensure_proxy_running(self, settings: Any | None = None) -> str:
        """Ensure the CLIProxy is running and return its base URL.

        Returns:
            Base URL string (e.g. 'http://127.0.0.1:7777/v1').
        """
        ...


class NullProxyMetricsPort:
    """Null-object implementation of ProxyMetricsPort.

    Used when no concrete proxy is available (e.g. during tests or when the
    agent package is not installed).  All methods return safe fallback values.
    """

    def fetch_provider_metrics(
        self,
        settings: Any | None = None,
    ) -> dict[str, dict[str, Any]] | None:
        """Return None — no live metrics available."""
        return None

    def ensure_proxy_running(self, settings: Any | None = None) -> str:
        """Return a placeholder URL — no proxy is managed."""
        try:
            port = getattr(settings, "cliproxy_port", 7777) if settings else 7777
            return f"http://127.0.0.1:{port}/v1"
        except Exception:
            return "http://127.0.0.1:7777/v1"


__all__ = [
    "NullProxyMetricsPort",
    "ProxyMetricsPort",
]
