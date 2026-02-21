"""Project root detection helpers for doctor."""

from pathlib import Path


def detect_project_root(start: Path | None = None) -> Path:
    """Detect the nearest project root containing src/thegent."""
    project_root = start or Path.cwd()
    if (project_root / "src" / "thegent").exists():
        return project_root

    curr = project_root
    while curr.parent != curr:
        if (curr / "src" / "thegent").exists():
            return curr
        curr = curr.parent

    return project_root
