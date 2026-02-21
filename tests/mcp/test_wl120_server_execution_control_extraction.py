# @trace WL-120 B90-W2-D4
"""Focused tests for MCP execution/control extraction loaders."""

from __future__ import annotations

import asyncio
import inspect
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock


def _mock_mcp_with_registry() -> tuple[MagicMock, dict[str, Any]]:
    registered: dict[str, Any] = {}

    def _tool_decorator(*args: Any, **kwargs: Any):
        def _inner(fn: Any) -> Any:
            registered[fn.__name__] = fn
            return fn

        return _inner

    mock_mcp = MagicMock()
    mock_mcp.tool = _tool_decorator
    return mock_mcp, registered


def test_register_execution_tools_registers_expected_names() -> None:
    from thegent.mcp.server_execution_tools import register_execution_tools

    mock_mcp, registered = _mock_mcp_with_registry()
    runtime = SimpleNamespace(
        config_resolve_impl=lambda **kwargs: kwargs,
        negotiate_contract_impl=lambda **kwargs: kwargs,
    )
    result = register_execution_tools(
        mcp=mock_mcp,
        server_tools_runtime=runtime,
        error_result=lambda message, hint=None, extra=None: {"error": message, "hint": hint, "extra": extra},
        get_default_cwd=lambda: None,
        get_default_owner=lambda: None,
        resolve_cwd=lambda value: value,
        run_impl=lambda *args, **kwargs: {"exit_code": 0, "args": args, "kwargs": kwargs},
        bg_impl=lambda **kwargs: {"session_id": "s1", **kwargs},
        session_contract_negotiate_impl=lambda **kwargs: kwargs,
        write_session_control_file=lambda **kwargs: None,
        normalize_bg_routing=lambda **kwargs: ("prefer_direct", "prefer_direct", "prefer_direct", False),
        build_route_request_payload=lambda **kwargs: kwargs,
        settings_factory=lambda: SimpleNamespace(default_routing="prefer_direct", default_timeout_free=90, session_dir="."),
        default_owner_tag=lambda _cwd: "owner",
        resolve_cwd_elicitation=lambda _response: (None, "declined"),
        resolve_owner_elicitation=lambda _response, default_owner_tag: (default_owner_tag, None),
        get_cached_elicitation=lambda _prompt, _response_type: "cached",
        cache_elicitation_response=lambda _prompt, _response_type, _response: None,
        accepted_elicitation_type=object,
        output_parser_schema_version="v1",
        elicit_timeout_s=30,
        elicit_cwd_msg="cwd?",
        elicit_owner_msg="owner?",
    )

    assert isinstance(result, tuple)
    assert len(result) == 9
    expected = {
        "thegent_config_resolve",
        "thegent_negotiate_contract",
        "thegent_run",
        "thegent_loop",
        "thegent_loop_takeover",
        "thegent_loop_stop",
        "thegent_bg",
        "thegent_free",
        "thegent_flash",
    }
    assert expected <= set(registered)


def test_execution_contract_negotiate_passes_session_contract_impl() -> None:
    from thegent.mcp.server_execution_tools import register_execution_tools

    mock_mcp, registered = _mock_mcp_with_registry()
    negotiate_impl = MagicMock(return_value='{"status":"ok"}')
    session_negotiate_impl = MagicMock(return_value={"ok": True})
    register_execution_tools(
        mcp=mock_mcp,
        server_tools_runtime=SimpleNamespace(
            config_resolve_impl=lambda **kwargs: kwargs,
            negotiate_contract_impl=negotiate_impl,
        ),
        error_result=lambda message, hint=None, extra=None: {"error": message, "hint": hint, "extra": extra},
        get_default_cwd=lambda: None,
        get_default_owner=lambda: None,
        resolve_cwd=lambda value: value,
        run_impl=lambda *args, **kwargs: {"exit_code": 0, "args": args, "kwargs": kwargs},
        bg_impl=lambda **kwargs: {"session_id": "s1", **kwargs},
        session_contract_negotiate_impl=session_negotiate_impl,
        write_session_control_file=lambda **kwargs: None,
        normalize_bg_routing=lambda **kwargs: ("prefer_direct", "prefer_direct", "prefer_direct", False),
        build_route_request_payload=lambda **kwargs: kwargs,
        settings_factory=lambda: SimpleNamespace(default_routing="prefer_direct", default_timeout_free=90, session_dir="."),
        default_owner_tag=lambda _cwd: "owner",
        resolve_cwd_elicitation=lambda _response: (None, "declined"),
        resolve_owner_elicitation=lambda _response, default_owner_tag: (default_owner_tag, None),
        get_cached_elicitation=lambda _prompt, _response_type: "cached",
        cache_elicitation_response=lambda _prompt, _response_type, _response: None,
        accepted_elicitation_type=object,
        output_parser_schema_version="v1",
        elicit_timeout_s=30,
        elicit_cwd_msg="cwd?",
        elicit_owner_msg="owner?",
    )

    result = asyncio.run(
        registered["thegent_negotiate_contract"](
            contract_id="csm",
            supported_versions=["1.0.0"],
        )
    )
    assert result == '{"status":"ok"}'
    negotiate_impl.assert_called_once_with(
        contract_id="csm",
        supported_versions=["1.0.0"],
        session_contract_negotiate_impl=session_negotiate_impl,
    )


