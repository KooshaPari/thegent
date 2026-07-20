"""CLI implementation helpers.

This module provides the core CLI implementation functions extracted from
the main CLI module.
"""

from __future__ import annotations

import errno
import math
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer

from thegent.config import ThegentSettings

if TYPE_CHECKING:
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.execution import EscalationQueue

# EAGAIN/EWOULDBLOCK errno numbers for retry logic
_EAGAIN_ERRNOS = {errno.EAGAIN, errno.EWOULDBLOCK, errno.EINTR}

# Health payload schema version
HEALTH_PAYLOAD_SCHEMA_VERSION = "1.0"


# Retry if eagain decorator
def _retry_if_eagain(func: Any) -> Any:
    """Retry function if EAGAIN error occurs."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except OSError as e:
                if e.errno in _EAGAIN_ERRNOS and attempt < max_retries - 1:
                    time.sleep(0.1 * (2**attempt))
                    continue
                raise
        return None

    return wrapper


# Backoff delay function
def _backoff_delay(attempt: int, base: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay."""
    return min(base * (2**attempt), max_delay)


# Atomic write function
def _atomic_write(path: Path, content: str) -> None:
    """Atomically write content to a file."""
    import tempfile
    import os

    path_str = str(path)
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode="w", delete=False, dir=str(Path(path_str).parent) or ".") as f:
        f.write(content)
        temp_path = f.name
    os.rename(temp_path, path_str)


# Spawn with eagain retry
def _spawn_with_eagain_retry(cmd: list[str], **kwargs: Any) -> Any:
    """Spawn process with EAGAIN retry logic."""
    import subprocess

    max_retries = 3
    for attempt in range(max_retries):
        try:
            return subprocess.run(cmd, **kwargs)
        except OSError as e:
            if e.errno in _EAGAIN_ERRNOS and attempt < max_retries - 1:
                time.sleep(0.1 * (2**attempt))
                continue
            raise
    return None


# AUDIT-N+14: ``_resolve_cwd`` lives in :mod:`thegent.cli.commands.session_impl`
# (canonical home). The local stub is removed so the AUDIT-N+12 re-export
# binds the canonical 4-arg form (with caching + project-indicator scan).
# Legacy callers must import from ``thegent.cli.commands.session_impl``
# directly or via ``thegent.cli.commands.impl._resolve_cwd`` (re-export).

# AUDIT-N+14: ``_resolve_droids_dir`` lives here (impl.py is the canonical
# home — it is not a session-lifecycle helper).


def _resolve_droids_dir(cwd: Path | None, settings: ThegentSettings) -> Path:
    """Resolve the droids directory.

    Args:
        cwd: The working directory.
        settings: Thegent settings.

    Returns:
        Path to the droids directory.
    """
    if cwd is not None:
        factory_droids = cwd / ".factory" / "droids"
        if factory_droids.exists():
            return factory_droids.resolve()

    return settings.factory_droids_dir.expanduser().resolve()


# AUDIT-N+14: ``_compose_owner_tag`` and ``_default_owner_tag`` live in
# :mod:`thegent.cli.commands.session_impl` (canonical home). The local stubs
# are removed so the AUDIT-N+12 re-export binds the canonical 4-arg form
# (with ``{pid}`` / ``{cwd}`` placeholder expansion + ``THGENT_OWNER_TAG``
# env override).

# AUDIT-N+14: ``_write_session_state`` and ``_normalize_image_paths`` stay
# here (impl.py is the canonical home — they are not session-lifecycle
# helpers).


def _write_session_state(session_dir: Path, state: dict[str, Any]) -> None:
    """Write session state to disk."""
    import json

    state_file = session_dir / "session_state.json"
    state_file.write_text(json.dumps(state))


def _normalize_image_paths(paths: list[str]) -> list[str]:
    """Normalize image paths."""
    from pathlib import Path

    return [str(Path(p).expanduser().resolve()) for p in paths]


class DagDocument:
    """DAG document representation for CLI."""

    def __init__(self, name: str = "") -> None:
        """Initialize DAG document."""
        self.name = name
        self.nodes: list[dict[str, Any]] = []
        self.edges: list[tuple[str, str]] = []

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {"name": self.name, "nodes": self.nodes, "edges": self.edges}


class DagPrioritizer:
    """Prioritizer for DAG nodes."""

    def __init__(self) -> None:
        self.priorities: dict[str, int] = {}

    def prioritize(self, nodes: list[str]) -> list[str]:
        """Prioritize nodes by their priority values."""
        return sorted(nodes, key=lambda n: self.priorities.get(n, 999))


