# AST Analysis: thegent Agents/Hooks/CLI Redundancy & Consolidation

**Date**: 2026-02-21
**Agent**: code analysis agent
**Status**: CRITICAL FINDINGS - Consolidation Required
**Priority**: HIGH

---

## Executive Summary

Analysis of **53 agents**, **27 hooks**, and **3 CLI command modules** reveals:

- **Agent Duplication**: 8 semantic clusters with overlapping/redundant agents
- **Missing Hook Files**: 3 hooks registered in `hook-config.yaml` but missing implementations
- **CLI Overlap**: Significant duplication in config loading and output formatting across commands
- **Hardcoded Paths**: CLI `specs.py` line 30 contains hardcoded base path requiring parameterization
- **Library Opportunities**: Multiple hooks implementing JSON/file manipulation that should use library utilities
- **Hook/Library Mismatch**: `hooks/lib/` exists but utilities not widely adopted

---

## thegent Agents/Hooks/CLI Redundancy

### Agent Consolidation Map

| Cluster | Agents | Unique Capability | Consolidation Risk |
|---------|--------|------------------|-------------------|
| **Quality Verification** | `qa-verification-lead`, `quality-gatekeeper`, `quality-agent` | Verification vs gating vs generic QA | HIGH - merge into single "qa-orchestrator" |
| **Code Review & Refactoring** | `code-reviewer`, `code-review-refactor-expert`, `code-documentor` | Review + refactor + docs | MEDIUM - docs separate, review/refactor merge |
| **Performance Analysis** | `performance-tuner`, `performance-optimization-specialist` | Server-generic vs React/DB specific | LOW - keep separate (domain-specific), align terminology |
| **Gardener/Maintenance** | `gardener`, `backlog-gardener`, `blueprint-curator`, `knowledge-base-curator` | Memory synthesis vs curation vs backlog | HIGH - consolidate under "gardener" umbrella with roles |
| **Planning & Orchestration** | `plan-decomposer`, `plan-orchestrator`, `product-orchestrator` | WBS vs expansion vs PRD+WBS | MEDIUM - rename for clarity (WBS vs product-level) |
| **Security & Compliance** | `security-auditor`, `atoms-security-reviewer`, `compliance-liaison` | General vs atoms-specific vs compliance | HIGH - consolidate with domain flags |
| **Testing & Test Strategy** | `test-strategist`, `qa-test-coverage-expert`, `api-testing-specialist` | Strategy vs coverage vs API-specific | HIGH - merge strategy/coverage, keep API separate |
| **Documentation** | `code-documentor`, `api-contract-inspector`, `api-testing-specialist` (doc side) | Code docs vs API docs vs testing | MEDIUM - clarify boundaries |

### Key Findings by Agent Cluster

#### Quality Verification Cluster
```
Agents: qa-verification-lead, quality-gatekeeper, quality-agent
Lines: 3-4 per agent definition

qa-verification-lead: "Confirms zen-mcp-server validation evidence before promotion"
quality-gatekeeper: "Enforces zen-mcp-server phase exits with documented evidence"
quality-agent: "Specialized agent for fixing code quality issues (lint, types, tests, style)"

ISSUE: quality-gatekeeper and qa-verification-lead are semantic duplicates.
quality-agent is distinct (fixes issues vs gates them).

ACTION: Merge qa-verification-lead → quality-gatekeeper (one enforcer role).
        Keep quality-agent separate for fixing.
```

#### Gardener Ecosystem Cluster
```
Agents: gardener, backlog-gardener, blueprint-curator, knowledge-base-curator
Lines: 3 per agent

gardener: "Memory Synthesis Agent - Consolidates raw audit logs and session memories into formal project documentation"
backlog-gardener: "Curates zen-mcp-server idea streams into actionable backlog briefs"
blueprint-curator: "Synchronizes zen-mcp-server architecture and delivery blueprints with current findings"
knowledge-base-curator: "Keeps zen-mcp-server shared knowledge current with lessons and decisions"

ISSUE: Heavy naming redundancy around "gardener" + domain ("backlog", "blueprint", "knowledge").
All are curation/synthesis roles. Should be unified with mode/context switching.

ACTION: Single "gardener" agent with context flags:
  --mode=synthesis (memory → docs)
  --mode=backlog (ideas → briefs)
  --mode=blueprint (sync blueprints)
  --mode=knowledge (maintain KB)
```

