# Web-Expanded Tech Landscape (Metaprovider Program)

Date: 2026-02-23
Scope: external libs/repos/projects to strengthen `agentapi++` + `cliproxy` + unified `provider-bridge` strategy.

## Executive Direction
Use a layered architecture, not a single replacement:
1. `provider-bridge` remains canonical contract.
2. `agentapi++` + `cliproxy` stay metaprovider/control-plane adapters.
3. Add an edge/core gateway layer only for policy/traffic/observability hardening.
4. Keep LiteLLM only as compatibility bridge during migration.

## Ranked Candidate Shortlist

### Tier 1 - Immediate pilot candidates
- Inference Gateway
  - Why: OSS, OpenAI-compatible, multi-provider, MCP-aware hooks, deployment-ready.
  - Use: reference implementation for gateway runtime and MCP-aware routing seams.
  - Link: https://github.com/inference-gateway/inference-gateway

- Kong AI Gateway
  - Why: mature plugin surface, AI-specific plugins, strong enterprise observability/policy posture.
  - Use: edge policy/governance layer (auth, rate/cost controls, prompt guardrails).
  - Link: https://docs.konghq.com/gateway/latest/ai-gateway/

- Envoy AI Gateway
  - Why: Kubernetes-native CRD model, strong tracing/metrics story, mesh/edge flexibility.
  - Use: internal/core data-plane option when you need Envoy-native operations.
  - Link: https://aigateway.envoyproxy.io/

- Buf + Connect (+ OpenAPI pipeline)
  - Why: versioned contract distribution, multi-language artifact generation, CLI-friendly HTTP/RPC surface.
  - Use: foundation for versioned `provider-bridge` API/SDK/CLI contracts.
  - Link: https://buf.build/docs/bsr/generated-sdks/

### Tier 2 - Near-term expansion
- Agentgateway (Rust)
  - Why: MCP/A2A-aware LLM gateway/data plane with provider breadth.
  - Use: compare against Bifrost/Inference Gateway as core runtime candidate.
  - Link: https://agentgateway.dev/docs/local/latest/

- APISIX AI Gateway
  - Why: plugin flexibility (Lua/Go/Wasm), pragmatic gateway hardening and logging.
  - Use: alternative edge layer where APISIX footprint already exists.
  - Link: https://apisix.apache.org/ai-gateway/

- Fern / Speakeasy
  - Why: accelerates SDK+docs generation from OpenAPI.
  - Use: pair with Buf/OpenAPI flow for external developer-facing SDK channels.
  - Links:
    - https://www.buildwithfern.com/
    - https://www.speakeasy.com/product/sdk-generation

### Tier 3 - Exploratory
- ContextForge MCP Gateway, Multi-MCP proxy, MCP Bridge, mcp-openapi-proxy
  - Why: useful for MCP federation and transport unification.
  - Use: future MCP federation layer once Python FastMCP becomes active concern.
  - Links:
    - https://www.mcpnow.io/en/server/multi-mcp-kfirtoledo-multi-mcp
    - https://gofastmcp.com/v2/servers/proxy
    - https://arxiv.org/abs/2504.08999
    - https://www.bestofthemcp.com/mcp/matthewhand/mcp-openapi-proxy

- InferXgate
  - Why: high-performance claims; potentially strong for self-hosted throughput.
  - Use: benchmark-only candidate before production confidence.
  - Link: https://inferxgate.com/

## Agent Runtime Options (Harness Replacement Surface)
- LangGraph/LangSmith Deployment
  - Fit: operational CLI and stateful workflow orchestration.
  - Link: https://docs.langchain.com/langgraph-platform/cli

- AG2/AutoGen ecosystem with MCP support
  - Fit: human-in-the-loop and multi-agent orchestration where approvals are required.
  - Link: https://research.aimultiple.com/agentic-frameworks//

- OpenAI Agents SDK
  - Fit: modern agents abstractions with guardrails/tracing, useful for narrow runtime lanes.
  - Link: https://openai.github.io/openai-agents-python/

## Production Practices to Copy (from case studies)
- Route/fallback policy as data (versioned configs), not app code.
- Health-aware automatic fallback with quota-aware routing.
- Per-tenant/provider cost attribution in gateway layer.
- BYOK-first and model access policy at gateway boundary.
References:
- https://aws.amazon.com/blogs/apn/scale-ai-application-in-production-build-a-fault-tolerant-ai-gateway-with-snapsoft/
- https://apiary-gateway.github.io/case-study/
- https://docs.helicone.ai/gateway/provider-routing
- https://aws.amazon.com/solutions/guidance/multi-provider-generative-ai-gateway-on-aws/

## Recommended Architecture Delta
1. Keep current metaprovider plan (`agentapi++` + `cliproxy`) unchanged.
2. Add gateway layer as independent concern:
   - Edge mode: Kong or APISIX for auth/policy/analytics.
   - Core mode: Envoy AI Gateway or Bifrost-style runtime for routing/execution.
3. Lock `provider-bridge` contract versioning:
   - OpenAPI + Buf labels
   - generated SDKs (Go/Python/TS first)
   - CLI consumes same generated client surface.
4. Run dual runtime pilot:
   - current stack vs one Tier-1 gateway candidate
   - compare latency, fallback success rate, cost controls, operator ergonomics.

## 30/60/90 Plan
- 30 days
  - Freeze `provider-bridge` v1 contract.
  - Add gateway-neutral routing policy schema.
  - Stand up one Tier-1 gateway PoC in shadow mode.

- 60 days
  - Integrate cost/rate governance and fallback analytics.
  - Validate SDK+CLI generated artifacts from single contract pipeline.
  - Run controlled traffic split.

- 90 days
  - Choose permanent edge/core gateway stack.
  - Decommission LiteLLM-control-plane dependence.
  - Keep LiteLLM adapter only where compatibility is still needed.

## Decision Notes
- Strong recommendation: do not rewrite everything into Zig/Rust first.
- Strong recommendation: finish contract and adapter boundaries before deep runtime swaps.
- Strong recommendation: use case-study-backed governance patterns early, not as phase-late add-ons.
