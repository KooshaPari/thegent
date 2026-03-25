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


class ProviderRuleEvaluationPhase(TypedDict):
    candidate_scores: dict[str, int]
    selection_strategy: str
    selected_provider: str


class WorkflowGuardPhase(TypedDict):
    workflow_id: str
    guard_results: dict[str, bool]
    execution_step: str


class HookRegistrationPhase(TypedDict):
    hook_name: str
    registration_options: dict[str, Any]
    invocation_payload: dict[str, Any]


class PolicyMatchPhase(TypedDict):
    policy_id: str
    matched_rules: list[str]
    enforcement_action: str


class QueuePriorityPhase(TypedDict):
    priority_bucket: str
    queued_turn_ids: list[str]
    dispatch_window: int


class SessionStateUpdatePhase(TypedDict):
    session_id: str
    state_changes: dict[str, Any]
    persistence_revision: int


class SyncDiffPhase(TypedDict):
    diff_records: list[dict[str, Any]]
    commit_message: str
    commit_author: str


class ObservabilityEventPhase(TypedDict):
    event_name: str
    event_payload: dict[str, Any]
    serialization_format: str


class CliCommandParsePhase(TypedDict):
    raw_command: str
    parsed_tokens: list[str]
    selected_handler: str


class RetryLoopPhase(TypedDict):
    attempt_count: int
    max_attempts: int
    terminal_outcome: str


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


def build_commit_phase(session_id: str, session: dict[str, Any], turn_id: str, turn: dict[str, Any]) -> CommitPhase:
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


def build_provider_rule_evaluation_phase(
    candidate_scores: dict[str, int],
    selection_strategy: str,
    selected_provider: str,
) -> ProviderRuleEvaluationPhase:
    return {
        "candidate_scores": candidate_scores,
        "selection_strategy": selection_strategy,
        "selected_provider": selected_provider,
    }


def resolve_provider_final_selection_target(
    phase: ProviderRuleEvaluationPhase,
) -> tuple[dict[str, int], str, str]:
    candidate_scores = phase.get("candidate_scores")
    selection_strategy = phase.get("selection_strategy")
    selected_provider = phase.get("selected_provider")
    if not isinstance(candidate_scores, dict) or not candidate_scores:
        raise ValueError("Provider final selection target unresolved: invalid candidate_scores")
    if any(not isinstance(provider, str) or not provider for provider in candidate_scores):
        raise ValueError("Provider final selection target unresolved: invalid provider key")
    if any(not isinstance(score, int) for score in candidate_scores.values()):
        raise ValueError("Provider final selection target unresolved: invalid provider score")
    if not isinstance(selection_strategy, str) or not selection_strategy:
        raise ValueError("Provider final selection target unresolved: invalid selection_strategy")
    if not isinstance(selected_provider, str) or not selected_provider:
        raise ValueError("Provider final selection target unresolved: invalid selected_provider")
    if selected_provider not in candidate_scores:
        raise ValueError("Provider final selection target unresolved: selected provider missing score")
    return candidate_scores, selection_strategy, selected_provider


def build_workflow_guard_phase(
    workflow_id: str,
    guard_results: dict[str, bool],
    execution_step: str,
) -> WorkflowGuardPhase:
    return {
        "workflow_id": workflow_id,
        "guard_results": guard_results,
        "execution_step": execution_step,
    }


def resolve_workflow_execution_target(
    phase: WorkflowGuardPhase,
) -> tuple[str, dict[str, bool], str]:
    workflow_id = phase.get("workflow_id")
    guard_results = phase.get("guard_results")
    execution_step = phase.get("execution_step")
    if not isinstance(workflow_id, str) or not workflow_id:
        raise ValueError("Workflow execution target unresolved: invalid workflow_id")
    if not isinstance(guard_results, dict) or not guard_results:
        raise ValueError("Workflow execution target unresolved: invalid guard_results")
    if any(not isinstance(name, str) or not name for name in guard_results):
        raise ValueError("Workflow execution target unresolved: invalid guard name")
    if any(not isinstance(passed, bool) for passed in guard_results.values()):
        raise ValueError("Workflow execution target unresolved: invalid guard value")
    if not all(guard_results.values()):
        raise ValueError("Workflow execution target unresolved: guard check failed")
    if not isinstance(execution_step, str) or not execution_step:
        raise ValueError("Workflow execution target unresolved: invalid execution_step")
    return workflow_id, guard_results, execution_step


