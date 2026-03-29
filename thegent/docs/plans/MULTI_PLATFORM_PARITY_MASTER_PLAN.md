# Multi-Platform Parity Master Plan & Matrix

**Purpose:** Complete plan and matrix for achieving and superceding parity across **Claude Code**, **Codex**, **Cursor-agent**, **Factory droid**, **Augment Code**, and **OpenCode**. Single source of truth for capability coverage, strategy, and execution.

**Status:** Living document — update as phases complete.

**References:**
- [CODEX_DONUT_HARNESS_PLAN.md](./CODEX_DONUT_HARNESS_PLAN.md) — Phase breakdown
- [CLAUDE_CODE_FEATURE_PARITY_AUDIT.md](../research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md) — Feature audit
- [MULTI_PLATFORM_DEEP_DIVE.md](../research/MULTI_PLATFORM_DEEP_DIVE.md) — Schemas, configs, MCP
- [08-OPTIMIZATION-CATALOG.md](./08-OPTIMIZATION-CATALOG.md) — OPT, ROB, UX items
- [MCP_TOOL_OPTIMIZATION_PLAN.md](./MCP_TOOL_OPTIMIZATION_PLAN.md) — MCP tool optimization, polish, end-to-end design
- [MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md](../research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md) — CLI↔MCP↔Codex/CC matrix; FastMCP transport spec usage

---

## 0. Design Philosophy: Maximal Yet Lean

| Principle | Meaning | Anti-Pattern |
|-----------|---------|--------------|
| **Intuitive** | Same mental model across platforms; `run -M X` works everywhere | Platform-specific quirks |
| **Robust** | Fail clearly; degrade gracefully; no silent corruption | Silent fallbacks, opaque errors |
| **Holistic** | End-to-end flows work (queue → harvest → handoff → next session) | Orphan features |
| **Complete** | Every entry point has an exit; every state has a transition | Half-implemented flows |
| **Maximal** | Full capability coverage; nothing left on the table | Feature gaps |
| **Lean** | No abstraction for abstraction's sake; YAGNI at the design level | Over-engineered layers |

**Balance:** Add capability when it closes a real gap; avoid speculative "might need" layers. Prefer composition (queue + harvest + rules as separate modules) over a monolithic "orchestration engine."

---

## 1. Executive Summary

| Goal | Approach |
|------|----------|
| **Achieve parity** | Match each platform's native capabilities via thegent harness (queue, harvest, rules, teams, MCP) |
| **Supercede parity** | Unify across platforms: single queue, single rules sync, single MCP toolset, cross-platform teams |
| **Platforms** | Claude Code (reference), Codex, Cursor, Factory droid, Augment, OpenCode |

**Key insight:** No single platform has all capabilities. Claude Code has 15 hooks + teams; Codex has notify only; Cursor has rules; Factory has droids; Augment has Context Engine + Intent; OpenCode has Zen. **thegent supercedes by providing a unified layer that works across all.**

---

## 2. Master Parity Matrix

### 2.1 Capability × Platform × Status × Strategy

| Capability | Claude Code | Codex | Cursor | Factory Droid | Augment | OpenCode | thegent Strategy | Status |
|------------|:-----------:|:-----:|:------:|:-------------:|:-------:|:--------:|------------------|--------|
| **Interactive TUI** | ✓ Native | ✓ Native | ✓ Composer | ✗ | ✓ auggie | ✓ oc | thegent codex/clode/dex wrap | ✓ |
| **Headless** | ✓ claude -p | ✓ codex exec - | ✓ cursor-agent | ✓ droid exec | ✓ auggie --print | ✓ oc | thegent run -M {agent} | ✓ |
| **Queue ($defer/$pending)** | ✓ UserPromptSubmit | ✗ | ✗ | ✗ | ✗ | ✗ | run_impl preprocessor + prompt-submit-guard | ⏳ |
| **Block ($block)** | ✓ UserPromptSubmit | ✗ | ✗ | ✗ | ✗ | ✗ | escalation + run_impl | ⏳ |
| **Harvest ($idea)** | ✓ UserPromptSubmit | ✗ | ✗ | ✗ | ✗ | ✗ | harvest-idea-seeds (all sources) | ✓ |
| **Session lifecycle hooks** | ✓ 15 events | ✗ (notify only) | ✗ | ✗ | ✗ | ✗ | Wrapper exit + run_impl + codex-notify | ⏳ |
| **Agent teams** | ✓ Native | ✗ | ✗ | ✗ | Intent | ✗ | thegent team (N codex exec + MCP) | ⏳ |
| **Subagents** | ✓ Task tool | ✗ | ✗ | ✗ | ✗ | ✗ | thegent_run/thegent_bg as subagent | ✓ |
| **Rules/Skills** | ✓ CLAUDE.md, skills | ✓ .codex/skills | ✓ .cursor/rules | ✓ .factory/droids | ✗ | ✓ .codex/skills | thegent rules sync → all | ⏳ |
| **MCP** | ✓ Full | ✓ Full | ✓ Full | ✓ .factory/mcp | ✓ Context Engine | ✓ Full | thegent serve (30+ tools) | ✓ |
| **Unified queue** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | .thegent/prompt_queue.jsonl | ⏳ |
| **Unified rules** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | thegent rules sync | ⏳ |
| **Harvest (multi-source)** | Claude only | Codex only | Cursor only | ✗ | ✗ | ✗ | harvest from Claude+Codex+Cursor | ✓ |
| **Context Engine** | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | Add Augment MCP to install | ⏳ |
| **Living specs** | ✗ | ✗ | ✗ | ✗ | ✓ Intent | ✗ | thegent team + DAG as spec | ⏳ |
| **Git worktrees** | ✗ | ✗ | ✗ | ✗ | ✓ Intent | ✗ | thegent team: separate processes | ⏳ |
| **Droid personas** | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | DroidRunner, droid as teammate | ✓ |
| **Lifecycle loop** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | thegent_loop + checker | ✓ |
| **Model routing** | ✗ | ✗ | ✗ | ✗ | ✗ | Zen | 12+ providers, failover, Pareto | ✓ |

**Legend:** ✓ Implemented | ⏳ Planned | ✗ Not available natively

### 2.2 Extended Capability Matrix (Breadth)

| Capability | Claude | Codex | Cursor | Droid | Augment | OpenCode | thegent |
|------------|:------:|:-----:|:------:|:-----:|:-------:|:--------:|---------|
| **PreToolUse** | ✓ | ✗ | ✗ | Factory hooks | ✗ | ✗ | N/A (no tool loop in exec) |
| **PostToolUse** | ✓ | notify (AfterAgent) | ✗ | Factory hooks | ✗ | ✗ | codex-notify |
| **PermissionRequest** | ✓ | Sandbox | ✗ | — | ✗ | ✗ | Different models |
| **Memory** | user/project/local | session | — | — | — | — | run registry |
| **Checkpointing** | Rewind | ✗ | ✗ | ✗ | Intent resumable | ✗ | run registry, handoff |
| **Resume session** | --resume | ✗ | ✗ | ✗ | Intent | ✗ | handoff file |
| **Structured output** | --json-schema | --json | ✗ | stream-json | ✗ | ✗ | Passthrough |
| **Sandbox** | Bash tool | exec sandbox | — | — | — | — | Per-agent |
| **Proxy agents** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | antigravity, kilo, nim, cliproxy |
| **Background agent** | ✗ | ✗ | Cursor bg | ✗ | ✗ | ✗ | thegent_bg |
| **Plan mode** | ✗ | ✗ | /plan | ✗ | ✗ | ✗ | thegent run mode? |
| **Code Review** | ✗ | ✗ | ✗ | ✗ | Augment | ✗ | — |
| **IDE extension** | ✗ | ✗ | Composer | ✗ | VS Code, JB | oc | N/A |
| **Desktop app** | ✗ | ✗ | ✗ | ✗ | Intent | Beta | — |
| **Slack delegate** | ✗ | ✗ | ✗ | ✗ | Augment | ✗ | — |
| **Remote agents** | ✗ | ✗ | ✗ | ✗ | Augment | ✗ | thegent serve HTTP |

### 2.3 Hook-by-Hook Strategy (15 Claude Hooks → All Platforms)

