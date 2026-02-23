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
import orjson as json
import logging
from hashlib import sha256
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)

# Max chars from prior session to inject
_CONTINUATION_TAIL_CHARS = 8000
_CONTINUATION_STDERR_CHARS = 2000

__all__ = [
    "_build_continuation_prompt",
    "_find_session_meta",
    "_is_non_empty_contract_string",
    "_load_prior_session_output",
    "_normalize_contract_string",
    "_normalize_output_format",
    "_parse_contract_timestamp",
    "_read_session_meta",
    "_resolve_latest_session_id",
    "_resolve_session_status",
    "_run_background_session_observer",
    "_save_session_meta",
    "_session_state_path",
    "_write_session_state",
]


# ---------------------------------------------------------------------------
# Session meta I/O helpers
# ---------------------------------------------------------------------------


def _read_session_meta(meta_path: Path) -> dict[str, Any]:
    if not meta_path.exists():
        raise typer.BadParameter(f"Session not found: {meta_path.stem}")
    return json.loads(meta_path.read_text(encoding="utf-8"))


def _save_session_meta(meta_path: Path, payload: dict[str, Any]) -> None:
    meta_path.write_text(json.dumps(payload, indent=2, option=json.OPT_SORT_KEYS).decode() + "\n", encoding="utf-8")


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
    """Stable WL-110 state contract path for a session (read path with mirror fallback)."""
    primary = _primary_session_state_path(settings, session_id)
    if primary.exists():
        return primary
    mirror = _mirror_session_state_path(settings, session_id)
    if mirror.exists():
        return mirror
    return primary


def _primary_session_state_path(settings: ThegentSettings, session_id: str) -> Path:
    return settings.session_dir.expanduser().resolve() / session_id / "state.json"


def _state_mirror_root(settings: ThegentSettings) -> Path:
    return settings.session_dir.expanduser().resolve() / "_state_contracts"


def _mirror_session_state_path(settings: ThegentSettings, session_id: str) -> Path:
    return _state_mirror_root(settings) / f"{session_id}.json"


def _state_ledger_path(settings: ThegentSettings) -> Path:
    return settings.session_dir.expanduser().resolve() / "state_contract_ledger.jsonl"


def _state_payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, option=json.OPT_SORT_KEYS, separators=(",", ":").decode()).encode("utf-8")
    return sha256(encoded).hexdigest()


def _write_state_with_conflict_branch(path: Path, payload: dict[str, Any], *, branch_label: str) -> tuple[bool, str]:
    """Write payload and branch conflicting versions without deleting prior artifacts."""
    payload_text = json.dumps(payload, indent=2, option=json.OPT_SORT_KEYS).decode() + "\n"
    payload_hash = _state_payload_hash(payload)
    conflict_detected = False

    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            existing = None
        if isinstance(existing, dict):
            existing_hash = _state_payload_hash(existing)
            if existing_hash != payload_hash:
                conflict_detected = True
                ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
                stem = path.stem
                prev_path = path.parent / f"{stem}.conflict.{ts}.{branch_label}.prev.json"
                next_path = path.parent / f"{stem}.conflict.{ts}.{branch_label}.next.json"
                prev_path.write_text(json.dumps(existing, indent=2, option=json.OPT_SORT_KEYS).decode() + "\n", encoding="utf-8")
                next_path.write_text(payload_text, encoding="utf-8")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload_text, encoding="utf-8")
    return conflict_detected, payload_hash


def _write_session_state(
    *,
    settings: ThegentSettings,
    session_id: str,
    run_id: str,
    agent: str | None,
    model: str | None,
    cwd: Path,
) -> Path:
    """Persist stable session state contract for resume flows with dual-redundancy."""
    primary_path = _primary_session_state_path(settings, session_id)
    mirror_path = _mirror_session_state_path(settings, session_id)
    payload: dict[str, Any] = {
        "session_id": session_id,
        "run_id": run_id,
        "agent": agent,
        "model": model,
        "cwd": str(cwd),
        "status": "running",
        "updated_at_utc": datetime.now(UTC).isoformat(),
    }
    primary_conflict, payload_hash = _write_state_with_conflict_branch(primary_path, payload, branch_label="primary")
    mirror_conflict, _ = _write_state_with_conflict_branch(mirror_path, payload, branch_label="mirror")

    ledger_path = _state_ledger_path(settings)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_event = {
        "event_type": "state_contract_write",
        "session_id": session_id,
        "run_id": run_id,
        "updated_at_utc": payload["updated_at_utc"],
        "primary_path": str(primary_path),
        "mirror_path": str(mirror_path),
        "payload_hash": payload_hash,
        "conflict_detected": bool(primary_conflict or mirror_conflict),
    }
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ledger_event, option=json.OPT_SORT_KEYS).decode() + "\n")
    return primary_path


def _resolve_latest_session_id(settings: ThegentSettings) -> str:
    """Resolve most-recent resumable session from state contracts first."""
    root = settings.session_dir.expanduser().resolve()
    latest_state: tuple[datetime, str] | None = None
    candidates = sorted(root.glob("*/state.json")) + sorted(_state_mirror_root(settings).glob("*.json"))
    for state_path in candidates:
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
        except (OSError, ValueError) as exc:
            _log.warning("Failed to read exit code from rc path %s: %s", rc_path, exc)
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
        except Exception as exc:
            _log.warning("Failed to compute session duration for %s: %s", path, exc)
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
