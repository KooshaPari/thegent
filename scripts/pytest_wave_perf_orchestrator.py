#!/usr/bin/env python3
"""Pytest performance-wave orchestration helpers.

Commands:
- collect-tests: run deterministic `pytest --collect-only` and emit node-id artifact.
- xdist: run selected lane with deterministic crash-safe options and artifact capture.
- testmon-pilot: run pilot impact tests using pytest-testmon with shared cache flow.
- testmon-evaluate: compare pilot artifact against full baseline artifact.
- shard-plan: build deterministic time-aware shard assignments from history.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_XDIST_DIST = "loadscope"
DEFAULT_XDIST_CACHE_PREFIX = "xdist"
TESTMON_CACHE_PREFIX = "testmon"
DEFAULT_SHARD_CACHE_PREFIX = "shard"
DEFAULT_CACHE_VERSION: str = "v2"

DEFAULT_XDIST_DURATIONS_TTL_DAYS = 14
DEFAULT_TESTMON_DURATIONS_TTL_DAYS = 14
DEFAULT_SHARD_DURATIONS_TTL_DAYS = 14
DEFAULT_DURATIONS_LIMIT = 100_000

WORKER_CRASH_SIGNS = (
    "worker lost",
    "worker failure",
    "died unexpectedly",
    "terminated unexpectedly",
    "process exited with code",
    "exit code was",
)

SHARD_FORMULA = (
    "time-aware weighted greedy assignment using duration history then "
    "deterministic blake2b(test_id + ':' + seed) fallback"
)

COLLECT_ARTIFACT_SCHEMA_VERSION = "collect/v1"
SHARD_PLAN_SCHEMA_VERSION = "shard-plan/v2"
DURATION_CACHE_SCHEMA_VERSION = "duration-cache/v1"


@dataclass(frozen=True)
class PytestSummary:
    collected: int | None
    passed: int | None
    failed: int | None
    skipped: int | None
    deselected: int | None
    xpassed: int | None
    xfailed: int | None


@dataclass(frozen=True)
class PytestArtifact:
    timestamp: str
    command: list[str]
    command_fallback: list[str] | None
    return_code: int
    elapsed_seconds: float
    summary: PytestSummary
    collected: int | None
    executed: int | None
    fallback_recovery: bool
    fallback_return_code: int | None
    worker_crash: bool
    crash_signals: list[str]
    cache_dir: str | None
    xdist_enabled: bool
    extra: dict[str, object]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_cache_root() -> Path:
    return Path(os.getenv("THGENT_PYTEST_CACHE_DIR", ".cache/thegent/pytest")).resolve()


def _resolve_cache_root(raw_cache_root: str | None) -> Path:
    if raw_cache_root is None:
        return _default_cache_root()

    requested = Path(raw_cache_root)
    if requested.is_absolute():
        return requested.resolve()

    return (_default_cache_root() / requested).resolve()


def _resolve_cache_dir(raw_cache_root: str | None, raw_cache_dir: str | None, prefix: str) -> Path:
    cache_root = _resolve_cache_root(raw_cache_root)
    if raw_cache_dir is None:
        cache_dir = cache_root / prefix
    else:
        requested = Path(raw_cache_dir)
        if requested.is_absolute():
            cache_dir = requested
        else:
            cache_dir = cache_root / requested

    return (cache_dir / DEFAULT_CACHE_VERSION).resolve()


def _safe_int(raw: str | None) -> int | None:
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _safe_float(raw: object) -> float | None:
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if not (value >= 0.0):
        return None
    return value


def _parse_summary(text: str) -> PytestSummary:
    collected = None
    passed = None
    failed = None
    skipped = None
    deselected = None
    xpassed = None
    xfailed = None

    for line in text.splitlines():
        if not line.startswith("="):
            continue
        if " in " not in line:
            continue

        header = line.split(" in ", 1)[0].strip("= ")
        if not header:
            continue

        for token in header.split(","):
            token = token.strip()
            if not token:
                continue
            match = re.match(r"^(\d+)\s+(\w+)$", token)
            if not match:
                continue

            value = _safe_int(match.group(1))
            if value is None:
                continue

            if match.group(2) == "passed":
                passed = value
            elif match.group(2) == "failed":
                failed = value
            elif match.group(2) == "skipped":
                skipped = value
            elif match.group(2) == "deselected":
                deselected = value
            elif match.group(2) == "xpassed":
                xpassed = value
            elif match.group(2) == "xfailed":
                xfailed = value
            elif match.group(2) == "error":
                failed = value

    collection_match = re.search(r"(\d+)\s+items?", text)
    if collection_match is not None:
        collected = _safe_int(collection_match.group(1))

    return PytestSummary(
        collected=collected,
        passed=passed,
        failed=failed,
        skipped=skipped,
        deselected=deselected,
        xpassed=xpassed,
        xfailed=xfailed,
    )


def _parse_executed(summary: PytestSummary) -> int | None:
    values = [summary.passed, summary.failed, summary.skipped, summary.xpassed, summary.xfailed]
    if all(value is None for value in values):
        return None
    return sum(value for value in values if value is not None)


def _parse_collect_test_ids(text: str) -> list[str]:
    test_ids: list[str] = []
    for line in text.splitlines():
        node = line.strip()
        if not node:
            continue
        if node.startswith("="):
            continue
        if node.startswith("collected "):
            continue
        if node.startswith("ERROR"):
            continue
        if "::" not in node:
            continue
        test_ids.append(node)
    return list(dict.fromkeys(test_ids))


def _parse_durations(text: str) -> dict[str, float]:
    durations: dict[str, float] = {}
    pattern = re.compile(r"^\s*(\d+(?:\.\d+)?)\s+s(?:\s+(setup|call|teardown))?\s+(.+)$")
    for line in text.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        duration = _safe_float(match.group(1))
        test_id = match.group(3).strip()
        if duration is None or not test_id:
            continue
        previous = durations.get(test_id)
        if previous is None or duration > previous:
            durations[test_id] = duration
    return durations


def _duration_cache_path(cache_dir: Path) -> Path:
    return cache_dir / "duration-history.json"


def _read_duration_payload(cache_dir: Path) -> dict[str, object]:
    path = _duration_cache_path(cache_dir)
    if not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"invalid duration cache schema: {path}")
    return payload


def _load_duration_history(cache_dir: Path, ttl_days: int) -> dict[str, float]:
    payload = _read_duration_payload(cache_dir)
    entries = payload.get("samples")
    if not isinstance(entries, dict):
        return {}

    now = time.time()
    cutoff = now - (ttl_days * 24 * 60 * 60) if ttl_days > 0 else 0.0
    history: dict[str, float] = {}

    for test_id, data in entries.items():
        if not isinstance(test_id, str) or not test_id:
            continue
        if not isinstance(data, dict):
            continue

        observed = _safe_float(data.get("observed_at"))
        if observed is None or observed < cutoff:
            continue

        duration = _safe_float(data.get("duration"))
        if duration is None:
            continue

        history[test_id] = duration
    return history


def _update_duration_history(
    cache_dir: Path,
    new_durations: dict[str, float],
) -> tuple[dict[str, float], int]:
    observed_at = time.time()
    payload = _read_duration_payload(cache_dir)
    raw_samples = payload.get("samples", {})
    samples = raw_samples if isinstance(raw_samples, dict) else {}

    updated = 0
    for test_id, duration in new_durations.items():
        if not test_id or duration <= 0.0:
            continue
        existing = samples.get(test_id)
        observations = 0
        if isinstance(existing, dict):
            observations = _safe_int(existing.get("observations"))
            if observations is None or observations < 0:
                observations = 0

        samples[test_id] = {
            "duration": duration,
            "observed_at": observed_at,
            "observations": observations + 1,
        }
        updated += 1

    merged = {
        "schema_version": DURATION_CACHE_SCHEMA_VERSION,
        "updated_at": observed_at,
        "samples": samples,
    }
    cache_dir.mkdir(parents=True, exist_ok=True)
    _duration_cache_path(cache_dir).write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")

    return {test_id: value["duration"] for test_id, value in samples.items() if isinstance(value, dict) and _safe_float(value.get("duration")) is not None}, updated


def _run_pytest(command: list[str], env: dict[str, str]) -> tuple[subprocess.CompletedProcess[str], float, PytestSummary]:
    start = time.perf_counter()
    proc = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
    elapsed = round(time.perf_counter() - start, 3)
    summary = _parse_summary(f"{proc.stdout}\n{proc.stderr}")
    return proc, elapsed, summary


def _run_collect_tests(marker: str, output: Path, maxfail: int, tests: list[str]) -> int:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "--collect-only",
        "-m",
        marker,
        "--maxfail",
        str(maxfail),
        "-q",
        *tests,
    ]
    proc, elapsed, summary = _run_pytest(command, os.environ.copy())
    payload = {
        "schema_version": COLLECT_ARTIFACT_SCHEMA_VERSION,
        "timestamp": _now_iso(),
        "command": command,
        "marker": marker,
        "maxfail": maxfail,
        "test_paths": tests,
        "return_code": proc.returncode,
        "elapsed_seconds": elapsed,
        "collected": summary.collected,
        "items": _parse_collect_test_ids(f"{proc.stdout}\n{proc.stderr}"),
    }
    _write_json(output, payload)
    return proc.returncode


def _detect_worker_crash(stdout: str, stderr: str) -> list[str]:
    text = f"{stdout}\n{stderr}".lower()
    return [signal for signal in WORKER_CRASH_SIGNS if signal in text]


def _prune_cache(cache_dir: Path, max_days: int) -> list[str]:
    if max_days <= 0:
        return []

    now = time.time()
    ttl_seconds = max_days * 24 * 60 * 60
    removed: list[str] = []

    for target in sorted(cache_dir.rglob("*")):
        if not target.is_file():
            continue
        if now - target.stat().st_mtime <= ttl_seconds:
            continue
        removed.append(str(target))
        target.unlink()

    return removed


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _serialize_artifact(artifact: PytestArtifact) -> dict[str, object]:
    return {
        "timestamp": artifact.timestamp,
        "command": artifact.command,
        "command_fallback": artifact.command_fallback,
        "return_code": artifact.return_code,
        "elapsed_seconds": artifact.elapsed_seconds,
        "collected": artifact.collected,
        "executed": artifact.executed,
        "deselected": artifact.summary.deselected,
        "failed": artifact.summary.failed,
        "passed": artifact.summary.passed,
        "skipped": artifact.summary.skipped,
        "xpassed": artifact.summary.xpassed,
        "xfailed": artifact.summary.xfailed,
        "xdist_enabled": artifact.xdist_enabled,
        "fallback_recovery": artifact.fallback_recovery,
        "fallback_return_code": artifact.fallback_return_code,
        "worker_crash": artifact.worker_crash,
        "crash_signals": artifact.crash_signals,
        "cache_dir": artifact.cache_dir,
        "extra": artifact.extra,
    }


def _run_pytest_with_cache(
    command: list[str],
    cache_dir: Path,
    cache_ttl_days: int,
    env: dict[str, str],
) -> tuple[subprocess.CompletedProcess[str], float, PytestSummary, dict[str, float], int]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    command.append(f"--durations={DEFAULT_DURATIONS_LIMIT}")
    command.append("-q")

    proc, elapsed, summary = _run_pytest(command, env)
    durations = _parse_durations(f"{proc.stdout}\n{proc.stderr}")
    history, updated = _update_duration_history(cache_dir, durations)
    _ = _load_duration_history(cache_dir, cache_ttl_days)
    return proc, elapsed, summary, history, updated


def _run_xdist(
    marker: str,
    workers: str,
    dist: str,
    tests: list[str],
    output: Path,
    maxfail: int,
    fallback: bool,
    cache_root: str | None,
    cache_dir_arg: str | None,
    cache_ttl_days: int,
) -> int:
    cache_dir = _resolve_cache_dir(raw_cache_root=cache_root, raw_cache_dir=cache_dir_arg, prefix=DEFAULT_XDIST_CACHE_PREFIX)
    removed = _prune_cache(cache_dir, cache_ttl_days)
    env = os.environ.copy()

    base_command = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        marker,
        "-n",
        str(workers),
        f"--dist={dist}",
        "--maxfail",
        str(maxfail),
    ]
    base_command.extend(tests)

    primary_proc, primary_elapsed, primary_summary, _, updated = _run_pytest_with_cache(
        base_command.copy(),
        cache_dir=cache_dir,
        cache_ttl_days=cache_ttl_days,
        env=env,
    )
    signals = _detect_worker_crash(primary_proc.stdout, primary_proc.stderr)
    primary_executed = _parse_executed(primary_summary)

    command = base_command
    return_code = primary_proc.returncode
    elapsed = primary_elapsed
    summary = primary_summary
    executed = primary_executed
    command_fallback: list[str] | None = None
    fallback_code: int | None = None

    if fallback and signals and primary_proc.returncode != 0:
        command_fallback = [
            sys.executable,
            "-m",
            "pytest",
            "-m",
            marker,
            "--maxfail",
            str(maxfail),
            *tests,
        ]
        fallback_proc, fallback_elapsed, fallback_summary, _, updated = _run_pytest_with_cache(
            command_fallback.copy(),
            cache_dir=cache_dir,
            cache_ttl_days=cache_ttl_days,
            env=env,
        )
        fallback_code = fallback_proc.returncode
        elapsed = round(primary_elapsed + fallback_elapsed, 3)
        command = command_fallback
        summary = fallback_summary
        executed = _parse_executed(fallback_summary)
        return_code = fallback_proc.returncode
        signals = _detect_worker_crash(fallback_proc.stdout, fallback_proc.stderr)
    artifact = PytestArtifact(
        timestamp=_now_iso(),
        command=command,
        command_fallback=command_fallback,
        return_code=return_code,
        elapsed_seconds=elapsed,
        summary=summary,
        collected=summary.collected,
        executed=executed,
        fallback_recovery=command_fallback is not None,
        fallback_return_code=fallback_code,
        worker_crash=bool(signals),
        crash_signals=signals,
        cache_dir=str(cache_dir),
        xdist_enabled=True,
        extra={
            "marker": marker,
            "workers": workers,
            "dist": dist,
            "maxfail": maxfail,
            "recovery_used": command_fallback is not None,
            "durations_limit": DEFAULT_DURATIONS_LIMIT,
            "cache_ttl_days": cache_ttl_days,
            "pruned_count": len(removed),
            "cache_pruned_files": removed,
            "duration_cache_updated_count": updated,
        },
    )
    _write_json(output, _serialize_artifact(artifact))

    return return_code


def _run_testmon(
    marker: str,
    tests: list[str],
    output: Path,
    cache_root: str | None,
    cache_dir_arg: str | None,
    cache_ttl_days: int,
    maxfail: int,
    baseline_collect: int | None,
    baseline_artifact: Path | None,
    required_hit_rate: float,
) -> int:
    cache_dir = _resolve_cache_dir(raw_cache_root=cache_root, raw_cache_dir=cache_dir_arg, prefix=TESTMON_CACHE_PREFIX)
    removed = _prune_cache(cache_dir, cache_ttl_days)

    baseline_count = baseline_collect
    if baseline_count is None and baseline_artifact is not None:
        payload = json.loads(baseline_artifact.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RuntimeError(f"invalid baseline artifact schema: {baseline_artifact}")
        raw_count = payload.get("collected")
        if isinstance(raw_count, int):
            baseline_count = raw_count

    datafile = cache_dir / ".testmondata"
    env = os.environ.copy()
    env["TESTMON_DATAFILE"] = str(datafile)

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        marker,
        "--testmon",
        "--maxfail",
        str(maxfail),
    ]
    command.extend(tests)

    proc, elapsed, summary, _, updated = _run_pytest_with_cache(
        command,
        cache_dir=cache_dir,
        cache_ttl_days=cache_ttl_days,
        env=env,
    )
    executed = _parse_executed(summary)

    hit_rate = None
    if baseline_count is not None and executed is not None and baseline_count > 0:
        hit_rate = min(1.0, executed / baseline_count)

    gate_pass = hit_rate is not None and hit_rate >= required_hit_rate
    fallback_candidate = (summary.deselected or 0) > 0
    fallback_required = proc.returncode != 0 or (hit_rate is not None and hit_rate < required_hit_rate)
    false_negative_risk = (
        (summary.failed or 0) > 0
        or (summary.xfailed or 0) > 0
        or (summary.deselected or 0) > 0
    )

    artifact = PytestArtifact(
        timestamp=_now_iso(),
        command=command,
        command_fallback=None,
        return_code=proc.returncode,
        elapsed_seconds=elapsed,
        summary=summary,
        collected=summary.collected,
        executed=executed,
        fallback_recovery=False,
        fallback_return_code=None,
        worker_crash=False,
        crash_signals=[],
        cache_dir=str(cache_dir),
        xdist_enabled=False,
        extra={
            "marker": marker,
            "maxfail": maxfail,
            "testmon_datafile": str(datafile),
            "cache_ttl_days": cache_ttl_days,
            "cache_ttl_removed": removed,
            "pruned_count": len(removed),
            "baseline_collect": baseline_count,
            "required_hit_rate": required_hit_rate,
            "hit_rate": hit_rate,
            "gate_pass": gate_pass,
            "fallback_candidate": fallback_candidate,
            "fallback_required": fallback_required,
            "false_negative_risk": false_negative_risk,
            "durations_limit": DEFAULT_DURATIONS_LIMIT,
            "duration_cache_updated_count": updated,
        },
    )
    _write_json(output, _serialize_artifact(artifact))

    if proc.returncode != 0:
        return proc.returncode
    if hit_rate is not None and not gate_pass:
        return 1
    return 0


def _evaluate_testmon(
    pilot_artifact: Path,
    baseline_artifact: Path,
    required_hit_rate: float,
    output: Path,
) -> int:
    pilot_payload = json.loads(pilot_artifact.read_text(encoding="utf-8"))
    baseline_payload = json.loads(baseline_artifact.read_text(encoding="utf-8"))

    if not isinstance(pilot_payload, dict):
        raise RuntimeError(f"invalid pilot artifact schema: {pilot_artifact}")
    if not isinstance(baseline_payload, dict):
        raise RuntimeError(f"invalid baseline artifact schema: {baseline_artifact}")

    baseline_count = baseline_payload.get("collected")
    if isinstance(baseline_count, int):
        baseline_count = max(0, baseline_count)
    else:
        baseline_count = None

    pilot_executed = pilot_payload.get("executed")
    if not isinstance(pilot_executed, int):
        pilot_executed = None

    if baseline_count is None or pilot_executed is None or baseline_count <= 0:
        hit_rate = None
    else:
        hit_rate = min(1.0, pilot_executed / baseline_count)

    if hit_rate is None:
        miss_rate = None
        risk_band = "unknown"
    else:
        miss_rate = round(1.0 - hit_rate, 6)
        if miss_rate >= 0.5:
            risk_band = "high"
        elif miss_rate >= 0.2:
            risk_band = "medium"
        else:
            risk_band = "low"

    fallback_candidate = bool(pilot_payload.get("fallback_candidate"))
    gate_pass = hit_rate is not None and hit_rate >= required_hit_rate
    baseline_failed = pilot_payload.get("return_code", 0) != 0
    false_negative_risk = bool(pilot_payload.get("false_negative_risk"))
    fallback_required = bool(pilot_payload.get("fallback_required"))
    fallback_risk = baseline_failed or false_negative_risk or fallback_candidate
    recommended_fallback = not gate_pass or fallback_required or baseline_failed
    estimated_missed_tests = None
    if baseline_count is not None and pilot_executed is not None:
        estimated_missed_tests = max(0, baseline_count - pilot_executed)

    evaluation = {
        "timestamp": _now_iso(),
        "pilot_artifact": str(pilot_artifact),
        "baseline_artifact": str(baseline_artifact),
        "required_hit_rate": required_hit_rate,
        "baseline_collected": baseline_count,
        "pilot_executed": pilot_executed,
        "estimated_hit_rate": hit_rate,
        "estimated_miss_rate": miss_rate,
        "risk_band": risk_band,
        "fallback_risk": fallback_risk,
        "gate_passed": gate_pass,
        "fallback_candidate": fallback_candidate,
        "recommended_fallback": recommended_fallback,
        "estimated_missed_tests": estimated_missed_tests,
        "details": {
            "pilot_return_code": pilot_payload.get("return_code"),
            "pilot_summary": {
                "passed": pilot_payload.get("passed"),
                "failed": pilot_payload.get("failed"),
                "skipped": pilot_payload.get("skipped"),
                "deselected": pilot_payload.get("deselected"),
                "xpassed": pilot_payload.get("xpassed"),
                "xfailed": pilot_payload.get("xfailed"),
            },
            "cache_dir": pilot_payload.get("cache_dir"),
            "fallback_required": fallback_required,
            "false_negative_risk": false_negative_risk,
        },
    }
    _write_json(output, evaluation)

    if hit_rate is None:
        return 1
    return 0 if gate_pass else 1


def _coerce_duration_cache_prefixes(raw_prefixes: list[str] | None) -> list[str]:
    if not raw_prefixes:
        return [DEFAULT_XDIST_CACHE_PREFIX, TESTMON_CACHE_PREFIX]

    prefixes: list[str] = []
    for item in raw_prefixes:
        for part in item.split(","):
            value = part.strip()
            if not value:
                continue
            prefixes.append(value)
    return prefixes


def _load_duration_history_from_prefixes(
    cache_root: str | None,
    prefixes: list[str],
    ttl_days: int,
) -> tuple[dict[str, float], list[str]]:
    merged: dict[str, float] = {}
    pruned: list[str] = []
    for prefix in prefixes:
        cache_dir = _resolve_cache_dir(raw_cache_root=cache_root, raw_cache_dir=prefix, prefix=prefix)
        pruned.extend(_prune_cache(cache_dir, ttl_days))
        history = _load_duration_history(cache_dir, ttl_days)
        for test_id, duration in history.items():
            existing = merged.get(test_id)
            if existing is None or duration > existing:
                merged[test_id] = duration
    return merged, pruned


def _coerce_test_ids(payload: dict[str, object]) -> list[str]:
    candidates: list[str] = []

    raw_tests = payload.get("tests")
    if isinstance(raw_tests, list):
        for test_id in raw_tests:
            if isinstance(test_id, str):
                candidates.append(test_id)

    raw_items = payload.get("items")
    if isinstance(raw_items, list):
        for entry in raw_items:
            if isinstance(entry, str):
                candidates.append(entry)
            elif isinstance(entry, dict) and isinstance(entry.get("nodeid"), str):
                candidates.append(entry["nodeid"])

    unique = set[str]()
    ordered: list[str] = []
    for test_id in candidates:
        if test_id in unique:
            continue
        unique.add(test_id)
        ordered.append(test_id)

    if not ordered:
        raise RuntimeError("collect artifact has no test ids: expected tests or items")

    return ordered


def _deterministic_shard_index(seed: str, test_id: str, shard_count: int) -> int:
    digest = hashlib.blake2b(f"{test_id}:{seed}".encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big") % shard_count


def _least_loaded_shard(loads: dict[str, float], seed: str, test_id: str) -> str:
    min_load = min(loads.values())
    candidates = [index for index, load in loads.items() if load == min_load]
    if len(candidates) == 1:
        return candidates[0]

    return str(
        min(
            candidates,
            key=lambda index: hashlib.blake2b(f"{seed}:{test_id}:{index}".encode(), digest_size=8).digest(),
        )
    )


def _assign_to_shards(
    test_ids: list[str],
    shard_count: int,
    seed: str,
    durations: dict[str, float],
) -> tuple[dict[str, list[str]], dict[str, float], dict[str, int]]:
    if shard_count <= 0:
        raise ValueError("shard_count must be greater than zero")

    shards: dict[str, list[str]] = {str(index): [] for index in range(shard_count)}
    loads: dict[str, float] = {str(index): 0.0 for index in range(shard_count)}
    counts: dict[str, int] = {str(index): 0 for index in range(shard_count)}
    weighted_nodes: list[str] = []
    fallback_nodes: list[str] = []
    sorted_inputs = sorted(test_ids)

    for test_id in sorted_inputs:
        if durations.get(test_id, 0.0) > 0.0:
            weighted_nodes.append(test_id)
        else:
            fallback_nodes.append(test_id)

    for test_id in sorted(weighted_nodes, key=lambda test_id: (-durations[test_id], test_id)):
        index = _least_loaded_shard(loads, seed, test_id)
        shards[index].append(test_id)
        loads[index] += durations[test_id]
        counts[index] += 1

    for test_id in sorted(fallback_nodes):
        index = str(_deterministic_shard_index(seed, test_id, len(shards)))
        shards[index].append(test_id)
        loads[index] += 1.0
        counts[index] += 1

    return shards, loads, counts


def _run_shard_plan(
    collect_artifact: Path,
    shard_count: int,
    seed: str,
    output: Path,
    cache_root: str | None,
    duration_cache_prefixes: list[str],
    cache_ttl_days: int,
    cache_dir_arg: str | None,
) -> int:
    payload = json.loads(collect_artifact.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"invalid collect artifact schema: {collect_artifact}")

    test_ids = _coerce_test_ids(payload)
    prefixes = _coerce_duration_cache_prefixes(duration_cache_prefixes)
    durations, pruned = _load_duration_history_from_prefixes(cache_root, prefixes, cache_ttl_days)
    shards, loads, counts = _assign_to_shards(test_ids, shard_count, seed, durations)
    load_values = list(loads.values())
    max_load = max(load_values) if load_values else 0.0
    min_load = min(load_values) if load_values else 0.0

    _write_json(
        output,
        {
            "timestamp": _now_iso(),
            "schema_version": SHARD_PLAN_SCHEMA_VERSION,
            "formula": SHARD_FORMULA,
            "input_artifact": str(collect_artifact),
            "input_schema_version": payload.get("schema_version"),
            "shard_count": shard_count,
            "seed": seed,
            "total_tests": len(test_ids),
            "duration_samples_used": len(durations),
            "duration_cache_root": _resolve_cache_root(cache_root).as_posix(),
            "duration_cache_prefixes": prefixes,
            "cache_ttl_days": cache_ttl_days,
            "cache_pruned": pruned,
            "cache_dir": _resolve_cache_dir(
                raw_cache_root=cache_root,
                raw_cache_dir=cache_dir_arg,
                prefix=DEFAULT_SHARD_CACHE_PREFIX,
            ).as_posix()
                if cache_dir_arg is not None or cache_root is not None
                else None,
            "assignment_stats": {
                "max_load": round(max_load, 6),
                "min_load": round(min_load, 6),
                "load_spread": round(max_load - min_load, 6),
                "format": "seconds",
            },
            "assignment_schema": {
                "index": "integer",
                "count": "integer",
                "estimated_load_seconds": "float",
                "testids": "array<string>",
            },
            "shards": [
                {
                    "index": int(index),
                    "count": counts[index],
                    "estimated_load_seconds": round(loads[index], 6),
                    "testids": tests,
                }
                for index, tests in sorted(shards.items(), key=lambda item: int(item[0]))
            ],
        },
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    collect = sub.add_parser(
        "collect-tests",
        help="Run deterministic collect-only and emit test-id artifact.",
    )
    collect.add_argument("--marker", default="not slow and not integration and not e2e and not load")
    collect.add_argument("--maxfail", default=1, type=int)
    collect.add_argument("--test-path", default=".", nargs="*")
    collect.add_argument("--output", required=True)

    xdist = sub.add_parser("xdist", help="Run fast xdist lane with deterministic crash safeguards.")
    xdist.add_argument("--marker", default="not slow and not integration and not e2e and not load")
    xdist.add_argument("--workers", default="auto")
    xdist.add_argument("--dist", default=DEFAULT_XDIST_DIST)
    xdist.add_argument("--maxfail", default=1, type=int)
    xdist.add_argument("--fallback", action="store_true")
    xdist.add_argument("--test-path", default=".", nargs="*")
    xdist.add_argument("--cache-root", default=None)
    xdist.add_argument("--cache-dir", default=DEFAULT_XDIST_CACHE_PREFIX)
    xdist.add_argument("--cache-ttl-days", default=DEFAULT_XDIST_DURATIONS_TTL_DAYS, type=int)
    xdist.add_argument("--output", required=True)

    pilot = sub.add_parser("testmon-pilot", help="Run pytest-testmon pilot lane with cache policy.")
    pilot.add_argument("--marker", default="not slow and not integration and not e2e and not load")
    pilot.add_argument("--output", required=True)
    pilot.add_argument("--cache-root", default=None)
    pilot.add_argument("--cache-dir", default=TESTMON_CACHE_PREFIX)
    pilot.add_argument("--cache-ttl-days", default=DEFAULT_TESTMON_DURATIONS_TTL_DAYS, type=int)
    pilot.add_argument("--maxfail", default=1, type=int)
    pilot.add_argument("--baseline-collect", type=int)
    pilot.add_argument("--baseline-artifact")
    pilot.add_argument("--required-hit-rate", default=0.65, type=float)
    pilot.add_argument("--test-path", default=".", nargs="*")

    evaluate = sub.add_parser(
        "testmon-evaluate",
        help="Evaluate testmon selection quality against baseline.",
    )
    evaluate.add_argument("--pilot-artifact", required=True)
    evaluate.add_argument("--baseline-artifact", required=True)
    evaluate.add_argument("--required-hit-rate", default=0.65, type=float)
    evaluate.add_argument("--output", required=True)

    shard = sub.add_parser(
        "shard-plan",
        help="Build deterministic time-aware shard assignments from test list.",
    )
    shard.add_argument("--collect-artifact", required=True)
    shard.add_argument("--shards", required=True, type=int)
    shard.add_argument("--seed", default="wave-66")
    shard.add_argument("--output", required=True)
    shard.add_argument("--cache-root", default=None)
    shard.add_argument(
        "--cache-dir",
        default=DEFAULT_SHARD_CACHE_PREFIX,
        help="Shard run cache directory (for consistency with xdist/testmon).",
    )
    shard.add_argument(
        "--cache-ttl-days",
        default=DEFAULT_SHARD_DURATIONS_TTL_DAYS,
        type=int,
        help="TTL used when loading duration history for planning.",
    )
    shard.add_argument(
        "--duration-cache-prefixes",
        nargs="+",
        default=[DEFAULT_XDIST_CACHE_PREFIX, TESTMON_CACHE_PREFIX],
        help="Cache prefixes to source duration history for greedy placement.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "xdist":
        return _run_xdist(
            marker=args.marker,
            workers=args.workers,
            dist=args.dist,
            tests=list(args.test_path),
            output=Path(args.output),
            maxfail=args.maxfail,
            fallback=args.fallback,
            cache_root=args.cache_root,
            cache_dir_arg=args.cache_dir,
            cache_ttl_days=args.cache_ttl_days,
        )

    if args.command == "collect-tests":
        return _run_collect_tests(
            marker=args.marker,
            output=Path(args.output),
            maxfail=args.maxfail,
            tests=list(args.test_path),
        )

    if args.command == "testmon-pilot":
        return _run_testmon(
            marker=args.marker,
            tests=list(args.test_path),
            output=Path(args.output),
            cache_root=args.cache_root,
            cache_dir_arg=args.cache_dir,
            cache_ttl_days=args.cache_ttl_days,
            maxfail=args.maxfail,
            baseline_collect=args.baseline_collect,
            baseline_artifact=Path(args.baseline_artifact) if args.baseline_artifact else None,
            required_hit_rate=args.required_hit_rate,
        )

    if args.command == "testmon-evaluate":
        return _evaluate_testmon(
            pilot_artifact=Path(args.pilot_artifact),
            baseline_artifact=Path(args.baseline_artifact),
            required_hit_rate=args.required_hit_rate,
            output=Path(args.output),
        )

    if args.command == "shard-plan":
        return _run_shard_plan(
            collect_artifact=Path(args.collect_artifact),
            shard_count=args.shards,
            seed=args.seed,
            output=Path(args.output),
            cache_root=args.cache_root,
            duration_cache_prefixes=list(args.duration_cache_prefixes),
            cache_ttl_days=args.cache_ttl_days,
            cache_dir_arg=args.cache_dir,
        )

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
