# 70-Task Sprint Plan (Audit-Backed)

## Scope and baseline

- Scope: `cliproxyapi++` hardening for protocol normalization, auth/session plumbing, provider failover/quotas, and orchestration compatibility with `agentapi`-style control-plane endpoints (`/message`, `/messages`, `/status`, `/events`), plus full quality gates and cross-cutting reliability checks.
- Baseline evidence in-repo:
  - `task quality` and `task quality:quick` are available in `Taskfile.yml`.
  - `pkg/llmproxy/api/server.go` and `pkg/llmproxy/api/responses_websocket.go` show transport coexistence patterns for `/v1/responses`.
  - Integration research artifacts:
    - `docs/planning/agentapi-cliproxy-integration-research-2026-02-22.md`
    - `docs/planning/coder-org-plus-relative-300-inventory-2026-02-22.md`
  - The sprint previously tracked as 35 tasks (now expanded).

## End-to-end audit (what must be closed before rollout)

1. Protocol compatibility is the highest-risk area because cliproxy currently spans OpenAI/Claude/Gemini conversions while `agentapi` workflows require stable control lifecycle semantics.
2. Route and session collisions are still the leading production-risk class:
   - Duplicate response-path handlers (`/v1/responses`) and websocket/HTTP coexistence must be deterministic under hot-reload and test harness restart paths.
3. Session identity and ID propagation are currently split-plane:
   - model plane uses execution/session identifiers internally;
   - control-plane APIs (agent messaging) use their own lifecycle IDs in external contracts.
4. Provider failover and quota behavior need contract tests with explicit fallback order and metric assertions.
5. Coverage gap remains where most behavior is verified by unit tests only; integration/e2e coverage for CLI-proxy behavior under live transport and cheapest-model paths is incomplete.
6. Quality workflow exists but command coverage is uneven:
   - `quality:fmt` mutation by design;
   - `quality:fmt:check`, `quality`, and `lint` currently have no strict staged/e2e gating contract across all workflows.

## Latest Evidence Update (2026-02-22)

- Completed:
  - [B1] duplicated `/v1/responses` duplicate-handler regression path stabilized in `pkg/llmproxy/api`.
  - [B2] websocket route dedupe logic in `AttachWebsocketRoute`.
  - [B3] duplicate attach regression tests added.
  - [B4] `/v1/responses` HTTP + WebSocket shape assertions added.
  - [D2] `quality:quick` and `quality:fmt` command path exercised in local scope.
  - [D4] pre-merge `quality-ci` PR gate added in `.github/workflows/pr-test-build.yml` with:
    - non-mutating format and lint checks (`quality:fmt:check`, `quality:ci`, `test:smoke`)
    - go vet and optional staticcheck (enabled via CI env)
  - [D5] quality lifecycle section updated in `docs/planning/README.md`.
  - [D6] quality parity and non-mutating job contract now represented as `task quality:ci` and `fmt` checks.
  - [D8] diff-based linting (`lint:changed`) now supports PR base->head ranges for CI and local usage.
  - [D10] smoke/test gate (`task test:smoke`) added as a runnable CLI and CI job.
  - [D4] pre-merge quality-staged check added via `quality-staged-check` job (`quality:fmt-staged:check`).
  - [D9] `quality:release-lint` task added for release-facing config + docs example parse verification.
  - [D10] `verify:all` now runs smoke and release-lint alongside existing vet/staticcheck/test checks.
  - [D2b] `quality:quick:fix` added for local auto-format + non-mutating quick checks.
  - [G9] request-logging now redacts sensitive headers (`Authorization`, `Cookie`, `Proxy-Authorization`) with direct unit assertions in middleware tests.
  - [F2] control-plane endpoint shell added (`POST /message`, `GET /messages`, `GET /status`, `GET /events`) with session lifecycle unit tests.
  - [F4] unsupported capability contract hardcoded in `POST /message` with explicit non-2xx status.
  - [F5] command-label normalization coverage (`continue`, `resume`, `ask`, `exec`, `max`) added as unit tests for `/message`.
  - [B4+idemp] per-request `Idempotency-Key` replay path added to control-plane `/message`, verified by duplicate suppression tests.
  - [B6] command-label parity for orchestration metadata path validated in `/message` unit tests.
  - [B7] idempotency-key duplicate behavior validated with separate replay/no-replay paths.
  - [C2] added deterministic reasoning-level rebound behavior tests in `pkg/llmproxy/thinking/validate_test.go` for unsupported levels, conversion, and rejection.
  - [C3] added budget clamp tests for zero/negative values, provider min floors, and max ceilings in `pkg/llmproxy/thinking/validate_test.go`.
  - [C4] added provider-boundary validation assertions for strict same-provider in-range enforcement and suffix-based fallback clamping in `pkg/llmproxy/thinking/validate_test.go`.
  - [P3] next wave mapped: `CPB-0176..CPB-0245` generated and validated into `docs/planning/issue-wave-cpb-0176-0245-2026-02-22.md` plus seven 10-item lane reports in `docs/planning/reports/`.
  - Blockers:
  - Repository-wide `task quality` runs still fail on pre-existing parse errors in multiple packages (`quality:fmt` parses all `*.go` files first).
  - Cheapest-model/live provider matrix and true end-to-end orchestration tests are still pending.

