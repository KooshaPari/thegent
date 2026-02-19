# LiteLLM + CLIProxyAPIPlus + Bifrost Harmony

**Status:** Design  
**Date:** 2026-02-15  
**Scope:** Make LiteLLM, CLIProxyAPIPlus (and optionally Bifrost) work harmoniously for model routing and provider load balancing.

**See also:** [CATALOG_CLIPROXY_FORK_ALIGNMENT.md](./CATALOG_CLIPROXY_FORK_ALIGNMENT.md) — catalog providers vs fork capabilities (nim, kilo, etc.).

---

## Research Summary (Codex + Web)

### Bifrost (maximhq/bifrost)

- **Type:** Go-based AI gateway, 2.4k stars
- **Claims:** 50x faster than LiteLLM, <100 µs overhead at 5k RPS, 15+ providers
- **Features:** Unified OpenAI-compat API, adaptive load balancer, cluster mode, guardrails, MCP gateway, semantic caching, custom plugins
- **Deployment:** NPX, Docker, Go SDK (embedded)
- **Gaps for thegent:** No Python SDK; separate process; model alias abstraction less mature than LiteLLM; 15–21 providers vs LiteLLM 100+

### LiteLLM

- **Type:** Python library + proxy server
- **Features:** Router class (in-process, no proxy needed); model_name → multiple deployments; 100+ providers; fallbacks, cost tracking, load balancing
- **Gaps for thegent:** thegent shells out to CLI tools (claude, codex, gemini) — LiteLLM makes API calls itself. Can't replace agentic execution.

### Recommendation: Option A + Future LiteLLM

- **Best now:** Option A — CLIProxyAPIPlus as single proxy (8317), fix base URL, align catalog with fork
- **Best long-term:** LiteLLM Router as in-process library for direct-API providers; CLIProxyAPIPlus for OAuth/CLI-backed providers
- **Bifrost:** Out for thegent — no Python SDK, separate process, fewer providers; 50x speed irrelevant at agent-scale (<50 concurrent calls)

---

## Current State

| Component | Location | Role |
|-----------|----------|------|
| **thegent** | `thegent/` | Agent orchestration, MCP server (3847), clode/claudemax shims |
| **CLIProxyAPIPlus-fork** | `../CLIProxyAPIPlus-fork/` | Chat proxy (8317), OAuth, openai-compatibility, minimax/zai. Go project, build: `go build -o cli-proxy-api-plus ./cmd/server` |
| **LiteLLM** | pheno-sdk, zen-mcp-server, agentapi | Multi-provider client, fallback chains, model discovery |
| **Bifrost** | (Go project with extensions) | Alternative proxy/gateway with extension system |

---

## Problem

1. **claudemax** points to MCP (3847) but MCP is for tools, not chat. Chat proxy is CLIProxyAPIPlus (8317).
2. Claude Code detects `ANTHROPIC_API_KEY` from env and prompts; thegent wants to use provider token for routing.
3. LiteLLM (used in pheno-sdk, zen-mcp-server) and CLIProxyAPIPlus are separate stacks; no unified routing.
4. Bifrost (Go + extensions) could be an alternative or complement.

---

## Architecture Options

### Option A: CLIProxyAPIPlus as Single Proxy (Current + Fix)

- **claudemax** → `ANTHROPIC_BASE_URL=http://127.0.0.1:8317/v1` (not 3847)
- **ANTHROPIC_API_KEY** = provider token (openrouter, minimax, zai) for routing
- CLIProxyAPIPlus handles model select → provider routing
- Factory config (`~/.factory/config.json`) credentials copied into cliproxy config

**Pros:** Minimal change, fork already exists  
**Cons:** CLIProxyAPIPlus has its own provider model; LiteLLM remains separate

---

### Option B: LiteLLM Proxy as Front Door, CLIProxyAPIPlus as Backend

```
Claude Code → LiteLLM Proxy (e.g. 4000) → CLIProxyAPIPlus (8317) or direct providers
```

- LiteLLM Proxy: model routing, fallback chains, load balancing
- CLIProxyAPIPlus: OAuth providers (antigravity, iflow, kiro), openai-compatibility (minimax, zai)
- LiteLLM config routes `minimax/*` → `http://127.0.0.1:8317/v1`, `openrouter/*` → OpenRouter, etc.

**Pros:** LiteLLM fallback chains, unified config  
**Cons:** Two proxies, config sync complexity

---

### Option C: Bifrost Extension for CLIProxy/LiteLLM Bridge

- Bifrost (Go) has extension system
- Extension: bridge to CLIProxyAPIPlus or LiteLLM
- thegent configures Bifrost as proxy; Bifrost extensions handle provider routing

**Pros:** Extensible, single Go binary  
**Cons:** Bifrost integration TBD; may need new extension

---

## Recommended Path: Option A + Config Alignment

1. **Fix claudemax base URL:** `CLIProxyAPIPlus` (8317) not MCP (3847) for chat.
2. **Ensure env isolation:** `ANTHROPIC_API_KEY` from thegent overrides shell env; consider `--dangerously-skip-permissions` to avoid Claude Code key prompt.
3. **Provider definitions:** Internal JSON; credentials via `thegent cliproxy login <provider>`.
4. **Fork path:** `start_proxy.py` looks for `../CLIProxyAPIPlus-fork/cli-proxy-api-plus`; ensure `THGENT_CLIPROXY_BINARY` or build from fork.

---

## LiteLLM + CLIProxyAPIPlus Sync (Future)

If LiteLLM is used for routing (e.g. pheno-sdk, zen-mcp-server):

- **LiteLLM config** can proxy to CLIProxyAPIPlus:
  ```yaml
  model_list:
    - model_name: minimax-m2.5
      litellm_params:
        model: openai/minimax-m2.5
        api_base: http://127.0.0.1:8317/v1
        api_key: sk-dummy
  ```
- **Shared config source:** `~/.factory/config.json` → both CLIProxyAPIPlus (via thegent copy) and LiteLLM (via config generator).

---

## Bifrost Integration (If Applicable)

- Bifrost: Go project with extensions
- **Extension idea:** `bifrost-cliproxy` – forwards requests to CLIProxyAPIPlus
- **Extension idea:** `bifrost-litellm` – forwards to LiteLLM Proxy
- Enables Bifrost as single gateway with pluggable backends

---

## Implementation Checklist

- [ ] `clode_main._get_claude_env`: use `cliproxy_port` (8317) for chat, not `mcp_port` (3847)
- [ ] Verify `ANTHROPIC_API_KEY` override in subprocess env
- [ ] Document `THGENT_CLIPROXY_BINARY` for fork: `../CLIProxyAPIPlus-fork/cli-proxy-api-plus` (or built binary path)
- [ ] **Catalog–fork alignment:** Ensure nim routes work — fork has no native "nim"; needs openai-compatibility. See CATALOG_CLIPROXY_FORK_ALIGNMENT.md.
- [ ] (Optional) LiteLLM config generator from `~/.factory/config.json`
- [ ] (Optional) Bifrost extension for CLIProxy bridge
