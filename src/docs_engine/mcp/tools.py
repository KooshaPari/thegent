"""FastMCP tool registrations for docs_engine.

# @trace FR-DOCS-012
"""

from __future__ import annotations

import os
from pathlib import Path

from docs_engine.capture.writer import DocWriter
from docs_engine.db.queries import DocQueries
from docs_engine.export.json_export import JsonExporter
from docs_engine.git.cliff import CliffRunner
from docs_engine.schema.base import DocType
from docs_engine.semantic.indexer import SemanticIndexer
from docs_engine.sidebar.generator import SidebarGenerator


def _docs_root() -> Path:
    return Path(os.environ.get("DOCS_ROOT", "docs"))


def _db_path() -> Path:
    return Path(os.environ.get("DOCS_ENGINE_DB", "docs/.docs-engine.db"))


def register_tools(mcp):  # noqa: ANN001 -- mcp is a FastMCP instance; type stub varies by version
    """Register all thegent_doc_* tools on the FastMCP server instance."""

    def doc_new(doc_type: str, title: str) -> str:
        """Create a new doc of the given type with the given title."""
        writer = DocWriter(docs_root=_docs_root(), db_path=_db_path())
        path = writer.new(DocType(doc_type), title=title)
        return str(path)

    def doc_search(query: str) -> list[dict]:
        """Search docs index by title keyword."""
        return DocQueries(_db_path()).search(query)

    def doc_list(doc_type: str) -> list[dict]:
        """List all docs of the given type."""
        return DocQueries(_db_path()).get_by_type(doc_type)

    def doc_export(out_dir: str = "docs/.vitepress/data") -> str:
        """Export JSON snapshots for VitePress data loaders."""
        JsonExporter(db_path=_db_path(), out_dir=Path(out_dir)).export_all()
        return f"Exported to {out_dir}"

    def doc_sidebar(out: str = "docs/.vitepress/sidebar-auto.ts") -> str:
        """Regenerate VitePress sidebar-auto.ts."""
        gen = SidebarGenerator(docs_root=_docs_root())
        gen.write(Path(out))
        return f"Sidebar written to {out}"

    def doc_semantic() -> str:
        """Run nightly semantic knowledge extractor over conversation dumps."""
        count = SemanticIndexer(docs_root=_docs_root(), db_path=_db_path()).run()
        return f"Extracted {count} new KB items"

    def doc_changelog(output: str = "CHANGELOG.md") -> str:
        """Regenerate CHANGELOG.md via git-cliff and index it."""
        runner = CliffRunner(repo_root=Path(), db_path=_db_path())
        dest = runner.run(output=Path(output))
        return f"CHANGELOG written to {dest}"

    mcp.tool("thegent_doc_new")(doc_new)
    mcp.tool("thegent_doc_search")(doc_search)
    mcp.tool("thegent_doc_list")(doc_list)
    mcp.tool("thegent_doc_export")(doc_export)
    mcp.tool("thegent_doc_sidebar")(doc_sidebar)
    mcp.tool("thegent_doc_semantic")(doc_semantic)
    mcp.tool("thegent_doc_changelog")(doc_changelog)
    return (
        doc_new,
        doc_search,
        doc_list,
        doc_export,
        doc_sidebar,
        doc_semantic,
        doc_changelog,
    )
