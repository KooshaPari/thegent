# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.2.0] - 2026-03-29

### Added

- Unblock Rust CI (cache, TUI tests, rustfmt) (#590)
- Wave D Rust lane handoff and known issues update (#589)
- Modernize Python tooling to 2026 bleeding-edge standards
- Remove package-lock.json (use bun/pnpm strictly)
- `docs/reference/FULL_TURN_DELIVERY.md` — stable pointer for **full-turn** expectations (merge to `main`/`release/*`, `gh` PR URLs, changelog, version, docs); `AGENTS.md` cross-link under Worktree Governance.
- Session documentation pack for Phenotype local worktree forest governance: blocker matrix, waves A–G (24-item queues), **full-turn delivery** policy (PR/merge to `main`/`release/*`, changelog, `gh` evidence), and PR #549 CI snapshot (`docs/sessions/20260324-phenotype-local-worktree-forest-blocker-matrix/`).
- Byteport cloud deployment platform (full source + security gitignore + templates) (#872, #873)
- Complete workspace consolidation with 913-file detached-HEAD work rescue (#865)
- Benchmark, dotfiles, and engine modules

### Changed

- `FULL_TURN_DELIVERY.md`: snapshot expanded with PR #550, `mergeStateStatus`, `main` branch CI signal, and **GitHub Actions billing** note (jobs not started until billing/spend limit fixed).
- Upgrade cryptography to 46.0.6 (CVE-2026-34073) (#861, #862)
- Wave 84 cleanup and module member export fixes

### Fixed

- Properly export ThegentSettings from config module (#867)
- Add ImportError handling in cli init, fix test import path (#866)
- Remove duplicate module_name parameter in test (#869)

### Chore

- Sync local template and test fix commits (#870)
- Sync local main commits (colab submodule + worktree gitignore) (#864)
- Archive 200+ BACKLOG items to reduce WORK_STREAM noise (#856)
- Refresh KooshaPari GitHub inventory timestamps (2026-03-29) (#857, #858)
- Security patches - update Rust lru and document Go/Python updates (#854)
- Merge PR #851 for final merge stabilization (#871)

## [0.1.0] - 2026-02-23

### Added

- mise integration for automated tool management (`install_mise`, `verify_mise_installation`, `install_system_dependencies` in `install.py`)
- `thegent install --system-deps` CLI flag installs Homebrew and mise and writes shell activation hooks
- `thegent install --verify-mise` validates mise is installed and shell hooks are configured
- `thegent install --uninstall-mise-hooks` removes mise activation lines from shell config files
- Automatic shell config backup before any modification (`~/.thegent/backups/`)
- Multi-shell support for mise hooks: zsh, bash, fish, tcsh
- `scripts/test_mise_installation.sh` integration test script for mise setup validation (WL-035)
- Stale `.shadow-*` directory cleanup in `mcp_prune` via `_prune_stale_shadow_and_logs` with configurable `--age` (default 24h) (WL-036)
- `thegent doctor` now reports stale shadow directories with actionable fix hint pointing to `thegent mcp prune` (WL-036)
- `GardeningManager.run_shadow_cleanup` periodic task in `sitback/gardening.py` removes `.shadow-*` dirs older than 7 days (WL-036)
- `NeverIdleLoop.GARDENING_STEPS` now includes `shadow_cleanup` for automatic periodic disk reclamation (WL-036)
- **Documentation Updates**:
  - ADR-005, ADR-006, ADR-007 added to ADR.md
  - FR_TRACKER.md expanded to cover all 95 FRs
  - User Stories (US-E1 through US-E5) added to PRD.md
  - Contract items for all ADRs, FRs, and User Stories

### Changed

### Deprecated

### Removed

### Fixed

### Security

## Unreleased

- ci: refresh PR body and add `layered-pr-exception` label to satisfy PR Governance Gate
  (re-trigger Governance Gate after the body/label fix).

## pyo3 0.28.3 → 0.29.0

Bumps the optional `pyo3` dependency from 0.28.3 to 0.29 across all
14 thegent crates that ship Python bindings. Required to clear
`cargo-deny advisories`:

- RUSTSEC-2026-0176: OOB read in `nth` / `nth_back` (fixed in 0.29)
- RUSTSEC-2026-0177: missing `Sync` bound (fixed in 0.29)

`pyo3` is gated behind the `python` feature in every crate, so the
change is contained to optional builds.
