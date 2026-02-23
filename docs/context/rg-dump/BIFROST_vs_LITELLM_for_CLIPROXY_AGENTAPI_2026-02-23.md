# Bifrost vs LiteLLM for cliproxy/agentapi Metaprovider Strategy

Date: 2026-02-23
Scope: choose runtime/core direction for a unified metaprovider boundary across `agentapi`, `cliproxy`, and future providers.

## Decision summary
Recommendation:
- Use `cliproxy + agentapi++` as your primary metaprovider boundary.
- Use Bifrost patterns as a source of architecture (and selective code adoption/fork if needed).
- Keep LiteLLM only as a compatibility adapter, not as core control-plane runtime.

Rationale:
- You already have substantial local wrapper/integration investment around LiteLLM and cliproxy.
- Bifrost provides stronger structural primitives for long-term gateway scale (routing/governance/extensibility), but direct replacement now would add migration risk.
- A bridge contract lets you add Bifrost-compatible or Bifrost-derived executors later without client breakage.

## Practical architecture target
Client surfaces:
- one API contract
- one SDK contract package
- one Go CLI contract layer
- Python FastMCP surface remains transport adapter, not decision core

Runtime layers:
1. `provider-bridge` contract (stable)
2. metaprovider adapters:
   - `AgentApiMetaProviderAdapter`
   - `CliproxyMetaProviderAdapter`
3. executor adapters:
   - `LiteLLMCompatExecutor` (transitional)
   - `BifrostStyleExecutor` (incremental adoption)

## Comparison grid
`Bifrost`
- Strengths: extension architecture, governance/routing model, high-performance gateway orientation.
- Risks: migration and integration complexity with your current harness stack.
- Best use: architectural source + optional fork components for policy/routing plugins.

`LiteLLM`
- Strengths: broad provider compatibility and existing wrapper footprint in your stack.
- Risks: wrapper sprawl and long-term control-plane clunkiness for your specific goals.
- Best use: compatibility and migration shim while bridge solidifies.

`cliproxy + agentapi++`
- Strengths: matches your metaprovider vision and current operational reality.
- Risks: requires strict boundary contract discipline to avoid more divergence.
- Best use: primary boundary owners and orchestrator surface.

## Migration stance
Phase 1 (now):
- Freeze `provider-bridge` schema and capability descriptors.
- Wrap current metaproviders behind the bridge.

Phase 2:
- Move routing/governance semantics into bridge middleware inspired by Bifrost patterns.
- Keep LiteLLM adapter for backward compatibility.

Phase 3:
- Replace or deprecate LiteLLM-dependent internals where Bifrost-style executors or native adapters are stable.

## Non-goals for MVP
- full runtime replacement of harness system in one cut
- simultaneous rewrite in Zig/Rust before boundary contract is stable
- forcing MCP and CLI into one codebase now

## Immediate implementation next steps
1. Add `provider-bridge` schema package and version it (`v0alpha1`).
2. Implement `AgentApiMetaProviderAdapter` and `CliproxyMetaProviderAdapter` against that schema.
3. Add capability matrix with nested provider support and executor tags.
4. Add fallback + governance middleware envelope (budget/rate/retry/routing hints).
5. Keep `LiteLLMCompatExecutor` while migrating traffic by route.
