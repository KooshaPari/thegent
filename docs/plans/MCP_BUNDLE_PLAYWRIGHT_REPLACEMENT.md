# MCP Bundle: thegent + Browser Tools (Replace Manual Playwright)

**Goal:** Bundle thegent MCP with browser/Playwright capabilities so Cursor, Claude Code, and Codex need only one MCP entry. Remove manual `@playwright/mcp` configs.

**References:**
- [flyto-core](https://github.com/flytohub/flyto-core) — 329 modules, 38 browser tools, 6 MCP tools (search_modules + execute_module pattern)
- [gofastmcp.com: mounting](https://gofastmcp.com/servers/providers/mounting) — `mcp.mount(create_proxy(...))`
- [gofastmcp.com: proxy](https://gofastmcp.com/servers/providers/proxy) — `create_proxy(url|config)`
- [Serena](https://github.com/oraios/serena) — LSP-based code tools (required mount)

---

## 1. Current State

| Client        | Config Path                          | Manual Playwright? |
|---------------|--------------------------------------|--------------------|
| Cursor        | `~/.cursor/mcp.json`, `.cursor/mcp.json` | Yes (`@playwright/mcp`) |
| Claude Code   | `~/.claude.json`                     | Yes (if configured) |
| Codex         | `~/.codex/mcp.json`, `~/.codex/config.toml` | Yes (timeout issues) |

**thegent MCP:** `http://127.0.0.1:3847/mcp` (HTTP) or stdio via `thegent mcp-stdio`.

---

## 2. Proposed Architecture: Single MCP, Mounted Sub-Servers

```
┌─────────────────────────────────────────────────────────────────┐
│  thegent MCP (FastMCP) — single process, port 3847               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ thegent tools   │  │ Playwright      │  │ Serena, Octocode │  │
│  │ run, bg, ps…    │  │ browser.*      │  │ (required)        │  │
│  │                 │  │                │  │                  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│         │ mount(proxy)      │ mount(proxy)       │                 │
└─────────┼───────────────────┼───────────────────┼─────────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
    Cursor / Claude Code / Codex — ONE config: thegent only
```

**Clients configure:** `thegent` only. No separate playwright, flyto-core, or serena entries.

---

## 3. Implementation Options

### Option A: Mount flyto-core via FastMCP proxy (recommended)

- **flyto-core** exposes 6 MCP tools; 329 modules behind `search_modules` + `execute_module` (low context bloat).
- **Mount:** `mcp.mount(create_proxy("http://localhost:8333/mcp"), namespace="browser")` when flyto-core HTTP server is running.
- **Or:** `create_proxy({"command": "python", "args": ["-m", "core.mcp_server"]})` — subprocess per session.

```python
# mcp_server.py (conceptual) — FastMCP 3.0+ API
from fastmcp import FastMCP
from fastmcp.server import create_proxy

mcp = FastMCP("thegent")

# Option 1: Mount flyto-core HTTP (when flyto serve runs on 8333)
mcp.mount(create_proxy("http://localhost:8333/mcp"), namespace="browser")

# Option 2: Mount flyto-core via subprocess (stdio)
flyto_config = {
    "mcpServers": {
        "default": {"command": "python", "args": ["-m", "core.mcp_server"]}
    }
}
mcp.mount(create_proxy(flyto_config), namespace="browser")

# Option 3: Mount @playwright/mcp (npm)
playwright_config = {
    "mcpServers": {
        "default": {"command": "npx", "args": ["-y", "@playwright/mcp@latest"]}
    }
}
mcp.mount(create_proxy(playwright_config), namespace="browser")
```

### Option B: Mount @playwright/mcp via proxy

- Proxy the existing `@playwright/mcp` npm package so it runs inside thegent’s process tree.
- **Downside:** Playwright MCP has 38+ tools, higher schema footprint; flyto-core’s 6-tool pattern is leaner.

### Option C: Embed browser tools in thegent (no external mount)

- Implement a minimal `browser_launch`, `browser_navigate`, `browser_click` etc. directly in thegent using Playwright.
- **Pro:** No extra process. **Con:** Maintenance burden, duplicates flyto-core.

---

## 4. Install Flow: Remove Playwright, Use thegent Only

**Before (current):**
```json
// .cursor/mcp.json
{
  "mcpServers": {
    "thegent": { "url": "http://127.0.0.1:3847/mcp" },
    "playwright": { "command": "npx", "args": ["@playwright/mcp@latest"] }
  }
}
```

**After (proposed):**
```json
{
  "mcpServers": {
    "thegent": { "url": "http://127.0.0.1:3847/mcp" }
  }
}
```

**`thegent mcp install` (default: `--replace-playwright`):**
- Writes `thegent` to Cursor, Claude Code, Codex configs.
- By default removes playwright entry from configs (use `--keep-playwright` to retain).
- `thegent mcp up` sets `THGENT_MCP_MOUNT_PLAYWRIGHT=1` — browser tools bundled.

```bash
thegent mcp install cursor
# or for all clients (removes playwright by default):
thegent mcp install all
# to keep manual playwright: thegent mcp install all --keep-playwright
```

**Browser tools via thegent:**
- Set `THGENT_MCP_MOUNT_PLAYWRIGHT=1` or `THGENT_MCP_MOUNT_FLYTO=1` before `thegent serve`.
- For flyto-core: run `flyto serve` (port 8333) or set `THGENT_FLYTO_URL`.

---

## 5. Multi-Tenant Single Process

**Goal:** One thegent MCP process serves multiple clients (Cursor, Claude Code, Codex) with shared tool registry.

| Aspect | Current | Proposed |
|--------|---------|----------|
| Process | One process (thegent serve) | Same |
| Clients | Cursor, Claude Code, Codex each connect to same URL | Same |
| Sub-servers | None | Playwright, Serena, Octocode (all required) — mounted as providers |
| Session isolation | Per HTTP request | FastMCP `create_proxy` gives session isolation per request |

**Skills/plugins:** Convert to mounted MCP servers or in-process tools:
- `skills/agent-orchestra` — already uses thegent; no change.
- `skills/browser-navigation` — could map to flyto-core `browser.*` or thegent-mounted tools.
- Third-party bundles — use `create_proxy` with config from `third_party_bundles.json`.

---

## 6. Implementation Checklist

- [x] Add optional `flyto-core` / `playwright` mount to `mcp_server.py` (config: `THGENT_MCP_MOUNT_FLYTO`, `THGENT_MCP_MOUNT_PLAYWRIGHT`)
- [x] Add `thegent mcp install --replace-playwright` to remove playwright from client configs (now default)
- [x] Add Serena mount (`THGENT_MCP_MOUNT_SERENA`) for LSP code tools
- [x] Enable playwright bundle by default in process-compose (`THGENT_MCP_MOUNT_PLAYWRIGHT=1`)
- [ ] Document `pip install flyto-core[browser]` and `playwright install chromium` for browser tools
- [ ] Document `flyto serve` for HTTP mode (optional; or use stdio subprocess)
- [ ] Test: Cursor, Claude Code, Codex with only thegent config

---

## 7. Serena & Multi-Tenant Plugins

**Serena** ([oraios/serena](https://github.com/oraios/serena)) — LSP-based code tools (goto-definition, find-references, etc.). Required; enabled by default:

```bash
THGENT_MCP_MOUNT_SERENA=1 thegent serve
# or add to process-compose environment
```

Uses `uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide`.

**Skills/plugins → multi-tenant single process:**
- **browser-navigation** skill: Map to `browser_*` tools from flyto-core or playwright mount.
- **Third-party bundles** (`third_party_bundles.json`): Each bundle can define `mcpServers` config; thegent mounts them at install time.
- **Octocode, software-planning-mcp, next-devtools**: Can remain as separate client entries, or be mounted into thegent for a single-process setup (one thegent = all tools).
- **flyto-core** (300+ tools): Alternative to playwright; set `THGENT_MCP_MOUNT_FLYTO=1` and run `flyto serve`.

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| flyto-core license (Source Available) | Use only for personal/internal; document commercial license need |
| Startup latency | Mount lazily or on first tool call; cache `list_tools` |
| Context bloat | flyto-core uses 6 tools only; avoid mounting 300+ tools directly |
| Playwright timeout | Single thegent process; no per-client playwright subprocess |

---

## 9. References

- [flyto-core README](https://github.com/flytohub/flyto-core)
- [FastMCP mounting](https://gofastmcp.com/servers/providers/mounting)
- [FastMCP proxy](https://gofastmcp.com/servers/providers/proxy)
- [Serena MCP](https://github.com/oraios/serena)
- [thegent mcp_manage.py](../src/thegent/mcp_manage.py)
- [thegent install.py](../src/thegent/install.py)
