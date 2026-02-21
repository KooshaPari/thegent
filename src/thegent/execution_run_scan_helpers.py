"""Helpers for scanning run registry JSONL lines."""

import json
from datetime import UTC, datetime
from typing import Any


def extract_session_id(line: str) -> str | None:
    """Extract session ID from a registry line."""
    try:
        data = json.loads(line)
        if data.get("status") == "started" or data.get("event") == "started":
            return data.get("correlation_id") or data.get("run_id")
    except Exception:
        pass
    return None


def extract_run_id(line: str) -> str | None:
    """Extract run ID from a registry line."""
    try:
        data = json.loads(line)
        return data.get("run_id")
    except Exception:
        pass
    return None


def update_run_state(line: str, run_id: str, current_state: Any, run_state_cls: Any) -> Any:
    """Update run state from a registry line."""
    try:
        data = json.loads(line)
        if data.get("run_id") != run_id:
            return current_state
        ev = data.get("event")
        if ev is None and data.get("status") == "started":
            return run_state_cls.RUNNING
        if ev == "finish":
            status = data.get("status", "")
            return run_state_cls.FAILED if status in ("failed", "timed_out") else run_state_cls.COMPLETED
        if ev == "pause":
            return run_state_cls.PAUSED
        if ev == "resume":
            return run_state_cls.RUNNING
    except Exception:
        pass
    return current_state


def process_run_entry(line: str, runs: dict[str, dict[str, Any]]) -> None:
    """Process a run entry and update the in-memory run map."""
    try:
        data = json.loads(line)
        rid = data.get("run_id")
        if not rid:
            return
        if data.get("event") == "finish":
            if rid in runs:
                runs[rid].update(data)
        else:
            runs[rid] = data
    except Exception:
        pass


def check_session_id(line: str, session_id: str) -> bool:
    """Check if a line matches the session ID."""
    try:
        data = json.loads(line)
        if data.get("correlation_id") == session_id or data.get("run_id") == session_id:
            return True
    except Exception:
        pass
    return False


def process_token_match(line: str, token: str, best: dict[str, Any] | None) -> dict[str, Any] | None:
    """Process a line for idempotency token matching."""
    try:
        data = json.loads(line)
        if data.get("idempotency_token") == token:
            rid = data.get("run_id")
            if data.get("event") == "finish":
                if best and best.get("run_id") == rid:
                    best.update(data)
            elif data.get("event") == "feedback":
                if best and best.get("run_id") == rid:
                    best["feedback_score"] = data.get("feedback_score")
            elif not best or data.get("started_at_utc", "") >= best.get("started_at_utc", ""):
                return data
    except Exception:
        pass
    return best


def process_calibration_entry(line: str, agent: str, runs: dict[str, dict[str, Any]]) -> None:
    """Process an entry for calibration calculation."""
    try:
        data = json.loads(line)
        rid = data.get("run_id")
        if not rid:
            return

        if data.get("event") == "finish":
            if rid in runs:
                runs[rid].update(data)
        elif data.get("event") == "feedback":
            if rid in runs:
                runs[rid]["feedback_score"] = data.get("feedback_score")
        elif data.get("agent") == agent:
            runs[rid] = data
    except Exception:
        pass


def extract_domain_tag(line: str) -> tuple[str | None, str | None]:
    """Extract run_id and domain_tag."""
    try:
        data = json.loads(line)
        return data.get("run_id"), data.get("domain_tag")
    except Exception:
        return None, None


def filter_expired_record(
    line: str,
    now: datetime,
    run_domains: dict[str, str],
    default_days: int,
    by_domain: dict[str, int],
) -> tuple[bool, str]:
    """Check if a record is expired. Returns (is_expired, line)."""
    try:
        data = json.loads(line)
        ts_str = data.get("timestamp") or data.get("started_at_utc")
        if not ts_str:
            return False, line

        ts = datetime.fromisoformat(ts_str)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC)

        rid = data.get("run_id")
        domain = run_domains.get(rid) if rid else data.get("domain_tag")
        days = by_domain.get(domain, default_days) if domain else default_days

        if (now - ts).days > days:
            return True, line

        return False, line
    except Exception:
        return False, line