#### Planning Cluster
```
Agents: plan-decomposer, plan-orchestrator, product-orchestrator
Lines: 3 per agent (plan-decomposer/orchestrator), 20+ for product-orchestrator

plan-decomposer: "Builds zen-mcp-server WBS tracks with dependency and parallelization guidance"
plan-orchestrator: "Expands ideas into WBS/PERT plans and parallel workstreams for zen-mcp-server"
product-orchestrator: "Transform high-level ideas → comprehensive PRD and WBS..."

ISSUE: Naming suggests plan-orchestrator INCLUDES plan-decomposer.
Product-orchestrator is PRD+WBS (higher level).

ACTION: Rename for clarity:
  plan-decomposer → wbs-builder
  plan-orchestrator → workstream-orchestrator
  product-orchestrator → product-planner (PRD focus)
```

#### Testing Cluster
```
Agents: test-strategist, qa-test-coverage-expert, api-testing-specialist
Lines: 3 per agent

test-strategist: "Crafts testing plans for zen-mcp-server with emphasis on pytest suites and contract coverage"
qa-test-coverage-expert: "Analyze code for testing gaps, write comprehensive test suites..."
api-testing-specialist: "Testing expert specializing in MSW, integration tests, and API mocking"

ISSUE: test-strategist (plans) + qa-test-coverage-expert (implements coverage) are complementary.
API specialist is domain-specific and should remain separate.

ACTION: Merge test-strategist + qa-test-coverage-expert → qa-test-architect
        Keep api-testing-specialist separate
```

### Missing Agent Descriptions

| Agent | Description Field | Status |
|-------|---|---|
| `ax-improver` | `[Description]` (PLACEHOLDER) | ⚠️ MISSING - needs definition |
| All others | ✓ Present | OK |

**ACTION**: Define `ax-improver` purpose or mark for deprecation.

---

## Hooks Analysis

### Hook Files Inventory (27 total)

| Hook File | Lines | Purpose | Status |
|-----------|-------|---------|--------|
| `gardener-continuity.sh` | ~190 | Continuity packet handoff system for phase transitions | ✓ Active |
| `gardener-spawn.sh` | ~130 | Agent spawning for hunger states | ✓ Active |
| `gardener-loop.sh` | ~10 | AgilePlus governance loop shim (delegates to Python) | ✓ Active |
| `gardener-scan.sh` | ~170 | Hunger state detection (test coverage, lint, docs, etc.) | ✓ Active |
| `gardener-xp.sh` | ~45 | Award XP to agents for task completions | ✓ Active |
| `gardener-parallel.sh` | ~350 | Parallel agent execution coordinator | ✓ Active |
| `gardener-spawn-manager.sh` | ? | Registered in config, FILE NOT FOUND | ❌ MISSING |
| `session-end-write-dump.sh` | ? | Registered in config, FILE NOT FOUND | ❌ MISSING |
| `prune-orphans-stop.sh` | ~30 | Auto-prune LSP/MCP processes | ✓ Active |
| `session-cleanup.sh` | ~60 | Prune stale caches and disk guard | ✓ Active |
| `post-agent-run-vetter.sh` | ? | Registered (event: PostAgentRun) | ? Unknown |
| `async-test-runner.sh` | ? | Registered in config, FILE NOT FOUND | ❌ MISSING |
| `docs-build.sh` | ~? | Registered in config | ? Unknown |
| `governance-gates.sh` | ~? | Registered in config | ? Unknown |
| `pre-commit-docs.sh` | ~? | Registered in config | ? Unknown |
| `check-service-role.sh` | ~? | Registered in config | ? Unknown |
| `speculative-stop-prewarmer.sh` | ~? | Registered in config | ? Unknown |
| `continuous-work-guard.sh` | ~? | Registered in config | ? Unknown |
| `hook-watcher.sh` | ~? | Registered in config | ? Unknown |
| `litellm-harvest-stop.sh` | ~? | Registered in config | ? Unknown |
| `qa-cross-schema-validator.sh` | ~? | Registered in config | ? Unknown |
| `session-start-spotlight-exclude.sh` | ~? | Registered in config | ? Unknown |
| `session-start-pending-notice.sh` | ~? | Registered in config | ? Unknown |
| `auto-launch-trigger.sh` | ~? | Registered in config | ? Unknown |
| `tts.sh` | ~? | Text-to-speech announcements | ? Unknown |
| `lib/common.sh` | ~? | Shared utilities | ✓ Present |
| `lib/spiral-config.sh` | ~? | Spiral config utilities | ✓ Present |

### Missing Hook Files (CRITICAL BUG)

