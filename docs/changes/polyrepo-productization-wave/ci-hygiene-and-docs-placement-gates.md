# CI hygiene and docs placement — proposed gates

**Tasks 19–20:** Define checks so **hub** and **repos** stay maintainable without noisy root-level markdown and stray `src/`/`tests/` confusion.

## Proposed gate: top-level hygiene (hub)

**When:** Optional script in `scripts/` or pre-commit hook on `Phenotype/repos` (if git-enabled).

**Rules:**

1. No new **markdown** at repo root except allowlist: `README.md`, `CHANGELOG.md`, `AGENTS.md`, `CLAUDE.md`, `WORKLOG.md` (if adopted).
2. Session/plan docs live under **`docs/`** with appropriate subfolder (`docs/changes/`, `docs/reports/`, `docs/sessions/`).
3. Hub `src/`, `tests/`, `scripts/` at **repos root** that are policy stubs — treat as **policy** or relocate under `docs/` / `.hub-meta/` (see ADR-005).

## Proposed gate: docs placement

**Rule:** All non-allowlisted `*.md` outside `docs/` (and standard roots) **fail** the gate or open a **migration** task.

**Allowlist exceptions:** `README.md` in subdirs, `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md` at repo root.

## CI billing note

If GitHub Actions does not run, run these checks **locally** or via **pre-commit** until billing is restored.

## Implementation status

- **Spec only** — wire into `scripts/validate-governance.sh` or Taskfile when hub is ready for automation.
