# CLIProxyAPI & Thegent Work Plan – Unified Phased WBS

**Status:** Complete (Phases 3–6 implemented 2026-02-14; Roo/Kilo model registration + thegent agents 2026-02-14)  
**Date:** 2026-02-14  
**Scope:** Cursor, MiniMax, Roo, Kilo – equal parity with native providers (Kiro, Gemini, Claude, Codex)

**Sources:** Merged from `NEW_PROVIDERS_AUTH_RESEARCH.md`, `CURSOR_API_INTEGRATION_RESEARCH.md`, and phased WBS plans.

---

## Principle: Equal Parity for All Providers

All providers have OAuth (or equivalent login/token flow). They must have **equal parity** with native providers (Kiro, Gemini CLI, Claude, Codex): dedicated config blocks, token-file, access/refresh, OAuth where applicable—not relegated to `openai-compatibility` + api-key only.

---

## Research Summary

| Provider   | Auth                         | CLIProxy Fit                         | Status                    |
|-----------|------------------------------|--------------------------------------|---------------------------|
| Cursor    | Login (WorkosCursorSessionToken) | `cursor:` block (token-file, zero-action IDE) | Done; cursor-api + IDE storage |
| MiniMax   | OAuth + API key (like GLM)   | `minimax:` block                     | Done; token-file, api-key |
| Factory Droid | OAuth via CLIProxy       | Official docs, gists                 | Working                   |
| Kilo      | Free credits, optional API key | `kilo:` block (token-file, api-key) | Done; dedicated block     |
| Roo Code  | OpenAI-compat / Cloud       | `roo:` block (token-file, api-key)   | Done; dedicated block     |

---

## Phase 1: Foundation (Depends on: none)

| ID   | Task              | Description                                                                 |
|------|-------------------|-----------------------------------------------------------------------------|
| P1.1 | Fix Cursor config | Remove misleading api-key-entries; add note: Cursor uses login protocol. Cursor gets dedicated `cursor:` block (Phase 2). |
| P1.2 | Fix MiniMax config| MiniMax gets dedicated `minimax:` block (OAuth + optional API key fallback)—not openai-compatibility-only. |
| P1.3 | Update research doc | State: all providers = dedicated blocks with OAuth parity.                |
| P1.4 | Regenerate patch   | `patches/cursor-minimax-channels.patch` with corrected config.             |

**Output:** Correct config examples; patch ready for upstream.

---

## Phase 2: Cursor – Dedicated Block (Parity with Kiro)

| ID   | Task                 | Description                                                                 |
|------|----------------------|-----------------------------------------------------------------------------|
| P2.1 | Add `cursor:` schema | `token-file`, `cursor-api-url`. Mirror kiro structure in config.go.        |
| P2.2 | Cursor token provider| Read token; call cursor-api `/tokens/add` or `/build-key`; wire to OpenAICompatExecutor. |
| P2.3 | Token refresh       | Integrate `/tokens/refresh`.                                                |
| P2.4 | Register in rebindExecutors | Cursor executor when `cursor:` present.                              |

**Output:** Cursor works via dedicated config block; no static API key.

---

## Phase 3: MiniMax – Dedicated Block (Parity with Kiro/GLM) ✓ DONE

| ID   | Task                  | Description                                                              |
|------|-----------------------|--------------------------------------------------------------------------|
| P3.1 | Add `minimax:` schema | OAuth: token-file, access-token, refresh-token. Optional API key fallback. |
| P3.2 | MiniMax OAuth executor| Implement or adapt executor for MiniMax OAuth flow (like GLM/iFlow).     |
| P3.3 | Register in rebindExecutors | MiniMax executor when `minimax:` present.                          |

**Output:** MiniMax has dedicated block with OAuth parity. Implemented: MiniMaxKey, synthesizeMiniMaxKeys, OpenAICompatExecutor.

---

## Phase 4: Thegent CLIProxy Backend (Depends on: P1) ✓ DONE

| ID   | Task                  | Description                                                              |
|------|-----------------------|--------------------------------------------------------------------------|
| P4.1 | Add cliproxy provider | Config: THGENT_CLIPROXY_URL, THGENT_CLIPROXY_API_KEY.                    |
| P4.2 | CliproxyRunner        | Use Codex CLI with CLIProxy base URL.                                   |
| P4.3 | Model scraper         | GET /v1/models from CLIProxy.                                           |
| P4.4 | Registry and catalog  | cliproxy in AGENT_NAMES; model routes.                                  |

