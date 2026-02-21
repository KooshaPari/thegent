from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_wl138_progress_script_emits_json(tmp_path: Path) -> None:
    repo_root = _repo_root()
    script = repo_root / "scripts" / "wl138_decomposition_progress.py"
    output = tmp_path / "progress.json"

    result = subprocess.run(
        [sys.executable, str(script), "--output", str(output), "--skip-execution-gates"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["workstream_id"] == "WL-138"
    assert payload["artifact_id"] == "wl138.decomposition_progress.v1"
    assert payload["total_checkpoints"] >= 5
    assert payload["complete_checkpoints"] <= payload["total_checkpoints"]
    assert payload["execution_gates"]["skipped"] is True

    runtime_matrix_checkpoint = next(
        item for item in payload["checkpoints"] if item["checkpoint_id"] == "runtime-matrix-artifacts"
    )
    matrix_paths = [check["path"] for check in runtime_matrix_checkpoint["checks"]]
    assert "contracts/runtime/runtime-modularization-matrix.json" in matrix_paths

    rust_checkpoint = next(item for item in payload["checkpoints"] if item["checkpoint_id"] == "rust-hook-splits")
    assert rust_checkpoint["evaluation"]["total_execution_gates"] >= 1
    assert rust_checkpoint["execution_gates"][0]["status"] == "skipped"


def test_build_progress_fails_checkpoint_when_execution_gate_fails() -> None:
    repo_root = _repo_root()
    script = repo_root / "scripts" / "wl138_decomposition_progress.py"
    namespace: dict[str, object] = {"__file__": str(script)}
    exec(script.read_text(encoding="utf-8"), namespace)

    checkpoint = {
        "checkpoint_id": "fake-checkpoint",
        "description": "fake",
        "paths": ["README.md"],
        "execution_gates": [
            {
                "gate_id": "failing-gate",
                "description": "fails",
                "command": [sys.executable, "-c", "raise SystemExit(7)"],
            }
        ],
    }

    result = namespace["_checkpoint_result"](repo_root, checkpoint, skip_execution_gates=False)
    assert result["evaluation"]["paths_complete"] is True
    assert result["evaluation"]["execution_gates_complete"] is False
    assert result["complete"] is False
    assert result["execution_gates"][0]["status"] == "fail"
    assert result["execution_gates"][0]["exit_code"] == 7
