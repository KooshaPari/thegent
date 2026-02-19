# Global Claude Code Instructions

These rules apply to ALL projects. Project-level CLAUDE.md files supplement (and may override) these.

---

# Heavy Web Research Policy
- Use DuckDuckGo (`thegent_ddg_search`) for comprehensive web research when local knowledge is insufficient.
- **Deep Research Protocol**: For multi-source or blocked sites (Reddit, Google), use the Deep Research Protocol (`docs/guides/DEEP_RESEARCH_PROTOCOL.md`).
- **Resilience**: Use `thegent_reddit_search` for Reddit and `thegent_scrape_url` (Playwright-backed) to bypass site blocks.
- **Protocol Tools**: Prefer `thegent_deep_research` orchestrator for complex investigations.
- Prefer `duckduckgo-search` library for programmatic access.
- Summarize findings for the user, providing links only for deep dives.

---

# Library-First Policy

**CRITICAL**: Prefer **library + thin wrapper** over full custom implementation. Apply from the start of development and throughout.

## Before Writing Code
- **First question**: "Is there a library that solves this?"
- **Generic problems** (retry, cache, file watch, circuit breaker, rate limit): Use a library.
- **Thin wrapper**: Adapt library to project conventions; keep wrapper < 50 LOC.

## Throughout Development
- **New feature**: Check for existing libraries before implementing.
- **Custom logic**: Only for domain-specific behavior (routing, health formula, policy).
- **ADR required**: If choosing custom over library, document rationale in ADR.

## Project Standards
| Need | Library | Notes |
|------|---------|------|
| Retry/backoff | tenacity | No manual retry loops; use `wait_random_exponential` |
| HTTP | httpx | No requests/urllib |
| File watching | watchdog | No os.walk polling for triggers |
| Caching | cachetools / diskcache | No custom TTL logic |
| Circuit breaker | pybreaker | Or tenacity + custom state |
| Logging | structlog (aspirational) | Structured, JSON for aggregation |

See: `docs/research/LIBRARY_FIRST_AUDIT_AND_PLAN.md`, `docs/guides/anti-patterns.md`

---

# Proactive Governance Evolution

**Do not wait for the user to ask.** When your work touches a governance domain (retry, cache, file watch, HTTP, auth, logging, etc.):

1. **Check** existing governance (anti-patterns.md, LIBRARY_FIRST_AUDIT_AND_PLAN.md, CLAUDE.md).
2. **Follow** it. If governance is missing or outdated, **propose or add** an update as part of the same task.
3. **At task completion**: Run a governance checkpoint. If you touched a governed domain and governance is incomplete, update it.

You are not required to ask "should I add governance?" — if you see a gap, update it. See: `docs/research/PROACTIVE_GOVERNANCE_EVOLUTION_PLAN.md`

---

# Conversation Dumps (Always Write)

**When completing significant work** (research, design, multi-file implementation, or decisions that affect the project):

1. **Write a conversation dump** to `docs/research/CONVERSATION_DUMP_YYYY-MM-DD.md` (or append to existing).
2. **Include**: Key decisions, findings, rationale, and handoff notes for the next agent or session.
3. **Do not wait** for the user to ask — write dumps proactively so work is recoverable and continuous.

See: `docs/research/CONVERSATION_DUMP_2026-02-16.md` for format and examples.

---

# Context Management Strategy

## The Manager Pattern

**CRITICAL**: Operate as a strategic manager, not a worker. Delegate to subagents.

### Keep in Main Context
- User intent and requirements
- Strategic decisions and trade-offs
- Summaries of completed work
- Critical architectural knowledge

### Delegate to Subagents
- File exploration (>3 files)
- Pattern searches across codebase
- Multi-file implementations
- Long command sequences
- Test execution
- **Default agent**: Unless specified, use `thegent free` (`thegent plan loop`, `thegent free --do-next`, `thegent_run`/`thegent_bg`, DAG tasks → copilot)
- **Stay controlled in idle**: Use waiting commands — `thegent plan loop` (not bash for-loops), `thegent plan wait-next` (block until work ready), `thegent wait <session_id>` (block until session exits). Avoid busy loops and bash wrappers.

**See**: [THGENT_COMMAND_MODEL_OPTIONS_AND_AGENT_FEATURES_RESEARCH.md](docs/research/THGENT_COMMAND_MODEL_OPTIONS_AND_AGENT_FEATURES_RESEARCH.md) for comprehensive thegent command reference.

## When to Delegate Code (Decision Guide)

**Delegate** when:
- **Scope**: Changes span >3 files or multiple modules
- **Exploration**: Need to search patterns across the codebase
- **Context budget**: Task would add >2000 tokens of file content/output
- **Independence**: Work can be done in isolation with clear handoff
- **Long-running**: Test suites, builds, or multi-step sequences

**Handle directly** when:
- **Single-file**: One file, one concern, clear fix
- **Quick answer**: User needs info, not implementation
- **Config/tweak**: Small Taskfile, env, or script change
- **<3 files**: Limited scope, you can hold it in context

**Rule of thumb**: If you would need to read >3 files to implement correctly, delegate exploration first and get a summary. If the implementation touches >3 files, delegate to `general-purpose` or a task agent.

## Strategy Quick Reference

| Need | Tool/Provider | Example Prompt |
|------|---------------|----------------|
| Heavy Web Research | DuckDuckGo (`ddgr`) | "Search DDG for latest VitePress plugins" |
| Find code patterns | `Explore` | "Find all error handling patterns" |
| Design approach | `Plan` | "Design auth implementation strategy" |
| Run commands | `Bash` | "Run test suite and report failures" |
| Multi-step implementation | `thegent free` or `thegent bg` | "Implement and test feature X" |
| Quick isolated fix | DO NOT delegate | Handle directly |
| Work stream integration | `thegent free --do-next` | Automatic work item execution |
| Continuous autonomous work | `thegent plan loop` | Continuous work loop |
| Background execution | `thegent bg` | Non-blocking task execution |
| Model-specific routing | `thegent run -M <model>` | Model-first routing |
| Idle waiting | `thegent plan wait-next` | Block until work ready |

## DuckDuckGo Search Mandate
- Use `ddgr` (or equivalent DDG tool) for all heavy web research.
- Prefer DuckDuckGo over other search engines for privacy and agent-friendliness.
- Research tasks should prioritize finding up-to-date documentation and community-driven solutions.

### Parallel vs Sequential

**Parallel** (no dependencies): Launch 2-3 explore agents simultaneously for independent searches.

**Sequential** (dependent): explore -> receive summary -> plan based on findings -> implement approved plan.

## Subagent Swarm (async orchestration)

**If you have subagent/swarm capabilities:** Use them as an **async swarm**.

- **Call task agents async.** Fire tasks so that as each completes, you are reawoken to re-evaluate, spawn more agents, or do more work yourself.
- **Run a swarm.** Up to **50 concurrent task agents**. Scale up when work is well decomposed and independent.
- **Work in between.** While tasks run async, use your own context for planning, monitoring, or other work.
- **Reawaken on completion.** When idle, you will be reawoken as each agent completes. Use that to spawn more agents, do follow-up work, or consolidate results.

## Directory Listing (ls Avoidance)

**When listing directory contents**, avoid `ls -l` in project root (node_modules, .venv cause 5m+ delays). Prefer:

- **fd**: `fd -t f -d 1` or `fd -t d -d 1` (excludes .git; add `-E node_modules -E .venv -E dist` for heavy dirs)
- **Subdirs**: `ls -l src/`, `ls -l docs/` instead of project root
- **Names only**: `ls -1` when only filenames needed (no stat)

See: `docs/reference/INDEXING_AND_OPTIMIZATION_SYSTEMS.md` §7.

## Anti-Patterns

| Bad | Good |
|-----|------|
| Reading 10 files to "understand" | Delegate exploration, get summary |
| `ls -l` in project root (node_modules present) | `fd -t f -d 1` or `ls -l src/` |
| Editing files for multi-file changes | Delegate to `general-purpose` |
| Sequential explorations one-by-one | Batch parallel explores |
| Asking subagent for "all results" | Ask for "summary" or "key files" |
| **Workspace Cleanup**: Running `git restore .` or `git clean` to "reset" the environment | **Respect Work**: Leave modified files alone; assume they are active tasks from other agents. |
| Overwriting a "dirty" file with your version | Merge or work around existing changes. |
| **Custom retry/cache/watch**: Reinventing generic logic | **Library-first**: Use tenacity, cachetools, watchdog; thin wrapper only |

## UX/DX Friction Reduction

**When you encounter repeated-action friction** (e.g. bash loops, `for i in 1 2 3; do X; done`, or scripts wrapping single commands), **automatically solve it** by adding native CLI support:

- **Prefer native options over bash wrapping.** If a workflow requires `for i in 1..N; do thegent X; done`, add `--repeat N` (or equivalent) to the CLI so users run `thegent X --repeat N` instead.
- **Apply this generally.** As you come across docs, scripts, or prompts that use shell loops or wrappers around thegent (or project CLI) commands, add the corresponding native option and update the instructions.
- **Examples:** `thegent free --do-next --repeat 5` (no bash loop needed); `thegent dag sync --watch` with auto-run-next (no separate spawn loop).

---

## DX/UX/AX Continuous Improvement (Governance Mandate)

**CRITICAL**: As an end-user of your own workflow, you are performing market testing. Continuously identify and fix friction points automatically. This is **part of governance** — not optional.

### Core Principle

**Every agent must reduce complexity and verbosity** of their own actions, embedding improvements into tooling, instructions, and skills.

### Mandatory Friction Detection

**CRITICAL**: The `friction-detector.sh` hook runs automatically and will alert you to friction patterns. **You must act on these alerts.**

**During every task**, check:
- [ ] **Hook detected friction?** → Fix immediately or delegate
- [ ] Am I making too many similar tool calls? → Batch them
- [ ] Is this more complex than needed? → Simplify
- [ ] Can I create a reusable helper? → Create it
- [ ] Will other agents benefit? → Share it
- [ ] Can this be automated? → Automate it
- [ ] **Did I see `cd &&`, `2>&1`, or `head` in commands?** → Fix CLI UX immediately

