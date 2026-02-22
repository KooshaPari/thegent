"""Utility functions and helpers."""

from rich.text import Text


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text. Uses rich Text.from_ansi().plain."""
    if not text:
        return text
    return Text.from_ansi(text).plain


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
        from pathlib import Path

        current_file = Path(__file__).resolve()
        # Expecting .../src/thegent/utils/__init__.py
        if "src/thegent" in str(current_file):
            project_root = current_file.parents[3]  # One level deeper than utils.py
            if (project_root / ".git").exists():
                return True
    except Exception:
        pass

    return False


def get_resource_path(relative_path: str):
    """Get absolute path to a resource file.

    In dev mode, looks in the project root.
    When installed, uses importlib.resources.
    """
    from thegent import resources

    return resources.get_resource_path(relative_path)
