# AI Gateway Master Feature Parity Plan

> **Date**: 2026-02-20
> **Scope**: Full competitive parity with OpenRouter, Vercel AI Gateway, LiteLLM Proxy,
>            Bifrost, Portkey, Cloudflare AI Gateway, Kong AI Gateway + 21-product landscape
> **Goal**: thegent as a best-in-class provider aggregate and LLM gateway
>
> **Research basis** (all in docs/research/ and docs/context/):
> - OpenRouter (API research, gap analysis, features, proxy audit, models)
> - Vercel AI Gateway (1,100-line research + 552-line context)
> - LiteLLM Proxy (1,147-line research + 455-line context + 377-line gap analysis)
> - Bifrost/Maxim AI (860-line research + 391-line context)
> - Portkey (1,085-line research + 518-line context)
> - Cloudflare AI Gateway (750-line research + 374-line context)
> - Kong AI Gateway (998-line research + 263-line context)
> - AI Gateway Landscape 2026 (21 products, 705-line research + 231-line context)

---

## Section 1: Our Current Advantages

These are features thegent has that most or all competitors lack. Protect and extend these.

| Advantage | Evidence | Action |
|-----------|----------|--------|
| **Self-hostable / local-first** | Vercel and Cloudflare are SaaS-only; LiteLLM requires PostgreSQL + Redis | Keep as core positioning |
| **Codex Responses API** (`/v1/responses`) | No competitor has this; OpenRouter has a beta; Vercel does not | Extend, don't break |
| **WebSocket bridge** | No competitor proxies WebSocket LLM sessions | Extend to more harnesses |
| **MCP server management** | Only Bifrost and Kong have MCP features; ours is native | Extend MCP gateway |
| **Pareto-front model selection** | Unique — multi-dimensional cost/quality/latency optimization | Formalize, expose as routing mode |
| **UID pool isolation** | No competitor has per-agent OS user isolation | Keep, extend to budget scoping |
| **Agent task-type routing** | Unique — route by agent role/task type | Formalize as routing dimension |
| **Teammate runner model** | Unique — agent lifecycle management at the routing layer | Extend |
| **Harness-native routing** | Route by harness (Codex vs Claude Code vs Cursor) | Formalize |

---

## Section 2: Table Stakes (Must-Have)

Every competitive gateway has these. We cannot claim to be competitive without them.

| Feature | Who Has It | Our State | Complexity |
|---------|-----------|-----------|------------|
| **Semantic caching** | Bifrost (5ms hit), Kong, LiteLLM, Portkey (also Cloudflare: planned) | **None** | L |
| **Exact-match caching** | Everyone | **None** | S |
| **Per-deployment circuit breaker** | LiteLLM, Portkey, Bifrost, Kong | **None** | M |
| **Virtual keys with budget** | LiteLLM (8-level hierarchy), Portkey, Bifrost, Kong | **None** | L |
| **Prometheus `/metrics`** | LiteLLM, Bifrost, Kong | **None** | M |
| **Model fallback chains** | Everyone | **Partial** (cost router has fallback but no explicit chain) | M |
| **Provider routing preferences** | OpenRouter, Vercel, Portkey | **None** | M |
| **SSE keep-alive handling** | Needed for OpenRouter/Cloudflare | **Bug: crashes** | S (P0 fix) |
| **WebSocket auth passthrough** | All | **Bug: drops header** | S (P0 fix) |
| **HTTPS verify=True** | All | **Bug: verify=False** | XS (P0 fix) |
| **Cost in every response** | OpenRouter, LiteLLM (`x-litellm-response-cost`), Bifrost | **None** | M |
| **Error format preservation** | All | **Replaces with generic message** | S |
| **Native Anthropic endpoint** | Vercel (`POST /v1/messages`) | **None** | M |

---

## Section 3: Priority Feature Backlog

### P0 — Bug Fixes (unblock everything)

