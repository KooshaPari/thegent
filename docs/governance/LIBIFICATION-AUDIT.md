# Libification Audit - Phenotype Ecosystem

**Date:** 2026-03-26
**Status:** Draft
**Owner:** Ecosystem Architecture Team

## Executive Summary

This audit identifies code patterns across the Phenotype ecosystem that are candidates for extraction into versioned shared libraries (`libs/`). The goal is to reduce duplication, improve maintainability, and establish a plugin-based architecture following hexagonal principles.

---

## Priority Candidates for Libification

### Tier 1: High Priority (Extract Immediately)

#### 1. Hexagonal Architecture Ports/Adapters Skeleton

| Attribute | Value |
|-----------|-------|
| **Current Locations** | `hexagon-rs/src/ports/`, `hexagon-ts/src/adapters/`, `hexagon-python/ports/`, `hexagon-go/`, `hexagon-java/` |
| **Suggested Library** | `libs/hexagonal-core` (multi-language) |
| **Rationale** | Core ports interfaces are ~80% identical across all implementations |
| **Versioning** | SemVer 1.0.0 with breaking changes policy |
| **Plugin vs Lib** | Library (stable interfaces, no runtime loading needed) |

**Candidate Extraction:**
```typescript
// Shared port interfaces (TypeScript)
interface InputPort<T> { handle(request: T): Promise<Result> }
interface OutputPort<T> { send(data: T): Promise<void> }
interface UseCase<TInput, TOutput> { execute(input: TInput): Promise<TOutput> }
```

#### 2. CLI Argument Parsing Patterns

| Attribute | Value |
|-----------|-------|
| **Current Locations** | `helios-cli/`, `phenotype-cli-core/`, `phenotype-cli-extensions/` |
| **Suggested Library** | `libs/cli-framework` |
| **Rationale** | Command registration, flag parsing, and help generation are duplicated |
| **Plugin vs Lib** | Library with optional plugin extensions |

#### 3. Configuration Management

| Attribute | Value |
|-----------|-------|
| **Current Locations** | `phenotype-config-ts/`, `phenotype-config/`, `helMo/` |
| **Suggested Library** | `libs/config-core` |
| **Rationale** | Environment loading, validation, and merging logic is duplicated |
| **Plugin vs Lib** | Library |

---

### Tier 2: Medium Priority (Next Quarter)

#### 4. Task Engine / Command Queue

| Attribute | Value |
|-----------|-------|
| **Current Locations** | `phenotype-task-engine/`, `phench/` |
| **Suggested Library** | `libs/task-queue` |
| **Rationale** | Async task scheduling, retry logic, and result handling duplicated |
| **Plugin vs Lib** | Library with async/await patterns |

#### 5. Logging/Tracing Abstraction

| Attribute | Value |
|-----------|-------|
| **Current Locations** | `phenotype-logger/`, `phenotype-tracing/`, `phenotype-logging-zig/` |
| **Suggested Library** | `libs/observability-core` |
| **Rationale** | Structured logging, span propagation, and metric collection patterns are similar |
| **Plugin vs Lib** | Library with adapter backends |

#### 6. Agent Preflight Checks

| Attribute | Value |
|-----------|-------|
| **Current Locations** | `phenotype-skills-clone/skills/agent_preflight*`, `phenotype-research-engine/` |
| **Suggested Library** | `libs/agent-preflight` |
| **Rationale** | Pre-execution validation, environment checks, and capability detection duplicated |
| **Plugin vs Lib** | Library |

---

### Tier 3: Low Priority (Future Consideration)

#### 7. Plugin Loading / Extension System

| Attribute | Value |
|-----------|-------|
| **Current Locations** | `bifrost-extensions/`, `thegent-plugin-host/` |
| **Suggested Library** | `libs/plugin-core` |
| **Rationale** | Dynamic module loading, lifecycle management, and registry patterns exist |
| **Plugin vs Lib** | Plugin architecture with extension points |

#### 8. Worktree Management Scripts

| Attribute | Value |
|-----------|-------|
| **Current Locations** | `worktree-manager/`, `worktrees/`, `scripts/worktree_governance.sh` |
| **Suggested Library** | `libs/worktree-utils` |
| **Rationale** | Git worktree listing, pruning, and cleanup scripts duplicated |
| **Plugin vs Lib** | Library (CLI scripts) |

