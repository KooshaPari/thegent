#!/usr/bin/env python3
"""WL-138 B90-W2-B5: Decomposition progress tracker.

Reads Wave-1 and Wave-2 B90 agent artifacts and produces a structured JSON
progress summary, then writes it to
docs/reports/artifacts/decomposition-progress-w2.json.

Requirements:
- stdlib only (pathlib, json, datetime, sys)
- No external dependencies

Usage:
    python scripts/decomposition_progress.py
"""

from __future__ import annotations

import orjson as json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ARTIFACTS_DIR = REPO_ROOT / "docs" / "reports" / "artifacts"
OUTPUT_PATH = ARTIFACTS_DIR / "decomposition-progress-w2.json"


# ---------------------------------------------------------------------------
# Item catalogue — B90 Wave-2 agent-b items being tracked
# ---------------------------------------------------------------------------

B90_W2_B_ITEMS = [
    {
        "item_id": "B90-W2-B1",
        "wl_id": "WL-130",
        "description": "Implement runtime matrix as machine-readable artifact",
        "artifact_paths": [
            "contracts/runtime/runtime-modularization-matrix.json",
            "tests/test_wl130_runtime_matrix.py",
        ],
    },
    {
        "item_id": "B90-W2-B2",
        "wl_id": "WL-131",
        "description": "Migrate Batch-A parser/helper function set to Rust",
        "artifact_paths": [
            "crates/thegent-parser/src/lib.rs",
            "tests/routing/test_wl131_parser_parity.py",
        ],
    },
    {
        "item_id": "B90-W2-B3",
        "wl_id": "WL-132",
        "description": "Implement Zig ABI contract version assertions",
        "artifact_paths": [
            "crates/thegent-zmx-interop/src/lib.rs",
            "tests/test_wl132_zig_abi_contract.py",
        ],
    },
    {
        "item_id": "B90-W2-B4",
        "wl_id": "WL-133",
        "description": "Implement deterministic Mojo kernel smoke check",
        "artifact_paths": [
            "tests/mojo/test_wl133_mojo_kernel_smoke.py",
            "tests/mojo/fixtures/deterministic_score_v1.json",
        ],
    },
    {
        "item_id": "B90-W2-B5",
        "wl_id": "WL-138",
        "description": "Add decomposition progress tracker output",
        "artifact_paths": [
            "scripts/decomposition_progress.py",
            "tests/test_wl138_decomposition_progress.py",
        ],
    },
]


def _collect_wave1_artifacts(artifacts_dir: Path) -> list[dict]:
    """Collect all Wave-1 agent artifact JSON files."""
    results = []
    pattern = "2026-02-21-B90-W1-agent-*.json"
    for artifact_file in sorted(artifacts_dir.glob(pattern)):
        try:
            data = json.loads(artifact_file.read_text())
            results.append(
                {
                    "file": artifact_file.name,
                    "report_id": data.get("report_id", artifact_file.stem),
                    "keys": list(data.keys()),
                }
            )
        except (json.JSONDecodeError, OSError) as exc:
            results.append(
                {
                    "file": artifact_file.name,
                    "error": str(exc),
                }
            )
    return results


def _check_item_completion(item: dict) -> dict:
    """Determine whether an item's artifact paths exist on disk."""
    completed_paths = []
    missing_paths = []
    for rel_path in item["artifact_paths"]:
        full = REPO_ROOT / rel_path
        if full.exists():
            completed_paths.append(rel_path)
        else:
            missing_paths.append(rel_path)

    status = "complete" if not missing_paths else "partial" if completed_paths else "pending"
    return {
        "item_id": item["item_id"],
        "wl_id": item["wl_id"],
        "description": item["description"],
        "status": status,
        "completed_paths": completed_paths,
        "missing_paths": missing_paths,
    }


def _identify_blockers(checked_items: list[dict]) -> list[dict]:
    """Return items that are not fully complete."""
    return [
        {
            "item_id": it["item_id"],
            "wl_id": it["wl_id"],
            "reason": f"Missing artifact paths: {it['missing_paths']}",
        }
        for it in checked_items
        if it["missing_paths"]
    ]


def build_progress_summary() -> dict:
    """Build the full progress summary dict."""
    wave1_artifacts = _collect_wave1_artifacts(ARTIFACTS_DIR)
    checked_items = [_check_item_completion(item) for item in B90_W2_B_ITEMS]
    completed_items = [it for it in checked_items if it["status"] == "complete"]
    blockers = _identify_blockers(checked_items)

    # Next wave deps: items that are partial or pending represent open threads
    next_wave_deps = [f"{it['wl_id']}: {it['description']}" for it in checked_items if it["status"] != "complete"]

    return {
        "wave": 2,
        "agent": "b",
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "source_artifacts_dir": str(ARTIFACTS_DIR.relative_to(REPO_ROOT)),
        "wave1_artifacts_found": wave1_artifacts,
        "items": checked_items,
        "completed_items": [it["item_id"] for it in completed_items],
        "total_items": len(checked_items),
        "complete_count": len(completed_items),
        "completion_pct": round(len(completed_items) / len(checked_items) * 100, 1),
        "blockers": blockers,
        "next_wave_deps": next_wave_deps,
    }


def main() -> int:
    """Entry point."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    summary = build_progress_summary()
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2).decode().decode() + "\n")

    print(f"[decomposition_progress] wrote {OUTPUT_PATH}")
    print(
        f"  wave={summary['wave']} agent={summary['agent']} "
        f"complete={summary['complete_count']}/{summary['total_items']} "
        f"({summary['completion_pct']}%)"
    )
    if summary["blockers"]:
        print(f"  blockers: {len(summary['blockers'])}")
        for b in summary["blockers"]:
            print(f"    - [{b['item_id']}] {b['reason']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