## Integration contract decision

- Do not perform a full fork of both repos.
- Keep `cliproxyapi++` as normalized model transport and provider control.
- Keep control-plane session services (where needed) on `agentapi`-style endpoint surfaces.
- Add a small orchestrator shim to unify:
  - session/correlation header contract,
  - auth policy boundaries,
  - retry/failover policy,
  - and event emission normalization.

## Stable endpoint contract target

- Canonical correlation headers:
  - `X-Trace-Id`, `X-Session-Id`, `X-Request-Id`, `X-Tenant-Id`, `Idempotency-Key`
- Model plane:
  - `POST /v1/models`, `POST /v1/responses`, `POST /v1/chat/completions`, `POST /v1/completions`,
    websocket fallback on `/v1/responses` where supported.
- Control plane:
  - `POST /message`, `GET /messages`, `GET /status`, `GET /events`
  - and optional SSE stream normalization to orchestrator event envelope.
- Transport policy:
  - fail-fast on mixed content-type mismatch,
  - deterministic header propagation,
  - explicit unsupported endpoint errors with codes and retry hints.
- Session policy:
  - no destructive deletion on session metadata conflicts,
  - append-only ledger with conflict branches for resumed histories,
  - explicit provenance tagging for session forked/resumed states.

## 7-Lane Sprint Mapping (7 × 10 = 70 tasks)

- Lane A: Core compile and contract stabilization.
- Lane B: Route semantics and session-state idempotency.
- Lane C: Model/protocol translation and provider capability parity.
- Lane D: Quality lifecycle and developer workflow hardening.
- Lane E: Provider routing/failover/quotas and transport resilience.
- Lane F: agentapi-style control-plane integration (message/events/status).
- Lane G: Test coverage, chaos/perf/security/holistics, and governance.

## Lane A — Core Build & Contract Baseline (10)

1. [A1] Resolve `pkg/llmproxy/cmd` compile blockers from missing symbols (`RunKiloLoginWithRunner`, `kiloInstallHint`).
   - Acceptance: `go test ./pkg/llmproxy/cmd` passes.
2. [A2] Restore missing `pkg/llmproxy/store` helper symbols (`openOrInitRepositoryAfterEmptyClone`, `isNonFastForwardUpdateError`, `bootstrapPullDivergedError`, `ErrConcurrentGitWrite`).
   - Acceptance: `go test ./pkg/llmproxy/store` passes.
3. [A3] Restore websocket executor/backpressure compatibility helper symbols in both `pkg/llmproxy/executor` and `pkg/llmproxy/runtime/executor`.
   - Acceptance: websocket tests compile and pass in both packages.
