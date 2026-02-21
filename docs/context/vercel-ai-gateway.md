# Vercel AI Gateway

> Definitive reference for implementing Vercel AI Gateway support in the proxy (CLIProxy / thegent routing layer).
> Sources: vercel.com/docs/ai-gateway (fetched 2026-02-20).

---

## What it is

Vercel AI Gateway is a SaaS-only LLM routing proxy that provides a unified API for accessing
hundreds of AI models from 37+ providers through a single endpoint. Key properties:

- Hosted at `ai-gateway.vercel.sh` — no self-hosted option
- Zero markup on tokens (charges at provider list price)
- 37 providers: OpenAI, Anthropic, Google, xAI, Amazon Bedrock, Azure, Mistral, Groq, etc.
- Two native API surfaces: OpenAI-compatible (`/v1/`) and Anthropic-compatible (`/`)
- Deep Vercel AI SDK integration (`@ai-sdk/gateway`)
- Automatic provider failover, explicit provider ordering, cross-provider model fallbacks
- Per-provider prompt caching orchestration (no gateway-level semantic cache)
- Spend monitoring, credit-based billing, generation lookup API

---

## Base URL / Authentication

### OpenAI-compatible surface

```
Base URL:  https://ai-gateway.vercel.sh/v1
Auth:      Authorization: Bearer <AI_GATEWAY_API_KEY>
Env var:   AI_GATEWAY_API_KEY
```

### Anthropic-compatible surface

```
Base URL:  https://ai-gateway.vercel.sh
Auth:      x-api-key: <AI_GATEWAY_API_KEY>
           OR  Authorization: Bearer <AI_GATEWAY_API_KEY>
```

### OIDC authentication (Vercel-native projects only)

```
Authorization: Bearer <VERCEL_OIDC_TOKEN>   (expires every 12h)
```

API key takes precedence over OIDC token when both present.

### Configuring existing clients

```python
# OpenAI Python SDK
from openai import OpenAI
client = OpenAI(api_key=os.getenv('AI_GATEWAY_API_KEY'),
                base_url='https://ai-gateway.vercel.sh/v1')

# Anthropic Python SDK
import anthropic
client = anthropic.Anthropic(api_key=os.getenv('AI_GATEWAY_API_KEY'),
                              base_url='https://ai-gateway.vercel.sh')
```

**Claude Code CLI:**

```bash
ANTHROPIC_BASE_URL="https://ai-gateway.vercel.sh"
ANTHROPIC_AUTH_TOKEN="<AI_GATEWAY_API_KEY>"
ANTHROPIC_API_KEY=""     # Must be empty — Claude Code checks this first
```

---

## OpenAI Compatibility

Vercel AI Gateway is fully OpenAI-compatible on the `/v1/` path:

| Endpoint | Notes |
|----------|-------|
| `GET /v1/models` | No auth required; returns model list |
| `GET /v1/models/{model}` | Single model details |
| `GET /v1/models/{creator}/{model}/endpoints` | Per-model provider list with pricing |
| `POST /v1/chat/completions` | Chat completions (streaming + non-streaming) |
| `POST /v1/embeddings` | Vector embeddings |
| `GET /v1/credits` | Credit balance |
| `GET /v1/generation` | Per-generation cost and metadata lookup |

**Model ID format:** `{creator}/{model-name}` — e.g.:
```
openai/gpt-5.2
anthropic/claude-sonnet-4.5
google/gemini-3-flash
xai/grok-4
```

**No `/v1/responses` endpoint** — Vercel AI Gateway does not implement the OpenAI Responses API.

---

## Request Extensions

These fields extend the standard OpenAI chat completions request body:

### `providerOptions.gateway` (object) — routing and configuration

