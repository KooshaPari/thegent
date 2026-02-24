"""Execution run metadata and registry for thegent orchestration."""

import orjson as json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from thegent.execution_coercion_helpers import as_bool as _as_bool_impl
from thegent.execution_coercion_helpers import as_float as _as_float_impl
from thegent.execution_coercion_helpers import as_int as _as_int_impl
from thegent.execution_event_builders import (
    build_feedback_event,
    build_finish_event,
    build_pause_event,
    build_resume_event,
    build_schema_marker_event,
)
from thegent.execution_hash_helpers import calculate_stable_record_hash
from thegent.execution_jsonl_parsers import parse_checkpoint_line, parse_checkpoint_by_id
from thegent.execution_run_scan_helpers import process_run_entry as _process_run_entry

_log = logging.getLogger(__name__)
_EXECUTION_WARNING_LIMIT = 3
_execution_warning_count = 0
_admission_import_warning_once: set[str] = set()
_execution_diagnostics: dict[str, Any] = {
    "optional_gate_import_failures": 0,
    "optional_gate_last_error_type": None,
    "optional_gate_last_error_message": None,
    "deadline_unregister": {
        "import_failures": 0,
        "runtime_failures": 0,
        "last_error_type": None,
        "last_error_message": None,
    },
    "message_parse": {
        "invalid_rows": 0,
        "non_pending_rows": 0,
        "last_error_type": None,
        "last_error_message": None,
    },
}


def _warn_bounded(message: str, *args: object) -> None:
    global _execution_warning_count
    _execution_warning_count += 1
    if _execution_warning_count <= _EXECUTION_WARNING_LIMIT:
        _log.warning(message, *args)


def get_execution_diagnostics() -> dict[str, Any]:
    """Return diagnostics snapshot for execution-path degradation."""
    return {
        "optional_gate_import_failures": _execution_diagnostics["optional_gate_import_failures"],
        "optional_gate_last_error_type": _execution_diagnostics["optional_gate_last_error_type"],
        "optional_gate_last_error_message": _execution_diagnostics["optional_gate_last_error_message"],
        "deadline_unregister": dict(_execution_diagnostics["deadline_unregister"]),
        "message_parse": dict(_execution_diagnostics["message_parse"]),
    }


def reset_execution_diagnostics() -> None:
    """Reset execution diagnostics (test helper)."""
    global _execution_warning_count
    _execution_warning_count = 0
    _admission_import_warning_once.clear()
    _execution_diagnostics["optional_gate_import_failures"] = 0
    _execution_diagnostics["optional_gate_last_error_type"] = None
    _execution_diagnostics["optional_gate_last_error_message"] = None
    _execution_diagnostics["deadline_unregister"] = {
        "import_failures": 0,
        "runtime_failures": 0,
        "last_error_type": None,
        "last_error_message": None,
    }
    _execution_diagnostics["message_parse"] = {
        "invalid_rows": 0,
        "non_pending_rows": 0,
        "last_error_type": None,
        "last_error_message": None,
    }


def _as_float(value: Any, default: float) -> float:
    """Coerce arbitrary values to float with a safe default."""
    return _as_float_impl(value, default)


def _as_int(value: Any, default: int) -> int:
    """Coerce arbitrary values to int with a safe default."""
    return _as_int_impl(value, default)


def _as_bool(value: Any, default: bool) -> bool:
    """Coerce arbitrary values to bool with a safe default."""
    return _as_bool_impl(value, default)


def _process_run_entry(line: str, runs: dict[str, dict[str, Any]]) -> None:
    """Process a single line from the registry file into a run entry."""
    try:
        entry = json.loads(line)
        run_id = entry.get("run_id") or entry.get("id")
        if run_id:
            runs[run_id] = entry
    except Exception:
        pass


def _check_session_id(line: str, session_id: str) -> bool:
    """Check if a line contains the given session_id."""
    try:
        entry = json.loads(line)
        return entry.get("session_id") == session_id
    except Exception:
        return False


