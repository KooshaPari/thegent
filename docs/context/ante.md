# Ante: Comprehensive Context & Reference Document

> **What is Ante?** Ante (Another Terminal) is a lightweight, native Rust terminal AI agent by Antigma Labs. It is the closest existing product to thegent's vision for autonomous agent orchestration. It is proprietary, currently in preview, and has documented reliability issues — but its design philosophy and architecture serve as the reference target for "turning Codex into Ante."
>
> **Source URLs:** https://docs.useante.com/ | https://antigma.ai/ | https://github.com/AntigmaLabs
> **Local archives:** ~/Downloads/*Ante.webarchive (16 pages extracted 2026-02-20)
> **Runtime version confirmed:** `ante 0.0.preview6` (from antigma_drift_report)
> **Last verified:** 2026-02-20

---

## 1. What Ante Does

Ante is a self-contained terminal AI coding agent. It occupies the same problem space as Claude Code and Codex CLI but with distinct architectural choices:

- **Problem it solves:** Autonomous, terminal-native AI agent that can read/write code, execute shell commands, search the web, spawn sub-agents, and accumulate persistent memory — all from a CLI/TUI interface.
- **Primary interface:** Terminal (TUI or headless CLI), not IDE panel or web UI.
- **Core differentiator:** Native Rust for performance and security, provider-agnostic multi-LLM support, clean client-daemon architecture, headless-first design.
- **Evaluation standing:** Topped Terminal Bench 1.0 leaderboard (2025) and Terminal Bench 2.0 leaderboard (February 2026, verified agent, best-in-class for Gemini). Uses Terminal Bench / Harbor as primary evaluation suite.
- **Status:** Preview (`0.0.preview6`). macOS and Linux only. Breaking changes expected. Windows planned for 2026-Q2.
- **Company:** Antigma Labs — mission is "building substrate for self-organizing intelligence." Treats agents as teammates, and treats users as another agent.

---

## 2. Key Features (Exhaustive)

### 2.1 Interface Modes

**Interactive TUI:**
- Built with `ratatui` (native Rust terminal UI library)
- Renders inline (up to 24 lines); debounced rendering at ~100fps
- Real-time streaming tokens as they arrive (no buffering)
- Chat interface with markdown rendering
- Tool approval prompts (Allow / Deny) for gated tools (Bash, Write)
- Fullscreen diff view on alternate screen for file edit proposals
- Model and provider selection during session (no restart needed)
- Theme selection system (dark/light, configurable)
- History navigation with keyboard shortcuts
- Ctrl+C to interrupt; Escape to cancel input; Enter to send
- Streaming can be disabled via `ANTE_DISABLE_STREAMING=1`

**Headless Mode:**
- Invoked with: `ante "prompt"` or `ante --prompt "prompt"` or `ante -p "prompt"`
- Accepts stdin input (`cat file | ante -p "review"`)
- When stdin + prompt provided: concatenated (stdin first)
- Streaming disabled — responses buffered for cleaner output
- Yolo policy implied — all tool calls auto-approved
- Authentication checked eagerly — exits immediately if not authenticated
- Automatically appends current directory folder structure to prompt (project layout awareness)
- `--check` flag: runs verification pass after main task (agent reviews its own work)

**Output formats (headless):**
- `minimal` (default) — agent messages, info, errors only
- `human` — all events, ANSI colors, human-readable
- `json` — every event as JSON object (one per line) for machine consumption

### 2.2 Tool System

All tools implement the `Tool` trait:

```rust
#[async_trait]
pub trait Tool: Send + Sync {
    fn metadata(&self) -> &ToolMetadata;
    async fn call(&self, input: ToolCallInput) -> Result<ToolCallOutput>;
}
```

**Built-in tools (12 total):**

| Tool | Category | Approval | Description |
|------|----------|----------|-------------|
| Read | File I/O | No | Read file contents; supports text, images (PNG/JPG), PDFs, Jupyter notebooks; offset/limit for large files |
| Write | File I/O | Yes | Create or overwrite files |
| Edit | File I/O | Yes | Exact string replacement (old_string → new_string; optional replace_all) |
| Glob | File I/O | No | Find files by glob pattern (e.g., `**/*.rs`) |
| Grep | File I/O | No | Search file contents with regex; built on ripgrep; supports path, glob, type filters, output_mode |
| Bash | Shell | Yes | Execute shell commands; default timeout 2 minutes, max 10 minutes |
| BashOutput | Shell | No | Read output from running/completed background shell by ID |
| KillShell | Shell | No | Terminate background shell by ID |
| Task | Builtin | No | Spawn sub-agent for complex tasks |
| TodoWrite | Builtin | No | Manage task list (id, content, status) for multi-step progress tracking |
| WebFetch | Builtin | No | Fetch URL content and process it |
| WebSearch | Builtin | No | Search the web and return results |

**Tool filtering:**
```bash
ante --allowed-tools Read Glob Grep "analyze only"       # allowlist
ante --disallowed-tools Bash Write "read-only analysis"  # denylist
ante --allowed-tools "Read" "Bash(cargo test)" "Bash(cargo clippy)"  # ToolMatcher syntax
```

- Tool names matched case-insensitively
- `ToolMatcher` syntax supports fine-grained pattern control
- `--yolo` flag skips all tool approval prompts

### 2.3 Skills System

Skills are the primary extensibility mechanism. They follow an open format called "Agent Skills" — portable across compatible agent products.

**Skill structure:**
```
my-skill/
├── SKILL.md           # Required — YAML frontmatter + instructions
├── scripts/           # Executable code the agent can run
├── references/        # Detailed docs loaded on demand
└── assets/            # Templates, schemas, data files
```

**SKILL.md frontmatter fields:**

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| name | No | Directory name | Skill identifier |
| description | No | First paragraph | When to use; shown to main agent for delegation |
| argument-hint | No | — | Hint for expected arguments (e.g., `<path>`) |
| user-invocable | No | true | Whether user can invoke via `/skillname` slash command |
| disable-model-invocation | No | false | Prevent model from auto-invoking |
| allowed-tools | No | — | Pre-approved tools (e.g., `Read`, `Bash(git diff -- *)`) |
| metadata | No | — | Arbitrary key-value pairs |

**Discovery order (later overrides earlier):**
1. System-level built-in skills
2. `~/.ante/skills/` (user-level)
3. `agents/skills/` (project-level)
4. `.ante/skills/` (project-level)
5. `.claude/skills/` (project-level — Claude.ai compatibility)

**Invocation:**
```bash
/commit                    # Invoke by name
/review src/core/session.rs  # With arguments ($ARGUMENTS placeholder)
```

### 2.4 Sub-Agents

Sub-agents are full independent agents (not just tools) spawned by the main agent via the `Task` tool.

**Built-in sub-agents (2):**
- **General** — General-purpose research, code search, multi-step tasks. Main agent delegates when it needs complex search it isn't confident completing in a few tries.
- **Explorer** — Fast agent specialized for codebase exploration. Finds files by pattern, searches keywords, answers structural questions.

**Custom sub-agents:**
Created as markdown files in `~/.ante/agents/` with YAML frontmatter:

```yaml
---
name: "security-reviewer"
description: "Reviews code for security vulnerabilities and OWASP top 10 issues"
color: "red"
---
You are a security-focused code reviewer...
```

Frontmatter fields: `name` (required), `description` (required), `model` (optional override), `tools` (optional restrict), `color` (optional TUI display).

**How delegation works:**
1. Main agent evaluates available sub-agents and their descriptions
2. Delegates via `Task` tool with a detailed prompt
3. Sub-agent runs independently with its own context
4. Result returned to main agent, incorporated into conversation

**State isolation:** Each sub-agent has its own independent session, memory, and configuration. Failures don't cascade to parent.

**Discovery:**
- Built-in agents (General, Explorer)
- `~/.ante/agents/` directory (user-level)
- All registered at session initialization time

### 2.5 Memory System

**Project memory (per-project, automatic):**
- Memory directory: `.claude/projects/<project-path>/memory/`
- Key file: `MEMORY.md` — first 200 lines injected into system prompt at every session start
- Agent consults existing memory, records new insights, updates/removes outdated memories
- Fully editable plain markdown; agent can also update via Write/Edit tools

**Memory file organization:**
```
memory/
├── MEMORY.md           # Auto-loaded (max 200 lines); link to details
├── debugging.md        # Detailed debugging notes
├── patterns.md         # Code patterns and conventions
└── architecture.md     # Architecture decisions
```

**Memory principles:** Concise (truncated at 200 lines), semantic (topic-organized, not chronological), accurate (updated/removed when wrong), actionable (what worked, what didn't, why).

**Per-project scoping:** Different projects have independent memory directories — React frontend knowledge doesn't bleed into Rust backend.

### 2.6 Eval & Benchmark

- Uses Terminal Bench and Harbor as primary external benchmark
- Philosophy: "Grade outcomes, not trajectories" — did the agent solve the problem?
- Principles: start early/simple, honest eval from actual failures, isolate and reproduce regressions
- Topped Terminal Bench 1.0 leaderboard (2025)
- Topped Terminal Bench 2.0 leaderboard (February 2026) — verified agent, best-in-class for Gemini
- Self-described: "Evaluation is the backbone of building a reliable AI agent."

### 2.7 Offline Mode (Experimental)

- Integrated llama.cpp inference engine (no external dependency)
- Discovers GGUF models on system (single-file and sharded models)
- Memory estimation based on model file size + KV cache (scales with context window)
- Minimum context window: 32K tokens
- Model preferences: `context_window`, `thinking`, `temperature`
- Antigma maintains curated list of verified GGUF models; also publishes models on Hugging Face
- Future: building toward self-contained agent stack (`AntigmaLabs/nanochat-rs` in progress)

### 2.8 Agent Organization (Experimental)

Four multi-agent coordination architectures:

**Independent:**
- Agents work in parallel with no interaction
- Aggregator synthesizes outputs at end
- Best for: diverse perspectives, brainstorming, redundant verification
- Pattern: Start → Parallel fan-out → Barrier/sync → Aggregator → End

**Decentralized:**
- Parallel rounds; agents read each other's prior outputs, propose refinements
- Fixed number of rounds; consensus without central coordinator
- Best for: debate-style reasoning, peer review, negotiation
- Pattern: Initialize → Shared board → Parallel read+propose → Append deltas → Convergence check loop

**Centralized Iterative:**
- Central orchestrator decomposes, dispatches in parallel, evaluates, decides refine-or-finish
- Best for: complex tasks with quality gates (code generation + review, multi-step research)
- Pattern: Setup → Orchestrator decomposes → Parallel execute → Barrier → Orchestrator evaluates → Done? → Final synthesis

**Hybrid Iterative:**
- Orchestrator plans + dispatches; then agents peer-refine each other's work; orchestrator evaluates
- Best for: high-quality collaborative output where structured planning + peer feedback both matter
- Pattern: Orchestrator plans → Parallel draft → Peer refine round → Orchestrator evaluates → Loop or done

---

## 3. Architecture

### 3.1 Client-Daemon Split

```
┌────────────────┐          ┌─────────────────────────────┐
│     Client      │    Op    │          Daemon             │
│                 │ ───────▶ │                             │
│  TUI (ratatui)  │          │  Session → Turn → Step      │
│  or Headless    │ ◀─────── │                             │
│                 │    Evt   │  Tools   Providers  Store   │
└────────────────┘          └─────────────────────────────┘
```

**Client** — User-facing layer (TUI or headless CLI). Sends `Op` operations and renders `Evt` events.

**Daemon** — Core engine. Receives operations, manages sessions, dispatches to LLM providers, schedules tool execution, emits events.

**Transport** — Bounded async channels (Tokio) within the same process. Message IDs enable tracing.

This architecture allows swapping frontends without touching the core engine.

### 3.2 Concept Hierarchy

```
Project
 └── Session
      └── Task
           └── Turn
                └── Step
