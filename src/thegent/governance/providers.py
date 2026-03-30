"""Provider registry for economic governance (WP-5003).

Centralized registry of provider configurations with fallback chains
and cost/reliability metadata for routing decisions.

See: docs/changes/research-economic-governance/design.md § 2.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar

# Re-export ProviderMetrics from scoring for backwards compatibility
from thegent.governance.scoring import ProviderMetrics, DefaultProviderScorer


class ProviderType(Enum):
    """Provider deployment type."""

    DIRECT = "direct"  # Direct API connection
    PROXY = "proxy"  # Proxy/gateway connection


@dataclass
class ProviderConfig:
    """Provider configuration.

    Attributes:
        provider_id: Unique provider identifier (e.g., "gemini-flash")
        name: Display name
        provider_type: DIRECT or PROXY
        api_endpoint: API base URL
        auth_method: "api_key", "oauth", etc.
        cost_per_1m_tokens: USD cost per million tokens
        reliability: Uptime/success rate (0.0-1.0)
        latency_p99_ms: 99th percentile latency in milliseconds
        max_rpm: Maximum requests per minute
        max_tpm: Maximum tokens per minute
        fallback_chain: List of provider IDs to try on failure (first is primary)
    """

    provider_id: str
    name: str
    provider_type: ProviderType = ProviderType.DIRECT
    api_endpoint: str = ""
    auth_method: str = "api_key"
    cost_per_1m_tokens: float = 0.0
    reliability: float = 1.0  # 0.0-1.0
    latency_p99_ms: float = 1000.0  # milliseconds
    max_rpm: int = 10000  # Requests per minute
    max_tpm: int = 100000  # Tokens per minute
    fallback_chain: list[str] = field(default_factory=list)

    def to_metrics(self) -> ProviderMetrics:
        """Convert provider config to metrics for scoring."""
        return ProviderMetrics(
            provider_id=self.provider_id,
            reliability=self.reliability,
            latency_p99=self.latency_p99_ms,
            cost_per_1m_tokens=self.cost_per_1m_tokens,
        )


class ProviderRegistry:
    """Centralized provider configuration and lookup.

    Manages provider definitions, routing metadata, and fallback chains.
    Implements singleton pattern with class-level registry.
    """

    _registry: ClassVar[dict[str, ProviderConfig]] = {}
    _initialized: ClassVar[bool] = False

    def __init__(self, scorer: Any = None) -> None:
        """Initialize provider registry with optional custom scorer.

        Args:
            scorer: Optional custom scorer implementing score(provider_id, metrics) -> float
                   If None, uses DefaultProviderScorer()
        """
        self.scorer = scorer if scorer is not None else DefaultProviderScorer()

    @classmethod
    def register(cls, config: ProviderConfig) -> None:
        """Register a provider configuration.

        Args:
            config: Provider configuration
        """
        cls._registry[config.provider_id] = config

    @classmethod
    def get(cls, provider_id: str) -> ProviderConfig | None:
        """Get provider configuration by ID.

        Args:
            provider_id: Provider identifier

        Returns:
            Provider config or None if not found
        """
        return cls._registry.get(provider_id)

    @classmethod
    def list_providers(cls) -> list[ProviderConfig]:
        """List all registered providers.

        Returns:
            List of provider configurations
        """
        return list(cls._registry.values())

    @classmethod
    def get_fallback_order(cls, provider_id: str) -> list[str]:
        """Get fallback chain for a provider.

        Args:
            provider_id: Provider identifier

        Returns:
            Ordered list of fallback provider IDs
        """
        config = cls.get(provider_id)
        return config.fallback_chain if config else []

    @classmethod
    def unregister(cls, provider_id: str) -> None:
        """Unregister a provider (for testing).

        Args:
            provider_id: Provider identifier to remove
        """
        cls._registry.pop(provider_id, None)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered providers (for testing).

        WARNING: This should only be called during tests.
        """
        cls._registry.clear()

    @classmethod
    def count(cls) -> int:
        """Get number of registered providers.

        Returns:
            Provider count
        """
        return len(cls._registry)

    def get_score(self, provider_id: str) -> float:
        """Get provider score for routing decisions.

        Args:
            provider_id: Provider identifier

        Returns:
            Score (higher = better) or 0.0 if provider not found

        Raises:
            ValueError: If provider not found
        """
        config = self.get(provider_id)
        if config is None:
            raise ValueError(f"Provider not found: {provider_id}")

        metrics = config.to_metrics()
        return self.scorer.score(provider_id, metrics)

    def get_ranked_providers(self) -> list[tuple[str, float]]:
        """Get all providers ranked by score (highest first).

        Returns:
            List of (provider_id, score) tuples sorted by score descending
        """
        providers = self.list_providers()
        scored = []
        for provider in providers:
            try:
                score = self.get_score(provider.provider_id)
                scored.append((provider.provider_id, score))
            except ValueError:
                # Skip providers that can't be scored
                continue
        scored.sort(key=lambda x: x[1].composite_score, reverse=True)
        return scored

    def validate_fallback_chains(self) -> list[str]:
        """Validate all fallback chains.

        Returns:
            List of validation errors, empty if all valid
        """
        errors = []
        for provider in self.list_providers():
            for fallback_id in provider.fallback_chain:
                if fallback_id not in self._registry:
                    errors.append(
                        f"Provider {provider.provider_id} has invalid fallback: {fallback_id} not found"
                    )
        return errors

    def get_cost_efficient_order(self) -> list[str]:
        """Get providers ordered by cost efficiency (cheapest first).

        Returns:
            List of provider IDs sorted by cost per 1M tokens ascending
        """
        providers = self.list_providers()
        sorted_providers = sorted(
            providers,
            key=lambda p: (
                p.cost_per_1m_tokens,
                -p.reliability,
                p.latency_p99_ms,
            ),
        )
        return [p.provider_id for p in sorted_providers]


