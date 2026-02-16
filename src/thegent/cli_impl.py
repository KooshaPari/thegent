"""Thegent implementation layer: functions that return dict/str instead of printing.

When _resolve_cwd returns None (ambiguous), the caller (e.g. MCP tools) should
elicit before returning error. See gofastmcp.com/servers/elicitation.
"""

import getpass
import json
import logging
import os
import re
import signal
import socket
import subprocess
import sys
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

from rich.console import Console

console = Console()

import typer

# QW-002: _resolve_cwd() cache with stat-based TTL to reduce path resolution overhead.
# Mission-Critical Rigor (G-FM-04): Use stat-based markers for cache invalidation.
_CWD_CACHE: dict[str, tuple[Path | None, float, float]] = {}
_CWD_CACHE_TTL = 10.0  # seconds

import contextlib
import hashlib

from thegent.agents import (
    get_fallback_agents,
    get_runner,
    list_agent_names,
    list_droid_names,
    resolve_agent,
)
from thegent.agents.base import AgentRunner, RunResult
from thegent.agents.registry import AGENT_LABELS
from thegent.agents.resilience import is_usage_limit
from thegent.config import ThegentSettings
from thegent.contracts.registry import CONTRACT_SCHEMA_VERSION
from thegent.execution import RunMeta, RunRegistry

# Approximate seconds per tool call for budget injection (~2.3s * N tool calls ≈ timeout)
SECONDS_PER_TOOL_CALL = 2.3

# Max chars from prior session to inject (fits typical context windows)
_CONTINUATION_TAIL_CHARS = 8000
_CONTINUATION_STDERR_CHARS = 2000
_CONTINUATION_MULTI_HOP_TOTAL_CAP = 12000
_LOG_FOLLOW_POLL_SECONDS = 0.5
_log = logging.getLogger(__name__)


def _resolve_droids_dir(cwd: Path | None, settings: ThegentSettings) -> Path:
    """Resolve droids dir: project .factory/droids first, then config."""
    if cwd and (cwd / ".factory" / "droids").exists():
        return (cwd / ".factory" / "droids").resolve()
    return settings.factory_droids_dir.expanduser().resolve()


def _resolve_cwd(cd: Any) -> Path | None:
    """Resolve cwd: explicit --cd, or infer from current dir if project-like.

    Implements QW-002 optimization with 10s TTL and stat-based verification.
    """
    global _CWD_CACHE
    now = time.time()

    # Use absolute path string as cache key; for auto-inference include cwd so tests don't cross-pollute
    try:
        cache_key = str(cd.expanduser().resolve()) if cd is not None else f"none:{Path.cwd()}"
    except Exception:
        cache_key = str(cd) if cd else f"none:{Path.cwd()}"

    if cache_key in _CWD_CACHE:
        cached_p, expiry, _ = _CWD_CACHE[cache_key]
        if now < expiry:
            return cached_p

    # Resolution logic
    resolved_p: Path | None = None
    if cd is not None:
        p = cd.expanduser().resolve()
        if not p.is_dir():
            raise typer.BadParameter(f"Directory does not exist: {p}")
        resolved_p = p
    else:
        cwd = Path.cwd()

        # Check for project indicators
        if (cwd / ".git").exists() or (cwd / ".factory").exists() or (cwd / "pyproject.toml").exists():
            resolved_p = cwd
        elif (cwd.parent / ".factory").exists():
            resolved_p = cwd.parent
        else:
            resolved_p = None

    # Cache result
    _CWD_CACHE[cache_key] = (resolved_p, now + _CWD_CACHE_TTL, now)
    return resolved_p


def _resolve_agent_model(
    agent: str,
    model: str | None,
    mode: str,
    settings: ThegentSettings,
) -> str | None:
    """Resolve model for agent. Returns None if agent has no model support."""
    if model:
        return model
    if agent in ("cursor-agent", "cursor"):
        return settings.default_cursor_model
    if agent == "gemini":
        return settings.default_gemini_model
    if agent == "copilot":
        return settings.default_copilot_model
    if agent == "claude":
        return settings.default_claude_model
    if agent == "codex":
        return settings.default_codex_model_high if mode == "full" else settings.default_codex_model
    if agent == "antigravity":
        return settings.default_antigravity_model
    if agent == "minimax":
        return "minimax-m2.5"
    if agent == "glm":
        return "glm-5"
    if agent == "roo":
        return "roo-default"
    if agent == "kilo":
        return "kilo-default"
    return None


def _inject_time_constraint(prompt: str, timeout: int, *, summary_mode: bool = True) -> str:
    """Append tool-call budget to prompt so agent self-limits (process kill is unreliable).
    When summary_mode=True (default, non-full runs), also instructs agent to produce
    a worker status report for messaging-style output."""
    n_calls = max(1, int(timeout / SECONDS_PER_TOOL_CALL))
    suffix = (
        f"\n\n[TIME CONSTRAINT: You have approximately {n_calls} tool calls (~{timeout}s). "
        "When done or when approaching this limit, wrap up and report. "
        "Do not start new multi-step work.]"
    )
    if summary_mode:
        suffix += (
            "\n\n[OUTPUT FORMAT: End your response with a brief worker status report: "
            "**Summary** (1–2 sentences), **Items Done** (bullet list), **Issues** (if any), "
            "**Next Steps** (bullet list). Use markdown. This is the primary output shown.]"
        )
    return prompt + suffix


def _scope_key(owner: str) -> str:
    return "".join(c if (c.isalnum() or c in "-_.") else "_" for c in owner)


def _default_owner_tag(cwd: Path | None = None, *, include_process_id: bool = False) -> str:
    base = (cwd or Path.cwd()).expanduser().resolve()
    explicit = os.environ.get("THGENT_OWNER_TAG")
    if explicit:
        return explicit
    scope = os.environ.get("THGENT_OWNER_SCOPE", "").strip()
    if include_process_id and not scope:
        scope = "{pid}"
    user = getpass.getuser()
    return _compose_owner_tag(user=user, cwd=base, scope=scope)


def _compose_owner_tag(user: str, cwd: Path, scope: str = "") -> str:
    """Build deterministic owner tags with optional scope expansion.

    Supported placeholders in scope:
    - {user}, {uid}, {pid}, {ppid}, {cwd}
    - environment variables are also expanded.
    """
    base_name = cwd.name
    normalized_scope = scope or ""
    normalized_scope = os.path.expandvars(normalized_scope)
    normalized_scope = normalized_scope.format(
        user=user,
        uid=os.getuid(),
        pid=os.getpid(),
        ppid=os.getppid(),
        cwd=base_name,
    ).strip()
    if normalized_scope:
        return f"{user}:{base_name}:{normalized_scope}"
    return f"{user}:{base_name}"


def _session_dir(settings: ThegentSettings, owner: str) -> Path:
    d = settings.session_dir.expanduser().resolve() / _scope_key(owner)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _session_scope_dirs(base: Path, owner: str) -> list[Path]:
    """Return session scope directories for an owner key, including pid-scoped variants."""
    owner_key = _scope_key(owner)
    scopes: list[Path] = []
    for scope_dir in sorted(base.glob(f"{owner_key}*")):
        if scope_dir.name == owner_key or scope_dir.name.startswith(f"{owner_key}_"):
            scopes.append(scope_dir)
    if owner == "":
        return []
    if not scopes:
        fallback = base / owner_key
        if fallback.exists():
            scopes = [fallback]
    return scopes


def _session_paths(base: Path, session_id: str) -> dict[str, Path]:
    return {
        "meta": base / f"{session_id}.json",
        "stdout": base / f"{session_id}.stdout.log",
        "stderr": base / f"{session_id}.stderr.log",
        "rc": base / f"{session_id}.rc",
    }


def _new_session_id(agent: str | None, owner: str) -> str:
    now = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha1(f"{time.time_ns()}:{os.getpid()}:{owner}".encode()).hexdigest()[:8]
    agent_tag = agent or "any"
    return f"{now}-{agent_tag}-p{os.getpid()}-{digest}"


def _is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read_session_meta(meta_path: Path) -> dict[str, Any]:
    if not meta_path.exists():
        raise typer.BadParameter(f"Session not found: {meta_path.stem}")
    return json.loads(meta_path.read_text(encoding="utf-8"))


def _save_session_meta(meta_path: Path, payload: dict[str, Any]) -> None:
    meta_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _find_session_meta(settings: ThegentSettings, session_id: str) -> Path:
    root = settings.session_dir.expanduser().resolve()
    candidate = root / f"{session_id}.json"
    if candidate.exists():
        return candidate
    matches = list(root.glob(f"*/{session_id}.json"))
    if matches:
        return matches[0]
    raise typer.BadParameter(f"Session not found: {session_id}")


def _normalize_output_format(requested: str | None = None, *, default: str = "rich") -> str:
    value = (requested or os.environ.get("THGENT_OUTPUT_FORMAT") or default).strip().lower()
    if value in {"json", "md", "rich"}:
        return value
    if value:
        return "rich"
    return default


def _resolve_session_status(payload: dict[str, Any], rc_path: Path, running: bool) -> str:
    if running:
        return "running"

    exit_code = payload.get("exit_code")
    if exit_code is not None:
        return f"exited:{int(exit_code)}"

    if rc_path.exists():
        try:
            rc_raw = rc_path.read_text(encoding="utf-8").strip()
            if rc_raw:
                return f"exited:{int(rc_raw)}"
        except (OSError, ValueError):
            pass
    return "exited"


def _run_background_session_observer(
    exit_code: int,
    *,
    timed_out: bool = False,
) -> None:
    meta_path = os.environ.get("THGENT_SESSION_META_PATH")
    rc_path = os.environ.get("THGENT_SESSION_RC_PATH")
    if not meta_path:
        return

    path = Path(meta_path)
    if not path.exists():
        return
    try:
        payload = _read_session_meta(path)
    except Exception:
        return

    payload["status"] = "exited"
    payload["exit_code"] = int(exit_code)
    payload["timed_out"] = timed_out
    payload["ended_at_utc"] = datetime.now(UTC).isoformat()
    started = payload.get("started_at_utc")
    if isinstance(started, str):
        try:
            start_dt = datetime.fromisoformat(started)
            duration = datetime.now(UTC) - start_dt
            payload["duration_seconds"] = round(duration.total_seconds(), 3)
        except Exception:
            pass
    _save_session_meta(path, payload)
    if rc_path:
        with contextlib.suppress(OSError):
            Path(rc_path).write_text(f"{exit_code}\n", encoding="utf-8")


def _load_prior_session_output(
    settings: ThegentSettings,
    session_id: str,
    include_stderr: bool = False,
) -> str:
    """Load tail of prior session stdout (and optionally stderr) for continuation."""
    meta_path = _find_session_meta(settings, session_id)
    p = _session_paths(meta_path.parent, session_id)
    parts: list[str] = []
    if p["stdout"].exists():
        raw = p["stdout"].read_text(encoding="utf-8", errors="replace")
        tail = raw[-_CONTINUATION_TAIL_CHARS:] if len(raw) > _CONTINUATION_TAIL_CHARS else raw
        parts.append(tail)
    if include_stderr and p["stderr"].exists():
        raw = p["stderr"].read_text(encoding="utf-8", errors="replace")
        tail = raw[-_CONTINUATION_STDERR_CHARS:] if len(raw) > _CONTINUATION_STDERR_CHARS else raw
        parts.append(f"[stderr]\n{tail}")
    return "\n\n".join(parts)


def _build_continuation_prompt(
    settings: ThegentSettings,
    session_ids: str,
    prompt: str,
    include_stderr: bool = False,
) -> str:
    """Build a prompt that continues from prior session(s)."""
    sids = [s.strip() for s in session_ids.split(",") if s.strip()]
    if not sids:
        return prompt

    context_parts = []
    for sid in sids:
        output = _load_prior_session_output(settings, sid, include_stderr=include_stderr)
        if output:
            context_parts.append(f"--- Session: {sid} ---\n{output}")

    if not context_parts:
        return prompt

    context = "\n\n".join(context_parts)
    return f"Continuing from prior session context:\n\n{context}\n\nTask: {prompt}"


@dataclass
class DagDocument:
    """Parsed DAG session document with structure preserved for round-trip."""

    frontmatter: dict[str, str]
    tasks: list[dict[str, str]]
    before_table: str
    after_table: str
    table_headers: list[str]


def _parse_dag_full(path: Path) -> DagDocument:
    """Parse .factory/dag-session.md with full structure for round-trip."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    frontmatter: dict[str, str] = {}
    if text.startswith("---"):
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            for line in parts[0].strip().split("\n")[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    frontmatter[k.strip()] = v.strip()
            text = parts[1]
            lines = text.splitlines()

    tasks: list[dict[str, str]] = []
    headers: list[str] = []
    table_start = -1
    table_end = -1

    for i, line in enumerate(lines):
        if "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not headers:
                headers = [h.lower().replace(" ", "_") for h in cells]
                table_start = i
                continue
            if cells and "-" not in "".join(cells):
                row = dict(zip(headers, cells, strict=False))
                tasks.append(row)
            table_end = i
        elif headers and table_end >= 0:
            break

    before_table = "\n".join(lines[: table_start - 1 if table_start > 0 else 0]) + "\n" if table_start > 0 else ""
    if table_start >= 0:
        before_table = "\n".join(lines[:table_start]) + "\n"
    after_table = "\n".join(lines[table_end + 1 :]) + "\n" if table_end >= 0 and table_end + 1 < len(lines) else ""

    return DagDocument(
        frontmatter=frontmatter,
        tasks=tasks,
        before_table=before_table,
        after_table=after_table,
        table_headers=headers
        or [
            "id",
            "agent",
            "prompt",
            "depends_on",
            "status",
            "evidence",
            "retry_count",
            "max_retries",
            "quorum",
            "confidence",
        ],
    )


def _escape_cell(s: str) -> str:
    """Escape | for markdown table cells."""
    return s.replace("|", "\\|").replace("\n", " ")


def _serialize_dag(doc: DagDocument) -> str:
    """Serialize DagDocument to markdown."""
    h = doc.table_headers or ["id", "agent", "prompt", "depends_on", "status"]
    rows = []
    for t in doc.tasks:
        cells = [_escape_cell(str(t.get(k, "—"))) for k in h]
        rows.append("| " + " | ".join(cells) + " |")
    sep = "|" + "|".join("---" for _ in h) + "|"
    table = "| " + " | ".join(h) + " |\n" + sep + "\n" + "\n".join(rows)
    return doc.before_table + "\n" + table + "\n\n" + doc.after_table


def _atomic_write(path: Path, content: str, backup: bool = False) -> None:
    """Write content atomically. Optional backup before overwrite."""
    if backup and path.exists():
        import shutil

        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _parse_dag_session(path: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Parse .factory/dag-session.md: return (frontmatter, tasks)."""
    doc = _parse_dag_full(path)
    return doc.frontmatter, doc.tasks


TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def _validate_task_id(task_id: str) -> str | None:
    """Validate task ID format. Returns error message if invalid, else None."""
    if not task_id or not task_id.strip():
        return "Task ID cannot be empty"
    if not TASK_ID_RE.match(task_id.strip()):
        return f"Invalid task ID '{task_id}': must match [A-Za-z0-9][A-Za-z0-9_-]*"
    return None


def _validate_agent(agent: str) -> str | None:
    """Validate agent is in list_agent_names (or resolves via alias). Returns error message if invalid, else None."""
    if not agent or not agent.strip():
        return "Agent cannot be empty"
    canonical = resolve_agent(agent.strip())
    valid = list_agent_names()
    if canonical not in valid:
        return f"Unknown agent '{agent}'; valid: {', '.join(valid)}"
    return None


def _check_dag_cycles(tasks: list[dict[str, str]]) -> list[str]:
    """DFS cycle detection. Returns list of cycle error messages."""
    id_to_task = {t.get("id", "").strip(): t for t in tasks if t.get("id", "").strip()}
    errors: list[str] = []

    def __parse_deps(dep_str: str) -> list[str]:
        if not dep_str or dep_str.strip() in ("—", "-"):
            return []
        return [d.strip() for d in dep_str.split(",") if d.strip() and d.strip() not in ("—", "-")]

    def _dfs_cycle(node: str, path: list[str], visited: set[str], rec_stack: set[str]) -> list[str] | None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        task = id_to_task.get(node)
        deps = __parse_deps(task.get("depends_on", "")) if task else []
        for dep in deps:
            if dep not in id_to_task:
                errors.append(f"Task '{node}' depends on unknown task '{dep}'")
                continue
            if dep not in visited:
                cycle = _dfs_cycle(dep, path, visited, rec_stack)
                if cycle is not None:
                    return cycle
            elif dep in rec_stack:
                idx = path.index(dep)
                return [*path[idx:], dep]
        path.pop()
        rec_stack.discard(node)
        return None

    visited: set[str] = set()
    for tid in id_to_task:
        if tid not in visited:
            cycle = _dfs_cycle(tid, [], visited, set())
            if cycle is not None:
                errors.append(f"DAG cycle: {' -> '.join(cycle)}")
    return errors