```json
{
  "providerOptions": {
    "gateway": {
      "order": ["bedrock", "anthropic"],
      "only": ["anthropic", "vertex"],
      "caching": "auto",
      "models": ["anthropic/claude-sonnet-4.5", "google/gemini-3-flash"],
      "byok": {
        "anthropic": [{ "apiKey": "sk-ant-..." }],
        "vertex": [
          { "project": "proj-1", "location": "us-east5",
            "googleCredentials": { "privateKey": "...", "clientEmail": "..." } }
        ],
        "bedrock": [{ "accessKeyId": "...", "secretAccessKey": "...", "region": "us-east-1" }]
      }
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `order` | string[] | Provider slugs to try in order (e.g. `["bedrock", "anthropic"]`) |
| `only` | string[] | Allowlist of providers; if none match, request fails |
| `caching` | `"auto"` | Auto-insert `cache_control` breakpoints for Anthropic (not Bedrock) |
| `models` | string[] | Model fallback list tried in order if primary fails |
| `byok` | object | Per-request provider credentials by provider slug |

When both `order` and `only` are set, the final order is the intersection: providers in
`order` that also appear in `only`, preserving `order` sequence.

### `models` (string[]) — top-level model fallback list (alternative to `providerOptions.gateway.models`)

```json
{
  "model": "openai/gpt-5.2",
  "models": ["anthropic/claude-sonnet-4.5", "google/gemini-3-flash"]
}
```

### `reasoning` (object) — cross-provider reasoning control

```json
{
  "reasoning": {
    "enabled": true,
    "max_tokens": 2000,
    "effort": "high",
    "exclude": false
  }
}
```

| Field | Values | Notes |
|-------|--------|-------|
| `enabled` | boolean | Enable reasoning output |
| `max_tokens` | integer | Reasoning token budget; mutually exclusive with `effort` |
| `effort` | `none`, `minimal`, `low`, `medium`, `high`, `xhigh` | Approx 0%, 10%, 20%, 50%, 80%, 95% of max |
| `exclude` | boolean | Suppress reasoning from response (still generates internally) |

### `providerOptions.anthropic` / `providerOptions.openai` — provider-specific options

Can be combined with `providerOptions.gateway`:

```json
{
  "providerOptions": {
    "anthropic": { "thinkingBudget": 0.001 },
    "openai": { "reasoningEffort": "high", "reasoningSummary": "detailed" },
    "gateway": { "order": ["vertex"] }
  }
}
```

### Attribution headers (optional)

```
http-referer: https://myapp.vercel.app
x-title: MyApp
```

Sets for app visibility on AI Gateway pages. No effect on routing.

---

## Response Extensions

### Standard non-streaming response additions

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "...",
      "reasoning": "Let me think...",
      "reasoning_details": [
        {
          "type": "reasoning.text",
          "text": "Let me think...",
          "signature": "anthropic-sig-xyz",
          "format": "anthropic-claude-v1",
          "index": 0
        }
      ]
    }
  }],
  "usage": {
    "completion_tokens_details": {
      "reasoning_tokens": 50
    }
  }
}
```

**Reasoning detail types:**
- `reasoning.text` — plain text reasoning (Anthropic); may include `signature` field
- `reasoning.encrypted` — encrypted/redacted reasoning payload (OpenAI); has `data` field
- `reasoning.summary` — condensed summary (OpenAI); has `summary` field

### AI SDK `providerMetadata` (gateway routing + cost)

When using `@ai-sdk/gateway` or the AI SDK, responses include:

```json
{
  "providerMetadata": {
    "gateway": {
      "routing": {
        "resolvedProvider": "anthropic",
        "fallbacksAvailable": ["bedrock", "vertex"],
        "attempts": [
          { "provider": "anthropic", "credentialType": "system",
            "success": true, "startTime": 458753.4, "endTime": 459891.7 }
        ]
      },
      "cost": "0.0045405",
      "marketCost": "0.0045405",
      "generationId": "gen_01K8KPJ0FZA7172X6CSGNZGDWY"
    }
  }
}
```

**`gateway.cost`** — Decimal string in USD, amount debited from AI Gateway Credits.
**`gateway.generationId`** — Use with `GET /v1/generation?id=` for detailed stats.

### Cost is NOT in the standard chat completion response body

To retrieve cost data, use:
```
GET https://ai-gateway.vercel.sh/v1/generation?id=gen_01ARZ3NDEKTSV4RRFFQ69G5FAV
Authorization: Bearer <AI_GATEWAY_API_KEY>
```

Returns: `total_cost`, `tokens_prompt`, `tokens_completion`, `native_tokens_cached`,
`native_tokens_reasoning`, `latency`, `generation_time`, `provider_name`, `is_byok`.

