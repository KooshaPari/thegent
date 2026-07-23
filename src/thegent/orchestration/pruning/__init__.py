"""Pruning package (AUDIT-N+39 hardened).

Re-exports the two submodules so callers can ``import thegent.
orchestration.pruning.prune`` / ``.smart_prune`` via the canonical
package path (mirrors the ``consensus`` re-export pattern from
AUDIT-N+38).
"""

from __future__ import annotations

from thegent.orchestration.pruning import prune, smart_prune

__all__ = ["prune", "smart_prune"]