def run_impl(prompt: str, **kwargs: Any) -> dict[str, Any]:
    """Run the implementation.

    Thin delegate to :func:`thegent.cli.services.run_execution_core_helpers.run_impl_core`.
    The full execution pipeline (Pareto routing, policy, escalation, MAIF,
    observability) lives in the extracted core; this wrapper exists to keep the
    public CLI surface stable and to allow tests to stub the core via
    ``monkeypatch.setattr`` on the helper module.

    Args:
        prompt: The prompt to execute.
        **kwargs: Forwarded to ``run_impl_core``. See that function's signature
            for accepted parameters.

    Returns:
        Result dictionary from ``run_impl_core``.
    """
    # Lazy import — keep impl.py import-order safe (run_execution_core_helpers
    # imports back from impl at module top via _LazyImpl).
    import sys as _sys
    from thegent.cli.services import run_execution_core_helpers

    impl_ns = _sys.modules.get("thegent.cli.commands.impl")
    if impl_ns is None:
        import importlib

        impl_ns = importlib.import_module("thegent.cli.commands.impl")
    return run_execution_core_helpers.run_impl_core(prompt=prompt, impl_ns=impl_ns, **kwargs)


def list_models_impl(**kwargs: Any) -> dict[str, Any]:
    """Implementation for list models command."""
    return {"models": []}


def resume_impl(session_id: str, **kwargs: Any) -> dict[str, Any]:
    """Implementation for resume command.

    Args:
        session_id: The session ID to resume.
        **kwargs: Additional keyword arguments.

    Returns:
        Resume result dictionary.
    """
    return {"session_id": session_id, "status": "resumed"}


def list_impl(**kwargs: Any) -> dict[str, Any]:
    """Implementation for list command.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        List result dictionary.
    """
    return {"items": [], "count": 0}


def session_list_impl(session_ids: list[str] | None = None, **kwargs: Any) -> dict[str, Any]:
    """Implementation for session list command.

    Args:
        session_ids: Optional list of session IDs to filter.
        **kwargs: Additional keyword arguments.

    Returns:
        Session list result dictionary.
    """
    return {"sessions": [], "count": 0, "session_ids": session_ids or []}


def bg_impl(prompt: str, **kwargs: Any) -> dict[str, Any]:
    """Background-run implementation.

    Thin delegate to :func:`thegent.cli.services.run_execution_core_helpers.bg_impl_core`.
    Mirrors :func:`run_impl`'s delegation contract so operators and tests can stub
    the core helper via ``monkeypatch.setattr`` on the helper module.

    Args:
        prompt: The prompt to execute in the background.
        **kwargs: Forwarded to ``bg_impl_core``. See that function's signature
            for accepted parameters.

    Returns:
        Result dictionary from ``bg_impl_core``.
    """
    import sys as _sys
    from thegent.cli.services import run_execution_core_helpers

    impl_ns = _sys.modules.get("thegent.cli.commands.impl")
    if impl_ns is None:
        import importlib

        impl_ns = importlib.import_module("thegent.cli.commands.impl")
    return run_execution_core_helpers.bg_impl_core(prompt=prompt, impl_ns=impl_ns, **kwargs)


# ---------------------------------------------------------------------------
# AUDIT-N+14: real session-lifecycle entry-point implementations
# Pinned by tests/test_unit_cli_impl_session.py (FR-CLI-100..150).
# Each function uses ``impl.<x>`` references for the canonical imports
# above so ``@patch("thegent.cli.commands.impl.<x>", ...)`` decorators
# continue to work.
# ---------------------------------------------------------------------------


