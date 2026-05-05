"""Policy contracts module."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any
from enum import Enum

if TYPE_CHECKING:
    pass


class FallbackPolicy(Enum):
    """Fallback policy enumeration."""
    NONE = "none"
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"
    RETRY = "retry"
    SKIP = "skip"
    FAIL = "fail"


class PolicyRule:
    """A policy rule definition."""

    def __init__(self, rule_id: str, policy_type: str, config: dict[str, Any]) -> None:
        self.rule_id = rule_id
        self.policy_type = policy_type
        self.config = config

    def matches(self, context: dict[str, Any]) -> bool:
        """Check if this rule matches the given context."""
        return True

    def evaluate(self, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate this rule against the context."""
        return {"matched": True, "action": "allow"}


def evaluate_fallback(
    policy: FallbackPolicy,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate a fallback policy.

    Args:
        policy: The fallback policy to evaluate.
        context: The context dictionary.

    Returns:
        Evaluation result dictionary.
    """
    return {
        "policy": policy.value,
        "action": policy.value,
        "context": context,
    }


__all__ = [
    "FallbackPolicy",
    "PolicyRule",
    "evaluate_fallback",
    "get_contracts_fallback_policy",
]


def get_contracts_fallback_policy() -> FallbackPolicy:
    """Get the contracts fallback policy."""
    return FallbackPolicy.ALLOW
