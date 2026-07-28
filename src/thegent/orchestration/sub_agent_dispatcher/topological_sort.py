"""Topological sort for :class:`OrchestrationPlan` graphs.

Re-exports the private ``_topological_order`` helper from the
sub-agent dispatcher so that performance benchmarks and external
callers can import a stable public API without reaching into
implementation details.

# @trace WL-082
"""

from __future__ import annotations

from thegent.orchestration.plan import OrchestrationPlan
from thegent.orchestration.sub_agent_dispatcher import _topological_order


def topological_order(plan: OrchestrationPlan) -> list:  # type: ignore[type-arg]
    """Return *plan.nodes* in deterministic topological order.

    Delegates to the canonical Kahn's-algorithm implementation in
    :mod:`thegent.orchestration.sub_agent_dispatcher`.  Cycles raise
    :class:`ValueError`.
    """
    return _topological_order(plan)


__all__ = ["topological_order"]
