"""Observe-summary payload constants and trend helpers — split from observability_impl (WL-124)."""

from __future__ import annotations

import hashlib
import orjson as json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from phenotype_thegent_core.config import ThegentSettings

_log = logging.getLogger(__name__)


def _health_snapshot_log_path() -> Path:
    """Get the path to the health snapshot log file."""
    settings = ThegentSettings()
    raw = str(settings.health_snapshot_path) if settings.health_snapshot_path else ""
    path = Path(raw).expanduser() if raw else Path.home() / ".thegent" / "health-snapshots.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# --- Constants ---

OBSERVE_SUMMARY_SCHEMA_VERSION = "observe-summary-schema-v1"
OBSERVE_SUMMARY_PAYLOAD_TYPES = ("observe_summary",)

__all__ = [
    "OBSERVE_SUMMARY_PAYLOAD_TYPES",
    "OBSERVE_SUMMARY_SCHEMA_VERSION",
    "_build_observe_summary_trend_scope",
    "_classify_observe_summary_trend_health",
    "_hash_observe_summary_payload",
    "_hash_observe_summary_trend_scope",
    "_load_observe_summary_snapshots",
    "_observe_summary_freshness_bucket",
    "_parse_observe_summary_env_float",
    "_parse_observe_summary_env_int",
    "_parse_observe_summary_timestamp",
]


# --- Helper Functions ---


def _hash_observe_summary_payload(payload: dict[str, Any]) -> dict[str, str]:
    """Return a stable hash for an observe-summary payload."""
    payload_for_hash = {
        key: value for key, value in payload.items() if key not in {"generated_at_utc", "payload_signature"}
    }
    body = json.dumps(payload_for_hash, option=json.OPT_SORT_KEYS).decode()
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
    scope_key_json = json.dumps(scope_key, option=json.OPT_SORT_KEYS).decode()
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
        if (
            rec.get("trend_scope_signature") != scope_signature
            and rec.get("scope_signature") != scope_signature
            and rec.get("scope_key_json") != scope_key_json
        ):
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
    policy_signature = hashlib.sha256(json.dumps(policy, option=json.OPT_SORT_KEYS)).hexdigest()

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


def observe_summary_impl(
    cd: str | None = None,
    limit: int = 500,
    drift_window: int = 50,
    structural_budget_pct: float = 5.0,
    semantic_budget_pct: float = 10.0,
    provider: str | None = None,
    top_escalations: int = 10,
    trend_samples: int = 0,
    format: str | None = None,
) -> dict[str, Any]:
    """FR-X08: Unified observability summary (KPIs, drift, escalation)."""
    # Stub implementation - returns empty summary
    # The actual implementation needs to be added
    return {
        "summary": "observe_summary not fully implemented",
        "limit": limit,
        "drift_window": drift_window,
    }
