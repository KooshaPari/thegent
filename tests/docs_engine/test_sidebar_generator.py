"""Tests for sidebar generator.

# @trace FR-DOCS-007
"""
from docs_engine.sidebar.generator import SidebarGenerator


def test_generate_empty_docs(tmp_path):
    gen = SidebarGenerator(docs_root=tmp_path / "docs")
    result = gen.generate()
    assert result == {}


def test_generate_groups_by_type(tmp_path):
    docs = tmp_path / "docs"
    (docs / "ideas").mkdir(parents=True)
    (docs / "ideas" / "2026-02-21-test.md").write_text(
        "---\ntype: idea\nstatus: draft\ntitle: Test idea\nlayer: 1\ndate: 2026-02-21\n---\n"
    )
    gen = SidebarGenerator(docs_root=docs)
    result = gen.generate()
    assert "idea" in result
    assert len(result["idea"]) == 1
    assert result["idea"][0]["text"] == "Test idea"


def test_generate_uses_filename_fallback(tmp_path):
    docs = tmp_path / "docs"
    (docs / "misc").mkdir(parents=True)
    (docs / "misc" / "no-frontmatter.md").write_text("# Just a title\n")
    gen = SidebarGenerator(docs_root=docs)
    result = gen.generate()
    # Grouped under directory name 'misc' when no type in frontmatter
    assert "misc" in result


def test_emit_typescript(tmp_path):
    docs = tmp_path / "docs"
    (docs / "ideas").mkdir(parents=True)
    (docs / "ideas" / "2026-02-21-test.md").write_text(
        "---\ntype: idea\nstatus: draft\ntitle: My Idea\nlayer: 1\ndate: 2026-02-21\n---\n"
    )
    gen = SidebarGenerator(docs_root=docs)
    ts = gen.emit_typescript()
    assert "export const sidebar" in ts
    assert "My Idea" in ts


def test_write_sidebar_file(tmp_path):
    docs = tmp_path / "docs"
    (docs / "ideas").mkdir(parents=True)
    (docs / "ideas" / "2026-02-21-test.md").write_text(
        "---\ntype: idea\nstatus: draft\ntitle: Written\nlayer: 1\ndate: 2026-02-21\n---\n"
    )
    out = tmp_path / "sidebar-auto.ts"
    gen = SidebarGenerator(docs_root=docs)
    gen.write(out)
    assert out.exists()
    assert "Written" in out.read_text()
