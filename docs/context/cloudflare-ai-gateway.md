# Cloudflare AI Gateway

**Last updated:** 2026-02-20
**Research source:** `docs/research/CLOUDFLARE_AI_GATEWAY_RESEARCH_2026-02-20.md`

---

## What It Is (Edge-Hosted Gateway)

Cloudflare AI Gateway is a fully managed, edge-native AI control plane. It proxies all AI API requests through Cloudflare's global network (300+ PoPs) before forwarding them to providers. Unlike LiteLLM (self-hosted) or Portkey (SaaS centralized), Cloudflare's gateway runs on its CDN infrastructure — the same backbone used for its core DDoS/CDN product.

Key identity: it is a **proxy** (not a router or SDK). You point your existing OpenAI client at a different URL. No code changes beyond `baseURL`.

Introduced: 2023. Major feature expansion: August 2025 (dynamic routing, DLP, BYOK, Unified Billing).

---

## URL Structure / Authentication

### Base URL Pattern

```
https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/{provider}
```

### OpenAI-Compatible Unified Endpoint

```
https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/compat
```

This is the recommended drop-in replacement for `https://api.openai.com/v1`. Any OpenAI SDK client pointing here will work across all supported providers without further code changes.

### Universal Endpoint (Fallback Chains)

```
POST https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}
```

Request body is a JSON array of provider objects tried in sequence.

### Dynamic Routing Endpoint

```
https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/dynamic/{route_name}
```

### Authentication Modes

| Mode | How | When to Use |
|------|-----|------------|
| **Pass-through** | Provider key in `Authorization: Bearer {key}` as normal | Default for unauthenticated gateways |
| **Gateway Auth** | Add `cf-aig-authorization: Bearer {cf_token}` alongside provider key | When gateway-level auth is enabled |
| **BYOK** | No provider key in request; add `cf-aig-byok-alias: {alias}` | Keys stored in Cloudflare Secret Store |
| **Unified Billing** | Only `Authorization: Bearer {cf_token}`; no provider key | For supported providers via Cloudflare credits |

---

## OpenAI Compatibility

Full drop-in replacement for OpenAI SDK clients:

```python
from openai import OpenAI

client = OpenAI(
    api_key="{cf_api_token_or_provider_key}",
    base_url="https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/compat"
)
```

Supported OpenAI endpoints via `/compat`:
- `/chat/completions`
- `/responses`
- `/v1/models` (lists available models with cost metadata)

The gateway translates provider-specific request/response formats automatically via its Unified Request/Response Translation layer (launched August 2025).

---

## Providers Supported

**24 providers** as of early 2026:

Workers AI, OpenAI, Anthropic, Google AI Studio, Google Vertex AI, Azure OpenAI, Amazon Bedrock, Mistral AI, Cohere, Groq, xAI (Grok), DeepSeek, Replicate, HuggingFace, Perplexity, OpenRouter, ElevenLabs, Cartesia, Cerebras, Fal AI, Baseten, Ideogram, Deepgram, Parallel.

Plus: **Custom Providers** — any OpenAI-compatible endpoint (self-hosted, regional, proprietary).

Unified Billing providers (5): OpenAI, Anthropic, Google AI Studio, xAI, Groq.

---

## Caching

- **Strategy:** Exact match only. Semantic/vector caching is **planned, not yet released**.
- **Scope:** Text and image responses. Audio/video not cached.
- **Backend:** Cloudflare's global CDN edge — responses served from nearest PoP.
- **Claimed benefit:** Up to 90% latency reduction on cache hits.

### Per-Request Cache Control Headers

| Header | Purpose |
|--------|---------|
| `cf-aig-cache-ttl` | TTL in seconds (min 60, max ~2.6M / ~1 month) |
| `cf-aig-skip-cache` | Bypass cache entirely for this request |
| `cf-aig-cache-key` | Override default key (use for per-user caching by embedding user ID) |
| `cf-aig-cache-status` | Response: `HIT` or `MISS` |

**Per-user caching:** Not native. Implement by setting `cf-aig-cache-key` to include a user identifier — this namespaces cache entries per user.