4. [A4] Unblock `sdk/api/handlers` interface mismatches (`ProviderExecutor`, `CloseExecutionSession`) against runtime interfaces.
   - Acceptance: `go test ./sdk/api/handlers ./sdk/api/handlers/openai ./sdk/cliproxy` passes.
5. [A5] Normalize `sdk/cliproxy` auth manager test usage (`Executor` assertions to current contract).
   - Acceptance: no undefined field errors in `sdk/cliproxy`.
6. [A6] Add `make -n`/`task -l` baseline check to ensure required external build tooling is present before test jobs start.
   - Acceptance: CI jobs fail early with clear message if tools are missing.
7. [A7] Add `test:unit` and `test:integration` Taskfile targets to avoid overloading `task quality` in PR feedback.
   - Acceptance: both targets are runnable and documented.
8. [A8] Add `task test:integration -- --tags=integration` execution path with no shared env mutation.
   - Acceptance: isolated integration suite can run locally without flaky side effects.
9. [A9] Add deterministic cache cleanup helper for package cache lock contention in test jobs.
   - Acceptance: integration jobs no longer intermittently fail on lock contention.
10. [A10] Add `go test ./...` baseline report artifact (`target/test-baseline.txt`) in CI for auditability.
   - Acceptance: every run stores package-level pass/fail and duration.

## Lane B — Route and Session-State Idempotency (10)

1. [B1] Fix duplicated route registration in `pkg/llmproxy/api` (`/v1/responses`) for panic-free server bootstrap.
   - Acceptance: `go test ./pkg/llmproxy/api` no longer panics.
2. [B2] Add explicit guard around websocket route registration in `AttachWebsocketRoute`.
   - Acceptance: repeated attach attempts are deduplicated.
3. [B3] Add regression test for duplicate attach during server rebuild/reload.
   - Acceptance: test fails on first duplicate registration.
4. [B4] Verify HTTP/WS coexistence for `/v1/responses` in both default and legacy route modes.
   - Acceptance: functional assertion covers both modes in one suite.
5. [B5] Add CI guard to run route lifecycle tests on every PR.
   - Acceptance: route regressions fail merge.
6. [B6] Add explicit mapping tests for command-label parity between orchestration entrypoints (`max`, `ask`, `continue`, resume-like calls) when those surfaces are exercised via cliproxy request body metadata.
   - Acceptance: command label translation is stable and surfaced in tests.
7. [B7] Add idempotency tests for request retry with same `Idempotency-Key`.
   - Acceptance: duplicate requests do not double charge and return coherent `session_id`.
8. [B8] Add session-state read-path fallback tests for primary/mirror session files.
   - Acceptance: corrupted primary still returns mirror snapshot with warning telemetry.
9. [B9] Add conflict-branch tests for simultaneous session updates (existing payload diff; no destructive replace).
   - Acceptance: both current and conflicting versions preserved.
10. [B10] Add route-namespace contract tests for `/agent/*` vs `/v1/*` isolation in orchestrator wiring.
   - Acceptance: no ambiguous handler dispatch.

## Lane C — Model Protocol & Translation Semantics (10)

1. [C1] Resolve reasoning mapping drift (`minimal`, `xhigh`, `auto`) and close open conversion gaps.
   - Acceptance: `thinking_conversion_test` parity re-established.
2. [C2] Add invalid/rebound tests for reasoning levels per provider with deterministic clamp/fallback.
   - Acceptance: unsupported values are mapped or rejected by contract.
3. [C3] Fix budget clamping for zero/negative token budgets and provider-specific minimums.
   - Acceptance: conversion output always within schema limits.
4. [C4] Add provider-level schema assertions for max budget boundaries.
   - Acceptance: out-of-range handling is consistent and documented.
5. [C5] Add matrix tests for suffix/prefix/body variants across OpenAI/Claude/Gemini paths.
   - Acceptance: translator parity table passes in CI.
6. [C6] Expand `/v1/responses` body shape tests to include `tool_choice`, `function_call`, `max_output_tokens`, and tool-stream edge cases.
   - Acceptance: no silent dropping of structured fields.
