"""Thegent CLI team monitoring commands — backwards-compat wrapper for extracted team subpackage.

This file provides backwards compatibility for code that imports from the old
location. All implementations have been moved to the team/ subpackage.

@trace WL-125: CLI god package decomposition - TEAM domain
"""

from thegent.cli.commands.team.team_monitoring_cmds import *  # noqa: F401, F403 -- WL-125 re-export

__all__ = [
    "dlq_list_cmd",
    "drift_monitor_cmd",
    "roadmap_cmd",
    "self_heal_tests_cmd",
    "traffic_cmd",
    "watchdog_cmd",
]
