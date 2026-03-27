# ADR-00N5: Naming Family for Market-Neutral Extracted Libraries

**Date:** 2026-03-26
**Status:** DECIDED
**Deciders:** Koosha Pari

## Context

When extracting market-neutral libraries from the Phenotype ecosystem for general reuse, we need a consistent naming scheme that:

1. Doesn't collide with existing product names (e.g., `forge` CLI tool)
2. Is available on package registries (npm, crates.io)
3. Clearly indicates the package is a hexagonal-architecture "port" or "kit"
4. Is short and memorable

## Decision

Use **`helix-`** as the prefix for all reusable library packages extracted from the Phenotype ecosystem.

### Rationale

1. **`helix-`** — Already adopted for observability libraries (`helix-logging`, `helix-tracing`), consistent and memorable
2. Avoid **`forge-*`** — Collides with the `forge` CLI tool name
3. Avoid **`kit-*`** — Too generic, could conflict with many existing packages
4. Avoid **`port-*`** — Accurate for hexagonal ports, but less memorable

### Consequences

**Positive:**
- Consistent with already-productized `helix-logging` and `helix-tracing`
- Clear brand identity: `helix-*` = hexagonal-architecture library
- Available on npm/crates.io as scoped packages (`@phenotype/helix-*`)

**Negative:**
- Requires migrating existing `cipher`, `gauge`, `nexus` packages to `helix-*` naming

## Alternatives Considered

| Family | Example | Decision |
|--------|---------|----------|
| `helix-*` | `helix-logging`, `helix-tracing` | DECIDED |
| `kit-*` | `hexkit-go`, `portkit` | Rejected — generic |
| `port-*` | `port-auth-ts` | Rejected — less memorable |
| `forge-*` | `forge-logging` | Rejected — collides with CLI |

## Migration

Libraries to rename:

| Current | Proposed | Status |
|---------|----------|--------|
| `cipher` | `helix-crypto` | Pending |
| `gauge` | Keep `gauge` | Keep (special purpose) |
| `nexus` | Keep `nexus` | Keep (service registry) |

## References

- POLYREPO_PACKAGE_NAMING_AND_PRODUCTIZATION.md
- ADR-0006: Library vs Package Distribution
