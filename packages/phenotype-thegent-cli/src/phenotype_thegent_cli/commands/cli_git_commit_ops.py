"""Compatibility re-export for commit/add/status operations owned by thegent-agint."""

from phenotype_thegent_agint.cli.commands.cli_git_commit_ops import __all__ as _agint_all
from phenotype_thegent_agint.cli.commands.cli_git_commit_ops import *  # noqa: F401,F403

__all__ = list(_agint_all)