**Cache hits:** Always report $0 cost in analytics.

**Note:** Volatile cache — simultaneous identical requests may not share a cache entry during initial population.

---

## Rate Limiting

### Gateway-Level Configuration

Set in dashboard or via API. Applies uniformly to all requests through the gateway.

| Parameter | Values |
|-----------|--------|
| `rate_limiting_interval` | Seconds (e.g., 60) |
| `rate_limiting_limit` | Max requests in interval |
| `rate_limiting_technique` | `fixed` (time buckets) or `sliding` (rolling window) |

- **429 Too Many Requests** returned when exceeded.
- No per-user or per-IP rate limiting natively at this level.

### Per-User / Per-Key Rate Limiting

Use **Dynamic Routing Rate Limit nodes** and **Budget Limit nodes** for per-user quota enforcement. This is the recommended path for fine-grained rate limiting. Supports fallback to cheaper model when quota exceeded.

---

## Observability / Analytics

### Analytics Dashboard

Metrics tracked:
- Total requests
- Token usage (input + output tokens)
- Cost estimates (per provider, per model)
- Error counts
- Cache hit rate (%)

Access: Cloudflare Dashboard > AI > AI Gateway. GraphQL API for external querying.

### Logging

Logged per request: prompt, response, provider, model, timestamp, status, tokens, cost, duration, cache status, custom metadata.

| Plan | Log Limit |
|------|-----------|
| Free | 100,000 total across all gateways |
| Paid | 10M per gateway |

Storage rate limit: 500 logs/second per gateway. Max log size: 10 MB (larger not stored).

Storage behavior: configure auto-delete oldest, stop at limit, or manual deletion.

**Logpush:** Export logs to S3, R2, Splunk, New Relic, etc. Workers Paid plan only. 4 jobs max; $0.05/M requests overage.

### Custom Metadata

Tag requests via `cf-aig-metadata` header (JSON, max 5 entries, string/number/boolean only):

```
cf-aig-metadata: {"user_id": "u_123", "session": "abc", "env": "prod"}
```

Metadata appears in logs and enables filtering.

### OpenTelemetry

Export traces to any OTEL backend (Jaeger, Grafana, Datadog, etc.) — added 2025-09-24.

### Response Headers for Observability

| Header | Description |
|--------|-------------|
| `cf-aig-event-id` | Unique event ID (all requests, including failures) |
| `cf-aig-log-id` | Log ID for feedback submission |
| `cf-aig-step` | Fallback chain step that handled request (0=primary) |
| `cf-aig-cache-status` | `HIT` or `MISS` |

### Cost Tracking

Per-request cost based on token usage × model pricing. Custom pricing override per request:

```
cf-aig-custom-cost: {"per_token_in": 0.000001, "per_token_out": 0.000002}
```

Covers voice models (added 2025-11-14) and async video (Sora 2, Veo 3; added 2025-10-24).

---

## Guardrails

Added 2025-02-26.

- Real-time content moderation for both **incoming prompts** and **outgoing responses**
- Applied uniformly across all providers through a single configuration
- Categories configurable (examples: violence, hate, sexual content)
- Per-category action: **block** (reject request/response) or **flag** (allow + log)
- Audit trails for all guardrail decisions (compliance: GDPR, HIPAA, etc.)
- Works at edge, before provider is called (if blocking prompt)

---

## Data Loss Prevention (DLP)

Added 2025-08-28. Part of the AI Gateway Firewall.

- Scans both incoming prompts and outgoing responses
- Pre-built profiles: financial data, SSN/Tax IDs, PII, healthcare data
- Custom pattern profiles supported
- Compliance frameworks: GDPR, HIPAA, PCI DSS
- Per-request logs show matched profiles and action taken
- Actions: **block** or **alert/flag**
- Configured as gateway-level policy (not per-request)

---

## Evaluations

- Create **datasets** from filtered log subsets (up to 10 per gateway)
- Run evaluators against datasets to measure performance
- **Human Feedback evaluator** (open beta): measures % positive ratings
- Metrics: cost, latency, accuracy
- **Model Playground** (added 2025-10-14): test and compare models in the dashboard without code
- Feedback submission API uses `cf-aig-log-id` response header
- Additional evaluators planned but not yet released

