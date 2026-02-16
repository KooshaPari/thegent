# Code Entity Map

**Last Updated:** {Date}
**Project:** {Project Name}
**Source Documents:** {List of requirement/design docs this map traces against — e.g., PRD v1.0, FR v1.0, ADR v1.0}

---

## 1. Forward Map: Code -> Requirements

{Maps each code entity to the requirements it implements. Use this to answer: "What requirement does this function fulfill?"}

### {Module/Package 1}: `{path/to/module}`

| Code Entity | File:Lines | Type | Maps To | Description |
|-------------|-----------|------|---------|-------------|
| `{function_name}` | `{file}:{start}-{end}` | Function | FR-{CAT}-{N}, E{x}.{y}.{z} | {What this function does} |
| `{class_name}` | `{file}:{start}-{end}` | Class | FR-{CAT}-{N}, ADR-{N} | {What this class represents} |
| `{handler_name}` | `{file}:{start}-{end}` | Handler | FR-{CAT}-{N}, E{x}.{y}.{z} | {What this handler processes} |
| `{config_name}` | `{file}:{start}-{end}` | Config | FR-{CAT}-{N} | {What this config controls} |

### {Module/Package 2}: `{path/to/module}`

| Code Entity | File:Lines | Type | Maps To | Description |
|-------------|-----------|------|---------|-------------|
| `{entity_name}` | `{file}:{start}-{end}` | {Type} | FR-{CAT}-{N} | {Description} |
| `{entity_name}` | `{file}:{start}-{end}` | {Type} | FR-{CAT}-{N}, E{x}.{y}.{z} | {Description} |

### {Module/Package 3}: `{path/to/module}`

| Code Entity | File:Lines | Type | Maps To | Description |
|-------------|-----------|------|---------|-------------|
| `{entity_name}` | `{file}:{start}-{end}` | {Type} | FR-{CAT}-{N} | {Description} |

{Continue for all modules...}

---

## 2. Reverse Map: Requirements -> Code

{Maps each requirement to its implementing code entities. Use this to answer: "Is this requirement implemented? Where?"}

### Functional Requirements

| Requirement | Code Entities | Completeness | Notes |
|-------------|---------------|-------------|-------|
| FR-{CAT1}-001 | `{entity1}`, `{entity2}`, `{entity3}` | COMPLETE | {Implementation notes} |
| FR-{CAT1}-002 | `{entity1}`, `{entity2}` | PARTIAL | {What is missing} |
| FR-{CAT1}-003 | — | NOT-STARTED | {Planned approach} |
| FR-{CAT2}-001 | `{entity1}` | COMPLETE | |
| FR-{CAT2}-002 | `{entity1}`, `{entity2}` | COMPLETE | |

### Epics / User Stories

| Story | Code Entities | Completeness | Notes |
|-------|---------------|-------------|-------|
| E{x}.{y}.{z} | `{entity1}`, `{entity2}` | COMPLETE | |
| E{x}.{y}.{z} | `{entity1}` | PARTIAL | {What remains} |
| E{x}.{y}.{z} | — | NOT-STARTED | |

### Architecture Decisions

| ADR | Code Entities | Implemented | Notes |
|-----|---------------|------------|-------|
| ADR-{N} | `{entity1}`, `{entity2}`, `{config1}` | YES | {How the decision manifests in code} |
| ADR-{N} | `{entity1}` | YES | |
| ADR-{N} | — | NO | {Planned or deferred} |

---

## 3. Dependency Map

{External dependencies and which requirements they support.}

| Dependency | Version | Used By | Required For | ADR |
|------------|---------|---------|-------------|-----|
| `{package_name}` | {version} | `{file1}`, `{file2}` | FR-{CAT}-{N} | ADR-{N} |
| `{package_name}` | {version} | `{file1}` | FR-{CAT}-{N}, FR-{CAT}-{N} | ADR-{N} |
| `{service_name}` | — | `{file1}`, `{file2}`, `{file3}` | FR-{CAT}-{N} | ADR-{N} |

---

## 4. Coverage Summary

| Category | Total Requirements | Implemented | Partial | Not Started |
|----------|-------------------|-------------|---------|-------------|
| FR-{CAT1} | {n} | {n} | {n} | {n} |
| FR-{CAT2} | {n} | {n} | {n} | {n} |
| FR-{CAT3} | {n} | {n} | {n} | {n} |
| ADRs | {n} | {n} | {n} | {n} |
| **Total** | **{n}** | **{n}** | **{n}** | **{n}** |

---

## 5. Unmapped Code

{Code entities that do not trace to any documented requirement. These may indicate undocumented features, technical debt, or requirements gaps.}

| Code Entity | File:Lines | Type | Possible Mapping | Notes |
|-------------|-----------|------|-----------------|-------|
| `{entity_name}` | `{file}:{start}-{end}` | {Type} | {Suggested FR or "None"} | {Why it exists} |

---

<!--
Code Entity Map Guidelines:
  - Update on every significant code change
  - Types: Function, Class, Method, Handler, Middleware, Config, Schema, Migration, Test
  - Completeness: COMPLETE, PARTIAL, NOT-STARTED
  - File:Lines format: relative path from project root, line range (e.g., src/auth/login.ts:15-48)
  - Forward map groups by module/package for navigation
  - Reverse map groups by requirement document for coverage analysis
  - Unmapped code section catches drift between docs and implementation
  - Coverage summary gives at-a-glance completeness
-->
