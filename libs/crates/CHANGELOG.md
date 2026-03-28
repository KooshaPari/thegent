# Changelog

All notable changes to the AgilePlus P2P project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-25

### Added

- Initial release of the crates repository with `agileplus-p2p` crate
- Core state export functionality with `export_state` function
- Deterministic JSON serialization using sorted keys and 2-space indentation
- Event store trait for fetching events by entity and sequence
- Snapshot store trait for saving and retrieving snapshots
- Device store trait for managing device metadata
- JSONL (JSON Lines) format export for events (one event per line)
- Snapshot export to pretty-printed JSON files
- Sync metadata export (sync mappings and device sync vectors)
- Atomic file writes to prevent corruption on failure
- Comprehensive error types with `ExportError` enum
- Export statistics tracking (events, snapshots, sync mappings, duration)
- Full workspace configuration with `Cargo.toml`
- Functional CI/CD scripts for quality gate, security audit, and policy validation
- GitHub Actions workflows for testing and validation
- Basic tests covering the full export flow
- Documentation (README, CLAUDE.md, CONTRIBUTING.md)

### Known Issues

- No compression support for large exports
- File writes are atomic but not transactional across multiple files
- Limited error recovery mechanisms
- No incremental/delta export (always exports full state)
- Test coverage is ~25% (target is 80%+)

### Not Yet Implemented

- Performance benchmarks
- Parallel entity export
- Merkle tree verification
- Conflict resolution strategies
- Database persistence layer
- Incremental sync support
- Property-based testing
- Full mutation testing

## Future Releases

### [0.2.0] (Planned Q2 2026)

- Compression support (gzip)
- Incremental export (only changes since last sync vector)
- Parallel entity export for large datasets
- Metrics and observability hooks
- Additional benchmarks

### [0.3.0] (Planned Q3 2026)

- Supabase/PostgreSQL persistence layer
- Merkle tree verification for data integrity
- Conflict resolution strategies
- Full test coverage (>80%)

---

## Guidelines for Updating

When making changes:

1. Add an entry under `[Unreleased]` for each change
2. Follow the categories: Added, Changed, Deprecated, Removed, Fixed, Security
3. Include a link to the relevant issue/PR if applicable
4. Before release, move entries to the version section and update the version header

### Format

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature description

### Changed
- Modification to existing feature

### Fixed
- Bug fix description

### Security
- Security issue fix

### Removed
- Deprecated feature removal
```