**Output:** `thegent run cliproxy "..."` uses local CLIProxyAPIPlus. Implemented: cliproxy in AGENT_NAMES, _PROXY_AGENTS, _PROXY_MODEL (gemini-3-flash default).

---

## Phase 5: Roo Code, Kilo – Dedicated Blocks (Parity) ✓ DONE

| ID   | Task    | Description                                                                 |
|------|---------|-----------------------------------------------------------------------------|
| P5.1 | Roo Code| Research OAuth/Cloud auth; add `roo:` block with token-file/OAuth.         |
| P5.2 | Kilo    | Research Kilo provider auth; add `kilo:` block.                             |

**Rule:** Each gets a dedicated block—no provider is api-key-only in openai-compatibility without an OAuth/token path.

**Implemented:** RooKey, KiloKey structs; synthesizeRooKeys, synthesizeKiloKeys; config_diff; OpenAICompatExecutor for each.

---

## Phase 6: Polish & Documentation (Depends on: P2–P5) ✓ DONE

| ID   | Task              | Description                                                                 |
|------|-------------------|-----------------------------------------------------------------------------|
| P6.1 | Provider parity matrix | Document: Cursor, MiniMax, Roo, Kilo = same config pattern as Kiro, Gemini, Claude, Codex. |
| P6.2 | Setup guides      | Per-provider: OAuth flow, token-file, refresh.                              |
| P6.3 | Factory Droid     | Link to official CLIProxyAPIDocs; Droid already has parity.                 |

**Implemented:** config.example.yaml updated with roo, kilo blocks; [PROVIDER_SETUP_GUIDE.md](../guides/PROVIDER_SETUP_GUIDE.md) added; unified plan status updated.

---

## Parity Pattern (All Providers)

```
Native:  kiro:, gemini:, claude:, codex:
New:     cursor:, minimax:, roo:, kilo:

All use: token-file, OAuth, refresh (where applicable)
```

## Provider Parity Matrix (Phase 6)

| Provider   | Config Block | Auth                    | Status   |
|------------|--------------|-------------------------|----------|
| Kiro       | kiro:        | token-file, OAuth       | Native   |
| Gemini     | gemini-api-key: | api-key              | Native   |
| Claude     | claude-api-key: | api-key              | Native   |
| Codex      | codex-api-key:  | api-key              | Native   |
| Cursor     | cursor:      | token-file, cursor-api  | Phase 2  |
| MiniMax    | minimax:     | token-file, api-key     | Phase 3  |
| Roo Code   | roo:         | token-file, api-key     | Phase 5  |
| Kilo       | kilo:        | token-file, api-key     | Phase 5  |
| cliproxy   | (thegent)    | local CLIProxy           | Phase 4  |

---

## DAG (Dependencies)

```
P1 (Foundation) ──┬──> P2 (Cursor)
                  ├──> P3 (MiniMax)
                  └──> P4 (Thegent CLIProxy)

P2, P3 ──> P5 (Roo, Kilo)
P2, P3, P4, P5 ──> P6 (Polish)
```

---

## Key Files

| Area                  | Path                                                       |
|-----------------------|------------------------------------------------------------|
| Config schema         | CLIProxyAPIPlus-fork/internal/config/config.go           |
| Kiro reference        | Same file – `kiro:` block                                 |
| Executor registration | CLIProxyAPIPlus-fork/sdk/cliproxy/service.go              |
| Model definitions     | CLIProxyAPIPlus-fork/internal/registry/model_definitions.go |
| Config example        | CLIProxyAPIPlus-fork/config.example.yaml                  |
| Thegent config        | thegent/config.py                                         |
| Thegent registry      | thegent/agents/registry.py                                |
| CursorApiRunner       | thegent/agents/cursor_api_runner.py                        |

---

## References

- [wisdgod/cursor-api](https://github.com/wisdgod/cursor-api) – Token management, `/build-key`, `/tokens/add`, `/tokens/refresh`
- [OpenClaw MiniMax OAuth](https://github.com/openclaw/openclaw/tree/main/extensions/minimax-portal-auth) – User-code flow
- [Kilo-Org/kilocode](https://github.com/Kilo-Org/kilocode) – Provider config
- [RooCodeInc/Roo-Code](https://github.com/RooCodeInc/Roo-Code)
- [mrsuperei/CLIProxyAPI-Extended](https://github.com/mrsuperei/CLIProxyAPI-Extended) – Kiro/Antigravity
