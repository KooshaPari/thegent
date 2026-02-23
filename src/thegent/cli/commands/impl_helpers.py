"""Thegent implementation layer helpers and constants (re-exports)."""

from thegent.cli.services import (
    pre_work_gate_helpers,
    run_audio_helpers,
    run_dag_helpers,
    run_event_helpers,
    run_health_helpers,
    run_input_helpers,
    run_model_helpers,
    run_observe_helpers,
    run_session_helpers,
    run_workstream_helpers,
    spawn_retry_helpers,
    retry_helpers,
    work_stream_orchestration,
    process_helpers,
)
from thegent.output_parser import condense_stream_to_display, extract_condensed
from thegent.execution import LoadClassifier

__all__ = [
    "CWD_CACHE",
    "SECONDS_PER_TOOL_CALL",
    "_CONTINUATION_MULTI_HOP_TOTAL_CAP",
    "_CONTINUATION_STDERR_CHARS",
    "_CONTINUATION_TAIL_CHARS",
    "_EAGAIN_ERRNOS",
    "_LOG_FOLLOW_POLL_SECONDS",
    "_MODEL_INDEXES_PATH",
    "_SUPPORTED_IMAGE_SUFFIXES",
    "LoadClassifier",
    "append_context_usage",
    "append_health_snapshot",
    "append_observe_summary_snapshot",
    "apply_pareto_routing",
    "backoff_delay",
    "build_audio_summary_metadata",
    "build_observe_summary_trend_scope",
    "check_dependencies_satisfied",
    "classify_observe_summary_trend_health",
    "coerce_issue_types",
    "collect_queued_items",
    "collect_work_stream_items",
    "compact_health_snapshot_log",
    "compose_owner_tag",
    "condense_stream_to_display",
    "dag_update_task",
    "default_owner_tag",
    "enforce_pre_work_hard_gate",
    "evidence_age_minutes",
    "extract_condensed",
    "get_fallback_agents",
    "get_ready_task_ids",
    "hash_health_payload",
    "hash_observe_summary_payload",
    "hash_observe_summary_trend_scope",
    "health_scope_key",
    "health_snapshot_log_path",
    "health_snapshot_max_lines",
    "inject_time_constraint",
    "is_pid_running",
    "list_agent_names",
    "load_observe_summary_snapshots",
    "load_previous_health_snapshot",
    "model_supports_vision",
    "new_session_id",
    "normalize_image_paths",
    "observe_summary_freshness_bucket",
    "parse_dag_full",
    "parse_dag_session",
    "parse_depends_on",
    "parse_observe_summary_env_float",
    "parse_observe_summary_env_int",
    "parse_observe_summary_timestamp",
    "parse_work_stream_md",
    "pre_work_gate_defaults",
    "pre_work_gate_thresholds",
    "pre_work_governance_block_payload",
    "priority_sort_key",
    "resolve_agent",
    "resolve_agent_model",
    "resolve_audio_transcript_for_output",
    "resolve_cwd",
    "resolve_droids_dir",
    "resolve_grounding_sources_for_output",
    "resolve_health_policy",
    "retry_if_eagain",
    "scope_key",
    "serialize_dag",
    "session_dir",
    "session_paths",
    "session_scope_dirs",
    "spawn_with_eagain_retry",
    "update_teammate_status",
    "validate_agent",
    "validate_dag",
    "validate_explicit_ollama_provider",
    "validate_image_capability",
    "validate_task_and_record_errors",
    "validate_task_id",
]

# Constants
SECONDS_PER_TOOL_CALL = 2.3
_CONTINUATION_TAIL_CHARS = 8000
_CONTINUATION_STDERR_CHARS = 2000
_CONTINUATION_MULTI_HOP_TOTAL_CAP = 12000
_LOG_FOLLOW_POLL_SECONDS = 0.5
_SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

from pathlib import Path
_MODEL_INDEXES_PATH = Path(__file__).resolve().parents[2] / "agents" / "cliproxy_data" / "model_indices.json"

