# @trace WL-120 B90-W2-D3
"""Focused tests for MCP planning/journal extraction loaders."""

from __future__ import annotations

import inspect
import json
from types import SimpleNamespace
from typing import Any
from unittest.mock import ANY, MagicMock


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


def test_register_planning_tools_registers_expected_names() -> None:
    from thegent.mcp.server_planning_tools import register_planning_tools

    mock_mcp, registered = _mock_mcp_with_registry()

    async def _dag_list_impl(**kwargs: Any) -> dict[str, Any]:
        return kwargs

    result = register_planning_tools(
        mcp=mock_mcp,
        server_tools_planning=SimpleNamespace(
            thegent_dag_list_impl=_dag_list_impl,
            thegent_do_next_impl=lambda **kwargs: kwargs,
            thegent_plan_get_next_impl=lambda **kwargs: kwargs,
            thegent_plan_wait_next_impl=lambda **kwargs: kwargs,
            thegent_history_impl=lambda **kwargs: kwargs,
            thegent_plan_progress_impl=lambda **kwargs: kwargs,
            thegent_plan_analyze_impl=lambda **kwargs: kwargs,
        ),
        server_tools_locking_planning=SimpleNamespace(
            thegent_lock_resource_impl=lambda **kwargs: kwargs,
            thegent_unlock_resource_impl=lambda **kwargs: kwargs,
            thegent_verify_context_impl=lambda **kwargs: kwargs,
            thegent_retry_impl=lambda **kwargs: kwargs,
            thegent_plan_incorporate_impl=lambda **kwargs: kwargs,
        ),
        server_tools_contract_observe=SimpleNamespace(
            thegent_dag_status_impl=lambda **kwargs: kwargs,
        ),
        server_tools_escalation=SimpleNamespace(
            thegent_escalate_list_impl=lambda **kwargs: kwargs,
            thegent_escalate_add_impl=lambda **kwargs: kwargs,
            thegent_escalate_approve_impl=lambda **kwargs: kwargs,
            thegent_escalate_resolve_impl=lambda **kwargs: kwargs,
            thegent_govern_list_pending_impl=lambda **kwargs: kwargs,
        ),
        get_default_cwd=lambda: None,
        resolve_cwd=lambda x: x,
        elicit_cwd_msg="cwd?",
        elicit_timeout_s=30,
        accepted_elicitation_type=object,
        declined_elicitation_type=object,
        cancelled_elicitation_type=object,
        dag_list_impl=lambda **kwargs: kwargs,
        do_next_impl=lambda **kwargs: kwargs,
        wait_next_impl=lambda **kwargs: kwargs,
        history_impl=lambda **kwargs: kwargs,
        plan_analyze_impl=lambda **kwargs: kwargs,
        retry_impl=lambda **kwargs: kwargs,
        incorporate_impl=lambda **kwargs: kwargs,
        dag_status_impl=lambda **kwargs: kwargs,
        escalate_list_impl=lambda **kwargs: kwargs,
        escalate_add_impl=lambda **kwargs: kwargs,
        escalate_approve_impl=lambda **kwargs: kwargs,
        escalate_resolve_impl=lambda **kwargs: kwargs,
        govern_list_pending_impl=lambda **kwargs: kwargs,
        error_result=lambda message, hint=None: {"error": message, "hint": hint},
    )

    assert isinstance(result, tuple)
    assert len(result) == 18
    expected = {
        "thegent_dag_list",
        "thegent_do_next",
        "thegent_lock_resource",
        "thegent_unlock_resource",
        "thegent_verify_context",
        "thegent_plan_get_next",
        "thegent_plan_wait_next",
        "thegent_history",
        "thegent_plan_progress",
        "thegent_plan_analyze",
        "thegent_retry",
        "thegent_plan_incorporate",
        "thegent_dag_status",
        "thegent_escalate_list",
        "thegent_escalate_add",
        "thegent_escalate_approve",
        "thegent_escalate_resolve",
        "thegent_govern_list_pending",
    }
    assert expected <= set(registered)


