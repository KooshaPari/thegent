#!/usr/bin/env python3
"""Evaluate unified quality summary and return gate status."""

from __future__ import annotations

import argparse
import orjson as json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("artifacts/quality/unified-quality-summary.json"),
        help="Unified quality summary path",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("contracts/unified-quality-gate-policy-v1.json"),
        help="Gate policy contract path",
    )
    parser.add_argument(
        "--mode",
        choices=["pr", "nightly"],
        default="pr",
        help="Gate evaluation mode",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Backward-compatible alias for nightly mode",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mode = "nightly" if args.strict else args.mode
    policy_payload: dict[str, Any] = json.loads(args.policy.read_text(encoding="utf-8"))
    fail_if_missing = bool(policy_payload.get("fail_if_summary_missing", True))
    mode_policy = (policy_payload.get("modes", {}) or {}).get(mode, {})
    fail_on_overall = set(mode_policy.get("fail_on_overall", ["fail"]))
    warn_statuses = set(mode_policy.get("warn_statuses", ["warn", "missing"]))
    max_warn_components = int(mode_policy.get("max_warn_components", 0))
    allowed_missing = set(mode_policy.get("allowed_missing_components", []))

    if not args.summary.exists():
        print("UNIFIED_QUALITY_GATE: missing summary artifact")
        return 1 if fail_if_missing else 0

    payload: dict[str, Any] = json.loads(args.summary.read_text(encoding="utf-8"))
    overall = str(payload.get("overall_status", "unknown"))
    components = payload.get("components", [])
    if not isinstance(components, list):
        components = []

    warn_components = [
        row for row in components if isinstance(row, dict) and str(row.get("status", "")) in warn_statuses
    ]
    missing_components = [
        str(row.get("name", "unknown"))
        for row in warn_components
        if isinstance(row.get("details"), dict) and row["details"].get("reason") == "missing"
    ]
    disallowed_missing = [name for name in missing_components if name not in allowed_missing]

    decision = {
        "mode": mode,
        "overall": overall,
        "component_count": len(components),
        "warn_component_count": len(warn_components),
        "max_warn_components": max_warn_components,
        "missing_components": missing_components,
        "disallowed_missing_components": disallowed_missing,
        "fail_on_overall": sorted(fail_on_overall),
    }
    print(f"UNIFIED_QUALITY_GATE: {json.dumps(decision, sort_keys=True).decode().decode()}")

    if overall in fail_on_overall:
        return 1
    if len(warn_components) > max_warn_components:
        return 1
    if disallowed_missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