# Re-exports from input helpers
def normalize_image_paths(image_paths: list[str] | None) -> list[str]:
    return run_input_helpers.normalize_image_paths(image_paths, supported_image_suffixes=_SUPPORTED_IMAGE_SUFFIXES)

append_context_usage = run_input_helpers.append_context_usage

def model_supports_vision(model: str) -> bool:
    return run_input_helpers.model_supports_vision(model, model_indexes_path=_MODEL_INDEXES_PATH)

def validate_image_capability(agent: str, model: str | None) -> None:
    run_input_helpers.validate_image_capability(
        agent=agent,
        model=model,
        model_supports_vision_impl=model_supports_vision,
    )

resolve_agent_model = run_model_helpers.resolve_agent_model
validate_explicit_ollama_provider = run_model_helpers.validate_explicit_ollama_provider

# Re-exports from health helpers
hash_health_payload = run_health_helpers.hash_health_payload
health_snapshot_log_path = run_health_helpers.health_snapshot_log_path
health_snapshot_max_lines = run_health_helpers.health_snapshot_max_lines

def resolve_health_policy(policy_profile: str | None, strict: bool, min_healthy_ratio: float) -> dict:
    from thegent.cli.commands.observability_health_impl import HEALTH_POLICY_PROFILES
    return run_health_helpers.resolve_health_policy(
        policy_profile=policy_profile,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        health_policy_profiles=HEALTH_POLICY_PROFILES,
    )

def compact_health_snapshot_log() -> None:
    run_health_helpers.compact_health_snapshot_log(
        log_path_resolver=health_snapshot_log_path,
        max_lines_resolver=health_snapshot_max_lines,
    )

health_scope_key = run_health_helpers.health_scope_key
coerce_issue_types = run_health_helpers.coerce_issue_types

def load_previous_health_snapshot(scope_key: dict) -> dict | None:
    return run_health_helpers.load_previous_health_snapshot(scope_key, log_path_resolver=health_snapshot_log_path)

def append_health_snapshot(payload: dict, scope_key: dict) -> None:
    run_health_helpers.append_health_snapshot(
        payload,
        scope_key,
        log_path_resolver=health_snapshot_log_path,
        compact_log_fn=compact_health_snapshot_log,
        coerce_issue_types_fn=coerce_issue_types,
    )

# Re-exports from observe helpers
build_observe_summary_trend_scope = run_observe_helpers.build_observe_summary_trend_scope
hash_observe_summary_trend_scope = run_observe_helpers.hash_observe_summary_trend_scope
parse_observe_summary_timestamp = run_observe_helpers.parse_observe_summary_timestamp
parse_observe_summary_env_float = run_observe_helpers.parse_observe_summary_env_float
parse_observe_summary_env_int = run_observe_helpers.parse_observe_summary_env_int
observe_summary_freshness_bucket = run_observe_helpers.observe_summary_freshness_bucket

def hash_observe_summary_payload(payload: dict) -> dict[str, str]:
    return run_observe_helpers.hash_observe_summary_payload(payload)

def load_observe_summary_snapshots(scope_signature: str, scope_key_json: str, limit: int) -> list[dict]:
    run_observe_helpers.health_snapshot_log_path = health_snapshot_log_path
    return run_observe_helpers.load_observe_summary_snapshots(scope_signature, scope_key_json, limit)

classify_observe_summary_trend_health = run_observe_helpers.classify_observe_summary_trend_health
append_observe_summary_snapshot = run_observe_helpers.append_observe_summary_snapshot

# Re-exports from audio/event helpers
build_audio_summary_metadata = run_audio_helpers.build_audio_summary_metadata
build_run_event_details = run_event_helpers.build_run_event_details
resolve_audio_transcript_for_output = run_event_helpers.resolve_audio_transcript_for_output
resolve_grounding_sources_for_output = run_input_helpers.resolve_grounding_sources_for_output

# Re-exports from retry helpers
_EAGAIN_ERRNOS = spawn_retry_helpers.EAGAIN_ERRNOS
retry_if_eagain = spawn_retry_helpers.retry_if_eagain

