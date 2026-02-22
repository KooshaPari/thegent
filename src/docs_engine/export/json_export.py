"""JSON export for VitePress data loaders.

# @trace FR-DOCS-008
"""

from __future__ import annotations

import json
from pathlib import Path

from docs_engine.db.queries import DocQueries


class JsonExporter:
    """Export SQLite index snapshots to JSON for VitePress loaders."""

    def __init__(self, db_path: Path, out_dir: Path) -> None:
        self._queries = DocQueries(db_path)
        self._out = out_dir
        self._out.mkdir(parents=True, exist_ok=True)

    def export_audit_log(self) -> Path:
        """Export worklog + completion-report docs as audit-log.json."""
        rows: list[dict] = []
        for doc_type in ("worklog", "completion-report", "test-log"):
            rows.extend(self._queries.get_by_type(doc_type))
        rows.sort(key=lambda r: r.get("date", ""), reverse=True)
        out = self._out / "audit-log.json"
        out.write_text(json.dumps(rows, indent=2))
        return out

    def export_kb_graph(self) -> Path:
        """Export kb-extract docs as graph nodes."""
        nodes = self._queries.get_by_type("kb-extract")
        out = self._out / "kb-graph.json"
        out.write_text(json.dumps({"nodes": nodes, "edges": []}, indent=2))
        return out

    def export_sprint_board(self) -> Path:
        """Export sprint-plan + sprint-retro docs."""
        sprints: list[dict] = []
        for doc_type in ("sprint-plan", "sprint-retro"):
            sprints.extend(self._queries.get_by_type(doc_type))
        sprints.sort(key=lambda r: r.get("date", ""))
        out = self._out / "sprint-board.json"
        out.write_text(json.dumps(sprints, indent=2))
        return out

    def export_all(self) -> None:
        """Export all three snapshots."""
        self.export_audit_log()
        self.export_kb_graph()
        self.export_sprint_board()
