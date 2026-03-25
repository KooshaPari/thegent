"""Thegent CLI team commands (consolidation) — backwards-compat wrapper for extracted team subpackage.

This file provides backwards compatibility for code that imports from the old
location. All implementations have been moved to the team/ subpackage.

@trace WL-125: CLI god package decomposition - TEAM domain
"""

from thegent.cli.commands.team.team_cmds import *  # noqa: F401, F403 -- WL-125 re-export

__all__ = [
    "dlq_list_cmd",
    "drift_monitor_cmd",
    "dump_categories_cmd",
    "dump_index_cmd",
    "dump_latest_cmd",
    "explain_cmd",
    "fallbacks_cmd",
    "handoff_cmd",
    "handoff_confirm_cmd",
    "handoff_list_cmd",
    "handoff_show_cmd",
    "project_list_cmd",
    "project_register_cmd",
    "queue_list_cmd",
    "recover_status_cmd",
    "roadmap_cmd",
    "self_heal_tests_cmd",
    "snapshot_daily_export_cmd",
    "snapshot_daily_index_cmd",
    "snapshot_daily_totals_cmd",
    "snapshot_export_cmd",
    "snapshot_index_cmd",
    "snapshot_list_cmd",
    "snapshot_meta_cmd",
    "snapshot_prune_cmd",
    "summary_cmd",
    "team_create_cmd",
    "team_task_add_cmd",
    "team_task_list_cmd",
]
