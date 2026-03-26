# Functional Requirements — thegent (HAX)

**Version:** 1.0
**Status:** Draft
**Date:** 2026-03-25
**Traces to:** PRD.md — Harmonious Agent Experience (HAX)

---

## Categories

| Code | Domain |
|------|--------|
| DOT | Dotfiles and environment configuration management |
| SYS | System setup and reproducible environment bootstrap |
| PKG | Package management and dependency orchestration |
| TPL | Templates and scaffolding |
| SYNC | Sync, backup, and cross-machine state |

---

## FR-DOT-001: Unified Rules Sync

**Priority**: SHALL
**Description**: The `thegent rules sync` command SHALL propagate the canonical rules/hooks set to all configured agent environments (Claude Code hooks, Cursor rules, Codex config) in a single operation.
**Acceptance Criteria**:
- [ ] Command reads source rules from a canonical location in the thegent repo
- [ ] All supported targets updated without manual file editing
- [ ] Sync reports each target as updated, skipped, or failed with reason
**Traces to**: 2.3
**Status**: Planned

---

## FR-DOT-002: Cross-Platform Directive Syntax

**Priority**: SHALL
**Description**: The `$defer`, `$block`, and `$idea` directive syntax SHALL be parsed and honored identically across Claude Code, Cursor, and Codex environments.
**Acceptance Criteria**:
- [ ] Parser handles all three directive types in all target environments
- [ ] Directive semantics are documented in a single specification file
- [ ] Integration tests verify identical behavior across at least two platforms
**Traces to**: 2.3
**Status**: Partial

---

## FR-DOT-003: Governance Template Distribution

**Priority**: SHALL
**Description**: thegent SHALL maintain canonical CLAUDE.md and AGENTS.md governance templates that are the authoritative source for rules injected into all downstream projects.
**Acceptance Criteria**:
- [ ] Templates stored under `templates/governance/` with versioned headers
- [ ] `thegent templates apply` copies templates to target project with merge-aware diff
- [ ] Downstream projects reference template version to detect drift
**Traces to**: 2.3
**Status**: Partial

---

## FR-DOT-004: Hook Pipeline Template Installation

**Priority**: SHALL
**Description**: thegent SHALL provide all Claude Code hook pipeline scripts as versioned, installable templates deployable to any project.
**Acceptance Criteria**:
- [ ] All hooks from the global Hook Pipeline Summary available as templates
- [ ] `thegent hooks install` deploys selected hooks to `.claude/hooks/` in the target project
- [ ] Hook version tracked; `thegent hooks status` reports installed vs. available versions
**Traces to**: 2.3
**Status**: Planned

---

## FR-DOT-005: Pre-commit Config Templates per Stack

**Priority**: SHOULD
**Description**: thegent SHOULD provide `.pre-commit-config.yaml` templates per language stack enforcing ruff, gitleaks, and trailing-whitespace at minimum.
**Acceptance Criteria**:
- [ ] Templates available for Python, TypeScript, Go, and Rust stacks
- [ ] `thegent precommit install --stack python` writes config and runs `pre-commit install`
- [ ] Template version recorded in project `.thegent/meta.json`
**Traces to**: 2.3
**Status**: Planned

---

## FR-SYS-001: Reproducible System Bootstrap

**Priority**: SHALL
**Description**: thegent SHALL provide a single bootstrap command that installs all required tools, dotfiles, and configurations on a fresh macOS, Linux, or WSL system without manual intervention.
**Acceptance Criteria**:
- [ ] `thegent setup` completes without prompting on a clean system
- [ ] All required CLI tools (mise, bun, uv, gh, process-compose, etc.) installed to pinned versions
- [ ] Idempotent: re-running on an already-configured system makes no destructive changes
**Traces to**: 2.3
**Status**: Planned

---

## FR-SYS-002: Mise Toolchain Version Pinning

**Priority**: SHALL
**Description**: All tool versions used by thegent-managed projects SHALL be pinned via `.mise.toml` and installed through `mise` for consistent cross-machine environments.
**Acceptance Criteria**:
- [ ] Root `.mise.toml` present with pinned versions for all primary tools
- [ ] `thegent sys verify` checks that installed tool versions match `.mise.toml`
- [ ] Version drift reported per tool with remediation command
**Traces to**: 2.3
**Status**: Partial

