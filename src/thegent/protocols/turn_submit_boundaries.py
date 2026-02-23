"""Typed phase boundaries for turn/submit orchestration helpers."""

from __future__ import annotations

from typing import Any, TypedDict


class ParsePhase(TypedDict):
    session_id: str
    user_input: str
    request_id: str | int | float | None
    request_has_id: bool


class CommitPhase(TypedDict):
    session_id: str
    session: dict[str, Any]
    turn_id: str
    turn: dict[str, Any]


class SideEffectsPhase(TypedDict):
    session_id: str
    turn_id: str
    turn: dict[str, Any]
    user_input: str
    requires_approval: bool
    approval_diff: str | None


class ResponsePhase(TypedDict):
    request_has_id: bool
    request_id: str | int | float | None
    turn: dict[str, Any]
    approval_payload: dict[str, Any] | None


def build_parse_phase(
    session_id: str,
    user_input: str,
    *,
    request_id: str | int | float | None,
    request_has_id: bool,
) -> ParsePhase:
    return {
        "session_id": session_id,
        "user_input": user_input,
        "request_id": request_id,
        "request_has_id": request_has_id,
    }


def resolve_parse_target(phase: ParsePhase) -> tuple[str, str, str | int | float | None, bool]:
    session_id = phase.get("session_id")
    user_input = phase.get("user_input")
    request_id = phase.get("request_id")
    request_has_id = phase.get("request_has_id")
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("Turn submit parse target unresolved: invalid session_id")
    if not isinstance(user_input, str):
        raise ValueError("Turn submit parse target unresolved: invalid user_input")
    if not isinstance(request_has_id, bool):
        raise ValueError("Turn submit parse target unresolved: invalid request_has_id")
    return session_id, user_input, request_id, request_has_id


def build_commit_phase(
    session_id: str, session: dict[str, Any], turn_id: str, turn: dict[str, Any]
) -> CommitPhase:
    return {
        "session_id": session_id,
        "session": session,
        "turn_id": turn_id,
        "turn": turn,
    }


def resolve_commit_target(phase: CommitPhase) -> tuple[str, dict[str, Any], str, dict[str, Any]]:
    session_id = phase.get("session_id")
    session = phase.get("session")
    turn_id = phase.get("turn_id")
    turn = phase.get("turn")
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("Turn submit commit target unresolved: invalid session_id")
    if not isinstance(session, dict):
        raise ValueError("Turn submit commit target unresolved: invalid session")
    if not isinstance(turn_id, str) or not turn_id:
        raise ValueError("Turn submit commit target unresolved: invalid turn_id")
    if not isinstance(turn, dict):
        raise ValueError("Turn submit commit target unresolved: invalid turn")
    return session_id, session, turn_id, turn


def build_side_effects_phase(
    session_id: str,
    turn_id: str,
    turn: dict[str, Any],
    user_input: str,
    requires_approval: bool,
    approval_diff: str | None,
) -> SideEffectsPhase:
    return {
        "session_id": session_id,
        "turn_id": turn_id,
        "turn": turn,
        "user_input": user_input,
        "requires_approval": requires_approval,
        "approval_diff": approval_diff,
    }


def resolve_side_effects_target(
    phase: SideEffectsPhase,
) -> tuple[str, str, dict[str, Any], str, bool, str | None]:
    session_id = phase.get("session_id")
    turn_id = phase.get("turn_id")
    turn = phase.get("turn")
    user_input = phase.get("user_input")
    requires_approval = phase.get("requires_approval")
    approval_diff = phase.get("approval_diff")
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("Turn submit side-effects target unresolved: invalid session_id")
    if not isinstance(turn_id, str) or not turn_id:
        raise ValueError("Turn submit side-effects target unresolved: invalid turn_id")
    if not isinstance(turn, dict):
        raise ValueError("Turn submit side-effects target unresolved: invalid turn")
    if not isinstance(user_input, str):
        raise ValueError("Turn submit side-effects target unresolved: invalid user_input")
    if not isinstance(requires_approval, bool):
        raise ValueError("Turn submit side-effects target unresolved: invalid requires_approval")
    if approval_diff is not None and not isinstance(approval_diff, str):
        raise ValueError("Turn submit side-effects target unresolved: invalid approval_diff")
    return session_id, turn_id, turn, user_input, requires_approval, approval_diff


def build_response_phase(
    request_has_id: bool,
    request_id: str | int | float | None,
    turn: dict[str, Any],
    approval_payload: dict[str, Any] | None,
) -> ResponsePhase:
    return {
        "request_has_id": request_has_id,
        "request_id": request_id,
        "turn": turn,
        "approval_payload": approval_payload,
    }


def resolve_response_target(
    phase: ResponsePhase,
) -> tuple[bool, str | int | float | None, dict[str, Any], dict[str, Any] | None]:
    request_has_id = phase.get("request_has_id")
    request_id = phase.get("request_id")
    turn = phase.get("turn")
    approval_payload = phase.get("approval_payload")
    if not isinstance(request_has_id, bool):
        raise ValueError("Turn submit response target unresolved: invalid request_has_id")
    if not isinstance(turn, dict):
        raise ValueError("Turn submit response target unresolved: invalid turn")
    if approval_payload is not None and not isinstance(approval_payload, dict):
        raise ValueError("Turn submit response target unresolved: invalid approval_payload")
    return request_has_id, request_id, turn, approval_payload
