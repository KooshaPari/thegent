"""Thegent CLI shared infrastructure - extracted from cli.py for domain submodules.

WL-124: Monolith Split shared helpers.
"""

from __future__ import annotations

import contextlib
import importlib
import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import typer

from thegent.cli.commands.output import health_export_writers
from thegent.cli.commands.output import health_serializers as health_output


def _get_run_subprocess_optimized():
    from thegent.infra import run_subprocess_optimized

    return run_subprocess_optimized


def _get_yaml_infra():
    from thegent.infra import yaml_dump, yaml_load

    return yaml_load, yaml_dump


class LazyConsole:
    """Lazy-loaded rich console to speed up CLI startup."""

    _real_console: Any | None = None

    def _resolve_target(self) -> Any:
        # Allow tests to patch `thegent.cli.console` and have all command modules honor it.
        cli_module = sys.modules.get("thegent.cli")
        if cli_module is not None:
            patched = getattr(cli_module, "console", None)
            if patched is not None and patched is not self:
                return patched
        if self._real_console is None:
            from rich.console import Console

            self._real_console = Console()
        return self._real_console

    def __getattr__(self, name: str) -> Any:
        return getattr(self._resolve_target(), name)


console = LazyConsole()


if TYPE_CHECKING:
    from collections.abc import Callable


# Lazy imports for thegent modules to speed up startup.
def _lazy_import(module: str, name: str) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        cli_module = sys.modules.get("thegent.cli")
        if cli_module is not None and hasattr(cli_module, name):
            patched = getattr(cli_module, name)
            if patched is not wrapper and patched is not globals().get(name):
                if callable(patched):
                    return patched(*args, **kwargs)
                return patched

        m = importlib.import_module(module)
        f = getattr(m, name)
        globals()[name] = f
        if callable(f):
            return f(*args, **kwargs)
        return f

    return wrapper


# thegent.agents
list_agent_names = _lazy_import("thegent.agents", "list_agent_names")
list_droid_names = _lazy_import("thegent.agents", "list_droid_names")
resolve_agent = _lazy_import("thegent.agents", "resolve_agent")
run_login = _lazy_import("thegent.agents.cliproxy_manager", "run_login")

# thegent.cli.commands.impl
_atomic_write = _lazy_import("thegent.cli.commands.impl", "_atomic_write")
_make_load_classifier = _lazy_import("thegent.cli.commands.impl", "_make_load_classifier")
_check_dag_cycles = _lazy_import("thegent.cli.commands.impl", "_check_dag_cycles")
_coerce_issue_types = _lazy_import("thegent.cli.commands.impl", "_coerce_issue_types")
_dag_path = _lazy_import("thegent.cli.commands.impl", "_dag_path")
_dag_update_task = _lazy_import("thegent.cli.commands.impl", "_dag_update_task")
_default_owner_tag = _lazy_import("thegent.cli.commands.impl", "_default_owner_tag")
_ensure_contract_version_header = _lazy_import("thegent.cli.commands.impl", "_ensure_contract_version_header")
_ensure_dag_file = _lazy_import("thegent.cli.commands.impl", "_ensure_dag_file")
_find_session_meta = _lazy_import("thegent.cli.commands.impl", "_find_session_meta")
_get_ready_task_ids = _lazy_import("thegent.cli.commands.impl", "_get_ready_task_ids")
_is_pid_running = _lazy_import("thegent.cli.commands.impl", "_is_pid_running")
_normalize_output_format = _lazy_import("thegent.cli.commands.impl", "_normalize_output_format")
_parse_dag_full = _lazy_import("thegent.cli.commands.impl", "_parse_dag_full")
_parse_dag_session = _lazy_import("thegent.cli.commands.impl", "_parse_dag_session")
_parse_depends_on = _lazy_import("thegent.cli.commands.impl", "_parse_depends_on")
_read_session_meta = _lazy_import("thegent.cli.commands.impl", "_read_session_meta")
_resolve_cwd = _lazy_import("thegent.cli.commands.impl", "_resolve_cwd")
_resolve_droids_dir = _lazy_import("thegent.cli.commands.impl", "_resolve_droids_dir")
_resolve_prompt = _lazy_import("thegent.cli.commands.impl", "_resolve_prompt")
_resolve_session_status = _lazy_import("thegent.cli.commands.impl", "_resolve_session_status")
_serialize_dag = _lazy_import("thegent.cli.commands.impl", "_serialize_dag")
_session_paths = _lazy_import("thegent.cli.commands.impl", "_session_paths")
_session_status_for = _lazy_import("thegent.cli.commands.impl", "_session_status_for")
_validate_agent = _lazy_import("thegent.cli.commands.impl", "_validate_agent")
_validate_dag = _lazy_import("thegent.cli.commands.impl", "_validate_dag")
_validate_task_id = _lazy_import("thegent.cli.commands.impl", "_validate_task_id")
dag_ready_impl = _lazy_import("thegent.cli.commands.impl", "dag_ready_impl")
dag_recover_impl = _lazy_import("thegent.cli.commands.impl", "dag_recover_impl")
dag_run_impl = _lazy_import("thegent.cli.commands.impl", "dag_run_impl")
dag_sync_impl = _lazy_import("thegent.cli.commands.impl", "dag_sync_impl")


