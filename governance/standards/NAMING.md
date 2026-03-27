# Naming Conventions

> **Lifecycle**: Active  
> **Owner**: Platform Team  
> **Version**: 1.0.0  

## Purpose

This document defines naming conventions for all Phenotype ecosystem packages, libraries, and tools.

---

## Package Naming Rules

### Phenotype-Hierarchy Packages

Phenotype-prefix packages follow the product taxonomy:

```
phenotype-<product>-<component>
```

Examples:
- `phenotype-cli-core` — CLI foundation
- `phenotype-config` — Configuration system
- `phenotype-design` — Design tokens/themes
- `phenotype-docs-engine` — Documentation tooling
- `phenotype-task-engine` — Task/orchestration engine

**Rule**: Use `phenotype-` when the package is tightly coupled to Phenotype-specific systems, internal integrations, or product-specific features.

### Market-Neutral / Helix Hierarchy

Market-neutral packages that could be published tocrates.io use the `helix-` prefix:

```
helix-<domain>
```

Examples:
- `helix-logging` — Structured logging
- `helix-tracing` — Distributed tracing
- `helix-crypto` — Cryptography primitives

**Rule**: Use `helix-` when the package has no Phenotype-specific dependencies and could stand alone as a general-purpose library.

### Special-Purpose Hubs

Reference/documentation hubs keep the `phenotype-` prefix:

```
phenotype-<hub-name>
```

Examples:
- `phenotype-xdd` — x-DD methodology compendium
- `phenotype-forge` — CLI task runner
- `phenotype-skills-clone` — Skills catalog

**Rule**: Use `phenotype-` for documentation hubs, skills repositories, and reference assets.

### Language-Specific Templates

Language template repos use the `template-lang-` prefix:

```
template-lang-<language>
```

Examples:
- `template-lang-rust` — Rust project template
- `template-lang-go` — Go project template
- `template-lang-typescript` — TypeScript project template

---

## Migration Guidance

| Old Name | New Name | Status |
|----------|----------|--------|
| `cipher` | `helix-crypto` | ✅ Complete |
| `logger` | `helix-logging` | ✅ Complete |
| `tracing-helpers` | `helix-tracing` | ✅ Complete |
| `phenotype-gauge` | Keep as-is | ✅ Productized |
| `phenotype-nexus` | Keep as-is | ✅ Productized |

---

## Branch Naming

```
<type>/<short-description>
```

Types:
- `feat/` — New features
- `fix/` — Bug fixes
- `chore/` — Maintenance tasks
- `docs/` — Documentation changes
- `refactor/` — Code refactoring

Examples:
- `feat/add-oauth-support`
- `fix/resize-handler-memory-leak`
- `chore/upgrade-dependencies`

---

## Commit Message Format

```
<type>(<scope>): <description>

[optional body]
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`

Examples:
- `feat(auth): add OAuth2 token refresh`
- `fix(api): handle nil response gracefully`
- `chore(deps): upgrade tracing to 0.1.50`

---

## See Also

- [ADR-0006: Library vs Package Distribution](../adr/0006-library-vs-package-distinction.md)
- [Package Naming Decision](NAMING_FAMILY_DECISION_PLACEHOLDER.md)
