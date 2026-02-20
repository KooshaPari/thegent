"""Tests for the thegent tool borrowing mechanism.

Tests cover:
- ToolManifest dataclass structure and serialization
- ToolBorrower.list_available_tools() returns non-empty manifests
- ToolBorrower.list_available_tools_by_category() grouping
- ToolBorrower.get_tool() lookup by name
- ToolBorrower.export_tool_config() produces valid MCP server config
- ToolBorrower.generate_mcp_json() writes correct file structure
- ToolBorrower.generate_mcp_json() merge/overwrite behavior
- ToolBorrower.generate_claude_md_snippet() format correctness
- BorrowConfig defaults and URL generation
- Error handling for unknown tool names
- CLI helpers (smoke import of commands.tools)

# @trace FR-TOOLS-BORROW-001
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from thegent.tools.borrow import (
    _DEFAULT_MCP_HOST,
    _DEFAULT_MCP_PORT,
    BorrowConfig,
    ToolBorrower,
    ToolManifest,
)

if TYPE_CHECKING:
    from pathlib import Path


# ---------------------------------------------------------------------------
# ToolManifest tests
# ---------------------------------------------------------------------------


class TestToolManifest:
    """Tests for the ToolManifest dataclass."""

    def test_manifest_fields_set_correctly(self) -> None:
        """ToolManifest stores all fields."""
        m = ToolManifest(
            name="thegent_run",
            description="Run an agent task",
            module="thegent.mcp_server",
            function="thegent_run",
            requires=["thegent"],
            category="session",
            read_only=False,
        )
        assert m.name == "thegent_run"
        assert m.description == "Run an agent task"
        assert m.module == "thegent.mcp_server"
        assert m.function == "thegent_run"
        assert m.requires == ["thegent"]
        assert m.category == "session"
        assert m.read_only is False

    def test_manifest_to_dict_contains_all_keys(self) -> None:
        """to_dict() returns all required keys."""
        m = ToolManifest(
            name="thegent_ps",
            description="List sessions",
            module="thegent.mcp_server",
            function="thegent_ps",
            requires=["thegent"],
            category="session",
            read_only=True,
        )
        d = m.to_dict()
        assert set(d.keys()) == {"name", "description", "module", "function", "requires", "category", "read_only"}

    def test_manifest_to_dict_values_match(self) -> None:
        """to_dict() values mirror the dataclass fields."""
        m = ToolManifest(
            name="thegent_ddg_search",
            description="DuckDuckGo search",
            module="thegent.mcp_server",
            function="thegent_ddg_search",
            requires=["thegent"],
            category="research",
            read_only=True,
        )
        d = m.to_dict()
        assert d["name"] == "thegent_ddg_search"
        assert d["category"] == "research"
        assert d["read_only"] is True
        assert d["requires"] == ["thegent"]

    def test_manifest_default_read_only_true(self) -> None:
        """ToolManifest defaults read_only=True."""
        m = ToolManifest(
            name="x",
            description="",
            module="m",
            function="f",
            requires=[],
        )
        assert m.read_only is True


# ---------------------------------------------------------------------------
# BorrowConfig tests
# ---------------------------------------------------------------------------


class TestBorrowConfig:
    """Tests for BorrowConfig."""

    def test_default_host_and_port(self) -> None:
        """BorrowConfig uses thegent defaults."""
        c = BorrowConfig()
        assert c.host == _DEFAULT_MCP_HOST
        assert c.port == _DEFAULT_MCP_PORT

    def test_url_format(self) -> None:
        """BorrowConfig.url produces correct http://host:port/mcp URL."""
        c = BorrowConfig(host="10.0.0.1", port=4000)
        assert c.url == "http://10.0.0.1:4000/mcp"

    def test_default_url(self) -> None:
        """Default BorrowConfig URL uses localhost:3847."""
        c = BorrowConfig()
        assert c.url == f"http://{_DEFAULT_MCP_HOST}:{_DEFAULT_MCP_PORT}/mcp"


# ---------------------------------------------------------------------------
# ToolBorrower.list_available_tools tests
# ---------------------------------------------------------------------------


