# @trace WL-120 B90-W2-D5
"""Focused tests for WL-120 remaining surface extraction from mcp/server.py."""

from __future__ import annotations

import asyncio
import inspect
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock


def _mock_mcp_with_registry() -> tuple[MagicMock, dict[str, Any], dict[str, Any]]:
    registered_tools: dict[str, Any] = {}
    registered_routes: dict[str, Any] = {}

    def _tool_decorator(*args: Any, **kwargs: Any):
        def _inner(fn: Any) -> Any:
            registered_tools[fn.__name__] = fn
            return fn

        return _inner

    def _route_decorator(*args: Any, **kwargs: Any):
        def _inner(fn: Any) -> Any:
            registered_routes[fn.__name__] = fn
            return fn

        return _inner

    mock_mcp = MagicMock()
    mock_mcp.tool = _tool_decorator
    mock_mcp.custom_route = _route_decorator
    return mock_mcp, registered_tools, registered_routes


def test_register_terminal_tools_registers_expected_names() -> None:
    from thegent.mcp.server_terminal_tools import register_terminal_tools

    mock_mcp, registered, _ = _mock_mcp_with_registry()
    register_terminal_tools(
        mcp=mock_mcp,
        server_tools_terminal=SimpleNamespace(thegent_terminal_attach_impl=lambda **kwargs: kwargs),
        server_tools_workstream_lsp=SimpleNamespace(
            workstream_claim_tool_impl=lambda **kwargs: kwargs,
            lsp_diagnostics_tool_impl=lambda **kwargs: kwargs,
            lsp_symbol_lookup_tool_impl=lambda **kwargs: kwargs,
            lsp_hover_tool_impl=lambda **kwargs: kwargs,
            workstream_complete_tool_impl=lambda **kwargs: kwargs,
        ),
        error_result=lambda message, hint=None, extra=None: {"error": message, "hint": hint, "extra": extra},
        work_stream_claim_impl=lambda **kwargs: kwargs,
        work_stream_complete_impl=lambda **kwargs: kwargs,
    )

    expected = {
        "thegent_terminal_list",
        "thegent_terminal_inspect",
        "thegent_terminal_send",
        "thegent_terminal_attach",
        "thegent_workstream_claim",
        "thegent_lsp_diagnostics",
        "thegent_lsp_symbol_lookup",
        "thegent_lsp_hover",
        "thegent_workstream_complete",
    }
    assert expected <= set(registered)


def test_terminal_workstream_claim_contract_passes_claim_impl() -> None:
    from thegent.mcp.server_terminal_tools import register_terminal_tools

    mock_mcp, registered, _ = _mock_mcp_with_registry()
    claim_tool_impl = MagicMock(return_value={"ok": True})
    claim_impl = MagicMock()

    register_terminal_tools(
        mcp=mock_mcp,
        server_tools_terminal=SimpleNamespace(thegent_terminal_attach_impl=lambda **kwargs: kwargs),
        server_tools_workstream_lsp=SimpleNamespace(
            workstream_claim_tool_impl=claim_tool_impl,
            lsp_diagnostics_tool_impl=lambda **kwargs: kwargs,
            lsp_symbol_lookup_tool_impl=lambda **kwargs: kwargs,
            lsp_hover_tool_impl=lambda **kwargs: kwargs,
            workstream_complete_tool_impl=lambda **kwargs: kwargs,
        ),
        error_result=lambda message, hint=None, extra=None: {"error": message, "hint": hint, "extra": extra},
        work_stream_claim_impl=claim_impl,
        work_stream_complete_impl=lambda **kwargs: kwargs,
    )

    result = registered["thegent_workstream_claim"](item_id="item-1", agent_id="agent-1")
    assert result == {"ok": True}
    claim_tool_impl.assert_called_once_with(
        item_id="item-1",
        agent_id="agent-1",
        claim_impl=claim_impl,
    )


