# WL-115 Agent-C Plan: Cross-Harness Benchmarking (`thegent bench`)

## Status
Blocked for full delivery (new command surface + fixture corpus + persistence contract). No safe one-file slice was available without introducing command/API drift.

## Implementation-ready next slices
1. Create benchmark domain model and storage contract.
- Files: `src/thegent/bench/models.py`, `src/thegent/bench/store.py`
- Output schema: JSONL fields `suite`, `harness`, `test_id`, `latency_sec`, `tokens_input`, `tokens_output`, `tool_calls`, `success`, `error_recovery_attempts`, `run_id`, `ts_utc`
- Validation: `pytest -q tests/test_wl115_bench_models.py tests/test_wl115_bench_store.py`

2. Add CLI wrapper command group.
- Files: `src/thegent/cli/apps/bench.py`, `src/thegent/cli/apps/main.py`
- Commands:
  - `thegent bench run --suite <name> --harness <name> [--test <id>]`
  - `thegent bench compare --baseline-harness <name> --candidate-harness <name> --suite <name>`
- Validation: `thegent bench --help`; `pytest -q tests/test_wl115_bench_cli.py`

3. Add first built-in suite fixtures (`code-gen`, `file-ops`).
- Files: `benchmarks/suites/code-gen.json`, `benchmarks/suites/file-ops.json`
- Validation: `pytest -q tests/test_wl115_bench_suites.py`

4. Wire CI-friendly JSON output.
- Files: `src/thegent/bench/report.py`
- Validation: `thegent bench compare --baseline-harness codex --candidate-harness claude --suite code-gen --output-format json`

## Exit criteria
- `~/.thegent/bench/results.jsonl` written for each run.
- Compare command returns deterministic JSON and exit code semantics for CI.
- >= 25 WL-115 tests green.

## Wave-2 Delta (2026-02-21)
- Completed slice 1:
  - Added `BenchRecord` schema model and JSONL store helpers.
  - Added focused tests for schema roundtrip, required-field validation, append/load behavior.
- Remaining blockers:
  - CLI surface (`thegent bench ...`) is not wired yet.
  - Suite fixture corpus and compare/report command path still pending.

## Wave-10 Delta (2026-02-21)
- Completed:
  - `bench compare` now normalizes persisted harness labels and selector flags case-insensitively, avoiding false "missing harness" failures when historical rows used mixed-case names.
  - Added regression coverage for mixed-case persisted harness values and mixed-case `--baseline-harness/--candidate-harness` selectors.
- Evidence:
  - `src/thegent/cli/apps/bench.py`
  - `tests/test_wl115_bench_cli.py`
