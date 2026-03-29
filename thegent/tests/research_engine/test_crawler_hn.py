"""Tests for Hacker News crawler. @trace FR-RE-005"""

from __future__ import annotations

from unittest.mock import MagicMock, patch


def test_hn_crawler_fetch_returns_items() -> None:
    """Fetch returns list of ResearchItem with correct source and score."""
    from research_engine.crawlers.hn import HNCrawler

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "hits": [
            {
                "objectID": "12345",
                "title": "Python MCP library",
                "url": "https://github.com/example/mcp",
                "points": 250,
                "story_text": "A library for MCP",
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response):
        crawler = HNCrawler()
        items = crawler.fetch(["python", "mcp"])

    assert len(items) == 1
    assert items[0].source == "hn"
    assert items[0].score == 250
    assert items[0].relevance > 0.0


def test_hn_crawler_fetch_empty_response() -> None:
    """Fetch handles empty response gracefully."""
    from research_engine.crawlers.hn import HNCrawler

    mock_response = MagicMock()
    mock_response.json.return_value = {"hits": []}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response):
        crawler = HNCrawler()
        items = crawler.fetch(["nonexistent"])

    assert len(items) == 0


def test_hn_crawler_fetch_multiple_items() -> None:
    """Fetch returns multiple items from response."""
    from research_engine.crawlers.hn import HNCrawler

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "hits": [
            {
                "objectID": "1",
                "title": "Python",
                "url": "https://example.com/1",
                "points": 100,
                "story_text": "Python story",
            },
            {
                "objectID": "2",
                "title": "Mcp Framework",
                "url": "https://example.com/2",
                "points": 200,
                "story_text": "MCP framework story",
            },
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response):
        crawler = HNCrawler()
        items = crawler.fetch(["python", "mcp"])

    assert len(items) == 2
    assert items[0].score == 100
    assert items[1].score == 200


def test_hn_crawler_fetch_url_fallback() -> None:
    """Fetch constructs HN URL when url field is missing."""
    from research_engine.crawlers.hn import HNCrawler

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "hits": [
            {
                "objectID": "999",
                "title": "Text-only submission",
                "points": 50,
                "story_text": "Some discussion",
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response):
        crawler = HNCrawler()
        items = crawler.fetch(["test"])

    assert items[0].url == "https://news.ycombinator.com/item?id=999"


def test_hn_crawler_tier() -> None:
    """HN crawler has hourly tier."""
    from research_engine.crawlers.hn import HNCrawler

    assert HNCrawler.tier == "hourly"


def test_hn_crawler_source() -> None:
    """HN crawler has correct source name."""
    from research_engine.crawlers.hn import HNCrawler

    assert HNCrawler.source == "hn"


def test_hn_crawler_tags() -> None:
    """Fetch populates tags based on topic matches."""
    from research_engine.crawlers.hn import HNCrawler

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "hits": [
            {
                "objectID": "1",
                "title": "Python and AI agents",
                "url": "https://example.com/1",
                "points": 100,
                "story_text": "Discussion about Python AI",
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response):
        crawler = HNCrawler()
        items = crawler.fetch(["python", "ai"])

    assert "python" in items[0].tags
    assert "ai" in items[0].tags
