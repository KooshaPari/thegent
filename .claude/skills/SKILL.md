# Thegent Skills

Unified orchestration guidance for external agents using `thegent` as the default execution path.

## Primary Rule

Use `thegent` subcommands, not legacy positional form.

- **Recommended default**: `thegent free` for most tasks (free tier, work stream integration)
- **Required**: `thegent run [options] "<prompt>" [agent]` (prompt-first; agent optional with `-M`/`--model-first`)
- **Required for long jobs**: `thegent bg ...`, then `thegent status`, `logs`, `wait`, `stop`
- **Recommended for continuous work**: `thegent plan loop` (instead of bash loops)
- **Recommended for idle waiting**: `thegent plan wait-next` (instead of busy loops)
- **Do not use**: wrapper scripts, bash loops, or `thegent <agent> <prompt>`.

**See**: [THGENT_CLI_REFERENCE.md](../../docs/guides/THGENT_CLI_REFERENCE.md) for complete command reference.

## Installation / Upgrade

Canonical standalone project path (replace with your checkout path if moved):

`/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent`

Install or refresh globally:

```bash
uv tool install --editable /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent
```

Verify:

```bash
thegent --help
thegent run --help
thegent list-agents
```

For minimax/glm: run `thegent cliproxy login minimax` or `thegent cliproxy login glm` (OAuth). Install `codexmax` and `codexglm` to `~/.local/bin` if using those CLIs.

Tip: install with an environment-independent root variable:

```bash
export THEGENT_ROOT=/path/to/kush/thegent
uv tool install --editable "$THEGENT_ROOT"
```

## Standard Invocation

### Recommended: Use `thegent free` for Default Tasks

```bash
# Default free tier agent (recommended)
thegent free "Task description"

# Work stream integration
thegent free --do-next

# Run next 5 work items sequentially
thegent free --do-next --repeat 5

# Background execution
thegent free "Long task" --bg
```

### Deep Research (DRP)

Use the Deep Research Protocol to bypass bot blocks on Reddit, DDG, and Arxiv.

```bash
# Basic deep research
thegent research deep "AI safety research"

# With specific subreddits
thegent research deep "AI safety research" --subreddits "MachineLearning,ArtificialIntelligence"

# Save to file
thegent research deep "AI safety research" --output results.json
```

### Foreground Execution with Full Control

```bash
# Foreground
thegent run -d /path/to/repo -m write -t 120 "Analyze and summarize risks" cursor-agent
thegent run -d /path/to/repo -m read-only -t 90 "List critical modules" gemini

# Model-first routing
thegent run -d /path/to/repo -m write -M gemini-3-pro-preview "Deep analysis"

# Model-first with provider override
thegent run -d /path/to/repo -m read-only -P antigravity -M claude-sonnet-4 "Architecture review"

# With routing policy
thegent run -d /path/to/repo -m write -M gemini-3-flash -R cheapest "Cost-sensitive task"
```

### Continuous Autonomous Work (Recommended Pattern)

```bash
# Continuous work loop (recommended for autonomous agents)
thegent plan loop

# With custom agent and sleep interval
thegent plan loop --agent codex --sleep 10

# With max iterations
thegent plan loop --max 10
```

### Idle Waiting (Instead of Busy Loops)

```bash
# Wait for work to become available
thegent plan wait-next

# Wait with timeout
thegent plan wait-next --timeout 300

# Wait for specific sources
thegent plan wait-next --sources dag,do_next
```

## Option Ordering (Typer-safe)

Use options first to avoid positional ambiguity:

```bash
thegent run -d "/path/to/repo" -m read-only -t 60 gemini "List top modules"
thegent bg -d "/path/to/repo" -m write -t 600 --full "Draft design notes" minimax
```

## Session Register / Inbox

For deterministic orchestration, treat `owner` as a session inbox key:

```bash
export THGENT_OWNER_TAG="agent-orch:${USER}:$(basename "$PWD"):$(date +%s)"

thegent bg --format json --owner "$THGENT_OWNER_TAG" -d /path/to/repo -m write "Implement feature X" cursor-agent
thegent ps --owner "$THGENT_OWNER_TAG" --format json
thegent inspect --owner "$THGENT_OWNER_TAG" --format json

# Parse newest session id
SESSION_ID="$(thegent ps --owner "$THGENT_OWNER_TAG" --format json | python -c 'import json,sys; j=json.load(sys.stdin); print(j[-1]["id"])')"
thegent logs "$SESSION_ID" --follow
thegent status "$SESSION_ID" --format json
```

## Long-Running / Observable Invocation

