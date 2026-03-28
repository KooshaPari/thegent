"""Compatibility re-export for git identity resolution owned by thegent-agint."""

from phenotype_thegent_agint.cli.commands.cli_git_identity import __all__ as _agint_all
from phenotype_thegent_agint.cli.commands.cli_git_identity import *  # noqa: F401,F403

__all__ = list(_agint_all)
