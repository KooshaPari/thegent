# Changelog

All notable changes to thegent are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

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
