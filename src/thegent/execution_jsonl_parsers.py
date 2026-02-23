"""JSONL parsing helpers used by execution registries."""

import importlib.util
import orjson as json
import logging
from datetime import UTC, datetime
from typing import Any

from thegent.config import ThegentSettings

_thegent_parser: Any = None
_log = logging.getLogger(__name__)
_native_parse_diagnostics: dict[str, Any] = {
    "total_failures": 0,
    "by_parser": {},
    "last_error_type": None,
    "last_error_message": None,
}


def _record_native_parse_failure(parser: str, exc: Exception) -> None:
    _native_parse_diagnostics["total_failures"] = int(_native_parse_diagnostics["total_failures"]) + 1
    by_parser = _native_parse_diagnostics["by_parser"]
    by_parser[parser] = int(by_parser.get(parser, 0)) + 1
    _native_parse_diagnostics["last_error_type"] = type(exc).__name__
    _native_parse_diagnostics["last_error_message"] = str(exc)
    _log.warning(
        "native_parser_failure",
        extra={
            "parser": parser,
            "error_type": type(exc).__name__,
            "error": str(exc),
        },
    )


def get_native_parse_diagnostics() -> dict[str, Any]:
    """Return snapshot of native parse diagnostics counters."""
    return {
        "total_failures": int(_native_parse_diagnostics["total_failures"]),
        "by_parser": dict(_native_parse_diagnostics["by_parser"]),
        "last_error_type": _native_parse_diagnostics["last_error_type"],
        "last_error_message": _native_parse_diagnostics["last_error_message"],
    }


def reset_native_parse_diagnostics() -> None:
    """Reset diagnostics counters (used by tests)."""
    _native_parse_diagnostics["total_failures"] = 0
    _native_parse_diagnostics["by_parser"] = {}
    _native_parse_diagnostics["last_error_type"] = None
    _native_parse_diagnostics["last_error_message"] = None


def _get_native_parser() -> Any:
    """Load the Rust parser extension when native parsing is enabled."""
    global _thegent_parser
    if _thegent_parser is not None:
        return _thegent_parser
    if not ThegentSettings().use_native_parser:
        return None
    for mod_path in ("thegent_parser.thegent_parser", "thegent_parser"):
        spec = importlib.util.find_spec(mod_path)
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _thegent_parser = mod
            return mod
    return None


def parse_checkpoint_by_id(line: str, checkpoint_id: str) -> dict[str, Any] | None:
    """Parse a checkpoint line and check if ID matches."""
    native = _get_native_parser()
    if native is not None and hasattr(native, "parse_checkpoint_by_id"):
        try:
            parsed = native.parse_checkpoint_by_id(line, checkpoint_id)
            if isinstance(parsed, dict):
                return parsed
        except Exception as exc:
            _record_native_parse_failure("parse_checkpoint_by_id", exc)
    try:
        data = json.loads(line)
        if data.get("checkpoint_id") == checkpoint_id:
            return data
    except Exception:
        pass
    return None


def parse_circuit_failure(
    line: str, target: str, category: str, now: datetime, window_s: int
) -> tuple[int, datetime | None]:
    """Parse a circuit breaker failure line."""
    native = _get_native_parser()
    if native is not None and hasattr(native, "parse_circuit_failure"):
        try:
            parsed = native.parse_circuit_failure(line, target, category, now.isoformat(), window_s)
            if isinstance(parsed, tuple) and len(parsed) == 2:
                count = int(parsed[0])
                ts_raw = parsed[1]
                ts = datetime.fromisoformat(ts_raw) if isinstance(ts_raw, str) and ts_raw else None
                return count, ts
        except Exception as exc:
            _record_native_parse_failure("parse_circuit_failure", exc)
    try:
        data = json.loads(line)
        if (
            data.get("target") == target
            and data.get("category", "agent") == category
            and data.get("event") == "failure"
        ):
            ts = datetime.fromisoformat(data.get("timestamp"))
            if (now - ts).total_seconds() < window_s:
                return 1, ts
    except Exception:
        pass
    return 0, None


def parse_override_unexpired(line: str, owner: str, now: datetime) -> bool:
    """Parse an override line and check if it's unexpired."""
    line = line.strip()
    if not line:
        return False
    native = _get_native_parser()
    if native is not None and hasattr(native, "parse_override_unexpired"):
        try:
            parsed = native.parse_override_unexpired(line, owner, now.isoformat())
            if isinstance(parsed, bool):
                return parsed
        except Exception as exc:
            _record_native_parse_failure("parse_override_unexpired", exc)
    try:
        data = json.loads(line)
        if data.get("owner") != owner:
            return False
        exp = data.get("expires_at_utc")
        if not exp:
            return False
        exp_dt = datetime.fromisoformat(exp)
        return now < exp_dt
    except Exception:
        return False


def parse_fatigue_line(line: str, now: datetime, window_s: int) -> int:
    """Parse a fatigue interruption line."""
    native = _get_native_parser()
    if native is not None and hasattr(native, "parse_fatigue_line"):
        try:
            parsed = native.parse_fatigue_line(line, now.isoformat(), window_s)
            return int(parsed)
        except Exception as exc:
            _record_native_parse_failure("parse_fatigue_line", exc)
    try:
        data = json.loads(line)
        ts = datetime.fromisoformat(data["timestamp"])
        if (now - ts).total_seconds() < window_s:
            return 1
    except Exception:
        pass
    return 0


def parse_dlq_item(line: str, status: str | None, run_id: str | None) -> dict[str, Any] | None:
    """Parse a single DLQ item with optional filtering."""
    native = _get_native_parser()
    if native is not None and hasattr(native, "parse_dlq_item"):
        try:
            parsed = native.parse_dlq_item(line, status, run_id)
            if isinstance(parsed, dict):
                return parsed
            return None
        except Exception as exc:
            _record_native_parse_failure("parse_dlq_item", exc)
    try:
        data = json.loads(line)
        if status and data.get("status") != status:
            return None
        if run_id and data.get("run_id") != run_id:
            return None
        return data
    except Exception:
        return None


def process_dlq_line(line: str, run_id: str, resolution: str) -> tuple[str, bool]:
    """Update a DLQ line for resolution handling."""
    try:
        data = json.loads(line)
        if data.get("run_id") == run_id and data.get("status") == "pending_review":
            data["status"] = resolution
            data["resolved_at"] = datetime.now(UTC).isoformat()
            return json.dumps(data).decode().decode(), True
        return json.dumps(data).decode().decode(), False
    except Exception:
        return line, False


def parse_checkpoint_line(line: str) -> dict[str, Any] | None:
    """Parse a checkpoint registry line."""
    native = _get_native_parser()
    if native is not None and hasattr(native, "parse_checkpoint_line"):
        try:
            parsed = native.parse_checkpoint_line(line)
            if isinstance(parsed, dict):
                return parsed
            return None
        except Exception as exc:
            _record_native_parse_failure("parse_checkpoint_line", exc)
    try:
        return json.loads(line)
    except Exception:
        return None