### Available Helpers (Use These)

- `batch_read_files()` - Batch file reading (`scripts/batch_file_ops.py`)
- `normalize_path()` - Path normalization (`scripts/batch_file_ops.py`)
- `log_friction()` - Friction logging (`scripts/friction_logger.py`)
- `get_next_items()` - Work stream helper (`scripts/workstream_helper.py`)

### Improvement Workflow

1. **Detect** → Identify friction during task
2. **Log** → Use `log_friction()` or add to `docs/research/FRICTION_LOG.md`
3. **Fix** → Quick fix (< 5 min) or create task (`dx-improve-*`, `ux-improve-*`, `ax-improve-*`)
4. **Delegate** → If specialized, delegate to `dx-improver`, `ux-improver`, or `ax-improver` agents
5. **Embed** → Add improvements to tooling/instructions/skills

### Automatic Friction Detection and Resolution

**CRITICAL**: Friction detection is now **automated via hooks**. The `friction-detector.sh` hook runs automatically on every Write/Edit/Execute operation and detects common friction patterns.

**When working, automatically:**

1. **Identify Friction Points** (NOW AUTOMATED):
   - ✅ **Hook detects**: `cd &&` patterns → CLI should work from any directory
   - ✅ **Hook detects**: `2>&1` patterns → CLI should handle stderr automatically
   - ✅ **Hook detects**: `head -n` patterns → CLI should have `--limit` option
   - ✅ **Hook detects**: `grep -v` patterns → CLI should filter noise automatically
   - ✅ **Hook detects**: Bash loops wrapping commands → CLI should have native loop support
   - ✅ **Hook detects**: Multiple sequential `read_file()` calls → Use `batch_read_files()`
   - ✅ **Hook detects**: Manual path resolution → Use `normalize_path()` helper
   - Verbose commands (long flags, repetitive patterns)
   - Multi-step operations (manual coordination required)
   - Unclear error messages
   - Missing shortcuts or aliases
   - Function signature mismatches (TypeError at runtime)
   - Manual coordination overhead (claiming, status checking)
   - Inefficient file operations (full reads vs targeted)
   - Inconsistent path handling

2. **Delegate Fixes Immediately**:
   - **Don't wait** for user to ask
   - **When hook detects friction**: Fix it immediately or delegate to `thegent free --bg`
   - **Hook output shows**: Priority (P1/P2), category (UX/DX/AX), and solution
   - Log friction points using `log_friction()` or add to `docs/research/FRICTION_LOG.md`
   - Use `thegent free --bg` to parallelize friction fixes

3. **Prioritize Actions That Reduce Complexity**:
   - **High Priority**: Reduce verbosity (shortcuts, aliases, batch operations)
   - **High Priority**: Reduce complexity (unified commands, auto-claim)
   - **Medium Priority**: Improve visibility (status commands, monitoring)
   - **Medium Priority**: Prevent errors (validation, type checking)

4. **Track and Measure**:
   - Record friction points with impact assessment
   - Track improvements (before/after command length, step count)
   - Measure reduction in complexity and verbosity

### Examples of Self-Optimization

**Friction**: `uv run thegent free --bg "long task description"` is verbose
**Action**: Delegate agent to create `thegent delegate "task"` shortcut

**Friction**: Need to run 5 commands: `plan do-next` → read → `free --bg` → claim → monitor
**Action**: Delegate agent to create `thegent work` unified command

**Friction**: TypeError from parameter mismatch
**Action**: Delegate agent to add function signature validation

**Friction**: Can't see what agents are doing
**Action**: Delegate agent to create `thegent status` command

**Friction**: Multiple `read_file()` calls for similar operations
**Action**: Use `batch_read_files()` helper or create one

**Friction**: Inconsistent path handling (relative vs absolute)
**Action**: Use `normalize_path()` helper

### Session Monitoring and Waiting

**CRITICAL**: When idle or waiting for work, **DO NOT finish the conversation**. Use blocking wait commands to keep the session active.

**CRITICAL**: **ALWAYS work on backlog items yourself when idle**. Don't just delegate - actively work on items directly.

**Proper Wait Patterns:**

1. **`thegent plan wait-next`** - Block until work is available (recommended for idle waiting)
 ```bash
 thegent plan wait-next --timeout 0 --poll 10
 ```
 - Blocks indefinitely (timeout 0)
 - Polls every N seconds
 - Keeps chat session active
 - Returns when work available

2. **`thegent plan loop`** - Continuous autonomous work loop (recommended for active processing)
 ```bash
 thegent plan loop --max 1000 --sleep 30
 ```
 - Processes work items continuously
 - Sleeps between iterations
 - Keeps session active while processing

3. **`thegent wait <session_id>`** - Wait for specific agent completion
 ```bash
 thegent wait <session_id> --timeout 300
 ```
 - Blocks until session completes
 - Useful for waiting on specific agents

**Anti-Pattern**: ❌ Don't finish the conversation when work is ongoing. Use wait commands instead.

**Pattern**: When you finish a task but work continues, **run `thegent plan wait-next` in the foreground** (not background) to block and keep the session active.

**CRITICAL**: Do not end conversations prematurely. Use `thegent plan wait-next` or `thegent plan loop` to maintain a monitor→act loop.

**CRITICAL - Continuous Work Mandate**:
- **When idle**: ALWAYS check backlog with `thegent plan do-next` and work on items DIRECTLY
- **Don't just delegate**: Work on items yourself using tools (read_file, search_replace, codebase_search, etc.)
- **Keep session alive**: Use `thegent plan wait-next` or `thegent plan loop` instead of finishing conversation
- **Check always**: Before finishing, always check if there's more work: `thegent plan get-next`
- **Never terminate**: Only terminate if explicitly told to stop or if truly no work exists

## Context Budget Rule

If task adds >2000 tokens of file content/output, **delegate it**.

---

# Optionality and Failure Behavior

**Require** dependencies where they belong; **require** clear, loud failures -- no silent or "graceful" degradation.

- **Force requirement where it belongs.** Do not make dependencies "optional" just to avoid failure. If a service or config is required for correctness, treat it as required and fail when missing.
- **Fail clearly, not silently.** Use explicit failures -- not reduced functionality, logging-only warnings, or hidden errors. Users must see *what* failed and that the process did not silently degrade.
- **Graceful in other ways.** Retries with visible feedback (e.g. "Waiting for X... (2/6)"); error messages that list each failing item; actionable messages and non-obscure stack traces. Do *not* use optionality or silent fallbacks as a substitute for fixing the real dependency.

---

# Planner Agents: No Code in Docs or Plans

**Planner agents** (PM, Analyst, Architect, etc.) must **never write code** in documentation and plans. Their job is to equip implementers. Write specs, acceptance criteria, architecture decisions, and clear handoffs. Prefer references, file paths, or brief pseudocode when necessary.

---

# Phased WBS and Plans with DAGs

When generating **plans**, **roadmaps**, or **implementation breakdowns**:

- **Phases:** Structure into ordered phases (Discovery, Design, Build, Test/Validate, Deploy/Handoff). Each phase contains deliverable-oriented work packages.
- **DAG:** Tasks have explicit **predecessors**; no cycles. List dependencies so execution order is unambiguous.
- **Output:** Phased WBS (hierarchy by phase) plus dependency list or DAG. Optionally: **Phase | Task ID | Description | Depends On** table.

---

# Timescales: Agent-Led, Aggressive Estimates

**Assume an agent-driven environment.** No user or external human intervention beyond prompts.

- **Forbidden in plans:** "Schedule external audit", "Stakeholder Presentation", "Team Kickoff", "Human checkpoint", "Get approval from X", or any step assigning work to a human.
- **Effort in agent terms only:** Agent actions (tool calls, subagent batches). Aggressive wall-clock -- err on the lower bound.
- **Rough mapping:**
  - Trivial change: 1-2 tool calls, <1 min
  - Small feature: 3-6 tool calls, 1-3 min
  - Cross-stack feature: 8-15 tool calls or 2-3 parallel subagents, 3-8 min
  - Major refactor: 15-30 tool calls or 3-5 parallel subagents, 8-20 min
  - Multi-phase initiative: decompose into agent batches; each batch 10-20 min max
- **Forbidden phrasing:** "This will take 2 days", "Schedule a review", "Assign owners", "Present to stakeholders". Use: "N tool calls", "N parallel subagents", "~M min wall clock".

---

# Conversation Dump Policy (Always Write Down)

**CRITICAL**: After any conversation that produces research, plans, decisions, or implementation details:

1. **Write a dump** to `docs/research/CONVERSATION_DUMP_YYYY-MM-DD.md` (or append to existing same-day file).
2. **Include:** Research findings, plans, decisions, fixes applied, open questions, next steps.
3. **Purpose:** Pick up later without hallucination; extend work across crashed sessions.
4. **Location:** Relevant project folder's `docs/` subfolder (e.g. `thegent/docs/research/`, `kush/docs/` for cross-project).
5. **Do not defer:** Write the dump as part of the same response/task. Do not say "I'll add it later."

**Format:** Use dated filename `CONVERSATION_DUMP_YYYY-MM-DD.md`. Sections: Issues Addressed, Fixes Applied, Research Findings, Plans, Open Questions, Cursor-Agent Recovery Note (if applicable).

**Cursor/Agent crashes:** If the user mentions crashed sessions, note in the dump that prior Cursor chat history (date X) should be manually reviewed and merged. Cursor stores chat in app state; export manually if needed.

**Tooling:** Use `thegent prompts sessions` to list Cursor/Codex/Claude sessions; `thegent prompts dump <session_id>` to dump a Cursor conversation to docs/research/. See `docs/guides/PROMPTS_TOOLING.md`.

See: `docs/research/CONVERSATION_DUMP_2026-02-16.md` for template.

