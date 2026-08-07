"""thegent.mesh.consensus — canonical consensus + escalation protocols (ADR-013, SCLI-P3.x).

This package is the canonical home for the mesh consensus surface, extracted
from the legacy single-file ``thegent.mesh.consensus`` module during
WL705 L1 Architecture hardening.

Sub-modules:

* :mod:`thegent.mesh.consensus.protocol` — ``ConsensusStatus`` enum and
  ``ConsensusProtocol`` (CP-WBFT) implementing the five-phase ADR-013
  flow (PROPOSE → DRAFT → SHARE → VOTE → TALLY & DECIDE).
* :mod:`thegent.mesh.consensus.influence` — ``CausalInfluenceTracker``
  (SCLI-P3.2 Shapley-value attribution).
* :mod:`thegent.mesh.consensus.escalation` — ``EscalationWorkflow`` with
  the five-tier SCLI-P3.3 escalation ladder and the SCLI-P3.4 asynchronous
  human escalation queue.
* :mod:`thegent.mesh.consensus._io` — Shared atomic-write + safe-load
  helpers used by all three protocol modules.

The legacy ``thegent.mesh.consensus`` (single-file) import path is
preserved as a thin back-compat shim — see
:mod:`thegent.mesh.consensus.__init__` of the parent module.
"""

from __future__ import annotations

from .escalation import EscalationWorkflow
from .influence import CausalInfluenceTracker
from .protocol import ConsensusProtocol, ConsensusStatus

__all__ = [
    "ConsensusStatus",
    "ConsensusProtocol",
    "CausalInfluenceTracker",
    "EscalationWorkflow",
]
