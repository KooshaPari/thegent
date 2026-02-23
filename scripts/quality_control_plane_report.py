#!/usr/bin/env python3
"""Emit control-plane readiness report for required quality artifacts."""

from __future__ import annotations

import argparse
import orjson as json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("contracts/quality-control-plane-v1.json"),
        help="Control-plane contract path",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("artifacts/quality/control-plane-readiness.json"),
        help="Output JSON report",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=Path("artifacts/quality/control-plane-readiness.md"),
        help="Output markdown report",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.contract.read_text(encoding="utf-8"))
    required = [Path(p) for p in payload.get("required_artifacts", [])]
    rows = []
    present = 0
    for path in required:
        exists = path.exists()
        if exists:
            present += 1
        rows.append({"path": str(path), "exists": exists})

    total = len(rows)
    ratio = (present / total) if total else 1.0
    out = {
        "schema_version": "quality-control-plane-readiness/v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "selected_plane": payload.get("selected_plane"),
        "required_artifacts_total": total,
        "required_artifacts_present": present,
        "presence_ratio": round(ratio, 4),
        "artifacts": rows,
    }

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(out, indent=2).decode().decode() + "\n", encoding="utf-8")

    lines = [
        "# Control Plane Readiness",
        "",
        f"- selected_plane: `{out['selected_plane']}`",
        f"- required_artifacts_present: `{present}/{total}`",
        f"- presence_ratio: `{out['presence_ratio']}`",
        "",
        "| Artifact | Exists |",
        "| --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['path']}` | `{'yes' if row['exists'] else 'no'}` |")
    args.md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote: {args.json_out}")
    print(f"Wrote: {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