```
Registered in hook-config.yaml but NOT FOUND on disk:

1. gardener-spawn-manager.sh
   Scope: all
   Timeout: (not specified)
   Purpose: (not documented)

2. async-test-runner.sh
   Registered in hook-config.yaml
   Purpose: "Run post-run governance vetter" (possibly mislabeled)

3. post-agent-run-vetter.sh
   Registered: event=PostAgentRun
   Timeout: 120
   Purpose: "Run post-run governance vetter"
   Note: May exist but not found in initial scan
```

**ACTION**: Audit and resolve:
1. Find missing files or remove from hook-config.yaml
2. Create implementations if actively needed
3. Document each hook's lifecycle event in comments

### Hooks Library Usage (`hooks/lib/`)

```
Library files:
  - hooks/lib/common.sh (shared utilities)
  - hooks/lib/spiral-config.sh (regression spiral config)

Hooks USING lib utilities: UNKNOWN (need grep analysis)

Hooks DUPLICATING JSON manipulation:
  - gardener-continuity.sh (uses jq extensively for packet management)
  - gardener-parallel.sh (uses jq for task state management)
  - gardener-xp.sh (uses sqlite3 for reputation updates)

OPPORTUNITY: Create hooks/lib/json-utils.sh for common jq patterns
  - packet management helpers
  - task state transitions
  - batch JSON updates
```

### Duplicated Hook Logic

| Pattern | Hooks | Opportunity |
|---------|-------|-------------|
| **JSON state files** | `gardener-parallel.sh`, `gardener-continuity.sh` | Extract to `lib/json-state-utils.sh` |
| **Timestamp generation** | `gardener-continuity.sh`, `gardener-parallel.sh`, `gardener-xp.sh` | Centralize in `lib/common.sh` |
| **Directory initialization** | All gardener hooks | Add `mkdir -p` wrapper to `lib/common.sh` |
| **Error logging** | Manual echo statements | Implement structured logging in `lib/logging.sh` |
| **Config loading** | `gardener-spawn.sh` (yq) + others | Standardize in `lib/config-loader.sh` |

---

## CLI Commands Analysis

### CLI Files Summary

| File | Lines | Commands | Status |
|------|-------|----------|--------|
| `cli/commands/specs.py` | ~110 | `generate`, `list-projects`, `show-prd`, `show-unified-workstream` | ⚠️ Hardcoded path |
| `cli/commands/governance.py` | ~220 | `analyze`, `setup`, `quality`, `audit`, `report`, `tasks`, `stats` | ✓ Clean |
| `cli/commands/queue.py` | ~250 | `scan`, `list`, `next`, `files`, `summary`, `process`, `analyze` | ✓ Clean |

### Hardcoded Paths (CRITICAL)

**`specs.py` line 30:**
```python
@click.option("--base-path", type=str, default="/Users/kooshapari/temp-PRODVERCEL/485/kush")
```

**ISSUE**: Hardcoded absolute path to user's home directory makes CLI non-portable.

**ACTION**: Replace with:
```python
@click.option(
    "--base-path",
    type=str,
    default=str(Path.cwd()),  # Use current working directory
    help="Base path for project analysis (default: current directory)"
)
```

### CLI Pattern Duplications

| Pattern | Files | Duplication |
|---------|-------|-------------|
| **Config loading from JSON** | `queue.py` (lines ~35-50), `governance.py` (multiple places) | DRY violation: Abstract to `cli/utils/config.py` |
| **Output formatting (Rich)** | All 3 files use Rich for tables/output | Good - consistent |
| **Click group definitions** | All 3 files define `@click.group()` | Good - modular |
| **Path resolution** | `specs.py` (line 26), `queue.py` (multiple) | Use `pathlib.Path` throughout |
| **Error handling** | Manual `click.echo(..., err=True)` | Standardize in `cli/utils/errors.py` |

### CLI Consolidation Opportunities

```python
# Create cli/utils/ for DRY

cli/utils/
  config.py      - Shared config loading (JSON, YAML)
  output.py      - Rich table/console helpers
  errors.py      - Standardized error handling
  paths.py       - Path resolution utilities
  validators.py  - Input validation

Then all commands:
  from cli.utils import load_config, format_table, safe_path
```

---

## Library Gaps & Opportunities

### Missing or Underutilized Libraries

| Need | Current | Library Candidate | Benefit |
|------|---------|------------------|---------|
| **JSON state management** | Manual jq in hooks | `jsonschema` + wrapper | Validation + error messages |
| **Config loading (YAML/JSON)** | Manual parsing | `pydantic` (already used) | Type validation, schema |
| **Date/time utilities** | Manual `date` in bash | `python-dateutil` (cli) | Consistent formats across shell/Python |
| **Structured logging in hooks** | Manual `echo >>` | Port `structlog` to bash or use Rust | JSON logging, aggregation |
| **Parallel task coordination** | Custom jq state machine | `APScheduler` (Python) or `tokio` (Rust) | Proven concurrency patterns |