---

# Thegent Command Reference for Agents

**CRITICAL**: This section provides comprehensive guidance on using thegent commands for agent execution, work stream integration, and delegation.

## Core Agent Execution Commands

### `thegent free` - Default Free Tier Agent (Recommended)

**Purpose**: Base free tier agent using Copilot gpt-5-mini. **Default choice for most tasks**.

**Basic Usage**:
```bash
thegent free "Task description"
```

**Work Stream Integration**:
```bash
# Run next work item from WORK_STREAM.md
thegent free --do-next

# Run next 5 work items sequentially
thegent free --do-next --repeat 5

# Background execution
thegent free "Long task" --bg
```

**Key Options**:
- `--do-next, -n`: Find next work item from plan do-next and run it
- `--repeat, -r <N>`: With --do-next: run up to N work packages sequentially
- `--mode, -m <mode>`: Execution mode (`read-only` | `write` | `full`, default: `write`)
- `--timeout, -t <seconds>`: Timeout (default: 300s from THGENT_DEFAULT_TIMEOUT_FREE)
- `--live/--no-live, -l`: Stream output live (default: on)
- `--bg, -b`: Run in background (async)
- `--diff, -D`: Suppress live stream; show diff/summary at end
- `--cd, -d <path>`: Working directory

**When to Use**:
- **Default choice** for most agent tasks
- Work stream integration (`--do-next`)
- Free tier cost optimization
- Background execution (`--bg`)

### `thegent run` - Foreground Agent with Full Control

**Purpose**: Run agent in foreground with full control, model routing, and real-time output.

**Basic Usage**:
```bash
thegent run "Task description" [agent]
```

**Model-First Routing** (Recommended when model matters):
```bash
# Model-first routing (auto-resolves provider)
thegent run "Task" -M gemini-3-flash

# Model-first with provider override
thegent run "Task" -M claude-sonnet-4.5 -P claude

# Model-first with routing policy
thegent run "Task" -M gemini-3-flash -R cheapest
```

**Key Options**:
- `--model, -M <model>`: Model override or model-first routing (when agent omitted)
- `--provider, -P <provider>`: Provider override for model-first routing
- `--routing, -R <policy>`: Routing policy (`prefer_direct` | `prefer_proxy` | `failover` | `round_robin` | `cheapest` | `cost_quality` | `pareto` | `roi`)
- `--mode, -m <mode>`: Execution mode (`read-only` | `write` | `full`, default: `write`)
- `--timeout, -t <seconds>`: Timeout hint (default: 90s)
- `--live`: Stream output live to terminal
- `--full, -f`: Show full raw output
- `--failover`: On failure, try next route (model-first only)
- `--include-contract`: Print resolved model route contract metadata
- `--retry --run-id <id>`: Retry failed run by run-id

**When to Use**:
- Need specific model/provider
- Need model-first routing
- Need routing policy control
- Foreground execution with live output
- Need contract metadata for debugging

### `thegent bg` - Background Agent Execution

**Purpose**: Start background run and register session. Non-blocking execution.

**Basic Usage**:
```bash
thegent bg "Task description" [agent]
```

**Session Management**:
```bash
# Start background task
thegent bg "Long task" free

# Continue from prior session
thegent bg "Continue task" -C <session_id>

# With owner tag
thegent bg "Task" --owner "project:feature"

# List running sessions
thegent ps

# Wait for session completion
thegent wait <session_id>

# Check session status
thegent status <session_id>
```

**Key Options** (inherits most from `run`):
- All `run` options plus:
- `--owner <tag>`: Session owner tag (default: `<user>:<cwd-name>`)
- `--format <format>`: Output format (`json` | `rich` (default) | `md` (agent-friendly))
- `--continuation, -C <session_id>`: Prior session id(s) to continue from (comma-separated)
- `--continuation-stderr`: Include stderr from prior session(s)

**When to Use**:
- Long-running tasks
- Non-blocking execution
- Session management needed
- Continuation from prior sessions
- Parallel task execution

### Role-Based Commands

**Purpose**: Run tasks with role-based system prompts.

**Commands**:
- `thegent summarize <prompt>`: Summarize content with brevity and key takeaways
- `thegent research <prompt>`: Deep dive research and comprehensive information gathering
- `thegent review <prompt>`: Critical analysis and quality checks for code or documentation
- `thegent explain <prompt>`: Explain code or concepts
- `thegent fix <prompt>`: Fix issues in code
- `thegent code <prompt>`: Generate or modify code

**Options** (all role commands):
- `--cd, -d <path>`: Working directory
- `--mode, -m <mode>`: Mode (`read-only` | `write` | `full`, default: `write`)
- `--timeout, -t <seconds>`: Timeout hint
- `--bg, -b`: Run in background
- `--model, -M <model>`: Model override
- `--live`: Stream output live

**Default Agent**: Uses virtual 'role' agent which defaults to `gemini-3-flash` unless `--agent` or `--model` specified.

**Examples**:
```bash
# Research task
thegent research "Latest VitePress plugins" --bg

# Code review
thegent review "Review auth.py for security issues"

# Code generation
thegent code "Implement user authentication"
```

## Work Stream Integration Commands

### `thegent plan do-next` - Find Next Work Items

**Purpose**: Find next actionable work items from WORK_STREAM.md, PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue.

**Usage**:
```bash
# Get next 5 work items (default)
thegent plan do-next

# Get next 10 work items
thegent plan do-next --limit 10

# JSON output for scripting
thegent plan do-next --format json
```

**Output**: List of actionable work items with IDs, prompts, dependencies, status.

### `thegent plan get-next` - Get First Work Item Prompt

**Purpose**: Get first work item prompt for scripting. Returns prompt only (plain text).

**Usage**:
```bash
# Get prompt for scripting
PROMPT=$(thegent plan get-next)
thegent free "$PROMPT"

# JSON format
thegent plan get-next --format json
```

**Use Case**: Scripting integration, e.g., `PROMPT=$(thegent plan get-next)`

### `thegent plan loop` - Continuous Work Loop (RECOMMENDED)

**Purpose**: Loop: get next item -> run bg -> repeat until no items or --max reached.

**Usage**:
```bash
# Continuous loop (unbounded, recommended)
thegent plan loop

# Loop with max 10 iterations
thegent plan loop --max 10

# Loop with custom agent and sleep interval
thegent plan loop --agent codex --sleep 10

# Dry run (see what would run)
thegent plan loop --dry-run
```

**Behavior**:
1. Get next work item via `plan do-next`
2. Run item in background with specified agent (default: `free`)
3. Sleep for specified interval (default: 5s)
4. Repeat until no items or max iterations reached

**When to Use**: **Recommended pattern for continuous autonomous work**. Use instead of bash loops.

### `thegent plan wait-next` - Block Until Work Ready

**Purpose**: Block until next actionable work exists (DAG ready, do-next, escalation, inbox).

**Usage**:
```bash
# Wait for any work
thegent plan wait-next

# Wait with timeout
thegent plan wait-next --timeout 300

# Wait for specific sources
thegent plan wait-next --sources dag,do_next

# Custom poll interval
thegent plan wait-next --poll 5
```

**Use Case**: **Idle waiting instead of busy loops**. Blocks until work is available.

**Options**:
- `--poll, -p <seconds>`: Poll interval (default: 2.0s)
- `--timeout, -t <seconds>`: Max wait time (0=unbounded, default: 0.0)
- `--sources, -s <sources>`: Comma-separated: `dag,do_next,escalation,inbox` (default: all)

### `thegent plan incorporate` - Merge Fragments into Work Stream

**Purpose**: Merge fragments from 02-UNIFIED-WBS.md, docs/plans/, docs/research/, docs/docset/ into WORK_STREAM.md.

**Usage**:
```bash
# Incorporate fragments
thegent plan incorporate

# Dry run
thegent plan incorporate --dry-run
```

**Behavior**:
- Scans `docs/plans/`, `docs/research/`, `docs/docset/` for fragments
- Extracts work items from fragments
- Merges into WORK_STREAM.md
- Resolves conflicts automatically
- Preserves CLAIMED and COMPLETED sections

### `thegent plan claim` / `thegent plan complete` - Work Stream Management

**Purpose**: Claim or complete items in unified work stream.

**Usage**:
```bash
# Claim work item
thegent plan claim research-library-http

# Complete work item
thegent plan complete research-library-http
```

**Options**:
- `--cd, -d <path>`: Project directory
- `agent_id`: Agent ID (auto-detected if missing)

## Background Execution and Session Management

### `thegent ps` - List Running Sessions

**Purpose**: List active background sessions.

**Usage**:
```bash
# List running sessions
thegent ps

# List all sessions (including exited)
thegent ps --all

# Filter by owner
thegent ps --owner "project:feature"

# JSON output
thegent ps --format json
```

**Output**: Table of sessions with ID, agent, prompt, status, started time, etc.

### `thegent wait` - Wait for Session Completion

**Purpose**: Block until session exits.

**Usage**:
```bash
# Wait for session
thegent wait <session_id>

# Wait with timeout
thegent wait <session_id> --timeout 300
```

**Use Case**: **Idle waiting instead of busy loops**. Blocks until session completes.

**Options**:
- `--timeout <seconds>`: Max wait time (0=unbounded)
- `--poll <seconds>`: Poll interval (default: 1.0s)

### `thegent status` - Check Session Status

**Purpose**: Check status of a background session.

**Usage**:
```bash
thegent status <session_id>
```

**Output**: Session status, metadata, output summary.

### `thegent kill` - Terminate Session

**Purpose**: Terminate a running session.

**Usage**:
```bash
thegent kill <session_id>

# Force kill
thegent kill <session_id> --force
```

## Model Routing and Provider Options

### Available Providers

