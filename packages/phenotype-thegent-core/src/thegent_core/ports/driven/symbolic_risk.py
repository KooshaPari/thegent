"""SymbolicRiskPort: Abstract protocol for symbolic risk exploration.

This port breaks the circular dependency between thegent-core and
thegent-audit: core/models/hybrid_router.py used to import directly from
thegent_audit.verification.symbolic.  Now core defines this abstract
protocol; the concrete implementation (SymbolicRiskExplorer) stays in
thegent-audit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass
class RiskPath:
    """A specific execution path with its associated risk score.

    This mirrors thegent_audit.verification.symbolic.RiskPath so that
    thegent-core does not need to import from thegent-audit.
    """

    path_id: str
    nodes: list[str]
    risk_score: float  # 0.0 - 1.0
    threat_category: str


@runtime_checkable
class SymbolicRiskPort(Protocol):
    """Port for symbolic risk exploration of task DAGs.

    The concrete implementation (SymbolicRiskExplorer) lives in thegent-audit.
    Core code only depends on this abstract protocol.
    """

    def explore(self, start_node: str) -> list[RiskPath]:
        """Explore all reachable paths from *start_node* and return risk paths."""
        ...

    def get_highest_risk_path(self) -> RiskPath | None:
        """Return the path with the highest risk score, or None if no paths exist."""
        ...


class NullSymbolicRiskPort:
    """Null-object implementation of SymbolicRiskPort.

    Used as fallback when thegent-audit is not available.  Returns empty
    exploration results and a zero-risk path.
    """

    def __init__(self, dag: Any | None = None) -> None:
        self._dag = dag
        self._risk_paths: list[RiskPath] = []

    def explore(self, start_node: str) -> list[RiskPath]:
        """Return an empty risk-path list."""
        self._risk_paths = []
        return self._risk_paths

    def get_highest_risk_path(self) -> RiskPath | None:
        """Return None — no paths were explored."""
        if not self._risk_paths:
            return None
        return max(self._risk_paths, key=lambda x: x.risk_score)


__all__ = [
    "NullSymbolicRiskPort",
    "RiskPath",
    "SymbolicRiskPort",
]
