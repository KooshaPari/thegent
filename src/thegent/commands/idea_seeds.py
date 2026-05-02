"""STUB MODULE - thegent.commands.idea_seeds

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


def _make_slug(text: str) -> str:
    """Create a URL-safe slug from text.

    Args:
        text: Text to slugify.

    Returns:
        Slugified text.
    """
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[_\s]+", "-", slug)
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    return slug


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
