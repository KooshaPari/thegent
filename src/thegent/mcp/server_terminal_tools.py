"""Terminal/workstream/LSP MCP tool registration helpers."""

from __future__ import annotations

import orjson as json
import time
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult


def register_terminal_tools(
    *,
    mcp: FastMCP,
    server_tools_terminal: Any,
    server_tools_workstream_lsp: Any,
    error_result: Any,
    work_stream_claim_impl: Any,
    work_stream_complete_impl: Any,
) -> tuple[object, object, object, object, object, object, object, object, object]:
    """Register terminal/workstream/LSP MCP tools."""

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_terminal_list(all: bool = False) -> ToolResult:
        """
        List active terminal panes (tmux).

        Args:
            all: Show all panes, not just Claude Code (default: False)
        """
        from thegent.skills.terminal import is_claude_code_pane, list_tmux_panes

        start_time = time.perf_counter()
        panes = list_tmux_panes()
        result = []
        for p in panes:
            is_cc = is_claude_code_pane(p)
            if not all and not is_cc:
                continue
            result.append(
                {
                    "pane_id": p.pane_id,
                    "session": p.session_name,
                    "window": p.window_index,
                    "pane": p.pane_index,
                    "path": p.path,
                    "command": p.command,
                    "title": p.title,
                    "is_claude_code": is_cc,
                }
            )
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return ToolResult(
            content=json.dumps(result).decode(),
            structured_content=result,
            meta={"execution_time_ms": elapsed_ms},
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_terminal_inspect(pane_id: str, last_lines: int = 50) -> ToolResult:
        """
        Capture the content of a terminal pane.
        """
        from thegent.skills.terminal import capture_tmux_pane

        start_time = time.perf_counter()
        content = capture_tmux_pane(pane_id, last_lines=last_lines)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return ToolResult(
            content=content,
            structured_content={"content": content, "pane_id": pane_id, "last_lines": last_lines},
            meta={"execution_time_ms": elapsed_ms},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_terminal_send(pane_id: str, text: str, enter: bool = True) -> ToolResult:
        """
        Send text/keys to a terminal pane.
        """
        from thegent.skills.terminal import send_to_tmux_pane

        start_time = time.perf_counter()
        success = send_to_tmux_pane(pane_id, text, enter=enter)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return ToolResult(
            content=json.dumps({"success": success}).decode(),
            structured_content={"success": success},
            meta={"execution_time_ms": elapsed_ms},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_terminal_attach(pane_id: str) -> ToolResult:
        """
        Get instructions to attach to a terminal session.
        """
        from thegent.skills.terminal import list_tmux_panes

        return server_tools_terminal.thegent_terminal_attach_impl(
            pane_id=pane_id,
            list_tmux_panes=list_tmux_panes,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_workstream_claim(item_id: str, agent_id: str) -> ToolResult:
        """
        Claim an item in the unified work stream.
        """
        return server_tools_workstream_lsp.workstream_claim_tool_impl(
            item_id=item_id,
            agent_id=agent_id,
            claim_impl=work_stream_claim_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_lsp_diagnostics(file_path: str) -> ToolResult:
        """WL-109: return normalized LSP diagnostics for a file."""
        from thegent.mcp.lsp_tools import lsp_diagnostics

        return server_tools_workstream_lsp.lsp_diagnostics_tool_impl(
            file_path=file_path,
            diagnostics_impl=lsp_diagnostics,
            error_result=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_lsp_symbol_lookup(symbol_name: str, file_path: str | None = None) -> ToolResult:
        """WL-109: lookup a symbol through the LSP adapter."""
        from thegent.mcp.lsp_tools import lsp_symbol_lookup

        return server_tools_workstream_lsp.lsp_symbol_lookup_tool_impl(
            symbol_name=symbol_name,
            file_path=file_path,
            symbol_lookup_impl=lsp_symbol_lookup,
            error_result=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_lsp_hover(file_path: str, line: int, character: int) -> ToolResult:
        """WL-109: return hover information for a source position."""
        from thegent.mcp.lsp_tools import lsp_hover

        return server_tools_workstream_lsp.lsp_hover_tool_impl(
            file_path=file_path,
            line=line,
            character=character,
            hover_impl=lsp_hover,
            error_result=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_workstream_complete(item_id: str, agent_id: str) -> ToolResult:
        """
        Mark an item as complete in the unified work stream.
        """
        return server_tools_workstream_lsp.workstream_complete_tool_impl(
            item_id=item_id,
            agent_id=agent_id,
            complete_impl=work_stream_complete_impl,
        )

    return (
        thegent_terminal_list,
        thegent_terminal_inspect,
        thegent_terminal_send,
        thegent_terminal_attach,
        thegent_workstream_claim,
        thegent_lsp_diagnostics,
        thegent_lsp_symbol_lookup,
        thegent_lsp_hover,
        thegent_workstream_complete,
    )
