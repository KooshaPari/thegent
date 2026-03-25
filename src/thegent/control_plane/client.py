"""Control plane HTTP client for ConfigProvider."""

from typing import Any

import httpx
import pybreaker
from opentelemetry import trace

# Tracer for control plane client
tracer = trace.get_tracer("thegent.control_plane.client")

# Circuit breaker for control plane: 5 failures = open for 30s
_cp_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)


class ControlPlaneUnavailable(Exception):
    """Control plane could not be reached."""


class ControlPlaneConfigProvider:
    """Connect to control plane; full resolution order applied server-side."""

    def __init__(self, url: str, timeout: float = 2.0) -> None:
        self._url = url.rstrip("/")
        self._timeout = timeout

    def resolve(
        self,
        tenant_id: str | None = None,
        session_id: str | None = None,
        request_overrides: dict[str, Any] | None = None,
        keys: list[str] | None = None,
    ) -> dict[str, Any]:
        """Resolve config from control plane. Fallback to local env on failure."""

        @_cp_breaker
        def _call_cp() -> dict[str, Any]:
            with tracer.start_as_current_span(
                "config.resolve",
                kind=trace.SpanKind.CLIENT,
                attributes={
                    "thegent.tenant_id": tenant_id or "default",
                    "thegent.session_id": session_id or "unknown",
                },
            ) as span:
                r = httpx.post(
                    f"{self._url}/v1/config/resolve",
                    json={
                        "tenant_id": tenant_id,
                        "session_id": session_id,
                        "overrides": request_overrides or {},
                        "keys": keys,
                    },
                    timeout=self._timeout,
                )
                r.raise_for_status()
                res = r.json()
                span.set_attribute("thegent.config.keys", str(list(res.keys())))
                return res

        try:
            return _call_cp()
        except (httpx.HTTPError, httpx.TimeoutException, ConnectionError, pybreaker.CircuitBreakerError):
            # Phase 3: Fallback to local EnvConfigProvider on failure (circuit breaker open or request failed)
            from thegent.config_provider import EnvConfigProvider

            return EnvConfigProvider().resolve(
                tenant_id=tenant_id,
                session_id=session_id,
                request_overrides=request_overrides,
                keys=keys,
            )

    def get_tenant_config(self, tenant_id: str) -> dict[str, Any] | None:
        """Get tenant config from control plane. Phase 2: not implemented."""
        return None
