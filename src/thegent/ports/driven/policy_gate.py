"""Protocol for governance policy evaluation."""

from __future__ import annotations

from typing import Any, Protocol


class PolicyGate(Protocol):
    """Port interface for governance policy evaluation.

    Breaks governance ↔ execution circular dependency by allowing
    execution logic to query policy decisions without importing
    governance implementation details.
    """

    def evaluate_policy(self, action: str, context: dict[str, Any]) -> bool:
        """Evaluate whether an action is allowed under current policies.

        Args:
            action: Action identifier (e.g., 'agent.spawn', 'hook.execute', 'file.write').
            context: Policy evaluation context (e.g., {'agent_type': 'free', 'module': 'cli'}).

        Returns:
            True if action is allowed, False otherwise.
        """
        ...

    def get_active_policies(self) -> list[str]:
        """Get list of currently active policy names.

        Returns:
            List of active policy identifiers.
        """
        ...


__all__ = [
    "PolicyGate",
]