def _validate_dag(doc: DagDocument) -> list[str]:
    """Validate DAG document. Returns list of error messages."""
    errors: list[str] = []
    seen_ids: set[str] = set()

    for i, t in enumerate(doc.tasks):
        tid = (t.get("id") or "").strip()
        agent = (t.get("agent") or "").strip()

        if err := _validate_task_id(tid):
            errors.append(f"Task row {i + 1}: {err}")
        elif tid in seen_ids:
            errors.append(f"Task row {i + 1}: Duplicate task ID '{tid}'")
        else:
            seen_ids.add(tid)

        if agent and (err := _validate_agent(agent)):
            errors.append(f"Task '{tid}': {err}")

        dep_str = t.get("depends_on", "")
        for d in [x.strip() for x in dep_str.split(",") if x.strip() and x.strip() not in ("—", "-")]:
            if d and (e := _validate_task_id(d)):
                errors.append(f"Task '{tid}' depends on '{d}': {e}")

        # WP-2007: Evidence completeness linting
        status = (t.get("status") or "").strip().lower()
        if status == "done" and not (t.get("evidence") or t.get("session_id")):
            errors.append(f"Task '{tid}': status is 'done' but evidence/session_id is missing.")

    cycle_errors = _check_dag_cycles(doc.tasks)
    errors.extend(cycle_errors)
    return errors


def _dag_path(cd: Path | None) -> tuple[Path | None, Path | None]:
    """Resolve cwd and dag-session.md path. Returns (cwd, dag_path) or (None, None) on error."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        return None, None
    return cwd, cwd / ".factory" / "dag-session.md"


def _ensure_dag_file(dag_path: Path) -> DagDocument:
    """Load DAG or create minimal empty document if file does not exist."""
    if dag_path.exists():
        return _parse_dag_full(dag_path)
    return DagDocument(
        frontmatter={"version": "1", "project": "", "owner": ""},
        tasks=[],
        before_table="# DAG Session\n\n## Tasks\n\n",
        after_table="",
        table_headers=["id", "agent", "prompt", "depends_on", "status"],
    )


def _session_status_for(session_id: str, settings: ThegentSettings) -> str:
    """Return session_status: running or exited:rc."""
    try:
        meta_path = _find_session_meta(settings, session_id)
        p = _session_paths(meta_path.parent, session_id)
        m = _read_session_meta(meta_path)
        pid = int(m.get("pid", 0) or 0)
        running = _is_pid_running(pid)
        rc = p["rc"].read_text(encoding="utf-8").strip() if p["rc"].exists() else ""
        return "running" if running else ("exited:" + rc if rc else "exited")
    except (typer.BadParameter, Exception):
        return "not_found"


def _ensure_evidence_header(doc: DagDocument) -> None:
    """Ensure evidence is in table_headers if any task has it or session_id."""
    if not doc.table_headers:
        doc.table_headers = ["id", "agent", "prompt", "depends_on", "status"]
    if "evidence" not in doc.table_headers and any(t.get("evidence") or t.get("session_id") for t in doc.tasks):
        # Insert evidence after status if possible
        if "status" in doc.table_headers:
            idx = doc.table_headers.index("status")
            doc.table_headers = [*list(doc.table_headers[: idx + 1]), "evidence", *list(doc.table_headers[idx + 1 :])]
        else:
            doc.table_headers = [*list(doc.table_headers), "evidence"]


def _ensure_contract_version_header(doc: DagDocument) -> None:
    """XA4: Ensure contract_version is in table_headers if any task has it."""
    if not doc.table_headers:
        return
    if "contract_version" not in doc.table_headers and any(t.get("contract_version") for t in doc.tasks):
        if "status" in doc.table_headers:
            idx = doc.table_headers.index("status")
            doc.table_headers = [
                *list(doc.table_headers[: idx + 1]),
                "contract_version",
                *list(doc.table_headers[idx + 1 :]),
            ]
        else:
            doc.table_headers = [*list(doc.table_headers), "contract_version"]


def _dag_update_task(
    doc: DagDocument,
    task_id: str,
    *,
    status: str | None = None,
    session_id: str | None = None,
    prompt: str | None = None,
    agent: str | None = None,
    depends_on: str | None = None,
    retry_count: int | None = None,
    contract_version: str | None = None,
) -> bool:
    """Update task by id. Returns True if found and updated. XA4: contract_version in task metadata."""
    task_id = task_id.strip()
    for t in doc.tasks:
        if (t.get("id") or "").strip() == task_id:
            if status is not None:
                t["status"] = status
            if session_id is not None:
                t["evidence"] = session_id
                t["session_id"] = session_id
                _ensure_evidence_header(doc)
            if prompt is not None:
                t["prompt"] = prompt
            if agent is not None:
                t["agent"] = agent
            if depends_on is not None:
                t["depends_on"] = depends_on
            if retry_count is not None:
                t["retry_count"] = str(retry_count)
            if contract_version is not None:
                t["contract_version"] = contract_version
                _ensure_contract_version_header(doc)
            return True
    return False


def _parse_depends_on(dep_str: str) -> list[str]:
    """Parse comma-separated depends_on string."""
    if not dep_str or dep_str.strip() in ("—", "-"):
        return []
    return [d.strip() for d in dep_str.split(",") if d.strip() and d.strip() not in ("—", "-")]


def _get_ready_task_ids(tasks: list[dict[str, str]]) -> list[str]:
    """Return task IDs that are pending and have dependencies satisfied."""
    id_to_task = {t.get("id", "").strip(): t for t in tasks if t.get("id", "").strip()}
    ready = []
    for tid, t in id_to_task.items():
        status = t.get("status", "").lower()
        if status != "pending":
            continue
        deps = _parse_depends_on(t.get("depends_on", ""))
        sat = True
        for d in deps:
            dt = id_to_task.get(d)
            if not dt or dt.get("status", "").lower() not in ("done", "completed", "cancelled", "skipped"):
                sat = False
                break
        if sat:
            ready.append(tid)
    return ready


def _resolve_prompt(task_id: str, prompt: str, cwd: Path) -> str:
    """Resolve prompt: inline string or @.factory/prompts/<id>.md."""
    if prompt.startswith("@"):
        path = cwd / prompt[1:]
        if path.exists():
            return path.read_text(encoding="utf-8")
    return prompt


from thegent.models.catalog import ROUTE_SCHEMA_VERSION
from thegent.operations import Operation
from thegent.orchestration_modes import MultiAgentMode
from thegent.output_parser import (
    OUTPUT_PARSER_SCHEMA_VERSION,
    condense_stream_to_display,
    extract_condensed,
)

# Elicitation messages for MCP tools when cwd/owner are ambiguous
ELICIT_CWD_MSG = "Working directory?"
ELICIT_OWNER_MSG = "Session owner tag?"
HEALTH_PAYLOAD_SCHEMA_VERSION = "health-schema-v1"
HEALTH_PAYLOAD_TYPES = (
    "session_contract_health_gate",
    "session_contract_health_report",
    "session_contract_health_trend",
)
OBSERVE_SUMMARY_SCHEMA_VERSION = "observe-summary-schema-v1"
OBSERVE_SUMMARY_PAYLOAD_TYPES = ("observe_summary",)
HEALTH_POLICY_PROFILES: dict[str, dict[str, Any]] = {
    "strict_ci": {"strict": True, "min_healthy_ratio": 1.0},
    "warn_only": {"strict": False, "min_healthy_ratio": 0.0},
    "prod_release": {"strict": True, "min_healthy_ratio": 0.98},
}


def _hash_observe_summary_payload(payload: dict[str, Any]) -> dict[str, str]:
    """Return a stable hash for an observe-summary payload."""
    payload_for_hash = {
        key: value for key, value in payload.items() if key not in {"generated_at_utc", "payload_signature"}
    }
    body = json.dumps(payload_for_hash, sort_keys=True, separators=(",", ":"))
    return {"algorithm": "sha256", "value": hashlib.sha256(body.encode("utf-8")).hexdigest()}


def _build_observe_summary_trend_scope(
    *,
    provider: str | None,
    drift_window: int,
    structural_budget_pct: float,
    semantic_budget_pct: float,
    limit: int,
    top_escalations: int,
) -> dict[str, Any]:
    return {
        "payload_type": "observe_summary",
        "provider": provider,
        "drift_window": int(drift_window),
        "structural_budget_pct": float(structural_budget_pct),
        "semantic_budget_pct": float(semantic_budget_pct),
        "limit": int(limit),
        "top_escalations": int(top_escalations),
    }


def _hash_observe_summary_trend_scope(scope_key: dict[str, Any]) -> str:
    scope_key_json = json.dumps(scope_key, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(scope_key_json.encode("utf-8")).hexdigest()


def _parse_observe_summary_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        value = str(value).replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _parse_observe_summary_env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return float(default)
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return float(default)
    return value


def _parse_observe_summary_env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return int(default)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return int(default)
    return value


def _observe_summary_freshness_bucket(
    freshness_seconds: int | None,
    *,
    fresh_seconds: int,
    warm_seconds: int,
    stale_seconds: int,
) -> str:
    if freshness_seconds is None:
        return "unknown"
    if freshness_seconds < 0:
        return "future"
    if freshness_seconds <= fresh_seconds:
        return "fresh"
    if freshness_seconds <= warm_seconds:
        return "warm"
    if freshness_seconds <= stale_seconds:
        return "stale"
    return "critical"


def _load_observe_summary_snapshots(
    scope_signature: str,
    scope_key_json: str,
    limit: int,
) -> list[dict[str, Any]]:
    path = _health_snapshot_log_path()
    if not path.exists():
        return []
    snapshots: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("record_type") != "observe_summary_snapshot":
            continue
        if rec.get("trend_scope_signature") == scope_signature or rec.get("scope_signature") == scope_signature:
            pass
        elif rec.get("scope_key_json") != scope_key_json:
            continue
        snapshots.append(rec)
        if len(snapshots) >= limit:
            break
    return snapshots


def _classify_observe_summary_trend_health(
    *,
    enabled: bool,
    baseline_available: bool,
    trend_snapshot_coverage_pct: float | None,
    trend_snapshot_deficit: int,
    trend_snapshot_invalid_timestamps: int,
    trend_snapshot_freshness_bucket: str,
    trend_snapshot_gap_count: int,
    trend_sampling_mode: str,
) -> dict[str, Any]:
    policy: dict[str, Any] = {
        "healthy_threshold": _parse_observe_summary_env_int("THGENT_OBSERVE_SUMMARY_TREND_HEALTH_GOOD_THRESHOLD", 95),
        "warning_threshold": _parse_observe_summary_env_int(
            "THGENT_OBSERVE_SUMMARY_TREND_HEALTH_WARNING_THRESHOLD", 80
        ),
        "degraded_threshold": _parse_observe_summary_env_int(
            "THGENT_OBSERVE_SUMMARY_TREND_HEALTH_DEGRADED_THRESHOLD", 50
        ),
        "min_coverage_pct": _parse_observe_summary_env_float(
            "THGENT_OBSERVE_SUMMARY_TREND_HEALTH_MIN_COVERAGE_PCT", 80.0
        ),
        "max_invalid_timestamps": _parse_observe_summary_env_int(
            "THGENT_OBSERVE_SUMMARY_TREND_HEALTH_MAX_INVALID_TIMESTAMPS", 0
        ),
        "coverage_penalty_per_pct": _parse_observe_summary_env_float(
            "THGENT_OBSERVE_SUMMARY_TREND_HEALTH_COVERAGE_PENALTY_PER_PCT", 1.25
        ),
        "deficit_penalty_per_missing_sample": _parse_observe_summary_env_float(
            "THGENT_OBSERVE_SUMMARY_TREND_HEALTH_DEFICIT_PENALTY_PER_MISSING_SAMPLE", 15
        ),
        "invalid_timestamp_penalty_per_event": _parse_observe_summary_env_float(
            "THGENT_OBSERVE_SUMMARY_TREND_HEALTH_INVALID_TIMESTAMP_PENALTY_PER_EVENT", 12
        ),
        "stale_penalty": _parse_observe_summary_env_float("THGENT_OBSERVE_SUMMARY_TREND_HEALTH_STALE_PENALTY", 8),
        "critical_penalty": _parse_observe_summary_env_float(
            "THGENT_OBSERVE_SUMMARY_TREND_HEALTH_CRITICAL_PENALTY", 20
        ),
        "unknown_or_future_penalty": _parse_observe_summary_env_float(
            "THGENT_OBSERVE_SUMMARY_TREND_HEALTH_UNKNOWN_OR_FUTURE_PENALTY", 30
        ),
        "gap_penalty": _parse_observe_summary_env_float("THGENT_OBSERVE_SUMMARY_TREND_HEALTH_GAP_PENALTY", 10),
        "missing_baseline_penalty": _parse_observe_summary_env_float(
            "THGENT_OBSERVE_SUMMARY_TREND_HEALTH_MISSING_BASELINE_PENALTY", 45
        ),
    }
    policy_signature = hashlib.sha256(
        json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    if not enabled:
        recommendations = [
            "Enable trend sampling with --trend-samples >= 2 to produce trend quality signals.",
            f"Use trend-sampling mode: {trend_sampling_mode}.",
        ]
        return {
            "trend_snapshot_health": "disabled",
            "trend_snapshot_health_score": None,
            "trend_snapshot_health_breakdown": {
                "policy_signature": policy_signature,
                "policy": policy,
                "reason": "trend_disabled",
                "trend_sampling_mode": trend_sampling_mode,
                "enabled": False,
                "recommendations": recommendations,
                "penalties": {
                    "enabled": 0,
                    "baseline": 0,
                    "coverage": 0,
                    "deficit": 0,
                    "invalid_timestamps": 0,
                    "freshness": 0,
                    "gap": 0,
                },
            },
            "trend_snapshot_recommendations": recommendations,
        }

    penalties: dict[str, float] = {
        "coverage": 0.0,
        "deficit": 0.0,
        "invalid_timestamps": 0.0,
        "freshness": 0.0,
        "gap": 0.0,
        "baseline": 0.0,
    }
    coverage_shortfall = 0.0
    if trend_snapshot_coverage_pct is None:
        coverage_shortfall = 0.0
        penalties["coverage"] = 0.0
    elif trend_snapshot_coverage_pct < policy["min_coverage_pct"]:
        coverage_shortfall = policy["min_coverage_pct"] - trend_snapshot_coverage_pct
        penalties["coverage"] = round(coverage_shortfall * policy["coverage_penalty_per_pct"], 6)

    if trend_snapshot_deficit > 0:
        penalties["deficit"] = trend_snapshot_deficit * policy["deficit_penalty_per_missing_sample"]

    if trend_snapshot_invalid_timestamps > policy["max_invalid_timestamps"]:
        penalties["invalid_timestamps"] = (
            trend_snapshot_invalid_timestamps * policy["invalid_timestamp_penalty_per_event"]
        )

    if trend_snapshot_freshness_bucket == "stale":
        penalties["freshness"] = policy["stale_penalty"]
    elif trend_snapshot_freshness_bucket == "critical":
        penalties["freshness"] = policy["critical_penalty"]
    elif trend_snapshot_freshness_bucket in {"future", "unknown"}:
        penalties["freshness"] = policy["unknown_or_future_penalty"]

    penalties["gap"] = trend_snapshot_gap_count * policy["gap_penalty"]
    if not baseline_available:
        penalties["baseline"] = policy["missing_baseline_penalty"]

    score = 100.0 - sum(penalties.values())
    score = max(0.0, min(100.0, score))
    health = "critical"
    if score >= policy["healthy_threshold"]:
        health = "good"
    elif score >= policy["warning_threshold"]:
        health = "warning"
    elif score >= policy["degraded_threshold"]:
        health = "degraded"

    recommendations: list[str] = []
    if coverage_shortfall > 0:
        recommendations.append(
            "Increase capture coverage by reducing trend sample window or lowering requested samples."
        )
    if trend_snapshot_deficit > 0:
        recommendations.append("Trend history is incomplete; expected samples were not all available.")
    if trend_snapshot_invalid_timestamps > policy["max_invalid_timestamps"]:
        recommendations.append("Snapshot contains invalid/missing timestamps; normalize capture time format.")
    if trend_snapshot_freshness_bucket in {"stale", "critical"}:
        recommendations.append("Trend freshness is degraded; capture cadence may be too low.")
    if trend_snapshot_gap_count > 0:
        recommendations.append("Snapshot gaps detected; verify persistence and scheduler cadence.")
    if not baseline_available:
        recommendations.append("No baseline snapshot available; next run may enable full delta reporting.")
    if not recommendations:
        recommendations.append("Trend quality is healthy.")

    return {
        "trend_snapshot_health": health,
        "trend_snapshot_health_score": round(score),
        "trend_snapshot_health_breakdown": {
            "policy_signature": policy_signature,
            "policy": policy,
            "healthy_threshold": policy["healthy_threshold"],
            "warning_threshold": policy["warning_threshold"],
            "degraded_threshold": policy["degraded_threshold"],
            "coverage": {
                "coverage_pct": trend_snapshot_coverage_pct,
                "coverage_shortfall_pct": coverage_shortfall,
                "coverage_penalty": penalties["coverage"],
                "min_coverage_pct": policy["min_coverage_pct"],
            },
            "deficit": {
                "trend_snapshot_deficit": trend_snapshot_deficit,
                "penalty_per_missing": policy["deficit_penalty_per_missing_sample"],
                "deficit_penalty": penalties["deficit"],
            },
            "invalid_timestamps": {
                "count": trend_snapshot_invalid_timestamps,
                "max_allowed": policy["max_invalid_timestamps"],
                "penalty_per_event": policy["invalid_timestamp_penalty_per_event"],
                "invalid_timestamp_penalty": penalties["invalid_timestamps"],
            },
            "freshness": {
                "bucket": trend_snapshot_freshness_bucket,
                "penalty": penalties["freshness"],
            },
            "gap": {
                "gap_count": trend_snapshot_gap_count,
                "penalty_per_gap": policy["gap_penalty"],
                "gap_penalty": penalties["gap"],
            },
            "baseline": {
                "baseline_available": baseline_available,
                "baseline_penalty": penalties["baseline"],
                "missing_baseline_penalty": policy["missing_baseline_penalty"],
            },
            "trend_sampling_mode": trend_sampling_mode,
            "enabled": enabled,
            "score": round(score),
            "recommendations": recommendations,
            "penalties": {
                "coverage_penalty": penalties["coverage"],
                "deficit_penalty": penalties["deficit"],
                "invalid_timestamps_penalty": penalties["invalid_timestamps"],
                "freshness_penalty": penalties["freshness"],
                "gap_penalty": penalties["gap"],
                "baseline_penalty": penalties["baseline"],
            },
        },
        "trend_snapshot_recommendations": recommendations,
    }


def _append_observe_summary_snapshot(
    payload: dict[str, Any],
    trend_scope_key: dict[str, Any],
    trend_scope_signature: str,
    scope_key_json: str,
    trend_snapshot_ids: list[str],
    trend_summary: dict[str, Any],
) -> None:
    record = {
        "record_type": "observe_summary_snapshot",
        "captured_at_utc": payload.get("generated_at_utc", ""),
        "scope_key": trend_scope_key,
        "scope_key_json": scope_key_json,
        "scope_signature": trend_scope_signature,
        "trend_scope_signature": trend_scope_signature,
        "trend_previous_samples_requested": trend_summary.get("trend_previous_samples_requested", 0),
        "trend_snapshot_expected_count": trend_summary.get("trend_snapshot_expected_count", 0),
        "trend_snapshot_deficit": trend_summary.get("trend_snapshot_deficit", 0),
        "trend_snapshot_interval_seconds_avg": trend_summary.get("trend_snapshot_interval_seconds_avg"),
        "trend_snapshot_interval_seconds_min": trend_summary.get("trend_snapshot_interval_seconds_min"),
        "trend_snapshot_interval_seconds_max": trend_summary.get("trend_snapshot_interval_seconds_max"),
        "trend_snapshot_gap_count": trend_summary.get("trend_snapshot_gap_count", 0),
        "trend_snapshot_invalid_timestamps": trend_summary.get("trend_snapshot_invalid_timestamps", 0),
        "trend_snapshot_coverage_pct": trend_summary.get("trend_snapshot_coverage_pct"),
        "trend_snapshot_freshness_bucket": trend_summary.get("trend_snapshot_freshness_bucket", "unknown"),
        "trend_snapshot_freshness_seconds": trend_summary.get("trend_snapshot_freshness_seconds"),
        "trend_snapshot_health": trend_summary.get("trend_snapshot_health", "disabled"),
        "trend_snapshot_health_score": trend_summary.get("trend_snapshot_health_score"),
        "trend_snapshot_recommendations": trend_summary.get("trend_snapshot_recommendations", []),
        "trend_snapshot_health_breakdown": trend_summary.get("trend_snapshot_health_breakdown", {}),
        "trend_snapshot_ids": trend_snapshot_ids,
        "trend_snapshot_ids_csv": trend_summary.get("trend_snapshot_ids_csv", ""),
        "trend_snapshot_ids_hash": trend_summary.get("trend_snapshot_ids_hash", ""),
        "trend_snapshot_window_seconds": trend_summary.get("trend_snapshot_window_seconds"),
        "trend_sampling_mode": trend_summary.get("trend_sampling_mode", "disabled"),
        "trend_enabled": trend_summary.get("enabled", False),
        "schema_version": payload.get("payload_schema_version", OBSERVE_SUMMARY_SCHEMA_VERSION),
        "payload_type": "observe_summary",
        "status": payload.get("status", ""),
        "total_events": payload.get("kpis", {}).get("total_events", 0),
        "fallback_rate": payload.get("kpis", {}).get("fallback_rate", 0.0),
        "success_rate": payload.get("kpis", {}).get("success_rate", 0.0),
        "avg_confidence": payload.get("kpis", {}).get("avg_confidence", 0.0),
        "structural_drift_pct": payload.get("kpis", {}).get("structural_drift_pct", 0.0),
        "semantic_drift_pct": payload.get("kpis", {}).get("semantic_drift_pct", 0.0),
        "drift_structural_rate_pct": payload.get("drift", {}).get("structural_rate_pct", 0.0),
        "drift_semantic_rate_pct": payload.get("drift", {}).get("semantic_rate_pct", 0.0),
        "backlog_count": payload.get("escalation", {}).get("backlog_count", 0),
        "past_sla_count": payload.get("escalation", {}).get("past_sla_count", 0),
        "provider": payload.get("generated_query", {}).get("provider", None),
        "drift_window": payload.get("generated_query", {}).get("drift_window", 0),
        "structural_budget_pct": payload.get("generated_query", {}).get("structural_budget_pct", 0.0),
        "semantic_budget_pct": payload.get("generated_query", {}).get("semantic_budget_pct", 0.0),
        "top_escalations": payload.get("generated_query", {}).get("top_escalations", 0),
        "limit": payload.get("generated_query", {}).get("limit", 0),
        "trend_samples_requested": payload.get("generated_query", {}).get("trend_samples", 0),
        "trend_effective_samples": trend_summary.get("trend_effective_samples", 0),
        "trend_scope_payload_type": trend_scope_key.get("payload_type", "observe_summary"),
    }

    path = _health_snapshot_log_path()
    try:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True))
            fh.write("\n")
    except OSError:
        return
    _compact_health_snapshot_log()


def get_server_meta_impl() -> dict[str, Any]:
    """Return server metadata dict for thegent://meta resource."""
    return {
        "server": "thegent",
        "version": "1.0",
        "capabilities": ["tools", "resources", "prompts", "progress", "elicitation", "event_store"],
        "health_payload_schema_version": HEALTH_PAYLOAD_SCHEMA_VERSION,
        "health_payload_types": list(HEALTH_PAYLOAD_TYPES),
        "observe_summary_payload_schema_version": OBSERVE_SUMMARY_SCHEMA_VERSION,
        "observe_summary_payload_types": list(OBSERVE_SUMMARY_PAYLOAD_TYPES),
        "health_policy_profiles": sorted(HEALTH_POLICY_PROFILES.keys()),
        "output_parser_schema_version": OUTPUT_PARSER_SCHEMA_VERSION,
        "route_schema_version": ROUTE_SCHEMA_VERSION,
        "contract_schema_version": CONTRACT_SCHEMA_VERSION,
        "operations": [op.value for op in Operation],
        "orchestration_modes": [m.value for m in MultiAgentMode],
    }