| Provider | Type | Default Model | Notes |
|----------|------|---------------|-------|
| `free` | Direct | `gpt-5-mini` | Copilot free tier (recommended default) |
| `claude` | Direct | `claude-haiku-4.5` | Anthropic Claude API |
| `gemini` | Direct | `gemini-3-flash` | Google Gemini API |
| `copilot` | Direct | `gpt-5-mini` | GitHub Copilot |
| `codex` | Direct | `gpt-5.3-codex` | Codex API |
| `cursor` | Proxy | `gemini-3-flash` | Cursor API (wisdgod) |
| `antigravity` | Proxy | `gemini-3-flash` | Antigravity proxy |
| `minimax` | Proxy | `minimax-m2.5` | MiniMax API |
| `glm` | Proxy | `glm-5` | Zhipu GLM API |
| `nim` | Proxy | `step-3.5-flash` | NVIDIA NIM |
| `kilo` | Proxy | `minimax-m2.5` | Kilo proxy |
| `kiro` | Proxy | `claude-haiku-4.5` | Kiro proxy |

### Model-First Routing

**When to Use**: Specify model without provider, let thegent resolve provider automatically.

**Syntax**:
```bash
thegent run "Task" -M <model> [--provider <provider>] [--routing <policy>]
```

**Examples**:
```bash
# Model-first with auto provider resolution
thegent run "Task" -M gemini-3-flash

# Model-first with provider override
thegent run "Task" -M claude-sonnet-4.5 -P claude

# Model-first with routing policy
thegent run "Task" -M gemini-3-flash -R cheapest

# Model-first with failover
thegent run "Task" -M gemini-3-flash --failover
```

### Routing Policies

| Policy | Description | Use Case |
|--------|-------------|----------|
| `prefer_direct` | Prefer direct provider connections | Low latency, high reliability (default) |
| `prefer_proxy` | Prefer proxy connections | Cost optimization, rate limit handling |
| `failover` | Try primary, fallback on failure | High availability |
| `round_robin` | Distribute across routes | Load balancing |
| `cheapest` | Select cheapest route | Cost optimization |
| `cost_quality` | Balance cost and quality | Optimal value |
| `pareto` | Pareto frontier optimization | Multi-objective optimization |
| `roi` | Return on investment optimization | Business value |

## Agent Usage Patterns

### Pattern 1: Continuous Autonomous Work (RECOMMENDED)

**Use Case**: Agent should continuously process work items from work stream.

**Pattern**:
```bash
thegent plan loop
```

**Why**: 
- Automatic work item discovery
- Background execution
- Non-blocking
- Handles all edge cases
- No manual iteration needed

### Pattern 2: Single Work Item Execution

**Use Case**: Execute single work item from work stream.

**Pattern**:
```bash
thegent free --do-next
```

**Variations**:
```bash
# Run next 5 items sequentially
thegent free --do-next --repeat 5

# With specific agent
thegent run --do-next codex -M claude-sonnet-4.5
```

### Pattern 3: Idle Waiting (Instead of Busy Loops)

**Use Case**: Wait for work to become available.

**Bad Pattern** (busy loop):
```bash
while true; do
  sleep 5
  # check work manually
done
```

**Good Pattern**:
```bash
thegent plan wait-next
```

**Variations**:
```bash
# Wait with timeout
thegent plan wait-next --timeout 300

# Wait for specific sources
thegent plan wait-next --sources dag,do_next
```

### Pattern 4: Background Execution with Session Management

**Use Case**: Long-running or parallel tasks.

**Pattern**:
```bash
# Start background task
thegent bg "Long task" free

# Monitor sessions
thegent ps

# Wait for completion
thegent wait <session_id>

# Check status
thegent status <session_id>
```

### Pattern 5: Model-Specific Routing

**Use Case**: Need specific model capabilities.

**Pattern**:
```bash
# Model-first routing
thegent run "Complex task" -M claude-sonnet-4.5

# With routing policy
thegent run "Cost-sensitive task" -M gemini-3-flash -R cheapest

# With failover
thegent run "Critical task" -M claude-opus-4.6 --failover
```

### Pattern 6: Continuation from Prior Sessions

**Use Case**: Continue work from prior session.

**Pattern**:
```bash
# Continue from prior session
thegent bg "Continue implementation" -C <session_id>

# Continue with stderr
thegent bg "Debug issue" -C <session_id> --continuation-stderr
```

## Command Selection Guide

| Task Type | Command | Notes |
|-----------|---------|-------|
| **Default choice** | `thegent free` | Free tier, work stream integration |
| Single task, foreground | `thegent run` or `thegent free` | Use `free` for default, `run` for control |
| Single task, background | `thegent bg` or `thegent free --bg` | Use `bg` for session management |
| **Work stream integration** | `thegent free --do-next` | Automatic work item selection |
| **Continuous autonomous work** | `thegent plan loop` | **Recommended for autonomous agents** |
| **Idle waiting** | `thegent plan wait-next` | **Instead of busy loops** |
| Model-specific routing | `thegent run -M <model>` | Model-first routing |
| Cost optimization | `thegent run -R cheapest` | Use cheapest routing policy |
| Long-running tasks | `thegent bg` | Background execution with session management |
| Parallel tasks | Multiple `thegent bg` calls | Start multiple background tasks |

## Best Practices

1. **Use `thegent plan loop`** for continuous autonomous work (recommended)
2. **Use `thegent plan wait-next`** instead of busy loops
3. **Use `thegent free`** as default agent (free tier, work stream integration)
4. **Use `thegent bg`** for long-running or parallel tasks
5. **Use model-first routing** (`-M`) when model matters more than provider
6. **Use routing policies** (`-R`) for cost/quality optimization
7. **Use `--do-next`** for automatic work stream integration
8. **Use `--repeat`** for sequential work item execution
9. **Use session management** (`ps`, `wait`, `status`) for background tasks
10. **Use `--continuation`** to continue from prior sessions

## Anti-Patterns to Avoid

1. **Don't use busy loops**: Use `plan wait-next` or `wait <session_id>`
2. **Don't use bash wrappers**: Use native `--repeat`, `--do-next`, `plan loop`
3. **Don't poll manually**: Use `plan wait-next` with polling
4. **Don't ignore work stream**: Use `plan do-next` and `plan incorporate`
5. **Don't hardcode agents**: Use `free` as default, override when needed
6. **Don't use `ls -l` in project root**: Use `fd` or subdirectories (see Directory Listing section)

## Environment Variables

### Timeout Configuration
- `THGENT_DEFAULT_TIMEOUT`: Default agent timeout (default: 90s)
- `THGENT_DEFAULT_TIMEOUT_CLAUDE`: Claude agent timeout (default: 300s)
- `THGENT_DEFAULT_TIMEOUT_FREE`: Free agent timeout (default: 300s)

### Routing Configuration
- `THGENT_DEFAULT_ROUTING`: Default routing policy (`prefer_direct` | `prefer_proxy`)

### Session Configuration
- `THGENT_OWNER_TAG`: Explicit owner tag override
- `THGENT_OWNER_SCOPE`: Owner scope (supports `{user}`, `{uid}`, `{pid}`, `{ppid}`, `{cwd}` placeholders)

### Debug Configuration
- `THGENT_DEBUG`: Enable debug mode (1=enabled)

---

# Documentation Organization

**CRITICAL**: All project documentation follows a strict organization structure.

### Root-Level Files (Keep in Root)
- `README.md` -- Main project documentation
- `CHANGELOG.md` -- Project changelog
- `AGENTS.md` -- AI agent instructions
- `CLAUDE.md` -- Claude-specific instructions
- `00_START_HERE.md` -- Getting started guide (if applicable)
- Spec docs: `PRD.md`, `ADR.md`, `FUNCTIONAL_REQUIREMENTS.md`, `PLAN.md`, `USER_JOURNEYS.md`

### Documentation Structure

All other `.md` files must be organized in `docs/` subdirectories:

```
docs/
  guides/              # Implementation guides and how-tos
    quick-start/       # Quick start guides
  reports/             # Completion reports, summaries, status reports
  research/            # Research summaries, indexes, analysis
  reference/           # Quick references, API references, trackers
  checklists/          # Implementation checklists, verification lists
  changes/             # Per-change proposal/design/task docs
    archive/           # Completed change docs
```

### File Organization Rules

1. **Quick Starts** -> `docs/guides/quick-start/` (`*QUICK_START*.md`, `*QUICKSTART*.md`)
2. **Quick References** -> `docs/reference/` (`*QUICK_REFERENCE*.md`, `*QUICK_REF*.md`)
3. **Implementation Guides** -> `docs/guides/` (`*GUIDE*.md`)
4. **Completion Reports** -> `docs/reports/` (`*COMPLETE*.md`, `*SUMMARY*.md`, `*REPORT*.md`, `PHASE_*.md`, `*TEST*.md`)
5. **Research Files** -> `docs/research/` (`*RESEARCH*.md`, `*INDEX*.md`)
6. **Checklists** -> `docs/checklists/` (`*CHECKLIST*.md`)
7. **Trackers** -> `docs/reference/` (`*TRACKER*.md`, `*STATUS*.md`, `*MAP*.md`)

### AI Agent Instructions

- **NEVER** create `.md` files in the project root (except allowed root-level files above)
- **ALWAYS** place new documentation in the appropriate `docs/` subdirectory
- **VERIFY** file location before creating documentation
- **MOVE** misplaced files to correct subdirectories if found

---

# Opinionated Quality Enforcement

- Enforce opinionated styling to a strict degree.
- Programmatic enforcement must guard against bad quality and antipatterns.
- Rather than disables or ignores, fix code properly.
- Use project linters, formatters, and type checkers. Never bypass them.

---

# Specification Documentation System

## Required Project Documentation

Every non-trivial project SHOULD maintain these spec docs (root level):

| File | Purpose |
|------|---------|
| `PRD.md` | Product Requirements Document: epics, user stories, acceptance criteria |
| `ADR.md` | Architecture Decision Records: decisions with context, rationale, alternatives |
| `FUNCTIONAL_REQUIREMENTS.md` | Functional Requirements: SHALL statements, traces to PRD |
| `PLAN.md` | Phased WBS with DAG dependencies |
| `USER_JOURNEYS.md` | User journeys with ASCII flow diagrams |