```

| Concept | Description |
|---------|-------------|
| Project | Git repo or root directory. Multiple sessions possible. |
| Session | One episode of interaction. Manages dialog state, token usage, context compaction. |
| Task | One piece of work. Can span multiple turns. Generally 1 task = 1 turn without approval interruption. |
| Turn | One back-and-forth with agent. Starts with user input, ends with agent message or approval request. |
| Step | One interaction from agent with LLM. Handles tool calls and mechanics. |

### 3.3 Op/Evt Message Protocol

**Message ID prefixes:**
- `op_` — operations (client → daemon)
- `evt_` — events (daemon → client)
- `ses_` — sessions
- `step_` — steps

**Operations reference:**

| Op | Fields | Description |
|----|--------|-------------|
| NewSession | model, provider, policy, streaming, config | Initialize new session |
| UserInput | String | Submit user prompt |
| ApprovalResponse | allow/deny | Respond to tool approval |
| SlashCommand | skill name, args | Invoke a skill |
| OfflineMode | OfflineModeOp | Offline mode operations |
| Interrupt | — | Abort current task |
| Shutdown | — | Clean shutdown |

**Events reference:**

| Evt | Fields | Description |
|-----|--------|-------------|
| SessionInit | metadata | Session is ready |
| TaskStarted | id | New task begun |
| TaskFinished | id, error, is_interrupted | Task completed or failed |
| AgentMessage | String | Text response from agent |
| Thinking | String | Chain-of-thought content |
| MessageDelta | String | Streaming content chunk |
| ToolCallStarted | tool_use | Tool execution began |
| ToolCallFinished | result | Tool execution completed |
| ToolCallCancelled | — | Tool execution was cancelled |
| RequestApproval | tool_use | Agent needs permission |
| UsageUpdate | tokens, cost | Token/cost tracking |
| Info | String | Informational message |
| Error | String | Error message |

### 3.4 LLM Provider System

Each provider implements a common interface:

```rust
pub trait Provider: Send + Sync {
    async fn send(&self, request: ProviderRequest) -> Result<ProviderResponse>;
    fn capability(&self) -> ProviderCapability;
}
```

**Provider catalog (from docs and runtime drift analysis):**

| ID | Provider | Wire Format | Models | Runtime Status |
|----|----------|------------|--------|---------------|
| anthropic | Anthropic | Messages API | Claude family | Confirmed in runtime |
| openai | OpenAI | Chat Completions | GPT-4o, o1, etc. | Confirmed |
| openai-response | OpenAI | Responses API | GPT-4o | Confirmed |
| gemini | Google Gemini | Gemini API | Gemini family | Docs only — NOT in runtime v0.0.preview6 (drift!) |
| open-router | Open Router | OpenAI-compatible | 400+ models | Confirmed |
| xai | Grok (xAI) | OpenAI-compatible | Grok models | Confirmed |
| local | llama.cpp | GGUF local | Qwen, Llama, etc. | Confirmed |

**Runtime drift note:** `gemini` provider is documented but NOT present in `ante 0.0.preview6` runtime (confirmed via network/binary analysis in `antigma_drift_report.md`). This is a known discrepancy between docs and implementation.

**Provider resolution order (CLI → project → user → env → defaults):**
1. CLI flags (`--provider`, `--model`)
2. Project config (`.ante/config.json`)
3. User settings (`~/.ante/settings.json`)
4. Environment variables
5. Compiled defaults

**Third-party / OpenAI-compatible providers:**
- Open Router: `export OPEN_ROUTER_API_KEY="sk-or-..."` then `ante --provider open-router --model anthropic/claude-sonnet-4-5`
- Custom base URL: `export OPENAI_API_BASE="https://api.together.xyz/v1"` then use `--provider openai`
- Requirement: model MUST support tool use (function calling) — Ante relies on tools for agent capabilities

### 3.5 Storage Layout

| Location | Purpose |
|----------|---------|
| `~/.ante/settings.json` | User preferences |
| `~/.ante/skills/` | User-level skills |
| `~/.ante/agents/` | User-level sub-agents |
| `.ante/` | Project-local config |
| `.claude/` | Claude.ai compatibility directory |
| `.claude/projects/<path>/memory/` | Per-project auto-memory |
| `/tmp/ante/<project-hash>/` | Temporary files, per-project scoped |
| `~/.ante/models/` | Local GGUF models (offline mode) |

Override home config via `ANTE_HOME` environment variable.

---

## 4. Session & Context Management

### 4.1 Session Lifecycle

1. Client sends `Op::NewSession` with model, provider, and policy
2. Daemon resolves provider, authenticates, discovers skills and sub-agents
3. Daemon creates Session, emits `Evt::SessionInit`
4. User sends `Op::UserInput` to start task
5. Session spawns a Turn → communicates with LLM
6. Turn executes tools, requests approvals, eventually completes
7. When context budget nears limit: auto-compaction summarizes history

### 4.2 Context Compaction

- Automatic summarization when approaching context limit
- No manual trigger required
- `MEMORY.md` truncated at 200 lines; only first 200 lines injected into system prompt
- Sessions expire after TTL (default 30 days); summaries persist longer

### 4.3 Session Commands

```bash
ante sessions              # List all sessions
ante resume <session-id>   # Resume a session
ante export <session-id>   # Export session
ante config get model      # Get setting
ante config set model claude-opus-4.6  # Set setting
ante config reset          # Reset to defaults
ante version               # Version info
ante doctor                # Environment diagnostics
```

---

## 5. Configuration Reference

### 5.1 Settings File (`~/.ante/settings.json`)

```json
{
  "model": "claude-sonnet-4-5-20250514",
  "provider": "anthropic",
  "theme": "default",
  "policy": "default",
  "has_completed_onboarding": true
}
```

Policy values: `"default"` (approval required for gated tools) or `"yolo"` (all auto-approved).

### 5.2 Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API auth |
| `OPENAI_API_KEY` | OpenAI API auth |
| `OPEN_ROUTER_API_KEY` | Open Router API auth |
| `OPENAI_API_BASE` | Custom OpenAI-compatible base URL |
| `ANTE_HOME` | Override home config directory |
| `ANTE_DISABLE_STREAMING` | Disable streaming in TUI mode |

### 5.3 Headless CLI Flags

| Flag | Description |
|------|-------------|
| `-p, --prompt <PROMPT>` | The prompt to run |
| `-m, --model <MODEL>` | Override model name |
| `--provider <PROVIDER>` | Override API provider |
| `--yolo` | Skip all tool approval prompts |
| `--output-format <FORMAT>` | Output format: json, human, minimal (default: minimal) |
| `--system-prompt <PROMPT>` | Replace default system prompt entirely |
| `--append-system-prompt <TEXT>` | Append text to system prompt |
| `--allowed-tools <TOOLS>...` | Only allow these tools (space-separated) |
| `--disallowed-tools <TOOLS>...` | Disallow these tools (space-separated) |
| `--check` | Run verification pass after main task |

---

## 6. Known Issues & Limitations

### 6.1 Documented Reliability Issues (Why Ante is "Insanely Buggy")

- **Preview instability:** `v0.0.preview6` — breaking changes expected and acknowledged
- **Gemini provider drift:** Docs advertise Gemini support; runtime binary does not include it (confirmed via binary analysis)
- **Context management fragility:** Context compaction at 200-line MEMORY.md limit is blunt; no semantic prioritization
- **Sub-agent coordination:** Parent-child coordination is basic — parent simply waits for result, no partial result streaming, no parallel sub-agent fan-out with progress visibility
- **Resource limits:** CPU/memory caps per sub-agent are designed for but not yet implemented
- **Agent organization:** All four patterns (Independent, Decentralized, Centralized Iterative, Hybrid Iterative) are "experimental" — no production reliability guarantees
- **Offline mode:** "Experimental" — llama.cpp integration, memory estimation not always accurate
- **Eval framework:** No built-in A/B testing between providers/models; Terminal Bench is external
- **Installation:** "Installation instructions coming soon" — quickstart page is a stub
- **Windows:** Not supported (Linux/macOS only)
- **IDE integration:** Not yet available (CLI-only)
- **Web UI:** No browser-based interface
- **SAML/enterprise SSO:** Not supported (env vars + OAuth only)
- **Debugging tools:** No integrated debugger
- **RAG system:** Not built-in; must be implemented via skills

### 6.2 Known Architecture Gaps vs Claude Code / Codex

| Gap | Impact |
|-----|--------|
| No IDE integration | Can't use from VS Code / Cursor panel |
| No team/org features | Single-user focused; no org-level settings |
| Smaller ecosystem | Fewer community skills/agents than established players |
| No cloud hosting | Users run locally; no managed service |
| No structured output schema | No first-class JSON output mode from agent (only from Bash tools) |
| Breaking changes | Not production-stable; upgrade paths not guaranteed |

---

## 7. Comparison to Alternatives

| Dimension | Ante | Claude Code | Codex | Gemini CLI | thegent |
|-----------|------|-------------|-------|-----------|---------|
| **Language** | Rust | Go | Rust (core) + Python (SDK) | Go | Python |
| **Interface** | CLI/TUI (ratatui) | CLI/IDE panel | CLI/IDE/Web | CLI | CLI/TUI (compositor) |
| **Dependencies** | Minimal (Rust native) | Low-moderate | Moderate | Low | Moderate |
| **Provider Support** | 6+ (incl. local) | Anthropic-primary | OpenAI-primary | Gemini-native | Via OpenRouter (400+) |
| **Offline Capable** | Yes (experimental) | Limited | Limited | No | No |
| **Skills System** | Yes (open format, portable) | Pattern-based (informal) | Plugin registry | Limited | Hooks (script-based) |
| **Sub-Agents** | Yes (built-in General + Explorer + custom) | Yes (via Task) | Yes (via Task) | Limited | Crew pattern |
| **Memory** | Persistent per-project (MEMORY.md auto-injected) | Session-based | Session-based | Session-based | Work-stream + dumps (manual) |
| **Eval/Benchmark** | Terminal Bench #1 (2025+2026) | Anthropic internal | OpenAI internal | Google internal | Quality gates (compliance focus) |
| **Maturity** | Preview (v0.0.preview6) | Stable | Stable | Beta | Active development |
| **Open Source** | Partial | Partial | Partial | Limited | Internal |
| **Agent Organization** | 4 patterns (experimental) | Limited | Worker pattern | Limited | Crew + work-stream |
| **Governance** | Tool filtering + approval only | Similar | Similar | Similar | Comprehensive policy engine |
| **Enterprise** | Single-user | Anthropic-backed | OpenAI-backed | Google-backed | Multi-tenant designed |

**Where Ante is stronger:**
- Native Rust (performance, security, minimal deps)
- True offline capability (local GGUF via llama.cpp)
- Headless-first design with structured output formats
- Clean client-daemon separation (testable, swappable frontends)
- Skills as open, portable, versioned format
- Terminal Bench leadership (real-world task completion)
- Multi-agent architecture patterns (4 named patterns with clear use-when guidance)

**Where Ante is weaker:**
- Preview reliability (bugs, missing features, breaking changes)
- No IDE integration (CLI-only)
- No org/enterprise features
- No built-in A/B benchmarking or metrics collection
- Governance is minimal (no policy engine, no quality gates)
- Gemini docs-vs-runtime gap (trust issues)

---

## 8. "Turn Codex into Ante" — Gap Analysis

This section identifies what Codex CLI (thegent's current harness foundation) needs to become Ante-equivalent. thegent's strategy is: use Codex as the harness foundation, implement Ante-like orchestration features on top of thegent's routing/governance/TUI infrastructure.

### 8.1 What Codex Already Has (Do Not Reinvent)

| Feature | Codex Status | Notes |
|---------|-------------|-------|
| Responses API integration | Complete | Core of Codex; app-server protocol |
| Tool system | Complete | apply_patch, exec, web_search, image_view |
| Streaming (SSE + WebSocket) | Complete | 8-event sequence fully implemented |
| TUI (ratatui) | Complete | Codex has its own ratatui-based TUI |
| Headless/exec mode | Complete | `codex exec` subcommand |
| Multi-provider routing | Via thegent proxy | CLIProxy + LiteLLM router |
| MCP server mode | Complete | `codex --mcp-server` |
| Sub-agent spawning | Via Task tool | Basic; needs enhancement |

### 8.2 Feature Gaps: What Codex Needs to Match Ante

**Gap 1: Skills System (High Priority)**

Ante has a discoverable, versioned, open-format skills system. Codex has no equivalent.

What to build:
- Skills discovery from `~/.codex/skills/` and `.codex/skills/` (+ `.claude/skills/` for compat)
- SKILL.md format: YAML frontmatter + markdown instructions
- `allowed-tools` per skill (pre-approved tool list)
- `/skillname` slash command invocation in TUI and headless
- `$ARGUMENTS` placeholder substitution
- `scripts/`, `references/`, `assets/` subdirectory support
- Override: project-level skills override user-level by name
- User-invocable vs model-invocable distinction

**Gap 2: Persistent Per-Project Memory (High Priority)**

Ante auto-injects `MEMORY.md` (first 200 lines) into every session system prompt. Codex has no persistent memory.

What to build:
- `MEMORY.md` at `.claude/projects/<hash>/memory/MEMORY.md` (or equivalent path)
- Auto-load and inject into system prompt at session init
- Agent can read/write memory files via existing Write/Edit tools
- 200-line injection limit; topic-file linking pattern
- Per-project scoping (project hash as directory key)

**Gap 3: Named Sub-Agent Types with Descriptions (Medium Priority)**

Ante has built-in General + Explorer sub-agents with natural-language descriptions used for routing. Codex's Task tool spawns agents but has no type system.

What to build:
- Sub-agent definition format (markdown + YAML frontmatter: name, description, model, tools, color)
- Discovery from `~/.codex/agents/` and `.codex/agents/`
- Built-in General and Explorer equivalents
- Main agent can query available sub-agents and their descriptions for delegation decisions
- All sub-agents registered at session init

**Gap 4: `--check` Verification Pass (Medium Priority)**

Ante's `--check` flag runs a second verification pass where the agent reviews its own work.

What to build:
- Post-completion hook: `--check` or `check: true` config
- Second LLM pass with prompt: "Review what was accomplished vs the original request. Complete anything missing. Optimize without affecting correctness."
- Exits with non-zero code if verification detects incomplete work

**Gap 5: Structured Headless Output Formats (Medium Priority)**

Ante has `minimal`, `human`, and `json` output modes with event-per-line JSON. Codex's headless output is less structured.

What to build:
- `--output-format json` mode: each agent event as JSON object, one per line
- Event types: agent_message, tool_call_started, tool_call_finished, usage_update, error
- `--output-format minimal` (default): only agent messages + errors
- `--output-format human`: all events with ANSI formatting
- Standard exit codes: 0=success, 1=input error, 2=execution error, 3=provider error, 4=cancelled

**Gap 6: Agent Organization Patterns (Lower Priority — Future)**

Ante defines four multi-agent coordination architectures. Codex/thegent has ad-hoc crew patterns.

What to build (eventually):
- Independent: parallel fan-out + aggregator synthesis
- Decentralized: shared board, parallel read+propose, convergence detection
- Centralized Iterative: orchestrator with quality-gated refinement loop
- Hybrid Iterative: orchestrator + peer refine rounds
- Selection via `--agent-organization independent|decentralized|centralized|hybrid`

**Gap 7: Context-Aware Directory Injection (Low Priority — Easy Win)**

Ante automatically appends current directory folder structure to headless prompts.

What to build:
- In headless mode: enumerate `fd -t f -d 3` output (or equivalent) and append to system prompt
- Or: inject `.tree` summary of top-level structure

**Gap 8: Offline / Local Model Support (Lower Priority)**

Ante integrates llama.cpp for fully offline GGUF inference.

What to build (eventually):
- `--provider local` flag routing to local llama.cpp or Ollama
- GGUF model discovery and memory estimation
- thegent already has OpenRouter for multi-provider; local models are an extension

### 8.3 What thegent Adds on Top of Codex (Ante Doesn't Have)

| thegent Feature | Ante Equivalent | Gap Direction |
|----------------|----------------|---------------|
| Comprehensive policy engine | Tool filtering + approval only | thegent is stronger |
| 5-layer security pipeline | None | thegent is stronger |
| Quality gates (coverage, complexity, SAST) | Terminal Bench external eval only | thegent is stronger |
| Multi-tenant org features | Single-user only | thegent is stronger |
| Work-stream (WORK_STREAM.md) | No equivalent | thegent is stronger |
| Hook system (lifecycle hooks) | No hooks | thegent is stronger |
| OpenRouter 400+ model routing | 6 providers (no OpenRouter equivalent by default) | thegent is stronger |
| Conversation dumps | Minimal memory (MEMORY.md) | thegent is stronger |
| thegent plan loop (autonomous continuous work) | No equivalent | thegent is stronger |

### 8.4 Implementation Priority (Ranked)

| Priority | Feature | Effort | Value |
|----------|---------|--------|-------|
| P1 | Skills system (SKILL.md format, discovery, slash commands) | M | Extensibility foundation |
| P1 | Persistent MEMORY.md injection | S | Cross-session continuity |
| P2 | Named sub-agent types with descriptions | M | Better task delegation |
| P2 | `--check` verification pass | S | Output quality |
| P2 | Structured headless output formats + exit codes | S | CI/CD integration |
| P3 | Context-aware directory injection (headless) | XS | Easy win |
| P3 | Agent organization patterns (4 modes) | L | Advanced orchestration |
| P4 | Offline / local model support | L | Air-gap capability |

---

## 9. Sources & References

| Source | URL | Fetched |
|--------|-----|---------|
| Ante official docs | https://docs.useante.com/ | 2026-02-20 |
| Antigma Labs homepage | https://antigma.ai/ | 2026-02-20 |
| Antigma GitHub | https://github.com/AntigmaLabs | 2026-02-20 |
| Antigma X/Twitter | https://x.com/antigma_labs | 2026-02-20 |
| nanochat-rs (Rust LLM core) | https://github.com/AntigmaLabs/nanochat-rs | 2026-02-20 |
| Terminal Bench leaderboard | https://www.tbench.ai/leaderboard | 2026-02-20 |
| Harbor framework (eval) | https://harborframework.com/docs/datasets/running-tbench | 2026-02-20 |
| Local webarchives | ~/Downloads/*Ante.webarchive (16 pages) | 2026-02-20 |
| Runtime drift analysis | docs/research/antigma/antigma_drift_report.md | 2026-02-20 |

**Ante documentation pages archived (16 total):**
Overview, Quickstart, Core Concepts & Protocol, Architecture, Interactive TUI, Headless Mode, Skills, Sub-Agents, Tools, Memory, Model & Provider Catalog, Preferences, Adding a 3rd Party Provider, Offline Mode (Experimental), Agent Organization (Experimental), Eval & Benchmark

---

## 10. Quick Reference

```
ANTE AT A GLANCE
================