def test_register_control_tools_registers_expected_names() -> None:
    from thegent.mcp.server_control_tools import register_control_tools

    mock_mcp, registered = _mock_mcp_with_registry()
    result = register_control_tools(
        mcp=mock_mcp,
        server_tools_runtime=SimpleNamespace(
            ps_tool_impl=lambda **kwargs: kwargs,
            status_tool_impl=lambda **kwargs: kwargs,
            logs_tool_impl=lambda **kwargs: kwargs,
        ),
        server_tools_contract_observe=SimpleNamespace(thegent_inspect_impl=lambda **kwargs: kwargs),
        server_tools_coordination=SimpleNamespace(
            thegent_wait_impl=lambda **kwargs: kwargs,
            thegent_inbox_list_impl=lambda **kwargs: kwargs,
            thegent_inbox_wait_impl=lambda **kwargs: kwargs,
            thegent_stop_impl=lambda **kwargs: kwargs,
            thegent_pause_impl=lambda **kwargs: kwargs,
            thegent_resume_impl=lambda **kwargs: kwargs,
            thegent_continuity_snapshot_impl=lambda **kwargs: kwargs,
        ),
        ps_impl=lambda **kwargs: kwargs,
        status_impl=lambda **kwargs: kwargs,
        logs_impl=lambda **kwargs: kwargs,
        inspect_impl=lambda **kwargs: kwargs,
        wait_impl=lambda **kwargs: kwargs,
        inbox_list_impl=lambda **kwargs: kwargs,
        stop_impl=lambda **kwargs: kwargs,
        continuity_snapshot_impl=lambda **kwargs: kwargs,
        settings_factory=lambda: SimpleNamespace(),
        logger=MagicMock(),
    )

    assert isinstance(result, tuple)
    assert len(result) == 11
    expected = {
        "thegent_ps",
        "thegent_status",
        "thegent_logs",
        "thegent_inspect",
        "thegent_wait",
        "thegent_inbox_list",
        "thegent_inbox_wait",
        "thegent_stop",
        "thegent_pause",
        "thegent_resume",
        "thegent_continuity_snapshot",
    }
    assert expected <= set(registered)


def test_control_contract_status_passes_expected_args() -> None:
    from thegent.mcp.server_control_tools import register_control_tools

    mock_mcp, registered = _mock_mcp_with_registry()
    status_tool_impl = MagicMock(return_value={"status": "running"})
    logger = MagicMock()
    status_impl = MagicMock()
    register_control_tools(
        mcp=mock_mcp,
        server_tools_runtime=SimpleNamespace(
            ps_tool_impl=lambda **kwargs: kwargs,
            status_tool_impl=status_tool_impl,
            logs_tool_impl=lambda **kwargs: kwargs,
        ),
        server_tools_contract_observe=SimpleNamespace(thegent_inspect_impl=lambda **kwargs: kwargs),
        server_tools_coordination=SimpleNamespace(
            thegent_wait_impl=lambda **kwargs: kwargs,
            thegent_inbox_list_impl=lambda **kwargs: kwargs,
            thegent_inbox_wait_impl=lambda **kwargs: kwargs,
            thegent_stop_impl=lambda **kwargs: kwargs,
            thegent_pause_impl=lambda **kwargs: kwargs,
            thegent_resume_impl=lambda **kwargs: kwargs,
            thegent_continuity_snapshot_impl=lambda **kwargs: kwargs,
        ),
        ps_impl=lambda **kwargs: kwargs,
        status_impl=status_impl,
        logs_impl=lambda **kwargs: kwargs,
        inspect_impl=lambda **kwargs: kwargs,
        wait_impl=lambda **kwargs: kwargs,
        inbox_list_impl=lambda **kwargs: kwargs,
        stop_impl=lambda **kwargs: kwargs,
        continuity_snapshot_impl=lambda **kwargs: kwargs,
        settings_factory=lambda: SimpleNamespace(),
        logger=logger,
    )

    result = registered["thegent_status"](session_id="s-1", include_contract=True)
    assert result == {"status": "running"}
    status_tool_impl.assert_called_once_with(
        session_id="s-1",
        include_contract=True,
        status_impl=status_impl,
        log=logger,
    )


def test_server_source_wires_execution_and_control_loader_rebinds() -> None:
    try:
        import thegent.mcp.server as server_mod
    except Exception as exc:  # pragma: no cover - environment dependent
        import pytest

        pytest.skip(f"server.py import raised: {exc}")

    source = inspect.getsource(server_mod)
    assert "_server_execution_tools.register_execution_tools(" in source
    assert "_server_control_tools.register_control_tools(" in source
    for name in (
        "thegent_run",
        "thegent_bg",
        "thegent_loop",
        "thegent_free",
        "thegent_flash",
        "thegent_status",
        "thegent_logs",
        "thegent_inspect",
        "thegent_wait",
        "thegent_stop",
        "thegent_pause",
        "thegent_resume",
        "thegent_continuity_snapshot",
    ):
        assert f"{name}," in source

