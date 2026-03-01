"""Autosync package.

Modular package for workstream autosync functionality.
Target: Under 800 LOC for main runner.
"""

from thegent_sync.autosync.runner import WorkstreamAutosyncRunner
from thegent_sync.autosync.cycle import run_sync_cycle
from thegent_sync.autosync.github_sync import sync_to_github, sync_from_github
from thegent_sync.autosync.linear_sync import sync_to_linear, sync_from_linear

__all__ = [
    "WorkstreamAutosyncRunner",
    "run_sync_cycle",
    "sync_from_github",
    "sync_from_linear",
    "sync_to_github",
    "sync_to_linear",
]