# thegent.config & execution
ThegentSettings = _lazy_import("thegent.config", "ThegentSettings")
RunRegistry = _lazy_import("thegent.execution", "RunRegistry")


def get_exit_message(*args: Any, **kwargs: Any):
    from thegent.exit_codes import get_exit_message as impl

    return impl(*args, **kwargs)


# Constants
EXIT_TIMEOUT = 124
EXIT_HEALTH_GATE_FAILED = 2


def _safe_dict(val: object) -> dict[str, Any]:
    """Return val as dict[str, Any], or empty dict if not a dict."""
    return cast("dict[str, Any]", val) if isinstance(val, dict) else {}


def _safe_list(val: object) -> list[Any]:
    """Return val as list[Any], or empty list if not a list."""
    return cast("list[Any]", val) if isinstance(val, list) else []


def _resolve_run_id(run_id: str | None) -> str:
    """Resolve run_id, defaulting to latest if None."""
    if run_id:
        return run_id
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    latest = registry.get_latest_run_id()
    if not latest:
        console.print("[red]No run ID provided and no previous runs found.[/red]")
        raise typer.Exit(1)
    return latest


def _resolve_session_id(session_id: str | None) -> str:
    """Resolve session_id, defaulting to latest if None."""
    if session_id:
        return session_id
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    latest = registry.get_latest_session_id()
    if not latest:
        console.print("[red]No session ID provided and no previous sessions found.[/red]")
        raise typer.Exit(1)
    return latest


def _resolve_checkpoint_id(checkpoint_id: str | None) -> str:
    """Resolve checkpoint_id, defaulting to latest if None."""
    if checkpoint_id:
        return checkpoint_id
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    latest = registry.get_latest_checkpoint_id()
    if not latest:
        console.print("[red]No checkpoint ID provided and no previous checkpoints found.[/red]")
        raise typer.Exit(1)
    return latest


_LOG_FOLLOW_POLL_SECONDS = 0.5  # Poll interval for log follow (seconds)


def _format_context_usage_line(context_usage: object) -> str | None:
    """WL-108: render a compact context budget line for user-facing CLI output."""
    if not isinstance(context_usage, dict):
        return None
    used = context_usage.get("used")
    max_val = context_usage.get("max")

    if isinstance(used, int) and isinstance(max_val, int):
        from thegent.cli.services.run_input_helpers import build_context_usage_payload

        shared_payload = build_context_usage_payload(
            used=used,
            max_tokens=max_val,
            ratio=context_usage.get("ratio") if isinstance(context_usage.get("ratio"), (float, int)) else None,
        )
        if isinstance(shared_payload, dict):
            display = shared_payload.get("display")
            if isinstance(display, str) and display:
                return f"Context usage: {display}"

    display = context_usage.get("display")
    if not isinstance(display, str) or not display:
        return None
    return f"Context usage: {display}"