## Required Tracker Documentation

Projects with spec docs SHOULD maintain trackers in `docs/reference/`:

| File | Purpose |
|------|---------|
| `PRD_TRACKER.md` | Epic/story status, progress %, code locations |
| `ADR_STATUS.md` | ADR implementation status, code artifacts |
| `FR_TRACKER.md` | FR implementation status, test coverage |
| `PLAN_STATUS.md` | Phase/task completion status |
| `JOURNEY_VALIDATION.md` | Journey validation status, gaps |
| `CODE_ENTITY_MAP.md` | Forward and reverse mapping: code entities <-> requirements |

## Auto-Detection Behavior

**On session start:**
- If spec docs are missing, acknowledge it and offer to generate them
- Greenfield project: offer to scaffold all spec docs from project analysis
- Brownfield project: offer to analyze existing codebase and generate docs mapping to what exists
- Do NOT auto-generate without user confirmation -- offer, don't force

## VitePress Docsite Setup (Greenfield/Brownfield)

**MUST include docsite setup in any new project initialization:**

For greenfield projects:
- Copy VitePress template from `thegent/templates/vitepress-full/` to new project
- Run `pnpm install && pnpm docs:build` to verify setup
- Document in project CLAUDE.md

For brownfield projects (existing projects without docsites):
- Check if `docs-dist/index.html` exists -- if not, propose adding docsite
- Use same template from `thegent/templates/vitepress-full/`
- Run `pnpm install && pnpm docs:build` to verify

**Quick setup (30 seconds):**
```bash
cp -r thegent/templates/vitepress-full myproject/docs/.vitepress
# Rename .template files, edit config.ts placeholders
cd myproject && pnpm install && pnpm docs:build
open docs-dist/index.html
```

**Why:** All projects should have statically viewable docs that can be opened via `file://` in browser.

---

## Project Setup Checklist (Greenfield/Brownfield)

**MUST initialize these for ALL new projects:**

### 1. Docsite (VitePress)
- [ ] Copy `thegent/templates/vitepress-full/` to `docs/.vitepress/`
- [ ] Run `pnpm install && pnpm docs:build`
- [ ] Verify `docs-dist/index.html` opens in browser
- [ ] Add to CLAUDE.md

### 2. Taskfile (NOT Make)
- [ ] Create `Taskfile.yml` with standard tasks:
  - `lint` - Run all linters
  - `test` - Run tests
  - `quality` - Run quality gates
  - `docs:build` - Build docsite

### 3. Linters (Language-Specific)
| Stack | Linter | Formatter | Config Template |
|-------|--------|-----------|---------------|
| Python | ruff | ruff format | `thegent/templates/python/pyproject.template.toml` |
| Python | pyright/pylance | - | `thegent/templates/quality/pyrightconfig.json` |
| Python | ty | - | `thegent/templates/quality/ty-config.toml` |
| Python | basedpyright | - | `thegent/templates/quality/basedpyrightconfig.json` |
| Python | mypy | - | `pyproject.toml` `[tool.mypy]` |
| Python | zuban | - | CLI flags (see `templates/quality/zuban-config.md`) |
| TypeScript | oxlint | oxfmt/prettier | `thegent/templates/typescript/oxlint.config.json` |
| Go | golangci-lint | gofumpt | `thegent/templates/go/.golangci.yml` |
| Rust | clippy | rustfmt | `thegent/templates/rust/clippy.toml` |
| Ruby | rubocop | rubocop | `thegent/templates/ruby/.rubocop.yml` |
| Java | checkstyle + spotbugs | google-java-format | `thegent/templates/java/checkstyle.xml` |
| C/C++ | clang-tidy | clang-format | `thegent/templates/cpp/.clang-tidy` |
| PHP | phpstan + psalm | PHP CS Fixer | `thegent/templates/php/phpstan.neon` |
| Bash | shellcheck | shfmt | `thegent/templates/bash/.shellcheckrc` |

**Python Type Checking (Dual Approach):**

**IDE (Real-time IntelliSense):**
- **Pyright/Pylance**: Copy `templates/quality/pyrightconfig.json` to project root
- Aggressive excludes prevent indexing large directories (`.venv`, `.worktrees`, `site-packages`, etc.)
- Configured for optimal performance in monorepos and workspaces
- See: `docs/guides/PYTHON_IDE_PERFORMANCE_SETUP.md`

**CI/Linting (Batch Checking):**
- **Fast path**: `ty` + `zuban` (10-50x faster than Pyright) - use for quick feedback
- **Strict path**: `basedpyright` + `mypy` (comprehensive) - use for CI/commit validation
- Configuration in `pyproject.toml`: `[tool.ty]`, `[tool.basedpyright]`, `[tool.mypy]`
- See: `docs/guides/COMPLETE_TYPE_CHECKER_SETUP.md`

**Setup:**
1. Copy `templates/python/pyproject.template.toml` type checker sections to `pyproject.toml`
2. Copy `templates/quality/pyrightconfig.json` to project root
3. Copy `templates/ide/.vscode/settings.json` to `.vscode/settings.json`
4. Add Taskfile tasks: `lint:type` (fast) and `lint:strict` (strict)
5. Configure pre-commit hooks: `ty` + `basedpyright`

### 4. Project Scaffolding Tools (CLI/App Frameworks)
| Stack | CLI Framework | Web Framework | Config |
|-------|--------------|---------------|--------|
| Python | typer | FastAPI/starlette | `pyproject.toml` |
| TypeScript | commander.js | Express/Fastify/Hono | `package.json` |
| Rust | clap | axum/actix | `Cargo.toml` |
| Go | cobra/urfave/cli | gin/echo/fiber | `go.mod` |
| Ruby | thor | Rails/Hanami | `Gemfile` |
| Java | picocli | Spring Boot | `pom.xml`/`build.gradle` |
| C# | commandline | ASP.NET Core | `.csproj` |

### 5. IDE Configuration (VS Code/Cursor)
- [ ] Copy `templates/ide/.vscode/settings.json` to `.vscode/settings.json` in project root
- [ ] Ensures Pylance is used (not Jedi) for optimal performance
- [ ] Configures file watcher and search exclusions for performance
- [ ] Sets up Python formatting with Ruff

**Performance Benefits:**
- Pylance language server (faster than Jedi)
- Aggressive file watcher exclusions (prevents indexing `.venv`, `.worktrees`, etc.)
- Search exclusions for build artifacts and dependencies
- Optimized memory settings for large files

### 6. Pre-commit Hooks
- [ ] Add `.pre-commit-config.yaml`
- [ ] Include: ruff-check, ruff-format, gitleaks, trailing-whitespace
- [ ] Run `pre-commit install`

### 7. Quality Gates
- [ ] Create `hooks/quality-gate.sh` with lint/test/coverage/security checks
- [ ] Run on pre-commit or Stop hook

### 8. Test Infrastructure (Per Language)
| Stack | Test Runner | Coverage | Test Config |
|-------|-------------|----------|-------------|
| Python | pytest + pytest-xdist | coverage.py | `pyproject.toml` [tool.pytest] |
| TypeScript | vitest | v8 | `vitest.config.ts` |
| Rust | cargo test | tarpaulin/grcov | `Cargo.toml` |
| Go | go test | gocov/coverprofile | `_test.go` files |
| Ruby | rspec | simplecov | `.rspec` |
| Java | JUnit 5 | JaCoCo | `pom.xml`/`build.gradle` |
| C++ | catch2/doctest | lcov | `CMakeLists.txt` |
| PHP | phpunit | phpunit-coverage | `phpunit.xml` |
| Bash | bats-core | - | `*.bats` files |

### 9. Full Traceability Setup
- [ ] Create `FUNCTIONAL_REQUIREMENTS.md` with FR-{CAT}-NNN IDs
- [ ] Create `docs/reference/FR_TRACKER.md` to track FR implementation status
- [ ] Create `docs/reference/CODE_ENTITY_MAP.md` mapping code <-> requirements
- [ ] Add FR ID tags to all test functions:
  - Python: `@pytest.mark.requirement("FR-XXX-NNN")`
  - TypeScript: `describe("FR-XXX-NNN: description", () => {...})`
  - Rust: `#[test] fn test_FR_XXX_NNN() {...}`
  - Add docstring: `Traces to: FR-XXX-NNN`
- [ ] Verify: `grep -r "FR-" tests/` shows all FRs have tests
- [ ] Run: `task quality` to verify spec verification

### 10. CLAUDE.md Project Instructions
Create project-specific CLAUDE.md with project info, library preferences, domain patterns.

---

## Quick Project Initialization

### Option 1: Copier (Recommended)
```bash
# Install copier if needed
pip install copier

# Initialize with all prompts
copier copy thegent/templates/initialize-project ./my-new-project

# Or with options specified
copier copy thegent/templates/initialize-project ./my-new-project \
  --project-name="my-project" \
  --project-description="A description" \
  --language="python" \
  --include-docs=true \
  --include-ci=true
```

### Option 2: Manual Template Selection
```bash
# Full setup for new project:
mkdir -p docs hooks
cp -r thegent/templates/vitepress-full/* docs/.vitepress/
mv docs/package.json.template docs/package.json
pnpm install && pnpm docs:build
open docs-dist/index.html
```

### Available Templates

| Template | Location | Purpose |
|----------|----------|---------|
| CLAUDE.md | `templates/claude/CLAUDE.md.template` | Project-specific agent instructions |
| Taskfile | `templates/{language}/Taskfile.{language}.yml` | Build automation |
| Quality | `templates/quality/` | 50+ lint/coverage configs for 25+ languages |
| VitePress | `templates/vitepress-full/` | Full docsite with versioning |
| Specs | `templates/specs/` | PRD, ADR, FR, PLAN templates |
| CI/CD | `templates/operational/ci/` | GitHub Actions workflows |
| Docker | `templates/operational/docker/` | Dockerfiles & compose |

