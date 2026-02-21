# Kong AI Gateway

> Context document for thegent competitive analysis and feature parity audit.
> Full research: `docs/research/KONG_AI_GATEWAY_RESEARCH_2026-02-20.md`

---

## What It Is

Kong AI Gateway is a **plugin-based connectivity and governance layer** for LLM traffic, built on top of Kong Gateway (Nginx/LuaJIT). It does not replace Kong — it extends it with 21 AI-specific plugins.

Design philosophy:
- LLM traffic gets the same controls as REST/gRPC APIs (auth, rate limiting, WAF, RBAC, logging, circuit breakers)
- No code changes required in applications — platform teams configure policy at the gateway layer
- Provider-agnostic universal API: clients send OpenAI-format; Kong translates to any backend provider
- Composable: stack plugins on any route declaratively in YAML

---

## Deployment (OSS / Konnect / Enterprise)

| Tier | Details |
|------|---------|
| **OSS** | Free. 6 AI plugins. No GUI. Self-hosted. |
| **Konnect (SaaS)** | Cloud control plane + self-hosted data planes. Free tier for AI. Full analytics. ~$105/mo/service + $34.25/1M requests. |
| **Enterprise** | Self-hosted. All 21 AI plugins. Kong Manager GUI. RBAC, SSO/OIDC, audit logs, developer portal. $50k+/year. |

All modes support declarative YAML (DB-less), Kubernetes via KIC, and hybrid topologies.

**Key friction**: Customization is in **Lua**. No Python plugin runtime. AI teams must learn Lua or Go.

---

## Core AI Plugins

### Free / OSS

| Plugin | What It Does |
|--------|-------------|
| `ai-proxy` | Routes requests to a single LLM provider. Translates OpenAI format ↔ provider format. |
| `ai-prompt-decorator` | Injects system messages before/after user chat history. Hidden from client. |
| `ai-prompt-guard` | Regex allow/deny list on prompt content. Blocks before LLM call. |
| `ai-prompt-template` | Fill-in-the-blank templates with `{{variable}}` injection prevention. |
| `ai-request-transformer` | Uses a (separate) LLM to rewrite the upstream request body. |
| `ai-response-transformer` | Uses a (separate) LLM to rewrite the upstream response body. |

### Enterprise / AI License

| Plugin | What It Does |
|--------|-------------|
| `ai-proxy-advanced` | Multi-target load balancing across providers (7 algorithms). |
| `ai-rate-limiting-advanced` | Token- and cost-based rate limiting per consumer/window. |
| `ai-semantic-cache` | Vector similarity caching (Redis/pgvector). Avoids redundant LLM calls. |
| `ai-semantic-prompt-guard` | Embedding-based semantic allow/deny. Multilingual. Beats regex circumvention. |
| `ai-semantic-response-guard` | Same as above, applied to LLM response content. |
| `ai-rag-injector` | Gateway-level RAG: auto-retrieves context from vector DB, injects into prompt. |
| `ai-pii-sanitizer` | Detects/redacts 20+ PII categories across 12 languages. Re-inserts in response. |
| `ai-prompt-compressor` | LLM-based prompt compression (up to 5x token reduction). |
| `ai-llm-as-judge` | Use one LLM to score/evaluate responses from another LLM. |
| `ai-mcp-proxy` | MCP protocol gateway (passthrough, REST-to-MCP conversion, aggregation). |
| `ai-mcp-oauth2` | OAuth2 for MCP endpoints. |
| `ai-aws-guardrails` | AWS Bedrock Guardrails integration. |
| `ai-azure-content-safety` | Azure Content Safety integration. |
| `ai-gcp-model-armor` | Google Cloud Model Armor integration. |
| `ai-lakera-guard` | Lakera Guard prompt injection detection. |

---

## ai-proxy / ai-proxy-advanced

### ai-proxy (OSS)

Single upstream. Accepts OpenAI-format → translates → routes → translates back.

Supported route types: `llm/v1/chat`, `llm/v1/completions`, `llm/v1/embeddings`, `llm/v1/audio/transcriptions`, `llm/v1/audio/speech`, `llm/v1/images/generations`.

