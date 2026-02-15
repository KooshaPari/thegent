"""Normalization policy and fallback evaluation for agent outputs.

Defines rules for when a normalized message is acceptable and when a fallback
to plain text extraction should be flagged or blocked.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FallbackPolicy:
    """Configuration for normalization fallback behavior."""

    allow_plain_fallback: bool = True
    min_confidence_threshold: float = 0.4
    max_fallback_rate: float = 0.3
    strict_providers: list[str] = field(default_factory=list)


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
