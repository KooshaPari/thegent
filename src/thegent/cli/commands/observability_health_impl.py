"""Health payload constants and helpers — split from observability_impl (WL-124)."""

from __future__ import annotations

import hashlib
<<<<<<< HEAD
import orjson as json
=======
import json
import logging
>>>>>>> fix/ci-remove-macos
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings

<<<<<<< HEAD
=======
_log = logging.getLogger(__name__)

# --- Constants ---

>>>>>>> fix/ci-remove-macos
HEALTH_PAYLOAD_SCHEMA_VERSION = "health-schema-v1"
HEALTH_PAYLOAD_TYPES = (
    "session_contract_health_gate",
    "session_contract_health_report",
    "session_contract_health_trend",
)
HEALTH_POLICY_PROFILES: dict[str, dict[str, Any]] = {
    "strict_ci": {"strict": True, "min_healthy_ratio": 1.0},
    "warn_only": {"strict": False, "min_healthy_ratio": 0.0},
    "prod_release": {"strict": True, "min_healthy_ratio": 0.98},
}

<<<<<<< HEAD
HEALTH_POLICY_PROFILES: dict[str, dict[str, Any]] = {
    "strict_ci": {"strict": True, "min_healthy_ratio": 1.0},
    "warn_only": {"strict": False, "min_healthy_ratio": 0.0},
    "prod_release": {"strict": True, "min_healthy_ratio": 0.98},
}
=======
__all__ = [
    "HEALTH_PAYLOAD_SCHEMA_VERSION",
    "HEALTH_PAYLOAD_TYPES",
    "HEALTH_POLICY_PROFILES",
    "_append_health_snapshot",
    "_coerce_issue_types",
    "_compact_health_snapshot_log",
    "_hash_health_payload",
    "_health_scope_key",
    "_health_snapshot_log_path",
    "_health_snapshot_max_lines",
    "_load_previous_health_snapshot",
    "_resolve_health_policy",
]


# --- Helper Functions ---
>>>>>>> fix/ci-remove-macos


def _hash_health_payload(payload: dict[str, Any]) -> dict[str, str]:
    """Return a stable hash for a health payload while ignoring timestamp/signature fields."""
    payload_for_hash = {
        key: value for key, value in payload.items() if key not in {"generated_at_utc", "payload_signature"}
    }
<<<<<<< HEAD
    body = json.dumps(payload_for_hash, sort_keys=True, separators=(",", ":").decode().decode())
=======
    body = json.dumps(payload_for_hash, sort_keys=True, separators=(",", ":"))
>>>>>>> fix/ci-remove-macos
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
    settings = ThegentSettings()
    raw = str(settings.health_snapshot_path) if settings.health_snapshot_path else ""
    path = Path(raw).expanduser() if raw else Path.home() / ".thegent" / "health-snapshots.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _health_snapshot_max_lines() -> int:
    settings = ThegentSettings()
    raw = str(settings.health_snapshot_max_lines)
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
    if isinstance(value, (list | tuple | set)):
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
<<<<<<< HEAD
            fh.write(json.dumps(rec, sort_keys=True).decode().decode())
=======
            fh.write(json.dumps(rec, sort_keys=True))
>>>>>>> fix/ci-remove-macos
            fh.write("\n")
    except OSError:
        return
    _compact_health_snapshot_log()
<<<<<<< HEAD


__all__ = [
    "HEALTH_PAYLOAD_SCHEMA_VERSION",
    "HEALTH_PAYLOAD_TYPES",
    "HEALTH_POLICY_PROFILES",
    "_append_health_snapshot",
    "_coerce_issue_types",
    "_compact_health_snapshot_log",
    "_hash_health_payload",
    "_health_scope_key",
    "_health_snapshot_log_path",
    "_health_snapshot_max_lines",
    "_load_previous_health_snapshot",
    "_resolve_health_policy",
]
=======
>>>>>>> fix/ci-remove-macos
