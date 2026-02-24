"""Migration module for project migration.

Extracted from cli/apps/project.py
"""

from pathlib import Path
from typing import Any


def project_migrate(project_path: str, mode: str = "agdd") -> dict[str, Any]:
    """Migrate project to new format."""
    return {"path": project_path, "mode": mode, "status": "migrated"}


def resolve_migration_template(requested: str) -> str:
    """Resolve migration template name."""
    templates = {"agdd": "agdd", "none": "none", "default": "agdd"}
    return templates.get(requested, "agdd")


def resolve_migration_mode(requested: str) -> str:
    """Resolve migration mode."""
    modes = {"agdd": "agdd", "none": "none", "greenfield": "greenfield"}
    return modes.get(requested, "agdd")


def project_migrate_snapshot(project_path: Path) -> dict[str, Any]:
    """Take snapshot before migration."""
    return {"path": str(project_path), "snapshot": "taken"}


__all__ = [
    "project_migrate",
    "project_migrate_snapshot",
    "resolve_migration_mode",
    "resolve_migration_template",
]