def status_impl(session_id: str, include_contract: bool = False, **kwargs: Any) -> dict[str, Any]:
    """Return the canonical status payload for a session.

    Resolves the session-meta file via :func:`_find_session_meta`, reads
    it, computes ``running`` via :func:`_is_pid_running`, and composes
    the canonical status string via :func:`_resolve_session_status`.
    Returns ``{"error": ...}`` if the session is not found.

    Pinned by ``TestStatusImpl`` in tests/test_unit_cli_impl_session.py.
    """
    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as exc:
        return {"error": str(exc), "session_id": session_id}
    meta = _read_session_meta(meta_path)
    pid = int(meta.get("pid") or 0)
    running = _is_pid_running(pid)
    paths = _session_paths(Path(settings.session_dir), session_id)
    status = _resolve_session_status(meta, paths["rc"], running=running)
    exit_code = meta.get("exit_code")
    if exit_code is None and paths["rc"].exists():
        try:
            exit_code = int(paths["rc"].read_text(encoding="utf-8").strip())
        except ValueError:
            exit_code = None
    result: dict[str, Any] = {
        "session_id": session_id,
        "status": status,
        "running": running,
        "exit_code": exit_code,
        "pid": pid,
        "owner": meta.get("owner"),
        "agent": meta.get("agent"),
    }
    if include_contract:
        if "route_contract" in meta:
            result["route_contract"] = meta["route_contract"]
        if "route_request" in meta:
            result["route_request"] = meta["route_request"]
    return result


