#!/usr/bin/env python3
"""Export thegent hook result envelopes to SARIF 2.1.0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", nargs="+", required=True, help="Hook result JSON file(s)")
    parser.add_argument("--output", required=True, help="SARIF output path")
    parser.add_argument("--tool-name", default="thegent-hooks", help="SARIF tool name")
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Skip missing input files instead of failing",
    )
    return parser.parse_args()


def _level_for_status(status: str) -> str | None:
    if status == "failed":
        return "error"
    if status == "warn":
        return "warning"
    return None


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root JSON value must be object")
    return data


def build_sarif(input_paths: list[Path], tool_name: str) -> dict[str, Any]:
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []

    for path in input_paths:
        payload = _load_json(path)
        hook = str(payload.get("hook", "unknown"))
        checks = payload.get("checks", [])
        if not isinstance(checks, list):
            continue
        for check in checks:
            if not isinstance(check, dict):
                continue
            name = str(check.get("name", "unknown-check"))
            status = str(check.get("status", "unknown"))
            level = _level_for_status(status)
            if level is None:
                continue
            rule_id = f"{hook}:{name}:{status}"
            rules.setdefault(
                rule_id,
                {
                    "id": rule_id,
                    "name": name,
                    "shortDescription": {"text": f"{hook} check {name}"},
                    "help": {"text": "thegent hook check outcome"},
                },
            )
            results.append(
                {
                    "ruleId": rule_id,
                    "level": level,
                    "message": {"text": f"{hook} check '{name}' reported status '{status}'"},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": str(path)}
                            }
                        }
                    ],
                }
            )

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "informationUri": "https://github.com/kooshapari/thegent",
                        "rules": sorted(rules.values(), key=lambda r: r["id"]),
                    }
                },
                "results": results,
            }
        ],
    }


def main() -> int:
    args = parse_args()
    inputs: list[Path] = []
    for raw in args.input:
        path = Path(raw)
        if not path.exists():
            if args.allow_missing:
                continue
            raise FileNotFoundError(f"Missing input: {path}")
        inputs.append(path)

    sarif = build_sarif(inputs, tool_name=args.tool_name)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(sarif, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
