"""Render SLO dashboard artifact to .quality/slo-dashboard.md.

Reads .quality/loc-metrics.json if available, otherwise uses sample data.
Reads src/thegent/governance/slo_metrics.py thresholds if available.
Produces .quality/slo-dashboard.md with a markdown table.

WL-135 B90-W2-E1
"""

# @trace WL-135 B90-W2-E1

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
QUALITY_DIR = ROOT / ".quality"
LOC_METRICS_PATH = QUALITY_DIR / "loc-metrics.json"
DASHBOARD_PATH = QUALITY_DIR / "slo-dashboard.md"


# SLO thresholds (sourced from Wave-1 E1 report and governance/slo.py)
_THRESHOLDS = {
    "file_loc_green": 1200,
    "file_loc_warn": 1500,
    "file_loc_red": 1800,
    "total_python_loc_green": 80_000,
    "total_python_loc_red": 120_000,
    "p95_latency_ms_green": 250,
    "p95_latency_ms_red": 500,
    "error_rate_pct_green": 0.5,
    "error_rate_pct_red": 1.0,
    "trend_health_good": 95,
    "trend_health_warning": 80,
    "trend_health_degraded": 50,
}


def _load_loc_metrics() -> dict:
    """Load loc-metrics.json from .quality/ if it exists, otherwise return sample data."""
    if LOC_METRICS_PATH.exists():
        with LOC_METRICS_PATH.open() as fh:
            return json.load(fh)
    # Sample data — representative of codebase state (Wave-1 E3 findings)
    return {
        "total_python_loc": 95_000,
        "file_loc_max": 3200,
        "file_loc_p95": 980,
        "file_loc_median": 320,
        "p95_latency_ms": 185,
        "error_rate_pct": 0.3,
        "trend_health_score": 87,
        "_sample": True,
    }


def _status_cell(value: float, green_threshold: float, red_threshold: float, lower_is_better: bool = True) -> str:
    """Return green or red status indicator."""
    if lower_is_better:
        if value <= green_threshold:
            return "GREEN"
        if value >= red_threshold:
            return "RED"
        return "WARN"
    # Higher is better (e.g. trend health score)
    if value >= green_threshold:
        return "GREEN"
    if value <= red_threshold:
        return "RED"
    return "WARN"


def _render_dashboard(metrics: dict) -> str:
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    is_sample = metrics.get("_sample", False)
    source_note = "(sample data — run collect_loc_metrics.py to populate)" if is_sample else f"(source: {LOC_METRICS_PATH})"

    t = _THRESHOLDS

    rows = [
        (
            "Total Python LOC",
            metrics.get("total_python_loc", "N/A"),
            _status_cell(metrics.get("total_python_loc", 0), t["total_python_loc_green"], t["total_python_loc_red"]),
            f"<={t['total_python_loc_green']:,}",
            f">={t['total_python_loc_red']:,}",
        ),
        (
            "file_loc max",
            metrics.get("file_loc_max", "N/A"),
            _status_cell(metrics.get("file_loc_max", 0), t["file_loc_green"], t["file_loc_red"]),
            f"<={t['file_loc_green']}",
            f">={t['file_loc_red']}",
        ),
        (
            "file_loc p95",
            metrics.get("file_loc_p95", "N/A"),
            _status_cell(metrics.get("file_loc_p95", 0), t["file_loc_green"], t["file_loc_red"]),
            f"<={t['file_loc_green']}",
            f">={t['file_loc_red']}",
        ),
        (
            "file_loc median",
            metrics.get("file_loc_median", "N/A"),
            _status_cell(metrics.get("file_loc_median", 0), t["file_loc_green"], t["file_loc_red"]),
            f"<={t['file_loc_green']}",
            f">={t['file_loc_red']}",
        ),
        (
            "p95 latency (ms)",
            metrics.get("p95_latency_ms", "N/A"),
            _status_cell(metrics.get("p95_latency_ms", 0), t["p95_latency_ms_green"], t["p95_latency_ms_red"]),
            f"<={t['p95_latency_ms_green']}ms",
            f">={t['p95_latency_ms_red']}ms",
        ),
        (
            "error rate (%)",
            metrics.get("error_rate_pct", "N/A"),
            _status_cell(metrics.get("error_rate_pct", 0), t["error_rate_pct_green"], t["error_rate_pct_red"]),
            f"<={t['error_rate_pct_green']}%",
            f">={t['error_rate_pct_red']}%",
        ),
        (
            "trend health score",
            metrics.get("trend_health_score", "N/A"),
            _status_cell(
                metrics.get("trend_health_score", 0),
                t["trend_health_good"],
                t["trend_health_degraded"],
                lower_is_better=False,
            ),
            f">={t['trend_health_good']}",
            f"<={t['trend_health_degraded']}",
        ),
    ]

    table_header = "| Metric | Value | Status | Threshold (Green) | Threshold (Red) |"
    table_sep = "|--------|-------|--------|-------------------|-----------------|"
    table_rows = "\n".join(
        f"| {name} | {value:,} | {status} | {green} | {red} |"
        if isinstance(value, int)
        else f"| {name} | {value} | {status} | {green} | {red} |"
        for name, value, status, green, red in rows
    )

    return f"""# LOC/SLO Dashboard ({now})

> Source: {source_note}
> Thresholds: Wave-1 E1 / `src/thegent/governance/slo.py`

{table_header}
{table_sep}
{table_rows}

## Breach States

| Condition | State |
|-----------|-------|
| `past_sla_count > 0` | CRITICAL — escalation backlog critical |
| `within_budget == false` | CRITICAL — contract drift over budget |
| `trend_health_score < {t["trend_health_degraded"]}` | CRITICAL |
| `trend_health_score < {t["trend_health_warning"]}` | DEGRADED |
| `trend_health_score < {t["trend_health_good"]}` | WARNING |
| All thresholds in green | HEALTHY |

## Threshold Source

- latency SLO: `<= {t["p95_latency_ms_red"]}ms`
- error-rate SLO: `<= {t["error_rate_pct_red"]}%`
- file LOC warn: `>= {t["file_loc_warn"]}`
- file LOC hard: `>= {t["file_loc_red"]}`

_Generated by `scripts/render_slo_dashboard.py` — WL-135 B90-W2-E1_
"""


def main() -> None:
    # Fail loudly if .quality/ cannot be written — no silent fallback
    QUALITY_DIR.mkdir(parents=False, exist_ok=True)
    if not QUALITY_DIR.is_dir():
        print(f"ERROR: .quality/ directory does not exist and could not be created: {QUALITY_DIR}", file=sys.stderr)
        sys.exit(1)

    metrics = _load_loc_metrics()
    dashboard = _render_dashboard(metrics)

    DASHBOARD_PATH.write_text(dashboard, encoding="utf-8")
    print(f"SLO dashboard written to {DASHBOARD_PATH}")


if __name__ == "__main__":
    main()
