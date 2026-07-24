"""Orchestration execution module (dormant-core: re-export shim).

The authoritative :class:`ExecutionEngine` lives in
:mod:`thegent.orchestration.execution.engine`. This module is kept as
a thin re-export shim so legacy imports of
``thegent.orchestration.execution.ExecutionEngine`` continue to work.
"""

from __future__ import annotations

from typing import Any

from thegent.orchestration.execution.engine import ExecutionEngine

__all__ = ["ExecutionEngine", "ExecutionContext"]


class ExecutionContext:
    """Lightweight container for execution metadata + result.

    Retained from the dormant surface for parity with the legacy API.
    """

    def __init__(self, task: Any) -> None:
        self.task = task
        self.metadata: dict[str, Any] = {}

    def set_result(self, result: Any) -> None:
        """Set execution result."""
        self.metadata["result"] = result

    def get_result(self) -> Any:
        """Get execution result."""
        return self.metadata.get("result")
