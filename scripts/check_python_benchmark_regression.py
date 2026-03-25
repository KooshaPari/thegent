#!/usr/bin/env python3
"""WL-078 benchmark regression check against a stored baseline."""

from __future__ import annotations

import argparse
import orjson as json
from math import isfinite
from pathlib import Path
from typing import Any


def _index_rows(payload: dict[str, Any], *, require_positive_avg: bool) -> dict[str, float]:
    rows = payload.get("benchmarks", [])
    if not isinstance(rows, list):
        raise ValueError("payload.benchmarks must be a list")
    indexed: dict[str, float] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each benchmark row must be an object")
        raw_label = row.get("label", "")
        if not isinstance(raw_label, str):
            raise ValueError("benchmark label must be a string")
        label = raw_label.strip()
        if not label:
            raise ValueError("benchmark label must be non-empty")
        raw_avg_us = row.get("avg_microseconds", 0.0)
        if isinstance(raw_avg_us, bool):
            raise ValueError("avg_microseconds must be numeric")
        try:
            avg_us = float(raw_avg_us)
        except (TypeError, ValueError) as exc:
            raise ValueError("avg_microseconds must be numeric") from exc
        if not isfinite(avg_us) or avg_us < 0:
            raise ValueError("avg_microseconds must be finite and >= 0")
        if require_positive_avg and avg_us <= 0:
            raise ValueError("baseline avg_microseconds must be > 0")
        if label in indexed:
            raise ValueError(f"duplicate benchmark label: {label}")
        indexed[label] = avg_us
    return indexed


def find_regressions(
    baseline_payload: dict[str, Any],
    current_payload: dict[str, Any],
    *,
    max_regression_pct: float,
    require_complete_baseline: bool = False,
) -> list[dict[str, Any]]:
    if not isfinite(max_regression_pct) or max_regression_pct < 0:
        raise ValueError("max_regression_pct must be finite and >= 0")
    baseline = _index_rows(baseline_payload, require_positive_avg=True)
    current = _index_rows(current_payload, require_positive_avg=False)

    regressions: list[dict[str, Any]] = []
    for label, baseline_avg in baseline.items():
        if label not in current:
            if require_complete_baseline:
                regressions.append(
                    {
                        "label": label,
                        "baseline_avg_us": round(baseline_avg, 3),
                        "current_avg_us": None,
                        "delta_pct": None,
                        "reason": "missing_from_current",
                    }
                )
            continue
        current_avg = current[label]
        delta_pct = ((current_avg - baseline_avg) / baseline_avg) * 100.0
        if delta_pct > max_regression_pct:
            regressions.append(
                {
                    "label": label,
                    "baseline_avg_us": round(baseline_avg, 3),
                    "current_avg_us": round(current_avg, 3),
                    "delta_pct": round(delta_pct, 2),
                }
            )
    return regressions


def evaluate_benchmark_gates(
    baseline_payload: dict[str, Any],
    current_payload: dict[str, Any],
    *,
    max_regression_pct: float,
    max_throughput_drop_pct: float,
    require_complete_baseline: bool = False,
) -> dict[str, Any]:
    """Evaluate latency and throughput regression gates."""
    regressions = find_regressions(
        baseline_payload,
        current_payload,
        max_regression_pct=max_regression_pct,
        require_complete_baseline=require_complete_baseline,
    )
    if not isfinite(max_throughput_drop_pct) or max_throughput_drop_pct < 0:
        raise ValueError("max_throughput_drop_pct must be finite and >= 0")

    def _throughput(payload: dict[str, Any]) -> float | None:
        benchmarks = payload.get("benchmarks")
        if not isinstance(benchmarks, list):
            return None
        elapsed_total = 0.0
        iterations_total = 0
        for row in benchmarks:
            if not isinstance(row, dict):
                continue
            elapsed = row.get("elapsed_seconds")
            iterations = row.get("iterations")
            if isinstance(elapsed, bool) or isinstance(iterations, bool):
                continue
            try:
                elapsed_value = float(elapsed)
                iterations_value = int(iterations)
            except TypeError, ValueError:
                continue
            if elapsed_value <= 0 or iterations_value <= 0:
                continue
            elapsed_total += elapsed_value
            iterations_total += iterations_value
        if elapsed_total <= 0 or iterations_total <= 0:
            return None
        return iterations_total / elapsed_total

    baseline_tp = _throughput(baseline_payload)
    current_tp = _throughput(current_payload)
    throughput_gate = {
        "baseline_ops_per_second": baseline_tp,
        "current_ops_per_second": current_tp,
        "drop_pct": None,
        "threshold_pct": max_throughput_drop_pct,
        "failed": False,
    }
    if baseline_tp is not None and current_tp is not None and baseline_tp > 0:
        drop_pct = ((baseline_tp - current_tp) / baseline_tp) * 100.0
        throughput_gate["drop_pct"] = round(drop_pct, 2)
        throughput_gate["failed"] = drop_pct > max_throughput_drop_pct

    return {
        "ok": len(regressions) == 0 and throughput_gate["failed"] is False,
        "latency_regressions": regressions,
        "throughput_gate": throughput_gate,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check WL-078 benchmark regression threshold.")
    parser.add_argument("--baseline", type=Path, default=Path("benchmarks/baseline.json"))
    parser.add_argument("--current", type=Path, default=Path("benchmarks/results/python/latest.json"))
    parser.add_argument("--max-regression-pct", type=float, default=15.0)
    parser.add_argument("--max-throughput-drop-pct", type=float, default=10.0)
    parser.add_argument(
        "--require-complete-baseline",
        action="store_true",
        help="Fail if any baseline benchmark labels are missing from current payload.",
    )
    args = parser.parse_args()
    if not isfinite(args.max_regression_pct) or args.max_regression_pct < 0:
        parser.error("--max-regression-pct must be finite and >= 0")
    if not isfinite(args.max_throughput_drop_pct) or args.max_throughput_drop_pct < 0:
        parser.error("--max-throughput-drop-pct must be finite and >= 0")

    baseline_payload = json.loads(args.baseline.read_text(encoding="utf-8"))
    current_payload = json.loads(args.current.read_text(encoding="utf-8"))
    gate = evaluate_benchmark_gates(
        baseline_payload,
        current_payload,
        max_regression_pct=args.max_regression_pct,
        max_throughput_drop_pct=args.max_throughput_drop_pct,
        require_complete_baseline=args.require_complete_baseline,
    )
    if not gate["ok"]:
        print(json.dumps(gate, indent=2).decode().decode())
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "max_regression_pct": args.max_regression_pct,
                "max_throughput_drop_pct": args.max_throughput_drop_pct,
                "throughput_gate": gate["throughput_gate"],
            },
            indent=2,
        )
    ).decode()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
