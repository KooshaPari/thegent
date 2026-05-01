"""STUB MODULE - thegent.commands.idea_seeds

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IdeaSeed:
    """An idea seed for idea generation."""
    id: str
    title: str
    description: str = ""
    category: str = "general"


# Default file extensions for idea seeds
DEFAULT_EXTENSIONS = [".py", ".js", ".ts", ".md", ".txt"]

# Seed patterns for idea generation
SEED_PATTERNS = [
    "feature_*",
    "bugfix_*",
    "refactor_*",
]


__all__ = ["DEFAULT_EXTENSIONS", "SEED_PATTERNS", "IdeaSeed", "IdeaSeedScanner"]


class IdeaSeedScanner:
    """Scanner for idea seeds."""

    def __init__(self, patterns: list[str] | None = None) -> None:
        self.patterns = patterns or SEED_PATTERNS

    def scan(self, directory: str) -> list[IdeaSeed]:
        """Scan directory for idea seeds."""
        return []