---

## Workers AI Integration

Workers AI = Cloudflare's own edge GPU inference service. Deep integration with AI Gateway:

- Access via `env.AI.run()` in Workers — no extra API token after 2025-11-14
- Same gateway features (caching, logging, guardrails) apply to Workers AI calls
- Workers AI runs colocated with the gateway on Cloudflare edge — zero extra network hop
- Supports Deepgram models via WebSocket
- Supports Pipecat models (voice/audio pipelines)
- Native binding: pre-authenticated within the Cloudflare account context

---

## Dynamic Routing

Flagship feature added August 2025.

Visual (drag-and-drop) or JSON-based routing flow configuration. No code changes needed. Deployed as versioned routes with instant rollback.

### Node Types

| Node | Purpose |
|------|---------|
| **Conditional** | Branch on request body, headers, or metadata expressions |
| **Percentage** | Probabilistic traffic split (A/B testing, gradual rollouts) |
| **Rate Limit** | Per-key request quotas; fallback on exceeded |
| **Budget Limit** | Per-key spend caps per period |
| **Provider** | Route to specific provider/model |
| **Fallback** | Handle provider failure |

### Use Cases

- Paid users → GPT-4o, free users → GPT-4o-mini
- 80% GPT-4o / 20% Claude 3.5 Sonnet A/B test
- Cap free tier at 100 requests/day, fallback to cheaper model
- Chain: sanitize prompt → main model → post-process response
- Geography-based model selection

---

## Unique Edge Advantages

1. **CDN-Native Caching**: Responses cached at 300+ global edge PoPs. Cache hits served at CDN speeds, not from a centralized server.

2. **Workers AI Colocation**: When using Workers AI, inference and gateway are on the same edge node — no external network hop.

3. **DDoS Protection Bundled**: Cloudflare's core DDoS mitigation applies to AI Gateway traffic automatically.

4. **Edge Routing Decisions**: Dynamic Routing rules evaluated at edge, not in a centralized gateway server. Minimal routing decision latency.

5. **Cloudflare Ecosystem Synergy**: Native integration with R2 (log storage), Workers (custom proxy logic), Zero Trust (access control), Secret Store (BYOK), DLP, and the broader platform.

6. **Zero Infrastructure Ops**: Fully managed. No servers to run, no ingress to configure, no scale-out planning.

7. **Argo Smart Routing** (if enabled): Optimized TCP paths from Cloudflare's network to AI providers, potentially reducing provider round-trip latency.

---

## Key Differences from OpenRouter / LiteLLM / Portkey

| Dimension | Cloudflare | OpenRouter | LiteLLM | Portkey |
|-----------|-----------|-----------|---------|---------|
| **Hosting** | CDN edge (SaaS) | SaaS centralized | OSS / self-hosted | SaaS centralized |
| **Provider count** | 24 + custom | 300+ models | 100+ providers | 250+ models |
| **Caching** | Edge (exact match) | None | Semantic + exact | Semantic + exact |
| **Dynamic routing** | Visual + JSON flows | None | Config-file-based | Limited |
| **DLP** | Yes (Firewall) | No | No | Limited |
| **Guardrails** | Yes (edge) | No | No | Yes (rules) |
| **WebSocket/Realtime** | Yes | No | Partial | No |
| **BYOK** | Yes (Secret Store) | No | No | Virtual keys |
| **Unified billing** | 5 providers | No (5% markup per req) | No | No |
| **OTEL export** | Yes | No | Yes | Yes |
| **Evaluation system** | Yes (basic, beta) | No | No | Yes (advanced) |
| **Model playground** | Yes | No | No | No |
| **Zero data retention** | Yes (OAI + Anthropic) | No | No | No |
| **Self-host option** | No | No | Yes | No |
| **Free tier** | Yes (generous) | Usage markup | Free OSS | $49/mo base |
| **Deployment overhead** | Zero | Zero | High (ops) | Zero |

**Cloudflare's moat:** Edge caching, Workers AI native colocation, DLP, ZDR, and seamless Cloudflare ecosystem integration.

