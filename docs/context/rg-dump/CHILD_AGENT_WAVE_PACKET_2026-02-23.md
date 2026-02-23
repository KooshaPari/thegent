# Child-Agent Wave Packet (6 Lanes)

Date: 2026-02-23
Goal: finalize a unified provider boundary where `agentapi` + `cliproxy` are metaproviders and client surfaces depend on one interface.

## Lane 1 - Bifrost core/extension extraction
Owner output:
- Identify concrete plugin/extension seams from `bifrost`.
- Map routing and governance hooks usable as middleware in `provider-bridge`.
- Produce "adopt/fork/avoid" table per seam.
Inputs:
- `bifrost/`
- `docs/context/rg-dump/bifrost-upstream-docs/`
Deliverable:
- `docs/context/rg-dump/lane1-bifrost-extraction.md`

## Lane 2 - LiteLLM compatibility surface analysis
Owner output:
- Enumerate LiteLLM interfaces currently valuable for your stack (routing, proxy config, provider normalization).
- List wrappers currently duplicated in `thegent/cliproxy` and cost of keeping them.
Inputs:
- `docs/context/rg-dump/litellm-upstream-docs/`
- `docs/context/rg-dump/LITELLM_RESEARCH_SUMMARY.md`
Deliverable:
- `docs/context/rg-dump/lane2-litellm-compat.md`

## Lane 3 - agentapi++ harness/orchestrator fit
Owner output:
- Inventory what in `agentapi++` should remain control plane vs move to provider runtime plane.
- Map replacement path for current CLI harness logic in `thegent`.
Inputs:
- `agentapi++/`
- `docs/context/rg-dump/agentapi++-selected/`
Deliverable:
- `docs/context/rg-dump/lane3-agentapi-harness.md`

## Lane 4 - cliproxy metaprovider contractization
Owner output:
- Define cliproxy adapter contract to plug into unified boundary with minimal churn.
- Propose stable capability descriptors for nested/sub-providers.
Inputs:
- `cliproxyapi-plusplus/`
- `docs/context/rg-dump/cliproxy-docs/`
Deliverable:
- `docs/context/rg-dump/lane4-cliproxy-contract.md`

## Lane 5 - Unified API/SDK/CLI contract package
Owner output:
- Draft canonical request/response schema package (`provider-bridge`) for API + SDK + CLI.
- Specify compatibility matrix for OpenAI-style transport + internal executor hints.
Inputs:
- `docs/context/rg-dump/providers_api.md`
- `docs/context/rg-dump/model-provider-catalog.md`
- `docs/context/rg-dump/UNIFIED_PROVIDER_BOUNDARY_PLAN_2026-02-23.md`
Deliverable:
- `docs/context/rg-dump/lane5-bridge-schema.md`

## Lane 6 - Migration/rollout program
Owner output:
- Produce staged rollout plan with measurable exits:
  - shadow mode
  - partial traffic
  - full cutover
- Include rollback envelope and test/evidence gates.
Inputs:
- all lane outputs
Deliverable:
- `docs/context/rg-dump/lane6-rollout.md`

## Aggregation contract (mandatory)
Each lane must return:
1. Facts with path evidence.
2. Decision proposals.
3. Risks.
4. Immediate next 3 implementation tasks.

## Session blocker note
Child-agent execution is currently blocked by active thread cap (`max 6`) in this session.
This packet is staged so execution can resume immediately once thread slots are available.