class TestListAvailableTools:
    """Tests for ToolBorrower.list_available_tools()."""

    def test_returns_non_empty_list(self) -> None:
        """list_available_tools() returns at least one manifest."""
        borrower = ToolBorrower()
        tools = borrower.list_available_tools()
        assert len(tools) > 0

    def test_returns_tool_manifest_instances(self) -> None:
        """Every item is a ToolManifest."""
        borrower = ToolBorrower()
        for tool in borrower.list_available_tools():
            assert isinstance(tool, ToolManifest)

    def test_results_sorted_by_category_then_name(self) -> None:
        """Tools are sorted: primary key=category, secondary key=name."""
        borrower = ToolBorrower()
        tools = borrower.list_available_tools()
        keys = [(t.category, t.name) for t in tools]
        assert keys == sorted(keys)

    def test_known_tools_present(self) -> None:
        """Core tools from TOOL_CATALOG are in the list."""
        borrower = ToolBorrower()
        names = {t.name for t in borrower.list_available_tools()}
        for expected in [
            "thegent_run",
            "thegent_ps",
            "thegent_ddg_search",
            "thegent_free",
            "thegent_history",
        ]:
            assert expected in names, f"{expected} missing from catalog"

    def test_list_available_tools_by_category_returns_dict(self) -> None:
        """list_available_tools_by_category() returns a dict of lists."""
        borrower = ToolBorrower()
        result = borrower.list_available_tools_by_category()
        assert isinstance(result, dict)
        for cat, tools in result.items():
            assert isinstance(cat, str)
            assert isinstance(tools, list)
            for t in tools:
                assert t.category == cat


# ---------------------------------------------------------------------------
# ToolBorrower.get_tool tests
# ---------------------------------------------------------------------------


class TestGetTool:
    """Tests for ToolBorrower.get_tool()."""

    def test_get_known_tool(self) -> None:
        """get_tool() returns the manifest for a known tool."""
        borrower = ToolBorrower()
        m = borrower.get_tool("thegent_run")
        assert m is not None
        assert m.name == "thegent_run"

    def test_get_unknown_tool_returns_none(self) -> None:
        """get_tool() returns None for unknown tools."""
        borrower = ToolBorrower()
        assert borrower.get_tool("not_a_real_tool") is None

    def test_get_tool_returns_correct_category(self) -> None:
        """get_tool() returns the manifest with the correct category."""
        borrower = ToolBorrower()
        m = borrower.get_tool("thegent_ddg_search")
        assert m is not None
        assert m.category == "research"


# ---------------------------------------------------------------------------
# ToolBorrower.export_tool_config tests
# ---------------------------------------------------------------------------


class TestExportToolConfig:
    """Tests for ToolBorrower.export_tool_config()."""

    def test_returns_dict_with_thegent_key(self) -> None:
        """export_tool_config() result has 'thegent' key."""
        borrower = ToolBorrower()
        config = borrower.export_tool_config(["thegent_run"])
        assert "thegent" in config

    def test_thegent_entry_has_type_and_url(self) -> None:
        """thegent entry contains type='http' and the server URL."""
        borrower = ToolBorrower()
        config = borrower.export_tool_config(["thegent_ps"])
        entry = config["thegent"]
        assert entry["type"] == "http"
        assert "url" in entry
        assert entry["url"].startswith("http://")

    def test_metadata_contains_borrowed_tools(self) -> None:
        """Metadata lists the requested tools."""
        borrower = ToolBorrower()
        names = ["thegent_run", "thegent_ps"]
        config = borrower.export_tool_config(names)
        assert config["thegent"]["metadata"]["borrowed_tools"] == names

    def test_empty_tool_names_includes_all(self) -> None:
        """Empty tool_names list includes all catalog tools."""
        borrower = ToolBorrower()
        config = borrower.export_tool_config([])
        meta = config["thegent"]["metadata"]
        all_names = [t.name for t in borrower.list_available_tools()]
        assert set(meta["borrowed_tools"]) == set(all_names)

    def test_unknown_tool_raises_value_error(self) -> None:
        """export_tool_config() raises ValueError for unknown tools."""
        borrower = ToolBorrower()
        with pytest.raises(ValueError, match="Unknown tool"):
            borrower.export_tool_config(["thegent_nonexistent_xyz"])

    def test_metadata_categories_are_sorted(self) -> None:
        """Metadata categories are sorted."""
        borrower = ToolBorrower()
        names = ["thegent_run", "thegent_ddg_search"]
        config = borrower.export_tool_config(names)
        cats = config["thegent"]["metadata"]["categories"]
        assert cats == sorted(cats)

    def test_config_url_reflects_custom_host_port(self) -> None:
        """Custom BorrowConfig host/port is reflected in the URL."""
        borrow_config = BorrowConfig(host="192.168.1.1", port=9999)
        borrower = ToolBorrower(config=borrow_config)
        result = borrower.export_tool_config(["thegent_ps"])
        assert result["thegent"]["url"] == "http://192.168.1.1:9999/mcp"


