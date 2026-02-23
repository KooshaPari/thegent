# Unified Provider Boundary Plan (agentapi++, cliproxy, and Bifrost/LiteLLM)

## What I completed now

1. `agentapi++` cloned from `agentapi` as a local fork workspace.
2. `bifrost` clone completed and now points at `main` in `thegent` workspace.
3. Pulled upstream docs into context dump:
   - `docs/context/rg-dump/bifrost-upstream-docs` (Bifrost README/AGENTS/docs)
   - `docs/context/rg-dump/litellm-upstream-docs` (LiteLLM README/docs)
   - `docs/context/rg-dump/agentapi++-selected` (agentapi++ docs/API/spec subset)
4. Existing local context corpus preserved:
   - `docs/context/rg-dump/cliproxy-docs`
   - `docs/context/rg-dump/providers_api.md`, `third-party-providers.md`, `model-provider-catalog.md`

## Repository map for planning

- `agentapi++/` (fork copy from current `agentapi`)
  - Current metaprovider candidate: CLI + MCP + service boundary.
  - Local docs subset: `docs/context/rg-dump/agentapi++-selected/*`
- `bifrost/` (upstream)
  - Docs mirror: `docs/context/rg-dump/bifrost-upstream-docs`
- `litellm/` docs mirror: `docs/context/rg-dump/litellm-upstream-docs`
- `cliproxyapi-plusplus/` and `agentapi` docs currently already in context from earlier pass.

## Proposed execution boundary (single contract)

## 1) Create a `provider-bridge` contract surface

Keep all runtimes behind one interface for:
- chat completion
- embeddings
- reranking/aux endpoints (optional)
- tool execution (MCP-aware)
- admin/provider config + model catalog lookups

Suggested primitives:
- `ProviderAdapter` (stateless façade)
- `ProviderRegistry` (providers + aliases + aliases→subproviders)
- `Executor` (sync/streaming)
- `MetaproviderAdapter` for providers that manage sub-providers.

## 2) Treat `agentapi` and `cliproxy` as meta-providers

- `agentapi` remains the orchestration tier for CLI harness + transport policy.
- `cliproxy` remains provider/runtime composition layer.
- Each exposes one internal adapter implementing the same `ProviderAdapter` contract.
- Add explicit `SubProviderDescriptor` objects so nested providers are first-class and composable.

## 3) Keep `cli` + `mcp` separate initially

- `cli`: Go boundary project for command orchestration.
- `mcp`: FastMCP Python service for tool surface only.
- Publish a stable client interface; ignore CLI internals in the SDK boundary.

## 4) Practical integration strategy

- Phase A: Read-only adapter for both providers
  - Wrap `agentapi` and `cliproxy` into bridge with capability discovery only.
- Phase B: Execution + routing unification
  - Standardize request/response envelope and streaming adapter contract.
- Phase C: Governance and fallback policies
  - Map routing hooks from Bifrost/CEL/governance ideas into adapter middleware:
    - provider scope, budget/rate checks, error-budget routing, fallback order.

## 5) “Two separate SDK projects” guidance

Given your current constraints:
- `agentapi-sdk` should target `agentapi++` + cli orchestration (Rust/FastMCP integration points, config model, contracts).
- `provider-sdk` should target `cliproxy` (transport, executors, runtime provider wrappers).
- Shared `provider-bridge` schema package between both (generated OpenAPI/JSON schema).

## 6) Why this is aligned with your goal

- Both `agentapi` and `cliproxy` are used as metaproviders exposing subproviders.
- Clients consume one interface only (metaprovider-aware, not provider-specific).
- Enables replacing internals later: Bifrost plugin-style or LiteLLM compatibility shim can be added as another adapter without touching clients.

## 7) Suggested next concrete tasks

1. Freeze the boundary schema (DTOs + request/response + telemetry fields).
2. Write `agentapi++` adapter shim + `cliproxy` adapter shim against that schema.
3. Add one capability matrix doc (`providers_api.md`) with implementation tags for each adapter.
4. Add governance extension points (routing hints, retry labels, cache hints, cost budget fields).
5. Add docs consolidation index updates from upstream dumps (run `find docs/context/rg-dump -maxdepth 3` in each context pass).