**During work:**
- When making significant code changes (new modules, features, architecture changes), note which spec docs would need updating
- When completing a task, mentally check if trackers should be updated
- If you add new functions/modules, note they should be added to CODE_ENTITY_MAP.md

**On session end:**
- If there are unmapped code changes, acknowledge and update trackers if appropriate
- Treat session end as a documentation checkpoint

## Change Documentation (per-change, for significant changes)

For significant changes (new features, major refactors, architecture changes):
- Create `docs/changes/{change-name}/` with:
  - `proposal.md` -- What and why
  - `design.md` -- Technical approach, affected components
  - `tasks.md` -- Implementation checklist
- Archive completed changes to `docs/changes/archive/`
- NOT required for small fixes, typos, or minor adjustments

## Doc Format Standards

- **ID systems:** E{n}.{m}.{k} for epics/stories, FR-{CAT}-{NNN} for requirements, ADR-{NNN} for decisions, P{n}.{m} for plan tasks, UJ-{N} for journeys
- **Cross-reference** between docs (FR traces to PRD epics, code maps to FRs and ADRs)
- **ASCII diagrams** for flows and architecture (not images)
- **Tables** for tracking, matrices, and summaries
- Templates are available at `~/.claude/templates/` for consistent formatting (if present)

### Global Reference Docs for Code Generation

**Use these references when generating code:**

| Domain | Reference Path |
|--------|---------------|
| UI Design | `docs/reference/UI_DESIGN_PRINCIPLES_REFERENCE.md` |
| Architecture | `docs/reference/SOFTWARE_ARCHITECTURE_REFERENCE.md` |
| Design Patterns | `docs/reference/SOFTWARE_DESIGN_PATTERNS_REFERENCE.md` |
| Performance | `docs/reference/performance/PERFORMANCE_OPTIMIZATION.md` |
| Testing | `docs/reference/testing/TESTING_STRATEGIES.md` |
| Security | `docs/reference/security/SECURITY_BEST_PRACTICES.md` |
| **Full Index** | `docs/reference/INDEX.md` |

For hyperspecialization, agents can use `docs/reference/INDEX.md` to find domain-specific references mapped to their roles.

## Session State Continuity

- The hooks system (if configured) tracks file changes per session via `.claude/session-changes.log`
- On stop, changes are reconciled against trackers
- This provides session-to-session continuity for documentation maintenance

---

# Generalized Dev Environment Pattern

## Service Management

- **The user runs a dev TUI/dashboard in their own terminal.** This is their primary observation interface. **Never** start, stop, or restart the entire dev stack (`make dev`, `make dev-tui`, `make dev-down`) — only the user does that.
- **Use CLI introspection and per-service manipulation commands** to interact with the running stack without disrupting the user's TUI session. Process orchestrators (e.g. `process-compose`) expose a CLI/API that operates on the same running instance.
- **Assume services use hot reload** (file watchers, HMR, etc.). Save files and let watchers pick up changes — do not restart services just because you edited files.
- **When a service needs restarting** (e.g. config change, dependency update, crash), restart only that specific service via CLI, not the whole stack.
- **Read logs via CLI or log files** — never attach to or interfere with the user's TUI terminal.
- Before starting dev yourself, verify processes are not already up (check health endpoints, status commands, or log files) to avoid duplicate stacks.

## Package Manager

**Use the project's preferred package manager.** Detect from lockfiles:
- `bun.lockb` or `bun.lock` -> use `bun`
- `pnpm-lock.yaml` -> use `pnpm`
- `yarn.lock` -> use `yarn`
- `package-lock.json` -> use `npm`
- If unclear, check `package.json` `packageManager` field or project CLAUDE.md

## Native Over Docker

**Prefer native services over Docker** for local development. Run databases, caches, reverse proxies as native processes. Use Docker only when native install is not feasible or explicitly required.

## OSS and Free First

**Strictly prefer local, OSS, and free tools** over paid SaaS. If a feature requires external services, prefer OSS/self-hosted or free options first. Document paid options only as labeled fallback.

## Multi-Actor Coordination (generalized)

When multiple agents or actors share a dev environment:
- **Concurrent Agent Environment**: Assume multiple agents are working in the same workspace simultaneously.
- **Git Safety - FORBIDDEN**: Never run `git restore`, `git reset`, or `git clean` on the workspace. These commands destroy work-in-progress from other agents.
- **Respect Dirty Files**: Modified files are active work-in-progress. Do not revert, "cleanup", or overwrite them unless specifically instructed to finish a task started by another agent. Work around existing changes.
- **Debounce commands:** Use project-provided wrappers (Makefile targets, scripts) that prevent concurrent execution conflicts.
- **Shared service management:** Use the project's process orchestrator as source of truth for service health.
- **Hold-if-running logic:** Prefer wrappers that allow multiple actors to share processes without force-killing.
- **Consolidated targets:** Prefer consolidated build/lint/test targets over a multitude of specialized ones.

---

# Plugin Ecosystem Awareness

Documentation and workflow frameworks (BMAD, OpenSpec, GSD, etc.) may be available as plugins or slash commands.

- Check available slash commands (`/`) for documentation workflows
- These complement the auto-detection system -- invoke explicitly for deeper workflows
- Auto-detection hooks handle common cases; plugins handle advanced scenarios
- If BMAD agents are installed (`.claude/commands/bmad/`), they can be activated via slash commands for specialized agent personas
- Start a new conversation to switch agent personas

---

# QA Governance

## Test-First Mandate

- Write tests BEFORE implementation. Test file must exist before source file for new modules.
- For bug fixes, write a failing test that reproduces the bug first, then fix.
- Test naming: descriptive, includes the FR ID when applicable.

## Suppression Policy

- **Zero new suppressions** without inline justification comment.
- Acceptable format: `# noqa: E501 -- line is a long URL` (note the `--` reason separator).
- The `suppression-blocker.sh` hook will BLOCK any Write/Edit that introduces new suppressions.
- If a suppression is genuinely needed, include the specific rule code AND a reason.

## Spec Traceability

- All test functions MUST reference an FR ID via one of:
  - Tag: `# @trace FR-XXX-NNN` in test file or function
  - Marker: `@pytest.mark.requirement("FR-XXX-NNN")`
  - Docstring: `Traces to: FR-XXX-NNN`
  - Test name: `@test "FR-XXX-NNN: description"` (BATS)
- Orphaned FRs (no test) and orphaned tests (no FR) are reported by the quality gate.

## Quality Gate Awareness

- `quality-gate.sh` runs on every Stop event -- it reports lint, security, and traceability findings.
- **Proactively run linters** before finishing work to avoid surprises at the quality gate.
- The gate is advisory (does not block Stop) but findings should be addressed.

## Static Analysis Config

- When scaffolding a new project, copy relevant templates from `~/.claude/templates/quality/` for detected stacks.
- Available templates: ruff.toml, ty-config.toml, oxlintrc.json, tsconfig-strict.json, golangci.yml, clippy.toml, shellcheckrc, pre-commit-config.yaml, pytest-config.toml, coverage-config.toml.

## Test Pyramid Targets

**CRITICAL: Agent-Only Environment Requirement**

Since **NO humans will test this system** - only agents will use it - we require **100% coverage** for all test types:

- **E2E**: **100%** of all CLI commands (CRITICAL - agents interact at CLI boundary)
- **Integration**: **100%** of all workflows (CRITICAL - cross-component behavior)
- **Unit**: **100%** of all functions (ESSENTIAL - isolated behavior)

**Why 100%?** In agent-only environments:
- ❌ NO humans will manually test commands
- ❌ NO manual verification possible
- ✅ **ONLY automated tests can verify behavior**
- ✅ **100% coverage is REQUIRED, not optional**

**Legacy Projects** (with human testers) may override in `.qa-config.json` or `.claude/quality.json`:
- **Unit**: 70% (tolerance: +/-5%)
- **Integration**: 20% (tolerance: +/-5%)
- **E2E**: 10% (tolerance: +/-5%)

**Agent-Only Projects** (thegent and similar): **100% coverage required for all types**.

## Hook Pipeline Summary (v3)

| Event | Hooks (execution order) |
|-------|------------------------|
| SessionStart | spec-preflight, qa-preflight |
| UserPromptSubmit | prompt-submit-guard |
| PreToolUse:Write | doc-location-guard, pre-write-validator, suppression-blocker |
| PreToolUse:Edit | pre-write-validator, suppression-blocker |
| PostToolUse:Edit\|Write | change-doc-tracker, post-edit-checker, async-test-runner |
| SubagentStart | subagent-quality-gate (start) |
| SubagentStop | subagent-quality-gate (stop) |
| TaskCompleted | task-completion-verifier |
| PreCompact | pre-compact-snapshot |
| Stop | quality-gate, stop-reconcile, spec-verifier, complexity-ratchet, security-pipeline, test-maturity |
| SessionEnd | session-cleanup |

## Test-First Development (TDD/BDD)

### TDD Mandate
- For NEW modules: test file MUST exist before implementation file
- For BUG FIXES: failing test MUST be written before the fix
- For REFACTORS: existing tests must pass before AND after

### BDD Requirements
- Feature files (*.feature / *.bdd) map to user stories in PRD
- Given/When/Then steps must be traceable to FRs
- BDD test names reference FR IDs: "Feature: FR-AUTH-001 User Login"

### Test Type Requirements (by project maturity)

**Agent-Only Projects** (thegent and similar): **ALL test types REQUIRED at 100% coverage**

| Test Type | New Project | Established | Critical System | **Agent-Only** |
|-----------|-------------|-------------|-----------------|----------------|
| Unit | Required | Required | Required | **Required (100%)** |
| Integration | Required | Required | Required | **Required (100%)** |
| E2E | Optional | Required | Required | **Required (100%)** |
| Property-based | Optional | Optional | Required | **Required** |
| Contract | Optional | Required (if APIs) | Required | **Required** |
| Mutation | Optional | Optional | Required | **Required (80%+)** |
| Security (SAST) | Required | Required | Required | **Required** |
| Accessibility | Optional | Required (if UI) | Required | **Required (if UI)** |
| Performance | Optional | Optional | Required | **Required** |
| Snapshot/Golden | Optional | Optional (if UI) | Required | **Required (if UI)** |