---

## Caching

Vercel AI Gateway has **no gateway-level semantic or exact-match response cache**.

It orchestrates **provider-side prompt token caching**:

| Provider | Behavior | Action needed |
|----------|----------|---------------|
| OpenAI, Google, DeepSeek | Implicit caching — automatic | None; provider caches automatically |
| Anthropic (direct, Vertex) | Requires explicit markers | Set `caching: 'auto'` in `providerOptions.gateway`, or add `cache_control: { type: "ephemeral" }` to messages |
| Amazon Bedrock | Not yet supported | Must disable auto-caching for Bedrock routes |

**Auto caching example:**

```json
{
  "providerOptions": { "gateway": { "caching": "auto" } }
}
```

When `caching: 'auto'` is set, the gateway inserts a `cache_control` breakpoint at the
end of static content before forwarding to Anthropic.

**Manual cache_control example:**

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Long system prompt...",
      "cache_control": { "type": "ephemeral" }
    }
  ]
}
```

Cache pricing tracked in model metadata (`input_cache_read`, `input_cache_write`) and in
generation lookup data (`native_tokens_cached`).

---

## Fallbacks / Load Balancing

### Provider-level routing

```json
{
  "providerOptions": {
    "gateway": {
      "order": ["bedrock", "anthropic"],
      "only": ["anthropic", "bedrock"]
    }
  }
}
```

- `order` — try providers in this sequence
- `only` — restrict to this set; request fails if none can serve
- No `sort` by price/throughput/latency (OpenRouter feature that is NOT present here)
- Default: automatic selection by Vercel's internal uptime/latency scoring

### Model-level fallbacks

```json
{
  "model": "openai/gpt-5.2",
  "models": ["anthropic/claude-sonnet-4.5", "google/gemini-3-flash"]
}
```

Failover sequence:
1. Try primary model via configured providers (respecting `order`)
2. On all-provider failure: try first model in `models` list
3. Continue through `models` list until success

The `model` field in the response always reflects the ACTUAL model used.

### BYOK failback

Dashboard-configured or per-request BYOK credentials are tried first. On BYOK credential
failure, the gateway automatically retries with Vercel system credentials (transparent
failback, no extra configuration).

### Load balancing

No explicit load-balancing policy exposed. Vercel auto-selects providers by internal
uptime/latency score. No `sort: "price"` / `sort: "throughput"` options exist (unlike OpenRouter).

---

## Rate Limiting

**No documented gateway-level rate limit configuration.** Rate limits are provider-enforced
and surfaced as `429 Too Many Requests`. No `X-RateLimit-*` headers documented.

Indirect budget controls:
- Credits balance depletes and requests stop when balance is zero
- Auto top-up prevents interruption

Error format on 429:
```json
{ "error": { "message": "...", "type": "...", "param": null, "code": "..." } }
```

No `Retry-After` header documented.

---

## Observability

### Dashboard (Vercel UI)

- **Requests by Model**: request volume per model over time
- **TTFT (Time to First Token)**: P-latency chart
- **Input/Output Token Counts**: token volume
- **Spend**: cost over time
- **Request logs**: per-request detail (model, provider, all token types, cost)
- **Grouped by**: project or API key
- **Scope**: team-wide or per-project

Extended log retention requires Observability Plus (paid add-on).

### Programmatic APIs

| Endpoint | Data |
|----------|------|
| `GET /v1/credits` | `{ "balance": "95.50", "total_used": "4.50" }` |
| `GET /v1/generation?id={id}` | Per-generation cost, tokens, latency, provider |
| `GET /billing/charges` | FOCUS v1.3 JSONL with 1-day granularity |

### No OTEL / External Export

No documented OpenTelemetry export, webhook delivery, or log streaming to external
observability platforms. All metrics are Vercel-dashboard-native.

---

## Key Differences from OpenRouter

| Dimension | Vercel AI Gateway | OpenRouter |
|-----------|-------------------|------------|
| **API surfaces** | OpenAI-compat + Anthropic-compat (two native surfaces) | OpenAI-compat only |
| **Anthropic endpoint** | `POST /v1/messages` native Anthropic format | Not supported |
| **Responses API** | Not documented | Beta (`/api/v1/responses`) |
| **Model routing** | `order`, `only` (Vercel picks default by score) | `order`, `only`, `ignore`, `allow_fallbacks`, `require_parameters` |
| **Load balancing** | Automatic (not configurable) | `sort: "price"/"throughput"/"latency"`, `max_price`, `preferred_min_throughput`, `preferred_max_latency`, percentile thresholds |
| **Routing constraints** | None (no data_collection, no ZDR, no quantization filter) | `data_collection`, `zdr`, `quantizations`, `require_parameters` |
| **Model ID suffixes** | None | `:nitro`, `:floor`, `:online`, `:free`, `:thinking`, `:extended`, `:exacto` |
| **Cost in response** | NOT in response body (use generation lookup or AI SDK providerMetadata) | NOT in response body (use `/api/v1/generation`) |
| **Streaming provider field** | NOT present in SSE chunks | `"provider": "OpenAI"` in every chunk |
| **Streaming keep-alive** | No comment lines | `": OPENROUTER PROCESSING"` comments |
| **Caching** | Provider-side prompt caching orchestration only | Provider-side prompt caching (pass-through only) |
| **Semantic cache** | No | No |
| **Plugins** | Web search tools (Perplexity, Parallel, native per provider) | `plugins: [{id: "web"/"file-parser"/"response-healing"}]` |
| **Context compression** | No | `transforms: ["middle-out"]` |
| **Reasoning normalization** | Deep: `reasoning`, `reasoning_details` with typed blocks and signatures | `reasoning.effort`, `reasoning.summary`; less structured |
| **BYOK** | Dashboard-level + per-request `providerOptions.gateway.byok`; no fee | Dashboard-level only; service fee (waived for first N requests/month) |
| **Pricing** | Zero markup; credit-based | Variable; zero markup on BYOK routes |
| **Self-hosting** | No | No |
| **Image/Video generation** | Yes (Flux, Recraft, Veo, Kling, Wan, Grok Imagine) | Limited |
| **Rate limit docs** | Not documented | Free tier: 60 req/min for `:free`; documented `X-RateLimit-*` in 429 metadata |
| **Framework integrations** | AI SDK (first-class), LangChain, LiteLLM, LlamaIndex, Mastra, Pydantic AI | LangChain, LiteLLM, many others |

---

## Key Differences from LiteLLM

| Dimension | Vercel AI Gateway | LiteLLM |
|-----------|-------------------|---------|
| **Deployment** | SaaS only | Self-hosted (also has hosted Cloud tier) |
| **OpenAI compat** | Yes | Yes |
| **Anthropic compat** | Yes (first-class) | Via proxy with translation |
| **Provider config** | Per-request `providerOptions.gateway` | Config file / environment variables |
| **Budget limits** | Credits balance + auto top-up | `max_budget`, `budget_duration`, `litellm_settings` |
| **Load balancing** | Automatic scoring | `routing_strategy`: `least-busy`, `usage-based`, `latency-based`, `cost-based` |
| **Rate limiting** | Not exposed | Per-user, per-team, per-key RPM/TPM limits |
| **Observability** | Vercel dashboard; no OTEL export | Prometheus, Langfuse, Helicone, Datadog, OTEL integration |
| **Fallbacks** | `models` array | `fallbacks` in config with model-specific fallback lists |
| **Caching** | Provider-side only | Semantic (Redis) + exact (Redis/in-memory) |
| **Pricing** | Zero markup, credit-based | Self-hosted: free; Cloud: pricing per seat |
| **Model management** | Dynamic model discovery via API | Static config file + model list |

---

## Proxy Considerations

What a proxy sitting between a client and Vercel AI Gateway must handle:

### Request Pass-Through (mandatory)

A proxy MUST pass through these Vercel-specific fields without dropping them:
- `providerOptions` object (entire `gateway`, `anthropic`, `openai`, etc. sub-objects)
- `models` array (model fallback list)
- `reasoning` object
- `cache_control` in message objects
- `file` content parts in messages

### Request Rewriting (may be required)

- `model`: Translate from internal catalog IDs (e.g. `claude-sonnet-4.5`) to Vercel format (e.g. `anthropic/claude-sonnet-4.5`)
- `Authorization`: Replace client key with `AI_GATEWAY_API_KEY`
- `http-referer` + `x-title`: Set to proxy identity if desired

### Response Pass-Through (mandatory)

- `model` field (actual model used — critical for fallback awareness)
- `choices[].message.reasoning` (cross-provider reasoning text)
- `choices[].message.reasoning_details` (structured reasoning blocks)
- `usage.completion_tokens_details.reasoning_tokens`
- `id` field (= generationId for generation lookup)
- `providerMetadata.gateway.cost` and `generationId` when using AI SDK

### Streaming Considerations

- No SSE comment lines to handle (Vercel doesn't send them)
- No `provider` field in streaming chunks (Vercel omits it)
- `delta.reasoning` and `delta.reasoning_details` must be forwarded (proxy must not drop these)
- `delta.tool_calls` must be forwarded (proxy must not drop tool call streaming)
- Final chunk contains `usage` stats (same as OpenAI spec)

### Cost / Usage Accounting

The chat completion response does NOT contain cost. To track spend:
1. Capture `id` from response body (= generationId)
2. After request completes: `GET /v1/generation?id={id}` — returns `total_cost`
3. AI SDK: cost is in `providerMetadata.gateway.cost`

### TLS

HTTPS required: `https://ai-gateway.vercel.sh`. Must use `verify=True` (not `verify=False`).