---

## Candidate Architecture Decisions

### Library Extraction Criteria

A component should be extracted if it meets **3 of 5** criteria:

1. **Duplication** - Identical/similar code exists in 2+ repos
2. **Stability** - Interface is unlikely to change frequently
3. **Coherence** - Component has a single, well-defined purpose
4. **Reusability** - Multiple projects need this functionality
5. **Independence** - Component has no hard dependencies on product-specific code

### Plugin vs Library Decision Tree

```
┌─────────────────────────────────────────────────────┐
│ Does the component need runtime loading or swapping? │
└─────────────────────────────────────────────────────┘
                          │
           ┌──────────────┴──────────────┐
           │ YES                            │ NO
           ▼                               ▼
    ┌────────────┐                 ┌────────────┐
    │  PLUGIN   │                 │  LIBRARY   │
    │ ARCHITECT.│                 │            │
    └────────────┘                 └────────────┘
```

**Plugin candidates:** CLI extensions, adapter implementations, worktree-specific tools
**Library candidates:** Core domain logic, ports interfaces, configuration, logging

---

## Versioning Strategy

### Semantic Versioning (SemVer) Policy

| Type | Increment When | Example |
|------|---------------|---------|
| **MAJOR** | Breaking interface changes | 1.0.0 → 2.0.0 |
| **MINOR** | New features (backward compatible) | 1.0.0 → 1.1.0 |
| **PATCH** | Bug fixes (backward compatible) | 1.0.0 → 1.0.1 |

### Release Channels

- **stable** - Production-ready, locked major version
- **beta** - Pre-release, may have breaking changes
- **dev** - Active development, unstable

### Deprecation Policy

1. Announce deprecation in CHANGELOG.md
2. Add `/** @deprecated */` annotations (TS) or rust `#[deprecated]`
3. Keep old version for 2 minor releases
4. Remove in next major version

---

## Extraction Workflow

### Phase 1: Inventory

```bash
# Find potential duplicates
fdupes -r repos/ --threshold=2
# or
find . -name "*.py" -exec md5sum {} \; | sort | uniq -d -w 32
```

### Phase 2: Interface Design

1. Extract shared interfaces/contracts first
2. Write integration tests for the interface
3. Publish as v0.1.0 (unstable)

### Phase 3: Implementation Migration

1. Replace duplicated code with library dependency
2. Run full test suite
3. Update AGENTS.md / CLAUDE.md to reflect library usage

### Phase 4: Publish & Version

```bash
# Library publication (example for npm)
npm version minor
npm publish --access public

# For Go modules
git tag v1.2.0
git push origin v1.2.0
```

---

## Anti-Patterns to Avoid

### 1. God Library
**Problem:** Extracting too much into a single library creates coupling.
**Solution:** Keep libraries focused; prefer multiple small libs over one large lib.

### 2. Diamond Dependency
**Problem:** Multiple versions of same library across repos.
**Solution:** Lockfile discipline; use workspace/monorepo tools where possible.

### 3. Premature Abstraction
**Problem:** Extracting before pattern is stable.
**Solution:** Wait for 2+ concrete implementations before abstracting.

---

## Immediate Action Items

| Priority | Action | Owner | Deadline |
|----------|--------|-------|----------|
| **P1** | Extract hexagonal-core ports to `libs/hexagonal-core` | TBD | 2026-Q2 |
| **P1** | Audit CLI frameworks in helios-cli vs phenotype-cli-core | TBD | 2026-Q2 |
| **P2** | Create shared config-core library | TBD | 2026-Q3 |
| **P2** | Consolidate task-queue patterns | TBD | 2026-Q3 |
| **P3** | Document plugin architecture decision (ADR) | TBD | 2026-Q4 |

---

## References

- [ADR-001: Repository Organization](../adr/ADR-001-REPOSITORY-ORGANIZATION.md)
- [Rolling Hand Rules](../governance/rolling-hand-rules.md)
- [Phenotype Org-Wide Engineering Standard](../governance/PHENOTYPE_ORG_WIDE_ENGINEERING_STANDARD.md)
- [Hexagonal Architecture Pattern](https://alistair.cockburn.us/hexagonal-architecture/)
