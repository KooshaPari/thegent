"""File coordination, OCC, and intent-based conflict prediction.

Canonical home for the 7 public classes / functions that previously lived
in the flat ``src/thegent/mesh/coordination.py`` god-module.

Lineage:
    * SCLI-P6.1  — OptimisticConcurrencyControl (occ.py)
    * SCLI-P6.2  — HLCTimestamp (hlc.py)
    * SCLI-P6.3  — FileClaimsRegistry (leases.py)
    * TGNT-P7.2  — EditIntent / IntentRegistry / ConflictPrediction /
      predict_merge_conflicts (intent.py + predict.py)

Back-compat: every public name is re-exported here so the legacy flat
import path ``from thegent.mesh.coordination import <Name>`` continues to
work — object-identity preserved (no proxies).
"""

from __future__ import annotations

from .hlc import HLCTimestamp
from .intent import ConflictPrediction, EditIntent, IntentRegistry
from .leases import FileClaimsRegistry
from .occ import OptimisticConcurrencyControl
from .predict import _line_ranges_overlap, predict_merge_conflicts

__all__ = [
    "ConflictPrediction",
    "EditIntent",
    "FileClaimsRegistry",
    "HLCTimestamp",
    "IntentRegistry",
    "OptimisticConcurrencyControl",
    "_line_ranges_overlap",
    "predict_merge_conflicts",
]