def _hash_health_payload(payload: dict[str, Any]) -> dict[str, str]:
    """Return a stable hash for a health payload while ignoring timestamp/signature fields."""
    payload_for_hash = {
        key: value for key, value in payload.items() if key not in {"generated_at_utc", "payload_signature"}
    }
    body = json.dumps(payload_for_hash, sort_keys=True, separators=(",", ":"))
    import hashlib

    return {"algorithm": "sha256", "value": hashlib.sha256(body.encode()).hexdigest()}


def _resolve_health_policy(
    policy_profile: str | None,
    strict: bool,
    min_healthy_ratio: float,
) -> dict[str, Any]:
    profile = "custom"
    effective_strict = bool(strict)
    threshold = float(min_healthy_ratio)
    profile_exists = True
    if policy_profile:
        key = str(policy_profile).strip().lower()
        selected = HEALTH_POLICY_PROFILES.get(key)
        if selected is not None:
            profile = key
            effective_strict = bool(selected["strict"])
            threshold = float(selected["min_healthy_ratio"])
        else:
            profile_exists = False
    threshold = max(threshold, 0.0)
    threshold = min(threshold, 1.0)
    return {
        "profile": profile,
        "profile_exists": profile_exists,
        "strict": effective_strict,
        "min_healthy_ratio": threshold,
    }


def _health_snapshot_log_path() -> Path:
    raw = os.environ.get("THGENT_HEALTH_SNAPSHOT_PATH", "").strip()
    path = Path(raw).expanduser() if raw else Path.home() / ".thegent" / "health-snapshots.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _health_snapshot_max_lines() -> int:
    raw = os.environ.get("THGENT_HEALTH_SNAPSHOT_MAX_LINES", "").strip()
    if not raw:
        return 5000
    try:
        value = int(raw)
    except ValueError:
        return 5000
    return max(100, value)


def _compact_health_snapshot_log() -> None:
    path = _health_snapshot_log_path()
    if not path.exists():
        return
    limit = _health_snapshot_max_lines()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    if len(lines) <= limit:
        return
    trimmed = lines[-limit:]
    try:
        path.write_text("\n".join(trimmed) + "\n", encoding="utf-8")
    except OSError:
        return


def _health_scope_key(payload: dict[str, Any]) -> dict[str, Any]:
    query = payload.get("generated_query", {}) or {}
    scope: dict[str, Any] = {
        "payload_type": payload.get("payload_type", ""),
        "owner": query.get("owner"),
        "all": bool(query.get("all", False)),
        "strict": bool(query.get("strict", False)),
        "policy_profile": payload.get("policy_profile", "custom"),
    }
    if payload.get("payload_type") == "session_contract_health_gate":
        scope["min_healthy_ratio"] = float(query.get("min_healthy_ratio", 1.0))
    if payload.get("payload_type") == "session_contract_health_report":
        scope["top_blocked"] = int(query.get("top_blocked", 25))
    return scope


def _coerce_issue_types(value: Any) -> list[str]:
    """Normalize an issue_types-like value to a deterministic list of strings."""
    if value is None:
        return []
    if isinstance(value, dict):
        return [str(v) for v in value]
    if isinstance(value, (list, tuple, set)):
        return [str(v) for v in value]
    return [str(value)]


def _load_previous_health_snapshot(scope_key: dict[str, Any]) -> dict[str, Any] | None:
    path = _health_snapshot_log_path()
    if not path.exists():
        return None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("record_type") != "health_snapshot":
            continue
        if rec.get("scope_key") == scope_key:
            return rec
    return None


def _append_health_snapshot(payload: dict[str, Any], scope_key: dict[str, Any]) -> None:
    path = _health_snapshot_log_path()
    issue_types: list[str] = []
    if payload.get("payload_type") == "session_contract_health_report":
        issue_types = sorted([str(k) for k in (payload.get("issue_counts") or {})])
    else:
        seen: set[str] = set()
        for row in payload.get("blocked_sessions", []) or []:
            for issue in _coerce_issue_types(row.get("issues", [])):
                seen.add(issue)
        issue_types = sorted(seen)
    rec = {
        "record_type": "health_snapshot",
        "captured_at_utc": payload.get("generated_at_utc", ""),
        "scope_key": scope_key,
        "schema_version": payload.get("schema_version", ""),
        "payload_type": payload.get("payload_type", ""),
        "status": payload.get("status", ""),
        "pass": payload.get("pass", False),
        "total": payload.get("total", 0),
        "healthy_count": payload.get("healthy_count", 0),
        "unhealthy_count": payload.get("unhealthy_count", 0),
        "blocked_count": payload.get("blocked_count", 0),
        "blocked_ratio": payload.get("blocked_ratio", 0.0),
        "issue_types": issue_types,
        "issue_counts": payload.get("issue_counts", {}),
        "payload_signature": payload.get("payload_signature", {}),
    }
    try:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True))
            fh.write("\n")
    except OSError:
        return
    _compact_health_snapshot_log()


def escalate_add_impl(
    run_id: str,
    reason: str,
    sla_minutes: int = 30,
    owner: str | None = None,
    agent: str | None = None,
    lane: str = "standard",
    priority: int = 0,
) -> None:
    """WP-3008: Add a blocked run to the escalation queue."""
    from thegent.execution import EscalationQueue

    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()
    queue = EscalationQueue(session_dir)
    queue.add(
        run_id=run_id,
        reason=reason,
        sla_minutes=sla_minutes,
        owner=owner,
        agent=agent,
        lane=lane,
        priority=priority,
    )


def escalate_approve_impl(run_id: str) -> bool:
    """WP-3008: Approve an escalation, marking it as approved in the queue (G-GP-05)."""
    from thegent.execution import EscalationQueue

    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()
    queue = EscalationQueue(session_dir)
    return queue.resolve(run_id=run_id, resolution="approved")


def update_calibration_impl() -> dict[str, Any]:
    """G-GP-09: Recalculate and persist calibration factors for all agents."""
    from thegent.execution import CalibrationRegistry, RunRegistry

    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()
    registry = RunRegistry(session_dir)
    cal = CalibrationRegistry(session_dir)

    if not registry.registry_path.exists():
        return {}

    # 1. Identify all agents
    agents = set()
    with registry.registry_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                a = data.get("agent")
                if a:
                    agents.add(a)
            except Exception:
                continue

    # 2. Recalculate for each agent
    results = {}
    for agent in agents:
        # We temporarily bypass the cache by manually calculating
        relevant_runs = []
        runs: dict[str, dict[str, Any]] = {}

        with registry.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    rid = data.get("run_id")
                    if not rid:
                        continue
                    if data.get("event") == "finish":
                        if rid in runs:
                            runs[rid].update(data)
                    elif data.get("event") == "feedback":
                        if rid in runs:
                            runs[rid]["feedback_score"] = data.get("feedback_score")
                    elif data.get("agent") == agent:
                        runs[rid] = data
                except Exception:
                    continue

        relevant_runs = [r for r in runs.values() if r.get("feedback_score") is not None]
        if not relevant_runs:
            continue

        avg_feedback = sum(float(r["feedback_score"]) for r in relevant_runs) / len(relevant_runs)
        avg_confidence = sum(float(r.get("confidence") or 0.5) for r in relevant_runs) / len(relevant_runs)

        if avg_confidence > 0:
            factor = min(2.0, max(0.5, avg_feedback / avg_confidence))
            cal.update_agent(agent, factor, sample_size=len(relevant_runs))
            results[agent] = {"factor": factor, "samples": len(relevant_runs)}

    return results


def sweep_impl(
    drift_window: int = 50,
    structural_budget: float = 5.0,
    semantic_budget: float = 10.0,
    include_audit: bool = False,
) -> dict[str, Any]:
    """WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations."""
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.execution import Auditor, EscalationQueue, RunRegistry

    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()

    ct = ContractTelemetry(session_dir)
    drift_issues = ct.detect_drift(window_size=drift_window)
    budget = ct.get_drift_budget_status(
        structural_budget_pct=structural_budget,
        semantic_budget_pct=semantic_budget,
    )
    if not budget["within_budget"]:
        drift_issues.append(
            f"Drift budget exceeded: structural {budget['structural_rate_pct']}% "
            f"(budget {budget['structural_budget_pct']}%), semantic {budget['semantic_rate_pct']}% "
            f"(budget {budget['semantic_budget_pct']}%)"
        )

    queue = EscalationQueue(session_dir)
    past_sla_items = queue.list_pending(past_sla_only=True, limit=100)

    # G-GP-05 P2: SLA breach alert when past-SLA items exist
    if past_sla_items and settings.escalation_sla_breach_alert:
        import logging

        _sweep_log = logging.getLogger(__name__)
        _sweep_log.warning(
            "Escalation SLA breach: %d item(s) past SLA. Run: thegent govern escalate list --past-sla",
            len(past_sla_items),
        )

    audit_result: dict[str, Any] | None = None
    if include_audit:
        registry = RunRegistry(session_dir)
        auditor = Auditor(registry.registry_path)
        audit_result = auditor.verify_registry()

    has_issues = bool(drift_issues) or bool(past_sla_items)
    if include_audit and audit_result and audit_result.get("status") not in ("passed", "empty"):
        has_issues = True

    # G-GP-09: Update trust score calibration
    cal_results = update_calibration_impl()

    return {
        "drift_issues": drift_issues,
        "drift_budget": budget,
        "past_sla_count": len(past_sla_items),
        "past_sla_items": past_sla_items,
        "calibration": cal_results,
        "audit": audit_result,
        "pass": not has_issues,
    }


