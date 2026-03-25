"""Compatibility re-export for legacy CLI git commands package entrypoint."""

from thegent_cli.commands.cli_git import __all__ as _agint_all
from thegent_cli.commands.cli_git import *  # noqa: F401,F403

__all__ = list(_agint_all)