**Agent-Only Rationale**: Since NO humans test the system, automated tests MUST cover every user journey, workflow, and function. E2E tests are MORE critical than unit tests because agents interact at the CLI/API boundary.

### Smart Contract Pattern (Spec Verification)
Specs (PRD/FR) -> Tests (must reference FR IDs) -> Checks (must be green) = Verified
- Every FR-XXX-NNN in FUNCTIONAL_REQUIREMENTS.md MUST have >=1 test referencing it
- Every test MUST reference >=1 FR-XXX-NNN (no orphan tests)
- All linters + type checkers + security scanners MUST pass (0 errors)
- **Coverage MUST meet threshold**:
  - **Agent-Only Projects**: **100%** (E2E, Integration, Unit)
  - **Legacy Projects**: 80% (default)
- If ALL checks green AND ALL FRs have tests -> spec is "programmatically verified"

**Agent-Only Requirement**: Every CLI command MUST have E2E tests. Every workflow MUST have integration tests. Every function MUST have unit tests. See `docs/governance/AGENT_ONLY_TEST_STRATEGY.md` and `docs/governance/TDD_BDD_SDD_GOVERNANCE.md`.

### Architecture Enforcement
- Python: import-linter config enforces layer boundaries
- Go: depguard in golangci.yml enforces package dependency rules
- TypeScript: eslint-plugin-boundaries enforces module boundaries
- When scaffolding: always add architecture enforcement config

### Universal Language Support

The QA system supports 25+ language stacks. See `~/.claude/qa-config.json` for the full list.
Stack detection is automatic via marker files (package.json, go.mod, Cargo.toml, etc.).
Quality templates for all supported languages are in `~/.claude/templates/quality/`.

## Subagent Quality Enforcement

Subagents and tasks are NOT exempt from quality gates. The following hooks fire on subagent lifecycle:
- SubagentStart: tracks subagent scope and expected file changes
- SubagentStop: runs lint/syntax/security on all files the subagent modified
- TaskCompleted: verifies task output meets quality standards (test files, lint, syntax)

## Specification Verification ("Smart Contract")

The spec-verifier runs on Stop and produces a verification verdict:
- VERIFIED: all FRs have tests, all checks green, coverage met
- GAPS: lists uncovered FRs, orphan tests, failing checks
This is the "if green, it works" guarantee — programmatic proof that specs are implemented.

## Complexity Ratchet

Complexity must never increase. The ratchet enforcer:
- Measures cyclomatic complexity, cognitive complexity, maintainability index
- Compares against baseline — any increase is flagged
- Baseline auto-updates downward (tighter over time)
- Max function: 40 lines. Max cyclomatic: 10. Max cognitive: 15.

## Security Pipeline

4-layer security scanning on every Stop:
1. Secret detection (gitleaks + regex patterns)
2. SAST (Semgrep, bandit, gosec, brakeman, psalm)
3. Dependency audit (pip-audit, npm audit, govulncheck, cargo audit)
4. Infrastructure (tfsec, hadolint, trivy)

## Test Maturity Model

Projects are assessed on a 5-level scale:
- Level 1 — MVP: tests exist and are runnable
- Level 2 — Production-Ready: coverage >= 60%, integration tests, no bare suppressions
- Level 3 — Scale: coverage >= 80%, FR traceability >= 50%, security scanning, strict linters
- Level 4 — High-Reliability: FR traceability >= 80%, architecture enforcement, complexity ratchet
- Level 5 — Mission-Critical: 100% FR traceability, mutation testing, chaos tests, runtime verification

**Target**: Level 3 for all projects, Level 4+ for critical systems.

**Agent-Only Projects** (thegent and similar): **Level 5 REQUIRED**
- **100% E2E coverage** (all CLI commands)
- **100% Integration coverage** (all workflows)
- **100% Unit coverage** (all functions)
- **100% FR traceability** (all requirements have tests)
- **Mutation testing** (80%+ mutation score)
- **BDD scenarios** (Gherkin-style for all user journeys)
- **SDD alignment** (tests validate SDD requirements)

See `docs/governance/AGENT_ONLY_TEST_STRATEGY.md` for complete requirements.

## Runtime Verification

For projects that opt in (via qa-config.json `runtime_verification`):
- Python: beartype (O(1) type checking at runtime), deal (Design by Contract)
- Go: goleak (goroutine leak detection), race detector
- Resilience: toxiproxy (network fault injection), chaos-toolkit (experiments)
Templates available in `~/.claude/templates/quality/runtime/`.

## QA Governance v3.1 — Deep Enforcement Enhancements

### Cognitive Complexity Enforcement
The complexity-ratchet hook now measures both cyclomatic AND cognitive complexity:
- Cognitive complexity weights branching by nesting depth (branch at nesting level N = score 1+N)
- Max cognitive complexity per function: 15 (configurable in qa-config.json)
- Code duplication detection via jscpd (max 5% duplication)
- Dead code detection via vulture (Python) and knip (JS/TS)