# ---------------------------------------------------------------------------
# ToolBorrower.generate_mcp_json tests
# ---------------------------------------------------------------------------


class TestGenerateMcpJson:
    """Tests for ToolBorrower.generate_mcp_json()."""

    def test_creates_mcp_json_file(self, tmp_path: Path) -> None:
        """generate_mcp_json() creates an mcp.json file."""
        borrower = ToolBorrower()
        written = borrower.generate_mcp_json(["thegent_run"], tmp_path)
        assert written.exists()
        assert written.name == "mcp.json"

    def test_returns_absolute_path(self, tmp_path: Path) -> None:
        """generate_mcp_json() returns the absolute path to the file."""
        borrower = ToolBorrower()
        written = borrower.generate_mcp_json(["thegent_ps"], tmp_path)
        assert written.is_absolute()

    def test_file_contains_valid_json(self, tmp_path: Path) -> None:
        """Written mcp.json is valid JSON."""
        borrower = ToolBorrower()
        written = borrower.generate_mcp_json(["thegent_run"], tmp_path)
        data = json.loads(written.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_mcpservers_key_present(self, tmp_path: Path) -> None:
        """Written file has 'mcpServers' key."""
        borrower = ToolBorrower()
        written = borrower.generate_mcp_json(["thegent_run"], tmp_path)
        data = json.loads(written.read_text(encoding="utf-8"))
        assert "mcpServers" in data

    def test_thegent_server_entry_present(self, tmp_path: Path) -> None:
        """Written file has 'thegent' server entry under mcpServers."""
        borrower = ToolBorrower()
        written = borrower.generate_mcp_json(["thegent_run"], tmp_path)
        data = json.loads(written.read_text(encoding="utf-8"))
        assert "thegent" in data["mcpServers"]

    def test_merge_preserves_existing_entries(self, tmp_path: Path) -> None:
        """Merge mode keeps pre-existing server entries."""
        from pathlib import Path as StdPath

        existing_config = {"mcpServers": {"other-server": {"type": "stdio", "command": "other"}}}
        mcp_file = StdPath(tmp_path) / "mcp.json"
        mcp_file.write_text(json.dumps(existing_config), encoding="utf-8")

        borrower = ToolBorrower()
        borrower.generate_mcp_json(["thegent_run"], tmp_path, merge=True)
        data = json.loads(mcp_file.read_text(encoding="utf-8"))
        assert "other-server" in data["mcpServers"]
        assert "thegent" in data["mcpServers"]

    def test_no_merge_overwrites_file(self, tmp_path: Path) -> None:
        """no_merge=True replaces existing mcp.json content."""
        from pathlib import Path as StdPath

        existing_config = {"mcpServers": {"only-this": {"type": "stdio", "command": "x"}}}
        mcp_file = StdPath(tmp_path) / "mcp.json"
        mcp_file.write_text(json.dumps(existing_config), encoding="utf-8")

        borrower = ToolBorrower()
        borrower.generate_mcp_json(["thegent_run"], tmp_path, merge=False)
        data = json.loads(mcp_file.read_text(encoding="utf-8"))
        assert "only-this" not in data["mcpServers"]
        assert "thegent" in data["mcpServers"]

    def test_creates_output_dir_if_missing(self, tmp_path: Path) -> None:
        """generate_mcp_json() creates the output directory if it does not exist."""
        from pathlib import Path as StdPath

        new_dir = StdPath(tmp_path) / "nested" / "project"
        borrower = ToolBorrower()
        written = borrower.generate_mcp_json(["thegent_ps"], new_dir)
        assert new_dir.exists()
        assert written.exists()


# ---------------------------------------------------------------------------
# ToolBorrower.generate_claude_md_snippet tests
# ---------------------------------------------------------------------------


class TestGenerateClaudeMdSnippet:
    """Tests for ToolBorrower.generate_claude_md_snippet()."""

    def test_returns_string(self) -> None:
        """generate_claude_md_snippet() returns a string."""
        borrower = ToolBorrower()
        result = borrower.generate_claude_md_snippet(["thegent_run"])
        assert isinstance(result, str)

    def test_contains_tool_names(self) -> None:
        """Snippet contains the requested tool names."""
        borrower = ToolBorrower()
        result = borrower.generate_claude_md_snippet(["thegent_ddg_search"])
        assert "thegent_ddg_search" in result

    def test_contains_server_url(self) -> None:
        """Snippet contains the MCP server URL."""
        borrower = ToolBorrower()
        result = borrower.generate_claude_md_snippet(["thegent_run"])
        assert borrower._config.url in result

    def test_contains_markdown_heading(self) -> None:
        """Snippet starts with a markdown H1 heading."""
        borrower = ToolBorrower()
        result = borrower.generate_claude_md_snippet(["thegent_run"])
        assert result.startswith("# thegent MCP Tools")

    def test_unknown_tool_raises_value_error(self) -> None:
        """Snippet generation raises ValueError for unknown tools."""
        borrower = ToolBorrower()
        with pytest.raises(ValueError, match="Unknown tool"):
            borrower.generate_claude_md_snippet(["thegent_does_not_exist"])

    def test_empty_list_includes_all_tools(self) -> None:
        """Empty tool list generates snippet covering all catalog tools."""
        borrower = ToolBorrower()
        result = borrower.generate_claude_md_snippet([])
        assert "thegent_run" in result
        assert "thegent_ddg_search" in result

    def test_snippet_has_usage_section(self) -> None:
        """Snippet contains a Usage section."""
        borrower = ToolBorrower()
        result = borrower.generate_claude_md_snippet(["thegent_run"])
        assert "## Usage" in result

    def test_snippet_has_available_tools_section(self) -> None:
        """Snippet contains an Available Tools section."""
        borrower = ToolBorrower()
        result = borrower.generate_claude_md_snippet(["thegent_run"])
        assert "## Available Tools" in result

    def test_read_only_annotation_in_snippet(self) -> None:
        """Read-only tools are annotated as such in the snippet."""
        borrower = ToolBorrower()
        result = borrower.generate_claude_md_snippet(["thegent_ps"])
        assert "read-only" in result.lower()

    def test_category_heading_in_snippet(self) -> None:
        """Category heading appears for research tools."""
        borrower = ToolBorrower()
        result = borrower.generate_claude_md_snippet(["thegent_ddg_search"])
        assert "Web Research" in result


# ---------------------------------------------------------------------------
# validate_server_reachable tests
# ---------------------------------------------------------------------------


class TestValidateServerReachable:
    """Tests for ToolBorrower.validate_server_reachable()."""

    def test_returns_true_on_200(self) -> None:
        """validate_server_reachable() returns True when server responds 200."""
        borrower = ToolBorrower()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("httpx.get", return_value=mock_resp):
            assert borrower.validate_server_reachable() is True

    def test_returns_false_on_non_200(self) -> None:
        """validate_server_reachable() returns False for non-200 status."""
        borrower = ToolBorrower()
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        with patch("httpx.get", return_value=mock_resp):
            assert borrower.validate_server_reachable() is False

    def test_returns_false_on_connection_error(self) -> None:
        """validate_server_reachable() returns False on network error."""
        import httpx

        borrower = ToolBorrower()
        with patch("httpx.get", side_effect=httpx.ConnectError("refused")):
            assert borrower.validate_server_reachable() is False
