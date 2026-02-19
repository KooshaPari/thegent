"""Shared utilities for thegent."""

from pathlib import Path

from rich.text import Text


def is_dev_mode() -> bool:
    """Check if thegent is running in development mode.

    Dev mode is active if:
    1. THGENT_DEV=1 is set (via ThegentSettings.dev)
    2. We are running from a git repository and src/thegent exists
    """
    from thegent.config import ThegentSettings

    if ThegentSettings().dev:
        return True

    # Check if we are in a git repo and running from source
    try:
        current_file = Path(__file__).resolve()
        # Expecting .../src/thegent/utils.py
        if "src/thegent" in str(current_file):
            project_root = current_file.parents[2]
            if (project_root / ".git").exists():
                return True
    except Exception:
        pass

    return False


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to a resource file.

    In dev mode, looks in the project root.
    When installed, uses importlib.resources.
    """
    from thegent import resources

    return resources.get_resource_path(relative_path)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences (colors, etc.) from text.
    Uses rich.text.Text.from_ansi() which is the idiomatic way to strip ANSI in Rich.
    """
    if not text:
        return text
    # Text.from_ansi() parses ANSI escape sequences and .plain returns the text without them.
    return Text.from_ansi(text).plain


# Backward compatibility: some code paths (e.g. worktrees) may still reference _strip_ansi
_strip_ansi = strip_ansi
