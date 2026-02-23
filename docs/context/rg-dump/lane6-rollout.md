# Lane 6 – Migration / Rollout Program

## Facts (with path evidence)
- `cliproxy + agentapi++` is the chosen primary metaprovider boundary that must stay stable during this migration, so the rollout only shifts the runtime behind those adapters rather than replacing them wholesale (docs/context/rg-dump/BIFROST_vs_LITELLM_for_CLIPROXY_AGENTAPI_2026-02-23.md:8).
- The unified `provider-bridge` contract is the surface the new boundary will publish, keeping chat completions, embeddings, tool execution, and catalog lookups behind identical adapter primitives (docs/context/rg-dump/UNIFIED_PROVIDER_BOUNDARY_PLAN_2026-02-23.md:27).
- The current “litellm-donut” compatibility wrapper is the transitional `LiteLLMCompatExecutor` running inside the metaprovider stack; it lets LiteLLM stay as a fallback while the bridge stabilizes (docs/context/rg-dump/BIFROST_vs_LITELLM_for_CLIPROXY_AGENTAPI_2026-02-23.md:30).
- LiteLLM Router’s `simple-shuffle` default delivers 8 ms P95 at 1 k RPS, so this latency claim becomes the baseline for parity instrumentation in the new boundary (docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:77).
- LiteLLM reliability knobs (retries, cooldowns, fallbacks, pre-call checks) provide the gating semantics we will surface in the rollout’s rollback envelopes (docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:81).
- Caching, cost tracking, and observability hooks built into LiteLLM (redis vs in-memory caching, budget config, and alert callbacks) are the signals we will monitor for exit criteria (docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:107).

## Decision proposals
- Keep LiteLLM as the compatibility shim while the bridge takes operational ownership, meaning the rollout only ramps traffic once the `provider-bridge` adapters prove their parity with the existing stack (docs/context/rg-dump/BIFROST_vs_LITELLM_for_CLIPROXY_AGENTAPI_2026-02-23.md:39; docs/context/rg-dump/UNIFIED_PROVIDER_BOUNDARY_PLAN_2026-02-23.md:42).
- Stage the migration through the mandated shadow → partial → cutover phases, each gated by measurable telemetry aligned with LiteLLM’s reliability and governance controls (docs/context/rg-dump/CHILD_AGENT_WAVE_PACKET_2026-02-23.md:58).
- Document every stage in `docs/context/rg-dump/lane6-rollout.md` itself so future lanes can cite the rollout evidence and satisfy the aggregation contract described at the beginning of that packet (docs/context/rg-dump/CHILD_AGENT_WAVE_PACKET_2026-02-23.md:70).

## Risks & mitigations
- Migration complexity risk: Bifrost notes that cutting over routing/governance hooks adds risk, so we will keep both CLI and MCP boundaries separate and only swap the executor under the bridge (docs/context/rg-dump/BIFROST_vs_LITELLM_for_CLIPROXY_AGENTAPI_2026-02-23.md:34).
- Observability gaps: without custom callbacks and alerts we cannot be confident in parity; instrumented logging, metrics, and budget alerts from LiteLLM must be mirrored in the bridge before ramping (docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:141).
- Budget drift: cost tracking fields included in LiteLLM (per-day provider budgets) will back the financial rollback gate to avoid runaway spend when new routes are exercised (docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:121).

## Rollout stages
### Preflight (bridge hardening)
- Freeze the `provider-bridge` schema DTOs, publish version `v0alpha1`, and implement the adapter shims for `agentapi++` and `cliproxy` so the new runtime can respond alongside the old LiteLLM donut wrapper (docs/context/rg-dump/UNIFIED_PROVIDER_BOUNDARY_PLAN_2026-02-23.md:80).
- Add capability matrix entries so each adapter documents which providers and executor tags it supports (docs/context/rg-dump/UNIFIED_PROVIDER_BOUNDARY_PLAN_2026-02-23.md:82) and add governance metadata for routing hints, retries, caches, and budgets before we begin parity checks (docs/context/rg-dump/UNIFIED_PROVIDER_BOUNDARY_PLAN_2026-02-23.md:84).
- Build instrumentation to compare responses between the bridge and the donut wrapper, tracking latency versus the simple-shuffle 8 ms P95 baseline (docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:77).

### Stage 1 – Shadow mode
- Route mirrored traffic through the new bridge while the Litellm donut wrapper remains the only active executor; capture response differences, latency, error types, retries, and cooldown triggers at the gateway layer.
- Exit criteria: 1,000 shadow requests with <0.5 % mismatch in output hashes, latency within 120 % of the 8 ms P95 baseline, and no cooldowns opened above the configured `allowed_fails` thresholds (LiteLLM reliability features from docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:89).
- Rollback gate: if error rate, retry storms, or cooldown opens exceed the configured LiteLLM thresholds (per-minute allowed fails) for two consecutive monitoring windows, disable the bridge and iterate on the adapter contracts.

### Stage 2 – Partial traffic (25–35 %)
- Start forwarding a fixed percentage of production traffic to the bridge while continuing to shadow all requests for parity; use cost-tracking metadata to verify budget alignment for each provider entry before the new path authorizes execution (LiteLLM cost tracking from docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:121).
- Verify cache population parity (in-memory/Redis groups) so downstream expectations on caching keys continue to hold (docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:107).
- Exit criteria: 48 hours with 99.7 % success on the new path, no alerts raised by LiteLLM’s observability callbacks, and costs within 5 % of the previous month’s per-provider budget allocations (docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:141).
- Rollback gate: sustained budget spikes, alert firing from Slack or webhook instrumentation, or cache hit-rate regressions below 90 % relative to the donut wrapper trigger an immediate rollback to 0 % and a pause for analysis.

### Stage 3 – Cutover
- After partial stage exit, promote 100 % traffic to the bridge and retire the litellm donut wrapper; keep the old wrapper runnable but dormant for quick rollback until cutover stability is proven.
- Exit criteria: 72 hours of bridge-only traffic with error rate ≤0.2 %, latency consistently within 1.1× the 8 ms benchmark, no retriggers of cooldowns, and budget spend tracking within expected tolerances (docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:77, docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:121).
- Rollback gate: any single incident that breaches SLO targets (errors, latency, budget) during this window will immediately fall back to the wrapper while root cause is analyzed.

## Rollback envelope
- Configurable thresholds mirror LiteLLM cooldown parameters (`allowed_fails`, per-deployment failure tracking) so every rollback decision references the same policy that governs LiteLLM deployments (docs/context/rg-dump/LITELLM_HARNESS_MASTER_PLAN.md:89).
- Every rollback decision is accompanied by parity logs, request/response diffs, and the latest cost/alert metadata so the team can triage without guessing what changed.

## Immediate next 3 implementation tasks
1. Freeze the `provider-bridge` schema (`DTOs + request/response + telemetry fields`) and version it so every adapter can rely on the same contract (docs/context/rg-dump/UNIFIED_PROVIDER_BOUNDARY_PLAN_2026-02-23.md:80).
2. Write the `AgentApiMetaProviderAdapter` and `CliproxyMetaProviderAdapter` against that schema, ensuring both can report parity telemetry into the same observability pipeline (docs/context/rg-dump/UNIFIED_PROVIDER_BOUNDARY_PLAN_2026-02-23.md:81).
3. Surface the capability matrix entries (providers + nested subproviders + executor tags) that describe what the new boundary supports before we start routing real traffic (docs/context/rg-dump/UNIFIED_PROVIDER_BOUNDARY_PLAN_2026-02-23.md:82).