Supported providers: OpenAI, Anthropic, Azure OpenAI, AWS Bedrock, Gemini, Vertex AI, Cohere, Mistral, Hugging Face, Llama.

### ai-proxy-advanced (Enterprise)

Multiple targets with load balancing. Key additions over ai-proxy:

- Unlimited targets with independent auth, models, weights
- 7 load balancing algorithms (see below)
- Configurable failover criteria (e.g., failover on HTTP 429, 502)
- Circuit breakers (v3.13+): auto-removes unhealthy targets
- Cost-based routing via `lowest-usage` + per-target pricing config
- Native LLM format support (skip OpenAI translation where not needed)

---

## Semantic Caching

Plugin: `ai-semantic-cache` (Enterprise)

Stores LLM responses in a vector database by semantic meaning. On new requests:
1. Embed the prompt
2. VSS query Redis/pgvector for similar prior requests (cosine similarity)
3. Cache hit at threshold → return cached response (no LLM call)
4. Cache miss → call LLM, store embedding + response

Backends: Redis VSS, AWS MemoryDB, PostgreSQL pgvector, AWS ElastiCache, Azure Managed Redis, Google Cloud Memorystore.

Default TTL: 300 seconds. Configurable threshold (0.0–1.0). Respects `Cache-Control` headers.

Headers: `X-Cache-Status: Hit|Miss`, `X-Cache-Key`, `Age`, `X-Cache-Ttl`.

Both exact caching (hash match) and semantic caching run simultaneously.

---

## AI Rate Limiting (Token-Based)

Plugin: `ai-rate-limiting-advanced` (Enterprise)

Extends standard rate limiting with LLM token awareness.

**Token strategies**: `total_tokens`, `prompt_tokens`, `completion_tokens`, `cost` (USD).

**Window strategies**: `local` (per-node in-memory), `cluster` (data store), `redis`.

**Scoping**: Per consumer, per consumer group, per route, per service.

**Enforcement lag**: Costs from the current response apply to the *next* request (one-request lag due to LLM returning token counts post-completion).

Response headers: `X-AI-RateLimit-Limit-{window}-{provider}`, `X-AI-RateLimit-Remaining-...`, `X-AI-RateLimit-Retry-After`.

---

## Guardrails (prompt-guard, semantic-prompt-guard)

### ai-prompt-guard (OSS) — Regex-Based

- Allow list: request must match at least one pattern
- Deny list: request matching any pattern → HTTP 400
- Deny takes precedence over allow
- Limitation: circumventable by paraphrasing

### ai-semantic-prompt-guard (Enterprise) — Semantic

- Vector embedding comparison against reference prompts
- Multilingual (embedding models handle cross-language semantic similarity)
- Embedding providers: Azure, Bedrock, Gemini, HuggingFace, Mistral, OpenAI
- Storage: Redis VSS / pgvector
- Also: `ai-semantic-response-guard` applies same to LLM responses

### External Guardrail Integrations (Enterprise)

AWS Bedrock Guardrails, Azure Content Safety, GCP Model Armor, Lakera Guard.

---

## Request/Response Transformation

### ai-request-transformer (OSS)

Runs before `ai-proxy`. Sends the entire request body to a configured LLM with an admin-defined transformation prompt. LLM's response becomes the new request body forwarded upstream.

Use cases: normalize request formats, inject context, translate schemas.

### ai-response-transformer (OSS)

Runs after `ai-proxy`. Sends response body to a configured LLM. Transformed response returned to client.

Feature: `parse_llm_response_json_instructions: true` — LLM can set response headers, status codes, and body in its response.

---

## Observability

### Metrics

