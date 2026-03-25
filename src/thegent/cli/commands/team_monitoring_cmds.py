"""DEPRECATED: Backwards-compatibility wrapper for team_monitoring_cmds.

This file has been moved to thegent.cli.commands.observability.team_monitoring_cmds.
All imports are re-exported from the new location.

@deprecated Use thegent.cli.commands.observability.team_monitoring_cmds instead.
"""

from __future__ import annotations

# Re-export all team monitoring commands from new location
from thegent.cli.commands.observability.team_monitoring_cmds import *  # noqa: F401, F403