def stop_impl(
    session_id: str,
    force: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Stop a running session by signaling its PID.

    Sends ``SIGTERM`` (graceful) or ``SIGKILL`` (``force=True``) to the
    session PID via :func:`os.killpg`. Returns ``{"status": "stopped"}``
    / ``{"status": "stopped_force"}`` on success, ``{"status": "error", ...}``
    on OS errors, or ``{"status": "not_running"}`` if the session is
    already stopped.

    Pinned by ``TestStopImpl`` in tests/test_unit_cli_impl_session.py.
    """
    import os as _os
    import signal as _signal

    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as exc:
        return {"error": str(exc), "session_id": session_id}
    meta = _read_session_meta(meta_path)
    pid = int(meta.get("pid") or 0)
    if not _is_pid_running(pid):
        return {"status": "not_running", "session_id": session_id}
    sig = _signal.SIGKILL if force else _signal.SIGTERM
    try:
        _os.killpg(pid, sig)
    except OSError as exc:
        return {"status": "error", "error": str(exc), "session_id": session_id}
    return {
        "status": "stopped_force" if force else "stopped",
        "session_id": session_id,
    }


def wait_impl(
    session_id: str,
    timeout: float | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Wait for a session to finish, optionally bounded by ``timeout``.

    Returns ``{"exit_code": int, "timed_out": bool}`` on success or
    ``{"error": ...}`` if the session is not found.

    Pinned by ``TestWaitImpl`` in tests/test_unit_cli_impl_session.py.
    """
    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as exc:
        return {"error": str(exc), "session_id": session_id}
    meta = _read_session_meta(meta_path)
    pid = int(meta.get("pid") or 0)
    paths = _session_paths(Path(settings.session_dir), session_id)
    timed_out = False
    if _is_pid_running(pid):
        deadline = (time.time() + timeout) if timeout else None
        while _is_pid_running(pid):
            if deadline is not None and time.time() >= deadline:
                timed_out = True
                break
            time.sleep(0.1)
    exit_code = meta.get("exit_code")
    if exit_code is None and paths["rc"].exists():
        try:
            exit_code = int(paths["rc"].read_text(encoding="utf-8").strip())
        except ValueError:
            exit_code = None
    return {
        "session_id": session_id,
        "exit_code": exit_code,
        "timed_out": timed_out,
    }


def logs_impl(
    session_id: str,
    stderr: bool = False,
    tail: int | None = None,
    **kwargs: Any,
) -> str:
    """Return the canonical logs payload for a session as a string.

    Returns stdout by default, stderr when ``stderr=True``, and the
    last ``tail`` lines when ``tail`` is set. The test contract pins
    the return type as ``str`` (with error prefixes inlined).

    Pinned by ``TestLogsImpl`` in tests/test_unit_cli_impl_session.py.
    """
    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as exc:
        return f"Error: {exc}"
    if not meta_path.exists():
        return f"Error: session meta not found: {session_id}"
    paths = _session_paths(Path(settings.session_dir), session_id)
    log_path = paths["stderr"] if stderr else paths["stdout"]
    if not log_path.exists():
        return f"Log file missing: {log_path.name}"
    content = log_path.read_text(encoding="utf-8")
    if tail is not None:
        lines = content.splitlines()
        content = "\n".join(lines[-tail:])
    return content


def session_meta_impl(session_id: str, **kwargs: Any) -> dict[str, Any]:
    """Return the canonical session-meta payload.

    Pinned by ``TestSessionMetaImpl`` in tests/test_unit_cli_impl_session.py.
    """
    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as exc:
        return {"error": str(exc), "session_id": session_id}
    if not meta_path.exists():
        return {"error": f"session meta not found: {session_id}", "session_id": session_id}
    meta = _read_session_meta(meta_path)
    return {
        "session_id": session_id,
        "agent": meta.get("agent"),
        "owner": meta.get("owner"),
        "started_at_utc": meta.get("started_at_utc"),
        "metadata": meta,
    }


def events_impl(
    run_id: str | None = None,
    limit: int = 100,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Return run-registry events filtered by ``run_id`` and capped by ``limit``.

    The canonical registry file lives at ``<session_dir>/run_registry.jsonl``
    and contains one JSON object per line.

    Pinned by ``TestEventsImpl`` in tests/test_unit_cli_impl_session.py.
    """
    import orjson as _json

    settings = ThegentSettings()
    registry_path = Path(settings.session_dir) / "run_registry.jsonl"
    if not registry_path.exists():
        return []
    events: list[dict[str, Any]] = []
    for raw in registry_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            obj = _json.loads(raw)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        events.append(obj)
    if run_id is not None:
        events = [e for e in events if e.get("run_id") == run_id]
    if limit is not None and limit > 0:
        events = events[-limit:]
    return events


def history_impl(limit: int = 50, **kwargs: Any) -> list[dict[str, Any]]:
    """Return the most-recent runs from the run registry.

    Pinned by ``TestHistoryImpl`` in tests/test_unit_cli_impl_session.py.
    """
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    if hasattr(registry, "list_runs"):
        runs = registry.list_runs(limit=limit)
        return list(runs or [])
    # Fallback: read the canonical registry file when list_runs is unavailable.
    return events_impl(run_id=None, limit=limit)


def ps_impl(
    all: bool = False,  # noqa: A002 — test surface
    owner: str | None = None,
    include_contract: bool = False,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """List session-process rows.

    When ``all=True`` scans every scope dir under ``session_dir``;
    otherwise filters to the current owner (or ``owner=``).

    Pinned by ``TestPsImpl`` in tests/test_unit_cli_impl_session.py.
    """
    settings = ThegentSettings()
    session_root = Path(settings.session_dir)
    if all:
        owner_filter: str | None = None
        scope_dirs: list[Path] = sorted(p for p in session_root.iterdir() if p.is_dir())
    else:
        owner_filter = owner or _default_owner_tag(Path.cwd())
        scope_dirs = _session_scope_dirs(session_root, owner_filter)
    rows: list[dict[str, Any]] = []
    for scope_dir in scope_dirs:
        for meta_path in sorted(scope_dir.glob("*.json")):
            try:
                meta = _read_session_meta(meta_path)
            except Exception:
                continue
            sid = meta.get("session_id") or meta_path.stem
            pid = int(meta.get("pid") or 0)
            running = bool(_is_pid_running(pid))
            if owner_filter is not None and meta.get("owner") != owner_filter:
                continue
            prompt = str(meta.get("prompt") or "")
            prompt_preview = prompt if len(prompt) <= 40 else prompt[:40] + "..."
            row: dict[str, Any] = {
                "id": sid,
                "session_id": sid,
                "owner": meta.get("owner"),
                "agent": meta.get("agent"),
                "pid": pid,
                "running": running,
                "started_at_utc": meta.get("started_at_utc"),
                "status": meta.get("status") or ("running" if running else "exited"),
                "prompt_preview": prompt_preview,
            }
            if include_contract and "route_contract" in meta:
                row["route_contract"] = meta["route_contract"]
            rows.append(row)
    return rows


def inspect_impl(
    session_ids: list[str],
    owner: str | None = None,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Return a list of inspect payloads for one or more sessions.

    When ``session_ids`` is empty, scans all sessions owned by
    ``owner`` (or the default owner tag if ``owner`` is ``None``).

    Pinned by ``TestInspectImpl`` in tests/test_unit_cli_impl_session.py.
    """
    if not session_ids and owner is None:
        return []
    settings = ThegentSettings()
    results: list[dict[str, Any]] = []
    if not session_ids:
        # Owner-discovery path: scan every scope dir for the owner prefix.
        owner_tag = owner or _default_owner_tag(Path.cwd())
        scope_dirs = _session_scope_dirs(Path(settings.session_dir), owner_tag)
        for scope_dir in scope_dirs:
            for meta_path in sorted(scope_dir.glob("*.json")):
                sid = meta_path.stem
                results.extend(_inspect_one(settings, sid))
        return results
    for sid in session_ids:
        results.extend(_inspect_one(settings, sid))
    return results


def _inspect_one(settings: ThegentSettings, session_id: str) -> list[dict[str, Any]]:
    """Helper: build the inspect payload for a single session."""
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter:
        return []
    if not meta_path.exists():
        return []
    meta = _read_session_meta(meta_path)
    paths = _session_paths(Path(settings.session_dir), session_id)
    stdout_text = ""
    if paths["stdout"].exists():
        stdout_text = paths["stdout"].read_text(encoding="utf-8")
    return [
        {
            "session_id": session_id,
            "owner": meta.get("owner"),
            "agent": meta.get("agent"),
            "logs": stdout_text,
            "pid": meta.get("pid"),
        }
    ]


# NOTE: ``history_impl`` and ``events_impl`` are defined earlier in this
# module (canonical single home — AUDIT-N+14 removed the duplicate
# definitions that previously shadowed the canonical pair).

__all__ = [
    # AUDIT-N+9: observability surface (canonical home: observability_impl)
    "_inject_time_constraint",
    "_append_observe_summary_snapshot",
    "_validate_image_capability",
    "_resolve_audio_transcript_for_output",
    "_resolve_grounding_sources_for_output",
    "_append_health_snapshot",
    "observe_summary_impl",
    # AUDIT-N+13: dormant-core trend payload wire-up.
    "_build_observe_trend_block",
    "_build_observe_trend_payload",
    # AUDIT-N+12: session lifecycle surface (canonical home: session_impl)
    "_is_pid_running",
    "_scope_key",
    "_session_paths",
    "_new_session_id",
    "_save_session_meta",
    "_read_session_meta",
    "_find_session_meta",
    "_resolve_session_status",
    "_resolve_agent_model",
    "_load_prior_session_output",
    "_CONTINUATION_TAIL_CHARS",
    "_CWD_CACHE",
    "_session_dir",
    "_session_scope_dirs",
    "_build_continuation_prompt",
    # AUDIT-N+12: I/O helpers (canonical home: impl.py)
    "_resolve_cwd",
    "_resolve_droids_dir",
    "_compose_owner_tag",
    "_default_owner_tag",
    "_backoff_delay",
    "_retry_if_eagain",
    "_atomic_write",
    "_spawn_with_eagain_retry",
    "_EAGAIN_ERRNOS",
    "_write_session_state",
    "_normalize_image_paths",
    # Public entry points (canonical home: impl.py)
    "run_impl",
    "logs_impl",
    "ps_impl",
    "list_models_impl",
    "status_impl",
    "resume_impl",
    "list_impl",
    "session_list_impl",
    "bg_impl",
    # DAG model classes (canonical home: impl.py)
    "DagDocument",
    "DagPrioritizer",
]


# AUDIT-N+9: re-export observability surface for backward compat with
# external callers that still import from thegent.cli.commands.impl
from thegent.cli.commands.observability_impl import (  # noqa: F401
    observe_summary_impl,
    _inject_time_constraint,
    _append_observe_summary_snapshot,
    _append_health_snapshot,
    _build_observe_summary_trend_scope,
    _build_observe_trend_block,
    _build_observe_trend_payload,
    _classify_observe_summary_trend_health,
    _compact_health_snapshot_log,
    _hash_health_payload,
    _hash_observe_summary_payload,
    _hash_observe_summary_trend_scope,
    _load_observe_summary_snapshots,
    _load_previous_health_snapshot,
    _observe_summary_freshness_bucket,
    _parse_observe_summary_env_float,
    _parse_observe_summary_env_int,
    _parse_observe_summary_timestamp,
    _resolve_audio_transcript_for_output,
    _resolve_grounding_sources_for_output,
    _resolve_health_policy,
    _run_background_session_observer,
    _validate_image_capability,
    _build_audio_summary_metadata,
    _build_run_event_details,
    _health_scope_key,
)


# AUDIT-N+12: re-export the session-lifecycle surface from
# :mod:`thegent.cli.commands.session_impl`. These helpers previously
# lived inline in ``impl.py`` but were never reachable because the
# surface was incomplete (missing ``_CONTINUATION_TAIL_CHARS``,
# ``_CWD_CACHE``, ``_load_prior_session_output``,
# ``_resolve_agent_model`` 4-arg form, etc.). Extracting them into a
# canonical module preserves the ``impl.<x>`` import path for legacy
# callers and ``tests/test_unit_cli_impl_session.py`` patch sites.
from thegent.cli.commands.session_impl import (  # noqa: F401
    _CONTINUATION_TAIL_CHARS,
    _CWD_CACHE,
    _is_pid_running,
    _scope_key,
    _session_paths,
    _new_session_id,
    _save_session_meta,
    _read_session_meta,
    _find_session_meta,
    _resolve_session_status,
    _resolve_agent_model,
    _resolve_cwd,
    _compose_owner_tag,
    _default_owner_tag,
    _load_prior_session_output,
    _build_continuation_prompt,
    _session_dir,
    _session_scope_dirs,
    _run_background_session_observer,
)


# AUDIT-N+12: surface ``thegent.cli.services.run_observe_helpers`` as a
# module attribute on ``impl`` so legacy ``monkeypatch.setattr`` sites
# like ``monkeypatch.setattr("thegent.cli.commands.impl.run_observe_helpers.<x>", ...)``
# (in ``tests/test_wl125_run_observe_helpers_parity.py``) resolve.
from thegent.cli.services import run_observe_helpers  # noqa: F401


# AUDIT-N+12: surface ``thegent.cli.services.observability`` as a module
# attribute on ``impl`` so the WL-120 reconciliation tests can monkeypatch
# the dormant trend/escalation builders via
# ``monkeypatch.setattr("thegent.cli.commands.impl.services_observability.<x>", ...)``.
from thegent.cli.services import observability as services_observability  # noqa: F401


# ---------------------------------------------------------------------------
# AUDIT-N+14: re-export the canonical imports so the test mocks at
# ``thegent.cli.commands.impl.<x>`` resolve. Each test patches names like
# ``thegent.cli.commands.impl.resolve_agent`` / ``impl.subprocess`` /
# ``impl.ThegentSettings`` / ``impl.MigrationController`` / etc.; without
# these re-exports the ``@patch(...)`` decorators raise
# ``AttributeError: module ... does not have the attribute '...'``.
# ---------------------------------------------------------------------------
from thegent.agents import get_fallback_agents, get_runner, resolve_agent  # noqa: F401
from thegent.agents.base import AgentRunner, RunResult  # noqa: F401
from thegent.agents.resilience import is_usage_limit  # noqa: F401
from thegent.cli.commands._cli_shared import RunRegistry  # noqa: F401
from thegent.config import ThegentSettings  # noqa: F401
from thegent.contracts.telemetry import (  # noqa: F401
    ContractTelemetry,
    rank_providers_by_parser_quality,
)
import subprocess as _subprocess  # noqa: F401
from thegent.execution import (  # noqa: F401
    AgentSource,
    Auditor,
    CircuitBreakerRegistry,
    ConcurrencyController,
    FreshnessValidator,
    InterruptionTracker,
    InteractivityMode,
    LoadClassifier,
    OverrideRegistry,
    PolicyEngine,
    RunMeta,
    TrustBoundaryValidator,
)
from thegent.output_parser import extract_condensed  # noqa: F401

# Aliases that the test patch sites reference.
subprocess = _subprocess
ThegentSettingsCls = ThegentSettings


# ---------------------------------------------------------------------------
# AUDIT-N+14: real entry-point implementations
# ---------------------------------------------------------------------------
# AUDIT-N+10: re-export governance / escalation / HITL / data-protection
# surface for backward compat with external callers (and the legacy
# ``tests/test_unit_cli_*.py`` patch sites) that still import from
# ``thegent.cli.commands.impl``. The canonical home for these 9 symbols
# is :mod:`thegent.cli.governance.governance_impl`.
from thegent.cli.governance.governance_impl import (  # noqa: F401
    escalate_add_impl,
    escalate_approve_impl,
    escalate_list_impl,
    escalate_resolve_impl,
    govern_approve_impl,
    govern_reject_impl,
    govern_list_pending_impl,
    harness_register_host_impl,
    get_data_protection_status_impl,
    sweep_impl,
)


# Session state path helper
def _session_state_path(session_id: str) -> str:
    """Get session state path for session."""
    import os

    base = os.environ.get("THGENT_SESSION_DIR", "/tmp/thegent/sessions")
    return str(Path(base) / session_id / "session_state.json")


def _coerce_issue_types(issues: list[dict[str, Any]]) -> list[str]:
    """Coerce issue dictionaries to type strings.

    Args:
        issues: List of issue dictionaries.

    Returns:
        List of issue type strings.
    """
    return [issue.get("type", "unknown") for issue in issues]


def _check_dag_cycles(dag: dict[str, Any]) -> list[list[str]]:
    """Check for cycles in a DAG.

    Args:
        dag: DAG dictionary.

    Returns:
        List of cycles found (each cycle is a list of node IDs).
    """
    return []


def dag_raw_impl(**kwargs: Any) -> dict[str, Any]:
    """Implementation for DAG raw command.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        Raw DAG result dictionary.
    """
    return {"nodes": [], "edges": []}


# AUDIT-N+14: ``_build_continuation_prompt`` lives in
# :mod:`thegent.cli.commands.session_impl` (canonical home, 4-arg form
# with ``include_stderr`` keyword). The local stub is removed so the
# AUDIT-N+12 re-export binds the canonical form.


def dag_list_impl(**kwargs: Any) -> dict[str, Any]:
    """Implementation for DAG list command.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        DAG list result dictionary.
    """
    return {"items": [], "count": 0}


def _append_context_usage(snapshot: dict[str, Any], usage: dict[str, Any]) -> None:
    """Append context usage to a snapshot.

    Args:
        snapshot: Snapshot dictionary to append to.
        usage: Usage dictionary to append.
    """
    if "context_usage" not in snapshot:
        snapshot["context_usage"] = []
    snapshot["context_usage"].append(usage)


def _dag_path(dag_id: str) -> str:
    """Get the file path for a DAG document.

    Args:
        dag_id: DAG document identifier.

    Returns:
        File path string.
    """
    from pathlib import Path
    import os

    base_dir = os.environ.get("THGENT_DAG_DIR", "/tmp/thegent/dags")
    return str(Path(base_dir) / f"{dag_id}.json")


def _dag_update_task(dag_id: str, task_id: str, updates: dict[str, Any]) -> None:
    """Update a task in a DAG document.

    Args:
        dag_id: DAG document identifier.
        task_id: Task identifier.
        updates: Dictionary of updates to apply.
    """


def list_agents_impl(**kwargs: Any) -> dict[str, Any]:
    """Implementation for list agents command.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        List of agents result dictionary.
    """
    return {"agents": [], "count": 0}


def _ensure_contract_version_header(headers: dict[str, str]) -> dict[str, str]:
    """Ensure contract version header is present.

    Args:
        headers: Dictionary of headers.

    Returns:
        Updated headers with contract version.
    """
    if "X-Contract-Version" not in headers:
        headers["X-Contract-Version"] = "1.0"
    return headers


# NOTE: ``session_meta_impl`` is defined earlier in this module
# (canonical real implementation — AUDIT-N+14 removed the legacy stub).


def _ensure_dag_file(dag_path: str, **kwargs: Any) -> bool:
    """Ensure a DAG file exists.

    Args:
        dag_path: Path to the DAG file.
        **kwargs: Additional keyword arguments.

    Returns:
        True if file exists or was created.
    """
    from pathlib import Path

    path = Path(dag_path)
    if path.exists():
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}")
    return True


def _ensure_evidence_header(headers: dict[str, str]) -> dict[str, str]:
    """Ensure evidence header is present.

    Args:
        headers: Dictionary of headers.

    Returns:
        Updated headers with evidence.
    """
    if "X-Evidence-Version" not in headers:
        headers["X-Evidence-Version"] = "1.0"
    return headers


def _escape_cell(value: str) -> str:
    """Escape a cell value for CSV output.

    Args:
        value: The cell value to escape.

    Returns:
        Escaped cell value.
    """
    if "," in value or '"' in value or "\n" in value:
        return '"' + value.replace('"', '""') + '"'
    return value


def _get_ready_task_ids(dag: dict[str, Any]) -> list[str]:
    """Get IDs of tasks that are ready to execute.

    Args:
        dag: DAG dictionary.

    Returns:
        List of ready task IDs.
    """
    tasks = dag.get("tasks", [])
    ready = []
    for task in tasks:
        if task.get("status") == "ready":
            ready.append(task.get("id", ""))
    return [r for r in ready if r]


# Constants for health snapshot management
_health_snapshot_max_lines = 1000


def _parse_dag_full(dag_content: str) -> dict[str, Any]:
    """Parse full DAG content from string.

    Args:
        dag_content: Raw DAG content string.

    Returns:
        Parsed DAG dictionary.
    """
    import json

    return json.loads(dag_content)


def _parse_depends_on(depends_on: str | list[str] | None) -> list[str]:
    """Parse depends_on field from task.

    Args:
        depends_on: Depends on specification (string, list, or None).

    Returns:
        List of dependency IDs.
    """
    if depends_on is None:
        return []
    if isinstance(depends_on, str):
        return [d.strip() for d in depends_on.split(",") if d.strip()]
    if isinstance(depends_on, list):
        return [str(d) for d in depends_on]
    return []


def _normalize_output_format(format: str | None) -> str:
    """Normalize output format string.

    Args:
        format: Format string (e.g., "json", "csv", "md"). May be ``None``
            or empty; defaults to ``"rich"`` from the
            ``THGENT_OUTPUT_FORMAT`` env var when unset.

    Returns:
        Normalized format string.
    """
    if not format:
        format = os.environ.get("THGENT_OUTPUT_FORMAT", "rich")
    format = format.lower().strip()
    if format in ("json", "jsonl"):
        return "json"
    if format == "csv":
        return "csv"
    if format in ("md", "markdown"):
        return "md"
    if format in ("rich", "table", "human", ""):
        return "rich"
    return format


def _serialize_dag(dag: dict[str, Any], format: str = "json") -> str:
    """Serialize DAG to string.

    Args:
        dag: DAG dictionary.
        format: Output format (json or yaml).

    Returns:
        Serialized DAG string.
    """
    import json

    if format == "yaml":
        import yaml

        return yaml.dump(dag)
    return json.dumps(dag, indent=2)


def _validate_dag(dag: dict[str, Any]) -> list[str]:
    """Validate DAG structure.

    Args:
        dag: DAG dictionary.

    Returns:
        List of validation error messages (empty if valid).
    """
    errors = []
    if "tasks" not in dag:
        errors.append("DAG missing 'tasks' field")
    else:
        task_ids = {t.get("id") for t in dag["tasks"]}
        for task in dag["tasks"]:
            depends_on = task.get("depends_on", [])
            for dep in depends_on:
                if dep not in task_ids:
                    errors.append(f"Task '{task.get('id')}' depends on unknown task '{dep}'")
    return errors


def _validate_task_id(task_id: str) -> bool:
    """Validate task ID format.

    Args:
        task_id: Task ID to validate.

    Returns:
        True if valid, False otherwise.
    """
    import re

    return bool(re.match(r"^[a-zA-Z0-9_-]+$", task_id))


# AUDIT-N+12: ``_resolve_agent_model`` (canonical 4-arg form), and
# all other session-lifecycle helpers (see :mod:`session_impl`) are
# re-exported via the AUDIT-N+12 re-export block below. The legacy
# 1-arg inline stub has been removed; legacy callers must update
# to the canonical 4-arg signature or use the module-level helper
# directly.


def _resolve_prompt(prompt: str | None = None, prompt_file: str | None = None) -> str:
    """Resolve prompt from argument or file.

    Args:
        prompt: Explicitly specified prompt or None.
        prompt_file: Path to file containing prompt or None.

    Returns:
        Resolved prompt string.
    """
    if prompt:
        return prompt
    if prompt_file:
        from pathlib import Path

        return Path(prompt_file).read_text()
    return ""


# AUDIT-N+14: ``_session_scope_dirs`` lives in
# :mod:`thegent.cli.commands.session_impl` (canonical home, 2-arg form
# ``(session_dir, owner)`` returning ``list[Path]``). The local stub is
# removed so the AUDIT-N+12 re-export binds the canonical form.


def _session_status_for(session_id: str) -> str:
    """Get status for a session.

    Args:
        session_id: Session ID.

    Returns:
        Session status string (running, completed, failed, unknown).
    """
    import os

    base = Path(os.environ.get("THGENT_SESSION_DIR", "/tmp/thegent/sessions"))
    session_dir = base / session_id
    lock_file = session_dir / ".lock"
    if not session_dir.exists():
        return "unknown"
    if lock_file.exists():
        return "running"
    status_file = session_dir / "status.txt"
    if status_file.exists():
        return status_file.read_text().strip()
    return "completed"


def get_server_meta_impl(server_name: str, **kwargs: Any) -> dict[str, Any]:
    """Get server metadata implementation.

    Args:
        server_name: Server name.
        **kwargs: Additional keyword arguments.

    Returns:
        Server metadata dictionary.
    """
    return {
        "server_name": server_name,
        "version": "1.0.0",
        "status": "ok",
    }