from .state import RunState, RunMeta, CheckpointMeta, CalibrationRegistry

class RunRegistry:
    """Manages persistence and retrieval of execution runs.

    OPT-019: Uses bloom filter for fast negative lookups on session_id (O(1) session existence checks).
    """

    SCHEMA_VERSION = 1

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.registry_path = session_dir / "run_registry.jsonl"
        # OPT-019: Set-based fast negative lookups (O(1) session existence checks)
        self._bloom_filter: set[str] = set()
        self._last_hash_status: dict[str, Any] = {"status": "uninitialized", "error_type": None, "error_message": None}
        self._ensure_version_marker()

    def get_latest_session_id(self) -> str | None:
        """Return the correlation_id (or run_id) of the most recent started run."""
        if not self.registry_path.exists():
            return None
        latest: str | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                latest = _extract_session_id(line) or latest
        return latest

    def get_latest_run_id(self) -> str | None:
        """Return the run_id of the most recent run."""
        if not self.registry_path.exists():
            return None
        latest: str | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                latest = _extract_run_id(line) or latest
        return latest

    def _ensure_version_marker(self) -> None:
        """Write a version marker if the file is new."""
        if not self.registry_path.exists():
            self.session_dir.mkdir(parents=True, exist_ok=True)
            marker = build_schema_marker_event(self.SCHEMA_VERSION)
            marker["hash"] = self._calculate_hash(marker)
            with self.registry_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(marker).decode() + "\n")

    def _get_last_hash(self) -> str | None:
        """Return the hash of the last record in the registry."""
        if not self.registry_path.exists():
            self._last_hash_status = {
                "status": "empty_registry",
                "error_type": None,
                "error_message": None,
            }
            return None

        try:
            with self.registry_path.open("r", encoding="utf-8") as f:
                last_line = None
                for line in f:
                    if line.strip():
                        last_line = line
                if not last_line:
                    self._last_hash_status = {
                        "status": "empty_chain",
                        "error_type": None,
                        "error_message": None,
                    }
                    return None

                data = json.loads(last_line)
                if not isinstance(data, dict):
                    self._last_hash_status = {
                        "status": "invalid_record_type",
                        "error_type": "TypeError",
                        "error_message": f"expected object, got {type(data).__name__}",
                    }
                    _warn_bounded("RunRegistry._get_last_hash: invalid trailing record type=%s", type(data).__name__)
                    return None

                hash_value = data.get("hash")
                if hash_value is None:
                    self._last_hash_status = {
                        "status": "missing_hash",
                        "error_type": "KeyError",
                        "error_message": "trailing record missing hash",
                    }
                    return None

                self._last_hash_status = {
                    "status": "ok",
                    "error_type": None,
                    "error_message": None,
                }
                return str(hash_value)
        except json.JSONDecodeError as exc:
            self._last_hash_status = {
                "status": "malformed_record",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            _warn_bounded("RunRegistry._get_last_hash: malformed trailing record (%s)", type(exc).__name__)
            return None
        except OSError as exc:
            self._last_hash_status = {
                "status": "io_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            _warn_bounded("RunRegistry._get_last_hash: read failed (%s)", type(exc).__name__)
            return None
        return None

    def get_last_hash_status(self) -> dict[str, Any]:
        """Return status metadata for the last _get_last_hash call."""
        return dict(self._last_hash_status)

    def _calculate_hash(self, data: dict[str, Any]) -> str:
        """Calculate a stable hash for a record, excluding the hash itself."""
        return calculate_stable_record_hash(data)

    def register_start(self, run: RunMeta) -> None:
        """Record the start of a run with hash chaining."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        run.prev_hash = self._get_last_hash()
        data = run.model_dump()
        run.hash = self._calculate_hash(data)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(run.model_dump_json() + "\n")
        # OPT-019: Add session_id to set for fast negative lookups
        session_id = run.correlation_id or run.run_id
        if session_id:
            self._bloom_filter.add(session_id)

    def register_end(
        self,
        run_id: str,
        exit_code: int,
        status: str,
        ended_at_utc: str,
        duration_s: float,
        error_class: str | None = None,
        cost_usd: float | None = None,
        event_details: dict[str, Any] | None = None,
    ) -> None:
        """Update a run with completion metadata and hash chaining. G-GP-06: cost_usd optional."""
        event = build_finish_event(
            run_id=run_id,
            exit_code=exit_code,
            status=status,
            ended_at_utc=ended_at_utc,
            duration_s=duration_s,
            error_class=error_class,
            prev_hash=self._get_last_hash(),
            cost_usd=cost_usd,
            event_details=event_details,
        )
        event["hash"] = self._calculate_hash(event)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event).decode() + "\n")

    def register_feedback(self, run_id: str, score: float, note: str | None = None) -> None:
        """Record operator feedback for a run with hash chaining."""
        event = build_feedback_event(
            run_id=run_id,
            score=score,
            note=note,
            prev_hash=self._get_last_hash(),
        )
        event["hash"] = self._calculate_hash(event)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event).decode() + "\n")

    def register_pause(
        self,
        run_id: str,
        reason: str,
        continuity_snapshot: dict[str, Any] | None = None,
    ) -> None:
        """Record run pause for state-aware orchestration (G-KD-03)."""
        event = build_pause_event(
            run_id=run_id,
            reason=reason,
            continuity_snapshot=continuity_snapshot,
            prev_hash=self._get_last_hash(),
        )
        event["hash"] = self._calculate_hash(event)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event).decode() + "\n")

    def register_resume(self, run_id: str) -> None:
        """Record run resume for state-aware orchestration (G-KD-03)."""
        event = build_resume_event(run_id=run_id, prev_hash=self._get_last_hash())
        event["hash"] = self._calculate_hash(event)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event).decode() + "\n")

    def get_run_state(self, run_id: str) -> RunState | None:
        """Return current run state from registry events (G-KD-03)."""
        if not self.registry_path.exists():
            return None
        state: RunState | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                state = _update_run_state(line, run_id, state)
        return state

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        """List recent runs by parsing the registry."""
        if not self.registry_path.exists():
            return []

        runs: dict[str, dict[str, Any]] = {}
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                _process_run_entry(line, runs)

        # Sort by started_at_utc desc
        sorted_runs = sorted(runs.values(), key=lambda x: x.get("started_at_utc", ""), reverse=True)
        return sorted_runs[:limit]

    def session_exists(self, session_id: str) -> bool:
        """OPT-019: Fast negative lookup using bloom filter (O(1) session existence checks).

        Returns False if session definitely doesn't exist (bloom filter negative).
        Returns True if session might exist (requires full registry scan for confirmation).
        """
        # OPT-019: Fast negative lookup - if not in set, definitely doesn't exist
        if session_id not in self._bloom_filter:
            return False  # Definitely doesn't exist (set negative)
        # If in set, confirm with full registry scan
        return self._session_exists_in_registry(session_id)

    def _session_exists_in_registry(self, session_id: str) -> bool:
        """Check if session exists by scanning registry."""
        if not self.registry_path.exists():
            return False
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                if _check_session_id(line, session_id):
                    return True
        return False

    def find_by_token(self, token: str) -> dict[str, Any] | None:
        """Find the most recent run with a given idempotency token."""
        if not self.registry_path.exists():
            return None

        best: dict[str, Any] | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                best = _process_token_match(line, token, best)
        return best

    def get_calibration_factor(self, agent: str) -> float:
        """
        Calculate calibration factor (avg feedback / avg confidence) for an agent.
        G-GP-09: Checks CalibrationRegistry first for persisted factor.
        """
        cal = CalibrationRegistry(self.session_dir)
        factor = cal.get_factor(agent)
        if factor != 1.0:
            return factor

        if not self.registry_path.exists():
            return 1.0

        runs: dict[str, dict[str, Any]] = {}
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                _process_calibration_entry(line, agent, runs)

        relevant_runs = [r for r in runs.values() if r.get("feedback_score") is not None]
        if not relevant_runs:
            return 1.0

        avg_feedback = sum(float(r["feedback_score"]) for r in relevant_runs) / len(relevant_runs)
        avg_confidence = sum(float(r.get("confidence") or 0.5) for r in relevant_runs) / len(relevant_runs)
        if avg_confidence == 0:
            return 1.0
        return min(2.0, max(0.5, avg_feedback / avg_confidence))

    def purge_expired(
        self,
        default_days: int,
        by_domain: dict[str, int],
        dry_run: bool = True,
    ) -> dict[str, int]:
        """
        WP-3006: Tiered retention purge (G-GP-07).
        Removes records exceeding retention period. Returns counts of kept/purged.
        """
        if not self.registry_path.exists():
            return {"kept": 0, "purged": 0}

        now = datetime.now(UTC)
        run_domains: dict[str, str] = {}
        kept_lines = []
        purged_count = 0

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                rid, domain = _extract_domain_tag(line)
                if rid and domain:
                    run_domains[rid] = domain

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                is_expired, checked_line = _filter_expired_record(line, now, run_domains, default_days, by_domain)
                if is_expired:
                    purged_count += 1
                else:
                    kept_lines.append(checked_line)

        if not dry_run and purged_count > 0:
            self.registry_path.write_text("".join(kept_lines), encoding="utf-8")

        return {"kept": len(kept_lines), "purged": purged_count}


class ChatEntry(BaseModel):
    """Structured chat message for session history (WP-9003)."""

    ts: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    role: str  # user, assistant, system, tool
    content: str
    tool_name: str | None = None
    tool_input: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatHistory:
    """Manages structured conversation history for a session (WP-9003)."""

    def __init__(self, chat_path: Path) -> None:
        self.chat_path = chat_path

    def append(self, entry: ChatEntry) -> None:
        """Append a new chat entry to the session log."""
        self.chat_path.parent.mkdir(parents=True, exist_ok=True)
        with self.chat_path.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")

    def load(self, limit: int | None = None) -> list[ChatEntry]:
        """Load chat history from the session log."""
        if not self.chat_path.exists():
            return []
        entries = []
        with self.chat_path.open("r", encoding="utf-8") as f:
            for line in f:
                entry = _parse_chat_line(line)
                if entry:
                    entries.append(entry)
        if limit:
            return entries[-limit:]
        return entries


class MessageEntry(BaseModel):
    """Pending message in the session queue (WP-9004)."""

    id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    ts: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    type: str = "reprompt"  # reprompt, command, system, interrupt
    sender: str = "user"
    content: str
    status: str = "pending"  # pending, delivered, processed, failed
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageRegistry:
    """Manages the pending message queue for a session (WP-9004)."""

    def __init__(self, messages_path: Path) -> None:
        self.messages_path = messages_path

    def push(self, entry: MessageEntry) -> None:
        """Add a message to the queue."""
        self.messages_path.parent.mkdir(parents=True, exist_ok=True)
        with self.messages_path.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")

    def list_pending(self) -> list[MessageEntry]:
        """List all pending messages in the queue."""
        if not self.messages_path.exists():
            return []
        entries = []
        with self.messages_path.open("r", encoding="utf-8") as f:
            for line in f:
                msg = _parse_message_line(line)
                if msg:
                    entries.append(msg)
        return entries

    def mark_processed(self, msg_id: str, status: str = "processed") -> None:
        """Mark a message as processed (appends an update event)."""
        # Since it's a JSONL queue, we append the update event
        # A more robust implementation would rewrite the file or use a separate state file
        update = {
            "id": msg_id,
            "status": status,
            "updated_at": datetime.now(UTC).isoformat(),
            "event": "update",
        }
        with self.messages_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(update).decode() + "\n")


class AuditEntry(BaseModel):
    """Audit trail entry for session actions (WP-9005)."""

    ts: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    action: str  # view, send, attach, stop, pause, resume
    actor: str
    session_id: str
    details: dict[str, Any] = Field(default_factory=dict)
    result: str = "success"  # success, denied, error


class AuditRegistry:
    """Manages the session audit trail (WP-9005)."""

    def __init__(self, audit_path: Path) -> None:
        self.audit_path = audit_path

    def record(self, entry: AuditEntry) -> None:
        """Record an action in the audit trail."""
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")


_LAST_POLL_MESSAGES_META: dict[str, Any] = {"status": "not_checked"}


class CheckpointRegistry:
    """Manages persistence and retrieval of state checkpoints."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.registry_path = session_dir / "checkpoint_registry.jsonl"

    def create_checkpoint(self, reason: str, dag_content: str, owner: str) -> CheckpointMeta:
        """Record a new checkpoint."""
        ckpt = CheckpointMeta(
            reason=reason,
            dag_content=dag_content,
            session_dir=str(self.session_dir),
            owner=owner,
        )
        self.session_dir.mkdir(parents=True, exist_ok=True)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(ckpt.model_dump_json() + "\n")
        return ckpt

    def list_checkpoints(self, limit: int = 20) -> list[dict[str, Any]]:
        """List recent checkpoints."""
        if not self.registry_path.exists():
            return []

        ckpts = []
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                ckpt = parse_checkpoint_line(line)
                if ckpt:
                    ckpts.append(ckpt)

        return sorted(ckpts, key=lambda x: x.get("created_at_utc", ""), reverse=True)[:limit]

    def get_checkpoint(self, checkpoint_id: str) -> dict[str, Any] | None:
        """Retrieve a specific checkpoint."""
        if not self.registry_path.exists():
            return None

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                data = parse_checkpoint_by_id(line, checkpoint_id)
                if data:
                    return data
        return None


def poll_session_messages(
    session_id: str | None = None,
    *,
    include_meta: bool = False,
) -> list[MessageEntry] | dict[str, Any]:
    """Poll for pending messages for the current session (WP-9004).

    If session_id is None, tries to read from THGENT_SESSION_ID env var (runtime value, not a setting).
    """
    global _LAST_POLL_MESSAGES_META  # noqa: PLW0603
    if session_id is None:
        # session_id is a runtime value, not a configuration setting
        # Keep using os.environ for runtime values that change per execution
        import os

        session_id = os.environ.get("THGENT_SESSION_ID")

    if not session_id:
        _LAST_POLL_MESSAGES_META = {"status": "missing_session_id"}
        missing_payload: dict[str, Any] = {"messages": [], "meta": dict(_LAST_POLL_MESSAGES_META)}
        return missing_payload if include_meta else []

    from thegent.cli.commands.impl import _find_session_meta
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
        msg_path = meta_path.parent / f"{session_id}.messages.jsonl"
        registry = MessageRegistry(msg_path)
        messages = registry.list_pending()
        _LAST_POLL_MESSAGES_META = {
            "status": "ok",
            "session_id": session_id,
            "pending_count": len(messages),
            "messages_path": str(msg_path),
        }
        ok_payload: dict[str, Any] = {"messages": messages, "meta": dict(_LAST_POLL_MESSAGES_META)}
        return ok_payload if include_meta else messages
    except FileNotFoundError as exc:
        _LAST_POLL_MESSAGES_META = {
            "status": "meta_missing",
            "session_id": session_id,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }
    except PermissionError as exc:
        _LAST_POLL_MESSAGES_META = {
            "status": "unreadable_messages",
            "session_id": session_id,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }
    except ValueError as exc:
        _LAST_POLL_MESSAGES_META = {
            "status": "parser_failure",
            "session_id": session_id,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }
    except OSError as exc:
        _LAST_POLL_MESSAGES_META = {
            "status": "io_failure",
            "session_id": session_id,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }

    empty_payload: dict[str, Any] = {"messages": [], "meta": dict(_LAST_POLL_MESSAGES_META)}
    return empty_payload if include_meta else []


def get_last_poll_session_messages_meta() -> dict[str, Any]:
    """Return diagnostics metadata for the latest poll_session_messages call."""
    return dict(_LAST_POLL_MESSAGES_META)


