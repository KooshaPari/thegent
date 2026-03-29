"""Tests for FastMCP tool registrations.

# @trace FR-DOCS-012
"""

from unittest.mock import MagicMock

from docs_engine.mcp.tools import register_tools


def test_register_tools_registers_seven_tools():
    mcp = MagicMock()
    # Capture tool names via the decorator calls
    registered: list[str] = []

    def fake_tool(name):
        registered.append(name)
        return lambda f: f

    mcp.tool = fake_tool
    register_tools(mcp)
    assert len(registered) == 7
    assert "thegent_doc_new" in registered
    assert "thegent_doc_search" in registered
    assert "thegent_doc_list" in registered
    assert "thegent_doc_export" in registered
    assert "thegent_doc_sidebar" in registered
    assert "thegent_doc_semantic" in registered
    assert "thegent_doc_changelog" in registered


def test_doc_new_calls_writer(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCS_ROOT", str(tmp_path / "docs"))
    monkeypatch.setenv("DOCS_ENGINE_DB", str(tmp_path / "test.db"))

    registered_fns: dict = {}

    def fake_tool(name):
        def decorator(f):
            registered_fns[name] = f
            return f

        return decorator

    mcp = MagicMock()
    mcp.tool = fake_tool
    register_tools(mcp)
    result = registered_fns["thegent_doc_new"](doc_type="idea", title="MCP test idea")
    assert "idea" in result or "MCP test idea" in result or result.endswith(".md")


def test_doc_search_calls_queries(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DOCS_ENGINE_DB", str(db_path))

    # Initialise schema so search can query the docs table
    from docs_engine.db.indexer import DocIndexer

    DocIndexer(db_path).init_schema()

    registered_fns: dict = {}

    def fake_tool(name):
        def decorator(f):
            registered_fns[name] = f
            return f

        return decorator

    mcp = MagicMock()
    mcp.tool = fake_tool
    register_tools(mcp)
    # Empty DB returns empty list
    results = registered_fns["thegent_doc_search"](query="anything")
    assert results == []