### Authentication

Vercel AI Gateway requires `Authorization: Bearer <AI_GATEWAY_API_KEY>`. The env var is
`AI_GATEWAY_API_KEY`. For BYOK pass-through, the `providerOptions.gateway.byok` object
carries per-provider credentials and must be forwarded as-is; the gateway applies them internally.

### Anthropic-Compatible Surface

To support tools like Claude Code connecting via the Anthropic SDK:
- Expose `POST /v1/messages` endpoint
- Accept `x-api-key` header in addition to `Authorization: Bearer`
- Forward to `https://ai-gateway.vercel.sh/v1/messages` (or translate to OpenAI format if not proxying directly)

### Provider Slug Reference

Used in `providerOptions.gateway.order` / `only`:
`anthropic`, `bedrock`, `vertex`, `openai`, `azure`, `google`, `groq`, `mistral`,
`fireworks`, `togetherai`, `deepinfra`, `deepseek`, `cohere`, `cerebras`, `xai`,
`perplexity`, `sambanova`, `novita`, `nebius`, `crusoe`, `arcee-ai`, `alibaba`,
`bytedance`, `moonshotai`, `morph`, `meituan`, `minimax`, `inception`, `bfl`,
`klingai`, `prodia`, `recraft`, `streamlake`, `baseten`, `parasail`, `voyage`, `zai`, `vercel`

