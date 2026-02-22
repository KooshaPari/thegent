"""Typer CLI for the docs-engine — `docs` subcommand group.

# @trace FR-DOCS-006
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import typer
import yaml

from docs_engine.capture.writer import DocWriter
from docs_engine.db.indexer import DocIndexer
from docs_engine.db.queries import DocQueries
from docs_engine.schema.base import DocType

app = typer.Typer(name="docs", help="Agent-driven documentation system", no_args_is_help=True)


def _docs_root() -> Path:
    return Path(os.environ.get("DOCS_ROOT", Path.cwd() / "docs"))


def _db_path() -> Path:
    default = Path.home() / ".thegent" / "docs-engine" / "index.db"
    p = Path(os.environ.get("DOCS_ENGINE_DB", str(default)))
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


@app.command("new")
def new_doc(
    doc_type: str = typer.Argument(..., help="Doc type (idea, research, adr, …)"),
    title: str = typer.Argument(..., help="Document title"),
) -> None:
    """Create a new doc of the specified type using a template."""
    try:
        dtype = DocType(doc_type)
    except ValueError:
        valid = [t.value for t in DocType]
        typer.echo(f"Unknown type: {doc_type!r}. Valid types: {valid}", err=True)
        raise typer.Exit(1)
    writer = DocWriter(docs_root=_docs_root(), db_path=_db_path())
    path = writer.new(dtype, title=title)
    typer.echo(f"Created: {path}")


@app.command("search")
def search_docs(query: str = typer.Argument(..., help="Search query")) -> None:
    """Full-text search across all indexed docs."""
    results = DocQueries(_db_path()).search(query)
    if not results:
        typer.echo("No results.")
        return
    for r in results:
        typer.echo(f"[{r['type']}] {r['title']}  ({r['path']})")


@app.command("index")
def index_cmd(action: str = typer.Argument("rebuild", help="Action: rebuild")) -> None:
    """Manage the SQLite doc index."""
    if action != "rebuild":
        typer.echo(f"Unknown action: {action!r}. Valid: rebuild", err=True)
        raise typer.Exit(1)
    indexer = DocIndexer(_db_path())
    indexer.init_schema()
    count = 0
    for md_file in _docs_root().rglob("*.md"):
        try:
            text = md_file.read_text()
            if not text.startswith("---"):
                continue
            parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)
            if len(parts) < 2:
                continue
            fm = yaml.safe_load(parts[1])
            if fm and "type" in fm:
                indexer.upsert_doc(str(md_file.relative_to(_docs_root())), fm)
                count += 1
        except Exception:  # noqa: BLE001 -- scanning unknown files, skip bad ones
            pass
    typer.echo(f"Indexed {count} documents.")


@app.command("export")
def export_cmd(
    output_dir: str = typer.Option(".vitepress/data", help="Output dir for JSON data files"),
) -> None:
    """Export SQLite data as JSON for VitePress data loaders."""
    import orjson

    out = _docs_root() / output_dir
    out.mkdir(parents=True, exist_ok=True)
    q = DocQueries(_db_path())

    audit = q.get_by_type("worklog") + q.get_by_type("test-log") + q.get_by_type("completion-report")
    audit.sort(key=lambda x: x.get("date", ""), reverse=True)
    (out / "audit-log.json").write_bytes(orjson.dumps(audit))

    kb_docs: list[dict] = []
    for dtype in ("kb-extract", "research", "adr", "design-doc"):
        kb_docs.extend(q.get_by_type(dtype))
    (out / "kb-graph.json").write_bytes(orjson.dumps(kb_docs))

    sprints = q.get_by_type("sprint-plan")
    (out / "sprint-board.json").write_bytes(orjson.dumps(sprints))
    typer.echo(f"Exported data loaders to {out}")


@app.command("sidebar")
def sidebar_cmd(
    out: str = typer.Option("docs/.vitepress/sidebar-auto.ts", "--out", "-o", help="Output path"),
) -> None:
    """Regenerate VitePress sidebar-auto.ts from docs directory."""
    from docs_engine.sidebar.generator import SidebarGenerator

    gen = SidebarGenerator(_docs_root())
    dest = Path(out)
    gen.write(dest)
    typer.echo(f"Sidebar written to {dest} ({len(gen.generate())} groups)")
