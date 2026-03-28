# Phenotype Libs — Canonical Library Index

This document records the canonical hexagonal architecture library per language and explains
the relationship between canonical packages, variant packages, and archived stubs.

## Hexagonal Architecture Libraries

| Language   | Canonical Package    | Status  | Path                  | Notes                                                                 |
|------------|----------------------|---------|-----------------------|-----------------------------------------------------------------------|
| Rust       | `hexagonal-rs`       | Active  | `libs/hexagonal-rs/`  | Full Cargo crate with `src/`, `Cargo.toml`. Use this.                |
| Go         | `hexagonal-go`       | Active  | `libs/hexagonal-go/`  | Full module with `adapters/`, `domain/`, `ports/`, `go.mod`.         |
| Python     | `hexagonal-py`       | Active  | `libs/hexagonal-py/`  | Full package with `pyproject.toml`, installable dist.                |
| TypeScript | `hexagonal-ts`       | Active  | `libs/hexagonal-ts/`  | Full npm package with `src/`, `tsconfig.json`, dist.                 |

## Rust Hexagonal Toolkit

| Package    | Status  | Path              | Notes                                                       |
|------------|---------|-------------------|-------------------------------------------------------------|
| `hexkit`   | Active  | `libs/hexkit/`    | Rust hexagonal architecture toolkit; includes benches and examples. |

## Variant / Comparison Packages

These directories contain alternative or experimental implementations. They are **not** the
canonical choice but are kept for reference and comparison purposes.

| Package      | Language   | Path                | Purpose                                        |
|--------------|------------|---------------------|------------------------------------------------|
| `go-hex`     | Go         | `libs/go-hex/`      | Alternative Go hex impl with comparison docs.  |
| `hexagon-go` | Go         | `libs/hexagon-go/`  | Earlier Go hex impl; has application/domain.   |
| `ts-hex`     | TypeScript | `libs/ts-hex/`      | Alternative TS hex impl with comparison docs.  |
| `pyhex`      | Python     | `libs/pyhex/`       | Alternative Python hex impl with comparison docs. |

## Archived / Deprecated Stubs

The following directories contained only LICENSE and README files with no implementation.
They have been moved to `.archive/deprecated-libs/` and must not be used.

| Archived Name    | Language   | Reason for Archival                                      |
|------------------|------------|----------------------------------------------------------|
| `hexagon-rs`     | Rust       | Stub only (LICENSE + README). Superseded by `hexagonal-rs`. |
| `hexagon-python` | Python     | Stub only (LICENSE + README). Superseded by `hexagonal-py`. |
| `hexagon-ts`     | TypeScript | Stub only (LICENSE + README). Superseded by `hexagonal-ts`. |
| `hexagon-java`   | Java       | Stub only (LICENSE + README). No canonical Java hex lib in scope. |
| `hexagon-rust`   | Rust       | Stub only (LICENSE + README). Superseded by `hexagonal-rs`. |
| `hexagon-elixir` | Elixir     | Stub only (LICENSE + README). No canonical Elixir hex lib in scope. |
| `hexkit-root-stub` | Rust     | Root-level `hexkit/` directory with CLAUDE.md only. Canonical `hexkit` is at `libs/hexkit/`. |

See `.archive/deprecated-libs/` for the archived directories.

## Canonical Choice Rules

1. Always import from `hexagonal-<lang>` (e.g. `hexagonal-rs`, `hexagonal-go`).
2. Use `libs/hexkit` for Rust-specific hexagonal toolkit utilities.
3. Never reference archived stubs in new code.
4. Variant packages (`go-hex`, `ts-hex`, `pyhex`, `hexagon-go`) may be read for comparison but
   should not be imported in production code without explicit ADR approval.

## See Also

- `libs/README.md` — Full library inventory and build instructions.
- `governance/adrs/0002-package-classification-framework.md` — Package classification rules.
- `.archive/deprecated-libs/` — Archived stub directories.
