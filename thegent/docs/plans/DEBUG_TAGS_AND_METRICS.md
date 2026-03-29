# Debug Tags and Metrics (Transient Response Tags)

**Status:** Design
**Date:** 2026-02-15
**Scope:** Transient tags around responses (model, provider, latency, tps) so the user can tell which model produced output; `--debug` flag to trigger on CLIProxy API or LiteLLM router.

---

## Goal

1. **Transient tags** — Wrap or prefix responses with metadata so the user can identify: model, provider, latency, tps, other debug metrics.
2. **--debug flag** — When set, enable debug output (tags, metrics) on CLIProxy API or LiteLLM router.

---

## Reference: How Other Projects Do It

| Project | Pattern | Location |
|---------|---------|----------|
| **API/argisroute** | `X-RateLimit-*` headers, metadata in responses | wrappers, rate limiting |
| **API/docs** | `metadata: { model, provider, processing_time_ms, token_usage }` | AGENT_SECURITY_COMPREHENSIVE_PART2 |
| **trace** | cliproxy config (routing, model_mappings) | `trace/backend/configs/cliproxy.yaml` |
| **CLIProxyAPI** | Bifrost integration, provider routing | API/research/CLIProxyAPI |

**Common pattern:** Response headers (`X-Model`, `X-Provider`, `X-Latency-Ms`) or metadata block in response body.

---

## Proposed Design

### 1. Response Tags (Where to Inject)

| Layer | Option | Pros | Cons |
|-------|--------|------|-----|
| **CLIProxyAPIPlus** | Add headers to proxied response | Single source; all clients benefit | Requires proxy modification |
| **CLIProxyAPIPlus** | Prefix first stream chunk with `<!-- model: X \| provider: Y \| latency_ms: Z -->` | Visible in stream; no client change | Pollutes content when debug on |
| **thegent** | Log to stderr when `--debug` | No proxy change | Only when thegent is caller |
| **LiteLLM** | `litellm.callbacks` or response metadata | Rich metrics | Only when LiteLLM is used |

**Recommendation:** CLIProxyAPIPlus adds `X-Response-Model`, `X-Response-Provider`, `X-Latency-Ms`, `X-TPS-1m` to response headers when `-debug` flag is set. Optional: prefix first chunk with HTML comment for visibility in Cursor/Claude Code if headers are not displayed.

### 2. --debug Flag Flow

```
User: thegent run --debug "task" minimax
  → thegent sets THGENT_DEBUG=1, passes X-Debug: 1 to proxy
  → Proxy (if -debug or X-Debug) adds response headers + logs metrics

User: Cursor/Claude Code with provider=minimax
  → Proxy started with -debug: adds headers to all responses
  → User sees tags in response (if client displays headers) or via prefix
```

### 3. CLIProxyAPIPlus Changes (Fork)

- Add `-debug` flag to server: when set, for each proxied request:
  - Log: `model`, `provider`, `latency_ms`, `tps_1m` (from metrics)
  - Add response headers: `X-Response-Model`, `X-Response-Provider`, `X-Latency-Ms`, `X-TPS-1m`
  - Optionally: if `X-Debug: 1` request header, enable for that request only (no global -debug)

### 4. LiteLLM (Future)

- `litellm.set_verbose=True` or callback to log model, provider, latency
- Response metadata in completion object
- When used as router: same header pattern as proxy

### 5. thegent CLI

- `thegent run --debug` → set `THGENT_DEBUG=1`, pass `X-Debug: 1` in requests to proxy
- When thegent is the direct caller (not Cursor): log metrics to stderr after each response if debug

---

## Implementation Phases

| Phase | Task | Status |
|-------|------|--------|
| 1 | Add `--debug` to `thegent run`, `thegent bg`; set `THGENT_DEBUG=1`; proxy gets `-debug` when env set | ✓ Done |
| 2 | CLIProxyAPIPlus: add `-debug` flag; when set, add response headers | Pending (fork; thegent already passes `-debug` when THGENT_DEBUG=1) |
| 3 | CLIProxyAPIPlus: optional response prefix `<!-- model: X \| provider: Y \| latency_ms: Z -->` when debug | Pending (fork) |

**Note:** If the fork does not yet support `-debug`, the proxy may fail to start when THGENT_DEBUG=1. Implement `-debug` in the fork to add response headers (X-Response-Model, X-Response-Provider, X-Latency-Ms, X-TPS-1m).
| 4 | Document in PROVIDER_SETUP_GUIDE, CLAUDE.md | ✓ Done |

---

## Metrics to Expose

| Metric | Source | Header |
|--------|--------|--------|
| model | Resolved model alias | `X-Response-Model` |
| provider | Provider name (minimax, glm, nim, etc.) | `X-Response-Provider` |
| latency_ms | Request latency | `X-Latency-Ms` |
| tps_1m | Rolling TPS from metrics | `X-TPS-1m` |
| cost_per_1k | From GET /v1/metrics/providers | `X-Cost-Per-1k` (optional) |

---

## References

- [OPENROUTER_STYLE_ROUTING_AND_CLIPROXY.md](./OPENROUTER_STYLE_ROUTING_AND_CLIPROXY.md) — metrics endpoint, routing
- [PROVIDER_MODEL_BEHAVIOR.md](../reference/PROVIDER_MODEL_BEHAVIOR.md) — minimax/glm constraints
- API/research/CLIProxyAPI — existing proxy patterns
