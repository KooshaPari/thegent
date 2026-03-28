# Session 2026-03-28: hexagon-go Cleanup

## Context
- Lane: `libs/hexagon-go` (fifth of the backlog set requested)
- Repository: Phenotype/libification push; the template currently exposes domain/application/infrastructure layers, a README that describes a `cmd/` entrypoint that is missing, and a CI matrix referencing go 1.24.
- Constraints: follow top-level `AGENTS.md` (UTF-8, CLI-first) plus the lane-specific `CLAUDE.md` (go test/go mod download, no `.claude/.codex` commits); plan must be documented before execution and wait for approval before making code changes.

## Cleanup Goal
Modernize this hexagonal Go template so it becomes runnable, documented, and aligns with the Phenotype libification roadmap (i.e., shared port definitions, outbound adapters, and consistent scaffolding with tests and CI).

## High-Level Plan (no execution yet)
1. **Audit the current template surface** – confirm which directories exist, what endpoints are referenced (README vs reality), and highlight any mismatches (missing `cmd/server`, stubbed CLI, outdated instructions). Record findings in this session doc before any code changes.
2. **Code hygiene & scaffolding** – prepare to add the missing entrypoint (`cmd/server`) by wiring a small HTTP or CLI runner, ensure `application` handlers hook into domain ports, and clean up any unused or redundant files (e.g., `domain/ports/inbound` interfaces not satisfied by the template)
3. **Dependency/tooling alignment** – sync `go.mod` to the CI-defined Go version (1.24), add/testing convenience (go test + golangci-lint) and ensure Docker/CI artifacts align with root conventions for libs (UTF-8 sources, no agent artifact check-ins).
4. **Verification & documentation** – plan for targeted unit tests, SQL schema stubs under `infrastructure`, and README/CLAUDE/CONTRIBUTING updates that reflect the new runnable sample before marking the lane as cleaned.

## Next Step
Hold until confirmed; once green-lit, the work will proceed in the order above, with short updates to this documentation channel after each step.
