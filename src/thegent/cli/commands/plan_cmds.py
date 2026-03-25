"""Backward compatibility shim for plan commands.

Phase 3 extraction (WL-125): Plan domain moved to thegent.cli.plan.

This module provides backward compatibility for code that imports from
the old location. All real functionality has been moved to the plan subpackage.
"""

# @trace WL-125 Phase-3 PLAN domain extraction

from __future__ import annotations

# Re-export everything from the new location
from thegent.cli.plan import *  # noqa: F401, F403 -- backward compatibility re-export
