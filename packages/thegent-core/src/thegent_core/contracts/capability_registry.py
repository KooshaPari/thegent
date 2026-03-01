"""WP-10002: Capability registry service.

Authoritative source for available capabilities, versions, and trust levels.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Capability:
    """A registered system capability."""

    id: str
    version: str
    trust_level: int = 1  # 1 (low) to 5 (high)
    metadata: dict[str, Any] = field(default_factory=dict)
    unsupported_combos: list[str] = field(default_factory=list)


class CapabilityRegistry:
    """Central registry for managing and querying system capabilities."""

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(Capability("orchestrate.run", "2.0", trust_level=5))
        self.register(Capability("orchestrate.bg", "2.0", trust_level=5))
        self.register(Capability("govern.negotiate", "1.0", trust_level=4))
        self.register(Capability("plan.analyze", "1.0", trust_level=3))

    def register(self, cap: Capability) -> None:
        """Register a new capability."""
        self._capabilities[cap.id] = cap

    def get_capability(self, cap_id: str) -> Capability | None:
        """Return capability metadata if found."""
        return self._capabilities.get(cap_id)

    def list_capabilities(self) -> list[Capability]:
        """List all registered capabilities."""
        return list(self._capabilities.values())

    def is_supported(self, cap_id: str, version: str | None = None) -> bool:
        """Check if a capability and version are supported."""
        cap = self.get_capability(cap_id)
        if not cap:
            return False
        if version and cap.version != version:
            return False
        return True
