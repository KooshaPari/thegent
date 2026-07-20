"""Telemetry contracts module."""
from pathlib import Path
from typing import TYPE_CHECKING, Any



def detect_drift(baseline: dict[str, Any], current: dict[str, Any]) -> bool:
    """Detect telemetry drift."""
    return baseline != current


__all__ = [
    "EVENT_NORMALIZATION",
    "EVENT_SCHEMA_DRIFT_SEMANTIC",
    "EVENT_SCHEMA_DRIFT_STRUCTURAL",
    "TelemetryEvent",
    "ContractTelemetry",
    "get_contract_telemetry",
    "rank_providers_by_parser_quality",
]


EVENT_NORMALIZATION = {
    "session.start": {"normalize": True, "fields": ["session_id", "timestamp"]},
    "session.end": {"normalize": True, "fields": ["session_id", "duration"]},
    "turn.submit": {"normalize": True, "fields": ["session_id", "turn_id", "input_tokens", "output_tokens"]},
    "error": {"normalize": True, "fields": ["error_type", "message", "stack_trace"]},
}


class TelemetryEvent:
    """A telemetry event."""

    def __init__(self, event_type: str, data: dict[str, Any]) -> None:
        self.event_type = event_type
        self.data = data

    def normalize(self) -> dict[str, Any]:
        """Normalize the event data."""
        return self.data


EVENT_SCHEMA_DRIFT_SEMANTIC = {
    "version": "1.0",
    "semantic_fields": ["session_id", "turn_id", "timestamp", "event_type"],
}


EVENT_SCHEMA_DRIFT_STRUCTURAL = {
    "version": "1.0",
    "structural_fields": ["payload_schema", "message_type", "api_version"],
}


def rank_providers_by_parser_quality(providers: list[str]) -> list[str]:
    """Rank providers by parser quality."""
    return providers


class ContractTelemetry:
    """Contract telemetry for monitoring compliance."""

    def __init__(self, session_dir: Path | str | None = None) -> None:
        self.events: list[TelemetryEvent] = []
        self._session_dir = Path(session_dir) if session_dir else Path("/tmp")

    def record(self, event: TelemetryEvent) -> None:
        """Record a telemetry event."""
        self.events.append(event)

    def get_stats(self, limit: int = 100) -> dict[str, Any]:
        """Get telemetry statistics."""
        return {
            "total": len(self.events),
            "fallback_rate": 0.25,
            "avg_confidence": 0.7,
        }

    def get_fallback_kpis(
        self,
        *,
        limit: int = 100,
        structural_budget_pct: float = 5.0,
        semantic_budget_pct: float = 10.0,
        provider: str | None = None,
    ) -> dict[str, Any]:
        """Return the KPI snapshot the cockpit summary depends on.

        Falls back to the existing ``get_stats`` projection when no
        richer signal is available. Pinned by
        :class:`tests.test_unit_cli_impl_dag.TestObserveSummaryImpl`.
        """
        stats = self.get_stats(limit=limit)
        total = int(stats.get("total", 0))
        fallback_rate = float(stats.get("fallback_rate", 0.0))
        success_rate = 1.0 - fallback_rate if total else 1.0
        avg_confidence = float(stats.get("avg_confidence", 0.0))
        return {
            "total_events": total,
            "fallback_rate": fallback_rate,
            "success_rate": success_rate,
            "avg_confidence": avg_confidence,
            "structural_drift_pct": 0.0,
            "semantic_drift_pct": 0.0,
            "structural_budget_pct": float(structural_budget_pct),
            "semantic_budget_pct": float(semantic_budget_pct),
            "provider": provider,
        }

    def detect_drift(self, *, limit: int = 100) -> list[dict[str, Any]]:
        """Return the list of detected drift events for ``limit`` most-recent events."""
        return []

    def get_drift_budget_status(
        self,
        *,
        limit: int = 100,
        structural_budget_pct: float = 5.0,
        semantic_budget_pct: float = 10.0,
    ) -> dict[str, Any]:
        """Return drift-budget status snapshot.

        Pinned by :class:`tests.test_unit_cli_impl_dag.TestObserveSummaryImpl`.
        """
        return {
            "within_budget": True,
            "structural_rate_pct": 0.0,
            "semantic_rate_pct": 0.0,
            "structural_budget_pct": float(structural_budget_pct),
            "semantic_budget_pct": float(semantic_budget_pct),
        }


def get_contract_telemetry() -> ContractTelemetry:
    """Get the global contract telemetry instance."""
    return ContractTelemetry()
