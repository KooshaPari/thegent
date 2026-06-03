"""Resource path helpers."""

from __future__ import annotations

from importlib import resources as pkg_resources
from pathlib import Path


def _find_dev_root(start: Path) -> Path | None:
    try:
        current = start.resolve()
    except Exception:
        return None
    for parent in [current, *current.parents]:
        if (parent / ".git").exists() and (parent / "contracts").exists():
            return parent
    return None


def get_resource_path(resource: str) -> Path:
    dev_root = _find_dev_root(Path(__file__).parent)
    if dev_root is not None:
        candidate = dev_root / resource
        if candidate.exists():
            return candidate
    try:
        with pkg_resources.path("thegent", resource) as path:
            return Path(path)
    except Exception:
        return Path(__file__).parent.parent / resource


__all__ = ["Path", "get_resource_path", "pkg_resources"]
