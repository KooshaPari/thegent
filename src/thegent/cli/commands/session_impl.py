"""AUDIT-N+12 session lifecycle helpers.

Canonical home for the session-management helpers that previously lived
inline in :mod:`thegent.cli.commands.impl`. The session surface includes
PID liveness, scope key derivation, session-meta IO (read/save/find),
session-status resolution, model-resolution (extended 4-arg signature),
prior-session output loading (continuation tail), and the
session-directory / scope-directory helpers used by the public
``status_impl`` / ``logs_impl`` / ``ps_impl`` / ``inspect_impl`` /
``history_impl`` / ``events_impl`` / ``session_meta_impl`` /
``run_impl`` / ``bg_impl`` flow.

Pinned by :mod:`tests.test_unit_cli_impl_session` (FR-CLI-100..150) and
:mod:`tests.test_unit_audit_n12_session_impl_extraction_parity` (the new
AUDIT-N+12 envelope parity test).
"""

from __future__ import annotations

import errno
import getpass
import os
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer

from thegent.config import ThegentSettings


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# How many trailing characters of prior-session output to retain when
# building a continuation prompt. Pinned by
# ``tests/test_unit_cli_impl_session.py::TestLoadPriorSessionOutput``.
_CONTINUATION_TAIL_CHARS = 8_000

# Cache of resolved working directories, keyed by ``Path`` identity so
# repeated ``thegent run`` invocations from the same cwd skip the
# project-indicator scan.
_CWD_CACHE: dict[Path, Path | None] = {}


# ---------------------------------------------------------------------------
# PID liveness
# ---------------------------------------------------------------------------


def _is_pid_running(pid: int) -> bool:
    """Return True iff the given OS PID is alive and visible to us.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestIsPidRunning``.
    """
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError as exc:  # noqa: PERF203 - explicit errno check
        if exc.errno == errno.ESRCH:
            return False
        if exc.errno == errno.EPERM:
            # Process exists but we lack permission to signal it.
            return True
        return False
    return True


# ---------------------------------------------------------------------------
# Scope key derivation
# ---------------------------------------------------------------------------


def _scope_key(value: str) -> str:
    """Derive a filesystem-safe scope key from a free-form value.

    Replaces ``:`` ``/`` and whitespace with ``-``. Empty input returns
    an empty string (so callers can detect "no scope" cleanly).
    """
    if not value:
        return ""
    out = []
    for ch in value:
        if ch.isalnum() or ch in "._-":
            out.append(ch)
        else:
            out.append("-")
    return "".join(out)


# ---------------------------------------------------------------------------
# Session paths
# ---------------------------------------------------------------------------


def _session_paths(session_dir: Path, session_id: str) -> dict[str, Path]:
    """Return the canonical on-disk paths for a session.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestSessionPaths``.
    """
    return {
        "meta": session_dir / f"{session_id}.json",
        "stdout": session_dir / f"{session_id}.stdout.log",
        "stderr": session_dir / f"{session_id}.stderr.log",
        "rc": session_dir / f"{session_id}.rc",
        "in": session_dir / f"{session_id}.in",
    }


def _new_session_id(agent: str, owner: str) -> str:
    """Compose a new, unique session id of the form ``<agent>-<scope>-<uuid>``.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestNewSessionId``.
    """
    scope = _scope_key(owner) if owner else "anon"
    short = uuid.uuid4().hex[:8]
    return f"{agent}-{scope}-{short}"


# ---------------------------------------------------------------------------
# Session-meta IO
# ---------------------------------------------------------------------------


def _save_session_meta(meta_path: Path, payload: dict[str, Any]) -> None:
    """Persist session metadata atomically via JSON.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestReadSaveSessionMeta``.
    """
    import orjson as json

    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(payload).decode("utf-8"), encoding="utf-8")


def _read_session_meta(meta_path: Path) -> dict[str, Any]:
    """Read session metadata or raise :class:`typer.BadParameter` if missing.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestReadSaveSessionMeta``.
    """
    if not meta_path.exists():
        raise typer.BadParameter(f"Session not found: {meta_path}")
    import orjson as json

    return json.loads(meta_path.read_text(encoding="utf-8"))


def _find_session_meta(settings: ThegentSettings, session_id: str) -> Path:
    """Locate the session-meta file by direct lookup or scope-dir scan.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestFindSessionMeta``.
    """
    session_dir = Path(settings.session_dir)
    direct = session_dir / f"{session_id}.json"
    if direct.exists():
        return direct
    # Fallback: search every scope-dir for a matching id.
    if session_dir.exists():
        for meta_path in session_dir.glob(f"*/{session_id}.json"):
            return meta_path
    raise typer.BadParameter(f"Session not found: {session_id}")


