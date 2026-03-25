"""Typer CLI for the docs-engine — `docs` subcommand group.

# @trace FR-DOCS-006
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import typer
from thegent.infra.fast_yaml_parser import yaml_load
from yaml import YAMLError

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
    skipped = 0
    skip_reasons: list[str] = []
    for md_file in _docs_root().rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            skipped += 1
            skip_reasons.append(f"{md_file}: read error ({type(exc).__name__}): {exc}")
            continue

        if not text.startswith("---"):
            continue

        parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)
        if len(parts) < 3:
            skipped += 1
            skip_reasons.append(f"{md_file}: malformed frontmatter (missing closing '---')")
            continue

        try:
            fm = yaml_load(parts[1])
        except (YAMLError, ValueError, TypeError) as exc:
            skipped += 1
            skip_reasons.append(f"{md_file}: frontmatter parse error ({type(exc).__name__}): {exc}")
            continue
        except Exception as exc:
            skipped += 1
            skip_reasons.append(f"{md_file}: frontmatter parse error ({type(exc).__name__}): {exc}")
            continue

        if fm and "type" in fm:
            indexer.upsert_doc(str(md_file.relative_to(_docs_root())), fm)
            count += 1

    typer.echo(f"Indexed {count} documents.")
    typer.echo(f"Skipped {skipped} files.")
    for reason in skip_reasons:
        typer.echo(f"- {reason}")


@app.command("export")
def export_cmd(
    out_dir: str = typer.Option(".vitepress/data", "--out-dir", help="Output dir for JSON data files"),
) -> None:
    """Export SQLite data as JSON for VitePress data loaders."""
    from docs_engine.export.json_export import JsonExporter

    out = _docs_root() / out_dir
    JsonExporter(db_path=_db_path(), out_dir=out).export_all()
    typer.echo(f"Exported audit-log, kb-graph, sprint-board to {out}")


@app.command("changelog")
def changelog_cmd(
    output: str = typer.Option("CHANGELOG.md", "--output", "-o", help="Output path for CHANGELOG.md"),
    repo: str = typer.Option(".", "--repo", help="Repository root"),
) -> None:
    """Regenerate CHANGELOG.md via git-cliff and index it."""
    from docs_engine.git.cliff import CliffRunner

    runner = CliffRunner(repo_root=Path(repo), db_path=_db_path())
    dest = runner.run(output=Path(output))
    typer.echo(f"CHANGELOG written to {dest}")


@app.command("semantic")
def semantic_cmd() -> None:
    """Run nightly semantic knowledge extractor over conversation dumps."""
    from docs_engine.semantic.indexer import SemanticIndexer

    indexer = SemanticIndexer(docs_root=_docs_root(), db_path=_db_path())
    count = indexer.run()
    typer.echo(f"Extracted {count} new KB items from conversation dumps.")


@app.command("hub")
def hub_cmd(
    hub_dir: str = typer.Option("../docs-hub", "--hub-dir", help="Hub output directory"),
) -> None:
    """Generate (or regenerate) the VitePress federation hub."""
    from docs_engine.hub.generator import HubGenerator

    projects = {"thegent": str(_docs_root())}
    gen = HubGenerator(hub_dir=Path(hub_dir), projects=projects)
    gen.generate()
    typer.echo(f"Hub generated at {hub_dir}")


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
