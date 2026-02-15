# Provider Setup Guide

Per-provider OAuth, token-file, and refresh instructions for thegent + CLIProxyAPIPlus.

---

## Quick start: get proxy agents passing

All providers use CLIProxyAPIPlus native config (no factory config merge):

1. **Start proxy:** `thegent mcp up`
2. **OAuth (antigravity, cliproxy, glm):** `thegent cliproxy login antigravity` or `thegent cliproxy login iflow` (GLM)
3. **MiniMax:** `thegent cliproxy login minimax` prompts for API key and writes it to config (no OAuth; automated).
4. **Verify:** `thegent run "Output only 1" minimax` (or glm, antigravity, cliproxy)

---

## OAuth Providers (thegent cliproxy login)

These providers use `thegent cliproxy login <provider>`. Matches CLIProxyAPIPlus default providers.

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

**Flow (CLIProxy providers):** Run the command → browser opens → log in → tokens stored in `~/.cli-proxy-api`. CLIProxyAPIPlus merges them into config on first proxy start.

**Flow (roo, kilo):** `thegent login roo` / `thegent login kilo` (or `thegent cliproxy login roo/kilo`) invokes `roo auth login` or `kilo auth` directly. Tokens stored in provider-specific paths. Ensure CLIProxy config has the roo/kilo block (see below).

---

## Cursor (cursor-api + zero-action)

**Option A – Zero-action (recommended):** Log in to Cursor IDE only. Configure:

```yaml
cursor:
  - cursor-api-url: "http://127.0.0.1:3000"
    auth-token: "${CURSOR_API_AUTH_TOKEN}"   # Must match cursor-api AUTH_TOKEN env
```

Token is auto-read from Cursor IDE storage (`state.vscdb`). No manual copy.

**Option B – Manual:** Run cursor-api `/build-key`, put `sk-...` in a file:

```yaml
cursor:
  - token-file: "~/.cursor/session-token.txt"
    cursor-api-url: "http://127.0.0.1:3000"
```

**Refresh:** cursor-api `/tokens/refresh` (integrated when using token manager).

---

## MiniMax (api-key; no OAuth)

**Automated:** `thegent cliproxy login minimax` prompts for your API key and writes it to config. Get key from platform.minimax.io. Restart proxy after login.

**Manual:** Add to `~/.config/thegent/cliproxy-config.yaml`:

```yaml
minimax:
  - api-key: "sk-..."
    base-url: "https://api.minimax.chat/v1"
```

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

## References

- [CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md](../plans/CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md)
- Cursor zero-action spec: `docs/guides/CURSOR_ZERO_ACTION_FLOW_SPEC.md` (in sharecli)