---

## Quick Reference: All Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/v1/models` | Optional | List all models with pricing and capabilities |
| GET | `/v1/models/{model}` | Optional | Single model details |
| GET | `/v1/models/{creator}/{model}/endpoints` | Optional | Per-model provider list |
| POST | `/v1/chat/completions` | Required | Chat completions (OpenAI-compat) |
| POST | `/v1/embeddings` | Required | Vector embeddings |
| POST | `/v1/messages` | Required | Anthropic Messages API (Anthropic-compat) |
| GET | `/v1/credits` | Required | Credit balance |
| GET | `/v1/generation?id={id}` | Required | Per-generation cost + metadata |
| GET | `/billing/charges` | Required | Cost data (FOCUS v1.3 JSONL, 1-day granularity) |

---

## Sources

- https://vercel.com/docs/ai-gateway
- https://vercel.com/docs/ai-gateway/models-and-providers/provider-options
- https://vercel.com/docs/ai-gateway/models-and-providers/model-fallbacks
- https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-compat
- https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-compat/advanced
- https://vercel.com/docs/ai-gateway/sdks-and-apis/anthropic-compat
- https://vercel.com/docs/ai-gateway/authentication-and-byok/byok
- https://vercel.com/docs/ai-gateway/capabilities/observability
- https://vercel.com/docs/ai-gateway/capabilities/usage
- https://vercel.com/docs/ai-gateway/capabilities/web-search
- https://vercel.com/docs/ai-gateway/pricing
- https://vercel.com/docs/ai-gateway/ecosystem/app-attribution
