"""Tests for JSON export to VitePress data loaders.

# @trace FR-DOCS-008
"""

import json
from docs_engine.export.json_export import JsonExporter
from docs_engine.db.indexer import DocIndexer


def test_export_audit_log(tmp_path):
    db = tmp_path / "test.db"
    indexer = DocIndexer(db)
    indexer.init_schema()
    indexer.upsert_doc(
        "docs/worklogs/WL-0001.md",
        {"type": "worklog", "status": "published", "title": "Fix thing", "layer": 3, "date": "2026-02-21"},
    )
    exporter = JsonExporter(db_path=db, out_dir=tmp_path / "data")
    exporter.export_audit_log()
    out = tmp_path / "data" / "audit-log.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert len(data) == 1
    assert data[0]["title"] == "Fix thing"


def test_export_kb_graph(tmp_path):
    db = tmp_path / "test.db"
    indexer = DocIndexer(db)
    indexer.init_schema()
    indexer.upsert_doc(
        "docs/kb/extract-001.md",
        {"type": "kb-extract", "status": "active", "title": "Key finding", "layer": 4, "date": "2026-02-21"},
    )
    exporter = JsonExporter(db_path=db, out_dir=tmp_path / "data")
    exporter.export_kb_graph()
    out = tmp_path / "data" / "kb-graph.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert any(n["title"] == "Key finding" for n in data["nodes"])


def test_export_sprint_board(tmp_path):
    db = tmp_path / "test.db"
    indexer = DocIndexer(db)
    indexer.init_schema()
    indexer.upsert_doc(
        "docs/sprints/SPRINT-001.md",
        {"type": "sprint-plan", "status": "active", "title": "Sprint 1", "layer": 2, "date": "2026-02-21"},
    )
    exporter = JsonExporter(db_path=db, out_dir=tmp_path / "data")
    exporter.export_sprint_board()
    out = tmp_path / "data" / "sprint-board.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert any(s["title"] == "Sprint 1" for s in data)


def test_export_all(tmp_path):
    db = tmp_path / "test.db"
    indexer = DocIndexer(db)
    indexer.init_schema()
    exporter = JsonExporter(db_path=db, out_dir=tmp_path / "data")
    exporter.export_all()
    assert (tmp_path / "data" / "audit-log.json").exists()
    assert (tmp_path / "data" / "kb-graph.json").exists()
    assert (tmp_path / "data" / "sprint-board.json").exists()
