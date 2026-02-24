"""Path utility functions."""

from pathlib import Path
from typing import Any


def normalize_path(path: str | Path) -> Path:
    """Normalize a path."""
    return Path(path).resolve()


def path_to_str(path: str | Path | None) -> str:
    """Convert path to string."""
    if path is None:
        return ""
    return str(path)


def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def safe_join(base: Path, name: str) -> Path:
    """Safely join path components."""
    return base / name
