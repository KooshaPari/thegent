# Wave-6 Aggregated Report (Metaprovider Boundary)

Date: 2026-02-23
Status: complete

## Outcome
A 6-lane child-agent wave completed and converged on a consistent direction:
- Keep `agentapi++` and `cliproxy` as metaproviders behind one `provider-bridge` contract.
- Keep LiteLLM as transitional compatibility adapter only.
- Reuse Bifrost extension seams (plugin hooks, provider interface, key selector, integration layer) rather than replacing your stack in one cut.

## Lane Findings

### Lane 1 - Bifrost extraction
Recommended adoption points:
- Plugin lifecycle hooks (`Pre/Post HTTP`, `Pre/Post LLM`, streaming chunk hooks).
- Provider abstraction + `KeySelector` as composable metaprovider steering seam.
- MCP managers and agent-mode execution path for tool orchestration.
- Transport integration layer for OpenAI-compatible frontdoor.
Guidance:
- Adopt hooks/integration seams.
- Fork/extend provider interface only where composite-provider behavior is needed.

### Lane 2 - LiteLLM compatibility
Keep for transition:
- Responses API router handler path with feature flag + fallback.
- `LiteLLMCompatExecutor` in bridge adapter layer.
Deprecate over time:
- LiteLLM as control plane runtime.
- Long-term dual-proxy mode (LiteLLM + CLIProxy chain).

### Lane 3 - agentapi++ harness fit
Keep in agentapi control plane:
- FastAPI orchestration, auth/context resolution, prompt/history, MCP composition.
- Operator CLI surface for server/docs/deploy/config flows.
Move/keep in provider runtime plane:
- LLM session lifecycle, streaming, tool execution loop, retry/usage handling.
Harness implication:
- Any thegent harness replacement must preserve operational CLI/API workflows and route into the same control-plane endpoints.

### Lane 4 - cliproxy contractization
Contract target:
- Add first-class `metaproviders` config while reusing OpenAI-compat provider shape.
- Reuse existing translator + registry stack for nested subprovider dispatch.
- Preserve payload rule system for nested parameter mapping.
Validation focus:
- Enforce nested-object payload mapping regressions in fixtures/tests.

### Lane 5 - provider-bridge schema
Core objects:
- `ProviderBridgeRequestEnvelope`
- `ProviderBridgeResponseEnvelope`
- `ProviderDescriptor`
- `CapabilityDescriptor`
Required features:
- `bridge_schema_version`
- provider/subprovider addressing
- capability typed execution (`chat`, `embedding`, `rerank`, `tool_execution`)
- governance metadata (budget/rate/fallback)
- streaming event model
Versioning:
- freeze `v1.0.0`, non-breaking in 1.x, break only in major.

### Lane 6 - rollout/cutover
Staged rollout pattern confirmed:
- shadow -> partial traffic -> full cutover
- explicit rollback gates and measurable exits per phase
Reference artifact:
- `docs/context/rg-dump/lane6-rollout.md`

## Implementation Order (recommended)
1. Freeze bridge schema package (`provider-bridge`), publish v1.0.0.
2. Implement `AgentApiMetaProviderAdapter` and `CliproxyMetaProviderAdapter` against the bridge schema.
3. Add `LiteLLMCompatExecutor` as temporary executor plugin behind the bridge.
4. Integrate Bifrost-style routing/governance as bridge middleware hooks.
5. Run shadow traffic with telemetry parity checks.
6. Shift to partial then full cutover; remove dual-proxy dependencies after exit criteria are met.

## Immediate Build Backlog
1. Create schema files + descriptors package scaffold.
2. Add capability matrix doc with adapter maturity tags (`alpha/beta/ga`) and fallback policy.
3. Implement metaprovider/subprovider descriptors in cliproxy config loader.
4. Add nested payload mapping tests for metaprovider-subprovider dispatch.
5. Add CLI harness compatibility map (thegent command -> agentapi control-plane endpoint).

## Primary Artifacts
- `docs/context/rg-dump/UNIFIED_PROVIDER_BOUNDARY_PLAN_2026-02-23.md`
- `docs/context/rg-dump/BIFROST_vs_LITELLM_for_CLIPROXY_AGENTAPI_2026-02-23.md`
- `docs/context/rg-dump/CHILD_AGENT_WAVE_PACKET_2026-02-23.md`
- `docs/context/rg-dump/lane6-rollout.md`