def _format_transcript_summary_line(audio_metadata: object) -> str | None:
    """WL-116: render transcript metadata in run summary output."""
    if not isinstance(audio_metadata, dict):
        return None
    length = audio_metadata.get("transcript_length_chars")
    source_count = audio_metadata.get("source_count")
    if not isinstance(length, int) or not isinstance(source_count, int):
        return None
    return f"Transcript input: {length} chars from {source_count} file(s)"


def _format_grounding_sources_lines(grounding_sources: object, *, max_rows: int = 3) -> list[str]:
    """WL-119: render grounding source URLs in human-facing output."""
    if not isinstance(grounding_sources, list):
        return []
    urls = [str(item) for item in grounding_sources if isinstance(item, str) and item]
    if not urls:
        return []
    lines = [f"Grounding sources ({len(urls)}):"]
    lines.extend(f"  - {url}" for url in urls[:max_rows])
    remaining = len(urls) - max_rows
    if remaining > 0:
        lines.append(f"  - ... and {remaining} more")
    return lines


def _scope_key(owner: str) -> str:
    """Stable filesystem-safe key for owner tags."""
    return "".join(c if (c.isalnum() or c in "-_.") else "_" for c in owner)


def _compose_owner_tag(user: str, cwd: Path, scope: str = "") -> str:
    """Build deterministic owner tags with optional scope expansion."""
    base_name = cwd.name
    normalized_scope = (
        os.path.expandvars(scope or "")
        .format(
            user=user,
            uid=os.getuid(),
            pid=os.getpid(),
            ppid=os.getppid(),
            cwd=base_name,
        )
        .strip()
    )
    if normalized_scope:
        return f"{user}:{base_name}:{normalized_scope}"
    return f"{user}:{base_name}"


def _inject_skill_instructions(prompt: str, skills: list[str] | None) -> str:
    """Inject selected skill instructions into the prompt payload."""
    if not skills:
        return prompt

    from thegent.skills.discovery import load_skill

    sections: list[str] = []
    for name in skills:
        skill = load_skill(name)
        if skill is None:
            console.print(f"[red]Skill not found: {name}[/red]")
            raise typer.Exit(1)
        content = str(skill.get("content", "")).strip()
        if not content:
            console.print(f"[red]Skill has no content: {name}[/red]")
            raise typer.Exit(1)
        sections.append(f"## Skill: {name}\n{content}")

    return f"{prompt}\n\n# Activated Skills\n\n" + "\n\n".join(sections)


def _get_health_targets_path(project_dir: Path) -> Path:
    """Find the health-targets.json path relative to project directory."""
    # Try project_dir/contracts/health-targets.json
    health_targets = project_dir / "contracts" / "health-targets.json"
    if health_targets.exists():
        return health_targets
    # Fallback: try current working directory
    cwd_health = Path.cwd() / "contracts" / "health-targets.json"
    if cwd_health.exists():
        return cwd_health
    # Default: raise error
    raise FileNotFoundError(f"health-targets.json not found. Expected at {health_targets} or {cwd_health}")


def _health_targets_exists(project_dir: Path) -> bool:
    """Return True if health-targets.json exists for the project."""
    for p in (project_dir / "contracts" / "health-targets.json", Path.cwd() / "contracts" / "health-targets.json"):
        if p.exists():
            return True
    return False