**Cloudflare's gaps:** No semantic caching (yet), smaller provider catalog than OpenRouter, evaluation system immature vs. Portkey, SaaS-only (no on-prem).

---

## What thegent Should Steal

### High Priority

1. **`cf-aig-metadata` pattern** — Allow callers to attach structured metadata (user_id, session_id, env, team) to every proxied request. Store in request context, expose in logs and analytics. Max 5 key-value pairs per request is a reasonable initial constraint.

2. **`cf-aig-step` response header** — When thegent's CLIProxy handles fallbacks, return a header/field indicating which provider/model ultimately served the request. Critical for debugging and cost attribution.

3. **`cf-aig-event-id` on every response** — Return a unique trace ID on every proxied response, including failures. This is the anchor point for all downstream observability (logs, feedback, OTEL spans).

4. **Per-request retry/backoff headers** — `cf-aig-max-attempts`, `cf-aig-retry-delay`, `cf-aig-backoff` (constant/linear/exponential). Callers control retry behavior without changing routing config.

5. **Per-request custom cost override** — `cf-aig-custom-cost: {"per_token_in": float, "per_token_out": float}`. Essential for accurate cost tracking when using negotiated provider rates.

6. **`cf-aig-skip-cache` per-request** — Allow callers to bypass cache on a per-request basis, not just globally. Needed for non-deterministic, time-sensitive, or user-personalized requests.

7. **`cf-aig-collect-log` override** — Per-request ability to suppress or force logging. Needed for PII-sensitive requests or high-volume debug scenarios.

### Medium Priority

8. **Cache-Key per-user namespacing** — Allow callers to include a user/session identifier in the cache key, enabling per-user caching semantics without building a separate cache system.

9. **Fixed vs. Sliding window rate limiting** — Both techniques should be available. Sliding window prevents burst clustering at window boundaries, which is a real pathological case for AI API usage.

10. **`cf-aig-cache-status` response header** — Always return HIT/MISS so callers can observe cache behavior without dashboard access. Useful for testing and client-side cost optimization.

11. **Fallback chain with step tracking** — Universal endpoint pattern: JSON array of provider configs tried in order. `step` in response (or header) tells you which one succeeded. This is more expressive than thegent's current fallback model.

12. **Zero Data Retention flag** — `cf-aig-zdr` header that routes to a provider endpoint that doesn't retain data. Implement as a routing hint to ZDR-capable provider endpoints. Critical for enterprise/regulated customers.

13. **Customizable log storage policies** — Auto-delete oldest vs. stop-on-limit. Don't silently drop logs; make the policy explicit and configurable.

### Lower Priority / Aspirational

14. **Visual dynamic routing** — A JSON/YAML-defined routing flow with conditional nodes, percentage splits, and budget limits. The JSON config approach is achievable before building a visual UI. This is a superset of thegent's current cost-aware routing.

15. **OTEL trace export** — Export per-request spans to external OTEL backends. The `cf-aig-event-id` anchor makes this implementable as a post-processing export rather than in-path instrumentation.

16. **Model playground** — A CLI or TUI interface to test and compare models against each other with the same prompt. `thegent compare "prompt" --models gpt-4o,claude-3-5 --metrics cost,latency`.

17. **DLP scanning** — Regex/pattern-based PII scanning on prompts and responses before they are logged or forwarded. Even a basic implementation (SSN, credit card patterns) provides significant compliance value.

18. **Evaluation datasets** — Allow users to create named sets of logged requests, then run evaluators (cost, latency, accuracy) against them. Builds on existing log storage.

### What NOT to Copy

- **Cloudflare ecosystem lock-in**: Logpush to R2, Workers AI binding, Secret Store — these only make sense within the Cloudflare platform. thegent must remain provider-agnostic.
- **Only exact-match caching**: thegent should implement semantic caching (Cloudflare has yet to release this).
- **No self-host option**: thegent is designed to be runnable locally/on-prem. That is a differentiation to preserve.
- **Centralized Unified Billing**: This is a complex billing product, not a gateway feature. Not worth replicating.