| ID | Feature | Inspired By | File | Complexity |
|----|---------|-------------|------|------------|
| GW-01 | Fix SSE keep-alive comment crash (`: OPENROUTER PROCESSING`) | OpenRouter, Cloudflare | `cliproxy_adapter.py` | XS |
| GW-02 | Fix WebSocket drops Authorization header | All | `cliproxy_adapter.py:661` | XS |
| GW-03 | Fix `verify=False` → `verify=True` for HTTPS backends | All | `cliproxy_adapter.py` | XS |
| GW-04 | Fix content array collapse in Responses transform (breaks cache_control) | OpenRouter, Anthropic | `cliproxy_adapter.py` | S |
| GW-05 | Preserve error body from backend (stop replacing with generic) | OpenRouter, LiteLLM | `cliproxy_adapter.py` | S |
| GW-06 | Add 402/408/502/503 to error map | OpenRouter, Cloudflare | `cliproxy_adapter.py` | XS |
| GW-07 | Fix tool call delta dropped in transform mode | OpenRouter, all | `cliproxy_adapter.py` | S |
| GW-08 | Add `openrouter` to `API_KEY_PROVIDERS` | OpenRouter | `routing/provider_types.py` | XS |
| GW-09 | Propagate actual routed model from SSE chunks | OpenRouter, Vercel | `cliproxy_adapter.py` | S |

### P1 — Routing Infrastructure

| ID | Feature | Inspired By | File | Complexity |
|----|---------|-------------|------|------------|
| GW-10 | **Recursive `RouteConfig` schema** — `strategy/targets/cache/retry/cb_config` | Portkey | `routing/route_config.py` (new) | L |
| GW-11 | **Provider routing preferences** — `order/only/ignore/allow_fallbacks/ZDR/quantizations/sort/max_price` | OpenRouter, Vercel | `routing/provider_preferences.py` (new) | M |
| GW-12 | **Model fallback chain** — `models: [...]` array, retry on failure | OpenRouter, Vercel, Portkey | `cliproxy_adapter.py`, `routing/` | M |
| GW-13 | **Per-deployment circuit breaker** — `allowed_fails + cooldown_time`, excludes failed deployments | LiteLLM, Portkey, Bifrost | `routing/circuit_breaker.py` (new) | M |
| GW-14 | **Model suffix routing** — `:nitro`/`:floor`/`:free`/`:thinking`/`:online` | OpenRouter | `routing/model_suffix_parser.py` (new) | S |
| GW-15 | **OpenRouter model ID mappings** — thegent alias → `provider/model` | OpenRouter | `routing/harness_model_mapping.py` | M |
| GW-16 | **LiteLLM router OpenRouter config** — add OpenRouter as first-class backend | LiteLLM | `routing/litellm_router.py` | S |
| GW-17 | **Provider budget routing** — auto-route away when provider hits spend cap | LiteLLM | `routing/cost_aware_router.py` | M |
| GW-18 | **Deployment pool concept** — N backends behind one model name, load-balanced | LiteLLM | `routing/cost_aware_router.py` | L |
| GW-19 | **Sliding window rate limiting** (prevents burst clustering at window reset) | Cloudflare | `routing/rate_limiter.py` (new) | M |
| GW-20 | **`tg-*` header namespace** — per-request control: `tg-cache-ttl`, `tg-skip-cache`, `tg-event-id`, `tg-fallback-step`, `tg-custom-cost` | Cloudflare `cf-aig-*` | `cliproxy_adapter.py` | M |
| GW-21 | **Session stickiness** — consistent-hashing LB for multi-turn conversations | Kong | `routing/cost_aware_router.py` | M |

### P1 — Caching

