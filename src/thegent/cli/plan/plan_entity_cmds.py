"""Canonical workstream entity commands."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any

import orjson as json
import typer
from rich.table import Table

from thegent.cli.commands._cli_shared import _resolve_cwd, console
from thegent.planning.workstream_entities import entity_operation

app = typer.Typer(help="Canonical workstream entity CRUD, batch import, export, and sync.")


def _parse_properties(values: list[str] | None, source: Path | None = None) -> dict[str, Any]:
    props: dict[str, Any] = {}
    if source is not None:
        payload = json.loads(source.read_bytes())
        if isinstance(payload, dict):
            props.update(payload)
    for item in values or []:
        if "=" not in item:
            raise typer.BadParameter(f"Expected KEY=VALUE, got {item!r}")
        key, raw_value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise typer.BadParameter("Property key cannot be empty")
        with contextlib.suppress(Exception):
            props[key] = json.loads(raw_value)
            continue
        props[key] = raw_value
    return props


def _load_records(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_bytes())
    except Exception:
        payload = None

    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        items = payload.get("items")
        if isinstance(items, list):
            return [dict(item) for item in items if isinstance(item, dict)]
        return [dict(payload)]

    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        loaded = json.loads(line)
        if isinstance(loaded, dict):
            records.append(dict(loaded))
    return records


def _render_payload(payload: dict[str, Any], format: str) -> None:
    fmt = format.lower()
    if fmt == "json":
        console.print_json(data=payload)
        return
    if "items" in payload and isinstance(payload["items"], list):
        table = Table(title=payload.get("entity_type", "Entity Results"))
        items = payload["items"]
        if items:
            columns = list(items[0].keys())
            for column in columns:
                table.add_column(column)
            for item in items:
                table.add_row(*[str(item.get(column, "")) for column in columns])
            console.print(table)
            console.print(f"[dim]count={payload.get('count', len(items))}[/dim]")
            return
    console.print(payload)


@app.command("list", help="List canonical records for a supported workstream entity table.")
def entity_list(
    entity_type: str = typer.Argument(..., help="Entity table name, e.g. workstream_items"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of records"),
    offset: int = typer.Option(0, "--offset", "-o", help="Row offset"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json"),
) -> None:
    result = entity_operation("list", entity_type, limit=limit, offset=offset)
    _render_payload(result, format)


@app.command("read", help="Read a single canonical record by entity ID.")
def entity_read(
    entity_type: str = typer.Argument(..., help="Entity table name"),
    entity_id: str = typer.Argument(..., help="Primary key value, or pipe-delimited composite key"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json"),
) -> None:
    result = entity_operation("read", entity_type, entity_id=entity_id)
    _render_payload(result, format)


@app.command("search", help="Search canonical records by text query.")
def entity_search(
    entity_type: str = typer.Argument(..., help="Entity table name"),
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of records"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json"),
) -> None:
    result = entity_operation("search", entity_type, query=query, limit=limit)
    _render_payload(result, format)


@app.command("upsert", help="Create or update a canonical record.")
def entity_upsert(
    entity_type: str = typer.Argument(..., help="Entity table name"),
    entity_id: str | None = typer.Option(None, "--entity-id", "-i", help="Primary key value"),
    property_value: list[str] | None = typer.Option(
        None, "--property", "-p", help="Property override in KEY=VALUE form"
    ),
    properties_file: Path | None = typer.Option(None, "--properties-file", help="JSON file with properties"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json"),
) -> None:
    props = _parse_properties(property_value, properties_file)
    result = entity_operation("upsert", entity_type, entity_id=entity_id, properties=props)
    _render_payload(result, format)


@app.command("delete", help="Delete a canonical record.")
def entity_delete(
    entity_type: str = typer.Argument(..., help="Entity table name"),
    entity_id: str = typer.Argument(..., help="Primary key value, or pipe-delimited composite key"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json"),
) -> None:
    result = entity_operation("delete", entity_type, entity_id=entity_id)
    _render_payload(result, format)


@app.command("import", help="Import canonical records from JSON or JSONL.")
def entity_import(
    entity_type: str = typer.Argument(..., help="Entity table name"),
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json"),
) -> None:
    records = _load_records(input_path)
    result = entity_operation("import", entity_type, records=records)
    _render_payload(result, format)


@app.command("export", help="Export canonical records to JSON.")
def entity_export(
    entity_type: str = typer.Argument(..., help="Entity table name"),
    output_path: Path | None = typer.Option(None, "--output", "-o", help="Write JSON output to file"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum number of records"),
    offset: int = typer.Option(0, "--offset", help="Row offset"),
) -> None:
    result = entity_operation("export", entity_type, limit=limit, offset=offset)
    payload = json.dumps(result, option=json.OPT_INDENT_2).decode()
    if output_path:
        output_path.write_text(payload, encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output_path}")
        return
    console.print(payload)


@app.command("sync", help="Sync canonical tables from markdown, AgilePlus, or queue sources.")
def entity_sync(
    source: str = typer.Option("all", "--source", "-s", help="Source set: markdown|agileplus|queues|all"),
    cd: Path | None = typer.Option(None, "--cd", help="Project directory for markdown sync"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json"),
) -> None:
    cwd = _resolve_cwd(cd)
    result = entity_operation("sync", "sessions", source=source, cd=cwd)
    _render_payload(result, format)
