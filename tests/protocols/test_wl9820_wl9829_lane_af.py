"""Lane AF regressions for WL-9820..WL-9829 on turn/submit phase boundaries."""

from __future__ import annotations

import orjson as json
import pytest
from thegent.protocols.jsonrpc_agent_server import SERVER_STATE, process_jsonrpc_line_full

from thegent.protocols import jsonrpc_agent_server as server


def _reset_state() -> None:
    SERVER_STATE.session_counter = 0
    SERVER_STATE.turn_counter = 0
    SERVER_STATE.approval_counter = 0
    SERVER_STATE.tool_call_counter = 0
    SERVER_STATE.sessions.clear()
    SERVER_STATE.turns.clear()
    SERVER_STATE.approvals.clear()


def _start_session() -> str:
    response, _notifications = process_jsonrpc_line_full(
        json.dumps({"jsonrpc": "2.0", "id": "start", "method": "session/start"}).decode()
    )
    assert response is not None
    return response["result"]["session"]["id"]


def test_wl9820_commit_phase_separates_plan_build_from_mutation() -> None:
    # @trace WL-9820
    _reset_state()
    session_id = _start_session()
    session = SERVER_STATE.sessions[session_id]
    commit_phase = server._build_turn_submit_commit_phase(session_id, session, "af")
    assert isinstance(commit_phase["turn_id"], str)
    assert commit_phase["turn"]["status"] == "in_progress"
    assert SERVER_STATE.turns == {}
    assert session["turn_ids"] == []


def test_wl9821_commit_target_resolution_is_typed_and_stable() -> None:
    # @trace WL-9821
    _reset_state()
    session_id = _start_session()
    session = SERVER_STATE.sessions[session_id]
    commit_phase = server._build_turn_submit_commit_phase(session_id, session, "af")
    turn_id, turn, resolved_session = server._resolve_turn_submit_commit_target(commit_phase)
    assert turn_id == commit_phase["turn_id"]
    assert turn is commit_phase["turn"]
    assert resolved_session is session


def test_wl9822_commit_target_fails_loudly_on_invalid_shape() -> None:
    # @trace WL-9822
    with pytest.raises(ValueError, match="Turn submit commit target unresolved"):
        server._resolve_turn_submit_commit_target({"turn_id": None, "turn": None, "session": None})


def test_wl9823_side_effects_phase_materializes_explicit_boundary_payload() -> None:
    # @trace WL-9823
    _reset_state()
    session_id = _start_session()
    turn_id = "turn-1"
    turn = {"id": turn_id, "session_id": session_id, "status": "in_progress"}
    phase = server._build_turn_submit_side_effects_phase(session_id, turn_id, turn, "af", False, None)
    assert phase["session_id"] == session_id
    assert phase["turn_id"] == turn_id
    assert phase["requires_approval"] is False


def test_wl9824_side_effects_target_resolution_preserves_approval_tuple() -> None:
    # @trace WL-9824
    _reset_state()
    session_id = _start_session()
    turn_id = "turn-1"
    turn = {"id": turn_id, "session_id": session_id, "status": "in_progress"}
    phase = server._build_turn_submit_side_effects_phase(session_id, turn_id, turn, "af", True, "diff")
    resolved = server._resolve_turn_submit_side_effects_target(phase)
    assert resolved[0] == session_id
    assert resolved[1] == turn_id
    assert resolved[2] is turn
    assert resolved[4] is True
    assert resolved[5] == "diff"


def test_wl9825_side_effects_target_fails_loudly_on_invalid_shape() -> None:
    # @trace WL-9825
    with pytest.raises(ValueError, match="Turn submit side-effects target unresolved"):
        server._resolve_turn_submit_side_effects_target(
            {
                "session_id": "session-1",
                "turn_id": "turn-1",
                "turn": {},
                "user_input": "af",
                "requires_approval": "yes",
                "approval_diff": None,
            }
        )


def test_wl9826_response_phase_preserves_turn_and_optional_approval_payload() -> None:
    # @trace WL-9826
    turn = {"id": "turn-1"}
    response_phase = server._build_turn_submit_response_phase(True, "req", turn, {"id": "approval-1"})
    assert response_phase["request_has_id"] is True
    assert response_phase["turn"] is turn
    assert response_phase["approval_payload"] == {"id": "approval-1"}


def test_wl9827_response_target_resolution_is_typed() -> None:
    # @trace WL-9827
    turn = {"id": "turn-1"}
    response_phase = server._build_turn_submit_response_phase(False, None, turn, None)
    request_has_id, request_id, resolved_turn, approval_payload = server._resolve_turn_submit_response_target(
        response_phase
    )
    assert request_has_id is False
    assert request_id is None
    assert resolved_turn is turn
    assert approval_payload is None


def test_wl9828_response_target_fails_loudly_on_invalid_shape() -> None:
    # @trace WL-9828
    with pytest.raises(ValueError, match="Turn submit response target unresolved"):
        server._resolve_turn_submit_response_target(
            {"request_has_id": True, "request_id": "req", "turn": {"id": "turn-1"}, "approval_payload": "bad"}
        )


def test_wl9829_handler_preserves_notification_mode_and_turn_mutation() -> None:
    # @trace WL-9829
    _reset_state()
    session_id = _start_session()
    response, notifications = process_jsonrpc_line_full(
        json.dumps(
            {"jsonrpc": "2.0", "method": "turn/submit", "params": {"session_id": session_id, "input": "af"}}
        ).decode()
    )
    assert response is None
    assert notifications[0]["method"] == "turn/started"
    assert notifications[-1]["method"] == "turn/completed"
    turn_id = SERVER_STATE.sessions[session_id]["turn_ids"][0]
    assert SERVER_STATE.turns[turn_id]["status"] == "completed"
