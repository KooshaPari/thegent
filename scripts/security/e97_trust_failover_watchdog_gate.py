#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys
from datetime import datetime, timezone


def _load_rows(path: pathlib.Path) -> tuple[list[dict], str | None]:
    try:
        if path.suffix.lower() == ".csv":
            return list(csv.DictReader(path.open())), None
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [], f"E97 invalid input: {exc}"

    if isinstance(data, list):
        return data, None
    if isinstance(data, dict):
        for key in ("watchdogs", "failovers", "trust_failovers", "items", "records", "events"):
            rows = data.get(key)
            if isinstance(rows, list):
                return rows, None
    return (
        [],
        "E97 invalid input: expected list or dict with "
        "watchdogs/failovers/trust_failovers/items/records/events",
    )


def _pick(row: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = row.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _parse_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _parse_minutes(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _is_watchdog_breach(row: dict, max_silence_minutes: float) -> bool:
    status = str(row.get("status", "")).strip().lower()
    if status in {"failed", "degraded", "timed_out", "broken", "offline"}:
        return True
    if bool(
        row.get("watchdog_breach")
        or row.get("watchdog_triggered")
        or row.get("heartbeat_missed")
        or row.get("health_check_failed")
    ):
        return True

    heartbeat = _parse_datetime(
        row.get("last_heartbeat_at")
        or row.get("heartbeat_at")
        or row.get("observed_at")
        or row.get("checked_at")
    )
    if heartbeat is None:
        return True

    now = _parse_datetime(row.get("evaluated_at")) or datetime.now(timezone.utc)
    silence_seconds = (now - heartbeat).total_seconds()
    if silence_seconds < 0:
        silence_seconds = 0

    listed_silence = _parse_minutes(
        row.get("silence_minutes")
        or row.get("missing_heartbeat_minutes")
        or row.get("watchdog_silence_minutes")
    )
    if listed_silence is not None:
        return listed_silence > max_silence_minutes

    return silence_seconds / 60.0 > max_silence_minutes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--watchdogs", required=True)
    parser.add_argument("--max-silence-minutes", type=float, default=10.0)
    parser.add_argument("--max-breached-watchdogs", type=int, default=0)
    args = parser.parse_args()

    rows, err = _load_rows(pathlib.Path(args.watchdogs))
    if err:
        print(err, file=sys.stderr)
        return 2

    breached = sorted(
        {
            _pick(r, ("id", "watchdog_id", "failover_id", "name"))
            for r in rows
            if _is_watchdog_breach(r, args.max_silence_minutes)
        }
    )
    if len(breached) > args.max_breached_watchdogs:
        print(
            f"E97 trust failover watchdog breach: count={len(breached)} "
            f"max={args.max_breached_watchdogs}",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

