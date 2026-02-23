#!/usr/bin/env python3
from __future__ import annotations

import argparse
import orjson as json
import math
import random
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTRACT_PATH = REPO_ROOT / "contracts" / "runtime" / "mojo_kernel_contract_v1.json"
DEFAULT_FIXTURE_ROOT = REPO_ROOT / "benchmarks" / "fixtures" / "mojo_score_rank_v1"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "benchmarks" / "results" / "mojo_score_rank_v1_latest.json"
DEFAULT_DATASET_SIZES: dict[str, int] = {
    "small-128": 128,
    "medium-1024": 1024,
    "large-8192": 8192,
}


@dataclass(frozen=True)
class KernelContract:
    absolute_error_max: float
    rank_order_exact: bool
    datasets: list[str]
    promotion_gate: dict[str, float | int]
    input_validator: Any
    output_validator: Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic benchmark harness for score.rank.v1 (Mojo vs Python baseline)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen = subparsers.add_parser("generate-fixtures", help="Generate deterministic fixtures with expected outputs.")
    gen.add_argument("--output-root", type=Path, default=DEFAULT_FIXTURE_ROOT)
    gen.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    gen.add_argument("--seed", type=int, default=1337)
    gen.add_argument("--small-cases", type=int, default=DEFAULT_DATASET_SIZES["small-128"])
    gen.add_argument("--medium-cases", type=int, default=DEFAULT_DATASET_SIZES["medium-1024"])
    gen.add_argument("--large-cases", type=int, default=DEFAULT_DATASET_SIZES["large-8192"])

    run = subparsers.add_parser(
        "run", help="Run benchmark harness and compare Mojo kernel output against deterministic fixtures."
    )
    run.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    run.add_argument("--fixture-root", type=Path, default=DEFAULT_FIXTURE_ROOT)
    run.add_argument("--mojo-kernel", type=Path, required=True)
    run.add_argument("--mojo-bin", default="mojo")
    run.add_argument("--datasets", nargs="+", default=["small-128", "medium-1024", "large-8192"])
    run.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    run.add_argument(
        "--no-enforce-gates",
        action="store_true",
        help="Skip promotion gate enforcement and only write benchmark/correctness results.",
    )
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_type(name: str, value: Any, expected: type | tuple[type, ...]) -> None:
    if not isinstance(value, expected):
        raise ValueError(f"{name} must be {expected}, got {type(value)}")


def _validate_score_rank_input(payload: dict[str, Any]) -> None:
    _require_type("input", payload, dict)
    for key in ["request_id", "candidates", "weights"]:
        if key not in payload:
            raise ValueError(f"missing input field: {key}")
    _require_type("request_id", payload["request_id"], str)
    _require_type("candidates", payload["candidates"], list)
    _require_type("weights", payload["weights"], dict)
    for field in ["cost", "latency", "quality"]:
        if field not in payload["weights"]:
            raise ValueError(f"missing weights field: {field}")
        _require_type(f"weights.{field}", payload["weights"][field], (int, float))
    for idx, candidate in enumerate(payload["candidates"]):
        _require_type(f"candidates[{idx}]", candidate, dict)
        for field in ["id", "cost", "latency", "quality"]:
            if field not in candidate:
                raise ValueError(f"missing candidates[{idx}] field: {field}")
        _require_type(f"candidates[{idx}].id", candidate["id"], str)
        _require_type(f"candidates[{idx}].cost", candidate["cost"], (int, float))
        _require_type(f"candidates[{idx}].latency", candidate["latency"], (int, float))
        _require_type(f"candidates[{idx}].quality", candidate["quality"], (int, float))


def _validate_score_rank_output(payload: dict[str, Any]) -> None:
    _require_type("output", payload, dict)
    for key in ["request_id", "ranked"]:
        if key not in payload:
            raise ValueError(f"missing output field: {key}")
    _require_type("request_id", payload["request_id"], str)
    _require_type("ranked", payload["ranked"], list)
    for idx, item in enumerate(payload["ranked"]):
        _require_type(f"ranked[{idx}]", item, dict)
        for field in ["id", "score", "rank"]:
            if field not in item:
                raise ValueError(f"missing ranked[{idx}] field: {field}")
        _require_type(f"ranked[{idx}].id", item["id"], str)
        _require_type(f"ranked[{idx}].score", item["score"], (int, float))
        _require_type(f"ranked[{idx}].rank", item["rank"], int)


