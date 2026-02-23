"""Scaffold module for project creation.

Extracted from cli/apps/project.py
"""

from pathlib import Path
from typing import Any


def _slug(name: str) -> str:
    """Convert name to slug format."""
    return name.lower().replace(" ", "-").replace("_", "-")


def scaffold_greenfield(project_name: str, template: str = "default") -> dict[str, Any]:
    """Create new greenfield project from template."""
    return {"name": project_name, "template": template, "type": "greenfield"}


def scaffold_brownfield(project_path: str, mode: str = "agdd") -> dict[str, Any]:
    """Scaffold existing project."""
    return {"path": project_path, "mode": mode, "type": "brownfield"}


def scaffold_brownfield_agdd(project_path: str) -> dict[str, Any]:
    """Scaffold AGDD project."""
    return scaffold_brownfield(project_path, "agdd")


def scaffold_brownfield_none(project_path: str) -> dict[str, Any]:
    """Scaffold bare project."""
    return scaffold_brownfield(project_path, "none")


def build_scaffold_data(project_name: str, template: str) -> dict[str, Any]:
    """Build scaffold data for project."""
    return {
        "name": project_name,
        "slug": _slug(project_name),
        "template": template,
    }


__all__ = [
    "build_scaffold_data",
    "scaffold_brownfield",
    "scaffold_brownfield_agdd",
    "scaffold_brownfield_none",
    "scaffold_greenfield",
]
