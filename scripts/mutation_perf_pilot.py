#!/usr/bin/env python3
"""Non-blocking mutation+performance pilot runner with JSON artifact output."""

from __future__ import annotations

import argparse
import orjson as json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/quality/mutation-perf-pilot.json"),
        help="Unified pilot artifact output",
    )
    parser.add_argument(
        "--perf-output",
        type=Path,
        default=Path("artifacts/quality/perf-smoke.json"),
        help="Performance smoke artifact output",
    )
    parser.add_argument("--perf-iterations", type=int, default=5000, help="Iterations for benchmark_python_suite")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any failed phase")
    return parser.parse_args()


def run_command(cmd: list[str], timeout: int = 900) -> dict[str, Any]:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def main() -> int:
    args = parse_args()

    phases: list[dict[str, Any]] = []
    failed = False

    perf_cmd = [
        sys.executable,
        "scripts/benchmark_python_suite.py",
        "--iterations",
        str(max(1, args.perf_iterations)),
        "--output",
        str(args.perf_output),
        "--overwrite",
    ]
    perf_result = run_command(perf_cmd, timeout=600)
    perf_status = "passed" if perf_result["returncode"] == 0 else "failed"
    phases.append(
        {
            "name": "perf_smoke",
            "status": perf_status,
            "artifact": str(args.perf_output),
            "details": perf_result,
        }
    )
    if perf_status == "failed":
        failed = True

    mutmut = shutil.which("mutmut")
    if not mutmut:
        phases.append(
            {
                "name": "mutation_smoke",
                "status": "skipped",
                "reason": "mutmut_not_available",
            }
        )
    else:
        mutation_cmd = [
            mutmut,
            "run",
            "--paths-to-mutate",
            "src/thegent/contracts",
            "--tests-dir",
            "tests",
            "--runner",
            f"{sys.executable} -m pytest -q tests/test_unit_contracts.py",
        ]
        mutation_result = run_command(mutation_cmd, timeout=1800)
        mutation_status = "passed" if mutation_result["returncode"] == 0 else "failed"
        phases.append(
            {
                "name": "mutation_smoke",
                "status": mutation_status,
                "details": mutation_result,
            }
        )
        if mutation_status == "failed":
            failed = True

    artifact = {
        "schema_version": "mutation-perf-pilot/v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "strict_mode": bool(args.strict),
        "overall_status": "failed" if failed else "passed",
        "phases": phases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2).decode().decode() + "\n", encoding="utf-8")
    print(f"Wrote pilot artifact: {args.output}")

    if args.strict and failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
