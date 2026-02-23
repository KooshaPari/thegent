# Portkey AI Gateway

> Definitive reference for evaluating Portkey as a provider-aggregate gateway.
> Sources: portkey.ai/docs, GitHub Portkey-AI/gateway, cross-product comparisons (fetched 2026-02-20).

---

## What it is / Deployment Options

Portkey is a production AI Gateway and LLMOps control plane that sits between your application and LLM providers. It provides routing, reliability, security, observability, and governance as a transparent proxy.

**Coverage:** 1,600+ models across 45+ providers (OpenAI, Anthropic, Google, Bedrock, Azure, Groq, Mistral, Cohere, Ollama, etc.)

**Three deployment tiers:**

| Mode | Description | Managed by |
|------|-------------|-----------|
| **OSS Gateway (self-hosted)** | Node.js/edge proxy; routing + fallbacks + LB + basic guardrails; no SaaS features | You |
| **Portkey-Managed SaaS** | Full platform on Portkey infra, isolated cluster per org | Portkey |
| **Hybrid (Enterprise)** | Gateway + data plane in your VPC; control plane by Portkey | Split |
| **Fully Airgapped (Enterprise)** | All components inside your network; zero external data | You |

**OSS install:**
```bash
docker pull portkeyai/gateway
docker run -p 8787:8787 portkeyai/gateway
# or: npx @portkey-ai/gateway
```

**Managed SaaS base URL:** `https://api.portkey.ai/v1`

---

## Authentication (x-portkey-* Headers)

### Core Headers

| Header | Purpose |
|--------|---------|
| `x-portkey-api-key` | Portkey account key — required for managed SaaS |
| `x-portkey-provider` | Direct provider name (`openai`, `anthropic`, etc.) |
| `x-portkey-virtual-key` | Virtual key slug (legacy; now `@provider-slug` in Model Catalog) |
| `x-portkey-config` | Config ID or inline JSON config object |

### Observability Headers

| Header | Purpose |
|--------|---------|
| `x-portkey-trace-id` | Custom trace ID |
| `x-portkey-span-id` | Span ID for distributed tracing |
| `x-portkey-parent-span-id` | Parent span for nested traces |
| `x-portkey-span-name` | Human-readable span label |
| `x-portkey-metadata` | JSON key-value pairs attached to every log entry |

### Cache Headers

| Header | Purpose |
|--------|---------|
| `x-portkey-cache-namespace` | Custom partition key (per-user caching) |
| `x-portkey-cache-force-refresh` | Bypass cache for this request |
| `x-portkey-debug` | Must be `true` for caching to work |

### OpenAI SDK Drop-In

```python
from openai import OpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

client = OpenAI(
    api_key="OPENAI_API_KEY",
    base_url=PORTKEY_GATEWAY_URL,
    default_headers=createHeaders(
        api_key="PORTKEY_API_KEY",
        provider="openai"
    )
)
```

W3C `traceparent`/`baggage` OTel headers are also accepted; `x-portkey-*` headers take precedence.

---

## Config-Based Routing

The **Config Object** is the central abstraction. It is JSON and can be:
1. Saved in Portkey UI → referenced by ID in `x-portkey-config: config_id`
2. Passed inline as JSON in `x-portkey-config: {"strategy":...}`
3. Set as default on a Virtual Key / AI Provider

### Config Schema

```json
{
  "strategy": {
    "mode": "single" | "fallback" | "loadbalance" | "conditional",
    "on_status_codes": [429, 500, 503],
    "conditions": [...],
    "default": "target_name"
  },
  "targets": [
    {
      "name": "target_name",
      "provider": "@provider-slug",
      "weight": 0.7,
      "override_params": { "model": "gpt-4o", "temperature": 0.7 },
      "cache": { "mode": "semantic", "max_age": 3600 },
      "retry": { "attempts": 3, "on_status_codes": [429] },
      "request_timeout": 30000,
      "input_guardrails": ["guardrail_id"],
      "output_guardrails": ["guardrail_id"],
      "forward_headers": ["x-custom-header"]
    }
  ],
  "cache": { "mode": "simple", "max_age": 604800 },
  "retry": { "attempts": 3, "use_retry_after_headers": true },
  "request_timeout": 60000,
  "cb_config": {
    "failure_threshold": 5,
    "cooldown_interval": 60000,
    "failure_status_codes": [500, 503]
  }
}
```