def build_hook_registration_phase(
    hook_name: str,
    registration_options: dict[str, Any],
    invocation_payload: dict[str, Any],
) -> HookRegistrationPhase:
    return {
        "hook_name": hook_name,
        "registration_options": registration_options,
        "invocation_payload": invocation_payload,
    }


def resolve_hook_invocation_target(
    phase: HookRegistrationPhase,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    hook_name = phase.get("hook_name")
    registration_options = phase.get("registration_options")
    invocation_payload = phase.get("invocation_payload")
    if not isinstance(hook_name, str) or not hook_name:
        raise ValueError("Hook invocation target unresolved: invalid hook_name")
    if not isinstance(registration_options, dict):
        raise ValueError("Hook invocation target unresolved: invalid registration_options")
    if not isinstance(invocation_payload, dict):
        raise ValueError("Hook invocation target unresolved: invalid invocation_payload")
    return hook_name, registration_options, invocation_payload


def build_policy_match_phase(
    policy_id: str,
    matched_rules: list[str],
    enforcement_action: str,
) -> PolicyMatchPhase:
    return {
        "policy_id": policy_id,
        "matched_rules": matched_rules,
        "enforcement_action": enforcement_action,
    }


def resolve_policy_enforcement_plan_target(
    phase: PolicyMatchPhase,
) -> tuple[str, list[str], str]:
    policy_id = phase.get("policy_id")
    matched_rules = phase.get("matched_rules")
    enforcement_action = phase.get("enforcement_action")
    if not isinstance(policy_id, str) or not policy_id:
        raise ValueError("Policy enforcement plan target unresolved: invalid policy_id")
    if not isinstance(matched_rules, list) or not matched_rules:
        raise ValueError("Policy enforcement plan target unresolved: invalid matched_rules")
    if any(not isinstance(rule, str) or not rule for rule in matched_rules):
        raise ValueError("Policy enforcement plan target unresolved: invalid matched rule")
    if not isinstance(enforcement_action, str) or not enforcement_action:
        raise ValueError("Policy enforcement plan target unresolved: invalid enforcement_action")
    return policy_id, matched_rules, enforcement_action


def build_queue_priority_phase(
    priority_bucket: str,
    queued_turn_ids: list[str],
    dispatch_window: int,
) -> QueuePriorityPhase:
    return {
        "priority_bucket": priority_bucket,
        "queued_turn_ids": queued_turn_ids,
        "dispatch_window": dispatch_window,
    }


def resolve_queue_execution_target(
    phase: QueuePriorityPhase,
) -> tuple[str, list[str], int]:
    priority_bucket = phase.get("priority_bucket")
    queued_turn_ids = phase.get("queued_turn_ids")
    dispatch_window = phase.get("dispatch_window")
    if not isinstance(priority_bucket, str) or not priority_bucket:
        raise ValueError("Queue execution target unresolved: invalid priority_bucket")
    if not isinstance(queued_turn_ids, list) or not queued_turn_ids:
        raise ValueError("Queue execution target unresolved: invalid queued_turn_ids")
    if any(not isinstance(turn_id, str) or not turn_id for turn_id in queued_turn_ids):
        raise ValueError("Queue execution target unresolved: invalid queued turn_id")
    if not isinstance(dispatch_window, int) or dispatch_window <= 0:
        raise ValueError("Queue execution target unresolved: invalid dispatch_window")
    return priority_bucket, queued_turn_ids, dispatch_window


def build_session_state_update_phase(
    session_id: str,
    state_changes: dict[str, Any],
    persistence_revision: int,
) -> SessionStateUpdatePhase:
    return {
        "session_id": session_id,
        "state_changes": state_changes,
        "persistence_revision": persistence_revision,
    }


def resolve_session_persistence_plan_target(
    phase: SessionStateUpdatePhase,
) -> tuple[str, dict[str, Any], int]:
    session_id = phase.get("session_id")
    state_changes = phase.get("state_changes")
    persistence_revision = phase.get("persistence_revision")
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("Session persistence plan target unresolved: invalid session_id")
    if not isinstance(state_changes, dict):
        raise ValueError("Session persistence plan target unresolved: invalid state_changes")
    if not isinstance(persistence_revision, int) or persistence_revision < 0:
        raise ValueError("Session persistence plan target unresolved: invalid persistence_revision")
    return session_id, state_changes, persistence_revision


def build_sync_diff_phase(
    diff_records: list[dict[str, Any]],
    commit_message: str,
    commit_author: str,
) -> SyncDiffPhase:
    return {
        "diff_records": diff_records,
        "commit_message": commit_message,
        "commit_author": commit_author,
    }


def resolve_sync_commit_plan_target(
    phase: SyncDiffPhase,
) -> tuple[list[dict[str, Any]], str, str]:
    diff_records = phase.get("diff_records")
    commit_message = phase.get("commit_message")
    commit_author = phase.get("commit_author")
    if not isinstance(diff_records, list):
        raise ValueError("Sync commit plan target unresolved: invalid diff_records")
    if any(not isinstance(record, dict) for record in diff_records):
        raise ValueError("Sync commit plan target unresolved: invalid diff record")
    if not isinstance(commit_message, str) or not commit_message:
        raise ValueError("Sync commit plan target unresolved: invalid commit_message")
    if not isinstance(commit_author, str) or not commit_author:
        raise ValueError("Sync commit plan target unresolved: invalid commit_author")
    return diff_records, commit_message, commit_author


def build_observability_event_phase(
    event_name: str,
    event_payload: dict[str, Any],
    serialization_format: str,
) -> ObservabilityEventPhase:
    return {
        "event_name": event_name,
        "event_payload": event_payload,
        "serialization_format": serialization_format,
    }


def resolve_observability_serialization_target(
    phase: ObservabilityEventPhase,
) -> tuple[str, dict[str, Any], str]:
    event_name = phase.get("event_name")
    event_payload = phase.get("event_payload")
    serialization_format = phase.get("serialization_format")
    if not isinstance(event_name, str) or not event_name:
        raise ValueError("Observability serialization target unresolved: invalid event_name")
    if not isinstance(event_payload, dict):
        raise ValueError("Observability serialization target unresolved: invalid event_payload")
    if not isinstance(serialization_format, str) or not serialization_format:
        raise ValueError("Observability serialization target unresolved: invalid serialization_format")
    return event_name, event_payload, serialization_format


def build_cli_command_parse_phase(
    raw_command: str,
    parsed_tokens: list[str],
    selected_handler: str,
) -> CliCommandParsePhase:
    return {
        "raw_command": raw_command,
        "parsed_tokens": parsed_tokens,
        "selected_handler": selected_handler,
    }


def resolve_cli_handler_selection_target(
    phase: CliCommandParsePhase,
) -> tuple[str, list[str], str]:
    raw_command = phase.get("raw_command")
    parsed_tokens = phase.get("parsed_tokens")
    selected_handler = phase.get("selected_handler")
    if not isinstance(raw_command, str) or not raw_command:
        raise ValueError("CLI handler selection target unresolved: invalid raw_command")
    if not isinstance(parsed_tokens, list) or not parsed_tokens:
        raise ValueError("CLI handler selection target unresolved: invalid parsed_tokens")
    if any(not isinstance(token, str) or not token for token in parsed_tokens):
        raise ValueError("CLI handler selection target unresolved: invalid parsed token")
    if not isinstance(selected_handler, str) or not selected_handler:
        raise ValueError("CLI handler selection target unresolved: invalid selected_handler")
    return raw_command, parsed_tokens, selected_handler


def build_retry_loop_phase(
    attempt_count: int,
    max_attempts: int,
    terminal_outcome: str,
) -> RetryLoopPhase:
    return {
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "terminal_outcome": terminal_outcome,
    }


def resolve_terminal_outcome_target(
    phase: RetryLoopPhase,
) -> tuple[int, int, str]:
    attempt_count = phase.get("attempt_count")
    max_attempts = phase.get("max_attempts")
    terminal_outcome = phase.get("terminal_outcome")
    if not isinstance(attempt_count, int) or attempt_count < 0:
        raise ValueError("Terminal outcome target unresolved: invalid attempt_count")
    if not isinstance(max_attempts, int) or max_attempts <= 0:
        raise ValueError("Terminal outcome target unresolved: invalid max_attempts")
    if attempt_count > max_attempts:
        raise ValueError("Terminal outcome target unresolved: attempt_count exceeds max_attempts")
    if not isinstance(terminal_outcome, str) or not terminal_outcome:
        raise ValueError("Terminal outcome target unresolved: invalid terminal_outcome")
    return attempt_count, max_attempts, terminal_outcome
