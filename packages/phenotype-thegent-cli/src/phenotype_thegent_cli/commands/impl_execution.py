"""Execution core boundary module extracted from impl.py (WL-120 B90-W2-A2).

Canonical boundary: run_impl, bg_impl, resume_impl, loop_impl.

These four functions are the primary execution entry points for the CLI:
- run_impl   — synchronous foreground agent run
- bg_impl    — background agent spawn
- resume_impl — WL-110 stable session resume with state-contract lookup
- loop_impl  — lifecycle loop with checker oversight (WP-4008)

This module imports the authoritative implementations from impl.py and
re-exports them under the impl_execution namespace.  Once all callers
are updated to import from impl_execution instead of impl, the bodies
can be migrated here in a follow-on sprint (WL-120 Phase 3).
"""
# @trace WL-120 B90-W2-A2

from __future__ import annotations

from phenotype_thegent_cli.commands.impl import (
    bg_impl,
    loop_impl,
    resume_impl,
    run_impl,
)

__all__ = [
    "bg_impl",
    "loop_impl",
    "resume_impl",
    "run_impl",
]
