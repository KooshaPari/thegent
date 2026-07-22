"""Orchestration layer — plans, message bus, dispatch, budget tracking.

Public surface
--------------
- :class:`OrchestrationPlan`, :data:`AGENT_HINT`, :data:`BUDGET_TOKENS`, …
  from :mod:`thegent.orchestration.plan`
- :class:`InterAgentMessage`, :class:`MessageBus`,
  :class:`InterAgentProtocol` from :mod:`thegent.orchestration.inter_agent_protocol`
- :class:`BudgetTracker`, :class:`BudgetExceededError` from
  :mod:`thegent.orchestration.budget_tracker`

Hardening (AUDIT-N+33)
----------------------
The re-export surface in this ``__init__`` is the single canonical import
path for orchestration primitives.  Submodules may carry their own
``__all__`` for direct consumers, but new code MUST import from
``thegent.orchestration`` so we have one place to wire deprecation /
aliasing later.

# @trace AUDIT-N+33
"""

from __future__ import annotations

from thegent.orchestration.aggregator import ResultAggregator
from thegent.orchestration.budget_tracker import (
    BudgetExceededError,
    BudgetTracker,
)
from thegent.orchestration.inter_agent_protocol import (
    InterAgentMessage,
    InterAgentProtocol,
    MessageBus,
    MessageType,
)
from thegent.orchestration.plan import (
    AGENT_HINT,
    BUDGET_TIME_S,
    BUDGET_TOKENS,
    MODEL_HINT,
    OUTPUT_SCHEMA,
    PARENT_RUN_ID,
    REQUIRE_HITL,
    SANDBOX,
    OrchestrationPlan,
)
from thegent.orchestration.sub_agent_dispatcher import (
    DispatchResult,
    SubAgentDispatcher,
)

__all__ = [
    "AGENT_HINT",
    "BUDGET_TIME_S",
    "BUDGET_TOKENS",
    "BudgetExceededError",
    "BudgetTracker",
    "DispatchResult",
    "InterAgentMessage",
    "InterAgentProtocol",
    "MessageBus",
    "MessageType",
    "MODEL_HINT",
    "OUTPUT_SCHEMA",
    "OrchestrationPlan",
    "PARENT_RUN_ID",
    "REQUIRE_HITL",
    "ResultAggregator",
    "SANDBOX",
    "SubAgentDispatcher",
]
