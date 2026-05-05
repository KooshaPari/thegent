"""thegent.cli.commands - CLI commands package.

This package contains the CLI command implementations extracted from the
main CLI module.
"""

from __future__ import annotations

import getpass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer

if TYPE_CHECKING:
    from thegent.config import ThegentSettings

# Re-export command modules
from thegent.cli.commands import impl, cli, cli_dag, plan_cmds, infra_cmds, _cli_shared
from thegent.cli.commands import team_commands as team_cmds
from thegent.cli.commands import cli_git_worktree_governance
from thegent.cli.commands import cli_git_identity
from thegent.cli.commands import work_stream_impl
from thegent.cli.commands import model_cmds

# Re-export commonly used items
from thegent.cli.commands.model_cmds import model_cmds_list
from thegent.cli.commands import session_owner_helpers

__all__ = [
    "impl",
    "cli",
    "cli_dag",
    "plan_cmds",
    "team_cmds",
    "infra_cmds",
    "_cli_shared",
    "cli_git_worktree_governance",
    "cli_git_identity",
    "work_stream_impl",
    "model_cmds",
    "model_cmds_list",
    "session_owner_helpers",
]
