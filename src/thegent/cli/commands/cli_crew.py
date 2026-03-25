"""Thegent CLI crew commands — backwards-compat wrapper for extracted team subpackage.

This file provides backwards compatibility for code that imports from the old
location. All implementations have been moved to the team/ subpackage.

@trace WL-125: CLI god package decomposition - TEAM domain
"""

from thegent.cli.commands.team.cli_crew import *  # noqa: F401, F403 -- WL-125 re-export

__all__ = [
    "crew_add_agent_cmd",
    "crew_add_task_cmd",
    "crew_create_cmd",
    "crew_execute_cmd",
    "crew_list_cmd",
    "crew_show_cmd",
    "crew_status_cmd",
]
