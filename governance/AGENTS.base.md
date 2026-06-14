# AGENTS.md — Base Template for Phenotype Ecosystem

This is the canonical base template for `AGENTS.md` files across the Phenotype ecosystem. Each project should include relevant sections and customize as needed.

## Table of Contents

1. [Project Identity & Work Management](#1-project-identity--work-management)
2. [Core Agent Expectations](#2-core-agent-expectations)
3. [Repository Mental Model](#3-repository-mental-model)
4. [Standard Operating Loop (SWE Autopilot)](#4-standard-operating-loop-swe-autopilot)
5. [File Size & Modularity Mandate](#5-file-size--modularity-mandate)
6. [Research-First Development](#6-research-first-development)
7. [Test-First Mandate](#7-test-first-mandate)
8. [Branch Discipline](#8-branch-discipline)
9. [Child-Agent and Delegation Policy](#9-child-agent-and-delegation-policy)
10. [Tool Usage & CLI Priority](#10-tool-usage--cli-priority)
11. [Naming Conventions](#11-naming-conventions)
12. [Session Documentation](#12-session-documentation)
13. [Quality Standards](#13-quality-standards)

---

## 1. Project Identity & Work Management

### [CUSTOMIZE] Project Overview

Update with your project name, description, and purpose:

```
- **Name**: [PROJECT_NAME]
- **Description**: [One-line description]
- **Location**: [Path in repos shelf]
- **Language Stack**: [Rust | Python | TypeScript | Go | ...]
- **Published**: [Yes | No | Internal]
```

### [OPTIONAL] AgilePlus Integration

**If this project uses AgilePlus for work tracking:**

```
All work MUST be tracked in AgilePlus:
- Reference: /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
- CLI: cd AgilePlus && agileplus <command>
- Specs: AgilePlus/specs/<feature-id>/ or the repo-local agileplus/<feature-id>/
- Worklog: AgilePlus/.work-audit/worklog.md

Requirements:
1. Check for AgilePlus spec before implementing
2. Create spec for new work: agileplus specify --title "<feature>"
3. Update work package status as work progresses
4. No code without corresponding AgilePlus spec
```

### [OPTIONAL] UTF-8 Encoding

All markdown files must use UTF-8 and avoid smart quotes/em-dashes:

```bash
# Validate encoding
agileplus validate-encoding --all --fix
```

---

## 2. Core Agent Expectations

### Autonomous Operation (Critical — Minimal Human Intervention)

Agents MUST operate with **maximum autonomy**:

**When to proceed without asking:**
- Implementation details and technical approach decisions
- Library/framework choices aligned with existing patterns
- Code structure and organization
- Test strategies and coverage approaches
- Refactoring and optimization decisions
- Bug fixes and performance improvements
- Documentation updates
- Decomposition of large files
- Consolidation of duplicate code
- Removing dead code and legacy patterns

**Only ask when truly blocked by:**
- Missing credentials/secrets (cannot be inferred from environment)
- External service access permissions
- Genuine product ambiguity (behavior not determinable from specs/code)
- Destructive operations (production data deletion, forced pushes)

**Default behavior: Research → Decide → Implement → Validate → Continue**

### Child-Agent Lifecycle (Required)

- Any spawned child agent must be explicitly closed at end of turn
- Keep parent-agent work focused on validation, synthesis, final merges
- Use subagents for high-context, parallel, or exploratory work

---

## 3. Repository Mental Model

Before editing, understand these first-class constraints:

### [CUSTOMIZE] Project Structure

Document your project's key modules and directory layout:

```
src/<package>/
  main.py              # Application entrypoint
  app.py               # ASGI/web entrypoint
  server.py            # Core server wiring
  api/                 # Routes/endpoints
    routes/            # Handler by domain
  services/            # Business logic layer
  infrastructure/      # External adapters
  models/              # Data models
  utils/               # Shared utilities
  cli/                 # CLI commands (Typer)
tests/
  unit/                # Unit tests
  integration/         # Integration tests
  e2e/                 # End-to-end tests
docs/
  sessions/            # Session-based work docs
  architecture/        # Architecture documentation
```

### [CUSTOMIZE] Style Constraints

- **Line length**: 100 characters (or project standard)
- **Formatter**: [Ruff | Black | rustfmt | gofmt | ...]
- **Type checker**: [mypy | pyright | clippy | ...]
- **Linter**: [Ruff | clippy | golangci-lint | ...]
- **File size target**: ≤350 lines, hard limit ≤500 lines
- **Typing**: Explicit typing where practical
- **Logging**: Structured, informative logging

### Key Constraints

- Reuse existing layers instead of bypassing them
- Keep changes minimal, composable, and test-driven
- Proactively decompose files approaching size limits
- Never introduce real secrets; use env vars and placeholders
- Match existing coding style and naming conventions

---

## 4. Standard Operating Loop (SWE Autopilot)

For every task (bug, feature, infra, test):

### 1. Review
- Read the issue/error, relevant code, and existing tests
- Use search tools to map usages before editing
- Check line counts on affected files; note decomposition needs
- Identify all callers and dependencies

### 2. Research
- Check related modules and patterns in-repo
- When external APIs/libraries are involved, consult official docs via web search
- Reference this contract for architectural constraints
- Document findings in session folder

### 3. Plan
- Formulate a short, concrete plan aligned with existing abstractions
- If any file will exceed size limits, include decomposition in the plan
- Identify test coverage requirements
- Design for backwards-incompatible changes (no shims; full migration)

### 4. Execute
- Implement in small, verifiable increments
- Match coding style, respect typing and logging conventions
- Decompose proactively; don't wait until a file hits size limits
- Update all callers simultaneously (no partial migrations)

### 5. Size-Check
- If any edited file nears size limits, plan decomposition
- Identify ALL callers/dependencies before changes—no partial updates
- Verify interfaces remain narrow and clear

### 6. Test
- Run targeted tests relevant to the change
- Start with focused suites; widen scope if risk is broader
- Verify decomposed modules have equivalent test coverage
- New tests must reference FR IDs where applicable

### 7. Review & Polish
- Re-read diffs; simplify and remove dead code
- Verify all files stay within size limits
- Ensure no backwards compatibility shims remain
- Check for "AI slop" (placeholder TODOs, lorem ipsum, generic comments)

### 8. Repeat
- If tests or behavior fail, loop without waiting for user direction
- Continue until clean; pause only when blocked

---

## 5. File Size & Modularity Mandate

**Hard constraint: All modules ≤500 lines (target ≤350)**

### Before Adding Features

```bash
# Check line count
wc -l src/<package>/module.py

# If approaching 350+ lines, decompose immediately

# Find all files exceeding limit
find src/ -name "*.py" -exec wc -l {} + | awk '$1 > 350'
```

### Decomposition Patterns

**Pattern 1: Service Submodule**
```
# Before: services/factory.py (400+ lines)
# After:
services/factory/
  __init__.py        (exports public API)
  core.py            (creation logic)
  cache.py           (caching layer)
  validators.py      (input validation)
  types.py           (shared types)
```

**Pattern 2: Adapter Extraction**
```
# Before: infrastructure/adapters.py (500+ lines)
# After:
infrastructure/
  db_adapter.py      (database operations)
  auth_adapter.py    (auth integration)
  cache_adapter.py   (caching layer)
  storage_adapter.py (file storage)
```

**Pattern 3: Route Splitting**
```
# Before: api/routes/users.py (500+ lines)
# After:
api/routes/users/
  __init__.py        (router registration)
  handlers.py        (route handlers)
  validators.py      (request validation)
```

**Pattern 4: Database Models**
```
# Before: db/models.py (600+ lines)
# After:
db/models/
  __init__.py      (exports all models)
  user.py          (user models)
  config.py        (config models)
```

---

## 6. Research-First Development

Before implementing ANY feature or fix, agents MUST conduct comprehensive research:

### Codebase Research (Always Required)

```bash
# Find similar implementations
rg "pattern_name" --type py -A 5 -B 5

# Trace call chains
rg "function_name\(" --type py

# Find test patterns
rg "def test_.*pattern" tests/ -A 10

# Check architecture patterns
rg "class.*Adapter\|class.*Factory\|class.*Service" --type py

# Find all usages of a module
rg "from.*module_name import" --type py
```

### Web Research (When Needed)

- Library documentation and examples
- Best practices for performance/security patterns
- Framework-specific patterns
- Cloud service integration patterns

### Research Documentation

- Document findings in `docs/sessions/<session-id>/01_RESEARCH.md`
- Include URLs, code examples, and decision rationale
- Update continuously as new information discovered
- Reference findings in implementation decisions

---

## 7. Test-First Mandate

### TDD Requirements

- **For NEW modules**: test file MUST exist before implementation file
- **For BUG FIXES**: failing test MUST be written before the fix
- **For REFACTORS**: existing tests must pass before AND after

### Test Naming & Organization

- **Unit tests**: `test_<module>_<function>.py`
- **Integration tests**: `test_<domain>_integration.py`
- **E2E tests**: `test_<flow>_e2e.py`
- **FR Traceability**: All tests MUST reference an FR ID via:
  - Tag: `# @trace FR-XXX-NNN` in test file/function
  - Marker: `@pytest.mark.requirement("FR-XXX-NNN")`
  - Docstring: `Traces to: FR-XXX-NNN`
  - Test name: `test_FR_XXX_NNN_...`

### Test Coverage Targets

| Type | Target | Tolerance |
|------|--------|-----------|
| Unit | 70% | ±5% |
| Integration | 20% | ±5% |
| E2E | 10% | ±5% |

---

## 8. Branch Discipline

**Feature branches in worktrees; canonical repo on main only**

- **Feature branches**: Use `repos/worktrees/<project>/<category>/<branch>` or `<project>-wtrees/<topic>/`
- **Canonical repository**: Always tracks `main` only
- **Return to main**: After merge/integration checkpoints
- **Branch naming**: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/` prefixes
- **PR workflow**: Create PRs on feature branches; merge via `gh pr merge`
- **Avoid `git reset --hard`**: Use `git pull --rebase origin main` to align safely

---

## 9. Child-Agent and Delegation Policy

**Use child agents liberally for high-context, multi-file, or parallelizable work.**

- Delegate exploration, audits, multi-repo scans, and implementation planning to subagents
- Keep parent-agent changes focused on validation, synthesis, and finalization
- Reserve parent-agent direct writes for the narrowest, final decision layer

**Parallel vs Sequential:**
- **Parallel** (no dependencies): Launch 2-3 subagents simultaneously
- **Sequential** (dependent): explore → receive summary → plan based on findings → implement

---

## 10. Tool Usage & CLI Priority

### CLI is REQUIRED — Primary Interface

**Always use the project CLI for operations instead of direct tool invocation.**

```bash
# Environment setup (always first)
source .venv/bin/activate    # Python projects
uv run <command>             # Or use uv directly

# ✅ REQUIRED: Use project CLI for all operations
task test                    # Run tests
task lint                    # Check code quality
task format                  # Auto-format code
task quality                 # Full quality checks

# ❌ AVOID: Direct tool invocation (only for debugging CLI itself)
pytest ...                   # Use: task test
ruff check ...               # Use: task lint
```

### Read-Only Tools First

Before using write/edit tools:
1. Use `Read` tool to understand current state
2. Use `Grep`/`Glob` to locate code patterns
3. Use shell (read-only commands) to verify state
4. Then use `Edit`/`Write` with full context

---

## 11. Naming Conventions

### Session/Conversation Naming

Format: `<project>:<brief-task-description>`

- Good: `thegent:auth-refactor`, `phenotype-infrakit:duplication-audit`
- Bad: `fix`, `implementation`, `agent work`

### File Naming in Sessions

Format: `<project>-<YYYYMMDD>-<task>-<version>.md`

- Good: `thegent-20260329-governance-consolidation-v1.md`
- Location: `docs/sessions/` or `worktrees/<project>/sessions/`

### Branch Naming

Format: `<type>/<description>`

- Good: `feat/token-refresh`, `chore/update-deps`, `fix/auth-bug`
- Bad: `feature-branch`, `fix`, `work`

---

## 12. Session Documentation

**All agents MUST maintain session documentation for research, decisions, and findings.**

### Location

- Default: `docs/sessions/<session-id>/`
- Worktrees: `worktrees/<project>/sessions/<session-id>/`

### Standard Session Structure

```
docs/sessions/<session-id>/
├── README.md           # Overview and context
├── 01_RESEARCH.md      # Findings and analysis
├── 02_PLAN.md          # Design and approach
├── 03_IMPLEMENTATION.md # Code changes and rationale
├── 04_VALIDATION.md    # Tests and verification
└── 05_KNOWN_ISSUES.md  # Blockers and follow-ups
```

### When to Document

- Research completions and findings
- Decisions made with rationale
- Issues found (duplication, performance, bugs)
- Work completions and status
- Planning for fork candidates or migration paths

---

## 13. Quality Standards

### Code Quality Mandate

- **All linters must pass** — zero errors, no suppressions without inline justification
- **Type checking must pass** — explicit types, no `Any` without reason
- **All tests must pass** — unit, integration, E2E where applicable
- **No AI slop** — avoid placeholder TODOs, lorem ipsum, generic comments
- **Backwards incompatibility**: No shims, full migrations, clean breaks

### Suppression Policy

- **Zero new suppressions** without inline justification comment
- Format: `# noqa: E501 -- line is a long URL` (note the `--` reason separator)
- Acceptable reasons: external format (JSON, YAML), vendor code, verified pre-existing
- Unacceptable reasons: non-blocking, will-fix-later, not-our-code

### PR Standards

See `governance/standards/pr-standards.md` for detailed PR requirements.

### Commit Message Format

See `governance/standards/commit-conventions.md` for commit message standards.

### Code Style Standards

See `governance/standards/code-style.md` for language-specific style guidelines.

### Testing Standards

See `governance/standards/testing-standards.md` for testing requirements and patterns.

---

## Additional Resources

- **CLAUDE.md** — Project-specific instructions and customizations
- **governance/standards/** — Detailed standards for commits, PRs, code style, testing
- **governance/templates/** — Document templates (PRD, ADR, PLAN, etc.)
- **docs/reference/** — Architecture, API references, and quick guides

---

## Version History

- **2026-03-29** — Initial version, consolidated from 36+ AGENTS.md copies across Phenotype