# Built-in provider configurations
_BUILTIN_PROVIDERS = [
    ProviderConfig(
        provider_id="gemini-flash",
        name="Google Gemini Flash",
        provider_type=ProviderType.DIRECT,
        api_endpoint="https://generativelanguage.googleapis.com",
        auth_method="api_key",
        cost_per_1m_tokens=0.10,
        reliability=0.995,
        latency_p99_ms=250,
        max_rpm=1500,
        max_tpm=1000000,
        fallback_chain=["claude-haiku", "gpt-4o-mini"],
    ),
    ProviderConfig(
        provider_id="claude-haiku",
        name="Anthropic Claude Haiku",
        provider_type=ProviderType.DIRECT,
        api_endpoint="https://api.anthropic.com/v1",
        auth_method="api_key",
        cost_per_1m_tokens=0.25,
        reliability=0.998,
        latency_p99_ms=300,
        max_rpm=1000,
        max_tpm=500000,
        fallback_chain=["gemini-flash", "gpt-4o-mini"],
    ),
    ProviderConfig(
        provider_id="gpt-4o-mini",
        name="OpenAI GPT-4o Mini",
        provider_type=ProviderType.DIRECT,
        api_endpoint="https://api.openai.com/v1",
        auth_method="api_key",
        cost_per_1m_tokens=0.15,
        reliability=0.997,
        latency_p99_ms=200,
        max_rpm=3500,
        max_tpm=2000000,
        fallback_chain=["claude-haiku", "gemini-flash"],
    ),
    ProviderConfig(
        provider_id="claude-sonnet",
        name="Anthropic Claude Sonnet",
        provider_type=ProviderType.DIRECT,
        api_endpoint="https://api.anthropic.com/v1",
        auth_method="api_key",
        cost_per_1m_tokens=3.00,
        reliability=0.999,
        latency_p99_ms=400,
        max_rpm=500,
        max_tpm=250000,
        fallback_chain=["claude-haiku"],
    ),
    ProviderConfig(
        provider_id="claude-opus",
        name="Anthropic Claude Opus",
        provider_type=ProviderType.DIRECT,
        api_endpoint="https://api.anthropic.com/v1",
        auth_method="api_key",
        cost_per_1m_tokens=15.00,
        reliability=0.9995,
        latency_p99_ms=600,
        max_rpm=200,
        max_tpm=100000,
        fallback_chain=["claude-sonnet"],
    ),
]


def _initialize_registry() -> None:
    """Initialize registry with built-in providers.

    Called once during module import to populate the default registry.
    """
    if ProviderRegistry._initialized:  # noqa: SLF001 -- intentional access to ClassVar sentinel on own class
        return

    for provider_config in _BUILTIN_PROVIDERS:
        ProviderRegistry.register(provider_config)

    ProviderRegistry._initialized = True  # noqa: SLF001 -- intentional access to ClassVar sentinel on own class


# Initialize registry on module import
_initialize_registry()
