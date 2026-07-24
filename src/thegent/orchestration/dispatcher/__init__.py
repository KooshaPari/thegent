"""Backwards-compatibility shim — re-exports from ``sub_agent_dispatcher``.

The canonical implementation of :class:`SubAgentDispatcher` and
:class:`DispatchResult` lives in
:mod:`thegent.orchestration.sub_agent_dispatcher`.  This module is
preserved so legacy imports of ``from thegent.orchestration.dispatcher
import SubAgentDispatcher`` continue to resolve.

# @trace AUDIT-N+33
"""

from __future__ import annotations

from thegent.orchestration.sub_agent_dispatcher import (  # noqa: F401
    CapabilityIndex,
    DispatchResult,
    SubAgentDispatcher,
    is_cli_harness,
)

__all__ = [
    "CapabilityIndex",
    "DispatchResult",
    "SubAgentDispatcher",
    "is_cli_harness",
]