| ID | Feature | Inspired By | File | Complexity |
|----|---------|-------------|------|------------|
| GW-22 | **Exact-match cache** — hash(model+messages) → cached response | LiteLLM, Portkey, Cloudflare | `routing/cache.py` (new) | M |
| GW-23 | **Semantic cache** — embedding cosine similarity (~5ms hit vs ~2s LLM) | Bifrost, Kong, LiteLLM, Portkey | `routing/semantic_cache.py` (new) | L |
| GW-24 | **Cache namespace header** — `tg-cache-namespace: user-123` for per-user partitioning | Portkey | `cliproxy_adapter.py` | S |
| GW-25 | **Cache force-refresh** — `tg-cache-force-refresh: true` per-request bypass | Portkey | `cliproxy_adapter.py` | XS |
| GW-26 | **DualCache L1+L2** — in-memory L1 + Redis/disk L2 | LiteLLM | `routing/cache.py` | M |
| GW-27 | **Cache-hit response headers** — `x-cache-status: HIT/MISS`, `x-cache-ttl` | LiteLLM, Kong, Cloudflare | `cliproxy_adapter.py` | S |

### P1 — Virtual Keys + Budget

| ID | Feature | Inspired By | File | Complexity |
|----|---------|-------------|------|------------|
| GW-28 | **Virtual key system** — per-key budget/rate/model restrictions | LiteLLM, Portkey, Bifrost | `routing/virtual_keys.py` (new) | L |
| GW-29 | **Budget hierarchy** — Team → User → Key spending limits | LiteLLM (8-level), Bifrost | `routing/budget.py` (new) | L |
| GW-30 | **Budget reset periods** — `24h`, `7d`, `30d`, `monthly` | LiteLLM | `routing/budget.py` | S |
| GW-31 | **Soft budget alerts** — notify at 80% threshold, hard block at 100% | LiteLLM, Portkey | `routing/budget.py` | S |
| GW-32 | **`tg-response-cost` response header** — USD cost on every response | LiteLLM (`x-litellm-response-cost`) | `cliproxy_adapter.py` | S |
| GW-33 | **Per-request cost injection** — compute cost from pricing table | LiteLLM, OpenRouter, Bifrost | `routing/cost_calculator.py` (new) | M |

### P1 — Observability

| ID | Feature | Inspired By | File | Complexity |
|----|---------|-------------|------|------------|
| GW-34 | **Prometheus `/metrics` endpoint** — token counts, latency, cost, error rates, cache hits | LiteLLM (25+ families), Bifrost, Kong | `observability/prometheus.py` (new) | M |
| GW-35 | **`tg-event-id` on every response** — unique trace anchor including failures | Cloudflare `cf-aig-event-id` | `cliproxy_adapter.py` | S |
| GW-36 | **`tg-fallback-step` header** — which step in fallback chain executed | Cloudflare `cf-aig-step` | `cliproxy_adapter.py` | S |
| GW-37 | **OTel OTLP export** — LLM call spans with GenAI semantic conventions | Kong, Portkey, LiteLLM | `observability/otel.py` (new) | L |
| GW-38 | **TTFT (Time-to-First-Token) tracking** | Kong, Bifrost | `cliproxy_adapter.py` | S |
| GW-39 | **Async observability** (no hot path impact) | Helicone | `observability/` | M |

### P1 — Request/Response Extensions

| ID | Feature | Inspired By | File | Complexity |
|----|---------|-------------|------|------------|
| GW-40 | **Unified `reasoning` interface** — `{effort: "high"}` → Anthropic `extended_thinking`, OpenAI `reasoning_effort`, Gemini `thinking_config` | OpenRouter, Vercel | `routing/reasoning_transform.py` (new) | M |
| GW-41 | **`transforms: ["middle-out"]`** — context compression for short-context models | OpenRouter | `routing/transforms.py` (new) | M |
| GW-42 | **Forward OpenRouter request fields** — `provider`, `models`, `transforms`, `plugins`, `reasoning`, `route` | OpenRouter | `cliproxy_adapter.py` | S |
| GW-43 | **Native Anthropic endpoint** — `POST /v1/messages` with `x-api-key` auth | Vercel | `cliproxy_adapter.py` | M |
| GW-44 | **Vercel `providerOptions.gateway` passthrough** | Vercel | `cliproxy_adapter.py` | S |
| GW-45 | **Forward special headers** — `x-session-id`, `x-anthropic-beta`, `structured-outputs-2025-11-13` | OpenRouter, Vercel | `cliproxy_adapter.py` | XS |
| GW-46 | **Enrich `/v1/models`** — add `pricing`, `context_length`, `supported_parameters`, `architecture` | OpenRouter, Vercel | `cliproxy_adapter.py` | M |
| GW-47 | **Inject missing proxy models** into `/v1/models` (fixes "Model metadata not found") | (our bug) | `cliproxy_adapter.py` | S |
| GW-48 | **`usage.cost` in every response** | OpenRouter, LiteLLM | `cliproxy_adapter.py` | S |
| GW-49 | **`native_finish_reason`** alongside normalized `finish_reason` | OpenRouter | `cliproxy_adapter.py` | S |

