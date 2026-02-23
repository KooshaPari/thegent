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


class ProviderSelectionPhase(TypedDict):
    candidate_providers: list[str]
    selected_provider: str
    selection_reason: str


class HookInvocationPhase(TypedDict):
    hook_name: str
    registration_id: str
    payload: dict[str, Any]


class QueueSchedulingPhase(TypedDict):
    prioritized_turn_ids: list[str]
    scheduler_epoch: int
    batch_size: int


class SyncCommitPhase(TypedDict):
    diff_records: list[dict[str, Any]]
    commit_id: str
    dry_run: bool


class CliDispatchPhase(TypedDict):
    parsed_command: str
    command_args: dict[str, Any]
    selected_handler: str


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


def build_provider_selection_phase(
    candidate_providers: list[str],
    selected_provider: str,
    selection_reason: str,
) -> ProviderSelectionPhase:
    return {
        "candidate_providers": candidate_providers,
        "selected_provider": selected_provider,
        "selection_reason": selection_reason,
    }


def resolve_workflow_guard_target(phase: ProviderSelectionPhase) -> tuple[list[str], str, str]:
    candidate_providers = phase.get("candidate_providers")
    selected_provider = phase.get("selected_provider")
    selection_reason = phase.get("selection_reason")
    if not isinstance(candidate_providers, list) or not candidate_providers:
        raise ValueError("Workflow guard target unresolved: invalid candidate_providers")
    if any(not isinstance(candidate, str) or not candidate for candidate in candidate_providers):
        raise ValueError("Workflow guard target unresolved: invalid candidate provider")
    if not isinstance(selected_provider, str) or not selected_provider:
        raise ValueError("Workflow guard target unresolved: invalid selected_provider")
    if not isinstance(selection_reason, str) or not selection_reason:
        raise ValueError("Workflow guard target unresolved: invalid selection_reason")
    return candidate_providers, selected_provider, selection_reason


def build_hook_invocation_phase(
    hook_name: str,
    registration_id: str,
    payload: dict[str, Any],
) -> HookInvocationPhase:
    return {
        "hook_name": hook_name,
        "registration_id": registration_id,
        "payload": payload,
    }


def resolve_policy_enforcement_target(
    phase: HookInvocationPhase,
) -> tuple[str, str, dict[str, Any]]:
    hook_name = phase.get("hook_name")
    registration_id = phase.get("registration_id")
    payload = phase.get("payload")
    if not isinstance(hook_name, str) or not hook_name:
        raise ValueError("Policy enforcement target unresolved: invalid hook_name")
    if not isinstance(registration_id, str) or not registration_id:
        raise ValueError("Policy enforcement target unresolved: invalid registration_id")
    if not isinstance(payload, dict):
        raise ValueError("Policy enforcement target unresolved: invalid payload")
    return hook_name, registration_id, payload


def build_queue_scheduling_phase(
    prioritized_turn_ids: list[str],
    scheduler_epoch: int,
    batch_size: int,
) -> QueueSchedulingPhase:
    return {
        "prioritized_turn_ids": prioritized_turn_ids,
        "scheduler_epoch": scheduler_epoch,
        "batch_size": batch_size,
    }


def resolve_session_persistence_target(
    phase: QueueSchedulingPhase,
) -> tuple[list[str], int, int]:
    prioritized_turn_ids = phase.get("prioritized_turn_ids")
    scheduler_epoch = phase.get("scheduler_epoch")
    batch_size = phase.get("batch_size")
    if not isinstance(prioritized_turn_ids, list) or not prioritized_turn_ids:
        raise ValueError("Session persistence target unresolved: invalid prioritized_turn_ids")
    if any(not isinstance(turn_id, str) or not turn_id for turn_id in prioritized_turn_ids):
        raise ValueError("Session persistence target unresolved: invalid turn_id")
    if not isinstance(scheduler_epoch, int) or scheduler_epoch < 0:
        raise ValueError("Session persistence target unresolved: invalid scheduler_epoch")
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("Session persistence target unresolved: invalid batch_size")
    return prioritized_turn_ids, scheduler_epoch, batch_size


def build_sync_commit_phase(
    diff_records: list[dict[str, Any]],
    commit_id: str,
    dry_run: bool,
) -> SyncCommitPhase:
    return {
        "diff_records": diff_records,
        "commit_id": commit_id,
        "dry_run": dry_run,
    }


def resolve_observability_target(
    phase: SyncCommitPhase,
) -> tuple[list[dict[str, Any]], str, bool]:
    diff_records = phase.get("diff_records")
    commit_id = phase.get("commit_id")
    dry_run = phase.get("dry_run")
    if not isinstance(diff_records, list):
        raise ValueError("Observability target unresolved: invalid diff_records")
    if any(not isinstance(record, dict) for record in diff_records):
        raise ValueError("Observability target unresolved: invalid diff record")
    if not isinstance(commit_id, str) or not commit_id:
        raise ValueError("Observability target unresolved: invalid commit_id")
    if not isinstance(dry_run, bool):
        raise ValueError("Observability target unresolved: invalid dry_run")
    return diff_records, commit_id, dry_run


def build_cli_dispatch_phase(
    parsed_command: str,
    command_args: dict[str, Any],
    selected_handler: str,
) -> CliDispatchPhase:
    return {
        "parsed_command": parsed_command,
        "command_args": command_args,
        "selected_handler": selected_handler,
    }


def resolve_retry_outcome_target(
    phase: CliDispatchPhase,
) -> tuple[str, dict[str, Any], str]:
    parsed_command = phase.get("parsed_command")
    command_args = phase.get("command_args")
    selected_handler = phase.get("selected_handler")
    if not isinstance(parsed_command, str) or not parsed_command:
        raise ValueError("Retry outcome target unresolved: invalid parsed_command")
    if not isinstance(command_args, dict):
        raise ValueError("Retry outcome target unresolved: invalid command_args")
    if not isinstance(selected_handler, str) or not selected_handler:
        raise ValueError("Retry outcome target unresolved: invalid selected_handler")
    return parsed_command, command_args, selected_handler
