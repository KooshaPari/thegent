# Global Claude Code Instructions

These rules apply to ALL projects. Project-level CLAUDE.md files supplement (and may override) these.

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

## Delegation Quick Reference

| Need | Delegate To | Example Prompt |
|------|-------------|----------------|
| Find code patterns | `Explore` | "Find all error handling patterns" |
| Design approach | `Plan` | "Design auth implementation strategy" |
| Run commands | `Bash` | "Run test suite and report failures" |
| Multi-step implementation | `general-purpose` | "Implement and test feature X" |
| Quick isolated fix | DO NOT delegate | Handle directly |

### Parallel vs Sequential

**Parallel** (no dependencies): Launch 2-3 explore agents simultaneously for independent searches.

**Sequential** (dependent): explore -> receive summary -> plan based on findings -> implement approved plan.

## Subagent Swarm (async orchestration)

**If you have subagent/swarm capabilities:** Use them as an **async swarm**.

- **Call task agents async.** Fire tasks so that as each completes, you are reawoken to re-evaluate, spawn more agents, or do more work yourself.
- **Run a swarm.** Up to **50 concurrent task agents**. Scale up when work is well decomposed and independent.
- **Work in between.** While tasks run async, use your own context for planning, monitoring, or other work.
- **Reawaken on completion.** When idle, you will be reawoken as each agent completes. Use that to spawn more agents, do follow-up work, or consolidate results.

## Anti-Patterns

| Bad | Good |
|-----|------|
| Reading 10 files to "understand" | Delegate exploration, get summary |
| Editing files for multi-file changes | Delegate to `general-purpose` |
| Sequential explorations one-by-one | Batch parallel explores |
| Asking subagent for "all results" | Ask for "summary" or "key files" |

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

- **Unit**: 70% (tolerance: +/-5%)
- **Integration**: 20% (tolerance: +/-5%)
- **E2E**: 10% (tolerance: +/-5%)
- Projects may override in `.qa-config.json` or `.claude/quality.json`.

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

| Test Type | New Project | Established | Critical System |
|-----------|-------------|-------------|-----------------|
| Unit | Required | Required | Required |
| Integration | Required | Required | Required |
| E2E | Optional | Required | Required |
| Property-based | Optional | Optional | Required |
| Contract | Optional | Required (if APIs) | Required |
| Mutation | Optional | Optional | Required |
| Security (SAST) | Required | Required | Required |
| Accessibility | Optional | Required (if UI) | Required |
| Performance | Optional | Optional | Required |
| Snapshot/Golden | Optional | Optional (if UI) | Required |

### Smart Contract Pattern (Spec Verification)
Specs (PRD/FR) -> Tests (must reference FR IDs) -> Checks (must be green) = Verified
- Every FR-XXX-NNN in FUNCTIONAL_REQUIREMENTS.md MUST have >=1 test referencing it
- Every test MUST reference >=1 FR-XXX-NNN (no orphan tests)
- All linters + type checkers + security scanners MUST pass (0 errors)
- Coverage MUST meet threshold (default 80%)
- If ALL checks green AND ALL FRs have tests -> spec is "programmatically verified"

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
Target: Level 3 for all projects, Level 4+ for critical systems.

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
- All new hooks must follow existing hook patterns in hooks/
- Provider pattern: use ProviderRegistry for extensible services
- MCP tools go through the standard FastMCP registration

---

## Domain-Specific Patterns

### What thegent Is

thegent is an **MCP server + agent hook system** for governing AI agent lifecycle and quality. The core domain is: define agents (personas with capabilities), dispatch hooks at lifecycle events (session start, tool use, stop), enforce governance policies (cost, quality, security), and expose MCP tools for agent management. It is fundamentally an **agent orchestration and governance platform**.

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