### P2 — Guardrails

| ID | Feature | Inspired By | File | Complexity |
|----|---------|-------------|------|------------|
| GW-50 | **Prompt injection detection** | Portkey, LiteLLM, Kong | `routing/guardrails/injection.py` | M |
| GW-51 | **PII masking round-trip** — redact on input, re-insert original in output | LiteLLM (Presidio), Kong | `routing/guardrails/pii.py` | L |
| GW-52 | **JSON schema validation** — output guardrail verifying structured output | Portkey | `routing/guardrails/json_schema.py` | S |
| GW-53 | **Webhook guardrail interface** — `POST url → {verdict, transformedData}` | Portkey | `routing/guardrails/webhook.py` | M |
| GW-54 | **Content moderation** (input + output) | Portkey (50+ checks), Kong | `routing/guardrails/moderation.py` | M |
| GW-55 | **Semantic prompt guard** — embedding similarity vs reference prompts | Kong, Portkey | `routing/guardrails/semantic_guard.py` | M |

### P2 — Advanced Routing

| ID | Feature | Inspired By | File | Complexity |
|----|---------|-------------|------|------------|
| GW-56 | **Conditional routing** — route by `metadata.<key>`, `params.<key>`, `url.pathname` with operators | Portkey (`$eq/$in/$regex/$and/$or`) | `routing/conditional.py` (new) | M |
| GW-57 | **CEL routing rules** — expression language for complex per-request routing | Bifrost | `routing/cel_router.py` (new) | L |
| GW-58 | **Tag-based routing** — route `free_tier` vs `paid_tier` to different deployments | LiteLLM | `routing/tag_router.py` (new) | M |
| GW-59 | **Traffic mirroring** — shadow A/B deployment (send to secondary silently) | LiteLLM | `routing/mirror.py` (new) | M |
| GW-60 | **EWMA latency tracking** — exponential weighted moving average for fastest-provider routing | Kong | `routing/latency_tracker.py` (new) | M |
| GW-61 | **Semantic load balancing** — route to model whose description best matches prompt | Kong (unique feature) | `routing/semantic_lb.py` (new) | XL |
| GW-62 | **Pre-call context window check** → triggers `context_window_fallbacks` | LiteLLM | `routing/context_validator.py` (new) | S |
| GW-63 | **Dynamic routing nodes** — Conditional / Percentage / Budget-Limit declarative flow | Cloudflare | `routing/route_config.py` | L |

### P2 — MCP Gateway

| ID | Feature | Inspired By | File | Complexity |
|----|---------|-------------|------|------------|
| GW-64 | **MCP gateway** — route LLM tool calls through MCP servers, expose as REST | Bifrost `/v1/mcp/tool/execute`, Kong `ai-mcp-proxy` | `mcp/gateway.py` (extend existing) | L |
| GW-65 | **Per-tool ACLs** — restrict which agents can call which MCP tools | Kong | `mcp/acl.py` | M |
| GW-66 | **REST → MCP conversion** — wrap any REST endpoint as MCP tool | Kong `ai-mcp-proxy` | `mcp/rest_to_mcp.py` | L |
| GW-67 | **A2A protocol support** | AgentGateway (OSS) | `protocols/a2a.py` | XL |

