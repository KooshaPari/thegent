"""Backwards-compatibility shim — re-exports from ``sub_agent_dispatcher``.

The canonical implementation of :class:`SubAgentDispatcher` and
:class:`DispatchResult` lives in
:mod:`thegent.orchestration.sub_agent_dispatcher`.  This module is
preserved so legacy imports of ``from thegent.orchestration.dispatcher
import SubAgentDispatcher`` continue to resolve.

# @trace AUDIT-N+33
# @trace AUDIT-LANE-DISPATCHCONFIG-001
"""

from __future__ import annotations

from dataclasses import dataclass

from thegent.orchestration.sub_agent_dispatcher import (  # noqa: F401
    CapabilityIndex,
    DispatchResult,
    SubAgentDispatcher,
    is_cli_harness,
)


@dataclass(frozen=True)
class DispatchConfig:
    """Minimal dispatcher configuration object.

    Exposed at :mod:`thegent.orchestration.dispatcher` for backwards
    compatibility — older callers (notably
    ``tests/test_wl681x_lane_d.py``) construct ``SubAgentDispatcher``
    with ``config=DispatchConfig(...)`` and read back the ``hitl_enabled``
    flag.

    Only the fields exercised by the legacy test contract are declared
    here.  The canonical dispatcher (see
    :mod:`thegent.orchestration.sub_agent_dispatcher`) treats ``config``
    as an opaque attribute and does not introspect its fields; future
    hardening should add fields as they become necessary.

    @trace AUDIT-LANE-DISPATCHCONFIG-001
    """

    hitl_enabled: bool = False


__all__ = [
    "CapabilityIndex",
    "DispatchConfig",
    "DispatchResult",
    "SubAgentDispatcher",
    "is_cli_harness",
]
