"""DEPRECATED: Backwards-compatibility wrapper for infra_observe_cmds.

This file has been moved to thegent.cli.commands.observability.infra_observe_cmds.
All imports are re-exported from the new location.

@deprecated Use thegent.cli.commands.observability.infra_observe_cmds instead.
"""

from __future__ import annotations

# Re-export all infra observability commands from new location
from thegent.cli.commands.observability.infra_observe_cmds import *  # noqa: F401, F403