def load_contract(contract_path: Path) -> KernelContract:
    payload = _read_json(contract_path)
    correctness = payload["correctness_contract"]["parity_tolerance"]
    bench = payload["benchmark_contract"]
    return KernelContract(
        absolute_error_max=float(correctness["absolute_error_max"]),
        rank_order_exact=bool(correctness["rank_order_exact"]),
        datasets=list(bench["datasets"]),
        promotion_gate={
            "p95_speedup_vs_python_min": float(bench["promotion_gate"]["p95_speedup_vs_python_min"]),
            "p99_regression_max_pct": float(bench["promotion_gate"]["p99_regression_max_pct"]),
            "correctness_failures_allowed": int(bench["promotion_gate"]["correctness_failures_allowed"]),
        },
        input_validator=_validate_score_rank_input,
        output_validator=_validate_score_rank_output,
    )


def python_score_rank(payload: dict[str, Any]) -> dict[str, Any]:
    request_id = payload["request_id"]
    weights = payload["weights"]
    ranked = []
    for candidate in payload["candidates"]:
        score = (
            (weights["quality"] * candidate["quality"])
            - (weights["cost"] * candidate["cost"])
            - (weights["latency"] * candidate["latency"])
        )
        ranked.append({"id": candidate["id"], "score": score})

    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    ordered = [{"id": item["id"], "score": item["score"], "rank": idx + 1} for idx, item in enumerate(ranked)]
    return {"request_id": request_id, "ranked": ordered}


def _norm_weights(rng: random.Random) -> dict[str, float]:
    raw = {
        "cost": rng.uniform(0.05, 1.0),
        "latency": rng.uniform(0.0005, 0.01),
        "quality": rng.uniform(0.2, 2.0),
    }
    total = sum(raw.values())
    return {k: (v / total) for k, v in raw.items()}


def _build_input(rng: random.Random, case_idx: int) -> dict[str, Any]:
    candidate_count = rng.randint(6, 20)
    candidates = []
    for cand_idx in range(candidate_count):
        candidates.append(
            {
                "id": f"cand-{case_idx:05d}-{cand_idx:02d}",
                "cost": round(rng.uniform(0.01, 5.0), 6),
                "latency": round(rng.uniform(10.0, 2500.0), 6),
                "quality": round(rng.uniform(0.0, 1.0), 6),
            }
        )
    return {
        "request_id": f"req-{case_idx:08d}",
        "candidates": candidates,
        "weights": _norm_weights(rng),
    }


def _fixture_name(dataset_id: str) -> str:
    return dataset_id.replace("-", "_") + ".json"


def generate_fixtures(args: argparse.Namespace) -> int:
    contract = load_contract(args.contract)
    dataset_sizes = {
        "small-128": int(args.small_cases),
        "medium-1024": int(args.medium_cases),
        "large-8192": int(args.large_cases),
    }

    args.output_root.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    generated = {}
    for dataset_id in contract.datasets:
        case_count = dataset_sizes[dataset_id]
        cases: list[dict[str, Any]] = []
        for case_idx in range(case_count):
            payload = _build_input(rng, case_idx)
            expected = python_score_rank(payload)
            contract.input_validator(payload)
            contract.output_validator(expected)
            cases.append({"input": payload, "expected_output": expected})
        fixture = {
            "kernel_id": "score.rank.v1",
            "dataset_id": dataset_id,
            "seed": args.seed,
            "case_count": case_count,
            "cases": cases,
        }
        out_path = args.output_root / _fixture_name(dataset_id)
        out_path.write_text(json.dumps(fixture, sort_keys=True).decode().decode() + "\n", encoding="utf-8")
        generated[dataset_id] = str(out_path)

    manifest = {
        "kernel_id": "score.rank.v1",
        "seed": args.seed,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "fixtures": generated,
    }
    manifest_path = args.output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True).decode().decode() + "\n", encoding="utf-8")
    print(f"Wrote deterministic fixtures: {args.output_root}")
    print(f"Wrote manifest: {manifest_path}")
    return 0


def _require_mojo(mojo_bin: str) -> str:
    resolved = shutil.which(mojo_bin)
    if resolved is None:
        message = (
            f"Mojo executable not found on PATH (expected '{mojo_bin}').\n"
            "Install Mojo: https://docs.modular.com/mojo/manual/get-started/\n"
            "Then rerun: python3 scripts/mojo_score_rank_harness.py run --mojo-kernel <path/to/score_rank.mojo>"
        )
        raise RuntimeError(message)
    return resolved


def _load_fixture(fixture_root: Path, dataset_id: str) -> dict[str, Any]:
    path = fixture_root / _fixture_name(dataset_id)
    if not path.exists():
        raise FileNotFoundError(
            f"Missing fixture file: {path}. Generate fixtures first with "
            f"'python3 scripts/mojo_score_rank_harness.py generate-fixtures --output-root {fixture_root}'."
        )
    return _read_json(path)