---

## FR-SYS-003: Platform Detection and Conditional Setup

**Priority**: SHALL
**Description**: The setup system SHALL detect the host platform (macOS, Linux, WSL) and apply platform-specific steps conditionally without user intervention.
**Acceptance Criteria**:
- [ ] Platform detected from `uname -s` and `$WSL_DISTRO_NAME`
- [ ] macOS-specific steps (Homebrew, Keychain) skip on Linux/WSL
- [ ] All conditional branches tested in CI via matrix strategy
**Traces to**: 2.3
**Status**: Planned

---

## FR-SYS-004: Post-Install Verification Suite

**Priority**: SHALL
**Description**: After bootstrap, thegent SHALL run a verification suite that confirms all installed tools are reachable at the expected version.
**Acceptance Criteria**:
- [ ] Verification checks each tool from the required tool list
- [ ] Exit code non-zero if any tool fails version check
- [ ] Human-readable report lists pass/fail per tool with actual vs. expected version
**Traces to**: 2.3
**Status**: Planned

---

## FR-PKG-001: Unified Prompt Queue

**Priority**: SHALL
**Description**: thegent SHALL implement a project-aware prompt queue stored in `.thegent/prompt_queue.jsonl` that serializes agent task submissions across sessions.
**Acceptance Criteria**:
- [ ] Queue entries written atomically (no partial writes)
- [ ] `thegent queue tui` displays pending, running, and completed entries
- [ ] `thegent run $defer` dequeues the next pending entry and dispatches it
**Traces to**: 3.1
**Status**: Partial

---

## FR-PKG-002: Queue Operation Latency

**Priority**: SHALL
**Description**: Enqueue and dequeue operations on the prompt queue SHALL complete in under 10 ms on local storage.
**Acceptance Criteria**:
- [ ] P99 enqueue latency < 10 ms measured by benchmark harness
- [ ] P99 dequeue latency < 10 ms measured by benchmark harness
- [ ] Benchmark runs in CI; regression blocks merge
**Traces to**: 4 (Success Metrics)
**Status**: Planned

---

## FR-PKG-003: Multi-Tenant Process Consolidation

**Priority**: SHALL
**Description**: thegent SHALL consolidate redundant MCP servers and LSP instances into persistent daemon processes, keeping total process count below 10 per active multi-agent session.
**Acceptance Criteria**:
- [ ] `thegent daemon status` reports all managed persistent processes
- [ ] Starting a second agent session reuses existing daemons rather than spawning new ones
- [ ] Integration test verifies process count <= 10 after spawning 3 concurrent agent sessions
**Traces to**: 3.3
**Status**: Planned

---

## FR-PKG-004: Intelligent Multi-Provider Routing

**Priority**: SHALL
**Description**: thegent SHALL integrate LiteLLM to route agent tasks to the optimal provider based on cost, quality, and speed with automated failover.
**Acceptance Criteria**:
- [ ] Routing resolution completes in under 100 ms
- [ ] Pareto-frontier selection configurable via routing policy file
- [ ] Failover triggered automatically when a provider returns 5xx or is rate-limited
**Traces to**: 2.2
**Status**: Planned

---

## FR-PKG-005: Universal Memory Backend

**Priority**: SHALL
**Description**: thegent SHALL integrate a graph memory backend (Supermemory.ai or equivalent) to persist agent knowledge across sessions and projects.
**Acceptance Criteria**:
- [ ] Memory writes survive process restart and are readable in a new session
- [ ] Cross-project knowledge queries return results from all registered projects
- [ ] `thegent memory search "<query>"` returns relevant items with source citations
**Traces to**: 2.1
**Status**: Planned

---

## FR-TPL-001: VitePress Docsite Template

**Priority**: SHALL
**Description**: thegent SHALL maintain a VitePress docsite template under `templates/vitepress-full/` that produces a locally-openable static docs site for any project.
**Acceptance Criteria**:
- [ ] Template includes `config.ts`, `package.json`, and index page stubs
- [ ] `pnpm install && pnpm docs:build` succeeds after template application with only placeholder edits
- [ ] Generated `docs-dist/index.html` opens in browser via `file://`
**Traces to**: 2.3
**Status**: Partial

---

## FR-TPL-002: Language Quality Config Templates

