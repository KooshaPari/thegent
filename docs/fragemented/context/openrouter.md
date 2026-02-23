# OpenRouter API Context

> Definitive reference for implementing OpenRouter support in the proxy (CLIProxyAPIPlus / thegent routing layer).
> Sources: openrouter.ai/docs (fetched 2026-02-20).

---

## What is OpenRouter

OpenRouter is a unified API gateway that provides access to hundreds of AI models from OpenAI,
Anthropic, Google, Meta, Mistral, DeepSeek, and many others through a single OpenAI-compatible
endpoint. It handles provider selection, failover, load balancing, cost optimization, and
aggregates usage metrics across providers.

Key capabilities:
- Single endpoint for 400+ models
- Automatic provider failover and load balancing
- Cost/throughput/latency-aware routing
- Plugins: real-time web search, PDF parsing, response healing
- Prompt transforms (middle-out context compression)
- Zero Data Retention (ZDR) routing options
- BYOK (Bring Your Own Key) for supported providers
- Generation stats and cost tracking via `/api/v1/generation`

---

## Base URL

```
https://openrouter.ai/api/v1
```

All endpoints are relative to this base.

---

## Authentication

### Required Header

```
Authorization: Bearer <OPENROUTER_API_KEY>
```

API keys are created at `https://openrouter.ai/keys`.

### Optional Attribution Headers

These are not required for API calls but affect app visibility on openrouter.ai leaderboards:

```
HTTP-Referer: https://your-app-url.com
X-Title: Your App Name
```

### Special-Purpose Request Headers

```
structured-outputs-2025-11-13: true
```
Required when using strict tool calls (`tools[].strict: true`). Without this header,
OpenRouter strips the `strict` field and routes normally.

### Auth Key Introspection

```
GET https://openrouter.ai/api/v1/key
Authorization: Bearer <API_KEY>
```

Response fields:

| Field | Type | Description |
|-------|------|-------------|
| `limit` | number\|null | Credit limit; null = unlimited |
| `limit_remaining` | number | Available credits |
| `limit_reset` | string | Reset interval type |
| `usage` | number | All-time credit consumption (USD) |
| `usage_daily` | number | Daily usage |
| `usage_weekly` | number | Weekly usage |
| `usage_monthly` | number | Monthly usage |
| `byok_usage` | object | BYOK usage metrics (same time periods) |
| `is_free_tier` | boolean | Whether account has no purchase history |

---

## Key Differences from Standard OpenAI API

| Area | OpenAI | OpenRouter |
|------|--------|------------|
| Model IDs | `gpt-4o`, `gpt-4o-mini` | `openai/gpt-4o`, `openai/gpt-4o-mini` |
| Extra request fields | None | `provider`, `route`, `models`, `transforms`, `plugins`, `reasoning`, `session_id`, `trace`, `metadata`, `debug` |
| Extra sampling params | None | `top_k`, `repetition_penalty`, `min_p`, `top_a` |
| `finish_reason` | Provider-native | Normalized to `stop\|tool_calls\|length\|content_filter\|error` |
| `native_finish_reason` | Not present | Raw provider finish reason |
| Usage in response | No cost | `/api/v1/generation` endpoint for cost; native token counts in response |
| Streaming SSE comments | None | `": OPENROUTER PROCESSING"` keep-alive comments (safe to ignore) |
| Provider in response | Not present | `model` field reflects actual model used (important with fallbacks) |
| Model routing | Not present | `provider` object, `models` array, model variant suffixes |
| Non-standard params | Rejected | Silently ignored if unsupported by target model |

---

## Model ID Format

OpenRouter model IDs use the format:

```
{provider}/{model-name}[:{variant}]
```

Examples:
- `openai/gpt-4o`
- `anthropic/claude-sonnet-4-5`
- `meta-llama/llama-3.3-70b-instruct`
- `google/gemini-2.0-flash-001`
- `deepseek/deepseek-chat`

### Model Variant Suffixes

Suffixes modify routing behavior. Two categories: **dynamic** (work on any model) and
**static** (only on models that declare support).