def test_planning_contract_plan_wait_next_passes_expected_args() -> None:
    from thegent.mcp.server_planning_tools import register_planning_tools

    mock_mcp, registered = _mock_mcp_with_registry()
    wait_next_impl = MagicMock(return_value={"wait": "next"})

    async def _dag_list_impl(**kwargs: Any) -> dict[str, Any]:
        return kwargs

    register_planning_tools(
        mcp=mock_mcp,
        server_tools_planning=SimpleNamespace(
            thegent_dag_list_impl=_dag_list_impl,
            thegent_do_next_impl=lambda **kwargs: kwargs,
            thegent_plan_get_next_impl=lambda **kwargs: kwargs,
            thegent_plan_wait_next_impl=wait_next_impl,
            thegent_history_impl=lambda **kwargs: kwargs,
            thegent_plan_progress_impl=lambda **kwargs: kwargs,
            thegent_plan_analyze_impl=lambda **kwargs: kwargs,
        ),
        server_tools_locking_planning=SimpleNamespace(
            thegent_lock_resource_impl=lambda **kwargs: kwargs,
            thegent_unlock_resource_impl=lambda **kwargs: kwargs,
            thegent_verify_context_impl=lambda **kwargs: kwargs,
            thegent_retry_impl=lambda **kwargs: kwargs,
            thegent_plan_incorporate_impl=lambda **kwargs: kwargs,
        ),
        server_tools_contract_observe=SimpleNamespace(
            thegent_dag_status_impl=lambda **kwargs: kwargs,
        ),
        server_tools_escalation=SimpleNamespace(
            thegent_escalate_list_impl=lambda **kwargs: kwargs,
            thegent_escalate_add_impl=lambda **kwargs: kwargs,
            thegent_escalate_approve_impl=lambda **kwargs: kwargs,
            thegent_escalate_resolve_impl=lambda **kwargs: kwargs,
            thegent_govern_list_pending_impl=lambda **kwargs: kwargs,
        ),
        get_default_cwd=lambda: None,
        resolve_cwd=lambda x: x,
        elicit_cwd_msg="cwd?",
        elicit_timeout_s=30,
        accepted_elicitation_type=object,
        declined_elicitation_type=object,
        cancelled_elicitation_type=object,
        dag_list_impl=lambda **kwargs: kwargs,
        do_next_impl=lambda **kwargs: kwargs,
        wait_next_impl=lambda **kwargs: kwargs,
        history_impl=lambda **kwargs: kwargs,
        plan_analyze_impl=lambda **kwargs: kwargs,
        retry_impl=lambda **kwargs: kwargs,
        incorporate_impl=lambda **kwargs: kwargs,
        dag_status_impl=lambda **kwargs: kwargs,
        escalate_list_impl=lambda **kwargs: kwargs,
        escalate_add_impl=lambda **kwargs: kwargs,
        escalate_approve_impl=lambda **kwargs: kwargs,
        escalate_resolve_impl=lambda **kwargs: kwargs,
        govern_list_pending_impl=lambda **kwargs: kwargs,
        error_result=lambda message, hint=None: {"error": message, "hint": hint},
    )

    result = registered["thegent_plan_wait_next"](
        cd="/tmp/repo",
        poll=3.0,
        timeout=8.0,
        sources="dag,escalation",
    )

    assert result == {"wait": "next"}
    wait_next_impl.assert_called_once_with(
        cd="/tmp/repo",
        poll=3.0,
        timeout=8.0,
        sources="dag,escalation",
        wait_next_impl=ANY,
        error_result_impl=ANY,
    )


def test_register_journal_tools_registers_expected_names() -> None:
    from thegent.mcp.server_journal_tools import register_journal_tools

    mock_mcp, registered = _mock_mcp_with_registry()
    result = register_journal_tools(mcp=mock_mcp, logger=MagicMock())

    assert isinstance(result, tuple)
    assert len(result) == 14
    expected = {
        "journal_create_session",
        "journal_record_change",
        "journal_snapshot",
        "journal_get_log",
        "journal_list_sessions",
        "journal_finalize",
        "journal_prune",
        "journal_create_enhanced",
        "journal_start_watching",
        "journal_get_attestations",
        "journal_get_stats",
        "journal_record_async",
        "journal_flush_batch",
        "thegent_orchestration_events",
    }
    assert expected <= set(registered)


def test_journal_contract_orchestration_events_returns_structured_payload(monkeypatch: Any) -> None:
    from thegent.mcp.server_journal_tools import register_journal_tools

    class _Event:
        def __init__(self, payload: dict[str, Any]) -> None:
            self._payload = payload

        def model_dump(self) -> dict[str, Any]:
            return self._payload

    class _Queue:
        def __init__(self, events: list[_Event]) -> None:
            self._events = events

        @property
        def empty(self) -> bool:
            return len(self._events) == 0

        def get_nowait(self) -> _Event:
            return self._events.pop(0)

    queue = _Queue([_Event({"id": "e1"}), _Event({"id": "e2"})])

    import thegent.orchestration.event_queue as event_queue

    monkeypatch.setattr(event_queue, "get_global_event_queue", lambda: queue)

    mock_mcp, registered = _mock_mcp_with_registry()
    register_journal_tools(mcp=mock_mcp, logger=MagicMock())
    result = registered["thegent_orchestration_events"](max_events=10, timeout_ms=0)

    assert result.structured_content == {"events": [{"id": "e1"}, {"id": "e2"}], "count": 2}
    raw_content = result.content[0].text if isinstance(result.content, list) else result.content
    assert json.loads(raw_content) == {"events": [{"id": "e1"}, {"id": "e2"}], "count": 2}


def test_server_source_wires_planning_and_journal_loader_rebinds() -> None:
    try:
        import thegent.mcp.server as server_mod
    except Exception as exc:  # pragma: no cover - environment dependent
        import pytest

        pytest.skip(f"server.py import raised: {exc}")

    source = inspect.getsource(server_mod)
    assert "_server_planning_tools.register_planning_tools(" in source
    assert "_server_journal_tools.register_journal_tools(" in source
    for name in (
        "thegent_plan_wait_next",
        "thegent_escalate_add",
        "journal_create_session",
        "thegent_orchestration_events",
    ):
        assert f"{name}," in source
