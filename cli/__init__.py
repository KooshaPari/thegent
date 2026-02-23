# thegent-cli
# CLI entry point sub-project
# Extracted from main repo - Phase 2 P2.1

__version__ = "0.1.0"

from .commands import main, run, list_commands
from .parser import parse_args

__all__ = ["main", "run", "list_commands", "parse_args"]