### P3 — Aspirational

| ID | Feature | Inspired By | Complexity |
|----|---------|-------------|------------|
| GW-68 | **ML meta-model routing** — task classification → best model | Not Diamond, Martian | XL |
| GW-69 | **Auto prompt rewriting per model** — normalize prompt style per provider | Not Diamond | XL |
| GW-70 | **Online eval routing** — route to highest-scoring model per task type | Braintrust | XL |
| GW-71 | **DLP** — GDPR/HIPAA/PCI DSS pre-built profiles | Cloudflare | L |
| GW-72 | **SSO/RBAC/audit logs** | LiteLLM Enterprise, Portkey Enterprise | XL |
| GW-73 | **Prompt library / versioning** | Portkey | L |
| GW-74 | **LLM evals integration** | Braintrust, Langfuse | L |

---

## Section 4: Architecture Decisions Needed

These require a design choice before implementation.

### 1. RouteConfig Schema (GW-10)
- **Option A**: Portkey's recursive `strategy/targets/cache/retry/cb_config`
- **Option B**: Flat config with explicit fallback lists
- **Recommendation**: Portkey pattern — recursive trees cover all cases (load balance inside fallback, conditional inside load balance)

### 2. Caching Backend (GW-22/23)
- **Option A**: Redis (standard; LiteLLM, Portkey)
- **Option B**: In-memory first (simple; for local-first / no-infra installs)
- **Option C**: DualCache L1 in-memory + L2 Redis (LiteLLM pattern)
- **Option D**: SQLite for semantic vectors (low-infra; like Bifrost's embedded option)
- **Recommendation**: DualCache — in-memory by default, Redis if configured. Semantic uses SQLite/Qdrant.

### 3. Virtual Key Storage (GW-28)
- **Option A**: PostgreSQL (LiteLLM requires it)
- **Option B**: SQLite (local-first friendly)
- **Option C**: Config file (simple, no DB)
- **Recommendation**: SQLite default; PostgreSQL optional for enterprise

### 4. `tg-*` Header Namespace (GW-20)
Design the full set now so it's consistent:
```
tg-cache-ttl: 300
tg-skip-cache: true
tg-cache-namespace: user-123
tg-cache-force-refresh: true
tg-event-id: <uuid>           (response only)
tg-fallback-step: 2           (response only — which fallback fired)
tg-response-cost: 0.00042     (response only — USD)
tg-custom-cost: 0.002         (request — override pricing)
tg-log-skip: true
tg-session-id: sess-abc       (group related requests)
```

### 5. Native Anthropic Endpoint (GW-43)
Add `POST /v1/messages` that accepts Anthropic native format and routes to any Anthropic-compatible backend. Required to be on par with Vercel AI Gateway.

### 6. ML Routing Integration (GW-68)
- **Option A**: Integrate Not Diamond API (SaaS dependency)
- **Option B**: Build lightweight task classifier (classify → routing rule)
- **Option C**: Use prompt embedding similarity to model capability vectors
- **Recommendation**: Start with Option C (no external dependency), offer Option A as premium

---

## Section 5: Implementation Batches

### Batch 1: P0 Bug Fixes (1-2 days, all parallelizable)
GW-01, GW-02, GW-03, GW-04, GW-05, GW-06, GW-07, GW-08, GW-09

### Batch 2: Provider Routing + Model Registry (3-5 days)
GW-10, GW-11, GW-12, GW-15, GW-16 | depends on: Batch 1

### Batch 3: Reliability Infrastructure (3-5 days)
GW-13, GW-17, GW-18, GW-19, GW-21 | depends on: Batch 2

### Batch 4: Caching (5-7 days)
GW-22, GW-23, GW-24, GW-25, GW-26, GW-27 | depends on: Architecture decision on backend

### Batch 5: Request/Response Extensions (3-5 days, parallelizable)
GW-40, GW-41, GW-42, GW-43, GW-44, GW-45, GW-46, GW-47, GW-48, GW-49 | depends on: Batch 1

### Batch 6: Virtual Keys + Budget (5-7 days)
GW-28, GW-29, GW-30, GW-31, GW-32, GW-33 | depends on: Batch 2

### Batch 7: Observability (3-5 days)
GW-34, GW-35, GW-36, GW-37, GW-38, GW-39 | depends on: Batch 3, 6

### Batch 8: Guardrails (5-7 days)
GW-50, GW-51, GW-52, GW-53, GW-54, GW-55 | depends on: Batch 5

### Batch 9: Advanced Routing (7-10 days)
GW-56, GW-57, GW-58, GW-59, GW-60, GW-61, GW-62, GW-63 | depends on: Batch 2, 3

### Batch 10: MCP Gateway Extensions (5-7 days)
GW-64, GW-65, GW-66 | depends on: Batch 5

### Batch 11: Model Suffix Routing (1-2 days)
GW-14 | depends on: Batch 2

---

## Section 6: What We Should NOT Build

| Feature | Why Not |
|---------|---------|
| Managed SaaS control plane | We're local-first/self-hosted — this contradicts our positioning |
| Kubernetes operator | Out of scope; users bring their own infra |
| Web-based observability dashboard | Not our UI surface; expose Prometheus, let users use Grafana |
| Billing/credit system | We're a routing layer, not a payment processor |
| SSO/RBAC enterprise auth | Not until P3; complex, low early ROI |
| Our own model inference | We route to providers, we don't run models |

---

## Section 7: Competitive Position After P0+P1

| Product | After P0+P1 | After P2 | We Excel |
|---------|------------|---------|---------|
| **OpenRouter** | Match all core features | Exceed on routing sophistication | Self-hosted, Codex Responses API, WebSocket, Pareto selection |
| **Vercel AI Gateway** | Match most | Exceed on routing + guardrails | Self-hosted, no SaaS lock-in, Codex native support |
| **LiteLLM Proxy** | Match most | Exceed on MCP + agent routing | Codex Responses API, agent-native routing, UID isolation |
| **Bifrost** | Match core | Exceed on agent integration | MCP native, agent task routing, harness awareness |
| **Portkey** | Match routing/cache | Match guardrails | Self-hosted, agent-native, Codex support |
| **Cloudflare AI Gateway** | Match | Exceed (semantic caching first!) | Self-hosted, no edge lock-in, provider depth |
| **Kong AI Gateway** | Match AI plugins | Approach on semantic features | Simpler setup, no Kong dependency, agent-native |

---

## New Files to Create

```
src/thegent/routing/
  route_config.py          # GW-10: recursive RouteConfig schema
  provider_preferences.py  # GW-11: ProviderPreferences model
  circuit_breaker.py       # GW-13: per-deployment circuit breaker
  model_suffix_parser.py   # GW-14: :nitro/:floor/:free/:thinking/:online
  rate_limiter.py          # GW-19: sliding window rate limiter
  cache.py                 # GW-22/26: exact + DualCache
  semantic_cache.py        # GW-23: embedding-based semantic cache
  reasoning_transform.py   # GW-40: unified reasoning → provider-native
  transforms.py            # GW-41: middle-out context compression
  cost_calculator.py       # GW-33: per-request USD cost computation
  latency_tracker.py       # GW-60: EWMA latency per provider
  context_validator.py     # GW-62: pre-call context window check
  conditional.py           # GW-56: conditional routing rules
  virtual_keys.py          # GW-28: virtual key lifecycle
  budget.py                # GW-29: hierarchical budget enforcement
  guardrails/
    injection.py           # GW-50
    pii.py                 # GW-51
    json_schema.py         # GW-52
    webhook.py             # GW-53
    moderation.py          # GW-54
    semantic_guard.py      # GW-55

src/thegent/observability/
  prometheus.py            # GW-34: metrics endpoint
  otel.py                  # GW-37: OpenTelemetry export
```
