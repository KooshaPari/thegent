# Architecture Decision Record Template

## ADR Template

Copy this template when creating a new ADR. Replace all `{...}` placeholders.

---

```markdown
# ADR-{NUMBER}: {Title}

**Date:** {YYYY-MM-DD}
**Status:** {Proposed|Accepted|Deprecated|Superseded}
**Superseded by:** ADR-{NUMBER} (if applicable)
**Supersedes:** ADR-{NUMBER} (if applicable)

---

## Context

{Describe the situation and problem that requires a decision.}

{Include relevant background, constraints, and stakeholders.}

---

## Decision

{Describe the decision that was made.}

{Explain the rationale and how it addresses the problem.}

---

## Consequences

### Positive

{...}

### Negative

{...}

### Neutral

{...}

---

## Alternatives Considered

### Alternative 1: {Name}

**Pros:**
- {...}

**Cons:**
- {...}

**Why not chosen:** {Reason}

### Alternative 2: {Name}

**Pros:**
- {...}

**Cons:**
- {...}

**Why not chosen:** {Reason}

---

## References

- [xDD Methodology Compendium](../xdd-methodology-compendium.md)
- {Other relevant links}

---

## Notes

{Any additional notes, implementation hints, or follow-up items.}

---

*Created: {YYYY-MM-DD}*
*Maintained by: {Team/Role}*
```

---

## Quick Reference

### ADR Status Definitions

| Status | Meaning |
|--------|---------|
| **Proposed** | Under review, not yet accepted |
| **Accepted** | Approved and should be implemented |
| **Deprecated** | No longer relevant, kept for history |
| **Superseded** | Replaced by a newer ADR |

### When to Create an ADR

Create an ADR when:

1. **Architectural decisions** - Significant changes to system structure
2. **Technology choices** - Selecting or replacing major technologies
3. **Pattern adoption** - Introducing new patterns or practices
4. **Trade-offs** - Decisions with meaningful trade-offs
5. **Cross-cutting concerns** - Affecting multiple components

### What Should Be in an ADR

An ADR should include:

1. **Clear context** - What problem are we solving?
2. **The decision** - What was decided?
3. **Consequences** - What are the impacts (good and bad)?
4. **Alternatives** - What else was considered and why not?

### What Should NOT Be in an ADR

An ADR should NOT include:

1. **Trivial decisions** - Use comments in code instead
2. **Implementation details** - Keep at the decision level
3. **Meeting minutes** - Summarize decisions, don't record discussions
4. **Changing requirements** - Update context, don't argue in ADR

---

## Example ADRs

For examples, see the ADRs in this directory:

- [ADR-001: Repository Organization](./0001-repository-organization.md) - Existing organizational decision
- [ADR-002: Package Classification Framework](./0002-package-classification-framework.md) - Classification system
- [ADR-003: Hexagonal Architecture Standard](./0003-hexagonal-architecture-standard.md) - Architecture pattern
- [ADR-004: Naming Conventions](./0004-naming-conventions.md) - Naming standards
- [ADR-005: Top-Level Directory Structure](./0005-top-level-directory-structure.md) - Directory layout
- [ADR-006: Library vs Package Distinction](./0006-library-vs-package-distinction.md) - Scope boundaries

---

## Related Documents

- [xDD Methodology Compendium](../xdd-methodology-compendium.md) - 100+ methodologies reference
- [Phenotype Architecture Reorganization Plan](../phenotype-architecture-reorganization.md) - Full reorganization plan