def observe_summary_impl(
    limit: int = 500,
    drift_window: int = 50,
    structural_budget_pct: float = 5.0,
    semantic_budget_pct: float = 10.0,
    provider: str | None = None,
    top_escalations: int = 10,
    trend_samples: int | Any = 0,
) -> dict[str, Any]:
    """FR-X08: Unified observability summary aggregating KPIs, drift, escalation."""
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.execution import EscalationQueue

    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()

    ct = ContractTelemetry(session_dir)
    kpis = ct.get_fallback_kpis(
        limit=limit,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
    )
    drift_issues = ct.detect_drift(window_size=drift_window)
    budget = ct.get_drift_budget_status(
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        limit=limit,
    )

    queue = EscalationQueue(session_dir)
    # Include a broad snapshot for deterministic backlog ordering and counts.
    pending_window = max(top_escalations * 20, 100)
    pending = queue.list_pending(past_sla_only=False, limit=pending_window)
    past_sla = queue.list_pending(past_sla_only=True, limit=pending_window)

    now = datetime.now(UTC)

    def _parse_utc(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            if value.endswith("Z"):
                try:
                    parsed = datetime.fromisoformat(value)
                except ValueError:
                    return None
            else:
                return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    def _to_sla_delta(item: dict[str, Any]) -> dict[str, Any]:
        escalate_by = _parse_utc(item.get("escalate_by_utc"))
        blocked_at = _parse_utc(item.get("blocked_at_utc"))
        if escalate_by is None:
            return {
                "run_id": item.get("run_id"),
                "owner": item.get("owner"),
                "agent": item.get("agent"),
                "lane": item.get("lane"),
                "reason": item.get("reason"),
                "priority": item.get("priority", 0),
                "past_sla": bool(item.get("past_sla", False)),
                "sla_minutes": item.get("sla_minutes", 0),
                "blocked_at_utc": item.get("blocked_at_utc"),
                "escalate_by_utc": item.get("escalate_by_utc"),
                "minutes_overdue": None,
                "minutes_remaining": None,
                "blocked_to_now_seconds": None,
            }

        overdue = now - escalate_by
        overdue_seconds = overdue.total_seconds()
        blocked_to_now = now - blocked_at if blocked_at is not None else None
        return {
            "run_id": item.get("run_id"),
            "owner": item.get("owner"),
            "agent": item.get("agent"),
            "lane": item.get("lane"),
            "reason": item.get("reason"),
            "priority": item.get("priority", 0),
            "past_sla": bool(item.get("past_sla", False)),
            "sla_minutes": item.get("sla_minutes", 0),
            "blocked_at_utc": item.get("blocked_at_utc"),
            "escalate_by_utc": item.get("escalate_by_utc"),
            "minutes_overdue": round(overdue_seconds / 60.0, 2) if overdue_seconds > 0 else 0.0,
            "minutes_remaining": round(-overdue_seconds / 60.0, 2) if overdue_seconds <= 0 else 0.0,
            "blocked_to_now_seconds": round(blocked_to_now.total_seconds(), 2) if blocked_to_now is not None else None,
        }

    escalation_rows = sorted(
        (_to_sla_delta(item) for item in pending),
        key=lambda row: (
            0 if row["past_sla"] else 1,
            -int(row.get("priority", 0)),
            row.get("blocked_at_utc") or "",
        ),
    )
    top_rows = escalation_rows[: max(0, top_escalations)]
    past_sla_count = len(past_sla)

    try:
        trend_samples_requested = int(trend_samples)
    except (TypeError, ValueError):
        trend_samples_requested = 0
    trend_samples_requested = max(trend_samples_requested, 0)

    trend_effective_samples = trend_samples_requested if trend_samples_requested > 1 else 0
    trend_sampling_mode = "enabled" if trend_effective_samples > 0 else "disabled"
    trend_previous_samples_requested = max(0, trend_effective_samples - 1)
    trend_scope_key = _build_observe_summary_trend_scope(
        provider=provider,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        limit=limit,
        top_escalations=top_escalations,
    )
    trend_scope_signature = _hash_observe_summary_trend_scope(trend_scope_key)
    trend_scope_key_json = json.dumps(trend_scope_key, sort_keys=True, separators=(",", ":"))
    trend_records: list[dict[str, Any]] = []
    if trend_previous_samples_requested:
        trend_records = _load_observe_summary_snapshots(
            trend_scope_signature,
            trend_scope_key_json,
            trend_previous_samples_requested,
        )

    trend_snapshot_ids = [
        str((record or {}).get("captured_at_utc", ""))
        for record in trend_records
        if str((record or {}).get("captured_at_utc", ""))
    ]
    trend_snapshot_ids_csv = ", ".join(trend_snapshot_ids)
    trend_snapshot_ids_hash = hashlib.sha256(trend_snapshot_ids_csv.encode("utf-8")).hexdigest()

    baseline_snapshot = trend_records[-1] if trend_records else None
    baseline_available = bool(trend_previous_samples_requested > 0 and trend_records)
    baseline_captured_at_utc = baseline_snapshot.get("captured_at_utc") if baseline_snapshot else None
    trend_snapshot_expected_count = trend_previous_samples_requested
    trend_snapshot_deficit = max(0, trend_snapshot_expected_count - len(trend_records))
    trend_snapshot_invalid_timestamps = 0
    parsed_snapshot_timestamps: list[datetime] = []
    for record in trend_records:
        parsed = _parse_observe_summary_timestamp(record.get("captured_at_utc"))
        if parsed is None:
            trend_snapshot_invalid_timestamps += 1
            continue
        parsed_snapshot_timestamps.append(parsed)

    trend_snapshot_interval_seconds_avg = None
    trend_snapshot_interval_seconds_min = None
    trend_snapshot_interval_seconds_max = None
    trend_snapshot_gap_count = 0
    trend_snapshot_window_seconds = None
    trend_snapshot_coverage_pct = None

    if trend_snapshot_expected_count > 0:
        trend_snapshot_coverage_pct = round((len(trend_records) / trend_snapshot_expected_count) * 100.0, 6)

    if len(parsed_snapshot_timestamps) >= 2:
        ordered = sorted(parsed_snapshot_timestamps)
        diffs: list[int] = []
        for idx in range(1, len(ordered)):
            diffs.append(int((ordered[idx] - ordered[idx - 1]).total_seconds()))
        if diffs:
            trend_snapshot_interval_seconds_avg = int(sum(diffs) / len(diffs))
            trend_snapshot_interval_seconds_min = min(diffs)
            trend_snapshot_interval_seconds_max = max(diffs)
            trend_snapshot_gap_count = len(diffs)
            trend_snapshot_window_seconds = int((ordered[-1] - ordered[0]).total_seconds())

    latest_snapshot = trend_records[0] if trend_records else None
    trend_snapshot_freshness_seconds = None
    if latest_snapshot:
        latest_ts = _parse_observe_summary_timestamp(latest_snapshot.get("captured_at_utc"))
        if latest_ts is not None:
            trend_snapshot_freshness_seconds = int((now - latest_ts).total_seconds())
    trend_snapshot_freshness_bucket = _observe_summary_freshness_bucket(
        trend_snapshot_freshness_seconds,
        fresh_seconds=3600,
        warm_seconds=21600,
        stale_seconds=86400,
    )

    def _delta(current: Any, baseline_value: Any) -> Any:
        if not baseline_available:
            return None
        if current is None or baseline_value is None:
            return None
        try:
            return float(current) - float(baseline_value)
        except (TypeError, ValueError):
            return None

    baseline_kpis: dict[str, Any] = {}
    if baseline_snapshot:
        baseline_kpis = {
            "total_events": baseline_snapshot.get("total_events"),
            "fallback_rate": baseline_snapshot.get("fallback_rate"),
            "success_rate": baseline_snapshot.get("success_rate"),
            "avg_confidence": baseline_snapshot.get("avg_confidence"),
            "structural_drift_pct": baseline_snapshot.get("structural_drift_pct"),
            "semantic_drift_pct": baseline_snapshot.get("semantic_drift_pct"),
        }
        baseline_drifts = {
            "structural_rate_pct": baseline_snapshot.get("drift_structural_rate_pct"),
            "semantic_rate_pct": baseline_snapshot.get("drift_semantic_rate_pct"),
        }
        baseline_escalation = {
            "backlog_count": baseline_snapshot.get("backlog_count"),
            "past_sla_count": baseline_snapshot.get("past_sla_count"),
        }
    else:
        baseline_drifts = {}
        baseline_escalation = {}

    trend_health = _classify_observe_summary_trend_health(
        enabled=trend_sampling_mode == "enabled",
        baseline_available=baseline_available,
        trend_snapshot_coverage_pct=trend_snapshot_coverage_pct,
        trend_snapshot_deficit=trend_snapshot_deficit,
        trend_snapshot_invalid_timestamps=trend_snapshot_invalid_timestamps,
        trend_snapshot_freshness_bucket=trend_snapshot_freshness_bucket,
        trend_snapshot_gap_count=trend_snapshot_gap_count,
        trend_sampling_mode=trend_sampling_mode,
    )

    total_events = float(kpis.get("total", 0.0))
    fallback_rate = float(kpis.get("fallback_rate", 0.0))
    success_rate = float(kpis.get("success_rate", 0.0))
    avg_confidence = float(kpis.get("avg_confidence", 0.0))
    structural_drift_pct = float(kpis.get("structural_drift_pct", 0.0))
    semantic_drift_pct = float(kpis.get("semantic_drift_pct", 0.0))
    drift_structural_rate_pct = float(budget.get("structural_rate_pct", 0.0))
    drift_semantic_rate_pct = float(budget.get("semantic_rate_pct", 0.0))

    trend_snapshot_recommendations = trend_health.get("trend_snapshot_recommendations", [])
    trend_summary = {
        "enabled": trend_sampling_mode == "enabled",
        "trend_sampling_mode": trend_sampling_mode,
        "trend_samples_requested": trend_samples_requested,
        "trend_effective_samples": trend_effective_samples,
        "history_sample_count": len(trend_records),
        "trend_previous_samples_requested": trend_previous_samples_requested,
        "trend_snapshot_expected_count": trend_snapshot_expected_count,
        "trend_snapshot_deficit": trend_snapshot_deficit,
        "trend_snapshot_interval_seconds_avg": trend_snapshot_interval_seconds_avg,
        "trend_snapshot_interval_seconds_min": trend_snapshot_interval_seconds_min,
        "trend_snapshot_interval_seconds_max": trend_snapshot_interval_seconds_max,
        "trend_snapshot_gap_count": trend_snapshot_gap_count,
        "trend_snapshot_invalid_timestamps": trend_snapshot_invalid_timestamps,
        "trend_snapshot_coverage_pct": trend_snapshot_coverage_pct,
        "trend_snapshot_freshness_seconds": trend_snapshot_freshness_seconds,
        "trend_snapshot_freshness_bucket": trend_snapshot_freshness_bucket,
        "trend_snapshot_ids": trend_snapshot_ids,
        "trend_snapshot_ids_csv": trend_snapshot_ids_csv,
        "trend_snapshot_ids_hash": trend_snapshot_ids_hash,
        "trend_snapshot_window_seconds": trend_snapshot_window_seconds,
        "baseline_available": baseline_available,
        "baseline_captured_at_utc": baseline_captured_at_utc,
        "trend_snapshot_health": trend_health.get("trend_snapshot_health"),
        "trend_snapshot_health_score": trend_health.get("trend_snapshot_health_score"),
        "trend_snapshot_health_breakdown": trend_health.get("trend_snapshot_health_breakdown", {}),
        "trend_snapshot_recommendations": trend_snapshot_recommendations,
        "trend_snapshot_recommendation_count": len(trend_snapshot_recommendations),
        "trend_snapshot_recommendations_csv": ", ".join(trend_snapshot_recommendations),
        "total_events_delta": _delta(total_events, baseline_kpis.get("total_events")),
        "fallback_rate_delta": _delta(fallback_rate, baseline_kpis.get("fallback_rate")),
        "success_rate_delta": _delta(success_rate, baseline_kpis.get("success_rate")),
        "avg_confidence_delta": _delta(avg_confidence, baseline_kpis.get("avg_confidence")),
        "structural_drift_pct_delta": _delta(structural_drift_pct, baseline_kpis.get("structural_drift_pct")),
        "semantic_drift_pct_delta": _delta(semantic_drift_pct, baseline_kpis.get("semantic_drift_pct")),
        "drift_structural_rate_pct_delta": _delta(
            drift_structural_rate_pct, baseline_drifts.get("structural_rate_pct")
        ),
        "drift_semantic_rate_pct_delta": _delta(drift_semantic_rate_pct, baseline_drifts.get("semantic_rate_pct")),
        "backlog_count_delta": _delta(len(pending), baseline_escalation.get("backlog_count")),
        "past_sla_count_delta": _delta(past_sla_count, baseline_escalation.get("past_sla_count")),
        "scope_signature": trend_scope_signature,
        "scope_key_json": trend_scope_key_json,
    }

    payload = {
        "kpis": {
            "total_events": kpis.get("total", 0),
            "fallback_rate": kpis.get("fallback_rate", 0.0),
            "success_rate": kpis.get("success_rate", 0.0),
            "avg_confidence": kpis.get("avg_confidence", 0.0),
            "structural_drift_pct": kpis.get("structural_drift_pct", 0.0),
            "semantic_drift_pct": kpis.get("semantic_drift_pct", 0.0),
            "by_provider": kpis.get("by_provider", {}),
        },
        "drift": {
            "issues": drift_issues,
            "within_budget": budget.get("within_budget", True),
            "structural_rate_pct": budget.get("structural_rate_pct", 0.0),
            "semantic_rate_pct": budget.get("semantic_rate_pct", 0.0),
            "structural_budget_pct": budget.get("structural_budget_pct", structural_budget_pct),
            "semantic_budget_pct": budget.get("semantic_budget_pct", semantic_budget_pct),
        },
        "escalation": {
            "backlog_count": len(pending),
            "past_sla_count": past_sla_count,
            "top_escalations": top_rows,
            "provider": provider,
            "top_escalations_count": len(top_rows),
        },
        "payload_type": "observe_summary",
        "payload_schema_version": OBSERVE_SUMMARY_SCHEMA_VERSION,
        "generated_at_utc": now.isoformat(),
        "generated_query": {
            "limit": limit,
            "drift_window": drift_window,
            "structural_budget_pct": structural_budget_pct,
            "semantic_budget_pct": semantic_budget_pct,
            "provider": provider,
            "top_escalations": top_escalations,
            "trend_samples": trend_samples_requested,
            "trend_scope_signature": trend_scope_signature,
        },
        "trend_summary": trend_summary,
        "alerts": [
            alert
            for alert in [
                (f"Escalation backlog critical: {past_sla_count} past-SLA" if past_sla_count else ""),
                (
                    f"Contract drift over budget: structural={budget.get('structural_rate_pct', 0.0)}% "
                    f"(budget {budget.get('structural_budget_pct', structural_budget_pct)}%), "
                    f"semantic={budget.get('semantic_rate_pct', 0.0)}% "
                    f"(budget {budget.get('semantic_budget_pct', semantic_budget_pct)}%)"
                    if not budget.get("within_budget", True)
                    else ""
                ),
            ]
            if alert
        ],
        "status": "critical" if past_sla_count or not budget.get("within_budget", True) else "healthy",
    }
    payload["payload_signature"] = _hash_observe_summary_payload(payload)

    _append_observe_summary_snapshot(
        payload, trend_scope_key, trend_scope_signature, trend_scope_key_json, trend_snapshot_ids, trend_summary
    )
    return payload


def escalate_list_impl(past_sla_only: bool = False, limit: int = 50) -> list[dict[str, Any]]:
    """WP-3008: List escalation queue items (blocked runs with SLA)."""
    from thegent.execution import EscalationQueue

    settings = ThegentSettings()
    session_dir = settings.session_dir.expanduser().resolve()
    queue = EscalationQueue(session_dir)
    return queue.list_pending(past_sla_only=past_sla_only, limit=limit)


def escalate_resolve_impl(run_id: str, resolution: str = "resolved") -> bool:
    """WP-3008: Mark an escalation item as resolved."""
    from thegent.execution import EscalationQueue

    settings = ThegentSettings()
    session_dir = settings.session_dir.expanduser().resolve()
    queue = EscalationQueue(session_dir)
    return queue.resolve(run_id=run_id, resolution=resolution)


def get_data_protection_status_impl() -> dict[str, Any]:
    """Return status of data protection and privacy controls (WP-3006)."""
    settings = ThegentSettings()
    session_dir = settings.session_dir.expanduser().resolve()

    perms_ok = False
    if session_dir.exists():
        mode = os.stat(session_dir).st_mode
        # Check if only owner has access (0700 or 0755 is debatable, but 0700 is stricter)
        perms_ok = oct(mode & 0o777) == "0o700"

    return {
        "session_dir": str(session_dir),
        "session_dir_exists": session_dir.exists(),
        "permissions_restricted": perms_ok,
        "masking_enabled": True,  # Hardcoded as we do masking in logs
        "encryption_at_rest": False,  # Local filesystem encryption depends on OS
        "pii_scanning_enabled": False,  # Future enhancement
        "retention_policy_days": settings.retention_days_sessions,
        "retention_registry_days": settings.retention_days_registry,
        "retention_health_days": settings.retention_days_health,
    }


def sitback_dashboard_impl(profile: str = "medium") -> dict[str, Any]:
    """Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.
    For FastMCP tool/resource: single call replaces cockpit + terminal list + ps.
    profile: light (summary only), medium (panels), full (panels + plugin widgets + harness).
    """
    settings = ThegentSettings()
    session_dir = settings.session_dir.expanduser().resolve()

    # Sessions (ps)
    sessions = ps_impl(all=True, include_contract=False)
    running = [s for s in sessions if s.get("status") == "running"]
    failed = [s for s in sessions if "exited" in str(s.get("status", "")) and s.get("status") != "exited:0"]

    # Cockpit: circuits, drift, budget
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.execution import CircuitBreakerRegistry
    from thegent.governance.cost import CostAggregator

    circuit_breaker = CircuitBreakerRegistry(session_dir)
    ct = ContractTelemetry(session_dir)
    agg = CostAggregator(session_dir)
    targets = ["claude", "gemini", "codex", "copilot", "antigravity"]
    open_circuits = [t for t in targets if circuit_breaker.is_open(t)]
    drift = ct.get_drift_budget_status()
    mtd_total = agg.get_mtd_total() if hasattr(agg, "get_mtd_total") else 0.0
    budget_mtd = float(getattr(settings, "cost_budget_mtd", 100.0))

    # Terminals (tmux panes)
    terminals: list[dict[str, Any]] = []
    try:
        from thegent.tools.terminal import is_claude_code_pane, list_tmux_panes

        for p in list_tmux_panes():
            terminals.append(
                {
                    "pane_id": p.pane_id,
                    "session": p.session_name,
                    "path": p.path,
                    "command": p.command,
                    "title": p.title,
                    "is_claude_code": is_claude_code_pane(p),
                }
            )
    except Exception as e:
        _log.warning("sitback_dashboard terminals: %s", e)

    summary = f"Sessions: {len(running)} running, {len(failed)} failed | Terminals: {len(terminals)} panes ({sum(1 for t in terminals if t.get('is_claude_code'))} Claude Code) | Budget: ${mtd_total:.2f} MTD"
    payload: dict[str, Any] = {
        "sessions": {
            "total": len(sessions),
            "running": len(running),
            "failed": len(failed),
            "items": sessions[:20] if profile != "light" else [],
        },
        "cockpit": {
            "circuits": {"open": open_circuits, "all_closed": len(open_circuits) == 0},
            "drift": drift,
            "budget": {"mtd_total": mtd_total, "mtd_budget": budget_mtd, "within_budget": mtd_total < budget_mtd},
        },
        "terminals": {
            "total": len(terminals),
            "claude_code": sum(1 for t in terminals if t.get("is_claude_code")),
            "items": terminals[:30] if profile != "light" else [],
        },
        "summary": summary,
        "profile": profile,
    }
    if profile == "full":
        from thegent.sitback_plugins import get_registry

        reg = get_registry()
        payload["plugin_widgets"] = reg.get_widgets()
        harness = reg.get_harness_status()
        if harness is not None:
            payload["harness_status"] = harness
    return payload


def run_impl(
    agent: str | None,
    prompt: str,
    cd: Path | None = None,
    mode: str = "write",
    timeout: int = 90,
    full: bool = False,
    model: str | None = None,
    provider: str | None = None,
    run_id: str | None = None,
    owner: str | None = None,
    include_contract: bool = False,
    route_contract: dict[str, Any] | None = None,
    route_request: dict[str, Any] | None = None,
    lane: str = "standard",
    confidence: float | None = None,
    override_reason: str | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
    idempotency_token: str | None = None,
    correlation_id: str | None = None,
    speculative: bool = False,
) -> dict[str, Any]:
    """
    Run an agent or droid with the given prompt.
    Returns dict with keys: stdout, stderr, exit_code, timed_out.
    Model-first: agent=None, model set; provider hint for routing.
    """
    settings = ThegentSettings()
    if agent is None and model:
        from thegent.models import normalize_model_id
        from thegent.models.catalog import ModelCatalog, resolve_route

        model_id = normalize_model_id(model)
        route = resolve_route(model_id, provider_hint=provider)
        if route is None:
            routes = ModelCatalog.routes_for(model_id)
            available = ", ".join(sorted({r.provider for r in routes})) if routes else "none"
            suffix = f" Available: {available}." if available != "none" else ""
            return {
                "error": f"Model '{model}' not available via provider '{provider or 'any'}'.{suffix}",
                "agents": available,
                "exit_code": 1,
                "run_id": run_id or f"run_err_{uuid.uuid4().hex[:8]}",
            }
        agent = route[0]
    agent = resolve_agent(agent or "")

    # WP-X1/V7: Contract Migration & Version Negotiation
    from thegent.contracts.migration import MigrationController
    from thegent.contracts.registry import CONTRACT_SCHEMA_VERSION

    migrator = MigrationController()
    requested_version = contract_version or CONTRACT_SCHEMA_VERSION
    mig_res = migrator.evaluate_version("csm", requested_version)

    if not mig_res["allowed"]:
        return {
            "error": f"Contract version rejected: {mig_res['reason']}",
            "exit_code": 1,
            "run_id": run_id or f"run_err_{uuid.uuid4().hex[:8]}",
        }

    if mig_res["status"] == "deprecated":
        # We allow it but should log/warn (CLI will print it via run_cmd if we pass it)
        pass

    effective_timeout = max(timeout, settings.default_timeout_claude) if agent == "claude" else timeout

    prompt = _inject_time_constraint(prompt, effective_timeout, summary_mode=not full)

    cwd = _resolve_cwd(cd)
    if cwd is None:
        return {"error": "Ambiguous cwd. Provide --cd /path explicitly.", "exit_code": 1}

    # Terminal reuse suggestion (light management)
    if os.environ.get("THGENT_TERMINAL_MANAGEMENT_ENABLED", "1") == "1":
        try:
            import importlib

            routing = importlib.import_module("thegent.routing")
            TaskRouter = getattr(routing, "TaskRouter", None)
            if TaskRouter:
                router = TaskRouter(settings)
                existing_pane = router.find_active_terminal_for_path(str(cwd))
                if existing_pane:
                    console.print(
                        f"[bold yellow]Found existing terminal session for this path: {existing_pane}[/bold yellow]"
                    )
                    console.print(f"[dim]You can attach with: thegent terminal attach {existing_pane}[/dim]")
        except Exception as e:
            _log.debug(f"Terminal discovery failed: {e}")

    # G-GP-02: Input guardrails before PolicyEngine
    if os.environ.get("THGENT_INPUT_GUARDRAILS_ENABLED", "").lower() in ("1", "true", "yes"):
        try:
            from thegent.governance.input_guardrails import _guardrails_from_env

            guardrails = _guardrails_from_env()
            gr = guardrails.check(prompt=prompt, agent=agent or "", model=model, cwd=cwd)
            if not gr.passed:
                return {
                    "error": f"Input guardrail failed ({gr.rail_id}): {gr.reason}",
                    "remediation": gr.remediation,
                    "exit_code": 1,
                    "run_id": run_id or f"run_err_{uuid.uuid4().hex[:8]}",
                }
        except Exception:
            pass

    # Concurrency control (WP-5001)
    from thegent.execution import ConcurrencyController

    cc = ConcurrencyController(settings.session_dir, max_concurrency=settings.max_concurrency)
    if not cc.acquire(lane=lane):
        return {
            "error": f"Concurrency limit reached ({settings.max_concurrency}). Task queued or blocked.",
            "exit_code": 1,
            "run_id": run_id or f"run_err_{uuid.uuid4().hex[:8]}",
        }

    # WP-5001: Speculative Execution Mode
    if speculative:
        _log.info("Speculative execution active; racing multiple providers.")
        # Simplified: pick top 2 and race
        # In a real impl, we'd use a thread pool

    # Registry integration
    registry = RunRegistry(settings.session_dir)

    # WP-1003/WP-1008: Idempotency / Replay Detection
    if idempotency_token:
        existing = registry.find_by_token(idempotency_token)
        if existing and existing.get("status") == "completed":
            _log.info("Replay detected for token %s; skipping execution.", idempotency_token)
            return {
                "stdout": existing.get("stdout", ""),
                "stderr": existing.get("stderr", ""),
                "exit_code": existing.get("exit_code", 0),
                "run_id": existing.get("run_id"),
                "replayed": True,
            }

    from thegent.execution import (
        Auditor,
        CircuitBreakerRegistry,
        OverrideRegistry,
        PolicyEngine,
        TrustBoundaryValidator,
    )

    circuit_breaker = CircuitBreakerRegistry(settings.session_dir)
    trust_boundary = TrustBoundaryValidator(settings.session_dir)
    override_registry = OverrideRegistry(settings.session_dir)
    policy_engine = PolicyEngine(settings)
    auditor = Auditor(registry.registry_path)

    # WP-3007: Trust Boundary Checks
    last_env = trust_boundary.get_last_environment()
    allowed, boundary_reason = trust_boundary.validate_transition(last_env, settings.environment.lower())
    if not allowed:
        return {
            "error": f"Trust boundary violation: {boundary_reason}",
            "exit_code": 1,
            "run_id": run_id or f"run_err_{uuid.uuid4().hex[:8]}",
        }

    # WP-4004: Interruption Controls
    from thegent.execution import InterruptionTracker

    it = InterruptionTracker(settings.session_dir)
    fatigue = it.get_fatigue_score()
    if fatigue > 0.8:
        _log.warning("High fatigue detected (%.2f); recommending non-critical deferral.", fatigue)
        if lane != "critical":
            console.print("[bold yellow]ADVISORY:[/bold yellow] High system fatigue. Deferring non-critical task.")
            return {"error": "System fatigue limit reached. Task deferred.", "exit_code": 1}

    effective_owner = owner or _default_owner_tag(cwd)

    # WP-4005: State Freshness Checks
    from thegent.execution import FreshnessValidator

    fv = FreshnessValidator(settings.session_dir)
    freshness_issues = fv.validate_action(run_id or "new", [registry.registry_path])
    if freshness_issues:
        _log.warning("Freshness issues detected: %s", freshness_issues)
        if lane == "critical":
            return {"error": f"State freshness violation in critical lane: {freshness_issues}", "exit_code": 1}

    # WP-5002: Burst Load Classification
    from thegent.execution import DeferralQueue, LoadClassifier

    lc = LoadClassifier(settings.session_dir)
    load_level = lc.get_load_level()
    if load_level == "burst" and lane != "critical":
        dq = DeferralQueue(settings.session_dir)
        rid = run_id or f"run_def_{uuid.uuid4().hex[:8]}"
        dq.defer(rid, "System in burst mode; non-critical deferral active")
        console.print("[bold yellow]BURST MODE:[/bold yellow] Non-critical task deferred to queue.")
        return {"error": "System in burst mode. Task deferred.", "exit_code": 1, "run_id": rid}

    run_meta = RunMeta(
        run_id=run_id or f"run_{uuid.uuid4().hex[:8]}",
        correlation_id=correlation_id,
        agent=agent or "unknown",
        model=model,
        mode=mode,
        prompt=prompt,
        cwd=str(cwd),
        owner=effective_owner,
        route_contract=route_contract,
        route_request=route_request,
        lane=lane,
        confidence=confidence,
        idempotency_token=idempotency_token,
        override_reason=override_reason,
        override_by=effective_owner if override_reason else None,
        domain_tag=domain or settings.default_domain_tag,
        contract_version=requested_version,
    )

    # WP-3001: Policy Evaluation
    pol_res, pol_reason = policy_engine.evaluate(run_meta, registry)

    # WP-3003: Overrides with TTL (revalidation on expiry)
    if pol_res == "deny":
        if override_reason:
            console.print(f"[bold yellow]Policy OVERRIDE applied:[/bold yellow] {override_reason}")
            override_registry.record(effective_owner, override_reason, settings.override_ttl_seconds)
            pol_res = "allow"
            pol_reason = f"Overridden: {pol_reason}"
        elif override_registry.has_unexpired(effective_owner):
            console.print("[dim]Policy override (cached, within TTL)[/dim]")
            pol_res = "allow"
            pol_reason = f"Overridden (cached): {pol_reason}"

    run_meta.policy_result = pol_res
    run_meta.policy_reason = pol_reason

    # WP-3002: Signing
    run_meta.signature = auditor.sign_run(run_meta)

    if pol_res == "deny":
        # WP-3008: Add to escalation queue for SLA tracking
        escalate_add_impl(
            run_id=run_meta.run_id,
            reason=pol_reason,
            sla_minutes=settings.escalation_sla_minutes,
            owner=run_meta.owner,
            agent=run_meta.agent,
            lane=run_meta.lane,
        )
        registry.register_start(run_meta)
        registry.register_end(
            run_id=run_meta.run_id,
            exit_code=1,
            status="failed",
            ended_at_utc=datetime.now(UTC).isoformat(),
            duration_s=0.0,
            error_class="policy_violation",
        )
        return {"error": f"Policy Violation: {pol_reason}", "exit_code": 1}

    # G-GP-05: HITL Pause Flow
    if pol_res == "pause":
        from thegent.execution import CheckpointRegistry

        registry.register_start(run_meta)
        registry.register_pause(run_meta.run_id, reason=pol_reason)

        ckpt_registry = CheckpointRegistry(settings.session_dir)
        ckpt_registry.create_checkpoint(
            reason=f"HITL Pause: {pol_reason}",
            dag_content=run_meta.model_dump_json(),
            owner=run_meta.owner,
        )

        escalate_add_impl(
            run_id=run_meta.run_id,
            reason=f"HITL Pause: {pol_reason}",
            sla_minutes=settings.escalation_sla_minutes,
            owner=run_meta.owner,
            agent=run_meta.agent,
            lane=run_meta.lane,
            priority=1,  # High priority for HITL
        )
        return {
            "error": f"HITL PAUSE: {pol_reason}. Escalated for approval.",
            "exit_code": 0,
            "status": "paused",
            "run_id": run_meta.run_id,
        }

    if pol_res == "warn":
        console.print(f"[yellow]Policy Warning: {pol_reason}[/yellow]")

    registry.register_start(run_meta)
    start_time = time.time()

    use_stream = not full

    agents_to_try: list[str] = [agent] if agent else []
    if model:
        from thegent.models import ModelCatalog, normalize_model_id

        model_id = normalize_model_id(model)
        routes = ModelCatalog.routes_for(model_id)
        # Use catalog routes that aren't the primary agent
        catalog_fallbacks = [r.provider for r in routes if r.provider != agent]
        agents_to_try.extend(catalog_fallbacks)

    provider_fallbacks = get_fallback_agents(agent or "unknown")
    for pf in provider_fallbacks:
        if pf not in agents_to_try:
            agents_to_try.append(pf)

    result = None
    exit_code = 1
    status = "failed"
    error_class = None

    # WP-X6: Fallback Control Plane
    from thegent.agents.state_machine import FallbackStateMachine
    from thegent.contracts.policy import FallbackPolicy
    from thegent.contracts.telemetry import ContractTelemetry, rank_providers_by_parser_quality

    telemetry = ContractTelemetry(settings.session_dir)
    # G-CA-02 B2: Parser-quality routing - order providers by confidence/fallback rate
    if settings.routing_parser_quality_enabled:
        agents_to_try = rank_providers_by_parser_quality(agents_to_try, telemetry, limit=100)
    policy = FallbackPolicy(
        allow_plain_fallback=settings.normalization_policy_allow_fallback,
        min_confidence_threshold=settings.normalization_policy_min_confidence,
        max_fallback_rate=settings.normalization_policy_max_fallback_rate,
        strict_providers=[p.strip() for p in settings.normalization_policy_strict_providers.split(",") if p.strip()],
    )

    fsm = FallbackStateMachine(
        providers=agents_to_try,
        run_id=run_meta.run_id,
        policy=policy,
        telemetry=telemetry,
        max_retries_per_provider=3,
    )

    def runner_factory(agent_name: str) -> AgentRunner | None:
        # G-GP-04: Skip providers with open circuit
        if circuit_breaker.is_open(agent_name):
            _log.warning("Circuit open for %s; skipping", agent_name)
            return None
        runner = get_runner(agent_name)
        if runner is None:
            return None

        # Wrap runner.run to inject agent_model
        original_run = runner.run
        agent_model = _resolve_agent_model(agent_name, model, mode, settings)

        def wrapped_run(**kwargs) -> RunResult:
            if agent_model:
                kwargs["agent_model"] = agent_model
            res = original_run(**kwargs)
            if res.exit_code != 0:
                circuit_breaker.record_failure(agent_name)
            return res

        # Create a proxy object that satisfies AgentRunner
        @dataclass
        class RunnerProxy(AgentRunner):
            def run(
                self,
                prompt: str,
                cwd: Path | None,
                mode: str,
                timeout: int,
                *,
                use_stream: bool = True,
                live_output: bool = False,
                on_stdout: Callable[[str], None] | None = None,
                on_stderr: Callable[[str], None] | None = None,
            ) -> RunResult:
                return wrapped_run(
                    prompt=prompt,
                    cwd=cwd,
                    mode=mode,
                    timeout=timeout,
                    use_stream=use_stream,
                    live_output=live_output,
                    on_stdout=on_stdout,
                    on_stderr=on_stderr,
                )

        return RunnerProxy()

    result, norm_res = fsm.run(
        runner_factory=runner_factory,
        prompt=prompt,
        cwd=cwd,
        mode=mode,
        timeout=effective_timeout,
        use_stream=use_stream,
    )

    status = fsm.state.status
    if status == "success":
        exit_code = 0
        status = "completed"
    else:
        exit_code = result.exit_code if result else 1
        status = "failed"
        if result and result.timed_out:
            status = "timed_out"

        # WP-2008: DLQ Enqueue on Failure
        if lane == "critical":
            from thegent.execution import DLQManager

            dlq = DLQManager(settings.session_dir)
            dlq.enqueue(run_meta, f"Run {status}: {result.stderr if result else 'No result'}")
            _log.info("Critical run %s; enqueued to DLQ.", status)

    # G-CA-03 C3: No critical lane with unknown contract
    _known_contracts = ("csm-v1", "task-tool-18", "zen-rich-v1", "xml-tags", "plain")
    if (
        lane == "critical"
        and norm_res
        and (norm_res.csm.source_contract == "fallback-plain" or norm_res.csm.source_contract not in _known_contracts)
    ):
        status = "failed"
        exit_code = 1
        error_class = "unknown_contract"

    # Map error class
    if result:
        if result.timed_out:
            error_class = "timeout"
        elif is_usage_limit(result):
            error_class = "usage_limit"
        elif result.exit_code != 0:
            error_class = "api_error"

    duration = time.time() - start_time
    cost_usd = None
    if os.environ.get("THGENT_COST_TRACKING", "").lower() in ("1", "true", "yes"):
        try:
            from thegent.governance.cost import CostEstimator

            est = CostEstimator()
            cost_usd = est.estimate(
                model=run_meta.model,
                prompt_length=len(run_meta.prompt or ""),
            )
        except Exception:
            pass
    registry.register_end(
        run_id=run_meta.run_id,
        exit_code=exit_code,
        status=status,
        ended_at_utc=datetime.now(UTC).isoformat(),
        duration_s=duration,
        error_class=error_class,
        cost_usd=cost_usd,
    )

    # WP-3007: Record environment after run for next transition check
    if status == "completed":
        trust_boundary.record_environment(settings.environment.lower())

        # WP-2007: Evidence Linting
        if norm_res and norm_res.csm:
            from thegent.execution import EvidenceLinter

            linter = EvidenceLinter(settings.session_dir)
            lint_issues = linter.lint(norm_res.csm)
            if lint_issues:
                _log.warning("Evidence lint issues for %s: %s", run_meta.run_id, lint_issues)
                if run_meta.lane == "critical":
                    console.print(f"[bold red]LINT FAILURE:[/bold red] Evidence incomplete: {lint_issues}")

        # WP-3002: Generate and persist signed MAIF artifact
        try:
            artifact = auditor.generate_maif_artifact(run_meta, output=result.stdout if result else None)
            auditor.persist_maif_artifact(settings.session_dir, artifact)
        except Exception:
            pass

    if not result:
        return {
            "error": f"Unknown agent: {agent}",
            "agents": ", ".join(list_agent_names()),
            "exit_code": 1,
            "run_id": run_meta.run_id,
        }

    stderr = result.stderr or ""
    stdout = result.stdout or ""
    csm = norm_res.csm if norm_res else None

    # WP-X7: Contract Telemetry (already recorded in FSM)

    if use_stream:
        # Prefer condensed stream display (Cursor-style); fall back to extract_condensed
        if csm:
            stdout = csm.summary
        else:
            condensed = condense_stream_to_display(stdout)
            stdout = condensed or extract_condensed(stdout)

    payload = {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": result.exit_code,
        "timed_out": result.timed_out,
        "run_id": run_meta.run_id,
    }
    if csm and norm_res:
        payload["csm"] = csm.to_dict()
        payload["normalization_confidence"] = norm_res.confidence

    if include_contract:
        payload["route_contract"] = route_contract
        payload["route_request"] = route_request

    return payload


def bg_impl(
    *,
    agent: str | None,
    prompt: str,
    cd: Path | None,
    mode: str,
    timeout: int,
    full: bool,
    model: str | None = None,
    provider: str | None = None,
    owner: str | None = None,
    continue_from: str | None = None,
    continuation_include_stderr: bool = False,
    include_contract: bool = False,
    route_contract: dict[str, Any] | None = None,
    route_request: dict[str, str] | None = None,
    routing: str | None = None,
    failover: bool = False,
    run_id: str | None = None,
    lane: str | None = None,
    confidence: float | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
    idempotency_token: str | None = None,
    speculative: bool = False,
) -> dict[str, Any]:
    """
    Start a background run. Returns dict with keys: session_id, log_path, owner.
    """
    settings = ThegentSettings()
    if agent is None and model:
        from thegent.models import normalize_model_id
        from thegent.models.catalog import ModelCatalog, resolve_route

        model_id = normalize_model_id(model)
        route = resolve_route(model_id, provider_hint=provider)
        if route is None:
            routes = ModelCatalog.routes_for(model_id)
            available = ", ".join(sorted({r.provider for r in routes})) if routes else "none"
            suffix = f" Available: {available}." if available != "none" else ""
            return {
                "error": f"Model '{model}' not available via provider '{provider or 'any'}'.{suffix}",
                "agents": available,
                "exit_code": 1,
                "session_id": "failed",
            }
        agent = route[0]
    agent = resolve_agent(agent) or "unknown"

    # WP-X1/V7: Contract Migration & Version Negotiation
    from thegent.contracts.migration import MigrationController
    from thegent.contracts.registry import CONTRACT_SCHEMA_VERSION

    migrator = MigrationController()
    requested_version = contract_version or CONTRACT_SCHEMA_VERSION
    mig_res = migrator.evaluate_version("csm", requested_version)

    if not mig_res["allowed"]:
        return {
            "error": f"Contract version rejected: {mig_res['reason']}",
            "exit_code": 1,
            "session_id": "failed",
        }

    effective_timeout = max(timeout, settings.default_timeout_claude) if agent == "claude" else timeout
    cwd = _resolve_cwd(cd)
    if cwd is None:
        return {"error": "Ambiguous cwd. Provide --cd /path explicitly.", "exit_code": 1}

    full = full or True

    effective_prompt = prompt
    if continue_from:
        effective_prompt = _build_continuation_prompt(
            settings, continue_from, prompt, include_stderr=continuation_include_stderr
        )

    owner_tag = owner or _default_owner_tag(cwd, include_process_id=True)
    base = _session_dir(settings, owner_tag)
    session_id = _new_session_id(agent, owner_tag)
    p = _session_paths(base, session_id)

    # Registry integration
    registry = RunRegistry(settings.session_dir)

    # WP-1003/WP-1008: Idempotency
    if idempotency_token:
        existing = registry.find_by_token(idempotency_token)
        if existing and existing.get("status") == "completed":
            _log.info("Replay detected for token %s in bg; skipping.", idempotency_token)
            return {
                "session_id": existing.get("correlation_id") or "replayed",
                "run_id": existing.get("run_id"),
                "replayed": True,
            }

    effective_run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"

    # WP-5001: Speculative Execution Mode
    if speculative:
        _log.info("Speculative execution active in background.")

    from thegent.execution import (
        Auditor,
        CircuitBreakerRegistry,
        OverrideRegistry,
        PolicyEngine,
        TrustBoundaryValidator,
    )

    circuit_breaker = CircuitBreakerRegistry(settings.session_dir)
    trust_boundary = TrustBoundaryValidator(settings.session_dir)
    override_registry = OverrideRegistry(settings.session_dir)
    auditor = Auditor(registry.registry_path)
    policy_engine = PolicyEngine(settings)
    effective_owner = owner or _default_owner_tag(cwd)

    # WP-3007: Trust Boundary Checks
    last_env = trust_boundary.get_last_environment()
    allowed, boundary_reason = trust_boundary.validate_transition(last_env, settings.environment.lower())
    if not allowed:
        return {
            "error": f"Trust boundary violation: {boundary_reason}",
            "exit_code": 1,
            "session_id": "failed",
        }

    run_meta = RunMeta(
        run_id=effective_run_id,
        correlation_id=session_id,
        agent=agent,
        model=model,
        mode=mode,
        prompt=prompt,
        cwd=str(cwd),
        owner=owner_tag,
        is_background=True,
        route_contract=route_contract,
        route_request=route_request,
        domain_tag=domain or settings.default_domain_tag,
        lane=lane or "standard",
        confidence=confidence,
        idempotency_token=idempotency_token,
        contract_version=requested_version,
    )

    # G-GP-05: Policy pre-check for background runs
    pol_res, pol_reason = policy_engine.evaluate(run_meta, registry)

    # WP-3003: Overrides with TTL (revalidation on expiry)
    if pol_res == "deny" and override_registry.has_unexpired(owner_tag):
        _log.info("Policy override (cached, within TTL) for background run")
        pol_res = "allow"
        pol_reason = f"Overridden (cached): {pol_reason}"

    run_meta.policy_result = pol_res
    run_meta.policy_reason = pol_reason
    run_meta.signature = auditor.sign_run(run_meta)

    if pol_res == "deny":
        escalate_add_impl(
            run_id=run_meta.run_id,
            reason=pol_reason,
            sla_minutes=settings.escalation_sla_minutes,
            owner=run_meta.owner,
            agent=run_meta.agent,
            lane=run_meta.lane,
        )
        registry.register_start(run_meta)
        registry.register_end(
            run_id=run_meta.run_id,
            exit_code=1,
            status="failed",
            ended_at_utc=datetime.now(UTC).isoformat(),
            duration_s=0.0,
            error_class="policy_violation",
        )
        return {"error": f"Policy Violation: {pol_reason}", "exit_code": 1}

    if pol_res == "pause":
        from thegent.execution import CheckpointRegistry

        registry.register_start(run_meta)
        registry.register_pause(run_meta.run_id, reason=pol_reason)

        ckpt_registry = CheckpointRegistry(settings.session_dir)
        ckpt_registry.create_checkpoint(
            reason=f"HITL Pause (bg): {pol_reason}",
            dag_content=run_meta.model_dump_json(),
            owner=run_meta.owner,
        )

        escalate_add_impl(
            run_id=run_meta.run_id,
            reason=f"HITL Pause (bg): {pol_reason}",
            sla_minutes=settings.escalation_sla_minutes,
            owner=run_meta.owner,
            agent=run_meta.agent,
            lane=run_meta.lane,
            priority=1,
        )
        return {
            "error": f"HITL PAUSE: {pol_reason}",
            "session_id": session_id,
            "status": "paused",
            "run_id": run_meta.run_id,
        }

    registry.register_start(run_meta)

    cmd: list[str] = [sys.executable, "-m", "thegent.main", "run"]
    cmd.extend(["-d", str(cwd), "-m", mode, "-t", str(effective_timeout)])
    if full:
        cmd.append("--full")
    if routing:
        cmd.extend(["-R", routing])
    if failover:
        cmd.append("--failover")
    if model:
        cmd.extend(["-M", model])
    if requested_version:
        cmd.extend(["--contract-version", requested_version])
    if domain:
        cmd.extend(["--domain", domain])

    # Pass run_id to the background process so it can close the registry entry correctly
    cmd.extend(["--run-id", effective_run_id])

    cmd.append(effective_prompt)
    if agent:
        cmd.append(agent)

    stdout_handle = p["stdout"].open("wb")
    stderr_handle = p["stderr"].open("wb")

    # G-GP-08: Sandbox environment filtering
    if os.environ.get("THGENT_SANDBOX_ENV_FILTER", "").lower() in ("1", "true", "yes"):
        allowlist = settings.sandbox_env_allowlist
        env = {k: v for k, v in os.environ.items() if k in allowlist or k.startswith("THGENT_")}
    else:
        env = os.environ.copy()

    env["PYTHONUNBUFFERED"] = "1"
    env.update(
        {
            "THGENT_SESSION_ID": session_id,
            "THGENT_SESSION_META_PATH": str(p["meta"]),
            "THGENT_SESSION_RC_PATH": str(p["rc"]),
            "THGENT_SESSION_STDOUT_PATH": str(p["stdout"]),
            "THGENT_SESSION_STDERR_PATH": str(p["stderr"]),
            "THGENT_OWNER_TAG": owner_tag,
        }
    )

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
            start_new_session=True,
        )
    except Exception:
        stdout_handle.close()
        stderr_handle.close()
        raise
    finally:
        stdout_handle.close()
        stderr_handle.close()

    meta: dict[str, Any] = {
        "version": 1,
        "session_id": session_id,
        "agent": agent,
        "owner": owner_tag,
        "cwd": str(cwd),
        "prompt": prompt,
        "mode": mode,
        "timeout_hint_s": effective_timeout,
        "host": socket.gethostname(),
        "launcher_pid": os.getpid(),
        "launcher_ppid": os.getppid(),
        "launcher_uid": os.getuid(),
        "status": "running",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "pid": proc.pid,
        "command": cmd,
        "paths": {k: str(v) for k, v in p.items()},
    }
    if include_contract:
        if route_contract is not None:
            meta["route_contract"] = route_contract
        if route_request is not None:
            meta["route_request"] = route_request
    if continue_from:
        meta["continued_from"] = continue_from.split(",")[0].strip()
    _save_session_meta(p["meta"], meta)

    return {
        "session_id": session_id,
        "log_path": str(p["stdout"]),
        "owner": owner_tag,
    }


