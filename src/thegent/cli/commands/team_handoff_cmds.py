"""Thegent CLI team handoff commands — backwards-compat wrapper for extracted team subpackage.

This file provides backwards compatibility for code that imports from the old
location. All implementations have been moved to the team/ subpackage.

@trace WL-125: CLI god package decomposition - TEAM domain
"""

from thegent.cli.commands.team.team_handoff_cmds import *  # noqa: F401, F403 -- WL-125 re-export

__all__ = [
    "handoff_cmd",
    "handoff_confirm_cmd",
    "handoff_list_cmd",
    "handoff_show_cmd",
]
