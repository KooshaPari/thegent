"""Tests for Vue component scaffolding.

# @trace FR-DOCS-009
"""
from pathlib import Path

THEME_DIR = Path(__file__).parents[2] / "docs" / ".vitepress" / "theme"


def test_doc_status_badge_exists():
    badge = THEME_DIR / "components" / "DocStatusBadge.vue"
    assert badge.exists()
    content = badge.read_text()
    assert "defineProps" in content
    assert "status" in content


def test_audit_timeline_exists():
    timeline = THEME_DIR / "components" / "AuditTimeline.vue"
    assert timeline.exists()
    content = timeline.read_text()
    assert "AuditEntry" in content


def test_kb_graph_exists():
    graph = THEME_DIR / "components" / "KBGraph.vue"
    assert graph.exists()
    content = graph.read_text()
    assert "KBNode" in content


def test_theme_registers_components():
    theme_index = THEME_DIR / "index.ts"
    if not theme_index.exists():
        theme_index = THEME_DIR / "index.js"
    assert theme_index.exists()
    content = theme_index.read_text()
    assert "DocStatusBadge" in content
    assert "AuditTimeline" in content
    assert "KBGraph" in content
