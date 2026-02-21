# Bifrost (AI Gateway)

**Product:** Bifrost by Maxim AI
**GitHub:** https://github.com/maximhq/bifrost
**Docs:** https://docs.getbifrost.ai
**License:** Apache 2.0 (Enterprise tier available)
**Language:** Go
**Research date:** 2026-02-20

---

## What It Is

Bifrost is a self-hosted, open-source AI gateway written in Go. It exposes a single
OpenAI-compatible HTTP API and routes requests across 15–20+ LLM providers. It is the fastest
known open-source LLM gateway: 11 µs mean overhead at 5,000 RPS, 50x faster P99 latency vs.
LiteLLM in benchmarks, 100% success rate at scale (vs. 88.78% for LiteLLM at 500 RPS).

Key value props:
- Near-zero latency overhead (Go, connection pooling, zero-alloc weighted key selection)
- Semantic caching (vector similarity, not exact match)
- Three-layer routing: CEL routing rules → governance → adaptive load balancing
- Enterprise governance: virtual keys, hierarchical budgets, rate limiting, SSO, audit logs
- Native MCP gateway (connects to MCP servers, injects tools into model function schema)
- Self-hosted = data sovereignty (prompts never leave controlled infra)

---

## Deployment

**One-liner (local dev):**
```bash
npx -y @maximhq/bifrost           # NPX
docker run -p 8080:8080 maximhq/bifrost   # Docker
```

**With persistence:**
```bash
docker run -p 8080:8080 -v $(pwd)/data:/app/data maximhq/bifrost
```

**Configuration modes:**
- **Web UI** (default): SQLite-backed, real-time config at `http://localhost:8080`
- **File-based**: `config.json` in app directory; disables Web UI; requires restart on changes

**Kubernetes (Helm):**
- Official Helm chart; production HA = 3 replicas, HPA to 20, 70% CPU / 80% memory targets
- PostgreSQL backend recommended for production
- Vector store (Weaviate, Qdrant, Redis) for semantic cache

**Embedded Go SDK:**
```go
import "github.com/maximhq/bifrost/core"
// Bypass HTTP transport entirely; embed in process
```

---

## Authentication

**Client to Bifrost:** Pass `api_key="dummy"` — Bifrost handles all provider credentials.

**With governance enabled:** Client passes `x-bf-vk: <virtual-key>` header.

**Provider credentials:** Configured via Web UI, REST API (`POST /api/providers`), or config.json.

**Environment variable injection in config:**
```json
{"value": "env.OPENAI_API_KEY"}
```

**Secrets management:** Kubernetes secrets, Vault, AWS Secrets Manager, Azure Key Vault.

---

## API Compatibility

**Primary endpoint:**
```
POST http://localhost:8080/v1/chat/completions
Content-Type: application/json

{
  "model": "openai/gpt-4o-mini",
  "messages": [...]
}
```

**Model ID format:** `provider/model` (e.g., `openai/gpt-4o`, `anthropic/claude-3-5-sonnet`)

**SDK-specific base URLs (drop-in replacement):**
```
http://localhost:8080/openai     # OpenAI SDK
http://localhost:8080/anthropic  # Anthropic SDK
http://localhost:8080/genai      # Google GenAI SDK
```

**Additional endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/chat/completions` | POST | Primary; OpenAI-compatible |
| `/api/providers` | POST | Dynamic provider configuration |
| `/v1/mcp/tool/execute` | POST | Explicit MCP tool execution |
| `/metrics` | GET | Prometheus scrape |

---

## Provider Support

15–20+ providers including:

| Provider | Notes |
|----------|-------|
| OpenAI | Full support |
| Anthropic | Claude 3.x, 4.x |
| AWS Bedrock | ARN + deployment mapping required |
| Google Vertex AI | Deployment config required |
| Azure OpenAI | Deployment mapping + api_version required |
| Cerebras | Fast inference |
| Cohere | Command family |
| Mistral | Full family |
| Ollama | Local models |
| Groq | Ultra-fast inference |
| Google GenAI | Gemini family |
| Hugging Face | Via inference API |
| Together AI | Supported |
| Perplexity | Supported |

Special key schemas for cloud providers:
- **Bedrock**: `access_key`, `secret_key`, `session_token`, `region`, `arn`, `deployments` map
- **Azure**: `deployments` map, `api_version` (default: `2024-10-21`)
- **Vertex**: deployment config

---

## Routing / Fallbacks

Three-layer pipeline, evaluated in order (first match wins):

```
1. Routing Rules (CEL expressions)     → override provider+model
2. Governance Routing (weighted random) → from virtual key provider_configs
3. Adaptive Load Balancing (enterprise) → performance-scored key+provider selection
```

### Layer 1: Routing Rules (CEL)

Dynamic, evaluated per request. Context variables available:
```
model, provider
headers["x-tier"], params["region"]
virtual_key_id, team_name, customer_id
budget_used, tokens_used    // 0-100 percentages
request                     // full request object
```

Example:
```cel
headers["x-tier"] == "premium"
budget_used > 85                    // failover at budget threshold
team_name == "ml-research"
```

Scope order: VirtualKey → Team → Customer → Global

### Layer 2: Governance Routing

Uses virtual key `provider_configs`:
- Validates model against `allowed_models` (empty = Model Catalog = all supported)
- Filters providers by budget limits and rate limits
- Weighted random selection among eligible providers
- Fallback chain = remaining providers sorted by weight (descending)

### Layer 3: Adaptive Load Balancing (Enterprise)

Two sub-levels:
- **Provider selection**: scored by error rate (50%), latency MV-TACOS (20%), utilization (5%)
- **Key selection**: always runs; scored by error rate, latency, TPM hits, health state

Health state machine per key: Healthy → Degraded → Failed → Recovering
- 90% penalty reduction in 30s (fast recovery)
- 25% exploration factor probes recovering keys

### Fallback Behavior

On failure: remaining providers tried in weight/score order. Circuit-broken keys (Failed state)
skipped entirely. Keys in Recovering state eligible with reduced probability.

### Model Catalog

Internal catalog downloaded from `https://getbifrost.ai/datasheet` (startup + 24h refresh) and
provider `/v1/models` endpoints. Provides O(1) model-to-provider lookup.