Targets are **recursive** — each target can itself be a full config, enabling nested strategies.

---

## Fallbacks + Load Balancing

### Fallback (Sequential Failover)

```json
{
  "strategy": {
    "mode": "fallback",
    "on_status_codes": [429, 500, 503]
  },
  "targets": [
    { "provider": "@openai-primary" },
    { "provider": "@anthropic-backup", "override_params": { "model": "claude-3-5-sonnet" } },
    { "provider": "@azure-tertiary" }
  ]
}
```

### Load Balancing (Weighted Distribution)

```json
{
  "strategy": { "mode": "loadbalance" },
  "targets": [
    { "provider": "@openai-prod", "weight": 0.7 },
    { "provider": "@openai-backup", "weight": 0.2 },
    { "provider": "@azure-openai", "weight": 0.1 }
  ]
}
```

### Nested: Load Balance with Embedded Fallback

```json
{
  "strategy": { "mode": "loadbalance" },
  "targets": [
    { "provider": "@anthropic", "weight": 0.5 },
    {
      "strategy": { "mode": "fallback" },
      "targets": [
        { "provider": "@openai", "override_params": { "model": "gpt-4o" } },
        { "provider": "@azure-openai", "override_params": { "model": "gpt-4o" } }
      ],
      "weight": 0.5
    }
  ]
}
```

### Conditional Routing (Metadata/Params-Based)

```json
{
  "strategy": {
    "mode": "conditional",
    "conditions": [
      {
        "query": { "metadata.user_plan": { "$eq": "enterprise" } },
        "then": "premium-target"
      },
      {
        "query": {
          "$and": [
            { "metadata.user_type": { "$eq": "pro" } },
            { "params.temperature": { "$gte": 0.7 } }
          ]
        },
        "then": "creative-target"
      }
    ],
    "default": "standard-target"
  },
  "targets": [
    { "name": "premium-target", "provider": "@anthropic", "override_params": { "model": "claude-3-5-opus" } },
    { "name": "creative-target", "provider": "@openai", "override_params": { "model": "gpt-4o" } },
    { "name": "standard-target", "provider": "@openai", "override_params": { "model": "gpt-4o-mini" } }
  ]
}
```

**Condition operators:** `$eq`, `$ne`, `$in`, `$nin`, `$regex`, `$gt`, `$gte`, `$lt`, `$lte`, `$and`, `$or`

**Query paths:** `metadata.<key>`, `params.<key>` (model/temperature/etc.), `url.pathname`

### Retry

```json
{
  "retry": {
    "attempts": 5,
    "on_status_codes": [429, 500],
    "use_retry_after_headers": true
  }
}
```

Exponential backoff applied automatically. Max 5 attempts.

### Circuit Breaker

```json
{
  "cb_config": {
    "failure_threshold": 5,
    "failure_threshold_percentage": 50,
    "cooldown_interval": 60000,
    "failure_status_codes": [500, 503],
    "minimum_requests": 10
  }
}
```

Minimum cooldown: 30 seconds. When open, all requests to that target are blocked until cooldown passes.

---

## Caching

Two modes:

| Mode | Matching | Plans | Notes |
|------|---------|-------|-------|
| `simple` | Exact content match | All | Works for all models incl. image gen |
| `semantic` | Cosine similarity on embeddings | Pro/Enterprise | ≤8,191 tokens, ≤4 messages |

```json
{ "cache": { "mode": "semantic", "max_age": 3600 } }
```

**TTL bounds:** 60s min, 90 days max (7,776,000s), default 7 days. Free plan: 1-day cap.

**Per-user cache namespace:**

```python
portkey.chat.completions.create(..., cache_namespace="user-123")
```
```bash
curl ... -H "x-portkey-cache-namespace: user-123"
```

Cache is partitioned solely by this string — all other headers ignored.

**Force refresh per-request:**
```bash
curl ... -H "x-portkey-cache-force-refresh: true"
```

**Per-target override:** Target-level cache config takes precedence over top-level.

---

## Guardrails

Run before (input hook) and/or after (output hook) each LLM call.

### Native Guardrails (All Plans)

| Check | Hook |
|-------|------|
| Regex Match | input/output |
| Word/Sentence/Character Count | input/output |
| JSON Schema validation | output |
| JSON Keys presence | output |
| Contains (word list) | output |
| Valid URLs | output |
| Contains Code (SQL, Python, etc.) | output |
| Ends With | input/output |
| Model Whitelist | input |
| JWT Token Validator | input |
| Webhook (Bring Your Own) | input/output |

