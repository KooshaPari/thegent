"""Session meta I/O, state contract, output format, and continuation helpers.

Extracted from session_impl.py as part of WL-120 LOC Reduction Program (Wave-3, W3-B2-split).
Contains:
- Session meta I/O: _read_session_meta, _save_session_meta, _find_session_meta
- Contract string helpers: _is_non_empty_contract_string, _normalize_contract_string
- Contract timestamp helper: _parse_contract_timestamp
- State contract helpers: _session_state_path, _write_session_state, _resolve_latest_session_id
- Output helpers: _normalize_output_format, _resolve_session_status
- Background observer: _run_background_session_observer
- Continuation helpers: _load_prior_session_output, _build_continuation_prompt
"""

from __future__ import annotations

import contextlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)

# Max chars from prior session to inject
_CONTINUATION_TAIL_CHARS = 8000
_CONTINUATION_STDERR_CHARS = 2000


# ---------------------------------------------------------------------------
# Session meta I/O helpers
# ---------------------------------------------------------------------------


def _read_session_meta(meta_path: Path) -> dict[str, Any]:
    if not meta_path.exists():
        raise typer.BadParameter(f"Session not found: {meta_path.stem}")
    return json.loads(meta_path.read_text(encoding="utf-8"))


def _save_session_meta(meta_path: Path, payload: dict[str, Any]) -> None:
    meta_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _is_non_empty_contract_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalize_contract_string(value: Any) -> str | None:
    if not _is_non_empty_contract_string(value):
        return None
    return value.strip()


def _parse_contract_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _find_session_meta(settings: ThegentSettings, session_id: str) -> Path:
    root = settings.session_dir.expanduser().resolve()
    candidate = root / f"{session_id}.json"
    if candidate.exists():
        return candidate
    matches = sorted(root.glob(f"*/{session_id}.json"))
    if matches:
        return matches[0]
    raise typer.BadParameter(f"Session not found: {session_id}")


def _session_state_path(settings: ThegentSettings, session_id: str) -> Path:
    """Stable WL-110 state contract path for a session."""
    return settings.session_dir.expanduser().resolve() / session_id / "state.json"


def _write_session_state(
    *,
    settings: ThegentSettings,
    session_id: str,
    run_id: str,
    agent: str | None,
    model: str | None,
    cwd: Path,
) -> Path:
    """Persist stable session state contract for resume flows."""
    state_path = _session_state_path(settings, session_id)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "session_id": session_id,
        "run_id": run_id,
        "agent": agent,
        "model": model,
        "cwd": str(cwd),
        "status": "running",
        "updated_at_utc": datetime.now(UTC).isoformat(),
    }
    state_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state_path


def _resolve_latest_session_id(settings: ThegentSettings) -> str:
    """Resolve most-recent resumable session from state contracts first."""
    root = settings.session_dir.expanduser().resolve()
    latest_state: tuple[datetime, str] | None = None
    for state_path in sorted(root.glob("*/state.json")):
        try:
            payload = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        session_id = _normalize_contract_string(payload.get("session_id"))
        run_id = _normalize_contract_string(payload.get("run_id"))
        updated_raw = payload.get("updated_at_utc", "")
        if session_id is None or run_id is None:
            continue
        updated = _parse_contract_timestamp(updated_raw)
        if updated is None:
            continue
        candidate = (updated, session_id)
        if latest_state is None or candidate > latest_state:
            latest_state = candidate
    if latest_state is not None:
        return latest_state[1]

    latest_meta: tuple[datetime, str] | None = None
    for meta_path in sorted(root.glob("*/*.json")):
        try:
            payload = _read_session_meta(meta_path)
        except Exception:
            continue
        session_id = payload.get("session_id")
        started_raw = payload.get("started_at_utc", "")
        if not isinstance(session_id, str) or not session_id:
            continue
        started = _parse_contract_timestamp(started_raw)
        if started is None:
            continue
        candidate = (started, session_id)
        if latest_meta is None or candidate > latest_meta:
            latest_meta = candidate
    if latest_meta is None:
        raise typer.BadParameter("No resumable session found.")
    return latest_meta[1]


def _normalize_output_format(requested: str | None = None, *, default: str = "rich") -> str:
    settings = ThegentSettings()
    value = (
        (requested or settings.output_format or default).strip().lower()
        if requested or settings.output_format
        else default.strip().lower()
    )
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
    settings = ThegentSettings()
    meta_path = str(settings.session_meta_path) if settings.session_meta_path else None
    rc_path = str(settings.session_rc_path) if settings.session_rc_path else None
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
    from thegent.utils.helpers import read_file_chunk

    from thegent.cli.services.session_path_helpers import session_paths as _session_paths_fn

    meta_path = _find_session_meta(settings, session_id)
    p = _session_paths_fn(base=meta_path.parent, session_id=session_id)
    parts: list[str] = []
    if p["stdout"].exists():
        size = p["stdout"].stat().st_size
        offset = max(0, size - _CONTINUATION_TAIL_CHARS)
        tail = read_file_chunk(p["stdout"], offset=offset)
        if tail:
            parts.append(tail)
    if include_stderr and p["stderr"].exists():
        size = p["stderr"].stat().st_size
        offset = max(0, size - _CONTINUATION_STDERR_CHARS)
        tail = read_file_chunk(p["stderr"], offset=offset)
        if tail:
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
