"""GLM routing policy helpers for clode."""

from collections import Counter
from typing import Any, Callable

GLM_OFFER_SET: tuple[str, ...] = ("nim", "kilo", "minimax", "glm")
GLM_OFFER_COST: dict[str, float] = {
    "nim": 0.22,
    "kilo": 0.28,
    "minimax": 0.36,
    "glm": 0.80,
}
GLM_PREFERRED_BACKENDS: frozenset[str] = frozenset({"glm", "kilo", "nim", "minimax", "openrouter"})


class InvalidPolicyError(ValueError):
    """Raised when a GLM policy string is invalid."""


def glm_offer_backends() -> tuple[str, ...]:
    """Return GLM offer set in deterministic order."""
    return GLM_OFFER_SET


def validate_policy(policy: str) -> str:
    normalized = (policy or "round_robin").strip().lower()
    allowed = {"round_robin", "cheapest", "prefer_proxy", "prefer_direct", "failover"}
    if normalized not in allowed:
        raise InvalidPolicyError(
            "Invalid policy. Allowed: round_robin | cheapest | prefer_proxy | prefer_direct | failover."
        )
    return normalized


def resolve_clode_token(
    provider: str,
    prefer: str,
    policy: str,
    policy_counter: Counter[str],
    fetch_metrics: Callable[[], dict[str, Any]],
) -> str:
    """Resolve provider token for ANTHROPIC_API_KEY."""
    prefer_auth = (prefer or "auto").strip().lower()
    policy_name = validate_policy(policy)

    if provider != "glm":
        return provider
    if prefer_auth in GLM_PREFERRED_BACKENDS:
        return prefer_auth
    if policy_name == "round_robin":
        idx = policy_counter[provider]
        backends = glm_offer_backends()
        selected_backend = backends[idx % len(backends)]
        policy_counter[provider] = (idx + 1) % len(GLM_OFFER_SET)
        return selected_backend
    if policy_name == "cheapest":
        metrics = fetch_metrics()
        backends = glm_offer_backends()

        def cost_key(backend: str) -> tuple[float, float, str]:
            fallback = GLM_OFFER_COST.get(backend, 999.0)
            m = (metrics or {}).get(backend, {})
            cost = m.get("cost_per_1k_output") or m.get("cost_per_1k_input")
            if cost is None or cost <= 0:
                cost = fallback
            sr = m.get("success_rate", 1.0)
            return (cost, -sr, backend)

        return min(backends, key=cost_key)
    return f"glm:{policy_name}"