def spawn_with_eagain_retry(cmd: list[str], *, cwd: str, env: dict[str, str], stdin, stdout, stderr):
    import subprocess
    from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random_exponential

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random_exponential(multiplier=0.1, min=0.1, max=5.0),
        retry=retry_if_exception(retry_if_eagain),
        reraise=True,
    )
    def _spawn():
        return subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
    return _spawn()

backoff_delay = retry_helpers.backoff_delay

# Re-exports from session helpers
resolve_droids_dir = run_session_helpers.resolve_droids_dir
resolve_cwd = run_session_helpers.resolve_cwd
CWD_CACHE = run_session_helpers._CWD_CACHE
scope_key = run_session_helpers.scope_key
default_owner_tag = run_session_helpers.default_owner_tag
compose_owner_tag = run_session_helpers.compose_owner_tag
session_dir = run_session_helpers.session_dir
session_scope_dirs = run_session_helpers.session_scope_dirs
session_paths = run_session_helpers.session_paths
new_session_id = run_session_helpers.new_session_id

def inject_time_constraint(prompt: str, timeout: int, *, summary_mode: bool = True) -> str:
    from thegent.cli.services import prompt_constraint_helpers
    return prompt_constraint_helpers.inject_time_constraint(
        prompt=prompt, timeout=timeout, seconds_per_tool_call=SECONDS_PER_TOOL_CALL, summary_mode=summary_mode
    )

# Process helpers
is_pid_running = process_helpers.is_pid_running

# DAG helpers
parse_dag_full = run_dag_helpers.parse_dag_full
serialize_dag = run_dag_helpers.serialize_dag
parse_dag_session = run_dag_helpers.parse_dag_session
validate_task_id = run_dag_helpers.validate_task_id
validate_agent = run_dag_helpers.validate_agent
validate_dag = run_dag_helpers.validate_dag
dag_update_task = run_dag_helpers.dag_update_task
parse_depends_on = run_dag_helpers.parse_depends_on
get_ready_task_ids = run_dag_helpers.get_ready_task_ids

# Work stream helpers
parse_work_stream_md = run_workstream_helpers.parse_work_stream_md
check_dependencies_satisfied = run_workstream_helpers.check_dependencies_satisfied
priority_sort_key = run_workstream_helpers.priority_sort_key
collect_work_stream_items = run_workstream_helpers.collect_work_stream_items
collect_queued_items = run_workstream_helpers.collect_queued_items

# Pre-work gate helpers
pre_work_gate_defaults = pre_work_gate_helpers.pre_work_gate_defaults
pre_work_gate_thresholds = pre_work_gate_helpers.pre_work_gate_thresholds
evidence_age_minutes = pre_work_gate_helpers.evidence_age_minutes
pre_work_governance_block_payload = pre_work_gate_helpers.pre_work_governance_block_payload
enforce_pre_work_hard_gate = pre_work_gate_helpers.enforce_pre_work_hard_gate

# Agent/provider helpers
def list_agent_names() -> list[str]:
    from thegent.agents import list_agent_names as base_list_agent_names
    return base_list_agent_names()

def resolve_agent(agent_name: str | None) -> str | None:
    from thegent.agents import resolve_agent as base_resolve_agent
    return base_resolve_agent(agent_name)

def get_fallback_agents():
    from thegent.agents import get_fallback_agents as _get_fallback_agents
    return _get_fallback_agents()

def apply_pareto_routing(agent, model, routing, include_contract, route_contract, route_request):
    from thegent.cli.commands.impl import _apply_pareto_routing
    return _apply_pareto_routing(agent, model, routing, include_contract, route_contract, route_request)

def update_teammate_status(task_id: str | None, status: str, summary: str | None = None) -> None:
    from thegent.cli.commands.impl import _update_teammate_status
    return _update_teammate_status(task_id, status, summary)

validate_task_and_record_errors = work_stream_orchestration._validate_task_and_record_errors