| Suffix | Category | Behavior | Equivalent to |
|--------|----------|----------|---------------|
| `:nitro` | Dynamic | Route to highest-throughput provider | `provider.sort: "throughput"` |
| `:floor` | Dynamic | Route to lowest-cost provider | `provider.sort: "price"` |
| `:online` | Dynamic | Enable real-time web search via Exa.ai | `plugins: [{id: "web"}]` |
| `:free` | Static | Use free tier of this model (low rate limits) | n/a — only on models with free variants |
| `:extended` | Static | Extended context window variant | n/a — model-specific |
| `:thinking` | Static | Extended reasoning / thinking tokens | n/a — model-specific |
| `:exacto` | Static | Curated routing for tool-calling accuracy | n/a — model-specific |

Examples:
- `anthropic/claude-3.5-sonnet:nitro` — fastest provider for this model
- `openai/gpt-4o:floor` — cheapest provider
- `openai/gpt-4o:online` — with real-time web search
- `meta-llama/llama-3-8b-instruct:free` — free tier variant
- `anthropic/claude-3-7-sonnet:thinking` — reasoning tokens enabled

### Permaslugs vs Canonical Slugs

- **canonical_slug**: URL-friendly identifier returned in the models API
- **permaslug** (model_id in endpoints API): Immutable ID for a specific model version
- The models API `id` field is the string used in requests

---

## Endpoints

### POST /api/v1/chat/completions

Primary completions endpoint. OpenAI-compatible with OpenRouter-specific extensions.

#### Request Schema

```typescript
{
  // --- Required ---
  messages: Message[];           // Conversation history

  // --- Core (one of model or models required) ---
  model?: string;                // Primary model ID (e.g. "openai/gpt-4o")
  models?: string[];             // Fallback model list in priority order

  // --- Standard OpenAI Sampling Parameters ---
  temperature?: number;          // Default 1.0, range 0.0–2.0
  top_p?: number;                // Default 1.0, range 0.0–1.0
  max_tokens?: number;           // Max output tokens
  max_completion_tokens?: number;// Alias for max_tokens
  stop?: string | string[];      // Stop sequences
  seed?: integer;                // Reproducibility seed
  frequency_penalty?: number;    // Range -2.0–2.0
  presence_penalty?: number;     // Range -2.0–2.0
  logit_bias?: Record<string, number>; // Token ID → bias (-100 to 100)
  logprobs?: boolean;
  top_logprobs?: number;         // 0–20
  stream?: boolean;              // Default false; enables SSE
  stream_options?: {
    include_usage: boolean;      // Include usage in stream final chunk
  };
  response_format?: ResponseFormat;
  structured_outputs?: boolean;
  tools?: Tool[];
  tool_choice?: "none" | "auto" | "required" | NamedToolChoice;
  parallel_tool_calls?: boolean; // Default true
  modalities?: ("text" | "image")[];

  // --- OpenRouter-Extended Sampling Parameters ---
  top_k?: integer;               // 0 = disabled; restricts to top N tokens
  repetition_penalty?: number;   // Default 1.0, range 0.0–2.0
  min_p?: number;                // Min probability relative to best token, 0.0–1.0
  top_a?: number;                // Dynamic top-p, 0.0–1.0

  // --- OpenRouter Routing ---
  provider?: ProviderPreferences; // Provider routing configuration (see below)
  route?: "fallback";            // Legacy; use models[] for fallbacks
  transforms?: string[];         // Currently: ["middle-out"] for prompt compression

  // --- OpenRouter Plugins ---
  plugins?: Plugin[];            // Enable per-request plugins

  // --- OpenRouter Reasoning ---
  reasoning?: {
    effort?: "xhigh" | "high" | "medium" | "low" | "minimal" | "none";
    summary?: "auto" | "concise" | "detailed";
  };

  // --- Observability ---
  user?: string;                 // End-user identifier (passed to providers)
  session_id?: string;           // Max 128 chars; groups related requests
  trace?: {
    trace_id?: string;
    trace_name?: string;
    span_name?: string;
    generation_name?: string;
    parent_span_id?: string;
  };
  metadata?: Record<string, unknown>; // Custom key-value; known keys: trace_id,
                                      // trace_name, span_name, generation_name,
                                      // parent_span_id (get special handling)

  // --- Debug (development only, do not use in production) ---
  debug?: {
    echo_upstream_body: boolean; // Returns upstream request body as first SSE chunk
  };
}
```