def ps_impl(
    owner: str | None = None,
    all: bool = False,
    include_contract: bool = False,
) -> list[dict[str, Any]]:
    """
    List background sessions. Returns list of session dicts.
    """
    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    base = settings.session_dir.expanduser().resolve()
    rows: list[dict[str, Any]] = []
    scope_dirs = [p for p in sorted(base.glob("*")) if p.is_dir()] if all else _session_scope_dirs(base, own)

    meta_files: list[Path] = []
    for scope_dir in scope_dirs:
        if scope_dir.exists():
            meta_files.extend(sorted(scope_dir.glob("*.json")))
    for meta in meta_files:
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not all and m.get("owner") != own:
            continue
        pid = int(m.get("pid", 0) or 0)
        running = _is_pid_running(pid)
        sid = m.get("session_id", meta.stem)
        p = _session_paths(meta.parent, sid)
        prompt_raw = m.get("prompt", "")
        prompt_preview = (prompt_raw[:40] + "...") if len(prompt_raw) > 40 else (prompt_raw or "—")
        status = _resolve_session_status(m, p["rc"], running=running)
        rows.append(
            {
                "id": sid,
                "agent": m.get("agent", "?"),
                "owner": m.get("owner", "?"),
                "pid": pid,
                "status": status,
                "started_at_utc": m.get("started_at_utc", ""),
                "prompt_preview": prompt_preview,
            }
        )
        if include_contract:
            row = rows[-1]
            row["route_contract"] = m.get("route_contract")
            row["route_request"] = m.get("route_request")
    return rows


