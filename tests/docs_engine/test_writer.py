"""Tests for DocWriter.

# @trace FR-DOCS-003
"""
import pytest
from docs_engine.capture.writer import DocWriter
from docs_engine.schema.base import DocType
from docs_engine.db.queries import DocQueries


def test_write_idea_creates_file(tmp_path):
    writer = DocWriter(docs_root=tmp_path / "docs", db_path=tmp_path / "test.db")
    path = writer.new(DocType.IDEA, title="Test idea")
    assert path.exists()
    content = path.read_text()
    assert "type: idea" in content
    assert "Test idea" in content


def test_write_indexes_to_db(tmp_path):
    writer = DocWriter(docs_root=tmp_path / "docs", db_path=tmp_path / "test.db")
    writer.new(DocType.IDEA, title="Indexed idea")
    results = DocQueries(tmp_path / "test.db").get_by_type("idea")
    assert len(results) == 1
    assert results[0]["title"] == "Indexed idea"


def test_write_rejects_empty_title(tmp_path):
    writer = DocWriter(docs_root=tmp_path / "docs", db_path=tmp_path / "test.db")
    with pytest.raises(ValueError, match="title"):
        writer.new(DocType.IDEA, title="")


def test_write_adr_gets_sequential_id(tmp_path):
    writer = DocWriter(docs_root=tmp_path / "docs", db_path=tmp_path / "test.db")
    p1 = writer.new(DocType.ADR, title="First decision")
    p2 = writer.new(DocType.ADR, title="Second decision")
    assert "ADR-001" in p1.name
    assert "ADR-002" in p2.name


def test_write_sets_correct_layer(tmp_path):
    writer = DocWriter(docs_root=tmp_path / "docs", db_path=tmp_path / "test.db")
    writer.new(DocType.IDEA, title="Informal doc")
    results = DocQueries(tmp_path / "test.db").get_by_type("idea")
    assert results[0]["layer"] == 1  # Layer 1 = informal


def test_adr_template_rendered(tmp_path):
    writer = DocWriter(docs_root=tmp_path / "docs", db_path=tmp_path / "test.db")
    path = writer.new(DocType.ADR, title="Use SQLite for doc index")
    content = path.read_text()
    assert "## Context" in content
    assert "## Decision" in content
    assert "## Rationale" in content
