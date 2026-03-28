"""Project command group extracted from cli.py (WL-124)."""

from __future__ import annotations

import orjson as json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rich.table import Table


def project_register_cmd(*, path: Path, name: str | None = None, console: Any) -> None:
    """Register a new project (WP-4008)."""
    from thegent_core.config import ThegentSettings

    settings = ThegentSettings()
    projects_file = settings.session_dir / "projects.jsonl"
    project = {"path": str(path.resolve()), "name": name or path.name, "registered_at": datetime.now(UTC).isoformat()}
    with projects_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(project).decode().decode() + "\n")
    console.print(f"Project registered: [bold green]{project['name']}[/bold green] at {project['path']}")


def project_list_cmd(*, format: str | None = None, console: Any) -> None:
    """List all registered projects (WP-4008)."""
    from thegent_core.config import ThegentSettings

    _fmt = (format or "rich").lower().strip()
    settings = ThegentSettings()
    projects_file = settings.session_dir / "projects.jsonl"
    if not projects_file.exists():
        if _fmt == "json":
            sys.stdout.write(json.dumps([]).decode().decode() + "\n")
        else:
            console.print("No projects registered.")
        return

    if _fmt == "json":
        rows: list[dict[str, Any]] = []
        with projects_file.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        sys.stdout.write(json.dumps(rows).decode().decode() + "\n")
        return

    table = Table(title="Registered Projects")
    table.add_column("Name", style="bold green")
    table.add_column("Path", style="cyan")

    with projects_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            _add_project_to_table(table, line)
    console.print(table)


def _add_project_to_table(table: Table, line: str) -> None:
    """Add a project to the table safely from a line in projects.jsonl."""
    payload = json.loads(line)
    table.add_row(payload["name"], payload["path"])


__all__ = ["project_list_cmd", "project_register_cmd"]
