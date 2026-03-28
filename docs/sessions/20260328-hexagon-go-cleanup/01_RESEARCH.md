- **Structure inventory**
  - `README.md` touts adapters (cmd/server, application, domain) but the repo currently contains `application`, `domain`, and `infrastructure` plus `.github`/CI workflows; no `cmd/` directory exists yet, which will be a focus for wiring the runnable layer.
  - `domain` exposes a simple `Example` entity with `CRUD` errors, `ports/outbound.Repository`, and auxiliary `valueobjects.Pagination`. The inbound port is defined but not consumed anywhere; commands/queries currently rely solely on the outbound repository.
  - `infrastructure/adapters/persistence` holds a `PostgresRepository` that implements `Save`, `FindByID`, `Delete`, `List`, `InitSchema`, and a `PostgresAdapter` helper; this is a good base for wiring tests but needs connection-string validation and migrations.
  - `.github/workflows/ci.yml` builds/tests against Go 1.24 and runs golangci-lint/gosec; `go.mod` is still set to go 1.21. Aligning these versions will be part of the cleanup.
  - `CLAUDE.md` documents the go test/go mod download command and has lightweight rules (UTF-8, no agent dirs, maintain main on canonical repo), which we will obey while editing.
  - Documentation: CONSISTENT path to `libs` to support hexagonal shared ports (per `docs/governance/LIBIFICATION-AUDIT.md`), meaning our cleanup should leave this template ready for future extraction into a shared library (align port interfaces, ensure README is accurate, include sample configuration).

This research/notes file will be updated if more context or discoveries arise before executing the cleanup.
