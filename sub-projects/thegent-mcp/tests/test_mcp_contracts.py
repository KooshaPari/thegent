"""Contract tests for thegent-mcp sub-project.

# @trace FR-T4-003 — MCP server tool aggregation contracts
"""

from __future__ import annotations

import json

import pytest

from thegent_mcp.models import ToolCall, ToolResult
from thegent_mcp.server import mcp


class TestMCPModels:
    """Verify MCP models conform to interface spec."""

    def test_tool_call(self) -> None:
        call = ToolCall(
            tool_name="github/list_repos",
            args={"owner": "anthropic"},
        )
        assert call.tool_name == "github/list_repos"
        assert call.timeout_sec == 30

    def test_tool_result_success(self) -> None:
        result = ToolResult(
            tool_name="github/list_repos",
            success=True,
            output=[{"name": "sdk"}],
            duration_ms=200,
        )
        assert result.success is True
        assert result.error is None

    def test_tool_result_error(self) -> None:
        result = ToolResult(
            tool_name="github/list_repos",
            success=False,
            error="Auth failed",
            duration_ms=50,
        )
        assert result.success is False
        assert result.error == "Auth failed"


class TestMCPServer:
    """Verify MCP server has expected tools registered."""

    def test_server_name(self) -> None:
        assert mcp.name == "thegent-mcp"
