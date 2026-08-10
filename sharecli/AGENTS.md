# thegent-sharecli Agent Instructions

## Project

CLI tooling for thegent share/directory functionality.

## Stack

TBD — this rig is being bootstrapped. Explore `pkg/`, `cmd/`, and `internal/` once code is present.

## Kilo Integration

This repo is a **rig** in Kilo Gastown:

- **Rig ID:** `03e7d736-587f-4e1a-aa4d-ea735ad5df45`
- **Town:** `78a8d430-a206-4a25-96c0-5cd9f5caf984`

### Work Delegation

Use `gt_sling` or `gt_sling_batch` to delegate work to other polecats in this rig or across the town.

### Tracking

Use `gt_list_convoys` to track convoy progress across this methodology chain.

## Polecat Conventions

Polecat agents in this rig follow the naming pattern: `{moniker}-{species}-{rig-hash}@{town-id}`

Example: `coral-polecat-03e7d736@78a8d430`

## Build & Test

Build commands will be documented once the project stack is established. Common patterns:

- Go: `go build ./...` / `go test ./...`
- Node: `npm run build` / `npm test`
- Python: `pip install` + `pytest`

Run `go vet ./...` or equivalent linter before submitting PRs.

## Architecture Notes

- TBD — document once codebase structure is populated
