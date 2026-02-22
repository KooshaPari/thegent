"""Tests for research_engine.mcp.tools — @trace FR-RES-031"""

from unittest.mock import MagicMock, patch


def test_register_tools_returns_tuple():
    """Verify register_tools returns a tuple of callables."""
    mcp = MagicMock()
    mcp.tool = MagicMock(return_value=lambda fn: fn)
    from research_engine.mcp.tools import register_tools

    result = register_tools(mcp)
    assert isinstance(result, tuple)
    assert len(result) == 6
    for fn in result:
        assert callable(fn)


def test_all_tools_registered():
    """Verify all 6 tools are registered."""
    calls = []
    mcp = MagicMock()

    def capture_tool(name):
        calls.append(name)
        return lambda fn: fn

    mcp.tool = capture_tool
    from research_engine.mcp.tools import register_tools

    register_tools(mcp)
    assert len(calls) == 6
    assert "thegent_research_search" in calls
    assert "thegent_research_recent" in calls
    assert "thegent_research_digest" in calls
    assert "thegent_research_crawl" in calls
    assert "thegent_research_topics" in calls
    assert "thegent_research_sync" in calls


def test_tool_search_returns_string(tmp_path):
    """Verify thegent_research_search returns string."""
    mcp = MagicMock()
    mcp.tool = MagicMock(return_value=lambda fn: fn)

    with patch("research_engine.mcp.tools._GLOBAL_DB", tmp_path / "test.db"):
        from research_engine.mcp.tools import register_tools

        funcs = register_tools(mcp)
        search_fn = funcs[0]

    with patch("research_engine.store.ResearchStore") as MockStore:
        store = MagicMock()
        store.search.return_value = []
        MockStore.return_value = store
        result = search_fn("python")
        assert isinstance(result, str)


def test_tool_recent_returns_string(tmp_path):
    """Verify thegent_research_recent returns string."""
    mcp = MagicMock()
    mcp.tool = MagicMock(return_value=lambda fn: fn)

    with patch("research_engine.mcp.tools._GLOBAL_DB", tmp_path / "test.db"):
        from research_engine.mcp.tools import register_tools

        funcs = register_tools(mcp)
        recent_fn = funcs[1]

    with patch("research_engine.store.ResearchStore") as MockStore:
        store = MagicMock()
        store.get_recent.return_value = []
        MockStore.return_value = store
        result = recent_fn()
        assert isinstance(result, str)


def test_tool_digest_returns_string(tmp_path):
    """Verify thegent_research_digest returns string."""
    mcp = MagicMock()
    mcp.tool = MagicMock(return_value=lambda fn: fn)

    with patch("research_engine.mcp.tools._GLOBAL_DB", tmp_path / "test.db"):
        from research_engine.mcp.tools import register_tools

        funcs = register_tools(mcp)
        digest_fn = funcs[2]

    with patch("research_engine.store.ResearchStore") as MockStore:
        with patch("research_engine.digest.DigestGenerator") as MockDigest:
            store = MagicMock()
            MockStore.return_value = store
            digest = MagicMock()
            digest.generate.return_value = "# Digest\n"
            MockDigest.return_value = digest
            result = digest_fn()
            assert isinstance(result, str)
            assert result == "# Digest\n"


def test_tool_crawl_returns_string(tmp_path):
    """Verify thegent_research_crawl returns string."""
    mcp = MagicMock()
    mcp.tool = MagicMock(return_value=lambda fn: fn)

    with patch("research_engine.mcp.tools._GLOBAL_DB", tmp_path / "test.db"):
        from research_engine.mcp.tools import register_tools

        funcs = register_tools(mcp)
        crawl_fn = funcs[3]

    with patch("research_engine.store.ResearchStore") as MockStore:
        with patch("research_engine.topics.TopicExtractor") as MockTopics:
            with patch("research_engine.crawlers.registry.CrawlerRegistry") as MockReg:
                store = MagicMock()
                MockStore.return_value = store
                topics = MagicMock()
                topics.extract.return_value = ["python"]
                MockTopics.return_value = topics
                registry = MagicMock()
                registry.get_all.return_value = []
                MockReg.instance.return_value = registry
                result = crawl_fn()
                assert isinstance(result, str)
                assert "Crawled" in result


def test_tool_topics_returns_string(tmp_path):
    """Verify thegent_research_topics returns string."""
    mcp = MagicMock()
    mcp.tool = MagicMock(return_value=lambda fn: fn)

    with patch("research_engine.mcp.tools._GLOBAL_DB", tmp_path / "test.db"):
        from research_engine.mcp.tools import register_tools

        funcs = register_tools(mcp)
        topics_fn = funcs[4]

    with patch("research_engine.topics.TopicExtractor") as MockTopics:
        topics = MagicMock()
        topics.extract.return_value = ["python", "rust"]
        MockTopics.return_value = topics
        result = topics_fn()
        assert isinstance(result, str)
        assert "python" in result


def test_tool_sync_returns_string(tmp_path):
    """Verify thegent_research_sync returns string."""
    mcp = MagicMock()
    mcp.tool = MagicMock(return_value=lambda fn: fn)

    with patch("research_engine.mcp.tools._GLOBAL_DB", tmp_path / "test.db"):
        from research_engine.mcp.tools import register_tools

        funcs = register_tools(mcp)
        sync_fn = funcs[5]

    with patch("research_engine.store.ResearchStore") as MockStore:
        store = MagicMock()
        store.mirror_to_project.return_value = 5
        MockStore.return_value = store
        result = sync_fn(str(tmp_path / "project.db"))
        assert isinstance(result, str)
        assert "5" in result
