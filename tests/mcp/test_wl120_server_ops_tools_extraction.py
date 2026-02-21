# @trace WL-120 B90-W2-D2
"""Focused tests for MCP ops/provider extraction in server_ops_tools.py."""

from __future__ import annotations

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


def _register_with_defaults(
    *,
    mcp: Any,
    server_tools_catalog: Any,
    list_models_impl: Any | None = None,
) -> tuple[object, ...]:
    from thegent.mcp.server_ops_tools import register_ops_tools

    server_tools_contract_observe = SimpleNamespace(
        thegent_session_contracts_impl=lambda **kwargs: {"tool": "session_contracts", **kwargs},
        thegent_session_contract_health_trend_impl=lambda **kwargs: {"tool": "session_contract_health_trend", **kwargs},
        thegent_observe_summary_impl=lambda **kwargs: {"tool": "observe_summary", **kwargs},
    )
    return register_ops_tools(
        mcp=mcp,
        server_tools_catalog=server_tools_catalog,
        server_tools_contract_observe=server_tools_contract_observe,
        stable_json=lambda payload: payload,
        error_result=lambda message, hint=None: {"error": message, "hint": hint},
        list_agents_impl=lambda: ["free"],
        list_models_impl=list_models_impl or (lambda provider=None: [{"provider": provider or "all"}]),
        observe_summary_impl=lambda **kwargs: {"summary": kwargs},
        session_contract_audit_impl=lambda **kwargs: {"audit": kwargs},
        session_contract_health_gate_impl=lambda **kwargs: {"gate": kwargs},
        session_contract_health_report_impl=lambda **kwargs: {"report": kwargs},
        session_contract_health_trend_impl=lambda **kwargs: {"trend": kwargs},
        session_contract_health_gate_helper=lambda **kwargs: {"gate_helper": kwargs},
        session_contract_health_report_helper=lambda **kwargs: {"report_helper": kwargs},
        coerce_issue_types=lambda values: values,
    )


def test_register_ops_tools_registers_expected_names() -> None:
    from thegent.mcp.server_ops_tools import register_ops_tools

    mock_mcp, registered = _mock_mcp_with_registry()
    server_tools_catalog = SimpleNamespace(
        thegent_list_operations_impl=lambda **kwargs: kwargs,
        thegent_list_modes_impl=lambda **kwargs: kwargs,
        thegent_suggest_mode_impl=lambda **kwargs: kwargs,
        thegent_list_agents_impl=lambda **kwargs: kwargs,
        thegent_list_models_impl=lambda **kwargs: kwargs,
        thegent_resolve_model_route_impl=lambda **kwargs: kwargs,
    )

    result = register_ops_tools(
        mcp=mock_mcp,
        server_tools_catalog=server_tools_catalog,
        server_tools_contract_observe=SimpleNamespace(
            thegent_session_contracts_impl=lambda **kwargs: kwargs,
            thegent_session_contract_health_trend_impl=lambda **kwargs: kwargs,
            thegent_observe_summary_impl=lambda **kwargs: kwargs,
        ),
        stable_json=lambda payload: payload,
        error_result=lambda message, hint=None: {"error": message, "hint": hint},
        list_agents_impl=lambda: [],
        list_models_impl=lambda provider=None: [],
        observe_summary_impl=lambda **kwargs: kwargs,
        session_contract_audit_impl=lambda **kwargs: kwargs,
        session_contract_health_gate_impl=lambda **kwargs: kwargs,
        session_contract_health_report_impl=lambda **kwargs: kwargs,
        session_contract_health_trend_impl=lambda **kwargs: kwargs,
        session_contract_health_gate_helper=lambda **kwargs: kwargs,
        session_contract_health_report_helper=lambda **kwargs: kwargs,
        coerce_issue_types=lambda values: values,
    )

    assert isinstance(result, tuple)
    assert len(result) == 11
    expected = {
        "thegent_list_operations",
        "thegent_list_modes",
        "thegent_suggest_mode",
        "thegent_list_agents",
        "thegent_list_models",
        "thegent_resolve_model_route",
        "thegent_session_contracts",
        "thegent_session_contract_health_gate",
        "thegent_session_contract_health_report",
        "thegent_session_contract_health_trend",
        "thegent_observe_summary",
    }
    assert expected <= set(registered)


