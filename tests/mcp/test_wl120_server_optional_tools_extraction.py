# @trace WL-120 B90-W2-D7
"""Focused tests for WL-120 optional-tools extraction from mcp/server.py."""

from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

from thegent.mcp import server_optional_tools


def _mock_mcp_with_registry() -> tuple[MagicMock, dict[str, Any]]:
    registered_tools: dict[str, Any] = {}

    def _tool_decorator(*args: Any, **kwargs: Any):
        def _inner(fn: Any) -> Any:
            registered_tools[fn.__name__] = fn
            return fn

        return _inner

    mock_mcp = MagicMock()
    mock_mcp.tool = _tool_decorator
    return mock_mcp, registered_tools


def test_register_storage_event_tools_wires_representative_helpers() -> None:
    mock_mcp, _ = _mock_mcp_with_registry()
    storage = MagicMock()
    storage.get.return_value = {"hello": "world"}
    event_store = MagicMock()
    event_store.emit.return_value = "evt-1"
    event_store.replay.return_value = [{"event_id": "evt-1"}]

    exported = server_optional_tools.register_storage_event_tools(
        mcp=mock_mcp,
        get_mcp_storage=lambda: storage,
        get_mcp_event_store=lambda: event_store,
    )

    set_result = exported["thegent_storage_set"](key="k1", value='{"x":1}', ttl_seconds=5)
    assert set_result.structured_content == {"ok": True, "key": "k1"}
    storage.set.assert_called_once_with("k1", {"x": 1}, ttl=5.0)

    get_result = exported["thegent_storage_get"](key="k1")
    assert get_result.structured_content["found"] is True
    assert get_result.structured_content["value"] == {"hello": "world"}
    storage.get.assert_called_once_with("k1")

    emit_result = exported["thegent_events_emit"](event_type="storage.set", payload='{"k":"v"}')
    assert emit_result.structured_content == {"ok": True, "event_id": "evt-1", "event_type": "storage.set"}
    event_store.emit.assert_called_once_with("storage.set", {"k": "v"})

    replay_result = exported["thegent_events_replay"](since_id="evt-0")
    assert replay_result.structured_content == {"events": [{"event_id": "evt-1"}], "count": 1}
    event_store.replay.assert_called_once_with(since_event_id="evt-0")


def test_register_optional_tools_delegates_storage_block_to_helper() -> None:
    mock_mcp, _ = _mock_mcp_with_registry()
    log = MagicMock()
    helper = MagicMock(return_value={"thegent_storage_get": object()})

    storage_mod = SimpleNamespace(
        get_mcp_storage=lambda: object(),
        get_mcp_event_store=lambda: object(),
    )

    def _import_module(name: str) -> Any:
        if name == "thegent.mcp.storage":
            return storage_mod
        raise ImportError(name)

    exported = server_optional_tools.register_optional_tools(
        mcp=mock_mcp,
        log=log,
        import_module_fn=_import_module,
        register_storage_event_tools_fn=helper,
    )

    assert exported == {"thegent_storage_get": helper.return_value["thegent_storage_get"]}
    helper.assert_called_once()
    assert helper.call_args.kwargs["mcp"] is mock_mcp
    assert helper.call_args.kwargs["get_mcp_storage"] is storage_mod.get_mcp_storage
    assert helper.call_args.kwargs["get_mcp_event_store"] is storage_mod.get_mcp_event_store


def test_server_source_delegates_to_optional_tools_registrar() -> None:
    try:
        import thegent.mcp.server as server_mod
    except Exception as exc:  # pragma: no cover - environment dependent
        import pytest

        pytest.skip(f"server.py import raised: {exc}")

    source = inspect.getsource(server_mod)
    assert "from thegent.mcp import server_optional_tools as _server_optional_tools" in source
    assert "_optional_tools_exports = _server_optional_tools.register_optional_tools(" in source
    assert "globals().update(_optional_tools_exports)" in source
