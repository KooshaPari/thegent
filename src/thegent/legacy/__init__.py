"""DEPRECATED: Legacy module for god function isolation.

This module is a temporary home for orchestration code during the
Phase 2-3 refactoring. Scheduled for removal in Q3 2026.

DECOMPOSITION STATUS (Phase 4 — 2026-04-24):
✅ run_impl_core orchestration split into named layers:
   - execution.executor: Pure orchestration (Executor class)
   - execution.planner: Task planning (Planner class)
   - execution.router: Request routing (Router class)
   - agents/loop_controller: Agent invocation (via ExecutionPort)
   - planning/auto_launch: Automatic task launching (via ExecutionPort)

✅ Circular dependencies eliminated (8 → 0)
✅ CLI imports removed from execution layer
✅ ExecutionPort pattern: agents call CLI via interface (not imports)
✅ Zero cycles validated with tach (forbid_circular_dependencies=true)

DEPRECATION TIMELINE:
- Phase 4 (2026-04-24): Isolation confirmed, deprecation marked
- Q3 2026: Full removal of thegent.legacy module

DO NOT add new code here. All new work goes to thegent.execution or
appropriate layer. If you're modifying run_impl_core or similar,
create an issue to track its decomposition.

See:
- docs/refactor/circular_deps_remediation_plan.md (Phase 4 results)
- docs/refactor/split_boundaries.md (5-way architecture)
- tach.toml (dependency boundaries enforcement)
"""
from __future__ import annotations

import warnings

__all__ = []

# Warn on import (will be removed in Q3 2026)
warnings.warn(
    "thegent.legacy is deprecated and will be removed in Q3 2026. "
    "Use thegent.execution or appropriate layer instead.",
    DeprecationWarning,
    stacklevel=2,
)
