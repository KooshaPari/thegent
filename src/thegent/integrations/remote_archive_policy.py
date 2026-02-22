"""Remote archive/delete policy.

# @trace WL-167
"""

from __future__ import annotations

from enum import Enum


class ArchiveAction(Enum):
    """Actions available for remote resource management."""

    ARCHIVE = "archive"
    DELETE = "delete"
    SKIP = "skip"


class RemoteArchivePolicy:
    """Manages archive and delete policies per connector."""

    def __init__(self, default_action: ArchiveAction = ArchiveAction.SKIP) -> None:
        """Initialize the archive policy.

        Args:
            default_action: The default action to apply if no connector-specific policy is set.
        """
        self._default_action = default_action
        self._policies: dict[str, ArchiveAction] = {}

    def set_policy(self, connector_id: str, action: ArchiveAction) -> None:
        """Set the policy for a specific connector.

        Args:
            connector_id: The connector identifier.
            action: The ArchiveAction to apply for this connector.
        """
        self._policies[connector_id] = action

    def get_action(self, connector_id: str) -> ArchiveAction:
        """Get the configured action for a connector.

        Args:
            connector_id: The connector identifier.

        Returns:
            The configured ArchiveAction, or the default if not configured.
        """
        return self._policies.get(connector_id, self._default_action)

    def apply(self, connector_id: str, items: list[str]) -> dict[str, list[str]]:
        """Apply the policy and group items by action.

        Args:
            connector_id: The connector identifier.
            items: List of item IDs to apply the policy to.

        Returns:
            Dictionary mapping action names (e.g., 'archive', 'delete') to lists of items.
        """
        action = self.get_action(connector_id)
        return {action.value: items}