#### Message Types

```typescript
type Message =
  | { role: "system";    content: string | ContentPart[]; name?: string }
  | { role: "user";      content: string | ContentPart[]; name?: string }
  | { role: "developer"; content: string | ContentPart[]; name?: string }
  | { role: "assistant"; content?: string | ContentPart[]; tool_calls?: ToolCall[];
      refusal?: string; name?: string }
  | { role: "tool";      content: string | ContentPart[]; tool_call_id: string }
```

Content parts support: `text`, `image_url`, `input_audio`, `input_video`, `video_url`.
Each part may include `cache_control` for prompt caching.

#### ResponseFormat Options

```typescript
type ResponseFormat =
  | { type: "text" }
  | { type: "json_object" }
  | { type: "json_schema"; json_schema: { name: string; description?: string;
      schema: object; strict?: boolean } }
  | { type: "grammar"; grammar: string }    // GBNF grammar string
  | { type: "python" }
```

#### ProviderPreferences Object

```typescript
type ProviderPreferences = {
  order?: string[];              // Provider slugs to try in order
  only?: string[];               // Whitelist: only use these providers
  ignore?: string[];             // Blacklist: skip these providers
  allow_fallbacks?: boolean;     // Default true; if false, only uses order[0]
  require_parameters?: boolean;  // Only route to providers supporting all params
  data_collection?: "allow" | "deny"; // "deny" = no non-transient data collection
  zdr?: boolean;                 // true = Zero Data Retention endpoints only
  enforce_distillable_text?: boolean; // Restrict to models allowing text distillation
  quantizations?: Quantization[]; // Filter by quantization level
  sort?: "price" | "throughput" | "latency" | SortObject;
  max_price?: {                  // Hard limits; request fails if unavailable
    prompt?: number;             // Max $/1M tokens for prompt
    completion?: number;         // Max $/1M tokens for completion
    image?: number;
    request?: number;
  };
  preferred_min_throughput?: number | PercentileObject; // Soft threshold (deprioritizes)
  preferred_max_latency?: number | PercentileObject;    // Soft threshold (deprioritizes)
};

type Quantization = "int4" | "int8" | "fp4" | "fp6" | "fp8" | "fp16" | "bf16" | "fp32" | "unknown";

type SortObject = {
  by: "price" | "throughput" | "latency";
  partition?: "model" | "none";  // "none" = sort globally across fallback models
};

// Percentile-based performance thresholds
type PercentileObject = {
  p50?: number;
  p75?: number;
  p90?: number;
  p99?: number;
};
```

**Important**: `max_price` is a HARD limit — request fails if no provider meets it.
`preferred_min_throughput` and `preferred_max_latency` are SOFT — providers failing
thresholds are deprioritized, not excluded.

**Default load balancing**: OpenRouter excludes providers with outages in the last 30 seconds,
then selects from lowest-cost candidates weighted by inverse square of price.

#### Plugin Object

```typescript
type Plugin =
  | { id: "web"; max_results?: number; enabled?: boolean }     // Web search (Exa.ai)
  | { id: "file-parser"; enabled?: boolean }                   // PDF/file parsing
  | { id: "response-healing"; enabled?: boolean }              // Auto-fix malformed JSON
```

Default: 5 web results. Pricing: $4 per 1,000 web results. `enabled: false` disables a
default plugin for the current request.

#### Transforms

```typescript
transforms?: ["middle-out"]
```

`middle-out`: Compresses prompts exceeding the model's context window by removing messages
from the middle of the conversation. Default for models with context ≤ 8k tokens.

---

#### Response Schema