def test_register_ops_tools_rebinding_uses_injected_catalog_instances() -> None:
    mock_mcp_a, registered_a = _mock_mcp_with_registry()
    mock_mcp_b, registered_b = _mock_mcp_with_registry()

    catalog_a = SimpleNamespace(
        thegent_list_operations_impl=lambda **kwargs: {"catalog": "A", **kwargs},
        thegent_list_modes_impl=lambda **kwargs: {"catalog": "A", **kwargs},
        thegent_suggest_mode_impl=lambda **kwargs: {"catalog": "A", **kwargs},
        thegent_list_agents_impl=lambda **kwargs: {"catalog": "A", **kwargs},
        thegent_list_models_impl=lambda **kwargs: {"catalog": "A", **kwargs},
        thegent_resolve_model_route_impl=lambda **kwargs: {"catalog": "A", **kwargs},
    )
    catalog_b = SimpleNamespace(
        thegent_list_operations_impl=lambda **kwargs: {"catalog": "B", **kwargs},
        thegent_list_modes_impl=lambda **kwargs: {"catalog": "B", **kwargs},
        thegent_suggest_mode_impl=lambda **kwargs: {"catalog": "B", **kwargs},
        thegent_list_agents_impl=lambda **kwargs: {"catalog": "B", **kwargs},
        thegent_list_models_impl=lambda **kwargs: {"catalog": "B", **kwargs},
        thegent_resolve_model_route_impl=lambda **kwargs: {"catalog": "B", **kwargs},
    )

    _register_with_defaults(mcp=mock_mcp_a, server_tools_catalog=catalog_a)
    _register_with_defaults(mcp=mock_mcp_b, server_tools_catalog=catalog_b)

    assert registered_a["thegent_list_modes"]()["catalog"] == "A"
    assert registered_b["thegent_list_modes"]()["catalog"] == "B"


def test_provider_tool_contract_list_models_passes_expected_args() -> None:
    mock_mcp, registered = _mock_mcp_with_registry()
    list_models_impl = MagicMock(return_value=[{"provider": "openai"}])
    catalog_list_models = MagicMock(return_value={"ok": True})
    server_tools_catalog = SimpleNamespace(
        thegent_list_operations_impl=lambda **kwargs: kwargs,
        thegent_list_modes_impl=lambda **kwargs: kwargs,
        thegent_suggest_mode_impl=lambda **kwargs: kwargs,
        thegent_list_agents_impl=lambda **kwargs: kwargs,
        thegent_list_models_impl=catalog_list_models,
        thegent_resolve_model_route_impl=lambda **kwargs: kwargs,
    )

    _register_with_defaults(
        mcp=mock_mcp,
        server_tools_catalog=server_tools_catalog,
        list_models_impl=list_models_impl,
    )
    result = registered["thegent_list_models"](
        provider="openai",
        include_contract=True,
        by_model=True,
    )

    assert result == {"ok": True}
    catalog_list_models.assert_called_once_with(
        provider="openai",
        include_contract=True,
        by_model=True,
        list_models_impl=list_models_impl,
    )


def test_server_source_wires_register_ops_tools_and_assignments() -> None:
    try:
        import thegent.mcp.server as server_mod
    except Exception as exc:  # pragma: no cover - environment dependent
        import pytest

        pytest.skip(f"server.py import raised: {exc}")

    source = inspect.getsource(server_mod)
    assert "_server_ops_tools.register_ops_tools(" in source
    for name in (
        "thegent_list_operations",
        "thegent_list_modes",
        "thegent_suggest_mode",
        "thegent_list_agents",
        "thegent_list_models",
        "thegent_resolve_model_route",
        "thegent_session_contracts",
        "thegent_session_contract_health_gate",
        "thegent_session_contract_health_report",
        "thegent_session_contract_health_trend",
        "thegent_observe_summary",
    ):
        assert f"{name}," in source
