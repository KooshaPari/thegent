# Global Claude Code Instructions

These rules apply to ALL projects. Project-level CLAUDE.md files supplement (and may override) these.

---

# Dependency & Technology Preferences (ENFORCED)

**Bleeding-edge first**: Always prefer the newest stable versions of libraries, frameworks, and tools. When selecting dependencies:
- Use latest major versions, not LTS unless explicitly required
- Prefer cutting-edge CSS/JS/UI tools over mature but stagnant ones
- Check npm/crates.io/pkg.go.dev for latest versions before specifying deps
- Flag any dep that is >1 major version behind latest

**Wrap/Fork/Integrate over Hand-Roll**:
- Before writing any utility, search for an existing OSS library that does it
- Prefer wrapping a well-maintained OSS package over reimplementing
- Fork and extend rather than rewrite from scratch
- Document the wrapped library in comments: `// wraps: <lib-name> <version>`
- Source: dinoforge xDD governance protocols, Phenotype wrap-over-handroll mandate

**Rich UI mandate**:
- All UI work must use a rich component library (Radix, shadcn, Headless UI, etc.)
- No plain HTML forms without a design system
- Prefer: hover-to-expand, progressive disclosure, gallery views, tooltips
- Typography: monospace for technical/code UI elements, system sans for prose
- Dark mode first, light mode as secondary

---

# Prose & Documentation Quality

- Use vale + markdownlint for all documentation
- Embed Mermaid diagrams for architecture flows
- Embed React/MDX widgets in VitePress docsites where appropriate
- Optimize docs for agentic R/W AND human R (no human writes -- prompts only)
- Store raw user prompts alongside agent-generated specs

---

## Child-Agent and Delegation Policy

- Use child agents as the default for high-context, multi-file, or parallelizable work.
- Delegate exploration, audits, and long-running analysis to subagents before the parent agent edits.
- Keep parent-agent direct edits narrowly scoped to synthesis, integration, and finalization.

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

## Subagent Swarm (async orchestration)

- **Call task agents async.** Fire tasks so that as each completes, you are reawoken.
- **Run a swarm.** Up to **50 concurrent task agents**. Scale up when work is well decomposed.
- **Work in between.** While tasks run async, use your own context for planning or other work.

## Anti-Patterns

| Bad | Good |
|-----|------|
| Reading 10 files to "understand" | Delegate exploration, get summary |
| Editing files for multi-file changes | Delegate to `general-purpose` |
| Sequential explorations one-by-one | Batch parallel explores |
| Asking subagent for "all results" | Ask for "summary" or "key files" |
| Committing all dirty worktree changes in one commit | Split into targeted, provenance-based commits |

## Dirty-Tree Commit Discipline (Required)

In dirty worktrees, separate commits by provenance:
- `MODE 1`: user-requested implementation changes.
- `MODE 2`: pre-existing work and WIP from other actors.
- `MODE 3`: generated or temporary artifacts.

Never mix modes in one commit.

## Context Budget Rule

If task adds >2000 tokens of file content/output, **delegate it**.

---

# Optionality and Failure Behavior

- **Force requirement where it belongs.** Do not make dependencies "optional" just to avoid failure.
- **Fail clearly, not silently.** Use explicit failures -- not reduced functionality, logging-only warnings, or hidden errors.
- **Graceful in other ways.** Retries with visible feedback; actionable error messages.

---

# Planner Agents: No Code in Docs or Plans

**Planner agents** (PM, Analyst, Architect, etc.) must **never write code** in documentation and plans.

---

# Phased WBS and Plans with DAGs

When generating **plans**, **roadmaps**, or **implementation breakdowns**:
- **Phases:** Structure into ordered phases (Discovery, Design, Build, Test/Validate, Deploy/Handoff).
- **DAG:** Tasks have explicit **predecessors**; no cycles.
- **Output:** Phased WBS plus dependency list or DAG.

---

# Timescales: Agent-Led, Aggressive Estimates

**Assume an agent-driven environment.** No user or external human intervention beyond prompts.
- **Forbidden:** "Schedule external audit", "Stakeholder Presentation", "Human checkpoint".
- Use: "N tool calls", "N parallel subagents", "~M min wall clock".

---

# Documentation Organization

**CRITICAL**: All project documentation follows a strict organization structure.

### Root-Level Files (Keep in Root)
- `README.md`, `CHANGELOG.md`, `AGENTS.md`, `CLAUDE.md`, `00_START_HERE.md`
- Spec docs: `PRD.md`, `ADR.md`, `FUNCTIONAL_REQUIREMENTS.md`, `PLAN.md`, `USER_JOURNEYS.md`

### Documentation Structure

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