---

## Caching

**Type:** Semantic (vector similarity), not exact-match. This is the key differentiator.

```json
{
  "cache": {
    "provider": "openai",
    "embedding_model": "text-embedding-3-small",
    "ttl": 3600,
    "threshold": 0.8,
    "conversation_history_threshold": 0.7,
    "cache_by_model": true,
    "cache_by_provider": false
  }
}
```

**Vector store backends:** Weaviate, Qdrant, Redis
**Cache hit latency:** ~5ms (vs. ~2,000ms for full LLM call)
**Cache miss with embedding:** ~60ms

Prometheus metric: `bifrost_cache_hits_total`

---

## Observability

### Prometheus (native)

Endpoint: `GET /metrics`

Key metrics:
- `bifrost_upstream_requests_total`
- `bifrost_cost_total`
- `bifrost_cache_hits_total`

Custom labels via request headers:
- `x-bf-prom-team`: tag by team
- `x-bf-prom-environment`: tag by environment

### OpenTelemetry

```json
{
  "telemetry": {
    "service_name": "my-gateway",
    "collector_url": "http://otel-collector:4318",
    "trace_type": "genai_extension",
    "headers": {"Authorization": "Bearer ..."}
  }
}
```

Uses GenAI OpenTelemetry semantic conventions.

### Structured Logging

SQLite (dev) or PostgreSQL (prod). Fields: request, response, tokens, cost, latency, errors.

### Maxim AI Plugin

Native integration; auto-forwards all traces to Maxim platform for evaluation, A/B testing, alerts.

### Web UI Dashboard

Real-time monitoring at `http://localhost:8080` (requires SQLite/Web UI mode):
analytics, provider health, cache hit rate, model catalog, virtual key management, budget charts.

---

## Unique Features

1. **Semantic caching**: Vector-similarity based; most gateways use exact-match only
2. **CEL routing rules**: Common Expression Language expressions with rich request context
3. **Adaptive Load Balancing**: ML-scored two-level (provider + key) routing (Enterprise)
4. **MCP gateway**: Native client+server MCP support with governance on tool execution
5. **Go implementation**: 11 µs overhead vs. ~1ms+ for Python-based alternatives
6. **Hierarchical budgets**: Customer → Team → User → VirtualKey with hard limits per level
7. **Health state machine**: Per-key circuit breaking with fast recovery and exploration probes
8. **Embedded SDK mode**: Go SDK can be embedded in-process, bypassing HTTP transport entirely
9. **Model Catalog**: Self-maintained pricing + availability data refreshed every 24h
10. **Enterprise SSO**: OIDC with Okta, Entra ID; SAML 2.0; LDAP; role sync from IdP groups

---

## Key Differences from OpenRouter / LiteLLM

### vs. OpenRouter

| Dimension | Bifrost | OpenRouter |
|-----------|---------|------------|
| Deployment | Self-hosted (full control) | SaaS only |
| Data sovereignty | Yes | No (data transits OpenRouter) |
| Provider count | 15–20+ | 300+ models, 50+ providers |
| Pricing | Free OSS + paid Enterprise | Per-token markup |
| Semantic cache | Yes | No |
| CEL routing rules | Yes | No |
| MCP gateway | Yes | No |
| Compliance (HIPAA/SOC2) | Yes (self-hosted) | Not documented |
| Performance overhead | 11 µs | N/A (external service) |

### vs. LiteLLM

