# LiteLLM Proxy

> Concise reference for AI agents working on thegent CLIProxy parity with LiteLLM's gateway product.
> Full research: `docs/research/LITELLM_PROXY_RESEARCH_2026-02-20.md`
> Sources fetched: 2026-02-20

---

## What It Is / Deployment

LiteLLM Proxy (also called "LiteLLM AI Gateway") is a self-hosted OpenAI-compatible HTTP server
that fronts 100+ LLM providers behind a single `POST /v1/chat/completions` interface.

**Install:** `pip install litellm[proxy]`
**Start:** `litellm --config config.yaml` (default port: 4000)
**Performance:** 1,500+ req/sec, 8ms P95 at 1k RPS (self-reported)

**Deployment stack:**
- Docker/Docker Compose (primary deployment path)
- **PostgreSQL** — required for virtual keys, spend logs, audit logs
- **Redis** — required for distributed rate-limiting, cross-instance load balancing, caching
- Single-binary mode (no DB/Redis) works for development only

Enterprise tier available via AWS Marketplace (~$30k/year) adds SSO, RBAC, audit logs, dedicated
support. Open-source (MIT) core is fully functional for routing, caching, cost tracking.

---

## Configuration (config.yaml Key Fields)

```yaml
model_list:
  - model_name: gpt-4o            # User-facing name (what clients send as model=)
    litellm_params:
      model: azure/gpt-4o         # provider/model-id format
      api_base: https://...
      api_key: os.environ/AZURE_API_KEY
      rpm: 500                    # Rate limit per deployment
      tpm: 100000
      extra_headers: {}
    model_info:
      id: "deployment-stable-uuid" # Stable ID for fallback references
      tags: ["eu", "paid"]         # For tag-based routing
      order: 1                     # Priority (lower = higher priority)

router_settings:
  routing_strategy: "usage-based-routing-v2"
  model_group_alias:
    gpt-4: gpt-4o                 # Rename incoming model names
  num_retries: 3
  timeout: 30
  redis_host: redis
  enable_pre_call_checks: true    # Context window + region checks
  enable_tag_filtering: true
  provider_budget_config:         # Cap spend per provider
    openai: {budget_limit: 100, time_period: "1d"}
    anthropic: {budget_limit: 200, time_period: "7d"}

litellm_settings:
  fallbacks:
    - {gpt-4o: [claude-sonnet, gemini-pro]}
  context_window_fallbacks:
    - {gpt-4o: [gpt-4o-128k]}
  allowed_fails: 3                # Failures before deployment cooldown
  cooldown_time: 60               # Cooldown seconds
  cache: true
  cache_params:
    type: redis-semantic
    ttl: 600
    similarity_threshold: 0.85
  success_callback: [langfuse, prometheus]

general_settings:
  master_key: sk-admin-key        # Proxy admin auth key
  database_url: postgresql://...
  max_budget: 10000               # Global proxy spend cap (USD)
  alerting: [slack]
```

---

## Authentication (Virtual Keys, Master Key)

**Master key:** Configured in `general_settings.master_key` or `LITELLM_PROXY_MASTER_KEY` env var.
Grants full admin access to all endpoints including management APIs. Must start with `sk-`.

**Virtual keys:** All external callers use virtual keys generated via the proxy's management API.
Format: `sk-{random}`. Only the hash is stored. Plaintext returned once at creation.