### AI Slop Detection
The post-edit-checker now scans every Write/Edit for AI-generated antipatterns:
- Placeholder TODOs ("TODO: implement", "TODO: add")
- Lorem ipsum filler text
- Placeholder domains (example.com in non-test files)
- LLM leakage ("As an AI", "I cannot", "I apologize")
- Lazy AI comments ("This function does...", "This is a helper...")
- Placeholder bodies (pass # TODO, throw new Error("not implemented"))
Advisory only — prints warnings, does not block.

### Dead Import & Dead Code Detection
Quality-gate.sh (Stop) and post-edit-checker.sh (PostToolUse) now detect:
- Dead imports: ruff F401 (Python), oxlint no-unused-vars (JS/TS)
- Dead code: vulture --min-confidence 80 (Python), knip --no-progress (JS/TS)
- Code duplication: jscpd with 5% threshold

### Supply Chain Security (Layer 5)
Security pipeline expanded from 4 to 5 layers:
1. Secrets (gitleaks + regex patterns)
2. SAST (semgrep, bandit, gosec)
3. Dependencies (pip-audit, npm audit, govulncheck, cargo-audit, osv-scanner)
4. Infrastructure (hadolint, tfsec, trivy)
5. **Supply Chain** (syft SBOM generation, OSV-Scanner, opengrep)

### Enhanced Test Maturity Model
Test maturity expanded from 16 to 20 criteria across 5 levels:
- **L4 new**: Snapshot/golden tests (3pts), Approval tests (2pts)
- **L5 new**: Chaos/resilience tests (3pts), Fuzz testing (3pts)
- Enhanced property-based test detection: hypothesis, fast-check, gopter, proptest
- Points rebalanced: 20pts per level, 100pts total

### Hook Stderr Convention
All hooks that exit non-zero now write descriptive failure messages to stderr.
Format: `HOOK_NAME FAIL: reason` (e.g., "SUPPRESSION BLOCKER FAIL: 2 new lint suppression(s)")
This ensures Claude Code displays the actual failure reason instead of "No stderr output".

---

## Development Philosophy

### Proactive Agent Mandate
- **NEVER** ask the user to run a command, search for code, or perform an edit that you have the tools to perform yourself.
- If a task is clear, execute it. If a dependency is missing and you can install/fix it, do so.
- Only ask for clarification if the requirements are truly ambiguous or require a strategic decision that only the user can make.
- "Proactive execution" is the default state. Assume you have permission to use all available tools to achieve the goal.

### Extend, Never Duplicate
- NEVER create a v2 file. Refactor the original.
- NEVER create a new class if an existing one can be made generic.
- NEVER create custom implementations when an OSS library exists.
- Before writing ANY new code: search the codebase for existing patterns.

### Primitives First
- Build generic building blocks before application logic.
- A provider interface + registry is better than N isolated classes.
- Template strings > hardcoded messages. Config-driven > code-driven.

### Research Before Implementing
- Check project deps (pyproject.toml) for existing libraries.
- Search PyPI before writing custom code.
- For non-trivial algorithms: check GitHub for 80%+ implementations to fork/adapt.

### Library Preferences (DO NOT REINVENT)
| Need | Use | NOT |
|------|-----|-----|
| Retry/resilience | tenacity | Custom retry loops |
| HTTP client | httpx | Custom wrappers |
| Logging | structlog | print() or logging.getLogger |
| Config | pydantic-settings | Manual env parsing |
| CLI | typer | argparse |
| Validation | pydantic | Manual if/else |
| Rate limiting | tenacity + asyncio.Semaphore | Custom rate limiter class |

### Code Quality Non-Negotiables
- Zero new lint suppressions without inline justification
- All new code must pass: ruff check, type checker, tests
- Max function: 40 lines. Max cognitive complexity: 15.
- No placeholder TODOs in committed code

### thegent-Specific Rules
- Use tach.toml for boundary enforcement (already configured)
- All new agents must use the agent runner strategy pattern
- **Rust tooling**: Prefer `rg` over `grep`, `fd` over `find`, `jaq` over `jq` for faster hook/agent execution. Hooks use grep-wrapper (routes to rg), fd-wrapper, and JQ_CMD (jaq first). For Claude Code: `export USE_BUILTIN_RIPGREP=0` to use system ripgrep (5-10x faster than bundled).
- All new hooks must follow existing hook patterns in hooks/
- Provider pattern: use ProviderRegistry for extensible services
- MCP tools go through the standard FastMCP registration

---

## Domain-Specific Patterns

### What thegent Is

thegent is an **MCP server + agent hook system** for governing AI agent lifecycle and quality. The core domain is: define agents (personas with capabilities), dispatch hooks at lifecycle events (session start, tool use, stop), enforce governance policies (cost, quality, security), and expose MCP tools for agent management. It is fundamentally an **agent orchestration and governance platform**.

### Local Development (Present)

**Dev stack**: MCP server + CLIProxyAPIPlus proxy via process-compose. Taskfile drives setup and dev.

| Task | Purpose |
|------|---------|
| `task setup` | Install deps, build cliproxy fork (if present), ensure config, install shims |
| `task dev` | Build cliproxy, ensure config, start MCP + proxy (TUI) |
| `task dev:bg` | Same as dev, background |
| `task dev:down` | Stop all services |
| `task dev:logs` | Follow service logs |
| `task cliproxy:build` | Build `../CLIProxyAPIPlus-fork/cli-proxy-api-plus` |
| `task cliproxy:ensure-config` | Ensure cliproxy config (port, auth-dir) |
| `task cliproxy:start`, `stop`, `restart` | Proxy lifecycle |
| `task mgmt:ensure-proxy` | Ensure MCP+proxy running (agent self-service) |
| `task mgmt:verify-codex-cliproxy` | Verify Codex+CLIProxy (agent self-service) |

**Proxy binary**: `scripts/start_proxy_dev.sh` uses the fork binary when built (`task cliproxy:build`), else falls back to `cli-proxy-api-plus` from PATH. process-compose runs this wrapper for the proxy process.

**Ports**: MCP 3847, proxy 8317. Fork at `../CLIProxyAPIPlus-fork`; metrics at `GET /v1/metrics/providers`.

**Debug**: `thegent run --debug` / `thegent bg --debug` sets `THGENT_DEBUG=1`; proxy gets `-debug` when env set. See `docs/plans/DEBUG_TAGS_AND_METRICS.md`.

### Key Ports and Interfaces

| Port | Responsibility | Location |
|------|---------------|----------|
| **AgentRunner** | Strategy pattern for executing agent personas | `agents/` |
| **HookDispatcher** | Dispatches lifecycle hooks (pre/post tool use, stop, etc.) | `hooks/hook-dispatcher/`, `hooks/*-dispatcher.sh` |
| **PolicyEngine** | Evaluates governance rules (cost caps, quality gates, security) | `hooks/qa-policy-engine.sh`, `contracts/` |
| **MCPToolRegistry** | Registers and serves MCP tools to connected clients | MCP server entry point |
| **CommandRegistry** | CLI commands for agent management, DAG compilation, spec ops | `commands/` |
| **ContractStore** | Stores and validates governance contracts and policies | `contracts/` |

### Provider Registry and Agent Strategy

- **Agent personas** live in `agents/` as markdown definitions. New agents = new `.md` file describing the persona, capabilities, and constraints.
- **Hooks** follow a strict naming and dispatch pattern. The dispatcher routes events to matching hook scripts. New hooks = new `.sh` file in `hooks/` following the naming convention (`qa-*.sh` for quality gates, `pre-*.sh` for pre-tool hooks, etc.).
- **Commands** in `commands/` define CLI-accessible operations (DAG compilation, ledger init, spec hashing). New commands = new entry in `commands/` + registration.
- **Contracts** define governance policies (cost limits, SLOs, migration rules). New governance rule = new contract JSON in `contracts/`.

### Common Anti-Patterns to Avoid

- **Direct MCP message handling in domain logic** -- MCP protocol concerns stay in the MCP server layer. Domain logic (agents, hooks, policies) must not import or depend on MCP transport
- **Custom agent discovery** -- Use the agent registry pattern. Never glob for agent files at runtime outside the registry
- **Hooks that bypass the dispatcher** -- All hooks fire through `hook-dispatcher/`. Never call hook scripts directly from application code
- **Inline governance rules** -- Cost caps, quality thresholds, and policy rules belong in `contracts/` or `hooks/hook-config.yaml`, not hardcoded in hook scripts
- **Monolithic hook scripts** -- Shared logic goes in `hooks/lib/`. Hook scripts should be thin dispatchers that call library functions

### Sitback Agent

`thegent sitback` launches Claude Code with a Sitback Agent persona: dashboard (cockpit + terminals + ps), FastMCP tools first, CLI fallback. Skills: `skills/sitback-agent/` (default), overridable via `--skill`. MCP precondition: `thegent serve` for full toolset.

### Workflow Triggers (Skill / MCP / Instruction)

Idea/task prompts, quality green, and "next thing to do" are wired at multiple levels:

| Level | Location | Purpose |
|-------|----------|---------|
| **Hook** | `hooks/prompt-submit-guard.sh` | UserPromptSubmit: pattern-detect, inject instructions to agent context |
| **Skill** | `skills/agent-orchestra/SKILL.md`, `skills/sitback-agent/SKILL.md` | Baked-in workflow section; agents with these skills follow it |
| **MCP resource** | `thegent://workflow/triggers` | URI-addressable; agent can read when needed |
| **MCP resource** | `thegent://workstream` | Work stream (canonical backlog) |
| **MCP prompts** | `thegent_workflow_idea`, `thegent_workflow_quality_green`, `thegent_workflow_next_item`, `thegent_workflow_gardening` | Template prompts for structured invocation |
| **MCP resource** | `thegent://workflow/gardening` | Gardening workflow (converge to empty backlog + green) |
| **MCP tool** | `thegent_do_next` | Find next actionable items from WORK_STREAM (canonical), PLAN_STATUS, FR_TRACKER, docs/plans/, escalation; returns prompt_suggestion for thegent_run/thegent_bg |
|| **MCP tool** | `thegent_memory_add` | Record observations, lessons, issues, and friction points into the audit log (MTSP-17) |
|| **MCP tool** | `thegent_memory_scrape_session` | Automatically collect user prompts and intents from terminal/history (MTSP-18) |
| **CLI** | `thegent plan do-next` | Same as thegent_do_next |

**Unified work stream**: Single source of truth is `docs/reference/WORK_STREAM.md`. All agents read it for work items; claim in CLAIMED before starting; update COMPLETED when done. Incorporator agent (`work-stream-incorporator`) merges fragments from plans, research, specs into the stream. See [UNIFIED_WORK_STREAM_DESIGN.md](docs/reference/UNIFIED_WORK_STREAM_DESIGN.md).

**Idea/task** → dump research to docs/research/, specs to docs/docset/, work items to unified stream. **Quality green** → `task quality-a-r`. **Next item** → `thegent_do_next` (or read WORK_STREAM.md), pick highest-priority, execute via `thegent_run`/`thegent_bg` with `prompt_suggestion`. **Gardening** → check gov traceability, tests, plan items; dispatch; converge to empty backlog and complete green (`thegent govern go health`, `go cycle`, `task quality-a-r`).

### Agent Memory & Issue Collection (MTSP-17/18)

All agents MUST contribute to the project's **Working Memory** to ensure knowledge persistence across multi-agent sessions.

1. **Record as you go**: Use `thegent_memory_add` to log discoveries, positive lessons, negative lessons, and friction points.
2. **Scrape session**: Periodically call `thegent_memory_scrape_session` to ingest user prompts and intents into the audit log automatically.
3. **Synthesis**: Before finishing a major task, use `thegent_memory_synthesize` to generate a summary of recent fragments.
4. **Friction Scopes**:
   - `agent`: General model behavior issues.
   - `ephemeral`: Transient environment issues (network, disk, etc.).
   - `project`: Codebase-specific issues.
   - `process`: Workflow/governance friction.

### Lifecycle Loops

| Command / Tool | Purpose |
|----------------|---------|
| `thegent orchestrate loop "prompt" "todo"` | Run Lifecycle loop (worker + checker) |
| `thegent orchestrate loop-send <session_id> <prompt>` | Send next prompt to running loop (human/agent takeover) |
| `thegent orchestrate loop-stop <session_id>` | Stop loop |
| `thegent takeover <session>` | Attach to tmux session; human types next prompt |
| `thegent_loop_takeover` (MCP) | Agent injects prompt into running loop |
| `--continuation <session_id>` | Resume from prior session (adds resumption appendix) |
| `--resume` (Codex/Claude) | Use when agent supports native resume |

**Premature session end:** If Codex/Claude supports `--resume`, use it. Otherwise: `thegent run/bg --continuation <prior_session_id> "Task"` — builds context from prior stdout + resumption appendix.

### WBS Agent Coordination (Multi-Agent "Do All")

When the user says **"do all"** or assigns work to multiple agents:

1. **Read** `docs/reference/WORK_STREAM.md` (canonical) — or `docs/plans/02-UNIFIED-WBS.md` + `docs/reference/WBS_AGENT_PROGRESS.md` for WBS-only coordination
2. **Claim before starting**: Append your work items to the **CLAIMED** table in `WORK_STREAM.md` (or `WBS_AGENT_PROGRESS.md` if using WBS-only) with a unique agent_id (e.g. `agent-1`, `runner-A`)
3. **Avoid overlap**: Do NOT pick items already in CLAIMED. Pick an equal batch of unclaimed items.
4. **Update progress**: When done, move items from CLAIMED to COMPLETED and update source file (e.g. `02-UNIFIED-WBS.md`) status to DONE

**Preferred**: Use `WORK_STREAM.md` — single file for all work types. `WBS_AGENT_PROGRESS.md` remains for backward compatibility with WBS-only "do all" flows.

### Where to Add New Functionality

| Want to add... | Put it in... |
|----------------|-------------|
| New agent persona | `agents/<persona-name>.md` -- follows existing agent template |
| New lifecycle hook | `hooks/<event>-<name>.sh` + register in `hooks/hook-config.yaml` |
| New governance policy | `contracts/<policy>.json` + wire into `qa-policy-engine.sh` |
| New MCP tool | MCP server registration (FastMCP pattern) |
| New CLI command | `commands/<command>/` + register in command dispatch |
| New quality gate | `hooks/qa-<gate-name>.sh` following existing `qa-*.sh` patterns |
| Shared hook utility | `hooks/lib/<utility>.sh` -- sourced by hook scripts, never called directly |