**Priority**: SHALL
**Description**: thegent SHALL provide per-language quality config templates (ruff, oxlint, golangci, clippy, shellcheck) enforcing the project's opinionated defaults.
**Acceptance Criteria**:
- [ ] Templates available for all stacks listed in the global CLAUDE.md Project Setup Checklist
- [ ] `thegent templates quality --stack <stack>` writes config to target project root
- [ ] Template versions tracked; drift detection available via `thegent templates diff`
**Traces to**: 2.3
**Status**: Planned

---

## FR-TPL-003: Taskfile Standard Tasks Template

**Priority**: SHALL
**Description**: thegent SHALL provide a Taskfile.yml template with standard `lint`, `test`, `quality`, and `docs:build` tasks for each supported language stack.
**Acceptance Criteria**:
- [ ] Template applied via `thegent templates taskfile --stack <stack>`
- [ ] All four standard tasks present and runnable after template application
- [ ] Taskfile includes tasks from thegent shared includes where available
**Traces to**: 2.3
**Status**: Planned

---

## FR-TPL-004: Gardener Memory Synthesis

**Priority**: SHOULD
**Description**: thegent SHOULD provide a Gardener agent command that synthesizes session audit logs and history into updated CLAUDE.md, ADR.md, and PRD.md documentation automatically.
**Acceptance Criteria**:
- [ ] `thegent memory garden` processes audit logs and produces documentation patches
- [ ] Patches applied with diff preview before commit
- [ ] Gardener output passes prose quality lint (vale + markdownlint)
**Traces to**: 3.2
**Status**: Planned

---

## FR-SYNC-001: Cross-Machine State Synchronization

**Priority**: SHALL
**Description**: thegent SHALL support syncing dotfiles and configuration state across machines via a git-backed remote, allowing any configured machine to restore full state.
**Acceptance Criteria**:
- [ ] `thegent sync push` commits and pushes local state to the configured remote
- [ ] `thegent sync pull` fetches and applies remote state without overwriting local uncommitted changes
- [ ] Conflicts reported with per-file resolution prompts; no silent overwrites
**Traces to**: 2.3
**Status**: Planned

---

## FR-SYNC-002: Selective Sync Exclusion

**Priority**: SHALL
**Description**: Users SHALL be able to configure which files and directories are excluded from sync via a `.thegentsyncignore` file using gitignore pattern syntax.
**Acceptance Criteria**:
- [ ] `.thegentsyncignore` follows `.gitignore` pattern syntax
- [ ] Secrets directory excluded by default; explicit opt-in required to include
- [ ] `thegent sync status` shows what would be pushed/pulled before execution
**Traces to**: 2.3
**Status**: Planned

---

## FR-SYNC-003: Multi-Agent Team Protocol

**Priority**: SHOULD
**Description**: thegent SHOULD provide cross-platform coordination primitives (Voting, Broadcast, Task Sync) for multi-agent swarms operating across different agent platforms.
**Acceptance Criteria**:
- [ ] Broadcast sends a message to all active agent instances in the current session
- [ ] Voting aggregates responses from N agents and returns the majority result
- [ ] Task Sync ensures a task is claimed by exactly one agent (no duplicate execution)
**Traces to**: 3.4
**Status**: Planned

---

## FR-SYNC-004: Atomic File Operations

**Priority**: SHALL
**Description**: All file writes performed by thegent SHALL use atomic operations (write-to-temp then rename) to prevent partial writes from corrupting state files.
**Acceptance Criteria**:
- [ ] All writes to `.thegent/` directory use temp-file-then-rename pattern
- [ ] Interrupted writes leave the original file intact
- [ ] Atomic write utility is a shared primitive used by all subsystems
**Traces to**: 5 (US-E3)
**Status**: Planned

---

## FR-SYNC-005: Git Command Timeout Enforcement

**Priority**: SHALL
**Description**: All git commands executed by thegent SHALL have explicit timeouts to prevent agent hangs on slow or unavailable remotes.
**Acceptance Criteria**:
- [ ] Default timeout: 30 seconds per git operation (configurable)
- [ ] Timeout triggers a clear error message naming the command and elapsed time
- [ ] Timeout value configurable per operation type in `.thegent/config.toml`
**Traces to**: 5 (US-E2)
**Status**: Planned