def _percentile_ms(samples_ms: list[float], pct: float) -> float:
    if not samples_ms:
        return 0.0
    ordered = sorted(samples_ms)
    rank = max(0, math.ceil((pct / 100.0) * len(ordered)) - 1)
    return ordered[rank]


def _rss_mb(kind: int) -> float:
    usage = resource.getrusage(kind)
    value = float(usage.ru_maxrss)
    if sys.platform == "darwin":
        return value / (1024.0 * 1024.0)
    return value / 1024.0


def _run_mojo_once(mojo_bin: str, kernel_file: Path, payload: dict[str, Any]) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        tmp.write(json.dumps(payload).decode().decode())
        tmp_path = Path(tmp.name)
    try:
        result = subprocess.run(
            [mojo_bin, "run", str(kernel_file), "--input-json", str(tmp_path)],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Mojo kernel execution failed.\n"
            f"Command: {exc.cmd}\n"
            f"Exit code: {exc.returncode}\n"
            f"stderr: {exc.stderr.strip()}"
        ) from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    stdout = result.stdout.strip()
    if not stdout:
        raise RuntimeError("Mojo kernel returned empty stdout; expected JSON payload.")
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    raise RuntimeError(f"Mojo kernel stdout did not contain valid JSON. Raw stdout:\n{stdout}")


def _compare_outputs(
    expected: dict[str, Any],
    actual: dict[str, Any],
    *,
    abs_error_max: float,
    rank_order_exact: bool,
) -> list[str]:
    failures: list[str] = []
    if expected["request_id"] != actual.get("request_id"):
        failures.append("request_id_mismatch")
    expected_ranked = expected["ranked"]
    actual_ranked = actual.get("ranked", [])
    if len(expected_ranked) != len(actual_ranked):
        failures.append("ranked_length_mismatch")
        return failures

    expected_ids = [item["id"] for item in expected_ranked]
    actual_ids = [item.get("id") for item in actual_ranked]
    if rank_order_exact and expected_ids != actual_ids:
        failures.append("rank_order_mismatch")

    expected_scores = {item["id"]: float(item["score"]) for item in expected_ranked}
    for idx, item in enumerate(actual_ranked, start=1):
        item_id = item.get("id")
        if item.get("rank") != idx:
            failures.append(f"rank_value_mismatch:{item_id}")
        if item_id not in expected_scores:
            failures.append(f"unknown_candidate:{item_id}")
            continue
        observed = float(item.get("score", 0.0))
        if abs(observed - expected_scores[item_id]) > abs_error_max:
            failures.append(f"score_error:{item_id}")
    return failures


