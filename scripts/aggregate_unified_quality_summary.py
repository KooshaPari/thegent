#!/usr/bin/env python3
"""Aggregate quality artifacts into a canonical unified summary."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_COMPONENTS: list[tuple[str, str]] = [
    ("quality_gate_result", "artifacts/hooks/quality-gate-result.json"),
    ("security_pipeline_result", "artifacts/hooks/security-pipeline-result.json"),
    ("hooks_sarif", "artifacts/hooks/hooks-results.sarif"),
    ("generated_python_json", "artifacts/quality/generated-python-antipatterns.json"),
    ("generated_python_sarif", "artifacts/quality/generated-python-antipatterns.sarif"),
    ("mutation_perf_pilot", "artifacts/quality/mutation-perf-pilot.json"),
    ("control_plane_readiness", "artifacts/quality/control-plane-readiness.json")
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/quality/unified-quality-summary.json"),
        help="Unified summary output path",
    )
    parser.add_argument(
        "--strict-missing",
        action="store_true",
        help="Mark missing components as fail instead of warn",
    )
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(value, dict):
        return None
    return value


def main() -> int:
    args = parse_args()
    components: list[dict[str, Any]] = []
    failures = 0
    warnings = 0

    for name, raw_path in DEFAULT_COMPONENTS:
        path = Path(raw_path)
        exists = path.exists()
        if not exists:
            status = "fail" if args.strict_missing else "warn"
            details = {"reason": "missing"}
            if status == "fail":
                failures += 1
            else:
                warnings += 1
        else:
            status = "ok"
            details: dict[str, Any] = {}
            payload = _read_json(path)
            if payload is not None:
                if payload.get("overall_status") == "failed":
                    status = "fail"
                    failures += 1
                elif payload.get("overall_status") == "warn":
                    status = "warn"
                    warnings += 1
                details = {
                    "schema_version": payload.get("schema_version"),
                    "reported_status": payload.get("status") or payload.get("overall_status"),
                }

        components.append(
            {
                "name": name,
                "status": status,
                "path": raw_path,
                "exists": exists,
                "details": details,
            }
        )

    overall_status = "fail" if failures > 0 else ("warn" if warnings > 0 else "ok")
    summary = {
        "schema_version": "unified-quality-summary/v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "overall_status": overall_status,
        "components": components,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
