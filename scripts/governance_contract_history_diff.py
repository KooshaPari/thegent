#!/usr/bin/env python3
"""Compare current governance contract report with previous run report."""

from __future__ import annotations

import argparse
import orjson as json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diff governance contract strict reports.")
    parser.add_argument("--prev-json", required=True, help="Path to previous report JSON")
    parser.add_argument("--current-json", required=True, help="Path to current report JSON")
    parser.add_argument("--json-out", required=True, help="Path for diff JSON output")
    parser.add_argument("--md-out", required=True, help="Path for diff Markdown output")
    return parser.parse_args()


def _load_optional(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _result_map(payload: dict) -> dict[str, dict]:
    return {entry["name"]: entry for entry in payload.get("results", [])}


def _render_md(diff: dict) -> str:
    out: list[str] = []
    out.append("### Governance Contract Strict Diff")
    out.append("")
    out.append(f"- Previous available: {diff['previous_available']}")
    out.append(f"- Current passed/failed: {diff['current_passed']}/{diff['current_failed']}")
    if diff["previous_available"]:
        out.append(f"- Previous passed/failed: {diff['previous_passed']}/{diff['previous_failed']}")
        out.append(f"- Passed delta: {diff['passed_delta']}")
        out.append(f"- Failed delta: {diff['failed_delta']}")
        out.append(f"- Changed checks: {len(diff['changed_checks'])}")
    out.append("")
    if diff["changed_checks"]:
        out.append("| Check | Prev OK | Curr OK |")
        out.append("|---|---|---|")
        for item in diff["changed_checks"]:
            out.append(f"| `{item['name']}` | {item['prev_ok']} | {item['curr_ok']} |")
        out.append("")
    return "\n".join(out)


def main() -> int:
    args = parse_args()
    prev_path = Path(args.prev_json)
    current_path = Path(args.current_json)

    prev_payload = _load_optional(prev_path)
    current_payload = json.loads(current_path.read_text(encoding="utf-8"))
    curr_map = _result_map(current_payload)

    diff = {
        "previous_available": prev_payload is not None,
        "current_passed": current_payload.get("passed", 0),
        "current_failed": current_payload.get("failed", 0),
        "previous_passed": 0,
        "previous_failed": 0,
        "passed_delta": 0,
        "failed_delta": 0,
        "changed_checks": [],
    }

    if prev_payload is not None:
        diff["previous_passed"] = prev_payload.get("passed", 0)
        diff["previous_failed"] = prev_payload.get("failed", 0)
        diff["passed_delta"] = diff["current_passed"] - diff["previous_passed"]
        diff["failed_delta"] = diff["current_failed"] - diff["previous_failed"]

        prev_map = _result_map(prev_payload)
        all_names = sorted(set(prev_map) | set(curr_map))
        changed: list[dict] = []
        for name in all_names:
            prev_entry = prev_map.get(name)
            curr_entry = curr_map.get(name)
            prev_ok = prev_entry["ok"] if prev_entry else None
            curr_ok = curr_entry["ok"] if curr_entry else None
            if prev_entry != curr_entry:
                changed.append({"name": name, "prev_ok": prev_ok, "curr_ok": curr_ok})
        diff["changed_checks"] = changed

    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(diff, indent=2).decode().decode() + "\n", encoding="utf-8")
    md_out.write_text(_render_md(diff), encoding="utf-8")
    print(md_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
