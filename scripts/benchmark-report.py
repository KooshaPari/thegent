#!/usr/bin/env python3
from __future__ import annotations

import argparse
import orjson as json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Result:
    scenario: str
    implementation: str
    command: str
    mean_seconds: float
    min_seconds: float
    max_seconds: float
    stddev_seconds: float

    @property
    def mean_ms(self) -> float:
        return self.mean_seconds * 1000.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render reproducible benchmark reports from Hyperfine JSON outputs.")
    parser.add_argument("--baseline-dir", type=Path, required=True, help="Directory of baseline Hyperfine JSON files.")
    parser.add_argument("--current-dir", type=Path, required=True, help="Directory of current Hyperfine JSON files.")
    parser.add_argument("--report-path", type=Path, required=True, help="Markdown report output path.")
    parser.add_argument("--summary-path", type=Path, required=True, help="Machine-readable summary JSON output path.")
    parser.add_argument("--title", default="Hook Runtime Benchmark Report", help="Report title.")
    return parser.parse_args()


def parse_filename(path: Path) -> tuple[str, str]:
    stem = path.stem
    if "_" not in stem:
        raise ValueError(f"Benchmark file must follow <scenario>_<implementation>.json, got: {path.name}")
    scenario, implementation = stem.rsplit("_", 1)
    return scenario, implementation


def load_result(path: Path) -> Result:
    payload = json.loads(path.read_text(encoding="utf-8"))
    results = payload.get("results", [])
    if not isinstance(results, list) or not results:
        raise ValueError(f"Hyperfine file has no results: {path}")
    first = results[0]
    scenario, implementation = parse_filename(path)
    return Result(
        scenario=scenario,
        implementation=implementation,
        command=str(first.get("command", "")),
        mean_seconds=float(first["mean"]),
        min_seconds=float(first["min"]),
        max_seconds=float(first["max"]),
        stddev_seconds=float(first["stddev"]),
    )


def collect_results(root: Path) -> dict[str, Result]:
    results: dict[str, Result] = {}
    if not root.exists():
        return results
    for file_path in sorted(root.glob("*.json")):
        result = load_result(file_path)
        results[result.scenario] = result
    return results


def format_speedup(speedup: float | None) -> str:
    if speedup is None:
        return "N/A"
    return f"{speedup:.2f}x"


def build_report(
    title: str,
    baseline: dict[str, Result],
    current: dict[str, Result],
    baseline_dir: Path,
    current_dir: Path,
) -> tuple[str, dict[str, Any]]:
    scenarios = sorted(set(baseline) | set(current))
    generated_at = datetime.now(UTC).isoformat()
    lines = [
        f"# {title}",
        "",
        f"- Generated (UTC): `{generated_at}`",
        f"- Baseline dir: `{baseline_dir}`",
        f"- Current dir: `{current_dir}`",
        "",
        "| Scenario | Baseline Impl | Current Impl | Baseline Mean (ms) | Current Mean (ms) | Speedup |",
        "|---|---|---|---:|---:|---:|",
    ]
    summary_scenarios: list[dict[str, Any]] = []
    mode_rows: dict[str, list[tuple[float, float]]] = {"cold": [], "warm": []}

    for scenario in scenarios:
        base = baseline.get(scenario)
        cur = current.get(scenario)
        speedup: float | None = None
        if base is not None and cur is not None and cur.mean_seconds > 0:
            speedup = round(base.mean_seconds / cur.mean_seconds, 4)
            if scenario.endswith("_cold"):
                mode_rows["cold"].append((base.mean_seconds, cur.mean_seconds))
            if scenario.endswith("_warm"):
                mode_rows["warm"].append((base.mean_seconds, cur.mean_seconds))

        lines.append(
            "| "
            + " | ".join(
                [
                    scenario,
                    base.implementation if base is not None else "-",
                    cur.implementation if cur is not None else "-",
                    f"{base.mean_ms:.3f}" if base is not None else "N/A",
                    f"{cur.mean_ms:.3f}" if cur is not None else "N/A",
                    format_speedup(speedup),
                ]
            )
            + " |"
        )

        summary_scenarios.append(
            {
                "scenario": scenario,
                "baseline": {
                    "implementation": base.implementation,
                    "command": base.command,
                    "mean_seconds": base.mean_seconds,
                    "min_seconds": base.min_seconds,
                    "max_seconds": base.max_seconds,
                    "stddev_seconds": base.stddev_seconds,
                }
                if base is not None
                else None,
                "current": {
                    "implementation": cur.implementation,
                    "command": cur.command,
                    "mean_seconds": cur.mean_seconds,
                    "min_seconds": cur.min_seconds,
                    "max_seconds": cur.max_seconds,
                    "stddev_seconds": cur.stddev_seconds,
                }
                if cur is not None
                else None,
                "speedup": speedup,
            }
        )

    lines.append("")
    lines.append("## Mode Split Aggregates")
    lines.append("")
    lines.append("| Mode | Baseline Mean (ms) | Current Mean (ms) | Speedup |")
    lines.append("|---|---:|---:|---:|")
    mode_aggregates: dict[str, dict[str, float] | None] = {}
    for mode in ("cold", "warm"):
        pairs = mode_rows[mode]
        if not pairs:
            lines.append(f"| {mode} | N/A | N/A | N/A |")
            mode_aggregates[mode] = None
            continue
        base_mean = sum(p[0] for p in pairs) / len(pairs)
        cur_mean = sum(p[1] for p in pairs) / len(pairs)
        speedup = base_mean / cur_mean if cur_mean > 0 else 0.0
        lines.append(f"| {mode} | {base_mean * 1000.0:.3f} | {cur_mean * 1000.0:.3f} | {speedup:.2f}x |")
        mode_aggregates[mode] = {
            "baseline_mean_seconds": round(base_mean, 6),
            "current_mean_seconds": round(cur_mean, 6),
            "speedup": round(speedup, 4),
        }

    summary = {
        "generated_at_utc": generated_at,
        "title": title,
        "baseline_dir": str(baseline_dir),
        "current_dir": str(current_dir),
        "scenarios": summary_scenarios,
        "mode_aggregates": mode_aggregates,
    }
    lines.append("")
    return "\n".join(lines), summary


def main() -> int:
    args = parse_args()
    baseline = collect_results(args.baseline_dir)
    current = collect_results(args.current_dir)

    report, summary = build_report(
        title=args.title,
        baseline=baseline,
        current=current,
        baseline_dir=args.baseline_dir,
        current_dir=args.current_dir,
    )

    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.summary_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(report + "\n", encoding="utf-8")
    args.summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True).decode().decode() + "\n", encoding="utf-8"
    )
    print(f"Wrote report: {args.report_path}")
    print(f"Wrote summary: {args.summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
