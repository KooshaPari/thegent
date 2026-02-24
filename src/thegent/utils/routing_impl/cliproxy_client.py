"""CLIProxy client for routing decisions.

This client replaces LiteLLM-based routing. All routing decisions go through CLIProxy
localhost:8317 /v1/routing/select endpoint with local fallback.

@trace FR-CLIPROXY-INTEGRATION-001
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from thegent.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class RoutingResponse:
    """Response from CLIProxy /v1/routing/select endpoint."""

    model_id: str
    provider: str
    estimated_cost: float
    estimated_latency_ms: int
    quality_score: float


class CLIProxyRoutingClient:
    """Client for CLIProxy routing endpoint with local fallback."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 10.0,
    ):
        """Initialize the CLIProxy routing client."""
        settings = get_settings()
        self.base_url = base_url or f"http://localhost:{settings.cliproxy_port}"
        self.timeout = timeout
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Lazy initialization of HTTP client."""
        if self._client is None:
            self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def select_model(
        self,
        task_complexity: str,
        max_cost_per_call: float,
        max_latency_ms: int,
        min_quality_score: float = 0.7,
    ) -> RoutingResponse:
        """Select optimal model via CLIProxy with local fallback."""
        try:
            resp = self.client.post(
                "/v1/routing/select",
                json={
                    "taskComplexity": task_complexity,
                    "maxCostPerCall": max_cost_per_call,
                    "maxLatencyMs": max_latency_ms,
                    "minQualityScore": min_quality_score,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return RoutingResponse(
                model_id=data["model_id"],
                provider=data["provider"],
                estimated_cost=data["estimated_cost"],
                estimated_latency_ms=data["estimated_latency_ms"],
                quality_score=data["quality_score"],
            )
        except httpx.HTTPError as e:
            logger.warning(f"CLIProxy routing failed: {e}, using local fallback")
            return self._local_fallback(task_complexity)

    def _local_fallback(self, complexity: str) -> RoutingResponse:
        """Simple fallback based on complexity."""
        models = {
            "FAST": ("minimax-m2.5", "minimax", 0.00007, 300, 0.72),
            "NORMAL": ("gemini-3-flash", "gemini", 0.0001, 800, 0.78),
            "COMPLEX": ("claude-sonnet-4.6", "claude", 0.003, 2000, 0.88),
            "HIGH_COMPLEX": ("gpt-5.3-codex-xhigh", "openai", 0.015, 4000, 0.95),
        }
        model, provider, cost, latency, quality = models.get(complexity.upper(), models["NORMAL"])
        return RoutingResponse(
            model_id=model,
            provider=provider,
            estimated_cost=cost,
            estimated_latency_ms=latency,
            quality_score=quality,
        )

    def __enter__(self) -> "CLIProxyRoutingClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
