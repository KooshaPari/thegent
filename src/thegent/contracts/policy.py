"""Normalization policy and fallback evaluation for agent outputs.

Defines rules for when a normalized message is acceptable and when a fallback
to plain text extraction should be flagged or blocked.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FallbackPolicy:
    """Configuration for normalization fallback behavior and SLO budgets."""

    allow_plain_fallback: bool = True
    min_confidence_threshold: float = 0.4
    max_fallback_rate: float = 0.3
    strict_providers: list[str] = field(default_factory=list)

    # SLO budgets (WP-X6)
    max_latency_ms: int = 30000  # 30s default
    min_success_rate: float = 0.9
    error_budget_percentage: float = 0.1


class PolicyRegistry:
    """Registry for named fallback policies."""

    def __init__(self) -> None:
        self._policies: dict[str, FallbackPolicy] = {}
        self._register_defaults()

    def register(self, name: str, policy: FallbackPolicy) -> None:
        """Register a named policy."""
        self._policies[name] = policy

    def get(self, name: str) -> FallbackPolicy:
        """Get policy by name, falling back to default."""
        return self._policies.get(name, self._policies.get("default", FallbackPolicy()))

    def _register_defaults(self) -> None:
        self.register("default", FallbackPolicy())
        self.register(
            "strict",
            FallbackPolicy(
                allow_plain_fallback=False,
                min_confidence_threshold=0.8,
                max_fallback_rate=0.1,
                max_latency_ms=15000,
            ),
        )
        self.register(
            "fast",
            FallbackPolicy(
                allow_plain_fallback=True,
                min_confidence_threshold=0.2,
                max_fallback_rate=0.5,
                max_latency_ms=5000,
            ),
        )
        # Lane-based policies (WP-1002, WP-X6)
        self.register(
            "critical",
            FallbackPolicy(
                allow_plain_fallback=False,
                min_confidence_threshold=0.9,
                max_fallback_rate=0.05,
                max_latency_ms=60000,
            ),
        )
        self.register(
            "recovery",
            FallbackPolicy(
                allow_plain_fallback=True,
                min_confidence_threshold=0.3,
                max_fallback_rate=0.4,
                max_latency_ms=120000,
            ),
        )


_policy_registry: PolicyRegistry | None = None


def get_policy_registry() -> PolicyRegistry:
    """Get global policy registry (singleton)."""
    global _policy_registry
    if _policy_registry is None:
        _policy_registry = PolicyRegistry()
    return _policy_registry


def evaluate_fallback(
    provider: str,
    confidence: float,
    is_fallback: bool,
    policy: FallbackPolicy,
    stats: dict[str, Any] | None = None,
) -> list[str]:
    """Evaluate if a normalization result violates fallback policies.

    Returns:
        List of policy violation strings. Empty if valid.
    """
    issues: list[str] = []

    # 1. Strict Provider Check
    if is_fallback and provider in policy.strict_providers:
        issues.append(f"Provider {provider} is in strict mode and must produce structured output.")

    # 2. Confidence Check
    if confidence < policy.min_confidence_threshold:
        issues.append(
            f"Normalization confidence {confidence:.2f} is below threshold {policy.min_confidence_threshold:.2f}"
        )

    # 3. Global Fallback Rate Check
    if stats and stats.get("fallback_rate", 0.0) > policy.max_fallback_rate:
        issues.append(
            f"Global fallback rate {stats['fallback_rate']:.1%} exceeds budget {policy.max_fallback_rate:.1%}"
        )

    # 4. Fallback Allowed Check
    if is_fallback and not policy.allow_plain_fallback:
        issues.append("Plain text fallback is disabled by policy.")

    return issues
