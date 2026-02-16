"""WP-10004: Adapter admission and trust policy.

Enforces trust-based admission rules for provider adapters.
"""

from typing import Any

from thegent.contracts.capability_registry import CapabilityRegistry


class AdapterAdmissionPolicy:
    """Policy engine for adapter admission control."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry

    def evaluate_admission(self, adapter_id: str, lane: str) -> dict[str, Any]:
        """Evaluate if an adapter can be admitted to a specific lane."""
        cap = self.registry.get_capability(f"adapter.{adapter_id}")
        if not cap:
            return {"allowed": False, "reason": "Adapter not registered."}

        # Critical lane requires trust level >= 4
        if lane == "critical" and cap.trust_level < 4:
            return {"allowed": False, "reason": f"Trust level {cap.trust_level} insufficient for critical lane."}

        return {"allowed": True, "trust_level": cap.trust_level}
