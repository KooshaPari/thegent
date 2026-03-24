# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `docs/reference/FULL_TURN_DELIVERY.md` — stable pointer for **full-turn** expectations (merge to `main`/`release/*`, `gh` PR URLs, changelog, version, docs); `AGENTS.md` cross-link under Worktree Governance.

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

---

## [Unreleased]

### Added

- Session documentation pack for Phenotype local worktree forest governance: blocker matrix, waves A–G (24-item queues), **full-turn delivery** policy (PR/merge to `main`/`release/*`, changelog, `gh` evidence), and PR #549 CI snapshot (`docs/sessions/20260324-phenotype-local-worktree-forest-blocker-matrix/`).

### Changed

- `FULL_TURN_DELIVERY.md`: snapshot expanded with PR #550, `mergeStateStatus`, `main` branch CI signal, and **GitHub Actions billing** note (jobs not started until billing/spend limit fixed).

### Deprecated

### Removed

### Fixed

### Security
