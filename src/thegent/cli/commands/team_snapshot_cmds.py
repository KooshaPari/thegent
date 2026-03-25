"""Thegent CLI team snapshot commands — backwards-compat wrapper for extracted team subpackage.

This file provides backwards compatibility for code that imports from the old
location. All implementations have been moved to the team/ subpackage.

@trace WL-125: CLI god package decomposition - TEAM domain
"""

from thegent.cli.commands.team.team_snapshot_cmds import *  # noqa: F401, F403 -- WL-125 re-export

__all__ = [
    "snapshot_daily_export_cmd",
    "snapshot_daily_index_cmd",
    "snapshot_daily_totals_cmd",
    "snapshot_export_cmd",
    "snapshot_index_cmd",
    "snapshot_list_cmd",
    "snapshot_meta_cmd",
    "snapshot_prune_cmd",
]
