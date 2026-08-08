"""Hybrid Logical Clock (HLC) primitive (SCLI-P6.2).

Canonical home for ``HLCTimestamp``. Backed by ``src/thegent/mesh/coordination/hlc.py``.
The legacy flat path ``from thegent.mesh.coordination import HLCTimestamp`` is preserved
as a re-export in ``src/thegent/mesh/coordination/__init__.py``.
"""

from __future__ import annotations

import time
from typing import Optional


class HLCTimestamp:
    """Hybrid Logical Clock (HLC) (SCLI-P6.2).

    Combines physical wall-clock millis with a per-clock logical counter to
    preserve monotonic ordering across distributed nodes without requiring
    synchronised time.
    """

    def __init__(self, physical: int = 0, logical: int = 0) -> None:
        self.physical = physical or int(time.time() * 1000)
        self.logical = logical

    def update(self, other: Optional["HLCTimestamp"] = None) -> "HLCTimestamp":
        """Update clock with physical and/or other logical clock."""
        now = int(time.time() * 1000)
        if other:
            self.physical = max(self.physical, other.physical, now)
            if self.physical == other.physical:
                self.logical = max(self.logical, other.logical) + 1
            else:
                self.logical = 0
        else:
            self.physical = max(self.physical, now)
            if self.physical == now:
                self.logical = 0
            else:
                self.logical += 1
        return self

    def __str__(self) -> str:
        return f"{self.physical}:{self.logical:04x}"

    @classmethod
    def parse(cls, s: str) -> "HLCTimestamp":
        """Parse HLC timestamp from string."""
        parts = s.split(":")
        if len(parts) == 2:
            return cls(int(parts[0]), int(parts[1], 16))
        return cls()


__all__ = ["HLCTimestamp"]