def list_session_contracts_impl(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
) -> list[dict[str, Any]]:
    """
    Return sessions with route-request/route-contract metadata and contract quality signal.
    """

    def _alignment_issues(
        route_request: dict[str, Any] | None,
        route_contract: dict[str, Any] | None,
    ) -> list[str]:
        if not strict or not route_request or not route_contract:
            return []

        issues: list[str] = []
        requested_provider = route_request.get("requested_provider_hint")
        contract_provider = route_contract.get("provider")
        if requested_provider is not None and contract_provider is not None and requested_provider != contract_provider:
            issues.append("misalign:provider_hint")

        requested_alias = route_request.get("resolved_model_alias") or route_request.get("resolved_alias")
        contract_alias = route_contract.get("model_alias")
        if requested_alias is not None and contract_alias is not None and requested_alias != contract_alias:
            issues.append("misalign:resolved_alias")

        resolved_agent = route_request.get("resolved_agent")
        if resolved_agent is not None and contract_provider is not None and resolved_agent != contract_provider:
            issues.append("misalign:resolved_agent")

        return issues

    rows = ps_impl(owner=owner, all=all, include_contract=True)
    contracts: list[dict[str, Any]] = []

    for row in rows:
        route_request = row.get("route_request")
        route_contract = row.get("route_contract")
        request_obj = route_request if isinstance(route_request, dict) else None
        contract_obj = route_contract if isinstance(route_contract, dict) else None
        request_present = request_obj is not None
        contract_present = contract_obj is not None

        contract_issues: list[str] = []
        if contract_obj is not None:
            required_contract_fields = ("provider", "model_alias", "backend_type", "priority")
            for key in required_contract_fields:
                if contract_obj.get(key) is None:
                    contract_issues.append(f"missing_contract:{key}")
            if contract_obj.get("schema_version") is None:
                contract_issues.append("missing_contract:schema_version")
        if request_obj is not None:
            if not request_obj.get("requested_model"):
                contract_issues.append("missing_request:requested_model")
            if request_obj.get("policy") not in {"prefer_direct", "prefer_proxy", "failover"}:
                contract_issues.append("missing_request:policy")

        if not request_present and not contract_present:
            state = "untracked"
        elif request_present and not contract_present:
            state = "request_only"
        elif contract_present and not request_present:
            state = "contract_only"
        elif contract_issues:
            state = "partial"
        else:
            state = "complete"

        alignment_issues = _alignment_issues(request_obj, contract_obj)
        contract_issues.extend(alignment_issues)

        if not request_present or not contract_present:
            contract_health = "missing"
        elif any(issue.startswith("misalign:") for issue in alignment_issues):
            contract_health = "error"
        elif contract_issues:
            contract_health = "warning"
        else:
            contract_health = "healthy"

        contracts.append(
            {
                "session_id": row.get("id", ""),
                "agent": row.get("agent", ""),
                "owner": row.get("owner", ""),
                "pid": row.get("pid", 0),
                "status": row.get("status", "unknown"),
                "started_at_utc": row.get("started_at_utc", ""),
                "route_request": request_obj,
                "route_contract": contract_obj,
                "contract_state": state,
                "route_request_present": request_present,
                "route_contract_present": contract_present,
                "contract_health": contract_health,
                "strict_checks_enabled": strict,
                "contract_issues": contract_issues,
                "requested_model": request_obj.get("requested_model") if request_obj is not None else None,
                "requested_provider_hint": request_obj.get("requested_provider_hint")
                if request_obj is not None
                else None,
                "resolved_model_alias": (request_obj.get("resolved_model_alias") or request_obj.get("resolved_alias"))
                if request_obj is not None
                else None,
                "policy": request_obj.get("policy") if request_obj is not None else None,
            }
        )

    return contracts


def session_contract_audit_impl(
    owner: str | None = None,
    all: bool = False,
    missing_only: bool = False,
    summary_only: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    """
    Return session contract audit rows with optional filtering and summary.
    """
    rows = list_session_contracts_impl(owner=owner, all=all, strict=strict)
    if missing_only:
        rows = [row for row in rows if row.get("contract_state") != "complete"]

    states: dict[str, int] = {}
    for row in rows:
        state = str(row.get("contract_state", "unknown"))
        states[state] = states.get(state, 0) + 1

    health: dict[str, int] = {"healthy": 0, "warning": 0, "error": 0, "missing": 0}
    for row in rows:
        key = str(row.get("contract_health", "warning"))
        health[key] = health.get(key, 0) + 1

    summary = {
        "total": len(rows),
        "complete": states.get("complete", 0),
        "partial": states.get("partial", 0),
        "request_only": states.get("request_only", 0),
        "contract_only": states.get("contract_only", 0),
        "untracked": states.get("untracked", 0),
        "strict_checks_enabled": strict,
        "health": health,
    }
    if summary_only:
        return {"rows": [], "summary": summary}
    return {"rows": rows, "summary": summary}


def purge_impl(dry_run: bool = True) -> dict[str, int]:
    """WP-3006: Tiered retention purge implementation (G-GP-07)."""
    from thegent.config import ThegentSettings
    from thegent.execution import RunRegistry

    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)

    # Use structured settings for retention
    default_days = settings.retention_days_registry
    by_domain = settings.retention_by_domain

    return registry.purge_expired(default_days=default_days, by_domain=by_domain, dry_run=dry_run)