_HEALTH_TARGETS_TEMPLATE = """{"version":"1.0.0","dimensions":{"test_coverage":{"weight":0.2,"target":80,"unit":"percent","direction":"higher_is_better","scan_tool":"pytest --cov","priority_class":"critical"},"lint_violations":{"weight":0.15,"target":0,"unit":"count","direction":"lower_is_better","scan_tool":"ruff check","priority_class":"critical"},"complexity_index":{"weight":0.15,"target":10,"unit":"cyclomatic_avg","direction":"lower_is_better","scan_tool":"radon cc -a","priority_class":"medium"},"security_findings":{"weight":0.15,"target":0,"unit":"count","direction":"lower_is_better","scan_tool":"security-pipeline","priority_class":"critical"},"spec_traceability":{"weight":0.1,"target":80,"unit":"percent","direction":"higher_is_better","scan_tool":"grep FR- tests/","priority_class":"medium"},"doc_organization":{"weight":0.1,"target":100,"unit":"percent","direction":"higher_is_better","scan_tool":"structure_audit","priority_class":"low"},"freshness":{"weight":0.1,"target":0,"unit":"stale_items","direction":"lower_is_better","scan_tool":"find -mtime +7","priority_class":"low"},"agent_health":{"weight":0.05,"target":0,"unit":"open_breakers","direction":"lower_is_better","scan_tool":"circuit_breakers.jsonl","priority_class":"critical"}},"bands":{"excellent":{"min":90,"label":"Excellent"},"healthy":{"min":70,"label":"Healthy"},"warning":{"min":40,"label":"Warning"},"critical":{"min":0,"label":"Critical"}},"budget":{"daily_agent_calls":20,"tiers":{"normal":{"max_utilization_pct":50,"description":"All agent types available"},"cautious":{"max_utilization_pct":80,"description":"Prefer cheaper/faster agents"},"restricted":{"max_utilization_pct":95,"description":"Only essential tasks"},"halted":{"max_utilization_pct":100,"description":"No new agent spawns"}}},"cycle":{"interval_s":300,"max_rerolls_per_task":2,"max_tasks_per_cycle":10,"cooldown_after_failure_s":60,"health_threshold":90,"debounce_s":30}}"""
_METRIC_CONTRACTS_TEMPLATE = """{
  "version": "1.0",
  "enforcement": {
    "require_metrics_report": true,
    "metrics_report_path": ".claude/verification/quality-metrics.json",
    "fail_closed": true
  },
  "domains": {
    "quality": {
      "max_lint_errors": 0,
      "max_type_errors": 0,
      "min_test_pass_rate": 0.98
    },
    "security": {
      "max_critical_vulns": 0,
      "max_high_vulns": 0,
      "max_secrets_detected": 0
    },
    "reliability": {
      "max_flake_rate": 0.05,
      "min_pass_rate": 0.98
    },
    "extensibility": {
      "max_file_lines": 500,
      "max_function_lines": 80
    },
    "other": {
      "max_todo_markers": 0
    }
  }
}"""


