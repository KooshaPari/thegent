"""Compatibility re-export for git CLI moved to thegent-agint."""

from thegent_agint.cli.commands.cli_git import __all__ as _agint_all
from thegent_agint.cli.commands.cli_git import *  # noqa: F401,F403

__all__ = list(_agint_all)