| Claude Hook | Blocking | Claude | Codex | Cursor | Droid | Augment | OpenCode | thegent Strategy |
|-------------|:--------:|:------:|:-----:|:------:|:-----:|:-------:|:--------:|------------------|
| SessionStart | No | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | Wrapper: inject handoff before spawn; exec: prepend stdin |
| UserPromptSubmit | Yes | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | run_impl preprocessor; prompt-submit-guard |
| PreToolUse | Yes | ✓ | ✗ | ✗ | Factory | ✗ | ✗ | SDK only; exec N/A |
| PermissionRequest | Yes | ✓ | Sandbox | ✗ | ✗ | ✗ | ✗ | Different model |
| PostToolUse | No | ✓ | notify | ✗ | Factory | ✗ | ✗ | codex-notify |
| PostToolUseFailure | No | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | — |
| Notification | No | ✓ | ✗ | ✗ | Factory | ✗ | ✗ | — |
| SubagentStart | No | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | thegent_run = subagent |
| SubagentStop | Yes | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | On thegent run exit |
| Stop | Yes | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | Wrapper exit; harvest |
| TeammateIdle | Yes | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | Wrapper poll teammate |
| TaskCompleted | Yes | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | MCP task lifecycle |
| PreCompact | No | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | — |
| SessionEnd | No | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | Wrapper exit |

### 2.4 Hooks Pipeline (Claude Code Reference)

| Order | Event | When | Blocking | Script/Hook |
|-------|-------|------|----------|-------------|
| 1 | SessionStart | New session, resume, clear, compact | No | — (optional handoff) |
| 2 | UserPromptSubmit | Before prompt sent | Yes | prompt-submit-guard.sh |
| 3 | PreToolUse | Before tool call | Yes | — |
| 4 | PermissionRequest | Permission dialog | Yes | — |
| 5 | PostToolUse | After tool call | No | — |
| 6 | PostToolUseFailure | After tool fails | No | — |
| 7 | Notification | Various | No | — |
| 8 | SubagentStart | Subagent spawned | No | — |
| 9 | SubagentStop | Subagent done | Yes | — |
| 10 | Stop | Session ends | Yes | harvest-pending-queue.sh, harvest-idea-seeds-stop.sh |
| 11 | TeammateIdle | Teammate about idle | Yes | — |
| 12 | TaskCompleted | Task marked done | Yes | — |
| 13 | PreCompact | Before compaction | No | — |
| 14 | SessionEnd | Session terminates | No | — |

**Codex equivalent:** Only notify (AfterAgent) fires; no UserPromptSubmit, Stop, etc. thegent compensates via wrapper + run_impl.

### 2.5 Sandbox & Permission Models (Breadth)

| Platform | Sandbox | Permission Model | thegent |
|----------|---------|------------------|---------|
| Claude Code | Bash tool sandbox | default, plan, acceptEdits, dontAsk, bypass | Passthrough |
| Codex | exec sandbox: workspace-write, danger-full-access | Implicit via sandbox | --sandbox passthrough |
| Cursor | — | — | — |
| Droid | — | tools: read-only, write, execute | DroidRunner mode |
| Augment | — | — | — |
| OpenCode | — | — | — |

### 2.6 Supercede Opportunities (thegent > Any Platform)

| Area | Platform Best | thegent Supercede |
|------|---------------|-------------------|
| **Queue** | Claude Code (UserPromptSubmit) | Unified .thegent queue for ALL platforms; MCP tools; TUI |
| **Rules** | Cursor (.cursor/rules) | Single source → sync to Claude, Codex, Cursor, droid |
| **Harvest** | Per-platform | Single harvest from Claude + Codex + Cursor transcripts |
| **Teams** | Claude Code / Augment Intent | thegent team works with Codex, droid, cursor; MCP-driven |
| **Model access** | OpenCode Zen (paid) | 12+ providers, free-first (Antigravity, Kilo, NIM) |
| **Orchestration** | Augment Intent (desktop) | CLI + MCP; works in CI, headless, any agent |
| **MCP toolset** | Per-client | 30+ tools, 20+ resources; same across Claude, Codex, Cursor |

---

## 3. Platform-by-Platform Parity Strategy

### 3.1 Claude Code (Reference)

| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| Hooks | 15 events | prompt-submit-guard, harvest Stop | — |
| Queue | UserPromptSubmit | Migrate to .thegent queue | Unified queue for all |
| Teams | Native | — | thegent team extends to Codex/droid |
| Headless | claude -p | thegent run -M claude | Same entry as Codex/Cursor |
| Rules | CLAUDE.md | rules sync writes | Single source → all platforms |

**Gaps to close:** SessionStart handoff inject; migrate queue path to .thegent.

### 3.2 Codex

| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| Hooks | notify (AfterAgent) | codex-notify; run_impl preprocessor; wrapper exit | Full lifecycle via wrapper |
| Queue | ✗ | run_impl $defer/$block; wrapper harvest | Same as Claude |
| Teams | ✗ | thegent team (N codex exec) | Teams for Codex |
| Interactive | codex TUI | thegent codex wrapper + exit hook | Harvest on exit |
| Rules | .codex/skills | rules sync | Single source |
| MCP | Full | thegent serve | 30+ tools |

**Gaps to close:** codex-notify, run_impl preprocessor, queue tools, team module, rules sync.

### 3.3 Cursor-Agent

| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| Rules | .cursor/rules | rules sync reads | Single source → Cursor |
| Harvest | ✗ | harvest from transcripts | $defer/$idea from Cursor |
| Headless | cursor-agent | thegent run -M cursor-agent | Same CLI as others |
| MCP | Full | thegent serve | Same tools |
| Modes | /plan, agent, bg | thegent run mode | — |

**Gaps to close:** run -M cursor-agent; harvest Cursor transcripts for $defer/$idea; rules sync to .cursor/rules.

### 3.4 Factory Droid

| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| Droids | droid exec | DroidRunner | droid as teammate |
| Tools | Per-droid | Frontmatter parsed | — |
| Queue | ✗ | run_impl preprocessor | Same queue |
| Harvest | ✗ | On droid exit | Same harvest |
| Rules | .factory/droids | Inject into prompt | rules sync |
| Teams | ✗ | Droid as teammate | Codex + droid teams |

**Gaps to close:** $defer/$block in run_impl for droid; harvest on exit; droid as teammate; rules inject.

### 3.5 Augment Code

| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| auggie CLI | auggie, auggie --print | thegent run -M augment | Same entry |
| Context Engine | MCP | Add to mcp install | Cross-platform context |
| Intent | Desktop orchestration | — | thegent team (CLI) |
| Living specs | Intent | — | DAG + team tasks |

**Gaps to close:** run -M augment; Context Engine MCP in install; document in registry.

### 3.6 OpenCode

| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| oc CLI | oc (terminal agent) | thegent run -M opencode | Same entry |
| Zen | Curated models | Not recommended (ZEN_INTEGRATION.md) | Free-first routing |
| MCP | Full | thegent serve | Same tools |
| Desktop | Beta | — | — |

**Gaps to close:** run -M opencode; document in registry. Zen: do not integrate (cost overhead).

---

## 3a. Implementation Deep Dive (Per-Strategy)

### 3a.1 run_impl Preprocessor (Depth)

**Location:** `cli_impl.run_impl` or `codex_proxy` before `subprocess.run([agent_cmd, ...])`

**Flow:**
1. Parse prompt for flags: `\$defer|\$pending|\$block|\$idea` (regex)
2. **$defer/$pending:** Strip flag from prompt; append `{ts, prompt, project, claimed_by, lease_expires_at}` to `.thegent/prompt_queue.jsonl`; return `{"queued": true, "count": N}`; exit 0; **do not spawn**
3. **$block:** Call `thegent govern escalate add`; return block message; exit 1; **do not spawn**
4. **$idea:** (Claude) prompt-submit-guard saves to idea-seeds; (Codex/Droid) append to harvest buffer; **continue** to spawn
5. **No flag:** Proceed to spawn agent

**Agents affected:** codex, droid, augment, opencode (all headless via run_impl)

**Edge cases:** Concurrent append (atomic write); empty project → fallback `~/.thegent/prompt_queue.jsonl`; corrupt file → truncate to last valid line.

### 3a.2 codex-notify (Depth)

**Entry:** `thegent codex-notify` — receives JSON as `argv[-1]`

**Payload:** `{"type":"agent-turn-complete","thread-id":"uuid","turn-id":"...","cwd":"/path","input-messages":["..."],"last-assistant-message":"..."}`

