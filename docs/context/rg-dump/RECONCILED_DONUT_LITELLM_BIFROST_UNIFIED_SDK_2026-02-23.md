# Reconciled Architecture: Donut + LiteLLM + Bifrost + Unified API/SDK

Date: 2026-02-23
Purpose: preserve prior LiteLLM/donut routing investment, integrate Bifrost cleanly, and keep one unified API+SDK with sub-level inherited consumption.

## 1) What happened to the prior donut architecture?
Nothing is discarded. It becomes a first-class execution lane behind the unified boundary.

```text
Before:
Harness/Agent paths -> LiteLLM donut wrappers -> provider APIs

Now (reconciled):
Harness/Agent paths -> Unified Bridge API/SDK -> Execution Lanes:
  Lane A: LiteLLM Donut Runtime (low-change)
  Lane B: Bifrost Runtime (go-forward)
```

So your prior donut is retained as `lane_litellm_donut`, not removed.

## 2) Unified Boundary (single surface)

```text
Clients (thegent, harnesses, tools)
  -> Unified API + Unified SDK
    -> Metaprovider Router
      -> AgentAPI control-plane path
      -> CLIProxyAPI execution-plane path
        -> lane_litellm_donut
        -> lane_bifrost
        -> lane_native (future)
```

## 3) Full stack fit with your current direction

```text
[mlx,vllm,llamacpp,ollama,openrouter,openai,claude,cursor,acct APIs,...]
    ^
    | provider calls
[CLIProxyAPI execution fabric]
    |- lane_litellm_donut (existing wrappers/routing)
    |- lane_bifrost (policy/routing/go-forward runtime)
    |- shared translator + registry + telemetry
    ^
    | normalized execution interface
[AgentAPI control plane]
    |- sessions, auth, org/project policy
    |- prompt/context assembly
    |- MCP/Skill/Env policy envelope
    ^
    | run orchestration
[Harnesses: Codex, Claude, Droid, Antigma, Codex-alt]
    ^
    | user/automation
[MCP + Skills + Env runtime context]
```

## 4) “LiteLLM less change” mode (explicit)
This mode minimizes refactors while still converging to one contract.

Rules:
1. Keep existing LiteLLM donut routing internals intact.
2. Wrap donut path with `ExecutionLaneAdapter` only.
3. Route by policy/config, not client-side branching.
4. Keep all clients on unified SDK now.
5. Migrate traffic gradually from donut lane to bifrost lane by profile/policy.

## 5) Unified SDK + sub-level inherited consumption

Model:
- `BaseExecutionRequest` (global fields)
- `MetaproviderRequest` extends base
- `LaneRequest` extends metaprovider request
- `ProviderRequest` extends lane request (optional lane-specific fields)

```text
Inheritance chain:
BaseExecutionRequest
  -> MetaproviderRequest
     -> LaneRequest (litellm_donut | bifrost | native)
        -> ProviderRequest (openai/anthropic/ollama/...)
```

This gives one SDK for all use cases while allowing lane/provider specializations.

## 6) Canonical request/response shape

```json
{
  "bridge_schema_version": "v1.0.0",
  "request_id": "req_...",
  "run_id": "run_...",
  "harness_profile": "codex",
  "metaprovider_id": "cliproxy",
  "lane_id": "litellm_donut",
  "provider_intent": {
    "class_order": ["cloud_direct", "cloud_aggregator", "local_inference"],
    "allow_models": ["openai/gpt-5", "anthropic/claude-sonnet"]
  },
  "governance": {
    "budget_usd_max": 3.0,
    "max_fallbacks": 2
  },
  "inputs": {
    "messages": [{"role": "user", "content": "..."}],
    "tools": []
  },
  "stream": true
}
```

Lane inheritance behavior:
- If `lane_id=litellm_donut`, apply donut routing config and wrappers.
- If `lane_id=bifrost`, apply bifrost route selection/plugins.
- Shared response envelope remains identical.

## 7) Where internals/external architectures fit

### Internals
- AgentAPI: control-plane and policy context.
- CLIProxyAPI: lane arbitration + translation + retry/fallback + telemetry.
- Lanes: implementation detail behind one interface.

### Externals
- Provider APIs stay unchanged.
- Optional gateway (Kong/Envoy/APISIX) can sit above unified API for global ingress policy.

```text
Client -> (optional gateway) -> Unified API -> lanes -> providers
```

### Application externals (`thegent`, harnesses)
- Harnesses only call unified SDK.
- No harness direct dependency on LiteLLM or Bifrost internals.
- Harness profile influences lane default via policy.

## 8) Policy-based lane selection (recommended)

```text
if harness_profile in [legacy_paths] -> default lane: litellm_donut
if harness_profile in [new_paths]    -> default lane: bifrost
if org_policy.force_lane set         -> override default
if lane health degraded              -> failover to other allowed lane
```

This preserves behavior while enabling controlled evolution.

## 9) What to write down from the two prior asks
This document is the write-down of both:
1. Expanded external libs/projects research integrated into target architecture.
2. Full internal/external/applicational architecture with ASCII and `thegent` fit.

## 10) Build plan (low-change + long-term)

Phase 1: contract and SDK unification
1. Freeze unified bridge schema v1.
2. Generate unified SDKs (Go/Python/TS).
3. Move harness callers to SDK only.

Phase 2: lane wrapping
1. Implement `lane_litellm_donut` adapter around current donut internals.
2. Implement `lane_bifrost` adapter around bifrost runtime path.
3. Normalize telemetry fields across lanes.

Phase 3: policy and inheritance
1. Add lane selection policy engine.
2. Add inherited request model classes in SDK.
3. Add fallback across lanes with same response envelope.

Phase 4: optimization
1. Shift selected workloads to bifrost lane where it wins.
2. Keep donut lane for cases needing compatibility/behavior parity.
3. Continue under one API/SDK indefinitely.

## 11) Non-negotiables
1. One API contract.
2. One SDK family.
3. Lane internals are hidden from clients.
4. `thegent` harnesses do not branch on provider runtime internals.
