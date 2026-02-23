"""Tests for WL-219: VitePress Ops Docset for Autosync.

# @trace WL-219
"""

from __future__ import annotations

import pytest

from thegent.integrations.vitepress_ops import VitePressOpsDocset


class TestVitePressOpsDocset:
    """Tests for VitePressOpsDocset class."""

    @pytest.mark.requirement("WL-219")
    def test_generate_nav_empty_list(self):
        """# @trace WL-219 — generate_nav handles empty items list."""
        nav = VitePressOpsDocset.generate_nav([])
        assert isinstance(nav, list)
        assert len(nav) == 0

    @pytest.mark.requirement("WL-219")
    def test_generate_nav_single_item(self):
        """# @trace WL-219 — generate_nav creates single nav item correctly."""
        nav = VitePressOpsDocset.generate_nav(["Introduction"])
        assert len(nav) == 1
        assert nav[0]["text"] == "Introduction"
        assert nav[0]["link"] == "/Introduction"

    @pytest.mark.requirement("WL-219")
    def test_generate_nav_multiple_items(self):
        """# @trace WL-219 — generate_nav creates multiple nav items correctly."""
        items = ["Home", "Guide", "API", "Examples"]
        nav = VitePressOpsDocset.generate_nav(items)
        assert len(nav) == 4
        for i, item in enumerate(items):
            assert nav[i]["text"] == item
            assert nav[i]["link"] == f"/{item}"

    @pytest.mark.requirement("WL-219")
    def test_generate_nav_structure(self):
        """# @trace WL-219 — generated nav items have correct keys."""
        nav = VitePressOpsDocset.generate_nav(["Test"])
        assert "text" in nav[0]
        assert "link" in nav[0]
        assert len(nav[0]) == 2

    @pytest.mark.requirement("WL-219")
    def test_generate_nav_link_format(self):
        """# @trace WL-219 — nav links have correct format with leading slash."""
        nav = VitePressOpsDocset.generate_nav(["Documentation", "FAQ"])
        assert all(item["link"].startswith("/") for item in nav)

    @pytest.mark.requirement("WL-219")
    def test_render_index_empty_items(self):
        """# @trace WL-219 — render_index handles empty items list."""
        markdown = VitePressOpsDocset.render_index("My Docs", [])
        assert "# My Docs" in markdown
        assert markdown.count("\n") >= 1

    @pytest.mark.requirement("WL-219")
    def test_render_index_single_item(self):
        """# @trace WL-219 — render_index renders single item correctly."""
        markdown = VitePressOpsDocset.render_index("Guide", ["Getting Started"])
        assert "# Guide" in markdown
        assert "- Getting Started" in markdown

    @pytest.mark.requirement("WL-219")
    def test_render_index_multiple_items(self):
        """# @trace WL-219 — render_index renders multiple items correctly."""
        items = ["Introduction", "Installation", "Usage", "API Reference"]
        markdown = VitePressOpsDocset.render_index("Documentation", items)
        assert "# Documentation" in markdown
        for item in items:
            assert f"- {item}" in markdown

    @pytest.mark.requirement("WL-219")
    def test_render_index_markdown_format(self):
        """# @trace WL-219 — render_index outputs valid markdown format."""
        markdown = VitePressOpsDocset.render_index("Title", ["Item 1", "Item 2"])
        lines = markdown.split("\n")
        assert lines[0].startswith("#")
        assert any(line.startswith("- ") for line in lines)

    @pytest.mark.requirement("WL-219")
    def test_render_index_with_special_characters(self):
        """# @trace WL-219 — render_index handles items with special characters."""
        items = ["API/REST", "Config & Setup", "Best-Practices"]
        markdown = VitePressOpsDocset.render_index("Docs", items)
        for item in items:
            assert f"- {item}" in markdown

    @pytest.mark.requirement("WL-219")
    def test_generate_nav_with_spaces(self):
        """# @trace WL-219 — generate_nav preserves item names with spaces."""
        items = ["Getting Started", "Advanced Topics", "FAQ"]
        nav = VitePressOpsDocset.generate_nav(items)
        assert nav[0]["text"] == "Getting Started"
        assert nav[1]["text"] == "Advanced Topics"
        assert nav[2]["text"] == "FAQ"
