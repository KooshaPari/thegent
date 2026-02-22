"""Connector health scoreboard helpers.

# @trace WL-209
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectorHealth:
    connector: str
    success_rate: float
    drift_count: int

    @property
    def score(self) -> int:
        bounded_rate = max(0.0, min(1.0, self.success_rate))
        base = round(bounded_rate * 100)
        penalty = self.drift_count * 5
        return max(0, min(100, base - penalty))

    @property
    def band(self) -> str:
        if self.score >= 90:
            return "green"
        if self.score >= 70:
            return "yellow"
        return "red"


def render_health_scoreboard(rows: list[ConnectorHealth]) -> list[str]:
    ordered = sorted(rows, key=lambda row: row.score, reverse=True)
    return [f"{row.connector} score={row.score} band={row.band} drift={row.drift_count}" for row in ordered]

