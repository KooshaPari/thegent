"""thegent CLI module.

This module provides the command-line interface for thegent.
"""

from __future__ import annotations

from thegent.cli import run_cmd, bg_cmd
from thegent.cli.commands import impl

__all__ = ["run_cmd", "bg_cmd", "impl"]
