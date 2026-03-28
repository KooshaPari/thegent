# ADR-011: SDK Release and Versioning Strategy

**Date**: 2026-03-25
**Status**: Proposed
**Deciders**: Phenotype Team

## Context

We maintain SDKs in multiple languages (Rust, Go, TypeScript, Python) that must be:
- Versioned consistently across languages
- Released in sync when breaking changes occur
- Backward compatible within major versions
- Documented with changelogs

## Decision

We adopt **Semantic Versioning 2.0** (SemVer) with the following conventions:

### Version Format
`MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (API incompatibility)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Channels

| Channel | Tag | Description |
|---------|-----|-------------|
| Stable | `v1.2.3` | Production-ready releases |
| Beta | `v1.2.3-beta.1` | Pre-release testing |
| Alpha | `v1.2.3-alpha.1` | Early development |
| Nightly | `nightly-20260325` | Daily builds |

### Release Process

1. **Release Planning**: Tag issues with milestone
2. **Change Log Generation**: Automated from conventional commits
3. **Version Bump**: Automated via release workflow
4. **Build & Test**: Multi-language CI pipeline
5. **Publish**: To respective registries
6. **Announcement**: GitHub release + documentation update

### SDK Version Matrix

| SDK | Registry | Format |
|-----|----------|--------|
| Rust | crates.io | `phenotype-logging = "1.0.0"` |
| Go | pkg.go.dev | `github.com/phenotype/sdk v1.0.0` |
| TypeScript | npm | `@phenotype/sdk@1.0.0` |
| Python | PyPI | `phenotype-sdk==1.0.0` |

## Consequences

### Positive
- Clear versioning expectations
- Automated release process
- Consistent release cadence
- Cross-SDK compatibility guaranteed

### Negative
- Strict breaking change policy
- Release coordination overhead
- Registry credential management