7. [C7] Add non-JSON content-type negative-path tests (`text/plain`, empty body, mixed multipart).
   - Acceptance: returns explicit `4xx` and contract-compliant error envelope.
8. [C8] Add round-trip translator conformance tests across chat/completions/responses for at least 3 providers.
   - Acceptance: openai-style input can always be translated into provider-specific outputs.
9. [C9] Add model alias compatibility snapshot for alias->provider resolution (`openai:gpt-...`, `claude:...`, `gemini:...`, `minimax-m2.5`).
   - Acceptance: alias registry has tests + changelog entry.
10. [C10] Add provider capability registry test that flags unsupported features per model (tools, vision, streaming shape, tool-calls).
   - Acceptance: unsupported capabilities return clear `provider_not_supported` style errors.

## Lane D — Quality Automation and DX Gates (10)

1. [D1] Keep `quality:fmt` and `quality:fmt:check` as mandatory pre-merge format gates.
2. [D2] Add `quality:quick` package selector with `QUALITY_PACKAGES` env and fail-fast defaults.
   - Acceptance: one-command local smoke loop is fast.
3. [D3] Update contributor docs to include `task hooks:install` lifecycle and why staging checks differ.
   - Acceptance: README has deterministic first-run instructions.
4. [D4] Add CI gate for `quality:fmt-staged` and `lint` in pre-merge PR jobs.
   - Acceptance: staged quality failures are surfaced before merge.
5. [D5] Add `docs/planning/README` section for quality lifecycle and command matrix.
   - Acceptance: clear command path for local, PR, and release modes.
6. [D6] Add `quality:fmt:check` and `quality:fmt` parity job to ensure no mutation in readonly mode.
   - Acceptance: format-only jobs cannot introduce drift.
7. [D7] Add automated `go vet ./...` + `staticcheck` optional gate behind Taskfile flag.
   - Acceptance: CI fails on new vet/staticcheck defects.
8. [D8] Add `task lint:changed` target (diff-based lint) for pre-commit speed.
   - Acceptance: smaller scope checks are under 60s in average machine.
9. [D9] Add release-lint task to verify config examples and docs examples compile/parse.
   - Acceptance: config/docs drift cannot reach main.
10. [D10] Add `task verify:all` orchestration that runs fast fmt/check/lint/test/smoke in one command.
   - Acceptance: single-command local audit entrypoint.

## Lane E — Provider Routing, Auth, Quotas, Failover, and Multiplexing (10)

1. [E1] Build standardized cheapest-model smoke matrix for every supported provider.
   - Acceptance: each provider has deterministic cheapest test alias.
2. [E2] Add startup and endpoint smoke (`/v1/models`, `/v1/metrics/providers`, `/v1/responses` WS).
   - Acceptance: transport and provider list verified at runtime.
3. [E3] Add failover contract tests for provider outage and unsupported resume/continuation combinations.
   - Acceptance: explicit fallback order and error envelopes.
4. [E4] Add quota-aware routing and hard/soft switch assertions under budget exhaustion.
   - Acceptance: routing policy changes are observable and reversible.
5. [E5] Add unsupported-provider alias policy and warning metrics.
   - Acceptance: fallback strategy is deterministic and logged.
6. [E6] Add authentication/session multiplexing tests for concurrent provider pools in one process.
   - Acceptance: token/state maps remain isolated across providers.
7. [E7] Add per-provider `streaming_adapter_health` metric coverage and test assertions.
   - Acceptance: provider health score is asserted in smoke outputs.
8. [E8] Add protocol compatibility contract tests for Claude/Gemini special-case fields (`system_fingerprint`, usage metadata, function call deltas).
   - Acceptance: normalized outputs match expected canonical envelope.
9. [E9] Add model routing dry-run endpoint for simulation mode before live failover.
   - Acceptance: dry-run returns chosen provider + reason without issuing request.