Key properties at creation time:
- `budget_limit` + `budget_duration` — hard spend cap with auto-reset
- `tpm_limit`, `rpm_limit`, `max_parallel_requests` — rate limits
- `models` — restrict to named models
- `team_id` — attach to a team (inherits team's budget)
- `aliases` — per-key model aliasing (`gpt-4` → `gpt-4o-mini` silently)
- `tags` — for tag-based routing and cost tracking
- `expires` — expiration timestamp
- `allowed_routes` — restrict to `llm_api_routes` or `management_routes`
- `auto_rotate` + `rotation_interval` — automatic key rotation

Key management endpoints: `/key/generate`, `/key/update`, `/key/delete`, `/key/regenerate`,
`/key/block`, `/key/info`, `/key/list`.

Custom header: configurable via `litellm_key_header_name` (default: `Authorization: Bearer`).

**Budget hierarchy (8 levels, checked in order):**
Key → User → Team → Organization → Model-specific → Global Proxy → Provider → Tag

Rate limit types: `input`, `output`, or `total` tokens (config: `token_rate_limit_type`).
Admin keys bypass all rate limits.

---

## Provider Support

100+ providers. Notable ones:

| Provider | Config `model` string |
|----------|----------------------|
| OpenAI | `openai/gpt-4o` |
| Anthropic | `anthropic/claude-3-5-sonnet` |
| Google / Vertex | `google/gemini-pro`, `vertex_ai/gemini-pro` |
| AWS Bedrock | `bedrock/anthropic.claude-3-sonnet-20240229-v1:0` |
| Azure OpenAI | `azure/<deployment-name>` |
| Cohere | `cohere/command-r` |
| Groq | `groq/llama-3.1-70b` |
| DeepSeek | `deepseek/deepseek-chat` |
| Mistral | `mistral/mistral-large` |
| NVIDIA NIM | `openai/meta-llama2-70b` (with `api_base`) |
| vLLM / Ollama | `openai/<model>` (with `api_base` pointing to local server) |
| HuggingFace | `huggingface/<model-id>` |
| OpenRouter | `openrouter/<model>` |

**Wildcard routing** — route any model from a provider without listing it:
```yaml
- model_name: openai/*
  litellm_params:
    model: openai/*
    api_key: os.environ/OPENAI_API_KEY
```

With `check_provider_endpoint: true`, the `/v1/models` endpoint dynamically queries the provider.

---

## Load Balancing Strategies

Multiple entries with the same `model_name` form a deployment pool:

| Strategy | Key | Use Case |
|----------|-----|----------|
| `simple-shuffle` | Weighted random (default) | General; lowest overhead |
| `usage-based-routing-v2` | Routes to deployment with lowest current TPM usage (Redis) | Rate-limit avoidance |
| `latency-based-routing` | Selects lowest-latency deployment (TTFT history) | Latency-sensitive |
| `least-busy` | Fewest in-flight concurrent requests | Parallel-heavy |
| `cost-based-routing` | Cheapest deployment via built-in cost map | Budget optimization |
| Custom | `CustomRoutingStrategyBase` | Any application logic |

**Weight distribution:** Set `weight: 9` vs `weight: 1` on deployments for proportional traffic.

**Priority ordering:** `model_info.order: 1` (primary), `order: 2` (secondary fallback).

**Max parallel requests:** `litellm_params.max_parallel_requests: 10` caps concurrency per deployment.

**Traffic mirroring:** Shadow deployments receive a copy of production traffic for silent A/B evaluation.

---

## Reliability (Fallbacks / Retries / Circuit Breakers)

**Three fallback types:**
1. **Regular** — any error: `fallbacks: [{gpt-4o: [claude-sonnet, gemini-pro]}]`
2. **Context window** — context exceeded: `context_window_fallbacks`
3. **Content policy** — moderation reject: `content_policy_fallbacks`
4. **Default** — catch-all: `default_fallbacks: [gpt-4o-mini]`

Fallbacks can reference specific deployment UUIDs (`model_info.id`) for precise control.
Per-request override: send `disable_fallbacks: true` in request body.

**Retries:**
- `num_retries: 3` — retries per deployment before attempting fallback
- `retry_after: 5` — delay between retries (seconds)
- `RateLimitError` → exponential backoff; generic errors → immediate retry

**Circuit breaker (cooldown):**
- `allowed_fails: 3` — failure threshold within the monitoring window
- `cooldown_time: 60` — seconds to exclude failing deployment from routing pool
- After cooldown, deployment is automatically re-admitted
- Prometheus: `litellm_deployment_cooled_down` tracks current cooldowns

**Pre-call checks** (`enable_pre_call_checks: true`):
- Context window check: rejects before calling if prompt would overflow; routes to `context_window_fallbacks`
- Region check: routes only to deployments matching region constraints (EU data residency)

---

## Caching

**7 cache backends:** `local` (in-memory), `disk`, `redis`, `redis-semantic`, `qdrant-semantic`, `s3`, `gcs`

**DualCache (L1+L2):** All Redis-backed deployments use two-tier caching:
- L1 (in-process dict): sub-millisecond, local only
- L2 (Redis): shared across all proxy instances

**Key config fields:**
```yaml
cache_params:
  type: redis-semantic         # or "redis", "local", "qdrant-semantic", "s3"
  ttl: 600                     # Default TTL seconds
  default_in_memory_ttl: 60    # L1 TTL
  default_in_redis_ttl: 3600   # L2 TTL
  namespace: "litellm.prod"    # Key prefix for multi-env isolation
  mode: default_off            # Opt-in: clients must send cache.use-cache=true
  similarity_threshold: 0.85   # Semantic cache match threshold
  embedding_model: "text-embedding-3-small"
  supported_call_types:        # Restrict caching to specific call types
    - completion
    - embedding
```

**Semantic caching:** Redis RediSearch module required. On a cache hit, returns stored response if
similarity score ≥ threshold. Response header `x-litellm-semantic-similarity` contains the score.

**Cache hit headers:** `x-litellm-cache-key` (hash), `x-litellm-semantic-similarity` (score).

**Per-request control:** `{"cache": {"use-cache": true}, "ttl": 120}` in request body.

---

## Cost Tracking + Budgets

**Auto-tracking:** Every request's token counts, model, cost (from built-in price map), key, user,
team, and tags are stored in `LiteLLM_SpendLogs` (PostgreSQL).

**Custom pricing:**
```yaml
litellm_params:
  input_cost_per_token: 0.000002
  output_cost_per_token: 0.000006
```
Provider margins (markup) and discounts also configurable.

**Tag-based cost tracking:** Attach `tags` to requests; view spend breakdown per tag. Tag budgets
(Enterprise) enforce hard USD caps per tag:
```yaml
tag_budgets:
  - tag: "cost-center-eng"
    max_budget: 500.0
    budget_duration: "30d"
```

**Provider budget routing:** Cap spending per provider; auto-route away when budget exhausted:
```yaml
router_settings:
  provider_budget_config:
    openai: {budget_limit: 100, time_period: "1d"}
```

**Budget reset periods:** `Xs`, `Xm`, `Xh`, `Xd`, `Xmo`

**End-user tracking:** The `user` field on each request attributes cost to an end-user identifier
without creating a key. `max_end_user_budget` sets a default limit per end-user.

**Spend query API:** Filter by key, team, model, date range. `/spend/report` for analytics (Enterprise).

**Budget alerts:** Soft-budget threshold alerts via Slack webhook before hard limit is hit.

---

## Guardrails

All guardrails run at configurable hooks: `pre_call`, `post_call`, `during_call`, `logging_only`.

| Guardrail | Type | Notes |
|-----------|------|-------|
| LiteLLM Content Filter | Built-in | Regex/keyword matching; no external deps |
| Presidio PII/PHI Masking | External (Presidio containers) | Mask/block SSN, credit cards, phone, email etc. |
| Prompt Injection Detection | Built-in | In-memory detection |
| OpenAI Moderation | External (OpenAI API) | Filters via OpenAI's moderation endpoint |
| LlamaGuard / LLM Guard | External LLM-based | Safety classification |
| Pillar Security | Third-party API | Injection, jailbreak, PII+PCI, secrets |
| Lasso Security | Third-party API | Enterprise content security |
| Secret Detection/Redaction | Enterprise | Masks API keys in logs/callbacks |
| Banned Keywords | Enterprise | Configurable keyword blocklist |

**PII/PHI masking config example:**
```yaml
guardrails:
  - guardrail_name: presidio-pii
    litellm_params:
      guardrail: presidio
      mode: pre_call
      presidio_filter_scope: both   # "input", "output", or "both"
      pii_entities_config:
        SSN: BLOCK
        PHONE_NUMBER: MASK
        EMAIL_ADDRESS: MASK
```

---

## Tag / Team / User Routing

**Tag routing** (preferred, replaces deprecated team-based routing):
- Assign `tags` to deployments in `model_info`
- Request tagged via `x-litellm-tags: free,eu` header or `"tags": ["free"]` in body
- `enable_tag_filtering: true` in `router_settings`
- `"default"` tag acts as fallback for untagged requests

**Four-level tenant hierarchy:**
```
Organization → Team → User → Virtual Key
```
Team budgets cannot exceed org budgets. User budgets cannot exceed team budgets.

**Team creation:** `POST /team/new` with `max_budget`, `budget_duration`, `models`, `tpm_limit`, `rpm_limit`

**Team-to-tag routing (Enterprise):** Teams are assigned tags; members' requests automatically receive team tags — no client-side tag injection needed.

**Roles:** `proxy_admin` (all access), `proxy_admin_viewer` (read-only), `internal_user` (default),
`org_admin` (Enterprise), `team_admin` (Enterprise)

---

## Observability

**Prometheus** (`/metrics` endpoint, ~25 metric families):
- Spend/budget metrics per key/team/user/provider with full label dimensions
- Deployment health: success/failure responses, cooldown state, fallback counts
- Latency histograms: e2e, TTFT, LLM API, Redis overhead
- Rate limit remaining: RPM/TPM per key and model

**Alerting** (24+ alert types via Slack/Discord/Teams webhooks):
- LLM performance: hanging calls, slow calls, failures, outages
- Budget: threshold alerts, daily spend reports
- Region outage: ≥5 failures/min in a region (Enterprise)

**Pre-built callbacks:**
- Langfuse (full LLM tracing with cost)
- Helicone, Lunary, Promptlayer, MLflow, Traceloop/OpenTelemetry
- Datadog: via Prometheus scrape of `/metrics`

**Audit logs (Enterprise):** Who created/modified/deleted any entity (key, team, model, user),
with timestamp and actor, with configurable retention.

---

## Key Differences from OpenRouter

| Aspect | LiteLLM Proxy | OpenRouter |
|--------|---------------|------------|
| **Model count** | 100+ | 300+ |
| **Deployment** | Self-hosted | SaaS |
| **Data residency** | Full on-prem control | Data flows through OpenRouter |
| **Virtual key management** | Full lifecycle: create, rotate, block, expire, alias | Simple API keys |
| **Budget system** | 8-level hierarchy (key/user/team/org/model/global/provider/tag) | Per-key credits |
| **Tag routing** | Route to deployment pools by request tags | No |
| **Provider budget caps** | Auto-skip provider when spend budget exhausted | No |
| **Semantic caching** | Redis-semantic, Qdrant-semantic (configurable threshold) | Prompt caching (exact) |
| **PII masking** | Presidio integration (pre-call scrubbing) | No |
| **Prompt injection detection** | Built-in + third-party integrations | No |
| **MCP Gateway** | Centralized MCP server registry with auth + budgets | No |
| **Prometheus metrics** | Native, ~25 metric families with label dimensions | No |
| **Circuit breaker** | `allowed_fails` + `cooldown_time` per deployment | Implicit provider switching |
| **Traffic mirroring** | Shadow deployments for silent A/B | No |
| **Wildcard routing** | Route `openai/*` without listing models | Not applicable |
| **Custom routing logic** | `CustomRoutingStrategyBase` | Not supported |
| **SSO / RBAC** | Enterprise SAML/OIDC + org/team/user roles | No |
| **Audit logs** | Enterprise: full action log with retention | No |
| **Config-as-code** | YAML `config.yaml`, GitOps friendly | API/UI only |
| **Pricing** | Free open-source + infra costs (~$200-500/mo) | No-markup pay-per-use |
| **Setup time** | 15-30 min | < 5 min |

---

## What We Should Steal for thegent

These LiteLLM features have the highest value for thegent's CLIProxy/routing layer:

### High Priority (Core Provider Aggregation)

1. **Provider budget routing** — `provider_budget_config` per provider with auto-skip when
   exhausted. thegent has per-model cost tracking but no per-provider spend caps that trigger
   routing changes. This is critical for cost governance when mixing free and paid providers.

2. **Virtual key budget hierarchy** — thegent has a single-level cost tracker. LiteLLM's
   8-level hierarchy (key → user → team → org) enables multi-tenant agent deployments where
   different teams/projects have isolated spend caps. Especially relevant for thegent's
   teammate runner isolation model.

3. **Tag-based routing to deployment pools** — thegent routes by model name only. LiteLLM's
   tag routing lets you define multiple deployment pools for the same model name (free tier vs.
   paid tier, EU vs. US region) and route by request/key/team tags. Directly enables thegent's
   multi-tier provider strategy.

4. **Wildcard provider routing** — `openai/*` style config so any new OpenAI-compatible model
   can be routed without code changes. thegent must update `harness_model_mapping.py` and
   `model_metadata.py` for every new model; LiteLLM's wildcard avoids this.

5. **Context window fallbacks** — distinct from general fallbacks. When a request overflows
   one model's context, route to a larger-context variant automatically. thegent's
   `validate_context_window()` only warns; no automatic fallback is triggered.

### Medium Priority (Reliability/Operations)

6. **Per-deployment cooldown (circuit breaker)** — thegent has retry logic but no deployment-level
   cooldown. LiteLLM's `allowed_fails` + `cooldown_time` removes a failing deployment from the pool
   for a configurable period. This prevents continuous hammering of a degraded provider.

7. **Pre-call context window check** — validate that the request will fit before making the API
   call; fail fast with a specific error rather than getting a provider error mid-request. Avoids
   wasted latency on certain-to-fail calls.

8. **Content policy fallbacks** — separate fallback path for moderation rejections vs. errors.
   Important when mixing providers with different content policies.

9. **Traffic mirroring / shadow deployments** — route production traffic to a secondary model
   silently for benchmarking. Useful for validating new models in thegent's catalog before
   promoting them.

### Medium Priority (Observability/Multi-Tenant)

10. **Prometheus metrics with label dimensions** — thegent has basic cost tracking but no
    Prometheus-native metrics. LiteLLM's ~25 metric families with `team`, `end_user`, `model`,
    `api_provider` labels are directly importable by existing infrastructure monitoring.

11. **Per-provider budget Prometheus metric** — `litellm_provider_remaining_budget_metric`
    gives real-time budget burn visibility per provider. thegent's `cost_tracker.py` has daily
    totals but no per-provider remaining budget signal.

12. **Budget reset periods** — LiteLLM supports flexible reset cadences (`30m`, `6h`, `7d`,
    `1mo`). thegent currently uses daily reset only.

### Lower Priority (Guardrails/Security)

13. **PII/PHI masking via Presidio** — Pre-call scrubbing enables GDPR-compliant use of
    cloud LLMs for agent workloads handling user data. No equivalent in thegent today.

14. **Prompt injection detection** — built-in detection as a pre-call guardrail. Relevant for
    any agentic scenario where user-controlled content is passed to the LLM.

15. **MCP gateway with per-key permissions** — LiteLLM's MCP gateway lets you register MCP
    servers and restrict which keys/teams can access which tools. thegent has MCP management
    (`thegent mcp prune`) but not per-key MCP tool access control.

### Lower Priority (Audit/Compliance)

16. **Audit logs** — Who generated/rotated/deleted which key, when, and from which IP.
    Important for enterprise thegent deployments.

17. **Custom key header** — `litellm_key_header_name` lets operators rename the auth header.
    Minor but useful for integrating with enterprise API gateways that use non-standard headers.

18. **Region-aware routing** — Pre-call region check that ensures requests only go to
    deployments in configured regions (EU data residency). Relevant for thegent enterprise.