```typescript
{
  id: string;                    // Completion ID; also the generation ID for /api/v1/generation
  object: "chat.completion";
  created: number;               // Unix timestamp
  model: string;                 // ACTUAL model used (may differ from request if fallback)
  system_fingerprint?: string | null;
  choices: Array<{
    index: number;
    message: {
      role: "assistant";
      content: string | ContentPart[] | null;
      tool_calls?: ToolCall[];
      refusal?: string | null;
      reasoning?: string | null;             // Reasoning text from thinking models
      reasoning_details?: ReasoningDetail[];
      images?: Array<{ image_url: { url: string } }>;
    };
    finish_reason: "stop" | "tool_calls" | "length" | "content_filter" | "error" | null;
    native_finish_reason?: string | null;    // Raw provider finish reason
    logprobs?: LogprobsObject | null;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    prompt_tokens_details?: {
      cached_tokens?: number;
      cache_write_tokens?: number;
      audio_tokens?: number;
      video_tokens?: number;
    };
    completion_tokens_details?: {
      reasoning_tokens?: number | null;
      audio_tokens?: number | null;
      accepted_prediction_tokens?: number | null;
      rejected_prediction_tokens?: number | null;
    };
  };
}
```

**Note**: The `model` field in the response reflects the model that ACTUALLY processed the
request. When using `models[]` fallbacks, this will be the model that succeeded, not the
primary requested model.

**Note**: `usage.total_cost` is NOT in the chat completion response. Use
`GET /api/v1/generation?id=<id>` to retrieve cost data.

---

### GET /api/v1/models

Lists all available models.

