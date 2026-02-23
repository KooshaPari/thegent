#!/usr/bin/env python3
"""Generate governance contract strict comparison reports for CI artifacts."""

from __future__ import annotations

import argparse
import hashlib
import orjson as json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _dispatcher_bin(repo_root: Path) -> Path:
    return repo_root / "hooks" / "hook-dispatcher" / "target" / "debug" / "hook-dispatcher"


def _run(dispatcher: Path, args: list[str], repo_root: Path) -> dict:
    proc = subprocess.run(
        [str(dispatcher), "governance", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(args)}\n{proc.stderr}")
    return json.loads(proc.stdout)


def _selector_snapshot_results(repo_root: Path, dispatcher: Path) -> list[CheckResult]:
    fixture = repo_root / "tests" / "fixtures" / "governance" / "spiral_selector_contract_snapshot.json"
    snapshot = json.loads(fixture.read_text(encoding="utf-8"))
    results: list[CheckResult] = []
    for case in snapshot["cases"]:
        got = _run(dispatcher, ["spiral-selector", "--format", "json", case["input"]], repo_root)
        ok = got == case["expected"]
        results.append(
            CheckResult(
                name=f"selector::{case['input']!r}",
                ok=ok,
                details=f"expected={case['expected']} got={got}",
            )
        )
    return results


def _trend_replay_results(repo_root: Path, dispatcher: Path) -> list[CheckResult]:
    fixture_root = repo_root / "tests" / "fixtures" / "governance"
    manifest = json.loads((fixture_root / "spiral_trend_replay_manifest.json").read_text(encoding="utf-8"))
    replay_dir = fixture_root / "replay"
    results: list[CheckResult] = []
    for case in manifest["cases"]:
        metrics_file = replay_dir / case["file"]
        got = _run(dispatcher, ["spiral-trend", str(metrics_file), "--window", "50"], repo_root)
        band_ok = got["policy_band"] == case["expected_band"]
        pressure_ok = case["min_pressure"] <= got["pressure_score"] <= case["max_pressure"]
        status_ok = got["latest_status"] == case["latest_status"]
        ok = band_ok and pressure_ok and status_ok
        results.append(
            CheckResult(
                name=f"trend::{case['file']}",
                ok=ok,
                details=(
                    f"band expected={case['expected_band']} got={got['policy_band']}; "
                    f"pressure expected_range=[{case['min_pressure']},{case['max_pressure']}] got={got['pressure_score']}; "
                    f"latest_status expected={case['latest_status']} got={got['latest_status']}"
                ),
            )
        )
    return results


def _fixture_digest_results(repo_root: Path) -> list[CheckResult]:
    manifest_path = repo_root / "tests" / "fixtures" / "governance" / "fixture_digests.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent
    files = manifest.get("files", [])
    results: list[CheckResult] = []

    for item in files:
        rel = item["path"]
        expected = item["sha256"]
        file_path = root / rel
        h = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        actual = h.hexdigest()
        ok = actual == expected
        results.append(
            CheckResult(
                name=f"digest::{rel}",
                ok=ok,
                details=f"expected={expected} got={actual}",
            )
        )

    lines = [f"{item['path']}:{item['sha256']}" for item in sorted(files, key=lambda x: x["path"])]
    aggregate = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    expected_signature = manifest.get("signed_digest", "")
    results.append(
        CheckResult(
            name="digest::signed_digest",
            ok=aggregate == expected_signature,
            details=f"expected={expected_signature} got={aggregate}",
        )
    )
    return results


def _render_markdown(results: list[CheckResult]) -> str:
    ok_count = sum(1 for r in results if r.ok)
    out: list[str] = []
    out.append("### Governance Contract Strict Report")
    out.append("")
    out.append(f"- Total checks: {len(results)}")
    out.append(f"- Passed: {ok_count}")
    out.append(f"- Failed: {len(results) - ok_count}")
    out.append("")
    out.append("| Check | Status | Details |")
    out.append("|---|---|---|")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        out.append(f"| `{result.name}` | {status} | {result.details} |")
    out.append("")
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate governance contract strict artifact reports.")
    parser.add_argument("--json-out", required=True, help="Path for JSON report output.")
    parser.add_argument("--md-out", required=True, help="Path for Markdown report output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = _repo_root()
    dispatcher = _dispatcher_bin(repo_root)
    if not dispatcher.exists():
        raise SystemExit(f"Missing hook-dispatcher binary at {dispatcher}. Build it first.")

    selector_results = _selector_snapshot_results(repo_root, dispatcher)
    trend_results = _trend_replay_results(repo_root, dispatcher)
    digest_results = _fixture_digest_results(repo_root)
    results = selector_results + trend_results + digest_results

    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "total": len(results),
        "passed": sum(1 for r in results if r.ok),
        "failed": sum(1 for r in results if not r.ok),
        "results": [{"name": r.name, "ok": r.ok, "details": r.details} for r in results],
    }
    json_out.write_text(json.dumps(payload, indent=2).decode().decode() + "\n", encoding="utf-8")
    md_out.write_text(_render_markdown(results), encoding="utf-8")
    print(md_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