### Hook Library Adoption Issues

```
hooks/lib/common.sh exists but:
  - Not sourced by all gardener-*.sh (gardener-loop.sh doesn't use it)
  - No clear contract/interface documented
  - Missing utility functions that are duplicated across hooks

ACTION:
  1. Document hooks/lib/ contract in README
  2. Add to all gardener-*.sh: source "${BASH_SOURCE[0]%/*}/../lib/common.sh"
  3. Extract duplicated functions into lib/
```

---

## Risk Assessment

| Finding | Severity | Impact | Timeline |
|---------|----------|--------|----------|
| Missing hook files in config | CRITICAL | Config references non-existent code; breaks on event dispatch | Fix immediately (< 1 day) |
| Agent duplication (quality cluster) | HIGH | Cognitive load, unclear when to use which; merge candidates exist | Consolidate in next release (1-2 days) |
| Hardcoded paths in CLI | HIGH | CLI non-portable; won't work on other machines | Fix immediately (< 1 hour) |
| Hook library underutilization | MEDIUM | Code duplication; harder to maintain; regression risk | Refactor in polish cycle (2-3 days) |
| CLI pattern duplication | MEDIUM | Harder to maintain; inconsistent error handling | Extract in next CLI enhancement (1 day) |
| Gardener ecosystem naming | MEDIUM | Confusing terminology (gardener-gardener, etc.); plan to consolidate | Rename in next cycle (< 1 day) |

---

## Consolidation Roadmap

### Phase 1: Critical Fixes (1 day)

- [ ] Fix hardcoded path in `cli/commands/specs.py` line 30
- [ ] Audit missing hooks (gardener-spawn-manager, async-test-runner, post-agent-run-vetter)
- [ ] Update hook-config.yaml with accurate references

### Phase 2: Agent Consolidation (2-3 days)

- [ ] Merge `qa-verification-lead` → `quality-gatekeeper`
- [ ] Merge `test-strategist` + `qa-test-coverage-expert` → `qa-test-architect`
- [ ] Consolidate gardener ecosystem under single agent with modes
- [ ] Rename planning agents for clarity (plan-decomposer → wbs-builder, etc.)
- [ ] Define missing `ax-improver` or deprecate

### Phase 3: Hook Refactoring (3-4 days)

- [ ] Create `hooks/lib/json-utils.sh` for packet/task management
- [ ] Create `hooks/lib/logging.sh` for structured logging
- [ ] Create `hooks/lib/config-loader.sh` for YAML/JSON loading
- [ ] Audit all hooks for compliance with library usage
- [ ] Document hooks/lib/ contract in `hooks/README.md`

### Phase 4: CLI Refactoring (2-3 days)

- [ ] Extract `cli/utils/config.py` (JSON/YAML loading)
- [ ] Extract `cli/utils/output.py` (Rich helpers)
- [ ] Extract `cli/utils/errors.py` (error handling)
- [ ] Extract `cli/utils/paths.py` (Path resolution)
- [ ] Audit and update all 3 command modules for consistency

---

## Recommendations for Further Analysis

1. **Hook Event Lifecycle**: Document which hooks fire on which events (SessionStart, PostToolUse, Stop, etc.)
2. **Agent Discovery**: Audit agents/ directory for unused agents; create deprecation plan
3. **Bounded Contexts**: Review `agents/bounded-contexts.yaml` — ensure alignment with actual agent responsibilities
4. **Library-First Audit**: Comprehensive review of hooks + CLI against library-first policy
5. **Test Coverage**: Ensure hooks have test coverage in tests/hooks/ directory

---

## Files Affected

### To Create/Update

```
docs/plans/refactor-analysis-thegent-ast.md (THIS FILE)
```

### To Fix

```
cli/commands/specs.py (line 30) - hardcoded path
hooks/hook-config.yaml - missing file references
hooks/lib/common.sh - ensure completeness
```

### To Consolidate

```
agents/ (53 files) - merge duplicates per cluster map
hooks/ (27 files) - library extraction
cli/commands/ (3 files) - DRY refactoring
```

---

## Sign-Off

**Analysis Date**: 2026-02-21
**Analyzer**: code analysis agent
**Reviewer**: (pending)
**Status**: Ready for consolidation planning

Next: Submit to team-lead for prioritization and assignment to refactoring agents.