```bash
# Use one explicit owner for the full session family (stable across status checks)
export THGENT_OWNER_TAG="agent-orch:${USER}:$(basename "$PWD"):$(date +%s)"

SESSION_JSON="$(thegent bg --format json -d /path/to/repo --owner "$THGENT_OWNER_TAG" -m write -t 600 --full "Implement feature X" cursor-agent)"
SESSION_ID="$(printf '%s' "$SESSION_JSON" | python -c 'import json, sys; print(json.load(sys.stdin)["session_id"])')"

# Monitor by explicit owner scope
thegent ps --owner "$THGENT_OWNER_TAG"
thegent status "$SESSION_ID"
thegent inspect --owner "$THGENT_OWNER_TAG" --format json
thegent logs --follow "$SESSION_ID"
thegent logs --follow --timeout 30 "$SESSION_ID"

# Completion / control
thegent wait -t 1800 "$SESSION_ID"   # exit code is authoritative
thegent stop "$SESSION_ID"
thegent stop --force "$SESSION_ID"
```

## Work Stream Integration

### Continuous Autonomous Work (Recommended)

```bash
# Continuous work loop (recommended for autonomous agents)
thegent plan loop

# With custom agent
thegent plan loop --agent codex

# With max iterations
thegent plan loop --max 10
```

### Single Work Item Execution

```bash
# Run next work item
thegent free --do-next

# Run next 5 items sequentially
thegent free --do-next --repeat 5
```

### Idle Waiting (Instead of Busy Loops)

```bash
# Wait for work to become available
thegent plan wait-next

# Wait with timeout
thegent plan wait-next --timeout 300
```

## Model Routing

### Model-First Routing

```bash
# Model-first routing (auto-resolves provider)
thegent run "Task" -M gemini-3-flash

# Model-first with provider override
thegent run "Task" -M claude-sonnet-4.5 -P claude

# Model-first with routing policy
thegent run "Task" -M gemini-3-flash -R cheapest

# Model-first with failover
thegent run "Task" -M gemini-3-flash --failover
```

### Routing Policies

- `prefer_direct`: Prefer direct provider connections (default)
- `prefer_proxy`: Prefer proxy connections
- `failover`: Try primary, fallback on failure
- `round_robin`: Distribute across routes
- `cheapest`: Select cheapest route
- `cost_quality`: Balance cost and quality
- `pareto`: Pareto frontier optimization
- `roi`: Return on investment optimization

## Sitback (Recommended for Multi-Session Orchestration)

For monitoring many terminals and Claude Code instances, use **Sitback**:

```bash
# Start Sitback Agent (dashboard + terminal list + ps on startup)
thegent sitback
thegent sitback -a kilo              # sibling session via kilo
thegent sitback --skill thegent-skills  # use this skill instead of sitback-agent
thegent sitback --no-dashboard       # manual mode
```

**Precondition:** Start MCP first for FastMCP tools: `thegent serve` (or `thegent mcp up`). If MCP is down, Sitback falls back to CLI.

## Agent Selection Guidance

- Prefer native tool-specific subagents only when a tool-only capability is required.
- Prefer `thegent` for cross-provider consistency, model override, and session observability.
- **Agents:** gemini, codex, copilot, cursor-agent, claude, minimax, glm

## Directory Listing (ls Avoidance)

When listing directory contents: prefer `fd -t f -d 1` or `fd -t d -d 1` (add `-E node_modules -E .venv -E dist` for heavy dirs). If using ls: run in subdirs (`ls -l src/`, `ls -l docs/`) not project root; or `ls -1` when only names needed. Avoid `ls -l` in project root when node_modules/.venv exist (causes 5m+ delays).

## Provider Constraints (minimax, glm)

When using **minimax** or **glm**: dispatch subagents sparingly. Handle 2–3 tasks directly before delegating. Do not announce "Let me dispatch..." repeatedly. Prefer sequential batches over parallel spam. Call in parallel only when tasks are truly independent and >3; otherwise batch sequentially.

## Models

```bash
thegent list-models
thegent list-models cursor-agent
thegent list-models minimax
thegent list-models glm
```

## Reliability Notes

- Use `--owner` for predictable session scoping across concurrent agents.
- Use `--full` in `bg` for raw logs when debugging.
- Reuse `THGENT_OWNER_TAG` across `bg`, `ps`, `inspect`, and `status` calls.
- Treat `thegent wait` exit code as the authoritative automation result.

---

## Test Coverage Requirements (Agent-Only Environment)

**CRITICAL**: Since NO humans will test this system - only agents will use it - comprehensive automated test coverage is REQUIRED.

