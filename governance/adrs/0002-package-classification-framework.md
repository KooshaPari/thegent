# ADR-002: Package Classification Framework

**Date:** 2026-03-25
**Status:** Proposed
**Supersedes:** N/A

---

## Context

The Phenotype ecosystem contains 20+ repositories with the `phenotype-` prefix, but not all of them represent Phenotype-specific functionality. Some packages contain general-purpose, domain-agnostic code that could be useful to the broader developer community, while others are tightly coupled to Phenotype's business domain.

This inconsistency leads to:
- Namespace pollution in the `phenotype-*` namespace
- Confusion about which packages are Phenotype-specific vs. general-purpose
- Missed opportunities for community contributions and reuse
- Difficulty in understanding project boundaries

---

## Decision

We establish a **three-tier classification system** for Phenotype packages:

### Type A: Phenotype-Domain Packages

**Naming:** `phenotype-{domain}`
**Examples:** `phenotype-config`, `phenotype-design`, `phenotype-agent`

**Criteria:**
- Contains Phenotype-specific business logic
- Tied to Phenotype's core domain model
- Not reusable outside Phenotype context
- Contains Phenotype-specific schemas or configurations

**Rules:**
- MUST retain the `phenotype-` prefix
- MUST be located in `packages/` directory
- MUST NOT depend on Type B packages without justification
- SHOULD be productized separately if the domain grows large

### Type B: Extractable Libraries

**Naming:** `{library-name}` (NO prefix)
**Examples:** `hexagonal-rs`, `event-sourcing`, `xdd-lib`, `config-lib`

**Criteria:**
- General-purpose, applicable to any software project
- No Phenotype-specific assumptions or dependencies
- Can be published as standalone packages (crates.io, npm, PyPI)
- Provides value independent of Phenotype

**Rules:**
- MUST NOT have the `phenotype-` prefix
- MUST be located in `libs/` directory
- MUST have comprehensive tests and documentation
- MUST be framework-agnostic where possible
- SHOULD be published to public registries for community use

### Type C: Internal Tools

**Naming:** `phenotype-{tool}` (as repository name, but internal)
**Examples:** `phenotype-skills`, `phenotype-cli`, `phenotype-scripts`

**Criteria:**
- Phenotype-specific tooling
- Not intended for external use
- Development/DevOps utilities
- Internal CLIs and scripts

**Rules:**
- Repository name MAY have `phenotype-` prefix
- Code within SHOULD NOT have prefix
- MUST be located in `tools/` or appropriate domain directory
- MAY be closed-source or internal-only

---

## Consequences

### Positive

1. **Clear separation** - Developers immediately know if a package is Phenotype-specific or general-purpose
2. **Community potential** - Type B packages can be opensourced and potentially gain external contributors
3. **Cleaner dependencies** - Type A packages have explicit dependencies on Type B, making the architecture clearer
4. **Namespace freed** - The `phenotype-` namespace is reserved for truly Phenotype-bound packages

### Negative

1. **Migration effort** - Existing packages must be reviewed and potentially reorganized
2. **Name changes** - Some packages will need renaming, which could break existing imports
3. **Additional governance** - New packages require classification decisions

### Neutral

1. **Classification ambiguity** - Some packages may fall into gray areas requiring judgment calls
2. **Reclassification possibility** - Packages may need to move between types over time

---

## Alternatives Considered

### Alternative 1: Keep All with `phenotype-` Prefix

**Pros:**
- Simple, consistent naming
- No migration required

**Cons:**
- Namespace pollution continues
- Misleading - packages aren't all Phenotype-specific
- Missed opportunities for community contributions

**Why not chosen:** Goes against the goal of creating clean, reusable libraries.

### Alternative 2: Two-Tier System (Public/Private Only)

**Pros:**
- Simpler than three tiers
- Clear public vs. private distinction

**Cons:**
- Doesn't distinguish between Phenotype-domain and generic libraries
- A `phenotype-logging` package would still be confusing if it's just a logging wrapper

**Why not chosen:** The three-tier system provides more nuanced guidance for package organization.

---

## Classification Decision Matrix

Use this flowchart to classify a new package:

```
Is the package Phenotype-specific?
│
├─ NO ──► Is it reusable by any developer/project?
│         │
│         ├─ YES ──► TYPE B: Extractable Library
│         │          (No prefix, publishable)
│         │
│         └─ NO ──► TYPE C: Internal Tool
│                    (Phenotype-specific tooling)
│
└─ YES ──► TYPE A: Phenotype-Domain Package
           (Keep phenotype- prefix)
```

---

## Migration Guidelines

### Existing Packages Review

Each existing `phenotype-*` package should be reviewed:

| Package | Classification | Action |
|---------|---------------|--------|
| `phenotype-config` | Type A | Keep in `packages/` |
| `phenotype-design` | Type A | Keep in `packages/` |
| `phenotype-hexagonal` | Type B | Move to `libs/hexagonal-rs` |
| `phenotype-ts-hexagonal` | Type B | Move to `libs/hexagonal-ts` |
| `phenotype-py-hexagonal` | Type B | Move to `libs/hexagonal-py` |
| `phenotype-go-hexagonal` | Type B | Move to `libs/hexagonal-go` |
| `phenotype-xdd-lib` | Type B | Move to `libs/xdd-lib-rs` |
| `phenotype-skills-clone` | Type C | Move to `tools/phenotype-skills` |

---

## References

- [xDD Methodology Compendium](../xdd-methodology-compendium.md)
- [ADR-001: Repository Organization](./0001-repository-organization.md)
- [ADR-005: Top-Level Directory Structure](./0005-top-level-directory-structure.md)
- [ADR-006: Library vs Package Distinction](./0006-library-vs-package-distinction.md)

---

## Notes

- Classification should be reviewed during quarterly architecture reviews
- New packages MUST be classified before creation
- Reclassification requires an ADR if it involves renaming

---

*Created: 2026-03-25*
*Maintained by: Architecture Guild*
