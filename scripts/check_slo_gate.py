"""SLO pass/fail gate script (WL-135 B90-W3-A4).

Reads .quality/slo-metrics.jsonl if it exists.
- No file: exits 0 (no data = no gate failure)
- Last record all green/yellow: exits 0
- Any field red: prints violations and exits 1

Fail-fast: no silent errors, no fallbacks.
"""
# @trace WL-135 B90-W3-A4

from __future__ import annotations

import orjson as json
import sys
from pathlib import Path

_DEFAULT_JSONL = Path(".quality") / "slo-metrics.jsonl"


def main() -> None:
    jsonl_path = _DEFAULT_JSONL

    if not jsonl_path.exists():
        # No data — gate passes vacuously
        sys.exit(0)

    lines = jsonl_path.read_text(encoding="utf-8").splitlines()
    non_empty = [line.strip() for line in lines if line.strip()]
    if not non_empty:
        # File exists but empty — gate passes vacuously
        sys.exit(0)

    last_line = non_empty[-1]
    record = json.loads(last_line)

    # Import evaluation machinery from canonical SLO module
    from thegent.governance.slo_metrics import SloMetric, SloThresholds, evaluate

    thresholds = SloThresholds()
    metric = SloMetric(
        file_loc=record["file_loc"],
        function_loc_p95=record["function_loc_p95"],
        impl_importers=record["impl_importers"],
        cross_boundary_import_edges=record["cross_boundary_import_edges"],
        cli_help_p95_ms=record["cli_help_p95_ms"],
        run_command_p95_ms=record["run_command_p95_ms"],
        decomposition_checkpoint_pass_rate=record["decomposition_checkpoint_pass_rate"],
        timestamp=record.get("timestamp", ""),
        source=record.get("source", "unknown"),
    )

    results = evaluate(metric, thresholds)
    red_fields = {field: status for field, status in results.items() if status == "red"}

    if red_fields:
        print("SLO GATE FAILED — red violations detected:", file=sys.stderr)
        for field, status in red_fields.items():
            value = getattr(metric, field)
            print(f"  {field}: {status} (value={value})", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
