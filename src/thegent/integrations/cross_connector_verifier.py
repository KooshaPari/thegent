"""Cross-connector consistency verification.

# @trace WL-301
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
import hashlib
import orjson as json
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
    first_seen_at: str | None = None
    ttl_seconds: int = 0
    escalated: bool = False


@dataclass
class ConflictRecord:
    """Conflict entry with TTL-based escalation metadata."""

    wl_id: str
    connector_a: str
    connector_b: str
    field: str
    value_a: Any
    value_b: Any
    first_seen_at: datetime
    ttl_seconds: int
    escalated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "wl_id": self.wl_id,
            "connector_a": self.connector_a,
            "connector_b": self.connector_b,
            "field": self.field,
            "value_a": self.value_a,
            "value_b": self.value_b,
            "first_seen_at": self.first_seen_at.isoformat(),
            "ttl_seconds": self.ttl_seconds,
            "escalated": self.escalated,
        }


@dataclass
class SplitBrainFinding:
    """Divergent fingerprints for the same workstream item."""

    wl_id: str
    fingerprints_by_connector: dict[str, str]
    connectors: list[str]


class CrossConnectorVerifier:
    """Verify status/priority consistency across all connectors per cycle."""

    # Fields that must be consistent across connectors
    CRITICAL_FIELDS: ClassVar[set[str]] = {"status", "priority"}
    FINGERPRINT_FIELDS: ClassVar[tuple[str, ...]] = ("status", "priority")

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

    def state_fingerprint(self, connector_state: dict[str, Any]) -> str:
        """Build canonical fingerprint for connector state."""
        canonical = {field: connector_state.get(field) for field in self.FINGERPRINT_FIELDS}
        payload = json.dumps(canonical, sort_keys=True, separators=(",", ":").decode().decode())
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()

    def detect_split_brain(self, states: list[dict[str, Any]]) -> list[SplitBrainFinding]:
        """Detect per-item connector divergence using state fingerprints."""
        grouped: dict[str, dict[str, str]] = {}
        required_keys = {"wl_id", "connector_name"}
        for state in states:
            missing = required_keys - set(state.keys())
            if missing:
                raise ValueError(f"connector_state missing required keys: {missing}")
            wl_id = str(state["wl_id"])
            connector = str(state["connector_name"])
            grouped.setdefault(wl_id, {})[connector] = self.state_fingerprint(state)

        findings: list[SplitBrainFinding] = []
        for wl_id, by_connector in grouped.items():
            unique = set(by_connector.values())
            if len(unique) <= 1:
                continue
            findings.append(
                SplitBrainFinding(
                    wl_id=wl_id,
                    fingerprints_by_connector=by_connector,
                    connectors=sorted(by_connector.keys()),
                )
            )
        return findings

    def materialize_conflicts(
        self,
        violations: list[ConsistencyViolation],
        *,
        ttl_seconds: int,
        now: datetime | None = None,
    ) -> list[ConflictRecord]:
        """Convert violations to conflict records with first_seen_at + ttl_seconds."""
        timestamp = now or datetime.now(timezone.utc)
        ttl = max(1, int(ttl_seconds))
        return [
            ConflictRecord(
                wl_id=violation.wl_id,
                connector_a=violation.connector_a,
                connector_b=violation.connector_b,
                field=violation.field,
                value_a=violation.value_a,
                value_b=violation.value_b,
                first_seen_at=timestamp,
                ttl_seconds=ttl,
            )
            for violation in violations
        ]

    def escalate_expired_conflicts(
        self,
        conflicts: list[ConflictRecord],
        *,
        now: datetime | None = None,
    ) -> list[ConflictRecord]:
        """Mark conflicts escalated when TTL window has elapsed."""
        at = now or datetime.now(timezone.utc)
        updated: list[ConflictRecord] = []
        for conflict in conflicts:
            expires_at = conflict.first_seen_at + timedelta(seconds=max(1, conflict.ttl_seconds))
            updated.append(replace(conflict, escalated=conflict.escalated or at >= expires_at))
        return updated
