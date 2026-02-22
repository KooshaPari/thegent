"""Cross-connector consistency verification.

# @trace WL-301
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass
class ConsistencyViolation:
    """A consistency violation between two connectors."""

    wl_id: str
    connector_a: str
    connector_b: str
    field: str
    value_a: Any
    value_b: Any


class CrossConnectorVerifier:
    """Verify status/priority consistency across all connectors per cycle."""

    # Fields that must be consistent across connectors
    CRITICAL_FIELDS: ClassVar[set[str]] = {"status", "priority"}

    def __init__(self) -> None:
        """Initialize the cross-connector verifier."""

    def compare(
        self, connector_a_state: dict[str, Any], connector_b_state: dict[str, Any]
    ) -> list[ConsistencyViolation]:
        """Compare state across two connectors and detect inconsistencies.

        Args:
            connector_a_state: State dictionary from connector A.
                Must contain keys: wl_id, connector_name, status, priority.
            connector_b_state: State dictionary from connector B.
                Must contain keys: wl_id, connector_name, status, priority.

        Returns:
            List of ConsistencyViolation objects for each mismatch.

        Raises:
            ValueError: If required keys are missing from state dictionaries.
        """
        violations = []

        # Validate required keys
        required_keys = {"wl_id", "connector_name", "status", "priority"}
        for state, label in [
            (connector_a_state, "connector_a_state"),
            (connector_b_state, "connector_b_state"),
        ]:
            missing = required_keys - set(state.keys())
            if missing:
                raise ValueError(f"{label} missing required keys: {missing}")

        wl_id = connector_a_state["wl_id"]
        connector_a_name = connector_a_state["connector_name"]
        connector_b_name = connector_b_state["connector_name"]

        # Compare critical fields
        for field in self.CRITICAL_FIELDS:
            value_a = connector_a_state.get(field)
            value_b = connector_b_state.get(field)

            if value_a != value_b:
                violations.append(
                    ConsistencyViolation(
                        wl_id=wl_id,
                        connector_a=connector_a_name,
                        connector_b=connector_b_name,
                        field=field,
                        value_a=value_a,
                        value_b=value_b,
                    )
                )

        return violations