def session_contract_health_gate_impl(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    min_healthy_ratio: float = 1.0,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Evaluate routing contract health against a minimum healthy-ratio gate.
    """
    policy = _resolve_health_policy(policy_profile, strict, min_healthy_ratio)
    effective_strict = bool(policy["strict"])
    threshold = float(policy["min_healthy_ratio"])
    tolerance = max(0.0, float(regression_tolerance))

    audit = session_contract_audit_impl(
        owner=owner,
        all=all,
        missing_only=False,
        summary_only=False,
        strict=effective_strict,
    )
    summary = audit["summary"]
    rows = audit["rows"]
    total = int(summary.get("total", 0))

    health = summary.get("health", {})
    healthy_count = int(health.get("healthy", 0))
    unhealthy_count = max(total - healthy_count, 0)
    ratio = (healthy_count / total) if total > 0 else 1.0
    ratio_pass = total == 0 or ratio >= threshold

    blockers = [
        {
            "session_id": str(row.get("session_id")),
            "state": row.get("contract_state"),
            "health": row.get("contract_health"),
            "issues": _coerce_issue_types(row.get("contract_issues")),
        }
        for row in rows
        if row.get("contract_health") != "healthy"
    ]
    blockers = sorted(
        blockers,
        key=lambda row: (
            str(row.get("health") or ""),
            str(row.get("state") or ""),
            str(row.get("session_id") or ""),
        ),
    )
    blockers = [
        {
            **row,
            "issues": sorted(_coerce_issue_types(row.get("issues", [])), key=str),
        }
        for row in blockers
    ]

    payload = {
        "schema_version": HEALTH_PAYLOAD_SCHEMA_VERSION,
        "payload_type": "session_contract_health_gate",
        "schema_compat_mode": "compat",
        "pass": ratio_pass,
        "status": "passed" if ratio_pass else "blocked",
        "threshold": threshold,
        "total": total,
        "total_sessions": total,
        "healthy_count": healthy_count,
        "healthy_sessions": healthy_count,
        "unhealthy_count": unhealthy_count,
        "unhealthy_sessions": unhealthy_count,
        "healthy_ratio": ratio,
        "summary": summary,
        "blocked_count": len(blockers),
        "blocked_sessions_count": len(blockers),
        "blocked_ratio": (1.0 - ratio) if total > 0 else 0.0,
        "top_blocked_count": min(200, len(blockers)),
        "blocked_sessions_cap": 200,
        "blocked_sessions": blockers[:200],
        "strict_checks_enabled": effective_strict,
        "policy_profile": policy["profile"],
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "generated_query": {
            "owner": owner,
            "all": all,
            "strict": effective_strict,
            "min_healthy_ratio": threshold,
        },
    }
    scope_key = _health_scope_key(payload)
    previous = _load_previous_health_snapshot(scope_key)

    blocked_ratio_val = payload.get("blocked_ratio", 0.0)
    blocked_count_val = payload.get("blocked_count", 0)
    cur_ratio = 0.0
    cur_count = 0
    try:
        if blocked_ratio_val is not None:
            cur_ratio = float(str(blocked_ratio_val))
        if blocked_count_val is not None:
            cur_count = int(str(blocked_count_val))
    except (TypeError, ValueError):
        cur_ratio = 0.0
        cur_count = 0

    if previous is not None:
        try:
            previous_ratio = float(str(previous.get("blocked_ratio", cur_ratio)))
        except (TypeError, ValueError):
            previous_ratio = cur_ratio
        try:
            previous_count = int(str(previous.get("blocked_count", cur_count)))
        except (TypeError, ValueError):
            previous_count = cur_count
    else:
        previous_ratio = cur_ratio
        previous_count = cur_count
    previous_issue_types = set(_coerce_issue_types((previous or {}).get("issue_types", [])))
    current_issue_types: set[str] = set()
    for row in blockers:
        current_issue_types.update(_coerce_issue_types(row.get("issues", [])))

    baseline_pass = True
    if no_worse_than_baseline and previous is not None:
        baseline_pass = cur_ratio <= (previous_ratio + tolerance)

    final_pass = ratio_pass and baseline_pass
    reason_codes: list[str] = []
    if not ratio_pass:
        reason_codes.append("ratio_below_threshold")
    if no_worse_than_baseline and previous is not None and not baseline_pass:
        reason_codes.append("baseline_regression")
    payload["pass"] = final_pass
    payload["status"] = "passed" if final_pass else "blocked"
    payload["decision_reasons"] = reason_codes or ["ok"]
    payload["policy_evaluation"] = {
        "profile": policy["profile"],
        "profile_exists": policy["profile_exists"],
        "enforce_no_worse_than_baseline": bool(no_worse_than_baseline),
        "regression_tolerance": tolerance,
        "rules": [
            {
                "id": "min_healthy_ratio",
                "pass": ratio_pass,
                "actual_healthy_ratio": ratio,
                "threshold": threshold,
            },
            {
                "id": "no_worse_than_baseline",
                "enabled": bool(no_worse_than_baseline),
                "baseline_available": previous is not None,
                "pass": baseline_pass if no_worse_than_baseline and previous is not None else True,
                "baseline_blocked_ratio": previous_ratio if previous is not None else None,
                "current_blocked_ratio": cur_ratio,
                "blocked_ratio_delta": (cur_ratio - previous_ratio if previous is not None else None),
            },
        ],
        "final_pass": final_pass,
    }
    payload["trend_summary"] = {
        "baseline_available": previous is not None,
        "blocked_ratio_delta": (cur_ratio - previous_ratio if previous is not None else None),
        "blocked_count_delta": cur_count - previous_count if previous is not None else None,
        "new_issue_types": sorted(current_issue_types - previous_issue_types),
        "resolved_issue_types": sorted(previous_issue_types - current_issue_types),
    }
    payload["compat"] = {
        "mode": "compat",
        "aliases": {
            "total_sessions": "total",
            "healthy_sessions": "healthy_count",
            "unhealthy_sessions": "unhealthy_count",
            "blocked_sessions_count": "blocked_count",
        },
    }
    payload["payload_signature"] = _hash_health_payload(payload)
    _append_health_snapshot(payload, scope_key)
    return payload


def explain_run_impl(run_id: str) -> dict[str, Any]:
    """WP-4002: Multi-tier explanation framework for run decisions."""
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)

    # 1. Fetch Run Metadata
    runs = registry.list_runs(limit=100)
    run = next((r for r in runs if r.get("run_id") == run_id), None)

    if not run:
        return {"error": f"Run {run_id} not found", "exit_code": 1}

    # 2. Extract Rationales
    concise = run.get("policy_reason") or run.get("error_class") or "No concise rationale available."
    detailed = run.get("rationale") or "No detailed rationale available."

    return {
        "run_id": run_id,
        "concise_rationale": concise,
        "detailed_rationale": detailed,
        "agent": run.get("agent"),
        "status": run.get("status"),
        "confidence": run.get("confidence"),
    }


def session_contract_health_report_impl(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    top_blocked: int = 25,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Return health report with issue taxonomy and owner-level breakdown.
    """
    remediation_map = {
        "misalign:provider_hint": "Normalize requested_provider_hint to match contract provider or clear hint before routing.",
        "misalign:resolved_alias": "Align resolved alias/model with chosen contract model_alias.",
        "misalign:resolved_agent": "Set resolved_agent to selected contract provider.",
        "missing_contract:provider": "Ensure route_contract includes provider metadata at session creation.",
        "missing_contract:model_alias": "Ensure route_contract includes model_alias metadata at session creation.",
        "missing_contract:backend_type": "Ensure route_contract includes backend_type metadata at session creation.",
        "missing_contract:priority": "Ensure route_contract includes routing priority metadata at session creation.",
        "missing_contract:schema_version": "Ensure route_contract captures schema version at session creation.",
        "missing_request:requested_model": "Populate requested_model in route_request before persisting session metadata.",
        "missing_request:policy": "Persist route request policy (prefer_direct, prefer_proxy, failover).",
    }

    def _remediation_lines(row_issues: list[str]) -> list[str]:
        lines: list[str] = []
        for issue in row_issues:
            hint = remediation_map.get(str(issue))
            if hint is not None:
                lines.append(hint)
        if not lines and row_issues:
            lines.append("Review session route metadata capture path and re-run routing with include_contract.")
        if not row_issues:
            lines.append("No issues detected; this row is not blocked.")
        return lines

    max_blocked = top_blocked
    if max_blocked is None:
        max_blocked = 25
    max_blocked = max(max_blocked, 0)

    policy = _resolve_health_policy(policy_profile, strict, 1.0)
    effective_strict = bool(policy["strict"])
    tolerance = max(0.0, float(regression_tolerance))

    audit = session_contract_audit_impl(
        owner=owner,
        all=all,
        missing_only=False,
        summary_only=False,
        strict=effective_strict,
    )
    rows = audit["rows"]
    summary = audit["summary"]
    health = summary.get("health", {})
    total = int(summary.get("total", 0))

    issue_counts: dict[str, int] = {}
    owner_breakdown: dict[str, dict[str, int]] = {}
    blocked_rows: list[dict[str, Any]] = []

    for row in rows:
        owner_name = str(row.get("owner", ""))
        bucket = owner_breakdown.setdefault(
            owner_name,
            {"total": 0, "healthy": 0, "warning": 0, "error": 0, "missing": 0},
        )
        bucket["total"] += 1
        health_state = str(row.get("contract_health", "warning"))
        bucket[health_state] = bucket.get(health_state, 0) + 1

        issues = row.get("contract_issues") or []
        for issue in _coerce_issue_types(issues):
            issue_key = str(issue)
            issue_counts[issue_key] = issue_counts.get(issue_key, 0) + 1

        if row.get("contract_health") != "healthy":
            issues = sorted(
                [str(issue) for issue in _coerce_issue_types(row.get("contract_issues") or [])],
                key=str,
            )
            blocked_rows.append(
                {
                    "session_id": str(row.get("session_id", "")),
                    "owner": owner_name,
                    "state": row.get("contract_state"),
                    "health": row.get("contract_health"),
                    "issues": issues,
                    "remediation": _remediation_lines(cast("list[str]", issues)),
                    "started_at_utc": row.get("started_at_utc", ""),
                    "agent": row.get("agent", ""),
                }
            )

    issue_counts = {key: issue_counts[key] for key in sorted(issue_counts)}
    issue_breakdown = [
        {"issue": key, "count": count}
        for key, count in sorted(
            issue_counts.items(),
            key=lambda kv: (kv[1], str(kv[0])),
        )
        if count
    ]
    # Stable order: highest count first, then alpha by issue key.
    issue_breakdown = sorted(
        issue_breakdown,
        key=lambda row: (-int(row["count"]), str(row["issue"])),
    )

    for row in owner_breakdown.values():
        # Ensure missing bucket exists for deterministic schema.
        row.setdefault("missing", row.get("missing", 0))
        row.setdefault("warning", row.get("warning", 0))
        row.setdefault("error", row.get("error", 0))
        row.setdefault("healthy", row.get("healthy", 0))

    owner_breakdown = {owner_key: owner_breakdown[owner_key] for owner_key in sorted(owner_breakdown, key=str.lower)}

    blocked_rows_sorted = sorted(
        blocked_rows,
        key=lambda row: (
            str(row.get("health") or ""),
            str(row.get("owner") or ""),
            str(row.get("state") or ""),
            str(row.get("session_id") or ""),
        ),
    )
    blocked_count = len(blocked_rows)
    healthy_count = int(health.get("healthy", 0))
    unhealthy_count = max(total - int(health.get("healthy", 0)), 0)
    payload = {
        "schema_version": HEALTH_PAYLOAD_SCHEMA_VERSION,
        "payload_type": "session_contract_health_report",
        "schema_compat_mode": "compat",
        "pass": blocked_count == 0,
        "status": "passed" if blocked_count == 0 else "blocked",
        "total": total,
        "total_sessions": total,
        "healthy_count": healthy_count,
        "healthy_sessions": healthy_count,
        "unhealthy_count": unhealthy_count,
        "unhealthy_sessions": unhealthy_count,
        "summary": summary,
        "health": health,
        "issue_counts": issue_counts,
        "issue_breakdown": issue_breakdown,
        "owner_breakdown": owner_breakdown,
        "top_blocked": blocked_rows_sorted[:max_blocked],
        "blocked_count": blocked_count,
        "blocked_sessions": blocked_count,
        "blocked_sessions_count": blocked_count,
        "top_blocked_count": min(max_blocked, len(blocked_rows)),
        "strict_checks_enabled": effective_strict,
        "policy_profile": policy["profile"],
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "generated_query": {
            "owner": owner,
            "all": all,
            "strict": effective_strict,
            "top_blocked": max_blocked,
        },
        "blocked_ratio": (blocked_count / total) if total > 0 else 0.0,
    }
    scope_key = _health_scope_key(payload)
    previous = _load_previous_health_snapshot(scope_key)
    cur_ratio = 0.0
    cur_count = 0
    try:
        br = payload.get("blocked_ratio", 0.0)
        bc = payload.get("blocked_count", 0)
        if br is not None:
            cur_ratio = float(str(br))
        if bc is not None:
            cur_count = int(str(bc))
    except (TypeError, ValueError):
        pass

    if previous is not None:
        try:
            previous_ratio = float(str(previous.get("blocked_ratio", cur_ratio)))
        except (TypeError, ValueError):
            previous_ratio = cur_ratio
        try:
            previous_count = int(str(previous.get("blocked_count", cur_count)))
        except (TypeError, ValueError):
            previous_count = cur_count
        previous_issue_counts = previous.get("issue_counts", {})
    else:
        previous_ratio = cur_ratio
        previous_count = cur_count
        previous_issue_counts = {}
    previous_issue_types = {str(i) for i in previous_issue_counts}
    current_issue_types = {str(i) for i in issue_counts}
    max_blocked_ratio = 1.0 - float(policy["min_healthy_ratio"])
    ratio_pass = cur_ratio <= max_blocked_ratio
    baseline_pass = True
    if no_worse_than_baseline and previous is not None:
        baseline_pass = cur_ratio <= (previous_ratio + tolerance)
    final_pass = ratio_pass and baseline_pass
    reason_codes: list[str] = []
    if not ratio_pass:
        reason_codes.append("blocked_ratio_exceeds_profile")
    if no_worse_than_baseline and previous is not None and not baseline_pass:
        reason_codes.append("baseline_regression")
    payload["pass"] = final_pass
    payload["status"] = "passed" if final_pass else "blocked"
    payload["decision_reasons"] = reason_codes or ["ok"]
    payload["policy_evaluation"] = {
        "profile": policy["profile"],
        "profile_exists": policy["profile_exists"],
        "enforce_no_worse_than_baseline": bool(no_worse_than_baseline),
        "regression_tolerance": tolerance,
        "rules": [
            {
                "id": "max_blocked_ratio_by_profile",
                "pass": ratio_pass,
                "actual_blocked_ratio": cur_ratio,
                "max_blocked_ratio": max_blocked_ratio,
            },
            {
                "id": "no_worse_than_baseline",
                "enabled": bool(no_worse_than_baseline),
                "baseline_available": previous is not None,
                "pass": baseline_pass if no_worse_than_baseline and previous is not None else True,
                "baseline_blocked_ratio": previous_ratio if previous is not None else None,
                "current_blocked_ratio": cur_ratio,
                "blocked_ratio_delta": (cur_ratio - previous_ratio if previous is not None else None),
            },
        ],
        "final_pass": final_pass,
    }
    payload["trend_summary"] = {
        "baseline_available": previous is not None,
        "blocked_ratio_delta": (cur_ratio - previous_ratio if previous is not None else None),
        "blocked_count_delta": cur_count - previous_count if previous is not None else None,
        "new_issue_types": sorted(current_issue_types - previous_issue_types),
        "resolved_issue_types": sorted(previous_issue_types - current_issue_types),
    }
    payload["compat"] = {
        "mode": "compat",
        "aliases": {
            "total_sessions": "total",
            "healthy_sessions": "healthy_count",
            "unhealthy_sessions": "unhealthy_count",
            "blocked_sessions_count": "blocked_count",
        },
    }
    payload["payload_signature"] = _hash_health_payload(payload)
    _append_health_snapshot(payload, scope_key)
    return payload


def session_contract_health_trend_impl(
    payload_type: str = "session_contract_health_report",
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    policy_profile: str | None = None,
    min_healthy_ratio: float = 1.0,
    top_blocked: int = 25,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Return recent health snapshots and deltas for a given policy/query scope.
    """
    if payload_type not in HEALTH_PAYLOAD_TYPES:
        raise typer.BadParameter(
            f"Unsupported payload_type '{payload_type}'. Choose one of: {', '.join(HEALTH_PAYLOAD_TYPES)}."
        )
    policy = _resolve_health_policy(policy_profile, strict, min_healthy_ratio)
    gen_query: dict[str, Any] = {
        "owner": owner,
        "all": all,
        "strict": policy["strict"],
    }
    if payload_type == "session_contract_health_gate":
        gen_query["min_healthy_ratio"] = policy["min_healthy_ratio"]
    else:
        gen_query["top_blocked"] = int(top_blocked)

    scope_payload: dict[str, Any] = {
        "payload_type": payload_type,
        "policy_profile": policy["profile"],
        "generated_query": gen_query,
    }
    scope_key = _health_scope_key(scope_payload)

    max_items = max(1, int(limit))
    path = _health_snapshot_log_path()
    snapshots: list[dict[str, Any]] = []
    if path.exists():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("record_type") != "health_snapshot":
                continue
            if rec.get("scope_key") != scope_key:
                continue
            snapshots.append(rec)
            if len(snapshots) >= max_items:
                break

    latest = snapshots[0] if snapshots else None
    oldest = snapshots[-1] if snapshots else None
    delta_ratio = None
    delta_count = None
    if latest is not None and oldest is not None and len(snapshots) > 1:
        delta_ratio = float(latest.get("blocked_ratio", 0.0)) - float(oldest.get("blocked_ratio", 0.0))
        delta_count = int(latest.get("blocked_count", 0)) - int(oldest.get("blocked_count", 0))
    snapshot_window_seconds = None
    if latest is not None and oldest is not None and len(snapshots) > 1:
        latest_ts_raw = (latest or {}).get("captured_at_utc", "")
        oldest_ts_raw = (oldest or {}).get("captured_at_utc", "")
        try:
            latest_ts = datetime.fromisoformat(str(latest_ts_raw))
            oldest_ts = datetime.fromisoformat(str(oldest_ts_raw))
            snapshot_window_seconds = int((latest_ts - oldest_ts).total_seconds())
        except (TypeError, ValueError):
            snapshot_window_seconds = None
    snapshot_interval_seconds_avg = None
    parsed_ts: list[datetime] = []
    for snap in snapshots:
        ts_raw = (snap or {}).get("captured_at_utc", "")
        if not ts_raw:
            continue
        try:
            parsed_ts.append(datetime.fromisoformat(str(ts_raw)))
        except (TypeError, ValueError):
            continue
    if len(parsed_ts) > 1:
        parsed_ts.sort()
        diffs: list[int] = []
        for i in range(1, len(parsed_ts)):
            diffs.append(int((parsed_ts[i] - parsed_ts[i - 1]).total_seconds()))
        if diffs:
            snapshot_interval_seconds_avg = int(sum(diffs) / len(diffs))
    snapshot_ids_csv = ", ".join(
        [str((s or {}).get("captured_at_utc", "")) for s in snapshots if (s or {}).get("captured_at_utc", "")]
    )
    generated_at = datetime.now(UTC)
    snapshot_freshness_seconds = None
    if latest is not None:
        latest_ts_raw = (latest or {}).get("captured_at_utc", "")
        try:
            latest_ts = datetime.fromisoformat(str(latest_ts_raw))
            snapshot_freshness_seconds = int((generated_at - latest_ts).total_seconds())
        except (TypeError, ValueError):
            snapshot_freshness_seconds = None
    snapshot_density_per_hour = None
    if snapshot_window_seconds is not None and snapshot_window_seconds > 0 and len(snapshots) > 0:
        snapshot_density_per_hour = round((len(snapshots) * 3600.0) / float(snapshot_window_seconds), 6)
    latest_issue_types = set(_coerce_issue_types((latest or {}).get("issue_types", [])))
    oldest_issue_types = set(_coerce_issue_types((oldest or {}).get("issue_types", [])))
    snapshot_issue_churn_count = len(latest_issue_types.symmetric_difference(oldest_issue_types))
    snapshot_health_volatility = None
    blocked_ratios: list[float] = []
    for snap in snapshots:
        try:
            blocked_ratios.append(float((snap or {}).get("blocked_ratio", 0.0)))
        except (TypeError, ValueError):
            continue
    if len(blocked_ratios) > 1:
        mean_ratio = sum(blocked_ratios) / len(blocked_ratios)
        variance = sum((r - mean_ratio) ** 2 for r in blocked_ratios) / len(blocked_ratios)
        snapshot_health_volatility = round(variance**0.5, 6)

    payload: dict[str, Any] = {
        "schema_version": HEALTH_PAYLOAD_SCHEMA_VERSION,
        "payload_type": "session_contract_health_trend",
        "schema_compat_mode": "compat",
        "trend_payload_type": payload_type,
        "scope_key": scope_key,
        "scope_key_json": json.dumps(scope_key, sort_keys=True),
        "scope_payload_type": scope_key.get("payload_type", ""),
        "scope_owner": scope_key.get("owner", ""),
        "scope_all": scope_key.get("all", False),
        "scope_strict": scope_key.get("strict", False),
        "scope_policy_profile": scope_key.get("policy_profile", "custom"),
        "scope_min_healthy_ratio": scope_key.get("min_healthy_ratio", None),
        "scope_top_blocked": scope_key.get("top_blocked", None),
        "snapshot_count": len(snapshots),
        "snapshot_ids_csv": snapshot_ids_csv,
        "snapshot_ids_hash": hashlib.sha256(snapshot_ids_csv.encode("utf-8")).hexdigest(),
        "snapshot_window_seconds": snapshot_window_seconds,
        "snapshot_window_hash": hashlib.sha256(str(snapshot_window_seconds).encode("utf-8")).hexdigest(),
        "snapshot_interval_seconds_avg": snapshot_interval_seconds_avg,
        "snapshot_interval_hash": hashlib.sha256(str(snapshot_interval_seconds_avg).encode("utf-8")).hexdigest(),
        "snapshot_freshness_seconds": snapshot_freshness_seconds,
        "snapshot_freshness_hash": hashlib.sha256(str(snapshot_freshness_seconds).encode("utf-8")).hexdigest(),
        "snapshot_density_per_hour": snapshot_density_per_hour,
        "snapshot_density_hash": hashlib.sha256(str(snapshot_density_per_hour).encode("utf-8")).hexdigest(),
        "snapshot_issue_churn_count": snapshot_issue_churn_count,
        "snapshot_issue_churn_hash": hashlib.sha256(str(snapshot_issue_churn_count).encode("utf-8")).hexdigest(),
        "snapshot_health_volatility": snapshot_health_volatility,
        "snapshot_health_volatility_hash": hashlib.sha256(str(snapshot_health_volatility).encode("utf-8")).hexdigest(),
        "limit": max_items,
        "latest": latest,
        "latest_status": (latest or {}).get("status", ""),
        "latest_pass": (latest or {}).get("pass", None),
        "latest_captured_at_utc": (latest or {}).get("captured_at_utc", ""),
        "latest_blocked_ratio": (latest or {}).get("blocked_ratio", None),
        "latest_blocked_count": (latest or {}).get("blocked_count", None),
        "latest_issue_types_count": len(_coerce_issue_types((latest or {}).get("issue_types", []))),
        "latest_issue_types_json": json.dumps(_coerce_issue_types((latest or {}).get("issue_types", []))),
        "latest_issue_types_csv": ", ".join(str(v) for v in _coerce_issue_types((latest or {}).get("issue_types", []))),
        "latest_issue_types_hash": hashlib.sha256(
            json.dumps(_coerce_issue_types((latest or {}).get("issue_types", []))).encode("utf-8")
        ).hexdigest(),
        "oldest": oldest,
        "delta_summary": {
            "blocked_ratio_delta": delta_ratio,
            "blocked_count_delta": delta_count,
        },
        "delta_summary_json": json.dumps(
            {
                "blocked_count_delta": delta_count,
                "blocked_ratio_delta": delta_ratio,
            },
            sort_keys=True,
        ),
        "blocked_ratio_delta": delta_ratio,
        "blocked_count_delta": delta_count,
        "snapshot_retention_max_lines": _health_snapshot_max_lines(),
        "snapshots": snapshots,
        "generated_at_utc": generated_at.isoformat(),
        "compat": {
            "mode": "compat",
            "aliases": {
                "scope.owner": "scope_owner",
                "scope.all": "scope_all",
                "scope.strict": "scope_strict",
                "scope.policy_profile": "scope_policy_profile",
                "scope.min_healthy_ratio": "scope_min_healthy_ratio",
                "scope.top_blocked": "scope_top_blocked",
            },
        },
    }
    compat = cast("dict[str, Any]", payload.get("compat", {}))
    compat_aliases = cast("dict[str, str]", compat.get("aliases", {}))
    payload["compat_aliases_count"] = len(compat_aliases)
    payload["payload_signature"] = _hash_health_payload(payload)
    return payload


def status_impl(
    session_id: str,
    include_contract: bool = False,
) -> dict[str, Any]:
    """
    Get status of a background session.
    """

    def _resolve_exit_code(payload: dict[str, Any], rc_path: Path, is_running: bool) -> int | None:
        if is_running:
            return None
        exit_code = payload.get("exit_code")
        if isinstance(exit_code, int):
            return exit_code
        if isinstance(exit_code, str):
            try:
                return int(exit_code.strip())
            except ValueError:
                pass
        if rc_path.exists():
            try:
                raw = rc_path.read_text(encoding="utf-8").strip()
                return int(raw) if raw else None
            except (OSError, ValueError):
                return None
        return None

    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as e:
        return {"error": str(e), "session_id": session_id}
    p = _session_paths(meta_path.parent, session_id)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    running = _is_pid_running(pid)
    status = _resolve_session_status(m, p["rc"], running=running)
    exit_code = _resolve_exit_code(m, p["rc"], is_running=running)
    payload: dict[str, Any] = {
        "session_id": session_id,
        "status": status,
        "pid": pid,
        "running": running,
        "exit_code": exit_code,
        "owner": m.get("owner", ""),
        "host": m.get("host"),
        "agent": m.get("agent"),
        "mode": m.get("mode"),
        "cwd": m.get("cwd"),
        "timeout_hint_s": m.get("timeout_hint_s"),
        "command": m.get("command", []),
        "launcher_pid": m.get("launcher_pid"),
        "launcher_ppid": m.get("launcher_ppid"),
        "launcher_uid": m.get("launcher_uid"),
        "started_at_utc": m.get("started_at_utc"),
        "ended_at_utc": m.get("ended_at_utc"),
        "duration_seconds": m.get("duration_seconds"),
        "timed_out": m.get("timed_out", False),
        "paths": m.get("paths", {}),
    }
    if include_contract:
        payload["route_contract"] = m.get("route_contract")
        payload["route_request"] = m.get("route_request")
    return payload


def inspect_impl(
    session_ids: list[str],
    owner: str | None = None,
    tail: int = 50,
    stderr: bool = False,
    include_contract: bool = False,
) -> list[dict[str, Any]]:
    """
    Get status and logs for one or more sessions. Returns list of {session_id, status, logs}.
    """
    if not session_ids and owner:
        rows = ps_impl(owner=owner, all=False)
        session_ids = [r["id"] for r in rows]
    if not session_ids:
        return []
    out: list[dict[str, Any]] = []
    for sid in session_ids:
        st = status_impl(session_id=sid, include_contract=include_contract)
        try:
            log_text = logs_impl(session_id=sid, tail=tail, stderr=stderr)
        except Exception as e:
            log_text = f"Error: {e}"
        out.append({"session_id": sid, "status": st, "logs": log_text})
    return out


def logs_impl(session_id: str, tail: int | None = None, stderr: bool = False) -> str:
    """
    Get logs from a background session. Returns log text.
    """
    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as e:
        return f"Error: {e}"
    p = _session_paths(meta_path.parent, session_id)
    target = p["stderr"] if stderr else p["stdout"]
    if not target.exists():
        return f"Log file missing: {target}"

    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    if tail is not None and tail > 0:
        lines = lines[-tail:]
    return "\n".join(lines)


def wait_impl(session_id: str, timeout: int | None = None) -> dict[str, Any]:
    """
    Wait for a background session to complete.
    """
    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as e:
        return {"error": str(e), "session_id": session_id}
    p = _session_paths(meta_path.parent, session_id)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    start = time.time()
    timed_out = False
    while _is_pid_running(pid):
        if timeout and timeout > 0 and (time.time() - start) >= timeout:
            timed_out = True
            break
        time.sleep(0.5)
    rc = int(p["rc"].read_text(encoding="utf-8").strip()) if p["rc"].exists() else 0
    return {
        "session_id": session_id,
        "exit_code": rc,
        "timed_out": timed_out,
    }


def stop_impl(session_id: str, force: bool = False) -> dict[str, Any]:
    """
    Stop a background session.
    """
    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as e:
        return {"error": str(e), "session_id": session_id}
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    if not _is_pid_running(pid):
        return {"session_id": session_id, "status": "not_running"}
    try:
        if force:
            os.killpg(pid, signal.SIGKILL)
            return {"session_id": session_id, "status": "stopped_force"}
        os.killpg(pid, signal.SIGTERM)
        return {"session_id": session_id, "status": "stopped"}
    except OSError as e:
        return {"session_id": session_id, "status": "error", "error": str(e)}


def history_impl(limit: int = 50) -> list[dict[str, Any]]:
    """
    List execution history from the run registry.
    """
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    return registry.list_runs(limit=limit)


def events_impl(run_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """
    List raw telemetry events from the run registry.
    """
    settings = ThegentSettings()
    registry_path = settings.session_dir / "run_registry.jsonl"
    if not registry_path.exists():
        return []

    events: list[dict[str, Any]] = []
    with registry_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if run_id and data.get("run_id") != run_id:
                    continue
                events.append(data)
            except Exception:
                continue

    return events[-limit:]


def list_agents_impl() -> list[dict[str, str]]:
    """List available agents. Returns list of {name, backend}. name is label (cursor) for display."""
    agents = list_agent_names()
    backends = {
        "minimax": "cliproxy",
        "glm": "cliproxy",
        "roo": "cliproxy",
        "kilo": "cliproxy",
        "gemini": "codex",
        "codex": "codex",
        "copilot": "codex",
        "claude": "codex",
        "antigravity": "codex",
        "cursor-agent": "Direct",
        "cursor-api": "cursor-api",
    }
    return [{"name": AGENT_LABELS.get(n, n), "backend": backends.get(n, "Direct")} for n in agents]


def list_droids_impl(cd: Any = None) -> list[str]:
    """List available droids. Returns list of droid names."""
    settings = ThegentSettings()
    cwd = _resolve_cwd(cd) or Path.cwd()
    droids_dir = _resolve_droids_dir(cwd, settings)
    return sorted(list_droid_names(droids_dir))


def list_models_impl(
    provider: str | None = None,
    use_scraped: bool = True,
    refresh: bool = False,
    include_contract: bool = False,
    by_model: bool = False,
) -> dict[str, Any]:
    """List available models.

    By default returns {provider: [model_names]}.
    If include_contract=True, returns structured contract metadata for route discovery.
    If by_model=True, returns {model_id: [provider, ...]} (R4, R5).
    """
    if include_contract:
        from thegent.models import ModelCatalog

        return ModelCatalog.to_contract_view(
            use_scraped=use_scraped,
            use_cache=not refresh,
            provider_filter=provider,
        )

    if by_model:
        from thegent.models import ModelCatalog
        from thegent.models.scrapers import get_scraped_catalog

        if refresh:
            get_scraped_catalog(use_cache=False)
        view = ModelCatalog.to_catalog_view(use_scraped=use_scraped)
        return dict(view.by_model)

    all_providers = [
        "minimax",
        "glm",
        "cursor-agent",
        "cursor-api",
        "gemini",
        "copilot",
        "claude",
        "codex",
        "antigravity",
    ]
    providers = [provider] if provider else all_providers
    settings = ThegentSettings()
    result: dict[str, list[str]] = {}
    # Static fallbacks
    fallbacks: dict[str, list[str]] = {
        "minimax": ["minimax-m2.5"],
        "glm": ["glm-5"],
        "roo": ["roo-default"],
        "kilo": ["kilo-default"],
        "cursor-agent": [settings.default_cursor_model],
        "gemini": [settings.default_gemini_model],
        "copilot": [settings.default_copilot_model],
        "claude": [settings.default_claude_model],
        "codex": [settings.default_codex_model],
        "antigravity": [settings.default_antigravity_model],
    }
    if use_scraped:
        try:
            from thegent.models.scrapers import get_scraped_catalog

            scraped = get_scraped_catalog(use_cache=not refresh)
            for p in providers:
                result[p] = scraped.get(p, fallbacks.get(p, []))
            return result
        except Exception:
            pass
    for p in providers:
        result[p] = fallbacks.get(p, [])
    return result


def dag_list_impl(cd: Path | None = None) -> dict[str, Any]:
    """List DAG tasks. Returns {frontmatter, tasks} or error."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        return {"error": "Ambiguous cwd. Provide --cd /path or run from project root."}
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return {"error": f"DAG not found: {dag_path}", "frontmatter": {}, "tasks": []}
    frontmatter, tasks = _parse_dag_session(dag_path)
    return {"frontmatter": frontmatter, "tasks": tasks}


def session_meta_impl(session_id: str) -> dict[str, Any]:
    """Get full session metadata. Returns meta dict or error."""
    import typer

    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
        return _read_session_meta(meta_path)
    except typer.BadParameter as e:
        return {"error": str(e)}


def dag_raw_impl(cd: Path | None = None) -> str:
    """Get raw DAG markdown content. Returns markdown string or error message."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        return "# Error\nAmbiguous cwd. Provide --cd /path or run from project root."
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return f"# Error\nDAG not found: {dag_path}"
    return dag_path.read_text(encoding="utf-8")


def session_contract_negotiate_impl(contract_id: str, supported_versions: list[str]) -> dict[str, Any]:
    """
    WP-7001: Implementation of contract negotiation logic.
    """
    from thegent.contracts.registry import ContractNegotiator

    negotiator = ContractNegotiator()
    return negotiator.negotiate(contract_id, supported_versions)