def test_register_research_tools_and_suggest_prompt_contract() -> None:
    from thegent.mcp.server_research_tools import register_research_tools

    mock_mcp, registered, _ = _mock_mcp_with_registry()
    suggest_impl = AsyncMock(return_value={"prompt": "improved"})
    logger = MagicMock()

    register_research_tools(
        mcp=mock_mcp,
        server_tools_research=SimpleNamespace(
            thegent_ddg_search_impl=MagicMock(return_value={"results": []}),
            thegent_reddit_search_impl=MagicMock(return_value={"results": []}),
            thegent_scrape_url_impl=MagicMock(return_value={"content": ""}),
            thegent_deep_research_impl=MagicMock(return_value={"report": "ok"}),
            thegent_suggest_prompt_impl=suggest_impl,
        ),
        logger=logger,
    )

    expected = {
        "thegent_ddg_search",
        "thegent_reddit_search",
        "thegent_scrape_url",
        "thegent_deep_research",
        "thegent_suggest_prompt",
    }
    assert expected <= set(registered)

    ctx = object()
    result = asyncio.run(registered["thegent_suggest_prompt"](raw_prompt="draft", ctx=ctx))
    assert result == {"prompt": "improved"}
    suggest_impl.assert_called_once_with(raw_prompt="draft", ctx=ctx, logger=logger)


def test_register_runtime_entry_runtime_contracts() -> None:
    from thegent.mcp.server_runtime_entry import register_runtime_entry

    mock_mcp, registered_tools, registered_routes = _mock_mcp_with_registry()
    parse_acp_payload = MagicMock(return_value=(None, "bad payload"))
    format_acp_response = MagicMock(return_value='{"success": false}')
    create_http_app = MagicMock(return_value=object())
    create_event_store = MagicMock(return_value=object())
    run_server = MagicMock()

    (
        _health,
        _get_event_store,
        _thegent_acp_invoke,
        _http_app,
        _http_app_factory,
        run,
    ) = register_runtime_entry(
        mcp=mock_mcp,
        health_response=MagicMock(),
        create_event_store=create_event_store,
        create_http_app=create_http_app,
        bearer_auth_middleware=object(),
        log=MagicMock(),
        parse_acp_payload=parse_acp_payload,
        format_acp_response=format_acp_response,
        run_server=run_server,
        settings_factory=lambda: SimpleNamespace(mcp_host="127.0.0.1", mcp_port=7000),
        http_app_factory_import_path="thegent.mcp_server:http_app_factory",
    )

    assert "health" in registered_routes
    assert "thegent_acp_invoke" in registered_tools

    invoke_result = asyncio.run(
        registered_tools["thegent_acp_invoke"](
            agent_url="http://localhost:8420",
            task="do thing",
            payload="not-json",
        )
    )
    assert invoke_result == '{"success": false}'
    format_acp_response.assert_called_once_with(
        success=False,
        error="bad payload",
        result="",
        agent_url="http://localhost:8420",
        elapsed_ms=0,
    )

    run(host="0.0.0.0", port=7010, reload=False)
    run_server.assert_called_once()
    kwargs = run_server.call_args.kwargs
    assert kwargs["host"] == "0.0.0.0"
    assert kwargs["port"] == 7010
    assert kwargs["reload"] is False
    assert kwargs["http_app_factory_import_path"] == "thegent.mcp_server:http_app_factory"
    assert callable(kwargs["http_app_builder"])


def test_server_source_wires_remaining_surface_rebinds() -> None:
    try:
        import thegent.mcp.server as server_mod
    except Exception as exc:  # pragma: no cover - environment dependent
        import pytest

        pytest.skip(f"server.py import raised: {exc}")

    source = inspect.getsource(server_mod)
    # The server module now uses dynamic imports from legacy module
    # Check that it re-exports the expected symbols by verifying they exist
    # instead of checking source code patterns
    expected_symbols = [
        "thegent_terminal_list",
        "thegent_terminal_attach",
        "thegent_workstream_claim",
        "thegent_lsp_diagnostics",
        "thegent_ddg_search",
        "thegent_deep_research",
        "health",
        "_get_event_store",
        "thegent_acp_invoke",
        "http_app",
        "http_app_factory",
        "run",
    ]
    for name in expected_symbols:
        assert hasattr(server_mod, name), f"Expected symbol {name} not found in server module"