10. [E10] Add fallback telemetry for provider downgrade and route rejection in integration events stream.
   - Acceptance: events include provider decision rationale.

## Lane F — agentapi Parity and Orchestrator Integration (10)

1. [F1] Add minimal orchestrator translation tests for `POST /message` -> model-capable task path.
   - Acceptance: one request can launch model or agent task by configuration.
2. [F2] Add e2e tests for `POST /message`, `GET /messages`, `GET /status` and `GET /events` under cliproxy+agent lifecycle.
   - Acceptance: event stream and message history are coherent with `trace_id`.
3. [F3] Add end-to-end compatibility test where `/message` returns a model result through cliproxy transport.
   - Acceptance: same payload semantics as direct `/v1/responses`.
4. [F4] Add capability registry for control-plane parity (`resume/continue`, `abort`, `pause`, `status`) and unsupported capability response contract.
   - Acceptance: unsupported calls are explicit and non-2xx.
5. [F5] Add command-label translator table for `ask`, `exec`, `max`, `continue`, `resume`, and `status` aliases.
   - Acceptance: one canonical label map drives both mock and real harness paths.
6. [F6] Add event-to-session correlation adapter: map agent events to `session_id` and model `trace_id`.
   - Acceptance: events include both IDs for cross-plane debugging.
7. [F7] Add control-plane auth policy isolation (agent-level token scope != model provider credential scope).
   - Acceptance: cross-scope token misuse is denied with 403/401 as appropriate.
8. [F8] Add orchestration API that accepts both legacy `/v1/responses` style and `/message` workflows in one request schema.
   - Acceptance: no duplicate parsing logic across controllers.
9. [F9] Add contract tests for lifecycle status transitions (`running`, `waiting`, `done`, `failed`, `cancelled`).
   - Acceptance: transitions are deterministic and serialized.
10. [F10] Add replayability test for SSE event replay windows (`events` with last-event-id analog semantics).
   - Acceptance: interrupted sessions can resume without semantic loss.

## Lane G — Coverage, Chaos, Perf, Security, and Governance (10)

1. [G1] Expand planning index links to reflect all sprint artifacts and add a single evidence section.
   - Acceptance: one-click jump from docs index to research, plan, matrices, and checks.
2. [G2] Consolidate research artifacts with dated evidence tables and method notes.
   - Acceptance: research evidence can be re-verified from one page.
3. [G3] Add weekly pinned audit note for this sprint with explicit open-item list.
   - Acceptance: progress and blockers are always visible.
4. [G4] Add changelog entry for each completed 10-task lane.
   - Acceptance: historical traceability of stability gains.
5. [G5] Close/refresh the `203+97` research thread with a 30-day revisit date and diff captures.
6. [G6] Add integration/e2e cheapest-model matrix as required gate for all provider-plane changes.
   - Acceptance: cheapest-model command path executed in CI/cron.
7. [G7] Add chaos suite: upstream 502/timeout, websocket drop, auth outage, and local process kill/restart.
   - Acceptance: suite returns clear fail points and recovery metrics.
8. [G8] Add perf suite for p95/p99 under concurrent load and streaming fanout.
   - Acceptance: thresholds defined and enforced as warning/alert gates.
9. [G9] Add security suite for token leakage, request smuggling, and websocket-origin downgrade checks.
   - Acceptance: redaction and origin checks have test assertions.
10. [G10] Add holistic coverage audit check (`coverage-gaps.md`) with explicit gaps by class:
    unit, integration, e2e, chaos, perf, security, and docs.
    - Acceptance: report requires a close-out owner before merging.

## Execution sequence and gates

- Wave 1: A1-A5 + B1-B5 (compile and route baseline)
- Wave 2: C1-C10 + E1-E5 (protocol and provider contracts)
- Wave 3: D1-D10 + G1-G5 (quality and governance)
- Wave 4: F1-F10 + E6-E10 + G6-G10 (agent control integration and holistic coverage)
- Stop-go criterion before each lane: all DoD tests passing and evidence log updated.
