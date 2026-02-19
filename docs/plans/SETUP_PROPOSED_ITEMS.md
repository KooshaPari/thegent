# thegent Setup: Proposed Hooks, Plugins, Skills, MCP & Docs

**Goal:** Complete thegent setup for all tooling — not just MCPs. Includes dex links, cliproxy, MCP mounts (Octocode, Serena, Playwright), and a curated list of items to incorporate from the web.

---

## 0. Research: Breadth & Depth

### 0.1 MCP Ecosystem

| Layer | Source | Description |
|-------|--------|-------------|
| **Registry** | [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io/) | Official MCP server registry |
| **Reference Servers** | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time |
| **Awesome List** | [wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers) | 100+ community servers; submit at [mcpservers.org/submit](https://mcpservers.org/submit) |
| **Python SDK** | [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | `pip install mcp` |
| **FastMCP** | [jlowin/fastmcp](https://github.com/jlowin/fastmcp) | `pip install fastmcp` — thegent uses this |

**Official Reference Servers (npx):**
- `@modelcontextprotocol/server-fetch` — Web content fetching
- `@modelcontextprotocol/server-filesystem` — Secure file ops
- `@modelcontextprotocol/server-github` — GitHub PRs, issues, repos
- `@modelcontextprotocol/server-memory` — Persistent knowledge graph
- `@modelcontextprotocol/server-sequential-thinking` — Chain-of-thought
- `@modelcontextprotocol/server-time` — Time/timezone

**Notable Community MCPs (by category):**
- **Browser:** Playwright, Browserbase, Hyperbrowser, mcp-chrome, Cua (Computer-Use Agent)
- **Code/Dev:** Octocode (GitHub/code search), Serena (LSP), JetBrains, CircleCI, Currents (Playwright tests)
- **Data:** ClickHouse, Supabase, Convex, Chroma, MotherDuck
- **Deploy:** Vercel, Railway, Cloudflare, Google Cloud Run
- **Docs:** Context7, Firecrawl, FetchSERP
- **Planning:** software-planning-mcp, next-devtools (Next.js)

### 0.2 Claude Code Ecosystem

| Repo | Stars | Purpose |
|------|-------|---------|
| [everything-claude-code](https://github.com/affaan-m/everything-claude-code) | 46k+ | Production agents, skills, hooks, commands, rules, MCP configs |
| [awesome-claude-code](https://github.com/awesome-claude-code/awesome-claude-code) | 23k+ | Curated list of Claude Code resources |
| [claude-code-infrastructure-showcase](https://github.com/affaan-m/claude-code-infrastructure-showcase) | — | Infrastructure patterns |
| [buildwithclaude](https://github.com/buildwithclaude) | — | Build patterns |
| [claude-mem](https://github.com/claude-mem) | — | Memory/context |
| [oh-my-opencode](https://github.com/oh-my-opencode) | — | OpenCode configs |

**everything-claude-code structure (37 skills, 13 agents, 31 commands):**
```
agents/           # planner, architect, tdd-guide, code-reviewer, security-reviewer, etc.
skills/           # 37 skills: tdd-workflow, backend-patterns, django-*, springboot-*, golang-*, etc.
commands/         # /plan, /tdd, /e2e, /code-review, /instinct-status, /pm2, /multi-*, etc.
hooks/            # memory-persistence, strategic-compact (session-start, session-end, pre-compact)
rules/            # common/, typescript/, python/, golang/
mcp-configs/      # github, firecrawl, supabase, memory, sequential-thinking, vercel, railway, etc.
```

**ECC MCP configs (mcp-servers.json):**
- github, firecrawl, supabase, memory, sequential-thinking
- vercel (HTTP), railway, cloudflare-docs/workers-builds/bindings/observability (HTTP)
- clickhouse (HTTP), context7, magic, filesystem

**ECC tools:** AgentShield (security scan), Skill Creator (git history → skills), Continuous Learning v2 (instincts)

### 0.3 Cursor Ecosystem

| Path | Purpose |
|------|---------|
| `.cursor/rules/` | Project rules (BMAD, custom) |
| `.cursor/agents/` | Agent definitions |
| `.cursor/commands/` | Slash commands |
| `.cursor/skills/` | Skill definitions |
| MCP config | Cursor settings → MCP servers |

### 0.4 Codex Ecosystem

| Component | Purpose |
|-----------|---------|
| Responses API | `/v1/responses` (HTTP + WebSocket) for Codex |
| Cliproxy adapter | Translates Responses ↔ Chat Completions |
| Backend | Port 8318; adapter 8317 |

### 0.5 Hooks & Automation

| Tool | URL | Purpose |
|------|-----|---------|
| pre-commit | [pre-commit.com](https://pre-commit.com/) | Git hooks framework (Python) |
| husky | [typicode.github.io/husky](https://typicode.github.io/husky) | Node git hooks |
| lefthook | [evilmartians/lefthook](https://github.com/evilmartians/lefthook) | Fast git hooks (Rust) |

**ECC hooks:** `session-start`, `session-end`, `pre-compact`, `suggest-compact`, `evaluate-session` (Node.js, cross-platform)

### 0.6 Documentation References

| Doc | URL |
|-----|-----|
| FastMCP Providers | [gofastmcp.com/servers/providers/overview](https://gofastmcp.com/servers/providers/overview) |
| FastMCP Mounting | [gofastmcp.com/servers/providers/mounting](https://gofastmcp.com/servers/providers/mounting) |
| Serena clients | [oraios.github.io/serena/02-usage/030_clients](https://oraios.github.io/serena/02-usage/030_clients.html) |
| ECC Shortform Guide | [the-shortform-guide.md](https://github.com/affaan-m/everything-claude-code/blob/main/the-shortform-guide.md) |
| ECC Longform Guide | [the-longform-guide.md](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md) |

### 0.7 Extended Research (Breadth & Depth)

#### Hooks — Deep Dive

**ECC Hook Input Schema (stdin JSON):**
```typescript
interface HookInput {
  tool_name: string;  // "Bash", "Edit", "Write", "Read"
  tool_input: { command?, file_path?, old_string?, new_string?, content? };
  tool_output?: { output? };  // PostToolUse only
}
```

**ECC Hook Scripts (scripts/hooks/):**
- `session-start.js` — Load context, detect package manager
- `session-end.js` — Persist session state
- `pre-compact.js` — Save state before compaction
- `suggest-compact.js` — Suggest /compact at intervals
- `evaluate-session.js` — Extract patterns (continuous learning)
- `check-console-log.js` — Stop: audit modified files
- `post-edit-format.js` — Prettier on Edit
- `post-edit-typecheck.js` — tsc --noEmit on .ts/.tsx
- `post-edit-console-warn.js` — Warn on console.log

**ECC Hook Recipes (from hooks/README.md):**
- Warn on TODO/FIXME comments
- Block files >800 lines
- Auto-format Python with ruff
- Require test file alongside new source files

**Async Hooks:** `"async": true, "timeout": 30` — run in background, cannot block.

**Exit Codes:** 0 = continue; 2 = block (PreToolUse only).

#### MCP — High-Impact Additions

| MCP | Stars | URL | Purpose |
|-----|-------|-----|---------|
| **Figma-Context-MCP** | 13k | [GLips/Figma-Context-MCP](https://github.com/GLips/Figma-Context-MCP) | Figma layout info for Cursor |
| **cursor-talk-to-figma-mcp** | 6.3k | [grab/cursor-talk-to-figma-mcp](https://github.com/grab/cursor-talk-to-figma-mcp) | Cursor ↔ Figma read/modify |
| **fastapi_mcp** | 11.5k | [tadata-org/fastapi_mcp](https://github.com/tadata-org/fastapi_mcp) | Expose FastAPI as MCP tools |
| **git-mcp** | 7.6k | [idosal/git-mcp](https://github.com/idosal/git-mcp) | Remote MCP for any GitHub project |
| **browser-tools-mcp** | 7k | [AgentDeskAI/browser-tools-mcp](https://github.com/AgentDeskAI/browser-tools-mcp) | Browser logs in Cursor |
| **Browser MCP** | 5.8k | [BrowserMCP/mcp](https://github.com/BrowserMCP/mcp) | Control browser via MCP |
| **unity-mcp** | 6k | [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) | Unity Editor bridge |
| **dbhub** | 2.1k | [bytebase/dbhub](https://github.com/bytebase/dbhub) | Zero-dep DB MCP (Postgres, MySQL, SQLite) |
| **claude-context** | 5.3k | [zilliztech/claude-context](https://github.com/zilliztech/claude-context) | Code search, full codebase context |
| **grepai** | 1.2k | [yoanbernabeu/grepai](https://github.com/yoanbernabeu/grepai) | Semantic search & call graphs (local) |

#### Skills — Official Scopes & Collections

**Codex Skill Scopes:**
- REPO: `$CWD/.codex/skills`, `$REPO_ROOT/.codex/skills`
- USER: `~/.codex/skills`
- ADMIN: `/etc/codex/skills`
- SYSTEM: Bundled (skill-creator, plan)

**Official Skill Sources:**
- [anthropics/skills](https://github.com/anthropics/skills) — docx, xlsx, pptx, pdf
- [openai/skills](https://github.com/openai/skills) — Codex catalog
- [huggingface/skills](https://github.com/huggingface/skills) — hf_dataset_creator, hf_model_evaluation, hf-llm-trainer

**awesome-agent-skills (heilcheng, 2.2k★):** Curated skills for Claude, Codex (proxy API), VS Code, Antigravity. Categories: Document Processing, Development, Data, Integration, Collaboration, Security, Advanced.

**ComposioHQ awesome-claude-skills (35k★):** 500+ automation skills (Composio integrations): Airtable, Slack, GitHub, Notion, Google, Salesforce, etc. Each `*-automation/` dir = one integration.

#### Plugins & Workflows — Breadth

**awesome-claude-code categories:**
- Agent Skills (AgentSys, Superpowers, Trail of Bits, Fullstack Dev, etc.)
- Workflows (AB Method, RIPER, Claude Code PM, Agentic Workflow Patterns)
- Lifecycle (awesome-ralph, ralph-orchestrator, ralph-wiggum-bdd)
- Tooling (cc-tools, recall, Rulesync, claude-code-tools, claudekit)
- Hooks (see ECC)
- Slash-Commands (Version Control, Code Analysis, Context Loading, CI/Deployment)
- CLAUDE.md (Language-Specific, Domain-Specific, Project Scaffolding)

**AgentSys (avifenesh, 399★):** 12 plugins, 41 agents, 27 skills — task-to-production, PR management, drift detection, multi-agent review. For Claude Code, OpenCode, Codex.

**claude-codex-settings (fcakyon, 419★):** Battle-tested skills, commands, hooks, agents, MCP — GitHub, Azure, MongoDB, Tavily, Playwright, Context7.

#### Tooling — Config & Session Management

| Tool | URL | Purpose |
|------|-----|---------|
| **Rulesync** | [dyoshikawa/rulesync](https://github.com/dyoshikawa/rulesync) | Generate rules, MCP, commands for AI agents; convert Claude↔others |
| **claude-rules-doctor** | [nulone/claude-rules-doctor](https://github.com/nulone/claude-rules-doctor) | Detect dead .claude/rules/ (paths: globs) |
| **ClaudeCTX** | [foxj77/claudectx](https://github.com/foxj77/claudectx) | Switch entire Claude Code config with one command |
| **recall** | [zippoxer/recall](https://github.com/zippoxer/recall) | Full-text search Claude sessions; Enter to resume |
| **claude-code-tools** | [pchalasani/claude-code-tools](https://github.com/pchalasani/claude-code-tools) | Session continuity, Rust/Tantivy session search, tmux-cli, safety hooks |
| **cc-tools** | [Veraticus/cc-tools](https://github.com/Veraticus/cc-tools) | Go hooks: linting, testing, statusline |
| **claude-starter-kit** | [serpro69/claude-starter-kit](https://github.com/serpro69/claude-starter-kit) | Claude Code + Serena + Task Master config templates |

#### CLIProxy / Codex Integration

| Repo | Stars | Purpose |
|------|-------|---------|
| **CLIProxyAPI** | 10.7k | [router-for-me/CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) | Wrap Codex (proxy API), Claude Code as OpenAI-compatible API |
| **proxypal** | 905 | [heyhuynhgiabuu/proxypal](https://github.com/heyhuynhgiabuu/proxypal) | Desktop app for AI subscriptions + any coding tool |
| **awesome-agent-skills** | 2.2k | [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) | Skills for Claude, Codex (proxy API), VS Code |

### 0.8 Additional Research (OpenCode, Windsurf/Cline, Ralph, Skills)

#### OpenCode & Antigravity Ecosystem

| Repo | Stars | Purpose |
|------|-------|---------|
| **opencode-antigravity-auth** | 8.4k | [NoeFabris/opencode-antigravity-auth](https://github.com/NoeFabris/opencode-antigravity-auth) | OAuth: OpenCode → Antigravity; use Codex (proxy API) instead of native Gemini |
| **peon-ping** | 2.2k | [PeonPing/peon-ping](https://github.com/PeonPing/peon-ping) | Warcraft III Peon voice notifications for Claude Code, Codex, Cursor, OpenCode |
| **skillshare** | 480 | [runkids/skillshare](https://github.com/runkids/skillshare) | Sync skills across Claude Code, OpenClaw, OpenCode, Codex, Cursor |
| **antigravity-skills** | 247 | [guanyang/antigravity-skills](https://github.com/guanyang/antigravity-skills) | Full-stack, planning, multimedia skills for Antigravity, OpenCode, Codex |
| **oh-my-opencode-slim** | 1.5k | [alvinunreal/oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim) | Slimmed oh-my-opencode, lower token usage |
| **opencode-bar** | 157 | [opgginc/opencode-bar](https://github.com/opgginc/opencode-bar) | Token usage tracker for OpenCode |
| **opencode-mystatus** | 193 | [vbgate/opencode-mystatus](https://github.com/vbgate/opencode-mystatus) | Check AI subscription quotas (OpenAI, Zhipu, Antigravity) |
| **agentrules-architect** | 105 | [trevor-nichols/agentrules-architect](https://github.com/trevor-nichols/agentrules-architect) | AGENTS.md/CLAUDE.md generator for Codex, Claude Code, Cursor, Windsurf, OpenCode |

#### Windsurf & Cline Ecosystem

| Repo | Stars | Purpose |
|------|-------|---------|
| **mcpm.sh** | 889 | [pathintegral-institute/mcpm.sh](https://github.com/pathintegral-institute/mcpm.sh) | CLI MCP package manager & registry; search, configure, router, profiles |
| **magic-mcp** | 4.3k | [21st-dev/magic-mcp](https://github.com/21st-dev/magic-mcp) | v0-like UI components in Cursor/Windsurf/Cline |
| **cipher** | 3.5k | [campfirein/cipher](https://github.com/campfirein/cipher) | Memory layer for Cursor, Codex, Claude Code, Windsurf, Cline |
| **DevDocs** | 2k | [cyberagiinc/DevDocs](https://github.com/cyberagiinc/DevDocs) | Free, private tech docs MCP for Cursor, Windsurf, Cline |
| **memory-bank-mcp** | 861 | [alioshr/memory-bank-mcp](https://github.com/alioshr/memory-bank-mcp) | Remote memory (Cline Memory Bank–inspired) for Cursor, Windsurf |
| **rulebook-ai** | 572 | [botingw/rulebook-ai](https://github.com/botingw/rulebook-ai) | Consistent rules for Codex (proxy API), Cursor, Roo Code, Cline, Windsurf, Claude Code |
| **context-engineering-kit** | 470 | [NeoLabHQ/context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) | Plugin marketplace for Claude Code, OpenCode, Cursor, Windsurf, Cline |
| **Feishu-MCP** | 438 | [cso1z/Feishu-MCP](https://github.com/cso1z/Feishu-MCP) | Feishu/Lark docs for Cursor, Windsurf, Cline |
| **ai-prompts** | 1k | [instructa/ai-prompts](https://github.com/instructa/ai-prompts) | Curated prompts for Cursor Rules, Cline, Windsurf, Codex (proxy API) |
| **BifrostMCP** | 201 | [biegehydra/BifrostMCP](https://github.com/biegehydra/BifrostMCP) | VSCode extension: Find Usages, Rename for Cursor, Windsurf, Cline |

#### Lifecycle Loop — Autonomous Development

**Reference:** [ghuntley.com/ralph](https://ghuntley.com/ralph), [ClaytonFarr/ralph-playbook](https://github.com/ClaytonFarr/how-to-ralph-wiggum)

**Three phases, two prompts, one loop:**
1. **Define Requirements** — JTBD → specs per topic (`specs/*.md`)
2. **Planning** — Gap analysis (specs vs code) → `IMPLEMENTATION_PLAN.md` only
3. **Building** — Implement from plan, commit, update plan

**Core loop:**
```bash
while :; do cat PROMPT.md | claude -p --dangerously-skip-permissions ; done
```
Works with `claude`, `amp`, `codex`, `opencode`. Swap `PROMPT_plan.md` / `PROMPT_build.md` for mode.

**Key files:** `loop.sh`, `PROMPT_plan.md`, `PROMPT_build.md`, `AGENTS.md`, `IMPLEMENTATION_PLAN.md`, `specs/*.md`

**Implementations:** gru (ralph.md), ralph-wiggum-marketer (ECC plugin), ralph-sentry-fixer, ralph-with-claude-code-and-linear, KLIEBHAN/ralph-loop, webmatze/ralph_loop_claude_template.

#### Skill-Installer & Skill-Creator (Codex/Claude)

| Concept | Purpose |
|--------|---------|
| **skill-creator** | Built-in: bootstrap new skills from scratch; `$skill-creator` in Codex |
| **skill-installer** | Built-in: install curated skills from GitHub; `$skill-installer create-plan` |
| **Locations** | REPO: `$CWD/.codex/skills`, USER: `~/.codex/skills`, ADMIN: `/etc/codex/skills` |
| **Docs** | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills), [support.claude.com creating-custom-skills](https://support.claude.com/en/articles/12512198-creating-custom-skills) |

**Implementations:** tnez/dot-agents, VTCode (vtcode-core), PromptHub, plurigrid/asi, generalaction/emdash.

### 0.9 Additional Research (Cursor, Multi-Agent, Rules Mapping)

#### Cursor Directory & Rules Ecosystem

| Resource | URL | Purpose |
|----------|-----|---------|
| **cursor.directory** | [cursor.directory](https://cursor.directory/) | 72k+ members; rules, MCPs, generate, jobs, board |
| **directories** | [leerob/directories](https://github.com/leerob/directories) (3.9k★) | Cursor Directory source; rules index at `packages/data/src/rules/` |
| **awesome-cursorrules** | [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) | Curated Cursor rules |
| **Agnxi.com** | — | Directory of 10k+ Agent Skills for Cursor, Claude Code, Windsurf |

**Cross-tool rules mapping (forge):**

| Tool | Rules File | Commands/Workflows | Skills |
|------|------------|--------------------|--------|
| Claude Code | CLAUDE.md | .claude/commands/ | .claude/skills/ |
| Codex (proxy API) | — | (replaces native Antigravity/Gemini) | — |
| Cursor | .cursorrules | .cursor/rules/ | .cursor/skills/ |
| Windsurf | .windsurfrules | .windsurf/workflows/ | .windsurf/skills/ |
| Kilo Code | AGENTS.md | .kilocode/workflows/ | .kilocode/skills/ |
| OpenCode | AGENTS.md | .opencode/commands/ | .opencode/skills/ |

#### Multi-Agent Orchestration (Claude Code, Codex, OpenCode)

| Repo | Stars | Purpose |
|------|-------|---------|
| **agents** | 28.7k | [wshobson/agents](https://github.com/wshobson/agents) | Multi-agent orchestration for Claude Code |
| **swarm** | 21k | [openai/swarm](https://github.com/openai/swarm) | OpenAI multi-agent framework |
| **deer-flow** | 20k | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | SuperAgent harness: research, code, create |
| **adk-python** | 17.7k | [google/adk-python](https://github.com/google/adk-python) | Agent Development Kit (Python) |
| **agent-framework** | 7.2k | [microsoft/agent-framework](https://github.com/microsoft/agent-framework) | Build, orchestrate AI agents (Python, .NET) |
| **oh-my-claudecode** | 6.4k | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) | Teams-first multi-agent for Claude Code |
| **cursor-talk-to-figma-mcp** | 6.3k | [grab/cursor-talk-to-figma-mcp](https://github.com/grab/cursor-talk-to-figma-mcp) | Cursor ↔ Figma read/modify |
| **myclaude** | 2.3k | [cexll/myclaude](https://github.com/cexll/myclaude) | Multi-agent (Claude Code, Codex (proxy API), OpenCode) |
| **multi-agent-shogun** | 881 | [yohey-w/multi-agent-shogun](https://github.com/yohey-w/multi-agent-shogun) | Samurai hierarchy (shogun→karo→ashigaru) for Claude Code |
| **Mysti** | 886 | [DeepMyst/Mysti](https://github.com/DeepMyst/Mysti) | Claude Code + Codex brainstorm in VS Code |

#### Awesome MCP — Notable Additions

| MCP | Purpose |
|-----|---------|
| **1mcpserver** | MCP of MCPs; remote discovery at mcp.1mcpserver.com |
| **Cua** | Computer-Use Agent (CUA) MCP server |
| **Currents** | Playwright test failures from Currents.dev |
| **Context 7** | Up-to-date docs for Cursor prompts |
| **mcpservers.org** | Submit new MCPs (awesome-mcp-servers uses this) |

#### FastMCP Mounting Pattern

```python
from fastmcp import FastMCP
from fastmcp.server import create_proxy
from fastmcp.transports import NpxStdioTransport

mcp = FastMCP("Orchestrator")
mcp.mount(
    create_proxy(NpxStdioTransport(package="@modelcontextprotocol/server-github")),
    namespace="github"
)
```

### 0.10 Templates, Tooling & Extended Items

#### Templates & Project Scaffolds

| Repo | Stars | Purpose |
|------|-------|---------|
| **ECC examples** | — | [examples](https://github.com/affaan-m/everything-claude-code/tree/main/examples): CLAUDE.md for SaaS Next.js, Django API, Go, Rust |
| **cherry-studio** | 39.9k | [CherryHQ/cherry-studio](https://github.com/CherryHQ/cherry-studio) | AI productivity studio; 300+ assistants; Claude Code, Codex, OpenCode |
| **meridian** | 134 | [markmdev/meridian](https://github.com/markmdev/meridian) | Zero-config Claude Code setup; task scaffolding, structured memory, TDD |
| **fulling** | 2.4k | [FullAgent/fulling](https://github.com/FullAgent/fulling) | Full-stack AI agent (Next.js, Claude, shadcn, PostgreSQL, Kubernetes) |
| **crystal** | 2.9k | [stravu/crystal](https://github.com/stravu/crystal) | Parallel Codex/Claude Code sessions in git worktrees |
| **project-guidelines-example** | — | ECC skills/ | Template for project-specific skills |

#### Tooling — Token, Context, Session Management

| Tool | Stars | Purpose |
|------|-------|---------|
| **tokscale** | 696 | [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale) | Token usage tracking: OpenCode, Claude Code, Codex (proxy API), Cursor, AmpCode, Factory |
| **OpenContext** | 383 | [0xranx/OpenContext](https://github.com/0xranx/OpenContext) | Personal context store; Codex/Claude/OpenCode with Skills; Tauri desktop app |
| **c0ntextKeeper** | 53 | [Capnjbrown/c0ntextKeeper](https://github.com/Capnjbrown/c0ntextKeeper) | Context preservation; 7 hooks, 187 semantic patterns, 3 MCP tools |
| **mcp-memory-service** | 1.3k | [doobidoo/mcp-memory-service](https://github.com/doobidoo/mcp-memory-service) | Automatic context memory for Claude, Cursor, 13+ AI tools |
| **claude-cognitive** | 438 | [GMaN1911/claude-cognitive](https://github.com/GMaN1911/claude-cognitive) | Working memory for Claude Code; persistent context, multi-instance coordination |
| **task-orchestrator** | 155 | [jpicklyk/task-orchestrator](https://github.com/jpicklyk/task-orchestrator) | MCP task orchestration; persistent project tracking; Cursor, Windsurf |
| **claude-squad** | 6k | [smtg-ai/claude-squad](https://github.com/smtg-ai/claude-squad) | Manage Claude Code, Aider, Codex, OpenCode, Amp in one place |
| **ccpm** | 7.3k | [automazeio/ccpm](https://github.com/automazeio/ccpm) | Project management for Claude Code; GitHub Issues + git worktrees |
| **ruler** | 2.5k | [intellectronica/ruler](https://github.com/intellectronica/ruler) | Apply same rules to Claude Code, Codex, Cursor, Aider, Windsurf |

#### Tooling — Memory & Knowledge

| Tool | Stars | Purpose |
|------|-------|---------|
| **cognee** | 12.3k | [topoteretes/cognee](https://github.com/topoteretes/cognee) | Knowledge engine for AI agent memory |
| **honcho** | 356 | [plastic-labs/honcho](https://github.com/plastic-labs/honcho) | Memory library for stateful agents |
| **nexus** | 300 | [nexi-lab/nexus](https://github.com/nexi-lab/nexus) | Shared heartbeat for agents and humans |

#### More MCP Servers (High-Impact)

| MCP | Stars | Purpose |
|-----|-------|---------|
| **notebooklm-mcp** | 912 | [PleasePrompto/notebooklm-mcp](https://github.com/PleasePrompto/notebooklm-mcp) | NotebookLM MCP; Claude Code, Codex research with grounded, citation-backed answers |
| **apple-docs-mcp** | 893 | [kimsungwhee/apple-docs-mcp](https://github.com/kimsungwhee/apple-docs-mcp) | Apple Developer docs; iOS/macOS/SwiftUI/UIKit, WWDC, Swift/ObjC APIs for Cursor, Claude |
| **Microsoft Learn MCP** | 1.4k | [MicrosoftDocs/mcp](https://github.com/MicrosoftDocs/mcp) | Official Microsoft Learn MCP; real-time docs & code samples for LLMs, Codex (proxy API) |
| **home-assistant-vibecode-agent** | 440 | [Coolver/home-assistant-vibecode-agent](https://github.com/Coolver/home-assistant-vibecode-agent) | Home Assistant MCP; vibe-code and manage HA from Cursor, Claude Code, VS Code |
| **mcp-gateway-registry** | 448 | [agentic-community/mcp-gateway-registry](https://github.com/agentic-community/mcp-gateway-registry) | Enterprise MCP Gateway & Registry; OAuth, dynamic tool discovery, unified access |
| **context7** | 45.8k | [upstash/context7](https://github.com/upstash/context7) | Up-to-date code docs for LLMs, Cursor |
| **github-mcp-server** | 27k | [github/github-mcp-server](https://github.com/github/github-mcp-server) | Official GitHub MCP |
| **chrome-devtools-mcp** | 25.6k | [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Chrome DevTools for coding agents |
| **n8n-mcp** | 13.5k | [czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp) | Build n8n workflows from Claude Code, Cursor, Windsurf |
| **Skill_Seekers** | 9.6k | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | Convert docs, GitHub, PDFs → Claude skills; MCP server |
| **mcp-use** | 9.2k | [mcp-use/mcp-use](https://github.com/mcp-use/mcp-use) | Easiest way to interact with MCP servers; custom agents |
| **IBM mcp-context-forge** | 3.3k | [IBM/mcp-context-forge](https://github.com/IBM/mcp-context-forge) | MCP Gateway & Registry; central tools/resources/prompts |
| **excel-mcp-server** | 3.3k | [haris-musa/excel-mcp-server](https://github.com/haris-musa/excel-mcp-server) | Excel file manipulation |
| **markdownify-mcp** | 2.4k | [zcaceres/markdownify-mcp](https://github.com/zcaceres/markdownify-mcp) | Convert almost anything to Markdown |
| **arxiv-mcp-server** | 2.2k | [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) | Search and analyze arXiv papers |
| **kubernetes-mcp-server** | 1.2k | [containers/kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server) | Kubernetes and OpenShift |
| **mysql_mcp_server** | 1.1k | [designcomputer/mysql_mcp_server](https://github.com/designcomputer/mysql_mcp_server) | Secure MySQL interaction |
| **mcp-server-qdrant** | 1.2k | [qdrant/mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant) | Qdrant vector DB |
| **mcp-neo4j** | 899 | [neo4j-contrib/mcp-neo4j](https://github.com/neo4j-contrib/mcp-neo4j) | Neo4j graph DB |
| **jupyter-mcp-server** | 896 | [datalayer/jupyter-mcp-server](https://github.com/datalayer/jupyter-mcp-server) | Jupyter MCP |

#### More Hooks & Context Automation

| Source | Hooks / Features |
|--------|------------------|
| **c0ntextKeeper** | 7 hooks, 187 semantic patterns, 3 MCP tools; never lose work to compaction |
| **ECC memory-persistence** | session-start, session-end, pre-compact, suggest-compact, evaluate-session |
| **ECC strategic-compact** | Manual compaction suggestions |
| **ECC check-console-log** | Block on console.log in TS/JS |
| **ECC post-edit-format** | Prettier on Edit |
| **ECC post-edit-typecheck** | tsc --noEmit on .ts/.tsx |

#### More Skills & Skill Creation

| Source | Purpose |
|--------|---------|
| **Skill_Seekers** | Docs, GitHub repos, PDFs → Claude skills; conflict detection |
| **ECC /skill-create** | Local git history → SKILL.md |
| **ECC Skill Creator GitHub App** | 10k+ commits, auto-PRs, team sharing |
| **ECC instinct-import/export** | Share learned patterns |
| **ECC evolve** | Cluster instincts into skills |

#### Other Notable Items

| Category | Item | Purpose |
|----------|------|---------|
| **IDE** | codecompanion.nvim (6.1k★) | AI coding in Neovim; Claude Code, Codex (proxy API) |
| **MCP curriculum** | mcp-for-beginners (14.4k★) | Microsoft MCP fundamentals; .NET, Java, TS, Python, Rust |
| **MCP registry** | modelcontextprotocol/registry (6.4k★) | Community MCP server registry |
| **Activepieces** | 20.8k★ | ~400 MCP servers; AI workflow automation |
| **n8n** | 174k★ | Workflow automation; MCP client/server |

### 0.11 Awesome Lists, Guides & GitHub Collections

#### Primary Awesome / Curated Lists

| Collection | Stars | URL | Scope |
|------------|-------|-----|-------|
| **awesome-claude-code** | 23.9k | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Skills, hooks, slash-commands, agents, CLAUDE.md, tooling |
| **awesome-claude-skills** | 7.2k | [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | Claude Skills, resources, workflows |
| **VoltAgent awesome-agent-skills** | 7.2k | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 300+ skills; Codex (proxy API), Antigravity, Cursor, OpenCode |
| **awesome-claude** | 996 | [tonysurfly/awesome-claude](https://github.com/tonysurfly/awesome-claude) | All things Anthropic Claude |
| **awesome-claude-plugins** | 1.3k | [ComposioHQ/awesome-claude-plugins](https://github.com/ComposioHQ/awesome-claude-plugins) | Plugins: commands, agents, hooks, MCP |
| **awesome-claude-code-plugins** | 478 | [ccplugins/awesome-claude-code-plugins](https://github.com/ccplugins/awesome-claude-code-plugins) | Slash commands, subagents, MCP, hooks |
| **awesome-claude-code-toolkit** | 477 | [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | 135 agents, 35 skills, 42 commands, 120 plugins, 19 hooks |
| **heilcheng awesome-agent-skills** | 2.2k | [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) | Claude, Codex (proxy API), VS Code |
| **skillmatic awesome-agent-skills** | 151 | [skillmatic-ai/awesome-agent-skills](https://github.com/skillmatic-ai/awesome-agent-skills) | Agent Skills architecture |
| **awesome-claude-code-sub-agents** | 130 | [supatest-ai/awesome-claude-code-sub-agents](https://github.com/supatest-ai/awesome-claude-code-sub-agents) | Specialised Claude Code sub-agents |

#### AI Coding & Vibe Coding Guides

| Guide | Stars | URL | Scope |
|-------|-------|-----|-------|
| **ai-guide** | 6.9k | [liyupi/ai-guide](https://github.com/liyupi/ai-guide) | AI resource大全; Vibe Coding; Cursor, MCP, RAG |
| **aicodeguide** | 2.1k | [automata/aicodeguide](https://github.com/automata/aicodeguide) | Roadmap to start coding with AI |
| **awesome-ai-coding-tools** | 1.5k | [ai-for-developers/awesome-ai-coding-tools](https://github.com/ai-for-developers/awesome-ai-coding-tools) | Curated AI-powered coding tools |
| **awesome-vibe-coding-guide** | 299 | [analyticalrohit/awesome-vibe-coding-guide](https://github.com/analyticalrohit/awesome-vibe-coding-guide) | 10x Vibe Coder; Claude Code, Cursor, Codex (proxy API), Windsurf |
| **Awesome-Vibecoding-Guide** | 448 | [ClavixDev/Awesome-Vibecoding-Guide](https://github.com/ClavixDev/Awesome-Vibecoding-Guide) | Commercial projects; AI-assisted code |
| **AI-Coding-Style-Guides** | 471 | [lidangzzz/AI-Coding-Style-Guides](https://github.com/lidangzzz/AI-Coding-Style-Guides) | Coding style for Vibe Coding, SWE-Agents |
| **awesome-ai-coding-techniques** | 317 | [inmve/awesome-ai-coding-techniques](https://github.com/inmve/awesome-ai-coding-techniques) | Claude Code, Codex (proxy API), Cursor; EN/ES/DE |
| **vibe-coding-for-dummies** | 347 | [cporter202/vibe-coding-for-dummies](https://github.com/cporter202/vibe-coding-for-dummies) | Beginner guide; Firebase Studio, Cursor |

#### Lifecycle & Autonomous Loops

| Collection | Stars | URL |
|------------|-------|-----|
| **awesome-ralph** | 723 | [snwfdhmp/awesome-ralph](https://github.com/snwfdhmp/awesome-ralph) |
| **ralph-playbook** | — | [ClaytonFarr/how-to-ralph-wiggum](https://github.com/ClaytonFarr/how-to-ralph-wiggum) |

#### Claude Code–Specific Guides & Docs

| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **Claude Code Ultimate Guide** | — | [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) | Beginner→power user; templates; quizzes |
| **Claude Code Handbook** | — | [nikiforovall.blog/claude-code-rules](https://nikiforovall.blog/claude-code-rules/) | Best practices, tips, plugins |
| **Claude Code Tips** | — | [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) | 35+ tips; voice, system prompt, containers |
| **Claude Code System Prompts** | — | [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) | All Claude Code system prompt parts |
| **Claude Code Repos Index** | — | [danielrosehill/Claude-Code-Repos-Index](https://github.com/danielrosehill/Claude-Code-Repos-Index) | 75+ Claude Code repos |
| **Claude Code Documentation Mirror** | — | [ericbuess/claude-code-docs](https://github.com/ericbuess/claude-code-docs) | Anthropic docs mirror |
| **claude-code-docs** | — | [costiash/claude-code-docs](https://github.com/costiash/claude-code-docs) | Docs with full-text search |

#### Cursor, Prompts & Rules

| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **prompts.chat** | 145k | [f/prompts.chat](https://github.com/f/prompts.chat) | Awesome ChatGPT Prompts; share, discover, collect prompts; self-host; Claude, Codex (proxy API) |
| **ai-prompts** | 1k | [instructa/ai-prompts](https://github.com/instructa/ai-prompts) | Cursor Rules, Cline, Windsurf, Codex (proxy API) |
| **cursor.directory** | — | [cursor.directory](https://cursor.directory/) | Rules, MCPs, generate, jobs |
| **directories** | 3.9k | [leerob/directories](https://github.com/leerob/directories) | Cursor Directory source |
| **awesome-ai-system-prompts** | 5.2k | [dontriskit/awesome-ai-system-prompts](https://github.com/dontriskit/awesome-ai-system-prompts) | System prompts for ChatGPT, Claude, etc. |
| **llms-txt-hub** | 698 | [thedaviddias/llms-txt-hub](https://github.com/thedaviddias/llms-txt-hub) | AI-ready docs; llms.txt standard |
| **awesome-devtools** | 622 | [devtoolsd/awesome-devtools](https://github.com/devtoolsd/awesome-devtools) | Cursor, Antigravity, dev tools |

#### OpenCode, Codex & Multi-Client

| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **oh-my-opencode** | 31.7k | [code-yeongyu/oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) | Best agent harness; Claude Code, Codex, OpenCode |
| **cc-switch** | 18.5k | [farion1231/cc-switch](https://github.com/farion1231/cc-switch) | All-in-one: Claude Code, Codex (proxy API), OpenCode |
| **AionUi** | 16k | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) | Cowork; Codex (proxy API), Claude Code, OpenCode, Qwen |
| **agent-of-empires** | 653 | [njbrake/agent-of-empires](https://github.com/njbrake/agent-of-empires) | Claude Code, OpenCode, Codex (proxy API); tmux, worktrees |
| **codexia** | 435 | [milisp/codexia](https://github.com/milisp/codexia) | GUI for Codex CLI + Claude Code; FileTree, prompts, worktrees |

#### Workflow & Agentic Patterns

| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **dify** | 129k | [langgenius/dify](https://github.com/langgenius/dify) | Production-ready agentic workflow platform; RAG, MCP, low-code orchestration |
| **firecrawl** | 82k | [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | Web Data API for AI; turn websites into LLM-ready markdown or structured data |
| **ragflow** | 73k | [infiniflow/ragflow](https://github.com/infiniflow/ragflow) | Open-source RAG engine; RAG + Agent; MCP; document parsing, deep research |
| **open-webui** | 124k | [open-webui/open-webui](https://github.com/open-webui/open-webui) | User-friendly AI interface; Ollama, OpenAI; MCP, RAG, self-hosted |
| **agentic-workflow-patterns** | — | [ThibautMelen/agentic-workflow-patterns](https://github.com/ThibautMelen/agentic-workflow-patterns) | Subagent, Progressive Skills, Master-Clone, etc. |
| **agentic-ai-systems** | 168 | [ThibautMelen/agentic-ai-systems](https://github.com/ThibautMelen/agentic-ai-systems) | Agentic systems with Mermaid diagrams |
| **quint-code** | 1.2k | [m0n0x41d/quint-code](https://github.com/m0n0x41d/quint-code) | Structured reasoning for Claude Code, Codex, Cursor |

#### Session & Logging

| Resource | Stars | URL |
|----------|-------|-----|
| **vibe-log-cli** | 282 | [vibe-log/vibe-log-cli](https://github.com/vibe-log/vibe-log-cli) |

### 0.12 More AI Coding — Agents, Skills, MCP

| Item | Stars | URL | Purpose |
|------|-------|-----|---------|
| **superset** | 1.7k | [superset-sh/superset](https://github.com/superset-sh/superset) | Command center: run Claude Code, OpenCode, Codex in parallel; git worktrees |
| **copilot-mcp** | 465 | [VikashLoomba/copilot-mcp](https://github.com/VikashLoomba/copilot-mcp) | VSCode: find/install Skills & MCP for Codex (proxy API), Claude Code |
| **skillport** | 312 | [gotalab/skillport](https://github.com/gotalab/skillport) | Bring Agent Skills to any AI agent via CLI or MCP |
| **refly** | 6.6k | [refly-ai/refly](https://github.com/refly-ai/refly) | Open-source agent skills builder; Claude Code, Cursor, Codex; vibe workflow |
| **claude-workflow-v2** | 1.2k | [CloudAI-X/claude-workflow-v2](https://github.com/CloudAI-X/claude-workflow-v2) | Universal Claude Code workflow; agents, skills, hooks, commands |
| **skillshare** | 480 | [runkids/skillshare](https://github.com/runkids/skillshare) | Sync skills across AI CLI tools; Claude Code, OpenClaw, OpenCode; team sharing |
| **skillkit** | 329 | [rohitg00/skillkit](https://github.com/rohitg00/skillkit) | Portable skills across Claude Code, Cursor, Codex (proxy API), 40+ more |
| **OpenContext** | 383 | [0xranx/OpenContext](https://github.com/0xranx/OpenContext) | Personal context store; reuse Codex/Claude/OpenCode with Skills/tools |
| **claude-codex-settings** | 419 | [fcakyon/claude-codex-settings](https://github.com/fcakyon/claude-codex-settings) | Battle-tested skills, commands, hooks, agents, MCP for daily use |
| **claude-context-local** | 187 | [FarhanAliRaza/claude-context-local](https://github.com/FarhanAliRaza/claude-context-local) | Code search MCP; local embeddings, no API cost |
| **claude-flow** | 14.1k | [ruvnet/claude-flow](https://github.com/ruvnet/claude-flow) | Agent orchestration for Claude; multi-agent swarms |
| **claude-code-mcp** | 1.1k | [steipete/claude-code-mcp](https://github.com/steipete/claude-code-mcp) | Claude Code as one-shot MCP (agent in agent) |
| **DesktopCommanderMCP** | 5.5k | [wonderwhy-er/DesktopCommanderMCP](https://github.com/wonderwhy-er/DesktopCommanderMCP) | Terminal control, file search, diff editing for Claude |
| **lobehub** | 72.3k | [lobehub/lobehub](https://github.com/lobehub/lobehub) | Agent harness; find, build, collaborate with agents |

#### More AI Coding — Claude Plugins, Skills & Guides

| Item | Stars | URL | Purpose |
|------|-------|-----|---------|
| **claude-plugins-official** | 7.5k | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Official Anthropic directory of Claude Code plugins |
| **antigravity-awesome-skills** | 9.9k | [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) | 800+ agentic skills for Claude Code/Antigravity/Cursor |
| **marketingskills** | 7.9k | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | Marketing skills for Claude Code; CRO, copywriting, SEO, analytics, growth |
| **AI-Research-SKILLs** | 3.5k | [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | AI research & engineering skills; Claude Code, Codex (proxy API); open-source |
| **claude-code-guide** | 3.4k | [zebbern/claude-code-guide](https://github.com/zebbern/claude-code-guide) | Setup, commands, workflows, agents, skills & tips |
| **claude-code-plugins-plus-skills** | 1.4k | [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) | 270+ plugins, 739 skills; Jupyter tutorials, CCPI package manager |
| **claude-pilot** | 1.1k | [maxritter/claude-pilot](https://github.com/maxritter/claude-pilot) | Production-grade code; tests enforced; context preserved |
| **pg-aiguide** | 1.5k | [timescale/pg-aiguide](https://github.com/timescale/pg-aiguide) | Postgres MCP + Claude plugin; better SQL for AI coding |
| **wcgw** | 641 | [rusiaaman/wcgw](https://github.com/rusiaaman/wcgw) | Shell and coding agent on MCP clients |

#### More AI Coding — Cursor/Windsurf/Cline & Memory

| Item | Stars | URL | Purpose |
|------|-------|-----|---------|
| **magic-mcp** | 4.3k | [21st-dev/magic-mcp](https://github.com/21st-dev/magic-mcp) | v0-like frontend in Cursor/Windsurf/Cline |
| **cipher** | 3.5k | [campfirein/cipher](https://github.com/campfirein/cipher) | Memory layer for coding agents; Cursor, Codex, Claude Code, Windsurf, Cline |
| **memory-bank-mcp** | 861 | [alioshr/memory-bank-mcp](https://github.com/alioshr/memory-bank-mcp) | Remote memory bank MCP; Cline Memory Bank–inspired |
| **DevDocs** | 2k | [cyberagiinc/DevDocs](https://github.com/cyberagiinc/DevDocs) | Free, private tech docs MCP; Cursor, Windsurf, Cline |
| **context-engineering-kit** | 470 | [NeoLabHQ/context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) | Plugin marketplace; Claude Code, OpenCode, Cursor, Windsurf, Cline |
| **rulebook-ai** | 572 | [botingw/rulebook-ai](https://github.com/botingw/rulebook-ai) | Vibe engineering rules; Codex (proxy API), Cursor, Cline, Windsurf, Claude Code |
| **rules_template** | 1.1k | [Bhartendu-Kumar/rules_template](https://github.com/Bhartendu-Kumar/rules_template) | Memory + reasoning rules for Cline/RooCode/Cursor/Windsurf |
| **Feishu-MCP** | 438 | [cso1z/Feishu-MCP](https://github.com/cso1z/Feishu-MCP) | Feishu/Lark docs for Cursor, Windsurf, Cline |

#### More AI Coding — Agents & Frameworks

| Item | Stars | URL | Purpose |
|------|-------|-----|---------|
| **OpenHands** | 67.9k | [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | AI-driven development |
| **continue** | 31.4k | [continuedev/continue](https://github.com/continuedev/continue) | Open-source CLI; headless async agents or TUI coding agent |
| **plandex** | 15k | [plandex-ai/plandex](https://github.com/plandex-ai/plandex) | AI coding agent for large projects |
| **how-to-build-a-coding-agent** | 5.1k | [ghuntley/how-to-build-a-coding-agent](https://github.com/ghuntley/how-to-build-a-coding-agent) | Workshop: build coding agent like Roo, Cline, Cursor, Windsurf |
| **golf** | 811 | [golf-mcp/golf](https://github.com/golf-mcp/golf) | Production MCP server framework; auth, observability, telemetry |
| **moltis** | 952 | [moltis-org/moltis](https://github.com/moltis-org/moltis) | Personal AI assistant; Rust, MCP, voice, multi-channel |
| **paperdebugger** | 1.3k | [PaperDebugger/paperdebugger](https://github.com/PaperDebugger/paperdebugger) | Multi-agent for academic writing, LaTeX, Overleaf |
| **raptor** | 1.1k | [gadievron/raptor](https://github.com/gadievron/raptor) | Claude Code as offensive/defensive security agent; rules, sub-agents, skills |
| **claude-code-config** | 936 | [jarrodwatts/claude-code-config](https://github.com/jarrodwatts/claude-code-config) | Personal Claude Code config; rules, hooks, agents, skills, commands |
| **langchain4j-aideepin** | 1.2k | [moyangzhan/langchain4j-aideepin](https://github.com/moyangzhan/langchain4j-aideepin) | AI productivity; RAG, workflow, MCP marketplace, long-term memory |

#### More AI Coding — Skills MCP & Browser Automation

| Item | Stars | URL | Purpose |
|------|-------|-----|---------|
| **browserwing** | 744 | [browserwing/browserwing](https://github.com/browserwing/browserwing) | Browser actions → MCP commands or Claude Skill; AI agents control browsers |
| **ios-simulator-skill** | 487 | [conorluddy/ios-simulator-skill](https://github.com/conorluddy/ios-simulator-skill) | iOS Simulator Skill for Claude Code; build, run, interact with apps |
| **skillz** | 359 | [intellectronica/skillz](https://github.com/intellectronica/skillz) | MCP server for loading skills; shim for non-Claude clients |
| **claude-skills-mcp** | 315 | [K-Dense-AI/claude-skills-mcp](https://github.com/K-Dense-AI/claude-skills-mcp) | MCP server for searching/retrieving Claude Agent Skills via vector search |

### 0.13 General SWE Tooling & Awesome Lists

#### Meta Awesome & Dev Tool Collections

| Collection | Stars | URL | Scope |
|------------|-------|-----|-------|
| **awesome** | 294k | [sindresorhus/awesome](https://github.com/sindresorhus/awesome) | Meta-list: platforms, languages, frameworks, tools; Development Environment, Testing, etc. |
| **awesome-chrome-devtools** | — | [ChromeDevTools/awesome-chrome-devtools](https://github.com/ChromeDevTools/awesome-chrome-devtools) | Chrome DevTools resources; debugging, profiling |
| **awesome-docker** | — | [veggiemonk/awesome-docker](https://github.com/veggiemonk/awesome-docker) | Docker resources; containers, orchestration |
| **awesome-kubernetes** | — | [ramitsurana/awesome-kubernetes](https://github.com/ramitsurana/awesome-kubernetes) | Kubernetes resources; orchestration, tooling |
| **awesome-terraform** | — | [shuaibiyy/awesome-terraform](https://github.com/shuaibiyy/awesome-terraform) | Terraform resources; IaC, providers, modules |
| **awesome-ai-devtools** | 3.6k | [jamesmurdza/awesome-ai-devtools](https://github.com/jamesmurdza/awesome-ai-devtools) | AI-powered developer tools |
| **Awesome-LLMOps** | 5.6k | [tensorchord/Awesome-LLMOps](https://github.com/tensorchord/Awesome-LLMOps) | LLMOps tools for developers |
| **awesome-data-engineering** | 8.3k | [igorbarinov/awesome-data-engineering](https://github.com/igorbarinov/awesome-data-engineering) | Data engineering tools |
| **awesome-ci** | 4k | [ligurio/awesome-ci](https://github.com/ligurio/awesome-ci) | CI services and tools |
| **awesome-developer-first** | 1.5k | [agamm/awesome-developer-first](https://github.com/agamm/awesome-developer-first) | Developer-first products |
| **best-of-python-dev** | 1.2k | [ml-tooling/best-of-python-dev](https://github.com/ml-tooling/best-of-python-dev) | Ranked Python dev tools |
| **go-recipes** | 4.5k | [nikolaydubina/go-recipes](https://github.com/nikolaydubina/go-recipes) | Tools for Go projects |
| **omni-tools** | 8.6k | [iib0011/omni-tools](https://github.com/iib0011/omni-tools) | Self-hosted web tools; converters, image/PDF/video |
| **dev-resources** | 1.2k | [marcelscruz/dev-resources](https://github.com/marcelscruz/dev-resources) | Collaborative dev resources list |
| **Awesome-independent-tools** | 2.3k | [yaolifeng0629/Awesome-independent-tools](https://github.com/yaolifeng0629/Awesome-independent-tools) | Indie dev & AI出海 tools |
| **awesome-awesome-nodejs** | 1.6k | [bnb/awesome-awesome-nodejs](https://github.com/bnb/awesome-awesome-nodejs) | Meta-list of Node.js awesome lists |
| **awesome-gis** | 5.2k | [sshuair/awesome-gis](https://github.com/sshuair/awesome-gis) | Geospatial tools, cartography, geoanalysis |
| **aws-toolbox** | 1.7k | [towardsthecloud/aws-toolbox](https://github.com/towardsthecloud/aws-toolbox) | AWS automation scripts for devs |
| **indie-hacker-tools-plus** | 1.5k | [XiaomingX/indie-hacker-tools-plus](https://github.com/XiaomingX/indie-hacker-tools-plus) | Tech stack for indie hackers |
| **DeFi-Developer-Road-Map** | 10.7k | [OffcierCia/DeFi-Developer-Road-Map](https://github.com/OffcierCia/DeFi-Developer-Road-Map) | DeFi dev handbook; DApps, smart contracts |
| **awesome-cross-platform-nodejs** | 1.2k | [bcoe/awesome-cross-platform-nodejs](https://github.com/bcoe/awesome-cross-platform-nodejs) | Cross-platform Node.js tools |

#### Web & Desktop Dev Tools

| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **it-tools** | 37k | [CorentinTh/it-tools](https://github.com/CorentinTh/it-tools) | Handy online tools for developers; converters, encoders, formatters |
| **Files** | 41.9k | [files-community/Files](https://github.com/files-community/Files) | Modern file manager; Windows, Git integration |
| **massCode** | 6.6k | [massCodeIO/massCode](https://github.com/massCodeIO/massCode) | Open-source code snippet manager |
| **wakapi** | 4.1k | [muety/wakapi](https://github.com/muety/wakapi) | Self-hosted WakaTime-compatible coding statistics |
| **kubero** | 4.1k | [kubero-dev/kubero](https://github.com/kubero-dev/kubero) | Self-hosted PaaS; Heroku/Netlify/Vercel alternative on Kubernetes |
| **waveterm** | 17.4k | [wavetermdev/waveterm](https://github.com/wavetermdev/waveterm) | Open-source cross-platform terminal for seamless workflows |

#### CLI & Terminal Productivity

| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **ohmyzsh** | 184.7k | [ohmyzsh/ohmyzsh](https://github.com/ohmyzsh/ohmyzsh) | zsh config framework; 300+ plugins |
| **Bash-it** | 14.9k | [Bash-it/bash-it](https://github.com/Bash-it/bash-it) | Community Bash framework; aliases, completion, plugins |
| **oh-my-bash** | 7.2k | [ohmybash/oh-my-bash](https://github.com/ohmybash/oh-my-bash) | Bash config framework; themes, plugins, auto-update |
| **lazygit** | 72.4k | [jesseduffield/lazygit](https://github.com/jesseduffield/lazygit) | Terminal UI for git |
| **bat** | 57.1k | [sharkdp/bat](https://github.com/sharkdp/bat) | cat clone with syntax highlighting |
| **fd** | 41.6k | [sharkdp/fd](https://github.com/sharkdp/fd) | Fast find alternative |
| **cheat.sh** | 40.9k | [chubin/cheat.sh](https://github.com/chubin/cheat.sh) | Cheat sheet in terminal |
| **httpie** | 37.6k | [httpie/httpie](https://github.com/httpie/httpie) | User-friendly HTTP client |
| **textual** | 34.3k | [Textualize/textual](https://github.com/Textualize/textual) | Python TUI framework |
| **yazi** | 32.7k | [sxyazi/yazi](https://github.com/sxyazi/yazi) | Blazing fast terminal file manager |
| **modern-unix** | 32.8k | [ibraheemdev/modern-unix](https://github.com/ibraheemdev/modern-unix) | Modern alternatives to common unix commands |
| **hyperfine** | 27.5k | [sharkdp/hyperfine](https://github.com/sharkdp/hyperfine) | CLI benchmarking |
| **withfig/autocomplete** | 25.1k | [withfig/autocomplete](https://github.com/withfig/autocomplete) | IDE-style shell autocomplete |
| **shell_gpt** | 11.8k | [TheR1D/shell_gpt](https://github.com/TheR1D/shell_gpt) | CLI productivity powered by LLMs |
| **nnn** | 21.2k | [jarun/nnn](https://github.com/jarun/nnn) | Terminal file manager |
| **jira-cli** | 5.1k | [ankitpokhrel/jira-cli](https://github.com/ankitpokhrel/jira-cli) | Interactive Jira CLI |
| **multi-gitter** | 1.2k | [lindell/multi-gitter](https://github.com/lindell/multi-gitter) | Update multiple repos with one command |
| **gita** | 1.8k | [nosarthur/gita](https://github.com/nosarthur/gita) | Manage many git repos |
| **Clipboard** | 5.7k | [Slackadays/Clipboard](https://github.com/Slackadays/Clipboard) | Smart clipboard manager |
| **amazon-q-developer-cli** | 1.9k | [aws/amazon-q-developer-cli](https://github.com/aws/amazon-q-developer-cli) | Agentic chat in terminal; MCP |

#### More CLI — HTTP, Git, File Mgmt (from modern-unix & search)

| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **posting** | 11.4k | [darrenburns/posting](https://github.com/darrenburns/posting) | Modern API client in terminal; REST, SSH |
| **xh** | 7.6k | [ducaale/xh](https://github.com/ducaale/xh) | Friendly HTTP client; HTTPie design, Rust speed |
| **npkill** | 9k | [voidcosmos/npkill](https://github.com/voidcosmos/npkill) | Find and remove node_modules; free disk space |
| **gitsome** | 7.7k | [donnemartin/gitsome](https://github.com/donnemartin/gitsome) | Supercharged Git/GitHub CLI |
| **gitlogue** | 4.2k | [unhappychoice/gitlogue](https://github.com/unhappychoice/gitlogue) | Cinematic Git commit replay; animated history |
| **xplr** | 4.7k | [sayanarijit/xplr](https://github.com/sayanarijit/xplr) | Hackable TUI file explorer |
| **eza** | 32k | [eza-community/eza](https://github.com/eza-community/eza) | Modern ls replacement |
| **ripgrep** | 44k | [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) | Fast grep; respects gitignore |
| **fzf** | 68k | [junegunn/fzf](https://github.com/junegunn/fzf) | Fuzzy finder |
| **jq** | 29k | [jqlang/jq](https://github.com/jqlang/jq) | sed for JSON |
| **zoxide** | 22k | [ajeetdsouza/zoxide](https://github.com/ajeetdsouza/zoxide) | Smarter cd; learns your habits |
| **tldr** | 52k | [tldr-pages/tldr](https://github.com/tldr-pages/tldr) | Simplified man pages with examples |

#### Developer Utilities & Code Quality

| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **Mac-CLI** | 9k | [guarinogabriel/Mac-CLI](https://github.com/guarinogabriel/Mac-CLI) | macOS CLI for developers; automate common Mac tasks |
| **dembrandt** | 1.3k | [dembrandt/dembrandt](https://github.com/dembrandt/dembrandt) | Extract website design system to tokens; logo, colors, typography; Playwright |
| **sttr** | 1.3k | [abhimanyu003/sttr](https://github.com/abhimanyu003/sttr) | Cross-platform string operations CLI; encode, decode, transform, JSON |
| **codeface** | 6.4k | [chrissimpkins/codeface](https://github.com/chrissimpkins/codeface) | Typefaces for source code |
| **tqdm** | 31k | [tqdm/tqdm](https://github.com/tqdm/tqdm) | Progress bar for Python/CLI |
| **tach** | 2.6k | [tach-org/tach](https://github.com/tach-org/tach) | Visualize + enforce dependencies; monorepo |
| **terragrunt** | 9.3k | [gruntwork-io/terragrunt](https://github.com/gruntwork-io/terragrunt) | Terraform/OpenTofu orchestration |

#### API Testing, Load Testing & HTTP Tools

| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **hoppscotch** | 77.8k | [hoppscotch/hoppscotch](https://github.com/hoppscotch/hoppscotch) | Open-source API dev ecosystem; Postman alternative; web, desktop, CLI |
| **httpbin** | 13.5k | [postmanlabs/httpbin](https://github.com/postmanlabs/httpbin) | HTTP request/response service; testing, debugging |
| **artillery** | 8.9k | [artilleryio/artillery](https://github.com/artilleryio/artillery) | Load testing platform; Playwright, HTTP, WebSocket, gRPC; serverless |

#### Observability & Monitoring

| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **netdata** | 77.7k | [netdata/netdata](https://github.com/netdata/netdata) | AI-powered full-stack observability; real-time metrics, alerting |
| **VictoriaMetrics** | 16.3k | [VictoriaMetrics/VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics) | Fast, cost-effective monitoring; time series DB; Prometheus-compatible |
| **hertzbeat** | 7k | [apache/hertzbeat](https://github.com/apache/hertzbeat) | AI-powered real-time observability; metrics, logs, alerts, status pages |
| **greptimedb** | 5.9k | [GreptimeTeam/greptimedb](https://github.com/GreptimeTeam/greptimedb) | Cloud-native observability DB; metrics, logs, traces; SQL/PromQL |

#### Testing & DevOps

| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **goreplay** | 19.2k | [probelabs/goreplay](https://github.com/probelabs/goreplay) | Capture and replay live HTTP traffic for testing |
| **terratest** | 7.9k | [gruntwork-io/terratest](https://github.com/gruntwork-io/terratest) | Go library for automated infrastructure testing |
| **goss** | 5.9k | [goss-org/goss](https://github.com/goss-org/goss) | Quick server testing and validation |
| **inspec** | 3k | [inspec/inspec](https://github.com/inspec/inspec) | Auditing and testing framework; compliance |
| **pytest-testinfra** | 2.5k | [pytest-dev/pytest-testinfra](https://github.com/pytest-dev/pytest-testinfra) | Test infrastructure with pytest |
| **CheatSheets-for-Developers** | 1.2k | [crescentpartha/CheatSheets-for-Developers](https://github.com/crescentpartha/CheatSheets-for-Developers) | Programming cheatsheets; Git, Docker, SQL, etc. |

### 0.14 Software Process, Vibe Coding, Agent-DD, Domain DD & Best Practices

#### Vibe Coding & Agent-Driven Development

| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **AI-Coding-Style-Guides** | 471 | [lidangzzz/AI-Coding-Style-Guides](https://github.com/lidangzzz/AI-Coding-Style-Guides) | Code compression for Vibe Coding/SWE-Agents; maximize context; 8 compression levels |
| **rulebook-ai** | 572 | [botingw/rulebook-ai](https://github.com/botingw/rulebook-ai) | Vibe engineering rules; consistent prompts for Codex (proxy API), Cursor, Cline, Windsurf, Claude Code |
| **awesome-ralph** | 723 | [snwfdhmp/awesome-ralph](https://github.com/snwfdhmp/awesome-ralph) | Ralph loop: run AI agents until specs fulfilled; automated agent loops |
| **ralph-playbook** | — | [ClaytonFarr/how-to-ralph-wiggum](https://github.com/ClaytonFarr/how-to-ralph-wiggum) | How to run Lifecycle–style agent loops |
| **agentic-workflow-patterns** | — | [ThibautMelen/agentic-workflow-patterns](https://github.com/ThibautMelen/agentic-workflow-patterns) | Subagent, Progressive Skills, Master-Clone, Spec-Driven patterns |
| **ccpm** | 7.3k | [automazeio/ccpm](https://github.com/automazeio/ccpm) | Project management for Claude Code; GitHub Issues + git worktrees; parallel agent execution |
| **vibe-log-cli** | 282 | [vibe-log/vibe-log-cli](https://github.com/vibe-log/vibe-log-cli) | Log and analyze Claude Code / Cursor AI-driven sessions |

#### Software Process & Development Best Practices

| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **clean-code-javascript** | 94.3k | [ryanmcdermott/clean-code-javascript](https://github.com/ryanmcdermott/clean-code-javascript) | Clean Code concepts adapted for JavaScript |
| **clean-code-typescript** | 9.7k | [labs42io/clean-code-typescript](https://github.com/labs42io/clean-code-typescript) | Clean Code + SOLID for TypeScript |
| **clean-code-php** | 12.5k | [piotrplenik/clean-code-php](https://github.com/piotrplenik/clean-code-php) | Clean Code concepts for PHP |
| **clean-code-dotnet** | 7.6k | [thangchung/clean-code-dotnet](https://github.com/thangchung/clean-code-dotnet) | Clean Code concepts and tools for .NET |
| **clean-code-python** | 4.8k | [zedr/clean-code-python](https://github.com/zedr/clean-code-python) | Clean Code concepts for Python |
| **Clean-Code-Notes** | 6.1k | [JuanCrg90/Clean-Code-Notes](https://github.com/JuanCrg90/Clean-Code-Notes) | Notes from Clean Code book |
| **evergreen-skills-developers** | 2.1k | [romenrg/evergreen-skills-developers](https://github.com/romenrg/evergreen-skills-developers) | Evergreen skills from software dev best practices; cross-framework principles; assessment |

#### Domain-Driven Design & Software Architecture

| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **awesome-ddd** | 12.1k | [heynickc/awesome-ddd](https://github.com/heynickc/awesome-ddd) | Curated DDD, CQRS, Event Sourcing, Event Storming resources |
| **evolutionary-architecture-by-example** | 3.2k | [evolutionary-architecture/evolutionary-architecture-by-example](https://github.com/evolutionary-architecture/evolutionary-architecture-by-example) | .NET DDD; modular monolith, microservices; step-by-step guide |
| **ddd-hexagonal-cqrs-es-eda** | 1.4k | [bitloops/ddd-hexagonal-cqrs-es-eda](https://github.com/bitloops/ddd-hexagonal-cqrs-es-eda) | DDD + Hexagonal + CQRS + Event Sourcing + EDA; NestJS, TypeScript |
| **go-food-delivery-microservices** | 1.1k | [mehdihadeli/go-food-delivery-microservices](https://github.com/mehdihadeli/go-food-delivery-microservices) | Go DDD; CQRS, ES, Vertical Slice, Event-Driven; BDD |
| **pitstop** | 1.2k | [EdwinVW/pitstop](https://github.com/EdwinVW/pitstop) | Garage Management sample; DDD, CQRS, Event Sourcing; .NET |
| **Practical.CleanArchitecture** | 2.4k | [phongnguyend/Practical.CleanArchitecture](https://github.com/phongnguyend/Practical.CleanArchitecture) | Full-stack Clean Architecture; DDD, CQRS, microservices, modular monolith |

#### Domain DD — Event Storming, Domain Storytelling & Context Mapping

| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **awesome-eventstorming** | — | [mariuszgil/awesome-eventstorming](https://github.com/mariuszgil/awesome-eventstorming) | Event Storming resources; workshop format for complex domains |
| **awesome-domain-storytelling** | — | [hofstef/awesome-domain-storytelling](https://github.com/hofstef/awesome-domain-storytelling) | Domain Storytelling; [domainstorytelling.org](http://domainstorytelling.org) |
| **context-mapping** | — | [ddd-crew/context-mapping](https://github.com/ddd-crew/context-mapping) | Context Mapping Cheatsheet & Starter Kit; bounded context integration |

#### Static Analysis, Linters & Code Quality (Tooling & Checkers)

| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **static-analysis** | 14.4k | [analysis-tools-dev/static-analysis](https://github.com/analysis-tools-dev/static-analysis) | Curated SAST tools & linters for all languages; [analysis-tools.dev](https://analysis-tools.dev/) |
| **awesome-dynamic-analysis** | — | [mre/awesome-dynamic-analysis](https://github.com/mre/awesome-dynamic-analysis) | Sister project: dynamic analysis tools |
| **sonarqube** | 10.2k | [SonarSource/sonarqube](https://github.com/SonarSource/sonarqube) | Continuous inspection; code quality, security, bugs |
| **reviewdog** | 9.1k | [reviewdog/reviewdog](https://github.com/reviewdog/reviewdog) | Automated code review; integrates any linter with GitHub/GitLab/Bitbucket |
| **infer** | 15.5k | [facebook/infer](https://github.com/facebook/infer) | Static analyzer for Java, C, C++, Objective-C |
| **SwiftLint** | 19.5k | [realm/SwiftLint](https://github.com/realm/SwiftLint) | Swift style and conventions |
| **checkstyle** | 8.9k | [checkstyle/checkstyle](https://github.com/checkstyle/checkstyle) | Java coding standard; Google Java Style, configurable |
| **pyre-check** | 7.1k | [facebook/pyre-check](https://github.com/facebook/pyre-check) | Python type-checking; taint analysis |
| **detekt** | 6.8k | [detekt/detekt](https://github.com/detekt/detekt) | Kotlin static analysis |
| **pylint** | 5.7k | [pylint-dev/pylint](https://github.com/pylint-dev/pylint) | Python linter; code quality |
| **pmd** | 5.3k | [pmd/pmd](https://github.com/pmd/pmd) | Multilanguage static analyzer; Java, Apex, PL/SQL, Swift |
| **qlty** | 3k | [qltysh/qlty](https://github.com/qltysh/qlty) | Code quality CLI; universal linting, auto-formatting, security, maintainability |
| **goreporter** | 3.1k | [qax-os/goreporter](https://github.com/qax-os/goreporter) | Go: static analysis, unit testing, code review, quality report |
| **DeepAudit** | 4.6k | [lintsinghua/DeepAudit](https://github.com/lintsinghua/DeepAudit) | AI multi-agent code audit; vulnerability mining; SAST, PoC verification |
| **tach** | 2.6k | [tach-org/tach](https://github.com/tach-org/tach) | Visualize + enforce dependencies; modular architecture; monorepo |

#### Linters & Formatters (High-Usage)

| Tool | Stars | URL | Scope |
|------|-------|-----|-------|
| **eslint** | — | [eslint/eslint](https://github.com/eslint/eslint) | JavaScript/TypeScript linter; pluggable |
| **prettier** | — | [prettier/prettier](https://github.com/prettier/prettier) | Opinionated code formatter; multi-language |
| **ruff** | — | [astral-sh/ruff](https://github.com/astral-sh/ruff) | Fast Python linter + formatter; replaces flake8, black, isort |

#### Best Practices, Tips & Guides (Consolidated)

| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **Claude Code Handbook** | — | [nikiforovall.blog/claude-code-rules](https://nikiforovall.blog/claude-code-rules/) | Best practices, tips, plugins |
| **Claude Code Tips** | — | [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) | 35+ tips; voice, system prompt, containers |
| **Claude Code Ultimate Guide** | — | [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) | Beginner→power user; templates; quizzes |
| **agentrules-architect** | 105 | [trevor-nichols/agentrules-architect](https://github.com/trevor-nichols/agentrules-architect) | AGENTS.md/CLAUDE.md generator for Codex, Claude Code, Cursor, Windsurf |
| **ruler** | 2.5k | [intellectronica/ruler](https://github.com/intellectronica/ruler) | Apply same rules to Claude Code, Codex, Cursor, Aider, Windsurf |

#### Tips & Tricks — Hooks & Quality Gates

| Tip | Source | Purpose |
|-----|--------|---------|
| **check-console-log** | ECC | Block on `console.log` in TS/JS before commit |
| **post-edit-format** | ECC | Run Prettier after Edit |
| **post-edit-typecheck** | ECC | Run `tsc --noEmit` on .ts/.tsx after Edit |
| **strategic-compact** | ECC | Manual compaction suggestions; avoid context loss |
| **memory-persistence** | ECC | session-start, session-end, pre-compact; preserve context |

---

## 1. Setup Completeness (Implemented)

| Item | Status | Notes |
|------|--------|------|
| **Provider credentials** | ✓ | nim, minimax (PROVIDER_LOGIN_CONFIG); kilo, glm need provider_definitions.json |
| **Clode links** | ✓ | claudeglm, claudemax |
| **Dex links** | ✓ | dex, dexmax, dexglm, dexhaiku, dexopus, dexsonnet, dexstep, dexcomposer |
| **Cliproxy config** | ✓ | _ensure_config in setup |
| **MCP install** | ✓ | run_wizard (Cursor, Claude Code, Codex, Claude Desktop, Droid) |
| **Playwright removal** | ✓ | Optional in wizard; thegent bundles browser tools |
| **MCP mounts** | ✓ | Playwright, Serena, Octocode (all required); flyto-core (optional browser alternative) |

---

## 2. Local Hooks (thegent/hooks)

| Hook | Purpose |
|------|---------|
| `harvest-pending-queue.sh` | Harvest pending queue |
| `prompt-submit-guard.sh` | Guard prompt submission |
| `task-completion-verifier.sh` | Verify task completion |
| `posttool-dispatcher.sh` | Post-tool dispatch |
| `pretool-dispatcher.sh` | Pre-tool dispatch |
| `hook-watcher.sh` | Watch hooks |
| `security-pipeline.sh` | Security pipeline |
| `governance-gates.sh` | Governance gates |
| `quality-gate.sh` | Quality gate |
| `spec-verifier.sh` | Spec verification |
| `qa-preflight.sh` | QA preflight |
| `async-test-runner.sh` | Async test runner |
| `qa-policy-test.sh` | QA policy test |
| `test_cache_*.sh` | Cache tests |
| `auto-checkpoint.sh` | Auto checkpoint |
| `test-maturity.sh` | Test maturity |
| `gardener-loop.sh` | Gardener loop |
| `hook-config.yaml` | Hook configuration |

**Proposed:** Add `thegent setup --hooks` to symlink/copy hooks into project `.git/hooks` or a hooks target dir.

---

## 3. Local Plugins & Skills

| Path | Type | Notes |
|------|------|-------|
| `.factory/droids/` | Factory droids | Droid definitions |
| `.factory/settings.json` | Factory config | |
| `.factory/config.json` | Factory config | |
| `skills/` | (empty) | Project skills; `.codex/skills/`, `.claude/skills/` |
| `.factory/plugins/marketplaces/` | Plugin marketplace | factory-plugins, droid-evolved, browser-navigation |

**Proposed:** Add `thegent setup --skills` to sync skills from a template or bundle. Add `thegent setup --plugins` to install Factory plugins.

---

## 4. MCP Servers (Local Config → Mount in thegent)

| MCP | Package/Command | Namespace | Mount Env |
|-----|-----------------|-----------|-----------|
| **thegent** | HTTP :3847 | (main) | — |
| **Playwright** | npx @playwright/mcp | browser | Required (default) |
| **Serena** | uvx serena start-mcp-server | serena | Required |
| **Octocode** | npx octocode-mcp | octocode | Required |
| **flyto-core** | python -m core.mcp_server or flyto serve | browser | THGENT_MCP_MOUNT_FLYTO=1 |
| **server-sequential-thinking** | npx @modelcontextprotocol/server-sequential-thinking | — | (client config) |
| **software-planning-mcp** | node build/index.js | — | (client config) |
| **next-devtools** | npx next-devtools-mcp | — | (client config) |

**Proposed:** Mount Octocode, Serena, software-planning-mcp, next-devtools into thegent for single-process. Set THGENT_MCP_MOUNT_*=1 in process-compose for dev.

---

## 5. Proposed Items from the Web

### MCP Servers

| Name | URL | Description | Incorporate? |
|------|-----|-------------|--------------|
| **flyto-core** | [github.com/flytohub/flyto-core](https://github.com/flytohub/flyto-core) | 300+ tools, 6 MCP tools, browser/file/API; low context | ✓ Mount option |
| **Serena** | [github.com/oraios/serena](https://github.com/oraios/serena) | LSP code tools (goto-def, find-refs) | ✓ Mount option |
| **Octocode** | [npm octocode-mcp](https://www.npmjs.com/package/octocode-mcp) | GitHub/code search | ✓ Mount option |
| **@playwright/mcp** | [npm @playwright/mcp](https://www.npmjs.com/package/@playwright/mcp) | Browser automation | ✓ Default mount |
| **software-planning-mcp** | Local / Cline | Planning, todos | □ Optional mount |
| **next-devtools** | [npm next-devtools-mcp](https://www.npmjs.com/package/next-devtools-mcp) | Next.js dev tools | □ Optional mount |
| **server-sequential-thinking** | @modelcontextprotocol/server-sequential-thinking | Chain-of-thought | □ Optional mount |
| **@modelcontextprotocol/server-memory** | npx @modelcontextprotocol/server-memory | Persistent memory | □ Client config |
| **@modelcontextprotocol/server-github** | npx @modelcontextprotocol/server-github | GitHub PRs, issues | □ Client config |
| **firecrawl-mcp** | npx firecrawl-mcp | Web scraping | □ Client config |
| **@context7/mcp-server** | npx @context7/mcp-server | Live docs lookup | □ Client config |
| **Figma-Context-MCP** | [GLips/Figma-Context-MCP](https://github.com/GLips/Figma-Context-MCP) | Figma layout for Cursor | □ Client config |
| **git-mcp** | [idosal/git-mcp](https://github.com/idosal/git-mcp) | Remote MCP for GitHub projects | □ Client config |
| **dbhub** | [bytebase/dbhub](https://github.com/bytebase/dbhub) | Postgres/MySQL/SQLite MCP | □ Client config |
| **claude-context** | [zilliztech/claude-context](https://github.com/zilliztech/claude-context) | Code search, full codebase context | □ Optional mount |
| **fastapi_mcp** | [tadata-org/fastapi_mcp](https://github.com/tadata-org/fastapi_mcp) | Expose FastAPI as MCP | □ Reference |
| **magic-mcp** | [21st-dev/magic-mcp](https://github.com/21st-dev/magic-mcp) | v0-like UI in Cursor/Windsurf/Cline | □ Client config |
| **mcpm.sh** | [pathintegral-institute/mcpm.sh](https://github.com/pathintegral-institute/mcpm.sh) | MCP package manager & registry | □ Optional tool |
| **memory-bank-mcp** | [alioshr/memory-bank-mcp](https://github.com/alioshr/memory-bank-mcp) | Remote memory for Cline/Cursor/Windsurf | □ Client config |
| **context7** | [upstash/context7](https://github.com/upstash/context7) | Up-to-date code docs for Cursor | □ Client config |
| **n8n-mcp** | [czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp) | Build n8n workflows from Cursor | □ Client config |
| **mcp-memory-service** | [doobidoo/mcp-memory-service](https://github.com/doobidoo/mcp-memory-service) | Auto context memory for Claude, Cursor | □ Client config |
| **Skill_Seekers** | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | Docs/GitHub/PDF → Claude skills | □ Optional tool |

### Incorporation Matrix (Priority × Effort)

| Item | Priority | Effort | Compatibility | Action |
|------|----------|--------|---------------|--------|
| Playwright | P0 | Done | Cursor, Codex, Claude | Required (default) |
| Serena | P0 | Done | Cursor, Codex, Claude | Required |
| Octocode | P0 | Done | Cursor, Codex, Claude | Required |
| flyto-core | P2 | Low | Cursor, Codex | Env flag |
| sequential-thinking | P2 | Low | All | Optional mount |
| software-planning-mcp | P2 | Low | Cursor, Cline | Optional mount |
| next-devtools | P2 | Low | Next.js projects | Optional mount |
| ECC skills/rules | P2 | Medium | Claude Code, Cursor | Sync template |
| ECC hooks | P2 | Medium | Claude Code | Reference only |
| pre-commit/husky | P3 | Low | Git | `setup --hooks` |
| ECC hook recipes | P3 | Low | Claude Code | Document in setup |
| Rulesync / claude-rules-doctor | P3 | Low | Config | Optional tools |
| git-mcp, dbhub, Figma MCP | P3 | Low | Per-project | Client config |

### Docs & References

| Doc | URL | Use |
|-----|-----|-----|
| FastMCP Providers | [gofastmcp.com/servers/providers/overview](https://gofastmcp.com/servers/providers/overview) | Mounting, proxying |
| FastMCP Mounting | [gofastmcp.com/servers/providers/mounting](https://gofastmcp.com/servers/providers/mounting) | create_proxy, namespace |
| MCP Registry | [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io/) | Discover servers |
| Awesome MCP | [wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers) | 100+ community servers |
| Serena clients | [oraios.github.io/serena/02-usage/030_clients](https://oraios.github.io/serena/02-usage/030_clients.html) | Cursor, Codex, Claude |
| ECC install | [everything-claude-code install.sh](https://github.com/affaan-m/everything-claude-code/blob/main/install.sh) | Rules/skills install |
| ECC hooks README | [hooks/README.md](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/README.md) | Hook schema, recipes, async |
| awesome-agent-skills | [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) | Skill scopes, official sources |
| Codex skill docs | [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills) | Codex skill scopes |
| Lifecycle playbook | [ClaytonFarr/how-to-ralph-wiggum](https://github.com/ClaytonFarr/how-to-ralph-wiggum) | Three phases, two prompts, loop mechanics |
| mcpm.sh | [pathintegral-institute/mcpm.sh](https://github.com/pathintegral-institute/mcpm.sh) | MCP package manager, router, profiles |
| skillshare | [runkids/skillshare](https://github.com/runkids/skillshare) | Cross-tool skill sync (Claude Code, OpenCode, Codex) |
| tokscale | [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale) | Token usage tracking across AI CLIs |
| mcp-for-beginners | [microsoft/mcp-for-beginners](https://github.com/microsoft/mcp-for-beginners) | MCP fundamentals; .NET, Java, TS, Python, Rust |
| Skill_Seekers | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | Docs/GitHub/PDF → Claude skills |
| awesome-claude-code | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Primary curated list (23.9k★) |
| awesome-claude-skills | [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | Claude Skills (7.2k★) |
| awesome-agent-skills | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 300+ skills; Codex, Cursor, OpenCode |
| awesome-vibe-coding-guide | [analyticalrohit/awesome-vibe-coding-guide](https://github.com/analyticalrohit/awesome-vibe-coding-guide) | 10x Vibe Coder guide |
| awesome-ralph | [snwfdhmp/awesome-ralph](https://github.com/snwfdhmp/awesome-ralph) | Lifecycle resources |
| Claude Code Ultimate Guide | [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) | Beginner→power user |
| ai-guide | [liyupi/ai-guide](https://github.com/liyupi/ai-guide) | AI resource大全; Vibe Coding (6.9k★) |
| cursor.directory | [cursor.directory](https://cursor.directory/) | Cursor rules, MCPs, generate, jobs (72k+ members) |
| directories | [leerob/directories](https://github.com/leerob/directories) | Cursor Directory source, rules index |
| wshobson/agents | [wshobson/agents](https://github.com/wshobson/agents) | Multi-agent orchestration for Claude Code |

### Hooks (External)

| Hook | Source | Purpose |
|------|--------|---------|
| pre-commit | [pre-commit.com](https://pre-commit.com/) | Git hooks framework |
| husky | [typicode.github.io/husky](https://typicode.github.io/husky/) | Node git hooks |
| lefthook | [github.com/evilmartians/lefthook](https://github.com/evilmartians/lefthook) | Fast git hooks |
| ECC hooks | everything-claude-code/hooks | session-start, session-end, compact |
| ECC hook recipes | hooks/README.md | TODO warn, block large files, ruff format, require tests |
| c0ntextKeeper | [Capnjbrown/c0ntextKeeper](https://github.com/Capnjbrown/c0ntextKeeper) | 7 hooks, 187 semantic patterns, 3 MCP tools; context preservation |

### Skills (External)

| Skill | Source | Purpose |
|-------|--------|---------|
| browser-navigation | .factory/plugins | Map to browser_* tools |
| agent-orchestra | skills/agent-orchestra | Multi-agent orchestration |
| BMAD workflows | .cursor/rules/bmad | Product, game, innovation workflows |
| ECC skills | everything-claude-code/skills | 37 skills: tdd, django, springboot, golang, etc. |
| anthropics/skills | [anthropics/skills](https://github.com/anthropics/skills) | docx, xlsx, pptx, pdf |
| openai/skills | [openai/skills](https://github.com/openai/skills) | Codex catalog |
| ComposioHQ awesome-claude-skills | 35k★, 500+ | Airtable, Slack, GitHub, etc. automation |
| awesome-agent-skills | [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) | Curated for Claude, Codex (proxy API) |
| Skill_Seekers | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | Docs, GitHub, PDF → Claude skills; conflict detection |

### Plugins (External)

| Plugin | Source | Purpose |
|--------|--------|---------|
| Factory droid-evolved | .factory/plugins | Enhanced droid |
| everything-claude-code | /plugin install | 13 agents, 37 skills, 31 commands |
| Cline MCP | Cline | MCP integration |
| Cursor rules | .cursor/rules | Project rules |
| AgentSys | [avifenesh/agentsys](https://github.com/avifenesh/agentsys) | 12 plugins, 41 agents, 27 skills |
| claude-codex-settings | [fcakyon/claude-codex-settings](https://github.com/fcakyon/claude-codex-settings) | Battle-tested GitHub, Azure, Playwright |
| Rulesync | [dyoshikawa/rulesync](https://github.com/dyoshikawa/rulesync) | Config generator Claude↔others |
| skillshare | [runkids/skillshare](https://github.com/runkids/skillshare) | Sync skills across Claude Code, OpenCode, Codex, Cursor |
| agentrules-architect | [trevor-nichols/agentrules-architect](https://github.com/trevor-nichols/agentrules-architect) | AGENTS.md generator for Codex, Cursor, Windsurf, OpenCode |

### Workflows (Autonomous Loops)

| Workflow | Source | Purpose |
|----------|--------|---------|
| Lifecycle | [ghuntley.com/ralph](https://ghuntley.com/ralph), [how-to-ralph-wiggum](https://github.com/ClaytonFarr/how-to-ralph-wiggum) | Autonomous loop: specs → plan → build; fresh context per iteration |
| ralph-wiggum-marketer | ECC plugin | Autonomous copywriter for SaaS content |
| gru ralph | [zscole/gru](https://github.com/zscole/gru) | Ralph loop integrated into Gru |

### Tooling (Config & Session)

| Tool | Purpose |
|------|---------|
| claude-rules-doctor | Detect dead rules (paths: globs) |
| ClaudeCTX | Switch Claude config with one command |
| recall | Full-text search sessions |
| claude-code-tools | Session continuity, Rust session search |
| tokscale | [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale) | Token tracking: OpenCode, Claude Code, Codex (proxy API), Cursor |
| OpenContext | [0xranx/OpenContext](https://github.com/0xranx/OpenContext) | Personal context store; Tauri desktop app |
| c0ntextKeeper | [Capnjbrown/c0ntextKeeper](https://github.com/Capnjbrown/c0ntextKeeper) | Context preservation; 7 hooks, 187 patterns |
| mcp-memory-service | [doobidoo/mcp-memory-service](https://github.com/doobidoo/mcp-memory-service) | Auto context memory for 13+ AI tools |
| ruler | [intellectronica/ruler](https://github.com/intellectronica/ruler) | Same rules across Claude Code, Codex, Cursor, Aider |
| claude-squad | [smtg-ai/claude-squad](https://github.com/smtg-ai/claude-squad) | Manage Claude Code, Aider, Codex, OpenCode, Amp |
| ccpm | [automazeio/ccpm](https://github.com/automazeio/ccpm) | Project management; GitHub Issues + git worktrees |

### Templates & Scaffolds

| Template | Source | Purpose |
|----------|--------|---------|
| ECC CLAUDE.md | everything-claude-code/examples | SaaS Next.js, Django API, Go, Rust |
| meridian | [markmdev/meridian](https://github.com/markmdev/meridian) | Zero-config Claude Code; task scaffolding, TDD |
| fulling | [FullAgent/fulling](https://github.com/FullAgent/fulling) | Full-stack AI agent (Next.js, Claude, K8s) |
| crystal | [stravu/crystal](https://github.com/stravu/crystal) | Parallel Codex/Claude sessions in git worktrees |

---

## 6. process-compose Environment (Current)

```yaml
environment:
  - THGENT_MCP_MOUNT_PLAYWRIGHT=1   # Browser tools (required)
  - THGENT_MCP_MOUNT_SERENA=1       # LSP code tools (required)
  - THGENT_MCP_MOUNT_OCTOCODE=1     # GitHub/code search (required)
```

All three mounts are required by default. Set to `0` to disable if needed.

---

## 7. Quick Commands

```bash
# Full setup
thegent setup

# Links only
thegent clode install-links
thegent dex install-links

# MCP
thegent mcp install all
thegent mcp up
thegent mcp restart

# Cliproxy
thegent cliproxy ensure-config
thegent cliproxy start
thegent cliproxy login <provider>
```

---

## 8. Gaps & Next Steps

### Immediate
- [ ] Add kilo, glm to provider_definitions.json (login block) for setup
- [ ] `thegent setup --hooks` to install hooks (pre-commit, husky, or thegent/hooks)
- [ ] `thegent setup --skills` to sync skills template (ECC or custom)
- [ ] Mount software-planning-mcp, next-devtools, sequential-thinking as optional providers

### Reference / Documentation
- [ ] Document flyto-core: `pip install flyto-core[browser]`, `playwright install chromium`
- [ ] Add ECC install reference: `./install.sh typescript` (or python/golang) for rules
- [ ] Link to MCP registry and awesome-mcp-servers for discovery

### Future
- [ ] Optional: `thegent setup --ecc` to install ECC rules/skills (with language selector)
- [ ] Optional: AgentShield scan integration (`npx ecc-agentshield scan`)
- [ ] Optional: Skill Creator from git history (`/skill-create` pattern)
- [ ] Optional: Lifecycle loop template (`loop.sh`, `PROMPT_plan.md`, `PROMPT_build.md`) for autonomous dev
- [ ] Optional: skillshare integration for cross-tool skill sync
- [ ] Optional: tokscale for token usage tracking
- [ ] Optional: ECC CLAUDE.md templates (SaaS, Django, Go, Rust) in setup
- [ ] Optional: c0ntextKeeper or mcp-memory-service for context preservation
- [ ] Optional: ruler for cross-tool rules sync