### LLM-Based Guardrails (Pro/Enterprise)

| Check | Hook |
|-------|------|
| Moderate Content | input |
| Check Language | input |
| Detect PII | input/output |
| Detect Gibberish | input/output |

### Partner Guardrail Integrations (13)

Aporia, Patronus AI, Pillar, Pangea, Palo Alto Prisma AIRS, AWS Bedrock Guardrails, Azure Content Safety, Acuvity, Javelin, Lasso Security, Mistral Moderation, Prompt Security, Qualifire.

### Bring Your Own Guardrails (Webhook)

```json
{
  "type": "webhook",
  "webhookURL": "https://your-service.com/check",
  "headers": { "Authorization": "Bearer token" }
}
```

Portkey POSTs data to your URL. Return:
```json
{ "verdict": true, "data": { "transformedData": "..." } }
```
Timeout: 3s hardcoded. Timeout = PASS (non-blocking).

### Guardrail in Config Target

```json
{
  "provider": "@openai-prod",
  "input_guardrails": ["pg-pii-detector-abc123"],
  "output_guardrails": ["pg-fact-checker-xyz789"]
}
```

---

## Observability

### What Every Log Captures

- Timestamp, user, application ID
- Full prompt + response content
- Provider, model, routing decision taken
- Latency (TTFT + total), token counts, cost
- Cache outcome (Hit / Miss / Semantic Hit / Refreshed / Disabled)
- Guardrail violations
- Retry attempts and fallback activations
- Custom metadata and tags

**Log retention:** Dev: 3 days | Pro: 30 days | Enterprise: custom.

### Tracing

Hierarchical spans for multi-step agent workflows. Each span: inputs, outputs, model, latency, token usage.

Trace headers:
```
x-portkey-trace-id: my-trace-001
x-portkey-span-id: span-001
x-portkey-parent-span-id: parent-span-001
x-portkey-span-name: "call-llm-for-summarization"
```

### OpenTelemetry

Portkey exposes an OTLP HTTP endpoint:
```
POST https://api.portkey.ai/v1/otel
x-portkey-api-key: YOUR_KEY
```

W3C `traceparent`/`baggage` accepted. Existing OTel instrumentation sends directly to Portkey; trace/span IDs auto-correlated with LLM logs.

### Metrics (40+)

Request count, error rate, latency (p50/p95/p99), cost per request/token, cache hit rate, guardrail violation rate, fallback rate, token usage by model/provider/workspace.

### Feedback API

```python
portkey.feedback.create(
    trace_id="xxx",
    value=1,     # 1 = thumbs up, -1 = thumbs down
    weight=1
)
```

### Custom Metadata

```python
portkey.chat.completions.create(
    ...,
    metadata={"user_id": "123", "environment": "prod", "feature": "search"}
)
```

---

## Virtual Keys + Budget Management

### Model Catalog (Current System, replaces Virtual Keys)

- Provider credentials stored AES-256 encrypted in Portkey vault
- Never exposed in code — reference by slug: `@my-openai-prod`
- Org-level credential creation, provisioned to workspaces
- `@provider_slug/model_name` syntax: `@openai-prod/gpt-4o`

### Budget and Rate Limits (Enterprise)

- USD budget cap per key — auto-expires when limit reached
- Per-workspace and per-team spend caps
- Rate limits: requests per minute/hour/day
- Granular budget tracking by workspace, team, user

### Access Control

- RBAC: Owner, Admin, Member, Viewer roles per workspace
- Key scoping: org-level API keys with specific permission scopes
- Model allowlists: restrict which models each workspace can use

---

## Prompt Library

- Centralized storage (3 templates free, unlimited Pro+)
- Version control: every edit = new version
- Labels: `staging`, `production`, `platform-team`, etc.
- Publish makes a version "production" (default for callers)
- A/B testing via label-based traffic split
- Template variables: `{{variable_name}}` syntax
- Prompt partials: reusable fragments
- Comparison view: side-by-side version diff
- Multimodal playground (text, vision, audio)

**Prompt API call:**
```python
portkey.prompts.completions.create(
    prompt_id="pp-my-prompt-abc",
    variables={"user_name": "Alice", "topic": "ML"}
)
```

---

## Unique Features

