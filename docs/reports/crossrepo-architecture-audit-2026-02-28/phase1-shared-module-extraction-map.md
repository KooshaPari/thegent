# Phase 1 Shared-Module Extraction Map (2026-02-28)

## Scope
- Source root: /Users/kooshapari/CodeProjects/Phenotype/repos
- Evidence baseline: /Users/kooshapari/CodeProjects/Phenotype/repos/docs/reports/crossrepo-architecture-audit-2026-02-28/mirror-duplication-matrix.csv

## Candidate Modules (Ranked)

1. `spec-kitty-task-engine` (highest ROI)
- Current source-of-truth candidate:
  - /Users/kooshapari/CodeProjects/Phenotype/repos/thegent/.kittify/scripts/tasks/
- Current duplicated consumers:
  - /Users/kooshapari/CodeProjects/Phenotype/repos/cliproxyapi++/.kittify/scripts/tasks/
  - /Users/kooshapari/CodeProjects/Phenotype/repos/cliproxyapi-plusplus/.kittify/scripts/tasks/
  - /Users/kooshapari/CodeProjects/Phenotype/repos/agentapi-plusplus/.kittify/scripts/tasks/
  - /Users/kooshapari/CodeProjects/Phenotype/repos/heliosApp/.kittify/scripts/tasks/
  - /Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI/.kittify/scripts/tasks/
  - /Users/kooshapari/CodeProjects/Phenotype/repos/helios-cli/.kittify/scripts/tasks/
  - /Users/kooshapari/CodeProjects/Phenotype/repos/portage/.kittify/scripts/tasks/
  - /Users/kooshapari/CodeProjects/Phenotype/repos/tokenledger/.kittify/scripts/tasks/
- Extraction target:
  - /Users/kooshapari/CodeProjects/Phenotype/repos/sdk/spec-kitty-task-engine (new)
- Packaging:
  - Python package with pinned version tags; thin repo-local wrappers only.

2. `contracts-core` (API/SDK consistency)
- Current fragmented locations:
  - /Users/kooshapari/CodeProjects/Phenotype/repos/cliproxyapi-plusplus/contracts
  - /Users/kooshapari/CodeProjects/Phenotype/repos/agentapi-plusplus/docs
  - /Users/kooshapari/CodeProjects/Phenotype/repos/thegent/contracts
- Extraction target:
  - /Users/kooshapari/CodeProjects/Phenotype/repos/contracts/core
- Contents:
  - OpenAPI schemas, event contracts, shared ID/error envelope schemas.

3. `runtime-id-and-trace` (polyglot consistency)
- Current fragmented implementations:
  - /Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI/codex-rs
  - /Users/kooshapari/CodeProjects/Phenotype/repos/thegent/src/thegent
  - /Users/kooshapari/CodeProjects/Phenotype/repos/tokenledger/src
- Extraction target:
  - /Users/kooshapari/CodeProjects/Phenotype/repos/sdk/runtime-id-trace
- Contents:
  - ID generation policy, trace/span envelope formats, correlation headers.

## Extraction Sequencing
1. Extract `spec-kitty-task-engine` first (lowest risk, highest duplication).
2. Extract `contracts-core` second (enables strict adapter/API boundaries).
3. Extract `runtime-id-and-trace` third (requires protocol lock across Rust/Python/TS).

## Adoption Rules
- No direct copy-paste of shared modules after extraction.
- Consumers pin explicit versions; upgrades via changelog + compatibility tests.
- Shared module PRs require cross-repo consumer test matrix evidence.
