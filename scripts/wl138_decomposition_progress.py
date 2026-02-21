#!/usr/bin/env python3
"""Emit WL-138 decomposition progress as a machine-readable artifact."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "reports" / "artifacts" / "wl138_decomposition_progress.json"


CHECKPOINTS = [
    {
        "checkpoint_id": "python-monolith-cuts",
        "description": "Python command/server decomposition scaffolding exists",
        "paths": [
            "src/thegent/cli/commands/helpers.py",
            "src/thegent/mcp/server_runtime_helpers.py",
        ],
    },
    {
        "checkpoint_id": "rust-hook-splits",
        "description": "Rust hook dispatcher decomposition folders exist and execute via Rust tests",
        "paths": [
            "hooks/hook-dispatcher/src/dispatch",
            "hooks/hook-dispatcher/src/contract",
            "hooks/hook-dispatcher/src/io",
        ],
        "execution_gates": [
            {
                "gate_id": "rust-hook-dispatcher-tests",
                "description": "hook-dispatcher decomposition modules compile + tests execute",
                "command": [
                    "cargo",
                    "test",
                    "-q",
                    "--manifest-path",
                    "hooks/hook-dispatcher/Cargo.toml",
                ],
            }
        ],
    },
    {
        "checkpoint_id": "zig-abi-gate",
        "description": "Zig ABI contract + promotion checks execute",
        "paths": [
            "contracts/runtime/zig_abi_contract_v1.json",
            "scripts/validate_zig_abi_contract.py",
            "scripts/check_zig_abi_artifact.py",
            "tests/fixtures/runtime/zig_abi_symbols_fixture.txt",
            "tests/fixtures/runtime/zig_abi_error_envelope_fixture.json",
        ],
        "execution_gates": [
            {
                "gate_id": "zig-contract-validation",
                "description": "contract schema and readiness gates validate",
                "command": [
                    sys.executable,
                    "scripts/validate_zig_abi_contract.py",
                    "--contract",
                    "contracts/runtime/zig_abi_contract_v1.json",
                ],
            },
            {
                "gate_id": "zig-abi-artifact-check",
                "description": "required symbols + error envelope pass artifact check",
                "command": [
                    sys.executable,
                    "scripts/check_zig_abi_artifact.py",
                    "--contract",
                    "contracts/runtime/zig_abi_contract_v1.json",
                    "--symbols-file",
                    "tests/fixtures/runtime/zig_abi_symbols_fixture.txt",
                    "--error-envelope-json",
                    "tests/fixtures/runtime/zig_abi_error_envelope_fixture.json",
                ],
            },
        ],
    },
    {
        "checkpoint_id": "mojo-gate",
        "description": "Mojo contract + promotion gate outcome tests execute",
        "paths": [
            "contracts/runtime/mojo_kernel_contract_v1.json",
            "scripts/mojo_score_rank_harness.py",
            "tests/test_mojo_score_rank_harness.py",
        ],
        "execution_gates": [
            {
                "gate_id": "mojo-promotion-gate-outcomes",
                "description": "harness smoke + enforced promotion-gate behavior are verified",
                "command": [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_mojo_score_rank_harness.py::test_run_smoke_with_fake_mojo",
                    "tests/test_mojo_score_rank_harness.py::test_run_enforces_promotion_gate_by_default",
                ],
            }
        ],
    },
    {
        "checkpoint_id": "runtime-matrix-artifacts",
        "description": "Wave-2 runtime and migration artifacts are present",
        "paths": [
            "contracts/runtime/runtime-modularization-matrix.json",
            "contracts/runtime/wl131_batch_a_rust_migration_v1.json",
        ],
    },
]


def _command_result(command: list[str], root: Path) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "status": "pass" if completed.returncode == 0 else "fail",
        "exit_code": completed.returncode,
        "duration_ms": elapsed_ms,
        "stdout_tail": (completed.stdout or "").strip().splitlines()[-5:],
        "stderr_tail": (completed.stderr or "").strip().splitlines()[-5:],
    }


def _execution_gates_result(
    root: Path, item: dict[str, Any], *, skip_execution_gates: bool
) -> tuple[list[dict[str, Any]], bool, int, int]:
    gates = item.get("execution_gates", [])
    if not gates:
        return [], True, 0, 0

    results: list[dict[str, Any]] = []
    passed = 0
    for gate in gates:
        command = gate["command"]
        if skip_execution_gates:
            gate_result = {
                "status": "skipped",
                "exit_code": None,
                "duration_ms": 0.0,
                "stdout_tail": [],
                "stderr_tail": [],
            }
        else:
            gate_result = _command_result(command, root)
            if gate_result["status"] == "pass":
                passed += 1

        results.append(
            {
                "gate_id": gate["gate_id"],
                "description": gate["description"],
                "command": " ".join(shlex.quote(part) for part in command),
                **gate_result,
            }
        )

    total = len(gates)
    gates_complete = (passed == total) and not skip_execution_gates
    return results, gates_complete, passed, total


def _checkpoint_result(root: Path, item: dict[str, Any], *, skip_execution_gates: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    paths_complete = True
    for rel_path in item["paths"]:
        path = root / rel_path
        exists = path.exists()
        checks.append({"path": rel_path, "exists": exists})
        if not exists:
            paths_complete = False

    execution_gates, gates_complete, passed_gates, total_gates = _execution_gates_result(
        root,
        item,
        skip_execution_gates=skip_execution_gates,
    )

    complete = paths_complete and gates_complete
    return {
        "checkpoint_id": item["checkpoint_id"],
        "description": item["description"],
        "complete": complete,
        "checks": checks,
        "execution_gates": execution_gates,
        "evaluation": {
            "paths_complete": paths_complete,
            "execution_gates_complete": gates_complete,
            "passed_execution_gates": passed_gates,
            "total_execution_gates": total_gates,
            "execution_gates_skipped": skip_execution_gates,
        },
    }


def build_progress(root: Path, *, skip_execution_gates: bool) -> dict[str, Any]:
    checkpoints = [_checkpoint_result(root, item, skip_execution_gates=skip_execution_gates) for item in CHECKPOINTS]
    complete_count = sum(1 for item in checkpoints if item["complete"])
    total = len(checkpoints)
    complete_execution_gates = sum(
        checkpoint["evaluation"]["passed_execution_gates"] for checkpoint in checkpoints
    )
    total_execution_gates = sum(
        checkpoint["evaluation"]["total_execution_gates"] for checkpoint in checkpoints
    )
    return {
        "workstream_id": "WL-138",
        "artifact_id": "wl138.decomposition_progress.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "complete_checkpoints": complete_count,
        "total_checkpoints": total,
        "completion_pct": round((complete_count / total) * 100, 2) if total else 0.0,
        "execution_gates": {
            "complete": complete_execution_gates,
            "total": total_execution_gates,
            "completion_pct": round((complete_execution_gates / total_execution_gates) * 100, 2)
            if total_execution_gates
            else 0.0,
            "skipped": skip_execution_gates,
        },
        "checkpoints": checkpoints,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate WL-138 decomposition progress artifact.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSON path.",
    )
    parser.add_argument(
        "--skip-execution-gates",
        action="store_true",
        help="Skip command execution gates and emit only path-level evaluation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_progress(REPO_ROOT, skip_execution_gates=args.skip_execution_gates)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote WL-138 progress artifact: {args.output}")
    print(
        f"completion: {payload['complete_checkpoints']}/{payload['total_checkpoints']} "
        f"({payload['completion_pct']}%)"
    )
    print(
        f"execution gates: {payload['execution_gates']['complete']}/{payload['execution_gates']['total']} "
        f"({payload['execution_gates']['completion_pct']}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
