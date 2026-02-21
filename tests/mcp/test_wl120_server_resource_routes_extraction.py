# @trace WL-120 B90-W2-D2
"""Tests for extracted MCP resource route registration in server_resource_routes.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from types import SimpleNamespace
from pathlib import Path
from typing import Any

import pytest

_MODULE_PATH = Path(__file__).parents[2] / "src" / "thegent" / "mcp" / "server_resource_routes.py"
_MODULE_KEY = "thegent.mcp._server_resource_routes_test"


def _import_extracted_module() -> types.ModuleType:
    if _MODULE_KEY in sys.modules:
        return sys.modules[_MODULE_KEY]
    spec = importlib.util.spec_from_file_location(_MODULE_KEY, _MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {_MODULE_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_KEY] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _make_mcp_resource_collector(registered_names: list[str]):
    def _resource_decorator(*args: Any, **kwargs: Any):
        def _inner(fn: Any) -> Any:
            registered_names.append(fn.__name__)
            return fn

        return _inner

    return _resource_decorator


def _register_routes() -> tuple[Any, ...]:
    mod = _import_extracted_module()
    registered: list[str] = []
    mock_mcp = SimpleNamespace(resource=_make_mcp_resource_collector(registered))

    sessions = SimpleNamespace(
        resource_sessions_impl=lambda **kwargs: json.dumps({"items": [], "include_contract": kwargs["include_contract"]}),
        resource_session_meta_impl=lambda **kwargs: json.dumps({"id": kwargs["session_id"]}),
        resource_session_logs_impl=lambda **kwargs: "ok",
    )
    catalog = SimpleNamespace(
        resource_dag_impl=lambda **kwargs: json.dumps({"tasks": []}),
        resource_agents_impl=lambda **kwargs: json.dumps([]),
        resource_models_impl=lambda **kwargs: json.dumps({"provider": kwargs["provider"], "include_contract": kwargs["include_contract"]}),
        resource_models_contract_impl=lambda: json.dumps({"contract": "ok"}),
    )
    workstream = SimpleNamespace(
        resource_workstream_impl=lambda: "# workstream",
        resource_events_session_complete_impl=lambda: json.dumps({"events": []}),
        resource_workstream_db_impl=lambda: json.dumps({"db": "ok"}),
    )
    contracts = SimpleNamespace(
        resource_session_contracts_impl=lambda **kwargs: json.dumps({"summary": {}}),
        resource_session_contract_health_gate_impl=lambda **kwargs: json.dumps({"gate": "ok"}),
        resource_session_contract_health_report_impl=lambda **kwargs: json.dumps({"report": "ok"}),
        resource_session_contract_health_trend_impl=lambda **kwargs: json.dumps({"trend": []}),
    )

    def _stable_json(payload: Any) -> str:
        return json.dumps(payload, sort_keys=True)

    def _gate_helper(**kwargs: Any) -> str:
        return kwargs["stable_json"](
            {
                "schema_version": "v1",
                "payload_type": "session_contract_health_gate",
                "payload": {"healthy": True},
            }
        )

    return mod.register_resource_routes(
        mcp=mock_mcp,  # type: ignore[arg-type]
        server_resource_sessions=sessions,
        server_resource_catalog=catalog,
        server_resource_workstream=workstream,
        server_resource_contracts=contracts,
        resource_session_contract_health_gate_helper=_gate_helper,
        resource_session_contract_health_report_helper=lambda **kwargs: kwargs["stable_json"]({"payload_type": "report"}),
        resource_session_contract_health_trend_helper=lambda **kwargs: kwargs["stable_json"]({"payload_type": "trend"}),
        ps_impl=lambda **kwargs: [],
        status_impl=lambda **kwargs: {},
        logs_impl=lambda **kwargs: "",
        dag_list_impl=lambda **kwargs: {},
        list_agents_impl=lambda **kwargs: [],
        list_models_impl=lambda **kwargs: [],
        session_contract_audit_impl=lambda **kwargs: {},
        session_contract_health_gate_impl=lambda **kwargs: {},
        session_contract_health_report_impl=lambda **kwargs: {},
        session_contract_health_trend_impl=lambda **kwargs: {},
        stable_json=_stable_json,
    )


def test_resource_routes_registers_expected_handler_set() -> None:
    mod = _import_extracted_module()
    registered: list[str] = []
    mock_mcp = SimpleNamespace(resource=_make_mcp_resource_collector(registered))

    mod.register_resource_routes(
        mcp=mock_mcp,  # type: ignore[arg-type]
        server_resource_sessions=SimpleNamespace(
            resource_sessions_impl=lambda **kwargs: "[]",
            resource_session_meta_impl=lambda **kwargs: "{}",
            resource_session_logs_impl=lambda **kwargs: "",
        ),
        server_resource_catalog=SimpleNamespace(
            resource_dag_impl=lambda **kwargs: "{}",
            resource_agents_impl=lambda **kwargs: "[]",
            resource_models_impl=lambda **kwargs: "[]",
            resource_models_contract_impl=lambda: "{}",
        ),
        server_resource_workstream=SimpleNamespace(
            resource_workstream_impl=lambda: "",
            resource_events_session_complete_impl=lambda: "{}",
            resource_workstream_db_impl=lambda: "{}",
        ),
        server_resource_contracts=SimpleNamespace(
            resource_session_contracts_impl=lambda **kwargs: "{}",
            resource_session_contract_health_gate_impl=lambda **kwargs: "{}",
            resource_session_contract_health_report_impl=lambda **kwargs: "{}",
            resource_session_contract_health_trend_impl=lambda **kwargs: "{}",
        ),
        resource_session_contract_health_gate_helper=lambda **kwargs: "{}",
        resource_session_contract_health_report_helper=lambda **kwargs: "{}",
        resource_session_contract_health_trend_helper=lambda **kwargs: "{}",
        ps_impl=lambda **kwargs: [],
        status_impl=lambda **kwargs: {},
        logs_impl=lambda **kwargs: "",
        dag_list_impl=lambda **kwargs: {},
        list_agents_impl=lambda **kwargs: [],
        list_models_impl=lambda **kwargs: [],
        session_contract_audit_impl=lambda **kwargs: {},
        session_contract_health_gate_impl=lambda **kwargs: {},
        session_contract_health_report_impl=lambda **kwargs: {},
        session_contract_health_trend_impl=lambda **kwargs: {},
        stable_json=lambda payload: json.dumps(payload),
    )

    assert len(registered) == 14
    expected = {
        "resource_sessions",
        "resource_session_meta",
        "resource_session_logs",
        "resource_dag",
        "resource_agents",
        "resource_models",
        "resource_models_contract",
        "resource_workstream",
        "resource_events_session_complete",
        "resource_workstream_db",
        "resource_session_contracts",
        "resource_session_contract_health_gate",
        "resource_session_contract_health_report",
        "resource_session_contract_health_trend",
    }
    assert expected == set(registered)


def test_representative_resource_contract_payload_shape() -> None:
    routes = _register_routes()
    resource_session_contract_health_gate = routes[11]

    payload = json.loads(resource_session_contract_health_gate())
    assert payload["schema_version"] == "v1"
    assert payload["payload_type"] == "session_contract_health_gate"
    assert payload["payload"]["healthy"] is True


def test_server_module_reexports_resource_handlers() -> None:
    try:
        import thegent.mcp.server as server_mod
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"server.py import raised: {exc}")

    for name in (
        "resource_sessions",
        "resource_session_meta",
        "resource_session_logs",
        "resource_dag",
        "resource_agents",
        "resource_models",
        "resource_models_contract",
        "resource_workstream",
        "resource_events_session_complete",
        "resource_workstream_db",
        "resource_session_contracts",
        "resource_session_contract_health_gate",
        "resource_session_contract_health_report",
        "resource_session_contract_health_trend",
    ):
        assert hasattr(server_mod, name), f"server.py missing expected resource symbol: {name}"