### AI Agent Instructions

- **NEVER** create `.md` files in the project root (except allowed root-level files above)
- **ALWAYS** place new documentation in the appropriate `docs/` subdirectory

---

# Opinionated Quality Enforcement

- Enforce opinionated styling to a strict degree.
- Use project linters, formatters, and type checkers. Never bypass them.
- **Zero new suppressions** without inline justification comment.
- Acceptable format: `# noqa: E501 -- line is a long URL`

---

# Specification Documentation System

## Required Project Documentation

| File | Purpose |
|------|---------|
| `PRD.md` | Product Requirements Document |
| `ADR.md` | Architecture Decision Records |
| `FUNCTIONAL_REQUIREMENTS.md` | Functional Requirements: SHALL statements |
| `PLAN.md` | Phased WBS with DAG dependencies |
| `USER_JOURNEYS.md` | User journeys with ASCII flow diagrams |

## VitePress Docsite Setup

**MUST include docsite setup in any new project initialization.**
- Copy template from `thegent/templates/vitepress-full/` to new project
- Run `pnpm install && pnpm docs:build` to verify

---

# Project Setup Checklist (Greenfield/Brownfield)

### 1. Docsite (VitePress)
- Copy `thegent/templates/vitepress-full/` to `docs/.vitepress/`

### 2. Taskfile (NOT Make)
- Create `Taskfile.yml` with: `lint`, `test`, `quality`, `docs:build`

### 3. Linters (Language-Specific)
| Stack | Linter | Formatter |
|-------|--------|-----------|
| Python | ruff | ruff format |
| TypeScript | oxlint | prettier |
| Go | golangci-lint | gofumpt |
| Rust | clippy | rustfmt |

### 4. Pre-commit Hooks
- Add `.pre-commit-config.yaml`
- Include: ruff-check, ruff-format, gitleaks, trailing-whitespace

### 5. Quality Gates
- Create `hooks/quality-gate.sh` with lint, test, coverage, security checks

---

# QA Governance

## Test-First Mandate

- Write tests BEFORE implementation.
- For bug fixes, write a failing test first.

## Test Pyramid Targets
- **Unit**: 70%
- **Integration**: 20%
- **E2E**: 10%

---

# Generalized Dev Environment Pattern

## Service Management
- Never start, stop, or restart the entire dev stack.
- Use per-service manipulation commands only.
- Assume services use hot reload.

## Package Manager (detect from lockfiles)
- `bun.lockb` or `bun.lock` -> use `bun`
- `pnpm-lock.yaml` -> use `pnpm`
- `yarn.lock` -> use `yarn`
- `package-lock.json` -> use `npm`

## Native Over Docker
Prefer native services over Docker for local development.

---

# GitHub Actions & CI Billing Policy

**CRITICAL**: The KooshaPari account has a persistent GitHub Actions spending-limit issue.
- **Skip Billed Runners**: Explicitly skip macOS, Windows, and non-standard large runners.
- **Bypass Rule**: If CI fails on billed runners due to spending limit, do NOT treat it as a blocking bug.
- **Merge Decision**: Proceed with merge if Linux runners pass and code is locally verified.
- Verify quality locally (build, lint, test) instead of relying on CI.

---

# Autonomous Operation (Critical)

## When to proceed without asking:
- Implementation details, library choices, code structure, test strategies, refactoring decisions

## Only ask when truly blocked by:
- Missing credentials/secrets
- External service access permissions
- Genuine product ambiguity not determinable from specs/code/tests
- Destructive operations (production data deletion, forced pushes)

**Default behavior: Research -> Decide -> Implement -> Validate -> Continue**

---

# Phenotype-Specific Governance

## Worktree Protocol
- Feature branches in `repos/worktrees/<project>/<category>/<branch>`
- Canonical repository tracks `main` only
- Return to `main` for merge/integration checkpoints

## Cross-Project Reuse Protocol
- Actively identify code that is sharable, modularizable, or decomposable for reuse.
- When reusable logic is found, prefer extraction into existing shared modules/projects first.
- For cross-repo moves, ask the user for confirmation on destination and rollout.

## Phenotype Git Delivery Protocol
- Use branch-based delivery with pull requests.
- Prefer stacked PRs for multi-part changes.
- Keep PRs linear and scoped: one concern per PR.
- Rebase or restack to keep branches current with target branch.

## Phenotype Long-Term Stability Protocol
- Optimize for long-term platform value over short-term convenience.
- Classify proposed changes as `quick_fix` or `stable_solution`; prefer `stable_solution`.
- Do not use deletions/reversions as the default strategy; prefer targeted edits.
- Do not merge any PR while any check is failing.
