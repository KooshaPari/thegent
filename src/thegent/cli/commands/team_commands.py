"""Thegent CLI team commands — backwards-compat wrapper for extracted team subpackage.

This file provides backwards compatibility for code that imports from the old
location. All implementations have been moved to the team/ subpackage.

@trace WL-125: CLI god package decomposition - TEAM domain
"""

from thegent.cli.commands.team.team_commands import *  # noqa: F401, F403 -- WL-125 re-export

__all__ = [
    "team_create_cmd",
    "team_crew_cmd",
    "team_hierarchy_cmd",
    "team_list_cmd",
    "team_task_add_cmd",
    "team_task_list_cmd",
]