def _bootstrap_metric_contracts(project_dir: Path, force: bool = False) -> tuple[bool, bool]:
    """Ensure metric contracts and quality.json metric gate config exist."""
    contracts_dir = project_dir / "contracts"
    contract_path = contracts_dir / "metric-contracts.json"
    quality_path = project_dir / ".claude" / "quality.json"

    created_contract = False
    updated_quality = False

    # Seed contracts/metric-contracts.json from template; fallback to built-in template string.
    if force or not contract_path.exists():
        contracts_dir.mkdir(parents=True, exist_ok=True)
        template_path = Path(__file__).resolve().parents[4] / "templates" / "quality" / "metric-contracts.json"
        if template_path.exists():
            contract_path.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            contract_path.write_text(_METRIC_CONTRACTS_TEMPLATE, encoding="utf-8")
        created_contract = True

    # Ensure .claude/quality.json has governance.metric_contracts.enforce_gate=true.
    quality_path.parent.mkdir(parents=True, exist_ok=True)
    quality_data: dict[str, Any]
    if quality_path.exists():
        try:
            raw = json.loads(quality_path.read_text(encoding="utf-8"))
            quality_data = raw if isinstance(raw, dict) else {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {quality_path}: {e}") from e
    else:
        quality_data = {}

    governance = quality_data.get("governance")
    if not isinstance(governance, dict):
        governance = {}
    metric_contracts = governance.get("metric_contracts")
    if not isinstance(metric_contracts, dict):
        metric_contracts = {}

    if metric_contracts.get("enforce_gate") is not True:
        metric_contracts["enforce_gate"] = True
        governance["metric_contracts"] = metric_contracts
        quality_data["governance"] = governance
        quality_path.write_text(json.dumps(quality_data, indent=2) + "\n", encoding="utf-8")
        updated_quality = True

    return created_contract, updated_quality


def _serialize_health_report_md(result: dict[str, Any]) -> str:
    return health_output.serialize_health_report_md(result)


def _serialize_health_report_csv(result: dict[str, Any]) -> str:
    return health_output.serialize_health_report_csv(result)


def _serialize_health_report_jsonl(result: dict[str, Any]) -> str:
    return health_output.serialize_health_report_jsonl(result)


def _serialize_health_gate_md(result: dict[str, Any]) -> str:
    return health_output.serialize_health_gate_md(result)


def _serialize_health_gate_csv(result: dict[str, Any]) -> str:
    return health_output.serialize_health_gate_csv(result)


def _serialize_health_gate_jsonl(result: dict[str, Any]) -> str:
    return health_output.serialize_health_gate_jsonl(result)


def _export_format_from_suffix(suffix: str) -> str | None:
    return health_output.export_format_from_suffix(suffix)


def _infer_export_format(path: Path, fallback: str = "json") -> str:
    return health_output.infer_export_format(path, fallback=fallback)


def _write_report_export(
    output: Path,
    report: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    return health_export_writers.write_report_export(
        output=output,
        report=report,
        export_format=export_format,
        overwrite=overwrite,
    )


def _write_health_gate_export(
    output: Path,
    report: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    return health_export_writers.write_health_gate_export(
        output=output,
        report=report,
        export_format=export_format,
        overwrite=overwrite,
    )


def _serialize_health_trend_md(result: dict[str, Any]) -> str:
    return health_output.serialize_health_trend_md(result)


def _serialize_health_trend_csv(result: dict[str, Any]) -> str:
    return health_output.serialize_health_trend_csv(result)


def _serialize_health_trend_jsonl(result: dict[str, Any]) -> str:
    return health_output.serialize_health_trend_jsonl(result)


def _write_health_trend_export(
    output: Path,
    result: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    return health_export_writers.write_health_trend_export(
        output=output,
        result=result,
        export_format=export_format,
        overwrite=overwrite,
        print_error=console.print,
    )


def _load_artifact(artifacts: list[Any], p: Path) -> None:
    """Load a single MAIF artifact safely."""
    with contextlib.suppress(Exception):
        artifacts.append(json.loads(p.read_text(encoding="utf-8")))


__all__ = [
    "EXIT_HEALTH_GATE_FAILED",
    "EXIT_TIMEOUT",
    "_LOG_FOLLOW_POLL_SECONDS",
    "LazyConsole",
    "_atomic_write",
    "_bootstrap_metric_contracts",
    "_check_dag_cycles",
    "_coerce_issue_types",
    "_compose_owner_tag",
    "_dag_path",
    "_dag_update_task",
    "_default_owner_tag",
    "_ensure_contract_version_header",
    "_ensure_dag_file",
    "_export_format_from_suffix",
    "_find_session_meta",
    "_format_context_usage_line",
    "_format_grounding_sources_lines",
    "_format_transcript_summary_line",
    "_get_health_targets_path",
    "_get_ready_task_ids",
    "_get_run_subprocess_optimized",
    "_get_yaml_infra",
    "_health_targets_exists",
    "_infer_export_format",
    "_inject_skill_instructions",
    "_is_pid_running",
    "_lazy_import",
    "_load_artifact",
    "_make_load_classifier",
    "_normalize_output_format",
    "_parse_dag_full",
    "_parse_dag_session",
    "_parse_depends_on",
    "_read_session_meta",
    "_resolve_checkpoint_id",
    "_resolve_cwd",
    "_resolve_droids_dir",
    "_resolve_prompt",
    "_resolve_run_id",
    "_resolve_session_id",
    "_resolve_session_status",
    "_safe_dict",
    "_safe_list",
    "_scope_key",
    "_serialize_dag",
    "_serialize_health_gate_csv",
    "_serialize_health_gate_jsonl",
    "_serialize_health_gate_md",
    "_serialize_health_report_csv",
    "_serialize_health_report_jsonl",
    "_serialize_health_report_md",
    "_serialize_health_trend_csv",
    "_serialize_health_trend_jsonl",
    "_serialize_health_trend_md",
    "_session_paths",
    "_session_status_for",
    "_validate_agent",
    "_validate_dag",
    "_validate_task_id",
    "_write_health_gate_export",
    "_write_health_trend_export",
    "_write_report_export",
    "console",
    "get_exit_message",
]