# ---------------------------------------------------------------------------
# Session status resolution
# ---------------------------------------------------------------------------


def _resolve_session_status(
    meta: dict[str, Any],
    rc_path: Path,
    *,
    running: bool,
) -> str:
    """Compute the canonical session status string.

    Returns one of:
      * ``"running"``           — PID still alive.
      * ``"exited:<code>"``     — process exited cleanly with a code.
      * ``"exited"``            — exited but no code captured.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestResolveSessionStatus``.
    """
    if running:
        return "running"
    code = meta.get("exit_code")
    if code is not None:
        return f"exited:{code}"
    if rc_path.exists():
        try:
            code = int(rc_path.read_text(encoding="utf-8").strip())
        except ValueError:
            return "exited"
        return f"exited:{code}"
    return "exited"


# ---------------------------------------------------------------------------
# Agent model resolution (extended 4-arg signature)
# ---------------------------------------------------------------------------


# Hard-coded default model for agents whose settings don't carry a
# per-agent default. Pin test contracts.
_HARDCODED_AGENT_MODELS: dict[str, str] = {
    "minimax": "minimax-m2.5",
    "glm": "glm-5",
    "roo": "roo-default",
    "kilo": "kilo-default",
}

# Aliases that resolve to a single canonical agent key.
_AGENT_ALIASES: dict[str, str] = {
    "cursor-agent": "cursor",
    "cursor": "cursor",
    "antigravity": "antigravity",
}


def _resolve_agent_model(
    agent: str,
    model: str | None,
    mode: str,
    settings: ThegentSettings,
) -> str | None:
    """Resolve the model for ``agent`` given an optional explicit ``model``.

    Resolution order:
      1. Explicit ``model`` argument wins.
      2. ``settings.default_<agent>_model`` (or ``_high`` for codex full mode).
      3. Hard-coded fallback in :data:`_HARDCODED_AGENT_MODELS`.
      4. ``None`` for unknown agents.

    Pinned by
    ``tests/test_unit_cli_impl_session.py::TestResolveAgentModel`` (lines
    213-256) and ``::TestResolveAgentModelExtended`` (lines 1691-1739).
    """
    if model:
        return model
    canonical = _AGENT_ALIASES.get(agent, agent)

    if canonical == "codex":
        if mode == "full":
            high = getattr(settings, "default_codex_model_high", None)
            if high:
                return high
        return getattr(settings, "default_codex_model", None)
    if canonical == "claude":
        return getattr(settings, "default_claude_model", None)
    if canonical == "gemini":
        return getattr(settings, "default_gemini_model", None)
    if canonical == "copilot":
        return getattr(settings, "default_copilot_model", None)
    if canonical in ("cursor", "antigravity"):
        # Per-agent resolution: antigravity has its own default.
        attr = "default_cursor_model" if canonical == "cursor" else "default_antigravity_model"
        return getattr(settings, attr, None)
    return _HARDCODED_AGENT_MODELS.get(agent)


# ---------------------------------------------------------------------------
# Owner tag composition
# ---------------------------------------------------------------------------


def _compose_owner_tag(
    user: str,
    cwd: Path,
    scope: str | None = None,
) -> str:
    """Compose the canonical ``user:cwd[:scope]`` owner tag.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestOwnerTag``.
    """
    base = f"{user}:{cwd.name}"
    if scope:
        scope = scope.replace("{pid}", str(os.getpid())).replace("{cwd}", cwd.name)
        return f"{base}:{scope}"
    return base


def _default_owner_tag(cwd: Path) -> str:
    """Default owner tag from ``THGENT_OWNER_TAG`` / ``THGENT_OWNER_SCOPE`` env.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestOwnerTag``.
    """
    explicit = os.environ.get("THGENT_OWNER_TAG")
    if explicit:
        return explicit
    user = getpass.getuser()
    scope = os.environ.get("THGENT_OWNER_SCOPE")
    return _compose_owner_tag(user, cwd, scope=scope)


# ---------------------------------------------------------------------------
# Continuation prompt building
# ---------------------------------------------------------------------------


def _load_prior_session_output(
    settings: ThegentSettings,
    session_id: str,
    *,
    include_stderr: bool = False,
) -> str:
    """Load stdout (and optionally stderr) of a prior session for continuation.

    Truncates to ``_CONTINUATION_TAIL_CHARS`` to bound the prompt size.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestLoadPriorSessionOutput``.
    """
    paths = _session_paths(Path(settings.session_dir), session_id)
    stdout_text = ""
    if paths["stdout"].exists():
        stdout_text = paths["stdout"].read_text(encoding="utf-8")
    stderr_text = ""
    if include_stderr and paths["stderr"].exists():
        stderr_text = paths["stderr"].read_text(encoding="utf-8")
    combined = stdout_text
    if stderr_text:
        combined = f"{combined}\n[stderr]\n{stderr_text}" if combined else stderr_text
    if len(combined) > _CONTINUATION_TAIL_CHARS:
        combined = combined[-_CONTINUATION_TAIL_CHARS:]
    return combined


