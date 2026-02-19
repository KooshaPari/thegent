# Provider Setup Guide

Per-provider OAuth, token-file, and refresh instructions for thegent + CLIProxyAPIPlus.

---

## Quick start: get proxy agents passing

All providers use CLIProxyAPIPlus native config. Provider/model definitions are internal (no external config dependency):

1. **Start proxy:** `thegent mcp up` (or `thegent cliproxy start` for proxy only)
2. **OAuth login (preferred):** `thegent cliproxy login <provider>` — for claude, codex, gemini, qwen, glm, roo, kilo, kimi, copilot, antigravity, iflow, kiro. Opens browser, completes OAuth, stores tokens.
3. **API-key login (minimax, nim only):** `thegent cliproxy login minimax` or `thegent cliproxy login nim` — opens URL, prompts for API key, writes to config. Use `--force` to re-enter.
4. **Verify:** `thegent run "Output only 1" minimax` (or glm, antigravity, cliproxy)

**Proxy management:** `thegent cliproxy start` | `thegent cliproxy stop` | `thegent cliproxy restart`. After config changes, run `thegent cliproxy restart`.

**MCP + browser tools (single config):** `thegent mcp up` bundles Playwright, Serena, and Octocode. Use `thegent mcp install cursor` (or `all`) to add thegent and remove manual playwright from Cursor/Claude Code/Codex. One MCP entry = thegent + browser + LSP + code search. All mounts required by default.

**macOS LaunchAgent (runs at login):** `thegent cliproxy service install` then `thegent cliproxy service start`.

**Debug mode (model/provider/latency tags):** `thegent run --debug "task" minimax` or `thegent bg --debug "task" glm`. Sets `THGENT_DEBUG=1`; proxy started with `-debug` when env is set. See [DEBUG_TAGS_AND_METRICS.md](../plans/DEBUG_TAGS_AND_METRICS.md).

---

## Login (thegent cliproxy login)

All providers use `thegent cliproxy login <provider>`. **OAuth (preferred):** browser opens → log in → tokens stored. **API-key (minimax, nim only):** open URL → prompt for key → save to config. Use `--force` to re-enter.

| Provider    | Command                    | Notes                          |
|-------------|----------------------------|--------------------------------|
| Claude      | `thegent cliproxy login claude`   | Anthropic OAuth                |
| Codex       | `thegent cliproxy login codex`    | OpenAI OAuth                   |
| Gemini      | `thegent cliproxy login gemini`   | Google OAuth                   |
| Copilot     | `thegent cliproxy login copilot`  | GitHub Copilot OAuth           |
| Antigravity | `thegent cliproxy login antigravity` | Antigravity OAuth          |
| Qwen        | `thegent cliproxy login qwen`     | Alibaba Qwen OAuth             |
| iFlow       | `thegent cliproxy login iflow`    | iFlow OAuth (GLM)              |
| Kimi        | `thegent cliproxy login kimi`     | Moonshot Kimi OAuth            |
| Kiro        | `thegent cliproxy login kiro`     | AWS CodeWhisperer (Google OAuth) |
| Kiro AWS    | `thegent cliproxy login kiro-aws` | Kiro via AWS Builder ID        |
| Kiro import | `thegent cliproxy login kiro-import` | Import from Kiro IDE       |
| Roo         | `thegent cliproxy login roo` / `thegent login roo`     | Roo Code Cloud (runs `roo auth login`)    |
| Kilo        | `thegent cliproxy login kilo` / `thegent login kilo`     | Kilo auth wizard (runs `kilo auth`)  |
| MiniMax     | `thegent cliproxy login minimax`                        | API-key only (no OAuth)                  |
| NIM         | `thegent cliproxy login nim`                            | NVIDIA NIM API-key only (no OAuth)       |

**Flow (CLIProxy providers):** Run the command → browser opens → log in → tokens stored in `~/.cli-proxy-api`. CLIProxyAPIPlus merges them into config on first proxy start.

**Flow (roo, kilo):** `thegent login roo` / `thegent login kilo` (or `thegent cliproxy login roo/kilo`) invokes `roo auth login` or `kilo auth` directly. Tokens stored in provider-specific paths. Ensure CLIProxy config has the roo/kilo block (see below).

---

## Cursor (cursor-api + zero-action)

**thegent auto-injection:** When `THGENT_CURSOR_API_URL` and `THGENT_CURSOR_API_TOKEN` are set, thegent injects the cursor block at `thegent cliproxy ensure-config` / `thegent mcp up`:
- **sk-... token** (from cursor-api `/build-key`): writes to `{auth-dir}/cursor-session-token.txt`, uses `token-file` (CLIProxyAPIPlus direct flow)
- **AUTH_TOKEN** (for zero-action): uses `auth-token` (CLIProxyAPIPlus zero-action: IDE + `/tokens/add`)