- Prometheus: token counts, latency (TTFT, e2e), error rates, cache hit/miss, cost per request
- OpenTelemetry: GenAI span attributes (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reason`)
- Streaming: Kong parses SSE chunks to extract token counts mid-stream

### Integrations

Grafana (official dashboard #24057), Prometheus, Datadog, Dynatrace, Langfuse, AWS CloudWatch, Konnect Advanced Analytics (Enterprise).

### Audit Logging

Full request/response body logging with redaction options. Structured JSON. Compliance-grade.

---

## Load Balancing Across Providers

Via `ai-proxy-advanced`. Seven algorithms:

| Algorithm | Strategy |
|-----------|----------|
| `round-robin` | Weighted distribution |
| `consistent-hashing` | Sticky sessions by header |
| `least-connections` | Route to target with most spare capacity (v3.13+) |
| `lowest-latency` | Peak EWMA latency tracking → fastest model |
| `lowest-usage` | Route by prompt/completion tokens or USD cost |
| `semantic` | Vector similarity: route prompt to model whose description matches best |
| `priority` | Tiered failover groups; cascade on failure |

Failover: configurable `failover_criteria` (HTTP status codes). Circuit breakers (v3.13+) with configurable `max_fails` and `fail_timeout`.

---

## Enterprise Features

Beyond AI plugins, Kong Enterprise adds:

- **Kong Manager GUI**: Visual configuration and monitoring
- **RBAC**: Role-based access with workspace isolation
- **SSO / OIDC**: Enterprise identity provider integration
- **Audit Logs**: Full admin action and API request audit trail
- **Developer Portal**: Self-service API/AI endpoint discovery for internal teams
- **Konnect Advanced Analytics**: Pre-built cost/token/latency dashboards
- **decK**: Declarative configuration management (git-compatible)
- **All 21 AI plugins**: Enterprise-only AI plugins require AI license add-on

---

## Key Differences from OpenRouter / LiteLLM / Portkey

| | Kong AI Gateway | OpenRouter | LiteLLM | Portkey |
|--|----------------|------------|---------|---------|
| Architecture | Plugin on API gateway (Nginx) | Cloud SaaS router | Python proxy + SDK | Cloud + self-hosted |
| Self-hostable | Yes | No | Yes | Enterprise |
| Provider breadth | 12+ (curated) | 500+ | 100+ | 200+ |
| Semantic routing | Yes (native vector) | No | No | No |
| Semantic caching | Yes | No | No | Yes |
| MCP gateway | Yes (4 modes + ACLs) | No | Basic | No |
| RAG injection | Yes (gateway layer) | No | No | No |
| PII sanitization | Yes (20+ categories) | No | No | Partial |
| Enterprise governance | Yes (RBAC, SSO, audit) | None | None | Partial |
| Performance | Highest (Nginx/LuaJIT) | High (cloud) | Lowest (Python) | Medium |
| Customization | Lua (niche) | None | Python | JS |
| Cost | Highest ($50k+/yr enterprise) | Free + per-call | Free (OSS) | Free + Enterprise |

**Kong's unique moat**: Semantic routing, gateway-layer RAG, MCP gateway with tool ACLs, and unified governance across AI + traditional API traffic.

---

## What thegent Should Steal

Ordered by impact:

1. **Semantic load balancing**: Route agent tasks to specialist models via prompt-model description similarity (vector embeddings + cosine similarity). Kong's `semantic` algorithm applied to thegent's model routing.

2. **Token budget enforcement per session/agent**: Kong's `ai-rate-limiting-advanced` `cost` strategy — enforce per-agent USD budgets, not just request counts.

3. **Priority failover chains**: Declarative primary/secondary/emergency model sequences. Kong's `priority` algorithm as a routing config primitive.

4. **Semantic response caching**: Cache agent LLM responses by semantic query similarity. Reuse near-identical results without re-calling the LLM.

5. **Circuit breaker per provider**: When a provider fails N times in a window, remove from routing pool for a timeout period. Auto-restore on recovery.

6. **Cost-aware routing**: `lowest-cost` mode routes to the cheapest adequate model. Informed by per-model token pricing config.

7. **MCP tool ACLs**: Per-agent fine-grained authorization over which MCP tools an agent can invoke. Prevent privilege escalation.

8. **Prompt decoration as routing middleware**: Inject system prompts at the CLIProxy routing layer, not in agent code.

9. **EWMA latency tracking**: Track time-per-output-token per provider using exponential moving average. Route to fastest active provider.

10. **Consistent-hashing for conversation sessions**: Route multi-turn conversations to the same provider for context consistency.