| Dimension | Bifrost | LiteLLM |
|-----------|---------|---------|
| Language | Go | Python |
| Overhead at 5k RPS | 11 µs | ~1,000+ µs |
| P99 at 500 RPS | 1.68s | 90.72s |
| Memory at 500 RPS | 120MB | 372MB |
| Provider count | 15–20 | 100+ |
| Semantic caching | Yes | Yes (via integration) |
| CEL routing | Yes | No |
| MCP gateway | Yes | No |
| Embedded SDK | Yes (Go) | No |
| Enterprise SSO | Yes | Yes (proxy server) |

---

## Proxy Considerations for thegent CLIProxy

### What Bifrost Does That CLIProxy Does Not

1. **Semantic caching**: CLIProxy has no caching layer at all. Bifrost's vector-similarity cache
   hits at ~5ms vs. full provider call at ~2s. For thegent's use case (repeated agent queries),
   this would be a significant cost and latency win.

2. **CEL routing rules**: CLIProxy's routing is static config-based. Bifrost evaluates CEL
   expressions with request context (headers, budget utilization, team name) per-request. This
   enables dynamic routing without code changes.

3. **Adaptive load balancing with health scoring**: CLIProxy passes through to a single backend
   or uses LiteLLM's round-robin/cheapest/fastest strategies. Bifrost's two-level ML-scored
   selection with per-key health state machines is more sophisticated.

4. **Per-key circuit breaking**: Bifrost tracks health state per API key, not just per provider.
   Multiple keys for the same provider are managed independently with exploration probes.

5. **MCP gateway**: CLIProxy has no native MCP client/server integration. Bifrost centralizes
   tool discovery, schema injection, and governed execution.

6. **Hierarchical budget enforcement**: CLIProxy's cost tracking (WP-5003 / Economic Governance
   Framework) is implemented but operates at a different granularity. Bifrost's Customer → Team →
   User → VirtualKey hierarchy is multi-tenant by design.

7. **Web UI**: CLIProxy has no operational UI. Bifrost ships a built-in dashboard.

8. **Native Prometheus metrics**: CLIProxy has no `/metrics` endpoint. Bifrost exposes
   `bifrost_upstream_requests_total`, `bifrost_cost_total`, `bifrost_cache_hits_total` natively.

9. **Provider-namespaced endpoints**: Bifrost exposes `/openai`, `/anthropic`, `/genai` so SDK
   clients need only a base URL change. CLIProxy requires `transform_responses` mode for
   Responses API compatibility but has no provider-namespaced routing.

10. **Enterprise SSO/RBAC**: CLIProxy has no authentication layer. Bifrost has OIDC, SAML 2.0,
    LDAP, role mapping, and audit logs.

### What CLIProxy Does That Bifrost Does Not

1. **Responses API translation**: CLIProxy translates OpenAI Responses API format to Chat
   Completions and back, emitting the correct 8-event SSE sequence. This is Codex CLI
   compatibility that Bifrost does not implement.

2. **WebSocket transport for Responses API**: CLIProxy bridges WebSocket `/v1/responses` to HTTP
   streaming, enabling persistent multi-turn Codex sessions. Bifrost is HTTP-only.

3. **Codex model metadata enrichment**: CLIProxy transforms `/v1/models` responses into the
   Codex-format schema (`models` key, 20+ required fields, `x-models-etag` header). Bifrost
   uses the standard `data` array format.

4. **thegent-internal model ID mapping**: CLIProxy maps thegent catalog IDs
   (`claude-sonnet-4.5`, `gemini-3-flash`) to backend-specific IDs. Bifrost uses
   `provider/model` format directly.

5. **Agent-specific session management**: CLIProxy integrates with thegent's session registry,
   work stream, and lifecycle hooks. Bifrost is a general-purpose gateway.

### Priority Gaps to Close

| Priority | Feature | Bifrost Approach | CLIProxy Gap |
|----------|---------|-----------------|--------------|
| P1 | Semantic caching | Vector store + threshold | No caching |
| P1 | Native Prometheus | `/metrics` endpoint | No metrics |
| P1 | Health-state circuit breaking | Per-key state machine | LiteLLM-level only |
| P2 | CEL routing rules | Per-request CEL evaluation | Static config only |
| P2 | Adaptive load balancing | ML-scored two-level | cheapest/fastest/round_robin |
| P2 | Virtual key governance | Hierarchical budget + rate limit | Budget tracking only |
| P3 | Web UI dashboard | Built-in at :8080 | None |
| P3 | MCP gateway integration | Native client+server | Separate MCP server only |
| P3 | Enterprise SSO | OIDC + SAML | None |

---

*Full research report: `docs/research/BIFROST_RESEARCH_2026-02-20.md`*
*Related: `docs/research/OPENROUTER_GAP_ANALYSIS_2026-02-20.md`*
*Context for: `docs/context/openrouter.md`*
