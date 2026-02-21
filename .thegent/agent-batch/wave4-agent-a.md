# Wave 4 Agent A Report

## Completed slices

- WL-102: Completed SDK resume API + session list parity updates.
  - Added `ThegentClient.resume(session_id, prompt=None) -> RunResult` with strict payload validation.
  - Made `list_sessions()` accept both list payloads and wrapped `{"sessions": [...]}` payloads.
  - Expanded typed models in `thegent_sdk.types.SessionInfo` for run/session parity fields (`run_id`, `correlation_id`, `model`, `owner`, `started_at_utc` mapping, `prompt_preview`, `source`, `interactivity`, `attach_target`, `pid`).
  - Added `context_usage_ratio` to SDK `RunResult` type/parsing.

- WL-103: Surfaced context usage ratio from compactor wiring into `RunResult`.
  - Added `context_usage_ratio` field to runtime `RunResult` dataclass.
  - Wired LiteLLM execution path in `CodexProxyRunner` to copy `compaction.usage_ratio` into returned `RunResult` (success and error paths).

- WL-105: Added dynamic tool response completion path for session flow.
  - Added completion event helper: `tool_call_completed_event(...)` in dynamic registry.
  - Added `dynamic_tool_complete` handling in session send flow with required payload fields: `callId`, `output`, `success`.
  - Completion now resolves pending call ownership by session and returns a `tool_call_completed` event payload.

- WL-101: Applied skill selection path to resume/continue flows.
  - Added `--skill` support to `thegent run resume` and top-level `thegent resume` commands.
  - Resume implementation now injects selected skill instructions into follow-up resume prompt before queueing `reprompt`.
  - Continue path remains skill-aware through existing `bg_cmd(..., skills=...)` prompt injection, now covered by the same WL-101 injection path expectations.

- WL-078: Added regression baseline refresh command + docs.
  - Added Task target: `task bench:baseline:refresh` to regenerate `benchmarks/baseline.json` via WL-078 benchmark suite.
  - Updated QA guide with baseline refresh command guidance.

## Validation

- `uv run pytest -q packages/thegent-sdk/tests/test_client.py tests/mcp/test_dynamic_tools.py tests/mcp/test_tools_sessions_dynamic_registry.py tests/test_wl103_context_compactor_wiring.py tests/test_wl101_skill_selection_cli.py tests/performance/test_python_benchmark_suite.py tests/performance/test_python_benchmark_regression.py`
  - Result: PASS (`38 passed`)
- `uv run python -m py_compile packages/thegent-sdk/src/thegent_sdk/types.py packages/thegent-sdk/src/thegent_sdk/client.py src/thegent/mcp/dynamic_tools.py src/thegent/mcp/server/tools_sessions.py src/thegent/cli/commands/impl.py src/thegent/cli/commands/cli.py src/thegent/cli/apps/run.py src/thegent/cli/apps/main.py src/thegent/agents/base.py src/thegent/agents/codex_proxy.py`
  - Result: PASS
- `uv run python scripts/benchmark_python_suite.py --iterations 250 --output /tmp/wl078-ci-smoke.json`
  - Result: PASS
- `uv run python scripts/check_python_benchmark_regression.py --baseline benchmarks/baseline.json --current /tmp/wl078-ci-smoke.json --max-regression-pct 100`
  - Result: PASS (`{"ok": true, ...}`)

## Blockers

- None.

## Exact files touched

- `packages/thegent-sdk/src/thegent_sdk/types.py`
- `packages/thegent-sdk/src/thegent_sdk/client.py`
- `packages/thegent-sdk/README.md`
- `packages/thegent-sdk/tests/test_client.py`
- `src/thegent/agents/base.py`
- `src/thegent/agents/codex_proxy.py`
- `src/thegent/mcp/dynamic_tools.py`
- `src/thegent/mcp/server/tools_sessions.py`
- `src/thegent/cli/commands/impl.py`
- `src/thegent/cli/commands/cli.py`
- `src/thegent/cli/apps/run.py`
- `src/thegent/cli/apps/main.py`
- `tests/test_wl103_context_compactor_wiring.py`
- `tests/mcp/test_dynamic_tools.py`
- `tests/mcp/test_tools_sessions_dynamic_registry.py`
- `tests/test_wl101_skill_selection_cli.py`
- `Taskfile.yml`
- `docs/guides/QUALITY_ASSURANCE.md`
