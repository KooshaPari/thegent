"""Back-compat shim — canonical home is :mod:`thegent.mesh.consensus` package.

The single-file ``mesh/consensus.py`` (368 LOC, 3 classes, CC=12 on
``get_consensus``) was split into a 3-submodule package during WL705 L1
Architecture hardening:

* :mod:`thegent.mesh.consensus.protocol` — ``ConsensusProtocol`` +
  ``ConsensusStatus`` (ADR-013 / SCLI-P3.1).
* :mod:`thegent.mesh.consensus.influence` — ``CausalInfluenceTracker``
  (SCLI-P3.2).
* :mod:`thegent.mesh.consensus.escalation` — ``EscalationWorkflow``
  (SCLI-P3.3 / SCLI-P3.4).

This shim re-exports the canonical surface so any out-of-tree plugin
that imports ``from thegent.mesh.consensus import ConsensusProtocol``
continues to resolve against the canonical package.
"""

from __future__ import annotations

from .consensus.escalation import EscalationWorkflow
from .consensus.influence import CausalInfluenceTracker
from .consensus.protocol import ConsensusProtocol, ConsensusStatus

__all__ = [
    "ConsensusStatus",
    "ConsensusProtocol",
    "CausalInfluenceTracker",
    "EscalationWorkflow",
]