1. **Recursive nested strategy configs** — load balance inside fallback inside conditional routing, arbitrarily deep
2. **Model Catalog / `@provider/model` syntax** — unified, governed model references across the org
3. **Semantic caching** — vector-similarity matching; reuses responses to semantically equivalent queries
4. **50+ built-in guardrails** with 13 partner integrations in a unified framework
5. **MCP Gateway** — act as MCP client; govern, auth, and observe all tool calls from agents
6. **Feedback API** — link user thumbs-up/down signals to specific LLM traces
7. **Circuit breaker** — `cb_config` with failure thresholds and configurable cooldown
8. **Cache namespace** — per-user/per-session cache partitioning without custom logic
9. **JWT Validator guardrail** — JWKS-based token validation at gateway level
10. **OTLP endpoint** — ingest external OTel spans; correlate infra traces with LLM calls
11. **`use_retry_after_headers`** — automatically honor provider Retry-After headers
12. **Airgapped enterprise deployment** — zero data leaves your network
13. **Prompt versioning + A/B testing** — full prompt lifecycle management

---

## Key Differences from OpenRouter / LiteLLM / Vercel

| Dimension | Portkey | OpenRouter | LiteLLM | Vercel AI Gateway |
|-----------|---------|-----------|---------|------------------|
| Deployment | SaaS + OSS + airgapped | SaaS only | OSS only | SaaS only |
| Pricing model | Flat monthly | 5% spend markup | Free (self-hosted) | Usage-based |
| Guardrails | 50+ native + 13 partners | None | Basic | None |
| Semantic cache | Yes | No | No | No |
| Prompt management | Full versioning/A/B | None | None | None |
| Conditional routing | Metadata + params | Model-based only | Limited | No |
| Circuit breaker | Yes | No | Limited | No |
| RBAC + SSO | Yes (Enterprise) | No | No | No |
| OTel ingestion | Yes (OTLP endpoint) | No | Via callbacks | No |
| MCP Gateway | Yes | No | No | No |
| Feedback API | Yes | No | No | No |
| Airgapped | Yes (Enterprise) | No | Yes | No |
| Per-user cache namespace | Yes | No | No | No |
| Budget limits per key | Yes | No | No | No |
| Nested strategy configs | Yes (recursive) | No | No | No |

---

## What thegent Should Steal

**Immediately actionable (copy the pattern):**

1. **Config Object schema** — adopt `strategy` + `targets` + `cache` + `retry` + `cb_config` JSON format as thegent's `RouteConfig`; make targets recursive so strategies compose
2. **Conditional routing operators** — `$eq/$ne/$in/$nin/$regex/$gt/$gte/$lt/$lte/$and/$or` on metadata and request params
3. **Circuit breaker pattern** — `failure_threshold`, `cooldown_interval`, `failure_status_codes` fields; state tracked per-target at router level
4. **`use_retry_after_headers`** — check for provider `Retry-After` header before scheduling retry
5. **Cache namespace header** — `x-thegent-cache-namespace: user-123` for per-user cache partitioning
6. **Cache TTL in config** — `max_age` field in cache config (seconds); min/max/org-level caps
7. **`cache_force_refresh` header** — per-request cache bypass without changing config
8. **Webhook guardrail interface** — `verdict` + optional `transformedData` pattern; 3s timeout = PASS
9. **`input_guardrails`/`output_guardrails` in target config** — attach guardrail IDs per target, not just globally
10. **Span header set** — `x-thegent-trace-id`, `x-thegent-span-id`, `x-thegent-parent-span-id`, `x-thegent-span-name`

**Medium-term (architectural investment):**

11. **OTLP endpoint** — `POST /v1/otel` to ingest external OTel traces and correlate with LLM call logs
12. **Feedback API** — `POST /v1/feedback` with `trace_id` + `value` to attach evaluation signals to logs
13. **Model Catalog / `@provider/model` syntax** — unified provider slug system for governed model references
14. **Budget limits per key** — USD cap on virtual keys with auto-expiry enforcement
15. **Per-target `override_params`** — allow per-target model/hyperparameter override in route config

**Skip (out of scope for CLIProxy):**

- Prompt Studio GUI — CLI-first; use YAML/JSON config files
- SCIM provisioning — separate concern
- 13-partner guardrail marketplace — implement the webhook interface; let partners be plugins
- FinOps GUI dashboards — expose raw metrics; let consumers build visualizations