def run_harness(args: argparse.Namespace) -> int:
    contract = load_contract(args.contract)
    mojo_bin = _require_mojo(args.mojo_bin)
    if not args.mojo_kernel.exists():
        raise FileNotFoundError(f"Mojo kernel file not found: {args.mojo_kernel}")

    unknown = sorted(set(args.datasets) - set(contract.datasets))
    if unknown:
        raise ValueError(f"Unknown dataset ids requested: {unknown}. Allowed: {contract.datasets}")

    result_datasets: list[dict[str, Any]] = []
    total_failures = 0
    gate_failures: list[dict[str, Any]] = []
    for dataset_id in args.datasets:
        fixture = _load_fixture(args.fixture_root, dataset_id)
        cases = fixture["cases"]

        baseline_latencies_ms: list[float] = []
        mojo_latencies_ms: list[float] = []
        correctness_failures: list[dict[str, Any]] = []

        baseline_started = time.perf_counter()
        for case in cases:
            payload = case["input"]
            expected = case["expected_output"]
            contract.input_validator(payload)
            contract.output_validator(expected)

            baseline_t0 = time.perf_counter()
            baseline_actual = python_score_rank(payload)
            baseline_latencies_ms.append((time.perf_counter() - baseline_t0) * 1000.0)

            baseline_diff = _compare_outputs(
                expected,
                baseline_actual,
                abs_error_max=contract.absolute_error_max,
                rank_order_exact=contract.rank_order_exact,
            )
            if baseline_diff:
                raise RuntimeError(
                    "Fixture generation/parity invariant violated: Python baseline diverged from expected output.\n"
                    f"dataset={dataset_id} request_id={payload['request_id']} failures={baseline_diff}"
                )
        baseline_total_s = max(time.perf_counter() - baseline_started, 1e-12)

        mojo_started = time.perf_counter()
        for case in cases:
            payload = case["input"]
            expected = case["expected_output"]
            t0 = time.perf_counter()
            actual = _run_mojo_once(mojo_bin, args.mojo_kernel, payload)
            mojo_latencies_ms.append((time.perf_counter() - t0) * 1000.0)
            contract.output_validator(actual)

            diffs = _compare_outputs(
                expected,
                actual,
                abs_error_max=contract.absolute_error_max,
                rank_order_exact=contract.rank_order_exact,
            )
            if diffs:
                correctness_failures.append({"request_id": payload["request_id"], "failures": diffs})
        mojo_total_s = max(time.perf_counter() - mojo_started, 1e-12)
        baseline_p95 = _percentile_ms(baseline_latencies_ms, 95)
        baseline_p99 = _percentile_ms(baseline_latencies_ms, 99)
        mojo_p95 = _percentile_ms(mojo_latencies_ms, 95)
        mojo_p99 = _percentile_ms(mojo_latencies_ms, 99)
        p95_speedup = baseline_p95 / max(mojo_p95, 1e-12)
        p99_speedup = baseline_p99 / max(mojo_p99, 1e-12)
        p99_regression_pct = 0.0
        if mojo_p99 > baseline_p99:
            p99_regression_pct = ((mojo_p99 - baseline_p99) / max(baseline_p99, 1e-12)) * 100.0

        dataset_result = {
            "dataset_id": dataset_id,
            "case_count": len(cases),
            "baseline_python": {
                "p50_ms": _percentile_ms(baseline_latencies_ms, 50),
                "p95_ms": baseline_p95,
                "p99_ms": baseline_p99,
                "throughput_ops_sec": len(cases) / baseline_total_s,
                "peak_rss_mb": _rss_mb(resource.RUSAGE_SELF),
            },
            "mojo": {
                "p50_ms": _percentile_ms(mojo_latencies_ms, 50),
                "p95_ms": mojo_p95,
                "p99_ms": mojo_p99,
                "throughput_ops_sec": len(cases) / mojo_total_s,
                "peak_rss_mb": _rss_mb(resource.RUSAGE_CHILDREN),
            },
            "speedup": {
                "p50": (_percentile_ms(baseline_latencies_ms, 50) / max(_percentile_ms(mojo_latencies_ms, 50), 1e-12)),
                "p95": p95_speedup,
                "p99": p99_speedup,
            },
            "regression_pct": {
                "p99": p99_regression_pct,
            },
            "correctness_failures": correctness_failures,
        }
        total_failures += len(correctness_failures)
        gate = contract.promotion_gate
        dataset_gate_failures: list[str] = []
        if p95_speedup < float(gate["p95_speedup_vs_python_min"]):
            dataset_gate_failures.append("p95_speedup_below_min")
        if p99_regression_pct > float(gate["p99_regression_max_pct"]):
            dataset_gate_failures.append("p99_regression_above_max_pct")
        if len(correctness_failures) > int(gate["correctness_failures_allowed"]):
            dataset_gate_failures.append("correctness_failures_above_allowed")
        if dataset_gate_failures:
            gate_failures.append(
                {
                    "dataset_id": dataset_id,
                    "failures": dataset_gate_failures,
                    "observed": {
                        "p95_speedup_vs_python": p95_speedup,
                        "p99_regression_pct": p99_regression_pct,
                        "correctness_failures": len(correctness_failures),
                    },
                    "required": gate,
                }
            )
        result_datasets.append(dataset_result)

    output_payload = {
        "harness_id": "mojo-kernel-bench-v1",
        "kernel_id": "score.rank.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "contract_path": str(args.contract),
        "fixture_root": str(args.fixture_root),
        "mojo_kernel": str(args.mojo_kernel),
        "datasets": result_datasets,
        "correctness_failures_total": total_failures,
        "promotion_gate": {
            "required": contract.promotion_gate,
            "enforced": not args.no_enforce_gates,
            "violations": gate_failures,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output_payload, indent=2, sort_keys=True).decode().decode() + "\n", encoding="utf-8")
    print(f"Wrote benchmark results: {args.output}")
    if total_failures > 0:
        raise RuntimeError(
            f"Mojo correctness check failed with {total_failures} failing cases. Inspect report: {args.output}"
        )
    if gate_failures and not args.no_enforce_gates:
        raise RuntimeError(
            "Mojo promotion gate failed. "
            f"{len(gate_failures)} dataset(s) violated contract thresholds. "
            f"Inspect report: {args.output}"
        )
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "generate-fixtures":
        return generate_fixtures(args)
    if args.command == "run":
        return run_harness(args)
    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
