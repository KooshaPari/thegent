#!/usr/bin/env python3
"""Weekly LOC/refactor diagnosis with trend alerts and CI summary."""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import orjson as json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import tomllib

LINE_EXTENSIONS = {
    ".py",
    ".rs",
    ".go",
    ".zig",
    ".mojo",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".sh",
    ".bash",
    ".zsh",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/wl137-diagnosis.toml"))
    parser.add_argument("--history", type=Path, default=Path("var/wl137/history.json"))
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument(
        "--ci-summary",
        type=Path,
        default=None,
        help="Optional JSON summary for CI dashboards (WL-135).",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _load_config(path: Path) -> dict[str, Any]:
    with path.open("rb") as fh:
        cfg = tomllib.load(fh)
    if not cfg.get("targets"):
        raise ValueError("Config must define at least one [[targets]] entry.")
    return cfg


def _resolved_excludes(repo_path: Path, exclude_dirs: list[str]) -> list[str]:
    resolved: set[str] = set()
    for entry in exclude_dirs:
        if any(ch in entry for ch in "*?[]"):
            for candidate in repo_path.glob(entry):
                resolved.add(candidate.name)
        else:
            resolved.add(entry)
    return sorted(resolved)


def _run_tokei(repo_path: Path, exclude_dirs: list[str]) -> dict[str, Any]:
    cmd = ["tokei", "--sort", "code", "--output", "json"]
    for excluded in _resolved_excludes(repo_path, exclude_dirs):
        cmd.extend(["--exclude", excluded])
    cmd.append(str(repo_path))
    try:
        completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("tokei is required but was not found in PATH.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"tokei failed for {repo_path}:\n{exc.stderr}") from exc
    return json.loads(completed.stdout)


def _count_nonempty_lines(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if line.strip():
                count += 1
    return count


def _matches_any_pattern(value: str, patterns: set[str]) -> bool:
    return any(fnmatch.fnmatch(value, pattern) for pattern in patterns)


def _collect_hotspots(
    repo_path: Path,
    exclude_dirs: list[str],
    top_files_limit: int,
    line_threshold_high: int,
    line_threshold_critical: int,
) -> dict[str, Any]:
    exclude_patterns = set(exclude_dirs)
    files: list[tuple[int, str]] = []
    over_high = 0
    over_critical = 0

    for root, dirs, names in os.walk(repo_path):
        root_path = Path(root)
        rel_root = root_path.relative_to(repo_path).as_posix()

        # Prune excluded subtrees early to keep runtime bounded.
        dirs[:] = [d for d in dirs if not _matches_any_pattern(d, exclude_patterns)]
        if rel_root != "." and _matches_any_pattern(rel_root, exclude_patterns):
            continue

        for name in names:
            if _matches_any_pattern(name, exclude_patterns):
                continue
            candidate = root_path / name
            if candidate.suffix.lower() not in LINE_EXTENSIONS:
                continue
            rel = candidate.relative_to(repo_path).as_posix()
            if _matches_any_pattern(rel, exclude_patterns):
                continue
            lines = _count_nonempty_lines(candidate)
            files.append((lines, rel))
            if lines > line_threshold_high:
                over_high += 1
            if lines > line_threshold_critical:
                over_critical += 1

    files.sort(reverse=True)
    return {
        "files_scanned": len(files),
        "files_over_high": over_high,
        "files_over_critical": over_critical,
        "top_files": [{"path": path, "lines": lines} for lines, path in files[:top_files_limit]],
    }


def _extract_code_by_language(tokei_payload: dict[str, Any]) -> dict[str, int]:
    code_by_language: dict[str, int] = {}
    for language, stats in tokei_payload.items():
        if language == "Total":
            continue
        code_by_language[language] = int(stats.get("code", 0))
    return code_by_language


def _load_history(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "runs": []}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _latest_for_target(history: dict[str, Any], target_name: str) -> dict[str, Any] | None:
    for run in reversed(history.get("runs", [])):
        snapshot = run.get("targets", {}).get(target_name)
        if snapshot:
            return snapshot
    return None


def _build_alerts(
    target: str,
    current: dict[str, Any],
    previous: dict[str, Any] | None,
    loc_delta_alert: int,
    hotspot_delta_alert: int,
) -> list[str]:
    if previous is None:
        return []
    alerts: list[str] = []
    loc_delta = current["total_code"] - previous["total_code"]
    high_delta = current["files_over_high"] - previous["files_over_high"]
    critical_delta = current["files_over_critical"] - previous["files_over_critical"]
    if loc_delta > loc_delta_alert:
        alerts.append(f"{target}: LOC increased by {loc_delta} (> {loc_delta_alert})")
    if high_delta > hotspot_delta_alert:
        alerts.append(f"{target}: files>{current['line_threshold_high']} increased by {high_delta}")
    if critical_delta > hotspot_delta_alert:
        alerts.append(f"{target}: files>{current['line_threshold_critical']} increased by {critical_delta}")
    return alerts


def _runtime_bucket(language: str) -> str:
    if language == "Python":
        return "python"
    if language == "Rust":
        return "rust"
    if language == "Zig":
        return "zig"
    if language == "Mojo":
        return "mojo"
    if language in {"TypeScript", "JavaScript"}:
        return "typescript_js"
    return "other"


def _bucket_runtime_loc(code_by_language: dict[str, int]) -> dict[str, int]:
    buckets = {"python": 0, "rust": 0, "zig": 0, "mojo": 0, "typescript_js": 0, "other": 0}
    for language, code in code_by_language.items():
        buckets[_runtime_bucket(language)] += code
    return buckets


def _build_ci_summary(timestamp_utc: str, targets_payload: dict[str, Any], history: dict[str, Any]) -> dict[str, Any]:
    targets: dict[str, Any] = {}
    for name, metrics in targets_payload.items():
        previous = _latest_for_target(history, name)
        drift = {"total_code_delta": 0, "files_over_high_delta": 0, "files_over_critical_delta": 0}
        if previous is not None:
            drift = {
                "total_code_delta": metrics["total_code"] - previous["total_code"],
                "files_over_high_delta": metrics["files_over_high"] - previous["files_over_high"],
                "files_over_critical_delta": metrics["files_over_critical"] - previous["files_over_critical"],
            }
        targets[name] = {
            "total_code": metrics["total_code"],
            "runtime_loc": _bucket_runtime_loc(metrics["code_by_language"]),
            "top_files": metrics["top_files"],
            "drift": drift,
        }
    return {"timestamp_utc": timestamp_utc, "targets": targets}


def _render_report(timestamp_utc: str, run_payload: dict[str, Any]) -> str:
    lines = [
        f"# WL-137 Weekly LOC/Refactor Diagnosis ({timestamp_utc[:10]})",
        "",
        f"- Timestamp (UTC): `{timestamp_utc}`",
        "",
        "## Summary",
        "",
        "| Target | Total Code LOC | Files Scanned | Files > High | Files > Critical |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, metrics in run_payload["targets"].items():
        lines.append(
            f"| {name} | {metrics['total_code']} | {metrics['files_scanned']} | "
            f"{metrics['files_over_high']} | {metrics['files_over_critical']} |"
        )

    lines.extend(["", "## Alerts", ""])
    if run_payload["alerts"]:
        for alert in run_payload["alerts"]:
            lines.append(f"- [ ] {alert}")
    else:
        lines.append("- [x] No threshold regressions detected.")

    for name, metrics in run_payload["targets"].items():
        lines.extend(["", f"## {name} Top Files", "", "| File | Non-empty Lines |", "|---|---:|"])
        for entry in metrics["top_files"]:
            lines.append(f"| `{entry['path']}` | {entry['lines']} |")
        lines.extend(["", f"### {name} Code LOC by Language", "", "| Language | Code LOC |", "|---|---:|"])
        ranked = sorted(metrics["code_by_language"].items(), key=lambda item: item[1], reverse=True)
        for language, code in ranked:
            lines.append(f"| {language} | {code} |")

    lines.extend(
        [
            "",
            "## Next Actions",
            "",
            "1. If alerts fired, open a decomposition work item and link this report.",
            "2. Update `docs/reference/WORK_STREAM.md` if priorities shift.",
            "3. Re-run next week to keep trend history continuous.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = _parse_args()
    config = _load_config(args.config)
    defaults = config.get("defaults", {})

    line_threshold_high = int(defaults.get("line_threshold_high", 500))
    line_threshold_critical = int(defaults.get("line_threshold_critical", 1000))
    top_files_limit = int(defaults.get("top_files_limit", 10))
    loc_delta_alert = int(defaults.get("loc_delta_alert", 2000))
    hotspot_delta_alert = int(defaults.get("hotspot_delta_alert", 3))

    history = _load_history(args.history)
    timestamp_utc = dt.datetime.now(dt.UTC).isoformat()
    targets_payload: dict[str, Any] = {}
    all_alerts: list[str] = []

    for target in config["targets"]:
        name = str(target["name"])
        repo_path = Path(str(target["path"])).expanduser().resolve()
        if not repo_path.exists():
            raise RuntimeError(f"Target path does not exist: {repo_path}")
        exclude_dirs = [str(item) for item in target.get("exclude_dirs", [])]

        tokei_payload = _run_tokei(repo_path, exclude_dirs)
        code_by_language = _extract_code_by_language(tokei_payload)
        hotspots = _collect_hotspots(
            repo_path=repo_path,
            exclude_dirs=exclude_dirs,
            top_files_limit=top_files_limit,
            line_threshold_high=line_threshold_high,
            line_threshold_critical=line_threshold_critical,
        )
        total_code = int(tokei_payload.get("Total", {}).get("code", sum(code_by_language.values())))
        current = {
            "path": str(repo_path),
            "total_code": total_code,
            "line_threshold_high": line_threshold_high,
            "line_threshold_critical": line_threshold_critical,
            "code_by_language": code_by_language,
            **hotspots,
        }

        previous = _latest_for_target(history, name)
        alerts = _build_alerts(name, current, previous, loc_delta_alert, hotspot_delta_alert)
        all_alerts.extend(alerts)
        targets_payload[name] = current

    run_payload = {"timestamp_utc": timestamp_utc, "targets": targets_payload, "alerts": all_alerts}
    report_text = _render_report(timestamp_utc, run_payload)

    if args.ci_summary is not None:
        ci_summary = _build_ci_summary(timestamp_utc, targets_payload, history)
        args.ci_summary.parent.mkdir(parents=True, exist_ok=True)
        args.ci_summary.write_text(json.dumps(ci_summary, indent=2).decode().decode() + "\n", encoding="utf-8")

    if args.dry_run:
        print(report_text)
        if args.ci_summary is not None:
            print(f"Wrote CI summary: {args.ci_summary}")
        return 1 if all_alerts else 0

    args.history.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    history.setdefault("version", 1)
    history.setdefault("runs", [])
    history["runs"].append(run_payload)

    with args.history.open("w", encoding="utf-8") as fh:
        json.dump(history, fh, indent=2)
        fh.write("\n")
    args.report.write_text(report_text, encoding="utf-8")

    print(f"Wrote history: {args.history}")
    print(f"Wrote report:  {args.report}")
    if args.ci_summary is not None:
        print(f"Wrote CI summary: {args.ci_summary}")
    if all_alerts:
        for alert in all_alerts:
            print(f"ALERT: {alert}")
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