```
GET https://openrouter.ai/api/v1/models
Authorization: Bearer <API_KEY>
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by use case: `programming`, `roleplay`, `marketing`, `marketing/seo`, `technology`, `science`, `translation`, `legal`, `finance`, `health`, `trivia`, `academia` |
| `supported_parameters` | string | Filter by supported parameter names |

#### Response

```typescript
{
  data: Array<{
    id: string;                  // Model ID for use in requests
    name: string;                // Display name
    canonical_slug: string;      // URL-friendly identifier
    created: number;             // Unix timestamp
    description: string;
    context_length: number | null;
    pricing: {
      prompt: string;            // Price per token (as string, in USD/token)
      completion: string;
      request: string;
      image: string;
      audio: string;
    };
    architecture: {
      tokenizer: string;
      instruct_type: string | null;
      modality: string;          // e.g. "text->text", "text+image->text"
    };
    supported_parameters: string[];
    default_parameters?: {
      temperature?: number;
      top_p?: number;
      frequency_penalty?: number;
    };
    per_request_limits?: {
      prompt_tokens?: number;
      completion_tokens?: number;
    };
    expiration_date?: string | null; // ISO 8601 or null
  }>;
}
```

---

### GET /api/v1/models/{author}/{slug}/endpoints

Returns all provider endpoints for a specific model with real-time performance metrics.

```
GET https://openrouter.ai/api/v1/models/{author}/{slug}/endpoints
Authorization: Bearer <API_KEY>
```

**Example**: `/api/v1/models/openai/gpt-4o/endpoints`

#### Response

```typescript
{
  data: {
    id: string;
    name: string;
    created: number;
    description: string;
    architecture: object;
    endpoints: Array<{
      name: string;
      model_id: string;          // Permaslug (immutable version-specific ID)
      model_name: string;
      provider_name: string;     // Provider slug (use in provider.order/only/ignore)
      tag: string | null;
      context_length: number;
      max_completion_tokens: number | null;
      max_prompt_tokens: number | null;
      pricing: {
        prompt: string;
        completion: string;
        request: string;
        image: string;
        audio: string;
        discount: number;
      };
      uptime_last_30m: number;   // 0.0–1.0 percentage
      latency_last_30m: {        // Milliseconds
        p50: number;
        p75: number;
        p90: number;
        p99: number;
      };
      throughput_last_30m: {     // Tokens per second
        p50: number;
        p75: number;
        p90: number;
        p99: number;
      };
      supported_parameters: string[];
      supports_implicit_caching: boolean;
      quantization: string | null;
    }>;
  };
}
```

Errors: `404` if model does not exist.

---

### GET /api/v1/generation

Retrieves request metadata, token counts, and cost for a completed generation.

```
GET https://openrouter.ai/api/v1/generation?id=<GENERATION_ID>
Authorization: Bearer <API_KEY>
```

The `GENERATION_ID` is the `id` field from the chat completion response, and also returned
in the `openrouter-generation-id` response header.

#### Response

```typescript
{
  data: {
    id: string;
    upstream_id: string | null;      // Provider's own request ID
    model: string;                   // Actual model used
    created_at: string;              // ISO 8601 timestamp
    origin: string;                  // Request origin URL

    // Cost fields (all in USD)
    total_cost: number;              // Total cost charged to your account
    cache_discount: number | null;   // Discount from prompt caching
    upstream_inference_cost: number | null; // What the provider charged
    usage: number;                   // Usage amount in USD

    // Standard token counts (OpenRouter-computed)
    tokens_prompt: number;
    tokens_completion: number;

    // Native token counts (provider-reported; pricing is based on these)
    native_tokens_prompt: number;
    native_tokens_completion: number;
    native_tokens_completion_images: number | null;
    native_tokens_reasoning: number | null;
    native_tokens_cached: number | null;

    // Performance metrics
    latency: number | null;          // Total latency in ms
    generation_time: number | null;  // Generation duration in ms
    moderation_latency: number | null;

    // Completion details
    finish_reason: string | null;
    native_finish_reason: string | null;
    streamed: boolean | null;
    cancelled: boolean | null;

    // Provider details
    provider_name: string | null;    // Which provider handled the request
    is_byok: boolean;
    provider_responses: object[] | null; // Fallback attempt records

    // Media/search
    num_media_prompt: number | null;
    num_media_completion: number | null;
    num_input_audio_prompt: number | null;
    num_search_results: number | null;

    // Routing
    router: string | null;           // Routing strategy used
    api_type: "completions" | "embeddings" | null;
    app_id: number | null;
    external_user: string | null;
  };
}
```

**Timing**: This endpoint may return incomplete data immediately after a request completes.
Add a short delay (100–500ms) before fetching if accurate final costs are needed.

---

### GET /api/v1/key

Checks current API key status, credit balance, and rate limits. See Authentication section above.

---

### POST /api/v1/responses (Beta)

OpenAI Responses API-compatible beta endpoint. Stateless; no server-side conversation state.

```
POST https://openrouter.ai/api/v1/responses
```

Request uses `input` field instead of `messages`. Supports reasoning, tool calling, web search.
Not for production use; subject to breaking changes.

---

### POST /api/v1/embeddings

Embeddings endpoint. OpenAI-compatible. Not covered in this document; see official docs.

---

## Streaming (SSE)

Enable with `stream: true` in the request body.

### Event Format

Each chunk is a standard SSE `data:` event with JSON:

```
data: {"id":"gen-abc","object":"chat.completion.chunk","created":1234567890,
       "model":"openai/gpt-4o","provider":"OpenAI","choices":[{"index":0,
       "delta":{"content":"Hello"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-abc","object":"chat.completion.chunk","created":1234567890,
       "model":"openai/gpt-4o","provider":"OpenAI","choices":[{"index":0,
       "delta":{"content":""},"finish_reason":"stop","native_finish_reason":"stop"}],
       "usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}}

data: [DONE]
```

### Streaming-Specific Fields

- `object` is `"chat.completion.chunk"` (not `"chat.completion"`)
- `choices[].delta` contains partial content (instead of `message`)
- `usage` only present in the **final chunk** before `[DONE]`
- `provider` field present in chunks (provider name string)
- `choices[].native_finish_reason` present in chunks

### Keep-Alive Comments

OpenRouter sends SSE comments to prevent connection timeouts during processing:

```
: OPENROUTER PROCESSING
```

These are valid SSE comments per spec and MUST be ignored by the client.

### Debug First Chunk

When `debug.echo_upstream_body: true` and `stream: true`, the FIRST chunk has:
- Empty `choices` array
- `debug` field containing the upstream request body

This is for development only.

### Mid-Stream Errors

If an error occurs after streaming has started, it arrives as an SSE event (HTTP status
remains 200 since headers were already sent):

```
data: {"error":{"code":500,"message":"Provider error","metadata":{"provider_name":"OpenAI",
       "raw":"...upstream error..."}},"finish_reason":"error","choices":[{"index":0,
       "delta":{},"finish_reason":"error"}]}

data: [DONE]
```

---

## OpenRouter-Specific Request Fields (Summary)

| Field | Type | Description |
|-------|------|-------------|
| `provider` | object | Provider routing preferences (see ProviderPreferences) |
| `models` | string[] | Fallback model list; tried in order if primary fails |
| `route` | `"fallback"` | Legacy routing flag; prefer `models[]` |
| `transforms` | string[] | Prompt transforms; currently `["middle-out"]` |
| `plugins` | Plugin[] | Enable web search, file parsing, response healing |
| `reasoning` | object | Reasoning effort and summary settings |
| `top_k` | integer | Not in OpenAI API; restricts to top N tokens |
| `repetition_penalty` | number | Not in OpenAI API; scales by token probability |
| `min_p` | number | Not in OpenAI API; minimum probability threshold |
| `top_a` | number | Not in OpenAI API; dynamic top-p |
| `session_id` | string | Groups related requests for observability |
| `trace` | object | Distributed tracing fields |
| `metadata` | object | Custom key-value; special keys for tracing |
| `debug` | object | Development: echo upstream request body |
| `verbosity` | enum | Output detail: `low`, `medium`, `high`, `max` |

---

## OpenRouter-Specific Response Fields (Summary)

| Field | Location | Description |
|-------|----------|-------------|
| `model` | root | ACTUAL model used (critical when using `models[]` fallbacks) |
| `provider` | chunk root (streaming only) | Provider name that served the request |
| `choices[].finish_reason` | normalized | Always one of: `stop`, `tool_calls`, `length`, `content_filter`, `error` |
| `choices[].native_finish_reason` | per choice | Raw finish reason string from provider |
| `choices[].message.reasoning` | per message | Reasoning/thinking text from thinking models |
| `choices[].message.reasoning_details` | per message | Structured reasoning token details |

**Cost data is NOT in the completion response.** Use `GET /api/v1/generation?id=<id>`.

---

## Response Headers

Headers returned by OpenRouter on chat completion responses:

| Header | Description |
|--------|-------------|
| `openrouter-generation-id` | Generation ID (same as `id` in body); use to query `/api/v1/generation` |
| `x-request-id` | Unique HTTP request identifier for support/debugging |
| `X-RateLimit-Limit` | Rate limit ceiling (in 429 error metadata) |
| `X-RateLimit-Remaining` | Remaining requests in window (in 429 error metadata) |
| `X-RateLimit-Reset` | Reset timestamp in Unix milliseconds (in 429 error metadata) |
| `Content-Type` | `application/json` or `text/event-stream` for streaming |

Rate limit headers are returned in the `metadata` object of 429 error responses, not as
standard HTTP headers on successful responses.

---

## Error Handling

### Error Response Format

```typescript
type ErrorResponse = {
  error: {
    code: number;      // Matches HTTP status code
    message: string;
    metadata?: {
      // For 429 errors:
      "X-RateLimit-Limit"?: string;
      "X-RateLimit-Remaining"?: string;
      "X-RateLimit-Reset"?: string;    // Unix ms timestamp

      // For 403 moderation errors:
      reasons?: string[];
      flagged_input?: string;          // Max 100 chars, truncated with "..."
      provider_name?: string;
      model_slug?: string;

      // For 502 provider errors:
      provider_name?: string;
      raw?: string;                    // Original provider error
    };
  };
};
```

### HTTP Error Codes

| Code | Meaning | Notes |
|------|---------|-------|
| 400 | Bad Request | Invalid or missing params; also CORS errors |
| 401 | Unauthorized | Invalid/disabled API key; expired OAuth session |
| 402 | Payment Required | Insufficient credits; negative balance |
| 403 | Forbidden | Input flagged by moderation |
| 408 | Request Timeout | Request timed out |
| 429 | Too Many Requests | Rate limited; check metadata for reset time |
| 502 | Bad Gateway | Provider down or returned invalid response |
| 503 | Service Unavailable | No provider meets routing requirements |

### Mid-Stream Errors

When streaming and an error occurs after tokens have been sent, the HTTP status is 200 (headers
already sent). The error arrives as an SSE event with `finish_reason: "error"` in choices.
Always check for `finish_reason === "error"` in streaming responses.

### Rate Limits

- **Free model variants** (`:free` suffix): 60 requests/minute
- **Daily limits without credits**: Limited requests/day
- **Daily limits with 10+ credits purchased**: 1,000 free model requests/day
- **DDoS protection**: Cloudflare blocks requests dramatically exceeding reasonable usage
- **RPS decreases** as account balance depletes; maintain sufficient balance in production

---

## Provider Routing

The `provider` object in requests controls how OpenRouter selects the backend provider.

### Provider Slugs

Provider slugs are the short identifiers used in `provider.order`, `provider.only`, and
`provider.ignore`. Obtain them from `GET /api/v1/models/{author}/{slug}/endpoints`
(`provider_name` field in each endpoint).

Common provider slugs: `OpenAI`, `Anthropic`, `Google`, `Amazon Bedrock`, `Together`,
`Fireworks`, `Groq`, `Replicate`, `DeepInfra`, `Azure`.

### Routing Examples

```json
// Use specific providers in priority order
{
  "provider": {
    "order": ["Anthropic", "Amazon Bedrock"],
    "allow_fallbacks": false
  }
}

// Lowest cost only
{
  "provider": { "sort": "price" }
}

// High throughput, no data collection
{
  "provider": {
    "sort": "throughput",
    "data_collection": "deny"
  }
}

// Hard price cap
{
  "provider": {
    "max_price": { "prompt": 0.001, "completion": 0.002 }
  }
}

// Performance thresholds (soft, deprioritizes non-compliant providers)
{
  "provider": {
    "preferred_max_latency": { "p90": 2.0 },
    "preferred_min_throughput": { "p50": 50 }
  }
}

// Zero data retention
{
  "provider": {
    "data_collection": "deny",
    "zdr": true
  }
}

// Only fp8 quantized endpoints
{
  "provider": {
    "quantizations": ["fp8"]
  }
}
```

### BYOK (Bring Your Own Key)

Supported providers: Amazon Bedrock, Google Vertex AI, Anthropic, Azure AI Services.

Configured in account settings; applied automatically. When BYOK key hits rate limit,
falls back to OpenRouter shared credits unless "Always use this key" is set. BYOK
endpoints are always prioritized over shared endpoints regardless of `provider.order`.
OpenRouter charges a service fee (waived for first N BYOK requests/month).

---

## Proxy Considerations

This section covers what a proxy sitting between a client and OpenRouter must handle.

### Request Pass-Through

A proxy MUST pass through these OpenRouter-specific fields without modification:
- `provider` object (routing preferences)
- `models` array (fallback list)
- `transforms` array
- `plugins` array
- `reasoning` object
- `session_id`, `trace`, `metadata` (observability)
- `top_k`, `repetition_penalty`, `min_p`, `top_a` (extra sampling params)

Fields the proxy may need to rewrite:
- `model`: May need to map from internal model names to `provider/model` format
- `Authorization`: Replace client key with proxy's OpenRouter key
- `HTTP-Referer`, `X-Title`: Set to proxy identity headers

### Response Pass-Through

A proxy MUST pass through:
- The `model` field (actual model used — clients need this for billing/routing decisions)
- `native_finish_reason` (clients may need the raw provider reason)
- `usage` object (token counts)
- `openrouter-generation-id` header (clients may query generation stats independently)
- `x-request-id` header (needed for support escalation)

### Streaming Considerations

- Pass SSE comments (`: OPENROUTER PROCESSING`) through to clients or silently drop them
  (both are valid per SSE spec)
- Mid-stream errors arrive as `data:` events with HTTP 200; proxy must not treat these
  as successful completions
- The `provider` field in streaming chunks should be passed through
- `usage` only in the final chunk before `[DONE]`; proxy must not buffer entire stream
  to inject usage

### Cost / Usage Accounting

The chat completion response does NOT contain cost. To track spend:
1. Capture `openrouter-generation-id` response header (or `id` from response body)
2. After request completes, call `GET /api/v1/generation?id=<id>` for cost data
3. Allow 100–500ms before querying; data may be incomplete immediately

### Model Name Translation

Clients using the OpenAI SDK may send bare model names like `gpt-4o`. A proxy targeting
OpenRouter must translate these to OpenRouter format:
- `gpt-4o` → `openai/gpt-4o`
- `claude-3-5-sonnet-20241022` → `anthropic/claude-3-5-sonnet`
- `gemini-2.0-flash` → `google/gemini-2.0-flash-001`

### Error Code Handling

OpenRouter adds error codes not in the standard OpenAI spec:
- `402`: Insufficient credits (not in OpenAI API)
- `503`: No provider meets routing requirements (not in OpenAI API)

Proxies forwarding to downstream clients should pass these through as-is.

### Strict Tool Calls Header

When a client sends `tools` with `strict: true`, the proxy MUST forward the header:
```
structured-outputs-2025-11-13: true
```
Without this header, OpenRouter strips `strict` from tool definitions.

### Parameter Handling

OpenRouter silently ignores parameters unsupported by the target model. A proxy does NOT
need to strip unknown parameters before forwarding — this is safe by design.

---

## Key Management API

Programmatic API key management. All endpoints under `/api/v1/keys` require a
**Management API key** (different from a standard API key) in the `Authorization` header.

```
GET    /api/v1/keys           # List keys
POST   /api/v1/keys           # Create key
GET    /api/v1/keys/{id}      # Get key
PATCH  /api/v1/keys/{id}      # Update key
DELETE /api/v1/keys/{id}      # Delete key
```

---

## Quick Reference: Complete Endpoint List

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/chat/completions` | Chat completions (primary) |
| POST | `/api/v1/responses` | Responses API beta |
| POST | `/api/v1/embeddings` | Text embeddings |
| GET | `/api/v1/models` | List all models |
| GET | `/api/v1/models/{author}/{slug}/endpoints` | Model provider endpoints + metrics |
| GET | `/api/v1/generation` | Generation stats + cost by ID |
| GET | `/api/v1/key` | Current key status + credit balance |
| GET/POST/PATCH/DELETE | `/api/v1/keys/*` | Key management (Management API key required) |
| GET | `/api/v1/auth/key` | Auth key info (alias for `/api/v1/key`) |

---

## Sources

- [OpenRouter API Reference Overview](https://openrouter.ai/docs/api/reference/overview)
- [Chat Completions Endpoint](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request)
- [Provider Routing Guide](https://openrouter.ai/docs/guides/routing/provider-selection)
- [Model Fallbacks](https://openrouter.ai/docs/guides/routing/model-fallbacks)
- [API Parameters](https://openrouter.ai/docs/api/reference/parameters)
- [Streaming Reference](https://openrouter.ai/docs/api/reference/streaming)
- [Models Endpoint](https://openrouter.ai/docs/api/api-reference/models/get-models)
- [Endpoints Endpoint](https://openrouter.ai/docs/api/api-reference/endpoints/list-endpoints)
- [Generation Endpoint](https://openrouter.ai/docs/api/api-reference/generations/get-generation)
- [Rate Limits](https://openrouter.ai/docs/api/reference/limits)
- [Error Handling](https://openrouter.ai/docs/api/reference/errors-and-debugging)
- [Authentication](https://openrouter.ai/docs/api/reference/authentication)
- [Quickstart](https://openrouter.ai/docs/quickstart)
- [Model Variants: Nitro](https://openrouter.ai/docs/guides/routing/model-variants/nitro)
- [Model Variants: Free](https://openrouter.ai/docs/guides/routing/model-variants/free)
- [Model Variants: Extended](https://openrouter.ai/docs/guides/routing/model-variants/extended)
- [Model Variants: Thinking](https://openrouter.ai/docs/guides/routing/model-variants/thinking)
- [Model Variants: Online](https://openrouter.ai/docs/guides/routing/model-variants/online)
- [Model Variants: Exacto](https://openrouter.ai/docs/guides/routing/model-variants/exacto)
- [Plugins Overview](https://openrouter.ai/docs/guides/features/plugins/overview)
- [BYOK](https://openrouter.ai/docs/guides/overview/auth/byok)
- [Responses API Beta](https://openrouter.ai/docs/api/reference/responses/overview)
