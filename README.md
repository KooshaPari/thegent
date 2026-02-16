# Thegent

Unified agent orchestration CLI for Factory skills and droids.

## Install

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent && uv sync
uv run thegent --help
```

Or from project root:
```bash
uv run --project /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent thegent --help
```

Install third-party bundles with the manifest system:
```bash
thegent install --bundle web-stack
thegent install --bundle hooks --bundle-manifest /path/to/third_party_bundles.json
thegent install --bundle all
```

## Usage

```bash
# Foreground run (prompt first, agent second; cwd inferred from .git, .factory, or pyproject.toml)
thegent run "List top-level directories" gemini

# Model-first: route by model, no agent needed (prefer_direct)
thegent run -M gemini-3-flash "Say 1"
thegent run -M claude-sonnet-4 --provider antigravity "Analyze risks"

# Explicit cwd, read-only mode
thegent run -d /path/to/project -m read-only "Analyze structure" gemini

# Stream full raw output live (no post-parse buffering)
thegent run -f --live -d /path/to/project "Do X and report progress" cursor-agent

# Run droid (generic; use --droid for specific droid)
thegent run "Expand idea X" droid
thegent run --droid plan-orchestrator "Create WBS" droid

# List agents and droids
thegent list-agents
thegent list-droids

# Background session lifecycle (no external bash wrapper needed)
thegent bg -d /path/to/project --owner my-scope "Long task" cursor-agent
thegent ps --owner my-scope
thegent status <session-id>
thegent logs <session-id> --follow
thegent logs <session-id> --follow --timeout 30
thegent wait <session-id> --timeout 300
thegent stop <session-id>
thegent stop <session-id> --wind-down --grace 30
thegent stop <session-id> --force
```

## Providers

- **gemini, codex, copilot, claude, antigravity, minimax, glm, roo, kilo:** Codex via our CLIProxyAPIPlus (starts proxy on first run; OAuth: `thegent cliproxy login <provider>` for claude, codex, gemini, copilot, antigravity, qwen, roo, kilo; minimax use config—see [Provider Setup Guide](docs/guides/PROVIDER_SETUP_GUIDE.md))
- **cursor-agent:** Direct Cursor CLI

For all proxy-backed agents: install [CLIProxyAPIPlus](https://github.com/router-for-me/CLIProxyAPIPlus/releases) (e.g. `CLIProxyAPIPlus_*_darwin_arm64.tar.gz` -> extract to `~/.local/bin`), then `thegent cliproxy login gemini` (or claude, codex, copilot, antigravity, roo, kilo). **GLM** is native (GLM-5); no extra config. **Minimax**: see [Provider Setup Guide](docs/guides/PROVIDER_SETUP_GUIDE.md).

Notes:
- CLI is subcommand-only. Args: `run PROMPT [AGENT]` (prompt first; agent optional when `-M` given).
- Model-first: `thegent run -M <model> "prompt"` routes to best provider. `thegent list-models --by-model` shows routing.
- Use `thegent run --help` and `thegent bg --help` for command-specific options.

Background sessions:
- Session metadata/logs default to `~/.cache/thegent/sessions`
- Override with `THGENT_SESSION_DIR=/path`

## cursor-agent

Thegent invokes the Cursor agent via `cursor-agent` (or `cursor` if `cursor-agent` is not on PATH). Set `THGENT_CURSOR_AGENT_CMD` if the CLI is elsewhere:

```bash
export THGENT_CURSOR_AGENT_CMD=/path/to/cursor-agent
# or, when using Cursor IDE's cursor CLI:
export THGENT_CURSOR_AGENT_CMD=/path/to/cursor
```

See `.env.example` for other overrides.

## sitback (Sitback Agent)

Start Claude Code with a pre-configured Sitback Agent persona (dashboard, terminal list, sessions):

```bash
thegent sitback                    # minimax, dashboard on startup
thegent sitback -a kilo            # sibling via kilo
thegent sitback --profile full     # full dashboard (plugins, harness)
thegent sitback --tmux             # run in dedicated tmux session
thegent sitback --skill agent-orchestra  # override skill
thegent sitback --no-dashboard    # manual mode
```

**Precondition:** `thegent serve` (or `thegent mcp up`) for FastMCP tools. Falls back to CLI if MCP is down.

CLI dashboard (no MCP needed): `thegent sitback-dashboard`, `--profile light|medium|full`, `--refresh 5` for live mode. Plugins: `~/.claude/sitback-plugins/` (see `docs/guides/SITBACK_PLUGINS.md`).

## clode (legacy CLI proxy shims)

`thegent clode` provides a Claude-code-compatible bridge with explicit provider routing:

```bash
thegent clode                          # raw claude session via nim
thegent clode nim                       # explicit nim backend
thegent clode openrouter                # explicit openrouter backend
thegent clode kilo                      # explicit kilo backend
thegent clode zai                       # explicit zai backend
thegent clode minimax                   # explicit minimax backend
thegent clode glm --policy round_robin      # policy-based GLM balancing (default)
thegent clode glm --policy cheapest         # choose cheapest configured backend in offer set
thegent clode glm --prefer kilo             # force a specific backend in GLM offer set
thegent clode glm --prefer openrouter       # force OpenRouter backend in GLM alias mode
thegent clode max                        # alias for openrouter backend
```

To install executable compatibility wrappers used by droids and legacy scripts:

```bash
thegent clode install-links --force
```

This writes:

- `clode` → `thegent clode`
- `claudeglm` → `thegent clode glm`
- `claudemax` → `thegent clode max`

The shims send routing hints through `ANTHROPIC_API_KEY` when invoking Claude Code:

- `glm:round_robin` (default for `glm`)
- `glm:cheapest`
- `glm:prefer_proxy`
- `glm:prefer_direct`
- `glm:failover`
- `kilo`, `zai`, `nim`, `minimax`, `openrouter` can be forced directly

You can also inspect available droids with:

```bash
thegent list-droids                # list project/discovery droids
thegent list-droids --cd /path/to/project
```

## MCP (Cursor, Claude Code, Codex, Droid)

Expose thegent as an MCP server so Cursor, Claude Code, Codex, and droids can invoke agents as tools.

**1. Install thegent into client configs:**
```bash
thegent mcp install cursor          # ~/.cursor/mcp.json
thegent mcp install claude-code     # ~/.claude.json
thegent mcp install codex           # ~/.codex/mcp.json
thegent mcp install droid           # .factory/mcp.json (cwd)
thegent mcp install all             # all of the above
```

**2. Run the HTTP server (required for clients to connect):**
```bash
# One-shot (foreground)
thegent serve

# Or as launchd service (macOS, starts at login)
thegent mcp service install
thegent mcp service start
thegent mcp service status   # Running (HTTP OK) | Not running
thegent mcp service stop
```

Default URL: `http://127.0.0.1:3847/mcp`. Override with `THGENT_MCP_HOST`, `THGENT_MCP_PORT`, or `--url` when installing.

## Tests

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent && uv sync --extra dev
uv run pytest tests/ -v                    # all tests (including integration/slow)
uv run pytest tests/ -m "not integration and not slow"  # fast only (skip real agent calls)
uv run pytest tests/ -m integration        # integration only (calls gemini, etc.)
```