### Coverage Targets
- **E2E Tests**: **100%** of all CLI commands (297 commands total)
- **Integration Tests**: **100%** of all workflows
- **Unit Tests**: **100%** of all functions

### Test Strategy
- **BDD-Style**: Use Gherkin scenarios for agent journeys
- **TDD Mandate**: Write tests BEFORE implementation
- **SDD Alignment**: Tests validate SDD requirements

### Coverage Analysis
Run coverage analysis:
```bash
python scripts/analyze_test_coverage.py
```

### Documentation
- `docs/governance/AGENT_ONLY_TEST_STRATEGY.md` - Complete test strategy
- `docs/governance/TDD_BDD_SDD_GOVERNANCE.md` - TDD/BDD/SDD alignment
- `docs/governance/TEST_COVERAGE_CRITICAL_GAP.md` - Current coverage gaps

### Current Status
- **E2E Coverage**: 21.21% (63/297 commands)
- **Gap**: 234 commands need E2E tests
- **Target**: 100% coverage required

**Why 100%?** In agent-only environments, automated tests are the ONLY way to verify behavior. Every user journey must be covered.

---

## Workflow Triggers (Idea → Research → Spec → Work Stream)

When the user gives **idea/task prompts** (research, explore, build, implement, design, create, feature, investigate):

1. **Dump research** to `docs/research/` (or `docs/guides/` as appropriate)
2. **Create or update specs** in `docs/docset/` (formal specification docset)
3. **Add work items** to unified work stream: `docs/reference/`, `contracts/`, `docs/plans/`, or project tracker
4. This enables: spam ideas here → open new chat → ask "find the next thing to do"

When the user says **"get task quality green"** or similar (quality green, make quality pass, fix quality):

- Run: `task quality-a-r` (full quality pipeline; on fail pipes to agent and reloads until green)
- Or: `task quality:dag` (DAG only, no agent loop)

When the user says **"find the next thing to do"** or similar (what next, pick next, next task):

1. Call `thegent_do_next` (MCP) or `thegent plan do-next` (CLI) — returns next_items with id, description, prompt_suggestion
2. Pick the first (or highest-priority) item from next_items
3. Execute via `thegent_run`/`thegent_bg` with the item's `prompt_suggestion`
4. Fallback: if no tool, read `thegent://workstream` (canonical), PLAN_STATUS.md, FR_TRACKER.md, docs/plans/, pending-handoff.md and pick manually

---

## Prompt Markers ($defer, $pending, $block)

When composing prompts in Claude Code (or harvesting from Cursor/Codex transcripts):

| Marker | Behavior |
|--------|----------|
| **$defer** | Prompt is queued for session stop; not sent to model. Appended to `.claude/pending-queue.jsonl`; on Stop, flushed to `docs/research/pending-handoff.md`. Use for "do this later" items. |
| **$pending** | Same as $defer. |
| **$block** | Prompt blocks until resolved. Calls `thegent govern escalate add` with reason; user must resolve via `thegent govern escalate resolve`. Use for human-gate items (approvals, decisions). |

`thegent_do_next` / `thegent plan do-next` reads `pending-handoff.md` and surfaces deferred items as next_items.

---

## Gardening (Converge to Empty Backlog + Complete Green)

When the user says **"garden"**, **"converge"**, **"empty backlog"**, **"complete green"**:

1. **Governance health** — `thegent govern go health` (8 dimensions: test_coverage, lint, docs, research, specs, debt, stale, agent_failure)
2. **Gov traceability** — `task quality`; FR traceability in tests; `hooks/spec-verifier.sh`
3. **Plan items** — Read `thegent://workstream` (canonical), `docs/reference/PLAN_STATUS.md`, `docs/plans/`, `docs/reference/FR_TRACKER.md`
4. **Escalation backlog** — `thegent govern escalate list --past-sla`
5. **Dispatch** — For each failing dimension: `thegent run` or `thegent bg` with remediation prompt
6. **Quality** — `task quality-a-r` until green
7. **Governance cycle** — `thegent govern go cycle` (AgilePlus)
8. **Repeat** until backlog empty and all green

---

## Lifecycle Loops

**Loop** = worker + checker until kill/stop. **Human:** `thegent takeover <session>` (tmux) or `thegent orchestrate loop-send <session_id> <prompt>`. **Agent:** `thegent_loop_takeover(session_id, prompt)`. When worker waits at CLI, sending to pane = next prompt. **Premature end:** Use `--resume` if agent supports it; else `--continuation <prior_session>` (adds resumption appendix).