Company:    Antigma Labs
Language:   Rust (native)
Status:     Preview v0.0.preview6 (breaking changes expected)
Platforms:  macOS, Linux
Benchmark:  #1 Terminal Bench 1.0 (2025) + Terminal Bench 2.0 (Feb 2026)

ARCHITECTURE:
  Client (TUI/Headless) ←Op/Evt→ Daemon (Sessions, Tools, Providers, Memory)
  Concept hierarchy: Project → Session → Task → Turn → Step

PROVIDERS (runtime-confirmed):
  anthropic | openai | openai-response | open-router | xai | local
  (gemini: documented but NOT in runtime v0.0.preview6)

BUILT-IN TOOLS (12):
  File I/O: Read, Write*, Edit*, Glob, Grep
  Shell:    Bash*, BashOutput, KillShell
  Builtin:  Task, TodoWrite, WebFetch, WebSearch
  (* = approval required by default)

SKILLS:
  Directory: ~/.ante/skills/ (user) or .ante/skills/ (project)
  Format:    SKILL.md (YAML frontmatter + markdown)
  Invoke:    /skillname [arguments]

SUB-AGENTS:
  Built-in: General, Explorer
  Custom:   ~/.ante/agents/*.md (YAML frontmatter: name, description, model, tools)

MEMORY:
  Location: .claude/projects/<path>/memory/MEMORY.md
  Behavior: First 200 lines auto-injected into system prompt every session
  Scope:    Per-project, independent between projects

KEY COMMANDS:
  ante                           # Interactive TUI
  ante "prompt"                  # Headless (minimal output)
  ante -p "prompt" --check       # Headless + self-verification
  ante --provider openai --model gpt-4o "prompt"
  ante --yolo "fix all warnings"
  ante --allowed-tools Read Glob Grep "read-only analysis"
  ante sessions                  # List sessions
  ante resume <id>               # Resume session

OUTPUT FORMATS (headless):
  minimal (default) | human | json (--output-format json)

AGENT ORGANIZATION (experimental):
  Independent | Decentralized | Centralized Iterative | Hybrid Iterative

KEY ENV VARS:
  ANTHROPIC_API_KEY | OPENAI_API_KEY | OPEN_ROUTER_API_KEY
  ANTE_HOME | ANTE_DISABLE_STREAMING | OPENAI_API_BASE

GAP ANALYSIS — "TURN CODEX INTO ANTE":
  P1: Skills system (SKILL.md, discovery, slash commands)
  P1: Persistent MEMORY.md auto-injection
  P2: Named sub-agent types with descriptions
  P2: --check verification pass
  P2: Structured headless output formats + exit codes
  P3: Context-aware directory injection (headless)
  P4: Offline / local model support
```

---

*Comprehensive Ante context document. Synthesized from 16 official Ante documentation pages (webarchive), runtime binary analysis (v0.0.preview6), and web research. Last updated: 2026-02-20. Maintained in: docs/context/ante.md*