**Actions:**
1. Parse JSON; if invalid → log, exit 0 (don't fail Codex)
2. If `type != "agent-turn-complete"` → ignore
3. Extract `input-messages`; check for $idea → append to harvest buffer
4. Write to run_registry or telemetry (optional)
5. **Limitation:** No session-end signal; harvest on wrapper exit

**Config injection:** `mcp_manage.install_to_codex` merges `notify = ["thegent", "codex-notify"]` into `~/.codex/config.toml`

### 3a.3 Harvest (Depth)

**Sources:** `~/.claude/history.jsonl` (display), `~/.codex/history.jsonl` (text), `~/.cursor/projects/*/agent-transcripts/*.jsonl` (message.content[].text)

**Offsets:** `~/.claude/.idea-harvest-claude-offset`, `~/.claude/.idea-harvest-codex-offset`, `~/.claude/.idea-harvest-cursor-done`

**Output:** `$idea` → `docs/research/idea-seeds/seed_{source}_{ts}_{id}.md`; `$defer/$pending` → `docs/research/pending-handoff.md` or `.thegent/next-session-prompts.md`

**Cursor path resolution:** Folder name = path segments joined by `-`; fallback: grep workspace_path from transcript metadata

### 3a.4 Rules Sync (Depth)

**Canonical source options:** `.thegent/rules/`, `.cursor/rules/`, `docs/reference/agent-rules/`

**Mapping:**
| Source format | Cursor | Claude Code | Codex | Droid |
|---------------|--------|--------------|-------|-------|
| .mdc | .cursor/rules/{name}.mdc | CLAUDE.md section or .claude/skills/{name}/SKILL.md | .codex/skills/{name}/SKILL.md | Inject into droid prompt |
| alwaysApply | alwaysApply: true | SessionStart inject | model_instructions | — |
| globs | globs field | N/A | N/A | — |

**Conflict:** Last-write-wins or configurable merge. Missing dirs → create.

### 3a.5 Team Coordinator (Depth)

**Storage:** `.thegent/teams/{team_id}/tasks.jsonl` — `{id, title, status, claimed_by, dependencies}`

**Spawn:** Lead = `thegent codex` or `codex`; Teammates = `codex exec - --cd /path --model X --json` with task prompt on stdin

**TeammateIdle:** Wrapper polls teammate stdout; when idle pattern detected → run hook script; exit 2 → inject feedback prompt

**TaskCompleted:** When teammate marks done via MCP → run TaskCompleted hook; exit 2 → block, send feedback

---

## 3b. Platform Variants & Edge Cases

| Platform | Variant | Config Path | Notes |
|----------|---------|-------------|-------|
| Claude Code | vs Claude Desktop | ~/.claude.json vs ~/Library/.../claude_desktop_config.json | Different config; both support MCP |
| Codex | Project vs user config | .codex/config.toml (trusted) vs ~/.codex/config.toml | Project overrides user |
| Cursor | Workspace vs user | .cursor/mcp.json vs ~/.cursor/mcp.json | Workspace preferred |
| Cursor | Composer vs cursor-agent | IDE vs CLI | Same MCP; different entry |
| Droid | Project only | .factory/mcp.json | No user-level |
| OpenCode | oc vs Zen | oc CLI vs Zen gateway | Zen = paid; don't integrate |

### 3b.1 Install Paths (Full)

| Client | MCP Config | Notify/Other |
|--------|------------|--------------|
| Cursor | ~/.cursor/mcp.json, .cursor/mcp.json | — |
| Claude Code | ~/.claude.json (stdio: command, args) | — |
| Codex | ~/.codex/mcp.json, ~/.config/codex/mcp.json | ~/.codex/config.toml notify |
| Claude Desktop | ~/Library/Application Support/Claude/claude_desktop_config.json | — |
| Droid | .factory/mcp.json | — |

### 3b.2 CLI Entry Points (Full)

| Platform | Interactive | Headless | thegent run |
|----------|-------------|----------|-------------|
| Claude Code | claude | claude -p "..." | run -M claude |
| Codex | codex | codex exec - | run -M codex |
| Cursor | Composer (IDE) | cursor-agent | run -M cursor-agent |
| Factory droid | — | droid exec -f path | run -M droid:name |
| Augment | auggie | auggie --print "..." | run -M augment |
| OpenCode | oc | oc | run -M opencode |
| Proxy (antigravity, kilo, etc.) | — | codex exec → proxy | run -M antigravity, etc. |

---

## 4. Unified Execution Plan (Phased)

### 4.1 Phase Dependencies (DAG)

```
Phase 1 (Foundation) ─┬─► Phase 2 (Exec preprocessor)
                     ├─► Phase 3 (Interactive wrapper)
                     ├─► Phase 4 (Queue TUI)
                     └─► Phase 7.1 (SessionStart)

Phase 2 ──────────────► Phase 6 (Agent teams)
Phase 4 ──────────────► Phase 6
Phase 6 ──────────────► Phase 7.4 (TeammateIdle, TaskCompleted)

Phase 9 (Rules sync) ──► Phase 10 (Cursor), Phase 11 (Droid)
Phase 10, 11, 12 ─────► Independent (Cursor, Droid, Augment)
Phase 13 ─────────────► OpenCode (independent)
```

### 4.2 Phase Summary Table

| Phase | Name | Platforms | Key Deliverables | Effort |
|-------|------|-----------|------------------|--------|
| **1** | Shared Foundation | All | Queue storage, migration, codex-notify, queue MCP tools | Medium |
| **2** | Exec Preprocessor | Codex, Droid, Augment, OpenCode | $defer/$block in run_impl; harvest on exit | Medium |
| **3** | Interactive Wrapper | Codex | thegent codex; exit hook | Small |
| **4** | Queue TUI | All | thegent queue tui; CLI; locking | Medium |
| **5** | Codex SDK (Optional) | Codex | Full UserPromptSubmit in interactive | High |
| **6** | Agent Teams | Codex, Droid | thegent team create; MCP tools; TeammateIdle | High |
| **7** | Full Hook Parity | Codex | SessionStart; SubagentStop; TeammateIdle | Medium |
| **8** | Claude Headless | Claude | run -M claude; --continue, --resume | Small |
| **9** | Rules Sync | All | thegent rules sync; canonical source | Medium |
| **10** | Cursor Integration | Cursor | run -M cursor-agent; harvest transcripts | Small |
| **11** | Droid Augmentation | Droid | $defer/$block; harvest; droid as teammate | Medium |
| **12** | Augment Integration | Augment | run -M augment; Context Engine MCP | Small |
| **13** | OpenCode Integration | OpenCode | run -M opencode; registry | Small |

### 4.3 Task-Level Matrix (Phase × Platform × Task)

| Phase | Task ID | Task | Claude | Codex | Cursor | Droid | Augment | OpenCode |
|-------|---------|------|:------:|:-----:|:------:|:-----:|:-------:|:--------:|
| 1 | 1.1 | Queue storage module | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1 | 1.2 | Migrate prompt-submit-guard to .thegent | ✓ | — | — | — | — | — |
| 1 | 1.3 | Migrate harvest to .thegent | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1 | 1.4 | codex-notify | — | ✓ | — | — | — | — |
| 1 | 1.5 | notify in install_to_codex | — | ✓ | — | — | — | — |
| 1 | 1.6 | thegent-queue skill | — | ✓ | — | — | — | — |
| 1 | 1.7 | Queue MCP tools | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | 2.1 | run_impl $defer/$block preprocessor | — | ✓ | — | ✓ | ✓ | ✓ |
| 2 | 2.2 | $defer → queue, no spawn | — | ✓ | — | ✓ | ✓ | ✓ |
| 2 | 2.3 | $block → escalation | — | ✓ | — | ✓ | ✓ | ✓ |
| 2 | 2.4 | Harvest on exit | — | ✓ | — | ✓ | ✓ | ✓ |
| 2 | 2.5 | Session start handoff | — | ✓ | — | — | — | — |
| 2 | 2.6 | SessionStart inject (Claude) | ✓ | — | — | — | — | — |
| 3 | 3.1 | thegent codex wrapper | — | ✓ | — | — | — | — |
| 3 | 3.2 | Optional codex shim | — | ✓ | — | — | — | — |
| 3 | 3.3 | Exit harvest integration | — | ✓ | — | — | — | — |
| 4 | 4.1 | thegent queue tui | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | 4.2 | queue CLI | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | 4.3 | Atomic claim/lease | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | 6.1 | Team task storage | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | 6.2 | Team MCP tools | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | 6.3 | thegent team create | — | ✓ | — | ✓ | — | — |
| 6 | 6.4 | team message/broadcast/shutdown | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | 6.5 | Display (tmux/TUI) | — | ✓ | — | ✓ | — | — |
| 6 | 6.6 | TeammateIdle | — | ✓ | — | ✓ | — | — |
| 6 | 6.7 | TaskCompleted hook | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | 6.8 | Headless team | — | ✓ | — | ✓ | — | — |
| 9 | 9.1 | Canonical rules format | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | 9.2 | thegent rules sync | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | 9.3 | Rule mapping | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | 9.4 | .cursorrules legacy | — | — | ✓ | — | — | — |
| 10 | 10.1 | run -M cursor-agent | — | — | ✓ | — | — | — |
| 10 | 10.2 | Harvest Cursor transcripts | — | — | ✓ | — | — | — |
| 10 | 10.3 | cursor-api queue/harvest | — | — | ✓ | — | — | — |
| 11 | 11.1 | Droid $defer/$block | — | — | — | ✓ | — | — |
| 11 | 11.2 | Droid harvest on exit | — | — | — | ✓ | — | — |
| 11 | 11.3 | Droid as teammate | — | — | — | ✓ | — | — |
| 11 | 11.4 | Droid rules inject | — | — | — | ✓ | — | — |
| 12 | 12.1 | run -M augment | — | — | — | — | ✓ | — |
| 12 | 12.2 | Context Engine MCP install | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 12 | 12.3 | Augment in registry | — | — | — | — | ✓ | — |
| 13 | 13.1 | run -M opencode | — | — | — | — | — | ✓ |
| 13 | 13.2 | OpenCode in registry | — | — | — | — | — | ✓ |

### 4.4 Granular Sub-Tasks (Phase 1 Example)

| Task | Sub-Task | Description | Acceptance |
|------|----------|-------------|------------|
| 1.1 | 1.1a | Create `src/thegent/queue/__init__.py` | Module imports |
| 1.1 | 1.1b | Implement `queue/storage.py` — append, read, list | Unit test: append 3, read 3 |
| 1.1 | 1.1c | Implement `queue/locking.py` — claim, release, extend_lease | Unit test: atomic claim |
| 1.1 | 1.1d | Path resolution: PROJECT/.thegent vs ~/.thegent | Fallback when project empty |
| 1.2 | 1.2a | Update prompt-submit-guard to write .thegent queue | Hook test: $defer → queue |
| 1.2 | 1.2b | Migration: if .claude/pending-queue.jsonl exists and .thegent empty, copy | Migration test |
| 1.2 | 1.2c | Dual-read during transition (read both, write .thegent) | Backward compat |
| 1.4 | 1.4a | Add `thegent codex-notify` subcommand | Parse argv[-1] JSON |
| 1.4 | 1.4b | Handle invalid JSON (log, exit 0) | No crash on malformed |
| 1.4 | 1.4c | Handle unknown type (ignore) | No crash |
| 1.7 | 1.7a | MCP tool: thegent_queue_list | Returns items[] |
| 1.7 | 1.7b | MCP tool: thegent_queue_claim | Atomic claim |
| 1.7 | 1.7c | MCP tool: thegent_queue_done | Mark done |
| 1.7 | 1.7d | MCP tools: add, edit, release, extend_lease | All implemented |

### 4.4b Granular Sub-Tasks (Phase 2)

| Task | Sub-Task | Description | Acceptance |
|------|----------|-------------|------------|
| 2.1 | 2.1a | Add flag regex to run_impl: `\$defer|\$pending|\$block|\$idea` | Unit: parse each flag |
| 2.1 | 2.1b | Branch before spawn: if $defer/$pending → queue path | No subprocess |
| 2.1 | 2.1c | Branch: if $block → govern escalate add | Exit 1 |
| 2.2 | 2.2a | queue.append() with ts, prompt, project | Queue has entry |
| 2.2 | 2.2b | Return JSON: `{queued: true, count: N}` | CLI output |
| 2.4 | 2.4a | Register atexit or subprocess callback | On exit |
| 2.4 | 2.4b | Call harvest-pending-queue logic | Handoff written |
| 2.4 | 2.4c | Call harvest-idea-seeds logic | Idea seeds written |
| 2.5 | 2.5a | Read .thegent/next-session-prompts.md | If exists |
| 2.5 | 2.5b | Prepend to stdin before prompt | Exec receives |

### 4.4c Granular Sub-Tasks (Phase 6)

| Task | Sub-Task | Description | Acceptance |
|------|----------|-------------|------------|
| 6.1 | 6.1a | Create `src/thegent/team/` module | Module imports |
| 6.1 | 6.1b | team/storage.py: tasks.jsonl read/write | CRUD tasks |
| 6.1 | 6.1c | Path: `.thegent/teams/{id}/tasks.jsonl` | Dir created |
| 6.2 | 6.2a | MCP: thegent_team_create | Returns team_id |
| 6.2 | 6.2b | MCP: thegent_team_task_list, assign, claim, done | All work |
| 6.2 | 6.2c | MCP: thegent_team_message, broadcast, shutdown | All work |
| 6.3 | 6.3a | team create: spawn lead (thegent codex or codex) | Process up |
| 6.3 | 6.3b | team create: spawn N teammates (codex exec -) | N processes |
| 6.3 | 6.3c | Pass task prompt via stdin or file | Teammate receives |
| 6.5 | 6.5a | tmux split panes option | Each teammate in pane |
| 6.5 | 6.5b | In-process TUI option (Shift+Up/Down) | List teammates |
| 6.6 | 6.6a | Poll teammate stdout for idle pattern | Detect |
| 6.6 | 6.6b | Run TeammateIdle hook script | Exit 2 → feedback |
| 6.6 | 6.6c | Inject feedback prompt to teammate | Teammate continues |

### 4.4d Granular Sub-Tasks (Phase 9)

| Task | Sub-Task | Description | Acceptance |
|------|----------|-------------|------------|
| 9.1 | 9.1a | Choose canonical: .thegent/rules or .cursor/rules | Decision doc |
| 9.1 | 9.1b | Define .mdc format (description, globs, alwaysApply) | Schema |
| 9.2 | 9.2a | rules/sync.py: read canonical | Parse all |
| 9.2 | 9.2b | Emit .cursor/rules/{name}.mdc | Copy or transform |
| 9.2 | 9.2c | Emit CLAUDE.md section or .claude/skills | Merge |
| 9.2 | 9.2d | Emit .codex/skills/{name}/SKILL.md | Create dir |
| 9.2 | 9.2e | Droid: inject rules into prompt | Prepend |
| 9.3 | 9.3a | Map .mdc globs → Cursor only | N/A for Claude/Codex |
| 9.3 | 9.3b | Map alwaysApply → SessionStart inject (Claude) | — |
| 9.4 | 9.4a | Parse .cursorrules if exists | Legacy |
| 9.4 | 9.4b | Merge into rules or emit as single rule | — |

### 4.5 Phase Dependencies (Detailed DAG)

```
Phase 1.1 (queue storage) ──► 1.2 (migration), 1.7 (MCP tools), 4.1 (TUI)
Phase 1.4 (codex-notify) ───► 1.5 (config merge), 3.1 (wrapper)
Phase 1.7 (queue MCP) ──────► 2.1 (preprocessor), 6.2 (team MCP)
Phase 2.1 (preprocessor) ───► 2.2, 2.3, 2.4; 6.3 (team create)
Phase 3.1 (wrapper) ────────► 3.3 (exit harvest)
Phase 4.1 (TUI) ────────────► 4.2, 4.3; 6.5 (team display)
Phase 6.1 (team storage) ───► 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8
Phase 9.1 (canonical rules) ► 9.2, 9.3, 9.4; 10.2, 11.4
Phase 10, 11, 12, 13 ──────► Independent; can run in parallel
```

### 4.6 Effort & Dependency Summary

| Phase | Effort | Blocked By | Unblocks |
|-------|--------|------------|----------|
| 1 | Medium | — | 2, 3, 4, 7 |
| 2 | Medium | 1 | 6 |
| 3 | Small | 1 | — |
| 4 | Medium | 1 | 6 |
| 5 | High | — | — (optional) |
| 6 | High | 2, 4 | 7 |
| 7 | Medium | 6 | — |
| 8 | Small | — | — |
| 9 | Medium | — | 10, 11 |
| 10 | Small | 9 | — |
| 11 | Medium | 9 | — |
| 12 | Small | — | — |
| 13 | Small | — | — |

---

## 5. Success Criteria (Platform-by-Platform)

### 5.1 Claude Code

- [ ] UserPromptSubmit: $defer/$pending queues, $block escalates, $idea saves
- [ ] Stop: harvest-pending-queue flushes to handoff
- [ ] Queue path: unified `.thegent/prompt_queue.jsonl`
- [ ] Queue tools: agent can list, claim, done via MCP
- [ ] Queue TUI: user can add/edit/list
- [ ] Headless: `thegent run -M claude "prompt"` uses `claude -p`
- [ ] SessionStart: optional handoff inject
- [ ] Rules sync: `thegent rules sync` writes to CLAUDE.md

### 5.2 Codex

- [ ] Interactive: on exit, harvest runs
- [ ] Headless: $defer, $block, harvest on exit
- [ ] Exec: $defer queues, $block escalates
- [ ] notify: thegent receives AfterAgent JSON
- [ ] Queue tools: agent can list, claim, done via MCP
- [ ] Queue TUI: same as Claude
- [ ] Agent teams: `thegent team create` spawns lead + teammates
- [ ] Rules sync: `thegent rules sync` writes to .codex/skills

### 5.3 Cursor-Agent

- [ ] `thegent run -M cursor-agent "prompt"` headless
- [ ] Harvest: $defer/$pending/$idea from Cursor transcripts
- [ ] Rules sync: `thegent rules sync` writes to .cursor/rules
- [ ] MCP: thegent tools available

### 5.4 Factory Droid

- [ ] `thegent run -M droid:name "prompt"` — $defer/$block, harvest on exit
- [ ] Droid as teammate in agent teams
- [ ] Rules injected into droid prompt
- [ ] MCP: thegent tools available

### 5.5 Augment Code

- [ ] `thegent run -M augment "prompt"` — auggie --print
- [ ] Context Engine MCP in thegent mcp install
- [ ] Documented in agent registry

### 5.6 OpenCode

- [ ] `thegent run -M opencode "prompt"` — oc
- [ ] Documented in agent registry
- [ ] Zen: NOT integrated (per ZEN_INTEGRATION.md)

### 5.7 Shared (Cross-Platform)

- [ ] Single queue storage for all platforms
- [ ] Unified rules: `thegent rules sync` → Cursor, Claude, Codex, droid
- [ ] Lifecycle: loop can check queue between iterations
- [ ] All features available interactively and headlessly (where applicable)
- [ ] MCP: 30+ tools, 20+ resources, same across all clients

---

## 6. Supercede Matrix (Where thegent Exceeds)

| Dimension | Best-in-Class Platform | thegent Supercede |
|-----------|------------------------|-------------------|
| **Unified queue** | Claude Code (per-platform) | Single .thegent queue; works for Claude, Codex, Cursor, droid, Augment, OpenCode |
| **Unified rules** | Cursor (.cursor/rules) | Single source → sync to 5+ platforms |
| **Unified harvest** | Per-platform scripts | Single harvest from Claude + Codex + Cursor |
| **Teams** | Claude Code / Augment Intent | thegent team: Codex, droid; CLI + MCP; no desktop required |
| **Model routing** | OpenCode Zen (paid) | 12+ providers, free-first (Antigravity, Kilo, NIM) |
| **Orchestration** | Augment Intent (desktop) | CLI + MCP; CI-ready; any agent |
| **MCP surface** | Per-client config | 30+ tools, 20+ resources; install once, use everywhere |
| **Agent coverage** | Single platform | 6 platforms: Claude, Codex, Cursor, droid, Augment, OpenCode |

---

## 6a. Error Handling & Edge Cases (Depth)

| Component | Error | Handling |
|-----------|-------|----------|
| **Queue** | Corrupt file | Truncate to last valid line; log; continue |
| **Queue** | Concurrent claim | Atomic rename or lock file; `claimed_by` + `lease_expires_at` |
| **Queue** | Empty project | Fallback to `~/.thegent/prompt_queue.jsonl` |
| **Harvest** | Missing offset | Start from line 0 |
| **Harvest** | Cursor path unknown | Use workspace_path from metadata; fallback grep |
| **Harvest** | Large history | Stream; don't load full file |
| **codex-notify** | Invalid JSON | Log; exit 0 (don't fail Codex) |
| **codex-notify** | Unknown type | Ignore |
| **Rules sync** | Missing target dir | Create `.cursor/rules`, `.codex/skills` |
| **Rules sync** | Conflict | Last-write-wins or configurable merge |
| **run_impl** | Agent not found | Clear error: "Agent X not found. Run thegent list-agents." |
| **run_impl** | $block escalation | Return block message; exit 1 |
| **Team** | Teammate crash | Mark task failed; notify lead |
| **Team** | Lead exit mid-task | Teammates continue; harvest on teammate exit |

### 6a.1 Rollback & Migration

| Change | Rollback |
|--------|----------|
| Queue path .claude → .thegent | Keep dual-read; revert prompt-submit-guard to write .claude |
| codex notify | Remove from config.toml; Codex continues without |
| Rules sync | Manual revert of .cursor/rules, CLAUDE.md, .codex/skills |
| Team module | Remove team create; MCP tools no-op |

---

## 6b. Testing Strategy (Depth)

| Component | Test Type | Coverage |
|------------|------------|----------|
| **Queue storage** | Unit | append, read, claim, release, extend_lease, concurrent claim |
| **Queue migration** | Integration | .claude exists → migrate → .thegent has data |
| **run_impl preprocessor** | Unit | $defer → no spawn, queue append; $block → exit 1; no flag → spawn |
| **codex-notify** | Unit | Valid JSON → parse; invalid → exit 0; unknown type → ignore |
| **Harvest** | Integration | Mock history files → run harvest → assert output |
| **Rules sync** | Integration | Canonical source → sync → assert .cursor, CLAUDE.md, .codex |
| **Team** | Integration | team create → assert N processes; task assign → teammate receives |
| **prompt-submit-guard** | Unit | $defer stdin → assert queue append, exit |
| **Wrapper exit** | Integration | Spawn codex, kill → assert harvest runs |

### 6b.1 Test Matrix (Platform × Capability)

| Test | Claude | Codex | Cursor | Droid | Augment | OpenCode |
|------|:------:|:-----:|:------:|:-----:|:-------:|:--------:|
| run -M X "prompt" | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| run -M X "prompt $defer" | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| run -M X "prompt $block" | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| Harvest on exit | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Queue MCP tools | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Rules sync | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Team create | — | ✓ | — | ✓ | — | — |

---

## 6c. Observability & Governance (Breadth)

| Dimension | Platform Native | thegent |
|------------|------------------|---------|
| **Run registry** | — | `.thegent/sessions/run_registry.jsonl` |
| **Contract telemetry** | — | `.thegent/sessions/contract_telemetry.jsonl` |
| **Escalation queue** | — | `.thegent/sessions/escalation_queue.jsonl` |
| **Circuit breakers** | — | `.thegent/sessions/circuit_breakers.jsonl` |
| **Cost governance** | — | thegent govern; cost caps |
| **Quality gates** | Claude hooks | hooks/quality-gate.sh; spec-verifier |
| **Health gate** | — | thegent_session_contract_health_gate |
| **Observe summary** | — | thegent_observe_summary |

### 6c.1 Governance Parity

| Governance | Claude | Codex | Cursor | thegent |
|------------|:------:|:-----:|:------:|---------|
| PreToolUse block | ✓ | ✗ | ✗ | N/A exec |
| Cost cap | — | — | — | thegent govern |
| Quality gate | Stop hook | — | — | quality-gate.sh |
| Escalation | $block | — | — | govern escalate |
| Spec traceability | — | — | — | spec-verifier |

### 6c.2 Contract & SLO Dimensions (Depth)

| Dimension | Contract | SLO | Gate |
|------------|----------|-----|------|
| **Session routing** | route_contract | Resolved provider | session_contract_health_gate |
| **Model availability** | ModelCatalog | Route exists | list_models |
| **Fallback rate** | — | <5% structural, <10% semantic | observe_summary |
| **Queue latency** | — | append <10ms | — |
| **Harvest completeness** | — | All sources processed | — |
| **FR traceability** | spec-verifier | 100% FRs have tests | spec-verifier |
| **Health ratio** | — | min_healthy_ratio 1.0 | session_contract_health_gate |

---

## 7. Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| Platform config changes | Version check; graceful fallback; merge, don't overwrite |
| Client MCP gaps (elicitation, progress) | Queue/blocking uses hooks, not MCP elicitation |
| Codex notify payload change | Parse with fallback; log unknown types |
| Queue file corruption | Append-only; atomic writes; lock file |
| Rules sync conflicts | Last-write-wins or configurable merge |
| Droid/oc not installed | Detect; clear error; document in install guide |
| Teammate crash | Mark task failed; notify lead; optional restart |
| Harvest path changes | Configurable paths; fallback resolution |
| Config overwrite | Merge only; never replace entire config |
| notify script blocks | Codex spawns async; fire-and-forget |

### 7.1 Platform-Specific Risks

| Platform | Risk | Mitigation |
|----------|------|------------|
| Codex | notify blocks | Async spawn; timeout optional |
| Cursor | Transcript path varies | Multiple path patterns; workspace_path metadata |
| Droid | droid not in PATH | Check ~/.local/bin, ~/.factory/bin; clear error |
| Augment | auggie not installed | Detect; suggest install; fallback message |
| OpenCode | Zen cost | Do not integrate Zen (ZEN_INTEGRATION.md) |

---

## 8. File Paths & Schemas Reference

### 8.1 Key Paths

| Purpose | Path |
|---------|------|
| Queue (project) | `PROJECT/.thegent/prompt_queue.jsonl` |
| Queue (global) | `~/.thegent/prompt_queue.jsonl` |
| Queue (legacy) | `~/.claude/pending-queue.jsonl`, `PROJECT/.claude/pending-queue.jsonl` |
| Team tasks | `.thegent/teams/{team_id}/tasks.jsonl` |
| Handoff | `docs/research/pending-handoff.md`, `.thegent/next-session-prompts.md` |
| Idea seeds | `docs/research/idea-seeds/seed_{source}_{ts}_{id}.md` |
| Harvest offsets | `~/.claude/.idea-harvest-{claude,codex,cursor}-*` |
| Claude history | `~/.claude/history.jsonl` |
| Codex history | `~/.codex/history.jsonl` |
| Cursor transcripts | `~/.cursor/projects/Users-*/agent-transcripts/*.jsonl` |
| Run registry | `.thegent/sessions/run_registry.jsonl` |
| Escalation | `.thegent/sessions/escalation_queue.jsonl` |
| Rules (canonical) | `.thegent/rules/` or `.cursor/rules/` |
| Codex skills | `.codex/skills/{name}/SKILL.md` |
| Cursor rules | `.cursor/rules/{name}.mdc` |
| Factory droids | `.factory/droids/*.md` |

### 8.2 Queue Schema

```json
{"ts":"ISO8601","prompt":"...","project":"/path","claimed_by":null,"lease_expires_at":null}
```

### 8.3 Team Task Schema

```json
{"id":"task-1","title":"...","status":"pending|in_progress|done","claimed_by":null,"dependencies":[]}
```

### 8.4 codex-notify Payload

```json
{"type":"agent-turn-complete","thread-id":"uuid","turn-id":"turn-1","cwd":"/path","input-messages":["..."],"last-assistant-message":"..."}
```

### 8.5 Config Merge Algorithm (Codex notify)

```python
# Pseudocode: mcp_manage or install step
def merge_codex_notify(config_path: Path) -> None:
    config = read_toml(config_path)
    notify = config.get("notify") or []
    if not isinstance(notify, list):
        notify = [notify]
    if "thegent" not in [str(x) for x in notify]:
        notify = list(notify) + ["thegent", "codex-notify"]
        config["notify"] = notify
        write_toml(config_path, config)
```

### 8.6 Run State Machine (Depth)

```
                    ┌─────────────┐
                    │   PENDING   │  (queued, not claimed)
                    └──────┬──────┘
                           │ claim
                           ▼
                    ┌─────────────┐
                    │   RUNNING   │  (agent process active)
                    └──────┬──────┘
                           │ exit 0 / timeout / kill
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │ COMPLETED│  │  FAILED  │  │ TIMED_OUT│
       └──────────┘  └──────────┘  └──────────┘
```

**Queue item states:** unclaimed → claimed (lease) → done | released

### 8.7 Agent Discovery Resolution (Depth)

| Step | Action | Source |
|------|--------|--------|
| 1 | Resolve alias (cursor-api → cursor) | _AGENT_ALIASES |
| 2 | Direct agent? (cursor, claude, codex, gemini, copilot) | DIRECT_AGENTS |
| 3 | Proxy agent? (antigravity, kilo, nim, cliproxy, etc.) | PROXY_AGENTS |
| 4 | Droid? (droid:name) | .factory/droids/*.md |
| 5 | Teammate from agents/*.md? | WP-16001 |
| 6 | Unknown | Return None; "Agent X not found" |

**Registry:** `src/thegent/agents/registry.py` — `get_runner(agent_name)`

### 8.8 CLI Command Surface (Breadth)

| Command | Purpose | Platforms |
|---------|---------|-----------|
| thegent run -M {agent} "prompt" | Headless run | All |
| thegent bg -M {agent} "prompt" | Background run | All |
| thegent codex / dex / clode | Interactive wrapper | Codex, Claude |
| thegent queue add\|list\|edit\|release\|status | Queue CLI | All |
| thegent queue tui | Queue TUI | All |
| thegent team create\|list\|message\|shutdown | Team CLI | Codex, Droid |
| thegent rules sync | Rules sync | All |
| thegent govern escalate add\|list\|resolve | Escalation | All |
| thegent codex-notify | Codex notify handler | Codex |
| thegent serve | MCP HTTP server | All |
| thegent mcp install {cursor,codex,...} | MCP config | All |
| thegent list-agents | List agents | All |
| thegent list-droids | List droids | All |
| thegent list-models | List models | All |
| thegent ps / status / logs / inspect | Session discovery | All |
| thegent loop / loop-takeover / loop-stop | Lifecycle | All |

### 8.9 Output Parsing & Extraction (Depth)

| Agent | Output Format | thegent Extraction |
|-------|---------------|-------------------|
| Claude | Stream or JSON | OUTPUT_PARSER_SCHEMA_VERSION; <think>, \<action\> |
| Codex | Stream; --json for JSONL | Passthrough; optional parse |
| Droid | stream-json | Passthrough |
| Augment | — | Passthrough |
| OpenCode | — | Passthrough |

**Condensation:** `full=False` → condensed output; `full=True` → raw. Used for quality-focused agents.

### 8.10 Quality & Security Pipeline (Breadth)

| Pipeline | Hooks | Triggers |
|----------|-------|----------|
| **quality-gate** | Stop | lint, test, coverage, traceability |
| **spec-verifier** | Stop | FR traceability, orphan check |
| **security-pipeline** | Stop | gitleaks, SAST, dependency audit |
| **suppression-blocker** | PreToolUse: Edit, Write | Block new lint suppressions |
| **prompt-submit-guard** | UserPromptSubmit | $defer, $block, $idea |
| **harvest-pending-queue** | Stop | Flush queue to handoff |
| **harvest-idea-seeds** | Stop | Extract $idea from history |

---

## 9. MCP Tool Coverage (Breadth)

| Tool Category | Tools | Platforms Using |
|---------------|-------|-----------------|
| **Run** | thegent_run, thegent_bg, thegent_do_next | All (via MCP) |
| **Queue** | thegent_queue_list, claim, done, add, edit, release, extend_lease | All (Phase 1) |
| **Team** | thegent_team_create, task_list, task_assign, task_claim, task_done, message, broadcast, shutdown | Codex, Droid (Phase 6) |
| **Discovery** | thegent_ps, status, logs, inspect, list_agents, list_droids, list_models | All |
| **Contract** | session_contracts, health_gate, health_report, health_trend | All |
| **Observe** | thegent_observe_summary | All |
| **Inbox** | thegent_inbox_list, thegent_inbox_wait | All |
| **Planning** | thegent_dag_list, thegent_do_next | All |
| **Terminal** | thegent_terminal_list, inspect, send, attach | All (tmux) |
| **Loop** | thegent_loop, thegent_loop_takeover, thegent_loop_stop | All |

**Client MCP config:** Claude Code (stdio), Cursor (HTTP), Codex (HTTP), Droid (.factory/mcp.json). Same tools, different transport.

---

## 9a. Proxy Agents (Breadth)

| Proxy | Backend | Models | thegent run |
|-------|---------|--------|-------------|
| antigravity | CLIProxyAPIPlus | Claude, Gemini (free) | run -M antigravity |
| kilo | CLIProxyAPIPlus | Kimi K2.5, DeepSeek, GLM, MiniMax, Qwen (free) | run -M kilo |
| nim | CLIProxyAPIPlus | DeepSeek, Llama Nemotron (free) | run -M nim |
| cliproxy | CLIProxyAPIPlus | Configurable | run -M cliproxy |
| minimax | CLIProxyAPIPlus | MiniMax | run -M minimax |
| glm | CLIProxyAPIPlus | GLM | run -M glm |

**Parity:** Proxy agents use Codex exec → CLIProxyAPIPlus; same run_impl preprocessor applies ($defer/$block); harvest on exit. No native hooks; thegent provides queue, harvest, MCP.

---

## 9b. Future & Consideration Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| **GooseAI** | Consideration | Inference API, not coding agent; could be model provider |
| **Windsurf** | Consideration | IDE agent; similar to Cursor |
| **Replit Agent** | Consideration | Cloud-based; different model |
| **GitHub Copilot** | Consideration | Already via run -M copilot; limited |
| **Bolt (StackBlitz)** | Consideration | Web IDE agent |
| **Continue** | Consideration | VS Code extension; MCP support |

**Integration pattern:** Add to registry; run -M {name}; same queue/harvest/rules if applicable.

---

## 9c. Sitback & TUI Integration (Breadth)

| Component | Purpose | Platforms |
|-----------|---------|-----------|
| **thegent sitback** | Launch Claude Code with Sitback Agent | Claude Code |
| **Sitback dashboard** | MCP resource: thegent://sitback/dashboard | All (cached 30s) |
| **thegent queue tui** | Textual TUI for queue | All |
| **Terminal tools** | thegent_terminal_list, inspect, send, attach | tmux |
| **heliosShield** | thegent_heliosShield_status | Multi-agent coordination |

**Sitback skills:** `skills/sitback-agent/` (default); overridable via `--skill`. MCP precondition: `thegent serve` for full toolset.

---

## 9d. Debugging & Troubleshooting (Depth)

| Symptom | Check | Resolution |
|---------|-------|------------|
| run -M X fails | `thegent list-agents` | Add agent to registry; check PATH |
| $defer not queuing | run_impl preprocessor | Ensure regex matches; check queue path |
| codex-notify not firing | ~/.codex/config.toml notify | Add ["thegent","codex-notify"]; merge |
| Harvest empty | Offset files; history paths | Reset offset; verify path exists |
| Rules sync overwrote | Conflict strategy | Use last-write-wins or backup before sync |
| Team teammate not receiving | stdin pipe | Verify task prompt on stdin |
| MCP tools not visible | Client MCP config | thegent mcp install {client} |
| Queue claim fails | claimed_by, lease | Release stale; extend_lease |
| Cursor harvest fails | Transcript path | Check ~/.cursor/projects/*/agent-transcripts |

### 9d.1 Diagnostic Commands

| Command | Purpose |
|---------|---------|
| `thegent ps --all` | List all sessions including completed |
| `thegent inspect --owner X` | Deep session inspection |
| `thegent session-contracts --missing-only` | Contract gaps |
| `thegent observe-summary` | KPIs, drift, escalations |
| `thegent govern escalate list --past-sla` | Blocked items |
| `thegent list-models --by-model` | Model → provider routing |

---

## 9e. SLO & Performance Targets (Depth)

| Metric | Target | Notes |
|--------|--------|------|
| run_impl preprocessor | <50ms | Before spawn |
| Queue append | <10ms | Atomic write |
| codex-notify parse | <5ms | Fire-and-forget |
| MCP tool latency | <500ms (read) | Exclude run, bg |
| thegent_run | Agent-dependent | Progress every 10s |
| Harvest (full) | <30s | Stream; don't load all |
| Rules sync | <5s | Per rule |
| Queue TUI render | <100ms | Cached where possible |

### 9e.1 Concurrency

| Operation | Safe? | Notes |
|-----------|-------|-------|
| Queue append | Yes | Append-only; atomic |
| Queue claim | Yes | claimed_by + lease; atomic |
| Harvest (multi-source) | Yes | Per-source offset; no shared state |
| Rules sync | Caution | Last-write-wins; avoid concurrent sync |
| Team task update | Yes | JSONL append or file lock |

---

## 9f. Model Routing Policies (Breadth)

| Policy | Behavior | Use Case |
|--------|----------|----------|
| prefer_direct | Direct API first (OpenAI, Anthropic, etc.) | Default |
| prefer_proxy | Proxy first (Antigravity, Kilo, NIM) | Free-first |
| failover | Try direct; on failure try next route | Resilience |
| round_robin | Rotate across providers | Load spread |
| cheapest | Lowest cost route | Cost optimization |

**Config:** `default_routing` in ThegentSettings; override via `--routing` or MCP param.

---

## 9g. Migration Script Steps (Depth)

### Queue Migration (.claude → .thegent)

1. **Pre:** Ensure prompt-submit-guard, harvest-pending-queue exist
2. **Create** PROJECT/.thegent/ and ~/.thegent/ if missing
3. **If** PROJECT/.claude/pending-queue.jsonl exists AND PROJECT/.thegent/prompt_queue.jsonl empty:
   - Read each line from .claude
   - Append to .thegent (preserve schema; add ts if missing)
   - Truncate or clear .claude (optional: keep backup)
4. **Same** for ~/.claude and ~/.thegent
5. **Update** prompt-submit-guard to write .thegent only
6. **Update** harvest-pending-queue to read .thegent only
7. **Dual-read** for 1 release: read both; write .thegent
8. **Post:** Remove dual-read; .thegent only

### Config Merge (Codex)

1. **Read** ~/.codex/config.toml (or .codex/config.toml)
2. **Parse** TOML
3. **Get** notify = config["notify"] or []
4. **If** "thegent" not in notify: append ["thegent", "codex-notify"]
5. **Write** back; preserve other keys
6. **Never** overwrite entire file

---

## 10. End-to-End Design (Holistic Flows)

### 10.1 Session Lifecycle (Complete)

```
User starts session
    │
    ├─► [Interactive] thegent codex / clode / dex
    │       │
    │       ├─► SessionStart (optional): inject handoff summary
    │       ├─► User types prompts
    │       │       │
    │       │       └─► [Claude] UserPromptSubmit → prompt-submit-guard ($defer/$block/$idea)
    │       │
    │       └─► User exits
    │               │
    │               └─► Stop: harvest-pending-queue, harvest-idea-seeds
    │
    └─► [Headless] thegent run -M X "prompt"
            │
            ├─► run_impl preprocessor: $defer → queue, return; $block → escalate, exit 1
            ├─► No flag: spawn agent, pipe prompt
            │       │
            │       └─► Agent exits
            │               │
            │               └─► Harvest on exit (same as Stop)
            │
            └─► Return stdout/stderr/exit_code
```

**Completeness:** Every path has a defined exit. No dangling states.

### 10.2 Queue → Harvest → Handoff (Complete)

```
$defer in prompt
    │
    └─► Append to .thegent/prompt_queue.jsonl
            │
            └─► Session ends (Stop / exit)
                    │
                    └─► harvest-pending-queue
                            │
                            └─► Flush queue → .thegent/next-session-prompts.md (or pending-handoff.md)
                                    │
                                    └─► Next session: SessionStart / exec stdin prepend
                                            │
                                            └─► User sees "N pending from last session" or first prompt
```

**Completeness:** Queue → handoff → next session. No orphaned deferred items.

### 10.3 Rules Sync (Complete)

```
Canonical source (.thegent/rules or .cursor/rules)
    │
    ├─► .cursor/rules/{name}.mdc (Cursor)
    ├─► CLAUDE.md section or .claude/skills/{name}/SKILL.md (Claude)
    ├─► .codex/skills/{name}/SKILL.md (Codex)
    └─► Droid prompt inject (Factory)
```

**Completeness:** One write, N targets. Idempotent; re-run safe.

### 10.4 Team Lifecycle (Complete)

```
thegent team create --teammates 3
    │
    ├─► Spawn lead (thegent codex)
    ├─► Spawn 3 teammates (codex exec -)
    ├─► Shared task list (.thegent/teams/{id}/tasks.jsonl)
    │
    ├─► Lead assigns via MCP
    ├─► Teammate claims, executes, marks done
    │       │
    │       └─► TaskCompleted hook (optional block)
    │
    ├─► TeammateIdle → wrapper injects feedback
    │
    └─► thegent team shutdown → graceful terminate
```

**Completeness:** Create → assign → execute → done → shutdown. No zombie teammates.

---

## 11. Optimization, Polish & Enhancements

### 11.1 Applied to Multi-Platform (From 08-OPTIMIZATION-CATALOG)

| Category | Item | Multi-Platform Application |
|----------|------|----------------------------|
| **Performance** | OPT-021 span attributes | Add model, provider, platform to run_impl spans |
| **Performance** | OPT-002 rate limiting | MCP already has 10/s; queue TUI debounce |
| **Performance** | OPT-020 route memo | Model-first routing in run_impl; cache resolved route |
| **Robustness** | ROB-013 config validation | Validate queue path, harvest paths on startup |
| **Robustness** | ROB-007 graceful shutdown | MCP drain; wrapper waits for harvest |
| **Robustness** | ROB-005 idempotency | Queue claim: idempotent release; extend_lease idempotent |
| **UX** | UX-001 tool annotations | Queue tools: readOnlyHint, idempotentHint |
| **UX** | UX-005 actionable errors | "Agent X not found. Run: thegent list-agents" |
| **UX** | UX-008 progressive disclosure | Queue TUI: list → inspect → claim |
| **DX** | DX-003 thegent inspect | Already exists; ensure queue/team visibility |

### 11.2 Multi-Platform–Specific Polish

| Area | Polish | Rationale |
|------|--------|-----------|
| **Queue** | `thegent queue status` — one-line summary (N pending, M claimed) | Quick glance |
| **Queue** | Lease expiry warning in TUI when <2min left | Avoid accidental release |
| **Harvest** | Progress indicator for large history (streaming) | UX for big transcripts |
| **Rules sync** | `--dry-run` to preview changes | Safe trial |
| **Team** | `thegent team status` — lead + teammates, task counts | At-a-glance |
| **run -M** | Suggest fallback agent on "not found" | Self-service |
| **codex-notify** | Structured log line (thread_id, turn_id) for traceability | Debugging |

### 11.3 Enhancement Tiers (Prioritized)

| Tier | Scope | Examples |
|------|-------|----------|
| **Tier 1 (Must)** | Parity + robustness | Queue, harvest, rules sync, team; error handling |
| **Tier 2 (Should)** | Polish + observability | Queue TUI, status commands, span attributes |
| **Tier 3 (Nice)** | Convenience | --dry-run, lease warning, fallback suggestion |
| **Tier 4 (Defer)** | Speculative | Multi-queue namespaces, rule versioning |

**Lean rule:** Tier 4 only when a concrete use case emerges.

---

## 12. Intuitive & Robust Feature Design

### 12.1 Intuitive Design Principles

| Principle | Application |
|-----------|-------------|
| **Consistent entry** | `thegent run -M {agent}` for all agents; same flags (--cd, --timeout) |
| **Predictable output** | JSON when --json; text when not; same schema across agents |
| **Discoverable** | `thegent list-agents`, `thegent queue --help`; no hidden commands |
| **Composable** | Queue + harvest + rules are independent; combine via flows |
| **Fail fast** | Config validation on startup; agent not found before spawn |
| **Clear feedback** | "Queued. 3 pending." not "Done."; "Agent X not found" with hint |

### 12.2 Robust Design Principles

| Principle | Application |
|-----------|-------------|
| **Explicit failure** | No silent degradation; $block returns block message, exit 1 |
| **Atomic operations** | Queue claim: atomic; append: atomic write |
| **Idempotent where safe** | Queue release, extend_lease; rules sync |
| **Bounded state** | Lease expiry; max queue size (optional); harvest offset |
| **Recoverable** | Queue corruption → truncate; harvest offset missing → start 0 |
| **Observable** | run_registry, escalation_queue, health gate |

### 12.3 Over-Engineering Avoidance

| Avoid | Prefer |
|-------|--------|
| Generic "orchestration framework" | Queue, team, rules as focused modules |
| Rule versioning before first conflict | Last-write-wins; add versioning if needed |
| Multi-queue namespaces before use case | Single queue; project vs global is enough |
| Custom DSL for rules | .mdc + YAML frontmatter (standard) |
| Abstract "agent adapter" interface | get_runner() + registry (concrete) |
| Event bus for internal comms | Direct calls; file/JSONL for persistence |

---

## 13. Complete End-to-End Plan (Unified View)

### 13.1 User Journeys (End-to-End)

| Journey | Steps | Platforms |
|---------|-------|-----------|
| **Defer and resume** | Prompt with $defer → queue → exit → next session → handoff inject → user continues | Claude, Codex, Droid, Augment, OpenCode |
| **Block and escalate** | Prompt with $block → escalate → resolve via CLI → retry | All |
| **Idea capture** | Prompt with $idea → save to idea-seeds → harvest on Stop | Claude, Codex, Cursor |
| **Multi-agent team** | team create → assign tasks → teammates execute → done → shutdown | Codex, Droid |
| **Unified rules** | Edit .thegent/rules → rules sync → all platforms updated | All |
| **Cross-platform run** | run -M codex "X" then run -M claude "Y" — same queue, same harvest | All |

### 13.2 Component Dependency Graph

```
                    ┌─────────────┐
                    │   run_impl  │
                    └──────┬──────┘
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                  ▼
  ┌────────────┐   ┌────────────┐   ┌────────────┐
  │   queue    │   │  escalate  │   │   spawn    │
  └─────┬──────┘   └────────────┘   └─────┬──────┘
        │                                  │
        │                           ┌──────┴──────┐
        │                           ▼             ▼
        │                    ┌────────────┐  ┌─────────┐
        │                    │   agent    │  │ harvest │
        │                    └────────────┘  └────┬────┘
        │                                         │
        └─────────────────────────────────────────┘
                          │
                          ▼
                   ┌────────────┐
                   │  handoff   │
                   └────────────┘
```

### 13.3 Verification Checklist (End-to-End)

- [ ] Defer → queue → exit → next session sees handoff
- [ ] Block → escalate → resolve → can retry
- [ ] Idea → idea-seeds file created
- [ ] Team create → N processes → tasks flow → shutdown clean
- [ ] Rules sync → Cursor, Claude, Codex, droid all updated
- [ ] run -M X for each platform works
- [ ] Queue TUI: add, list, claim, done
- [ ] Harvest from Claude + Codex + Cursor in one run
- [ ] MCP tools work from Claude Code, Cursor, Codex

---

## 14. Quick Reference

| Need | Location |
|------|----------|
| Design philosophy | §0 |
| End-to-end flows | §10 (Session, Queue→Harvest→Handoff, Rules, Team) |
| Optimization & polish | §11 (OPT/ROB/UX mapping, tiers) |
| Intuitive & robust design | §12 |
| Complete plan & verification | §13 |
| Phase tasks | §4.3 Task-Level Matrix |
| Granular sub-tasks | §4.4 (Phase 1), §4.4b (Phase 2), §4.4c (Phase 6), §4.4d (Phase 9) |
| Hooks pipeline | §2.4 |
| Sandbox/permission models | §2.5 |
| Platform strategy | §3 Platform-by-Platform |
| Implementation depth | §3a |
| Platform variants | §3b |
| Success criteria | §5 |
| Supercede opportunities | §2.4, §6 |
| Hook-by-hook strategy | §2.3 |
| Extended capabilities | §2.2 |
| Error handling | §6a |
| Testing strategy | §6b |
| Observability | §6c |
| File paths | §8.1 |
| Schemas | §8.2–8.4 |
| Config merge | §8.5 |
| Run state machine | §8.6 |
| Agent discovery | §8.7 |
| CLI commands | §8.8 |
| Output parsing | §8.9 |
| Quality/security pipeline | §8.10 |
| MCP coverage | §9 |
| Proxy agents | §9a |
| Future platforms | §9b |
| Sitback/TUI | §9c |
| Debugging/troubleshooting | §9d |
| SLO/performance | §9e |
| Model routing policies | §9f |
| Migration script steps | §9g |
| Detailed phase breakdown | [CODEX_DONUT_HARNESS_PLAN.md](./CODEX_DONUT_HARNESS_PLAN.md) |
| Schemas, MCP, configs | [MULTI_PLATFORM_DEEP_DIVE.md](../research/MULTI_PLATFORM_DEEP_DIVE.md) |
| Feature audit | [CLAUDE_CODE_FEATURE_PARITY_AUDIT.md](../research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md) |