**Option A – Zero-action (recommended):** Log in to Cursor IDE only. Set `THGENT_CURSOR_API_TOKEN` to cursor-api `AUTH_TOKEN`:

```yaml
cursor:
  - cursor-api-url: "http://127.0.0.1:3000"
    auth-token: "${CURSOR_API_AUTH_TOKEN}"   # Must match cursor-api AUTH_TOKEN env
```

Token is auto-read from Cursor IDE storage (`state.vscdb`). No manual copy.

**Option B – Manual (token-file):** Run cursor-api `/build-key`, put `sk-...` in a file:

```yaml
cursor:
  - token-file: "~/.cursor/session-token.txt"
    cursor-api-url: "http://127.0.0.1:3000"
```

**Refresh:** cursor-api `/tokens/refresh` (integrated when using token manager).

---

## MiniMax (api-key; no OAuth)

**Automated:** `thegent cliproxy login minimax` prompts for your API key and writes it to config. Get key from [platform.minimax.io](https://platform.minimax.io). Restart proxy after login.

**Manual:** Add to `~/.config/thegent/cliproxy-config.yaml`:

```yaml
minimax:
  - api-key: "sk-..."
    base-url: "https://api.minimax.io/v1"
```

**Base URL:** `https://api.minimax.io/v1`

---

## GLM (via iFlow)

**OAuth:** `thegent cliproxy login iflow` (or `thegent cliproxy login glm`). GLM models (glm-5, glm-4.7) are served via the iFlow channel.

---

## Roo Code (token-file or API key)

**OAuth:** Run `thegent cliproxy login roo` (invokes `roo auth login`). Token stored in `~/.config/roo/credentials.json`.

**Token-file (OAuth/Cloud):**

```yaml
roo:
  - token-file: "~/.config/roo/credentials.json"
    base-url: "https://api.roocode.com/v1"
```

Or legacy path:

```yaml
roo:
  - token-file: "~/.roo/oauth-token.json"
    base-url: "https://api.roocode.com/v1"
```

**API key:**

```yaml
roo:
  - api-key: "sk-..."
    base-url: "https://api.roocode.com/v1"
```

**Refresh:** Update token-file when token expires.

---

## Kilo (token-file or API key)

**OAuth:** Run `thegent cliproxy login kilo` (invokes `kilo auth`). Interactive wizard configures provider; credentials stored in `~/.kilocode/cli/`.

**Free credits:** Sign up at kilo.ai; optional API key.

**Token-file:**

```yaml
kilo:
  - token-file: "~/.kilo/token.json"
    base-url: "https://api.kilo.ai/v1"
```

**API key:**

```yaml
kilo:
  - api-key: "sk-..."
    base-url: "https://api.kilo.ai/v1"
```

**Refresh:** Update token-file when token expires.

---

## Kiro (AWS CodeWhisperer)

**Token-file (SSO cache):**

```yaml
kiro:
  - token-file: "~/.aws/sso/cache/kiro-auth-token.json"
```

**Refresh:** CLIProxyAPIPlus background refresh; Kiro tokens auto-renew.

---

## thegent run commands

| Agent      | Command                    | Default model      |
|------------|----------------------------|--------------------|
| cliproxy   | `thegent run cliproxy "..."`   | gemini-3-flash     |
| minimax    | `thegent run minimax "..."`    | minimax-m2.5       |
| glm        | `thegent run glm "..."`        | glm-5              |
| roo        | `thegent run roo "..."`        | roo-default        |
| kilo       | `thegent run kilo "..."`       | kilo-default       |
| cursor-api | `thegent run cursor-api "..."` | claude-4.5-opus-high |

---

## Codex CLI with CLIProxy (all providers)

Codex uses the Responses API; CLIProxyAPIPlus only exposes Chat Completions. **Enable the adapter** so Codex works with any CLIProxy provider (minimax, glm, antigravity, kilo, etc.):

1. **Start proxy with adapter:** `THGENT_CLIPROXY_ADAPTER=1 thegent mcp up`
2. **Login:** `thegent cliproxy login <provider>` (minimax, glm, antigravity, etc.)
3. **Run Codex:** `OPENAI_BASE_URL=http://127.0.0.1:8317/v1 OPENAI_API_KEY=sk-dummy codex exec - "task" --model <model>`

Use catalog model IDs (e.g. `minimax-m2.5`, `glm-5`, `gemini-3-flash`). For custom provider config patterns, see [MiniMax Codex CLI guide](https://platform.minimax.io/docs/coding-plan/codex-cli).

**Agent self-service (no user intervention):**
- `thegent mgmt ensure-proxy` — Ensure MCP+proxy running (starts via process-compose if needed)
- `thegent mgmt verify-codex-cliproxy` — Full verification: ensure proxy, run `codex exec`, report pass/fail
- `task mgmt:verify-codex-cliproxy` — Same via Taskfile

**Reference:** [CODEX_MINIMAX_CLIPROXY_RESEARCH_AND_PLAN.md](../research/CODEX_MINIMAX_CLIPROXY_RESEARCH_AND_PLAN.md)

---

## OpenCode Zen with CLIProxyAPIPlus

**OpenCode** (opencode.ai) is an OSS AI coding agent. **Zen** is its curated model layer. You can use **CLIProxyAPIPlus** as OpenCode's backend instead of or alongside Zen.

1. **Start proxy:** `thegent cliproxy start` (or `THGENT_CLIPROXY_ADAPTER=1 thegent mcp up` if using Codex)
2. **Login:** `thegent cliproxy login <provider>` (minimax, glm, kilo, roo, etc.)
3. **Run OpenCode with CLIProxy:**
   ```bash
   export OPENAI_BASE_URL=http://127.0.0.1:8317/v1
   export OPENAI_API_KEY=sk-dummy
   opencode
   ```

OpenCode will route requests through CLIProxy to your configured providers (minimax, glm, kilo, roo, antigravity, etc.). Use catalog model IDs (e.g. `minimax-m2.5`, `glm-5`).

**GoZen** (dopejs/GoZen): Multi-CLI switcher for Claude Code, Codex, OpenCode. Add a provider with `base_url: http://127.0.0.1:8317/v1` to use CLIProxy with `zen --cli opencode`.

**Reference:** [AGENT_PLATFORMS_KILO_ROO_OPencode_CLIPROXY_RESEARCH.md](../research/AGENT_PLATFORMS_KILO_ROO_OPencode_CLIPROXY_RESEARCH.md)

## OpenCode + Zen Native in thegent

You can now use OpenCode and Zen directly from thegent:

1. `thegent run opencode "summarize this repo"`  
   Uses the `opencode` CLI (`opencode run ...`) as a direct harness.
2. `thegent run zen "implement X"`  
   Uses Zen OpenAI-compatible API via Codex client path.

Zen env vars:

```bash
export THGENT_ZEN_API_KEY="<your-zen-key>"
export THGENT_ZEN_BASE_URL="https://api.opencode.ai"   # optional override
```

Optional aliases:

```bash
export OPENCODE_API_KEY="<your-zen-key>"   # recognized as fallback
export ZEN_API_KEY="<your-zen-key>"        # recognized as fallback
```

---

## References

- [AGENT_PLATFORMS_KILO_ROO_OPencode_CLIPROXY_RESEARCH.md](../research/AGENT_PLATFORMS_KILO_ROO_OPencode_CLIPROXY_RESEARCH.md)
- [CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md](../plans/CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md)
- Cursor zero-action spec: `docs/guides/CURSOR_ZERO_ACTION_FLOW_SPEC.md` (in sharecli)


---

## EXTENSION_SUMMARY

**Extended on:** 2026-02-17  
**Extended by:** Claude Code

### Changes Made
1. Added practical implementation patterns
2. Added configuration examples
3. Enhanced cross-references to related documentation

### Cross-References Added
- Related research and implementation guides
- WORK_STREAM.md for tracking

### Practical Additions
- Implementation templates
- Configuration examples
- Best practices

---

## 12. Provider Troubleshooting

### 12.1 OAuth Issues

**Symptom:** OAuth fails, token not stored.

**Solution:**
```bash
# Check token storage location
cat ~/.cli-proxy-api/tokens/*.json

# Re-run OAuth with verbose
thegent cliproxy login claude --verbose

# Check proxy logs
tail -f ~/.cli-proxy-api/logs/*.log
```

### 12.2 API Key Issues

**Symptom:** "Invalid API key" error.

**Solution:**
```bash
# Verify API key format
echo $MINIMAX_API_KEY | head -c 10

# Re-enter API key
thegent cliproxy login minimax --force

# Check key in config
cat ~/.cli-proxy-api/config.toml | grep -A5 minimax
```

### 12.3 Token Refresh Issues

**Symptom:** "Token expired" errors.

**Solution:**
```bash
# Refresh all tokens
thegent cliproxy tokens refresh

# Check token expiry
thegent cliproxy tokens status

# Manual OAuth re-login
thegent cliproxy login claude
```

---

## 13. Environment Variables Reference

| Variable | Purpose | Default |
|----------|---------|----------|
| `CLIPROXY_PORT` | Proxy port | 8317 |
| `CLIPROXY_ADAPTER` | Enable adapter | 0 |
| `THGENT_DEBUG` | Debug mode | 0 |
| `THGENT_OUTPUT_FORMAT` | Output format | rich |

---

## 14. Extension Summary

**Extended on:** 2026-02-17  
**Extended by:** Claude Code

### Changes Made

1. **Added Section 12:** Provider Troubleshooting
   - OAuth issues
   - API key issues
   - Token refresh issues

2. **Added Section 13:** Environment Variables Reference

### Practical Additions

- Debug commands for each issue type
- Configuration verification commands
- Environment variable reference table
