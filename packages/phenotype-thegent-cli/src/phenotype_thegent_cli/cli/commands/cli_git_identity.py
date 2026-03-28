"""Compatibility re-export for legacy CLI git identity helpers path."""

from phenotype_thegent_cli.commands.cli_git_identity import __all__ as _agint_all
from phenotype_thegent_cli.commands.cli_git_identity import *  # noqa: F401,F403

__all__ = list(_agint_all)
