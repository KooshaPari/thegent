"""Thegent CLI conversation dump commands (extracted from team_cmds.py)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import sys
from pathlib import Path

from thegent_cli.cli.commands._cli_shared import (
    _normalize_output_format,
    console,
)


def dump_index_cmd(project: Path | None = None, format: str | None = None) -> None:
    """Generate and display dump category index."""
    from thegent_planning.research.always_write_dumps import ConversationDumper

    project_path = project or Path.cwd()
    dumper = ConversationDumper(docs_dir=project_path / "docs" / "dumps")
    index_path = dumper.persist_dump_index()
    markdown_path = dumper.export_dump_index_markdown()
    payload = {"index_path": str(index_path), "markdown_path": str(markdown_path)}
    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    console.print(f"[green]Dump index[/green] json={payload['index_path']} md={payload['markdown_path']}")


def dump_latest_cmd(
    project: Path | None = None,
    category: str | None = None,
    json_only: bool = False,
    format: str | None = None,
) -> None:
    """Show latest dump path for a category or globally."""
    from thegent_planning.research.always_write_dumps import ConversationDumper

    project_path = project or Path.cwd()
    dumper = ConversationDumper(docs_dir=project_path / "docs" / "dumps")
    normalized_category = category.strip() if category is not None else None
    latest = dumper.latest_dump(category=normalized_category or None, json_only=json_only)
    payload = {"latest": str(latest) if latest else None}
    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    console.print(payload["latest"] or "(none)")


def dump_categories_cmd(project: Path | None = None, format: str | None = None) -> None:
    """List available dump categories."""
    from thegent_planning.research.always_write_dumps import ConversationDumper

    project_path = project or Path.cwd()
    dumper = ConversationDumper(docs_dir=project_path / "docs" / "dumps")
    categories = dumper.list_dump_categories()
    payload = {"categories": categories, "count": len(categories)}
    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    console.print(f"[bold cyan]Dump Categories[/bold cyan]: {payload['count']}")
    console.print(", ".join(categories) if categories else "(none)")


__all__ = [
    "dump_categories_cmd",
    "dump_index_cmd",
    "dump_latest_cmd",
]