def _build_continuation_prompt(
    settings: ThegentSettings,
    continue_from: str,
    prompt: str,
    include_stderr: bool = False,
) -> str:
    """Build a continuation prompt that includes prior-session output.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestBuildContinuationPrompt``.
    """
    if not continue_from:
        return prompt
    prior_output = _load_prior_session_output(settings, continue_from, include_stderr=include_stderr)
    if not prior_output:
        return prompt
    return (
        f"Continuing from prior session {continue_from}.\n\n"
        f"--- previous output ---\n{prior_output}\n--- end previous output ---\n\n"
        f"{prompt}"
    )


# ---------------------------------------------------------------------------
# Session directory helpers
# ---------------------------------------------------------------------------


def _session_dir(settings: ThegentSettings, owner: str) -> Path:
    """Return (and create) the per-owner session directory.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestSessionDir``.
    """
    base = Path(settings.session_dir)
    owner_dir = base / _scope_key(owner)
    owner_dir.mkdir(parents=True, exist_ok=True)
    return owner_dir


def _session_scope_dirs(session_dir: Path, owner: str) -> list[Path]:
    """Return the list of session-scope dirs matching the owner prefix.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestSessionScopeDirs``.
    """
    if not owner or not session_dir.exists():
        return []
    prefix = _scope_key(owner)
    return sorted(
        p for p in session_dir.iterdir() if p.is_dir() and (p.name == prefix or p.name.startswith(f"{prefix}_"))
    )


# ---------------------------------------------------------------------------
# Working-directory resolution (with cache)
# ---------------------------------------------------------------------------


def _resolve_cwd(cwd: Path | None) -> Path | None:
    """Resolve the working directory, with caching.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestResolveCwd``.
    """
    if cwd is not None:
        expanded = cwd.expanduser()
        if not expanded.exists():
            raise typer.BadParameter(f"Directory does not exist: {cwd}")
        resolved = expanded.resolve()
        _CWD_CACHE[resolved] = resolved
        return resolved

    current = Path.cwd()
    if current in _CWD_CACHE:
        return _CWD_CACHE[current]

    for parent in [current, *current.parents]:
        if (parent / ".git").exists() or (parent / ".factory").exists() or (parent / "pyproject.toml").exists():
            _CWD_CACHE[current] = parent
            return parent

    _CWD_CACHE[current] = None
    return None


# ---------------------------------------------------------------------------
# Background-session observer (timeout/exit-code capture)
# ---------------------------------------------------------------------------


def _run_background_session_observer(exit_code: int, *, timed_out: bool = False) -> None:
    """Observer hook invoked from the backgrounded session wrapper.

    Reads ``THGENT_SESSION_META_PATH`` / ``THGENT_SESSION_RC_PATH`` from
    the env to update meta and rc files. No-op if env vars are unset.

    Pinned by ``tests/test_unit_cli_impl_session.py::TestRunBackgroundSessionObserver``.
    """
    meta_path_str = os.environ.get("THGENT_SESSION_META_PATH")
    if not meta_path_str:
        return
    meta_path = Path(meta_path_str)
    if meta_path.exists():
        import orjson as json

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
        meta["status"] = "exited"
        meta["exit_code"] = exit_code
        meta["timed_out"] = timed_out
        meta.setdefault("finished_at_utc", datetime.now(UTC).isoformat())
        meta_path.write_text(json.dumps(meta).decode("utf-8"), encoding="utf-8")
    rc_path_str = os.environ.get("THGENT_SESSION_RC_PATH")
    if rc_path_str:
        Path(rc_path_str).write_text(f"{exit_code}\n", encoding="utf-8")


__all__ = [
    "_CONTINUATION_TAIL_CHARS",
    "_CWD_CACHE",
    "_is_pid_running",
    "_scope_key",
    "_session_paths",
    "_new_session_id",
    "_save_session_meta",
    "_read_session_meta",
    "_find_session_meta",
    "_resolve_session_status",
    "_resolve_agent_model",
    "_compose_owner_tag",
    "_default_owner_tag",
    "_load_prior_session_output",
    "_build_continuation_prompt",
    "_session_dir",
    "_session_scope_dirs",
    "_resolve_cwd",
    "_run_background_session_observer",
]
