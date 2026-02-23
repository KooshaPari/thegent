# Polyglot Runtime Decision Matrix

This template doc is the project-level baseline for runtime/testing and conversion decisions.

## Runtime Matrix

| Language | Primary | Secondary | Fallback | Required Gates |
|---|---|---|---|---|
| Python | CPython 3.14 (`uv`) | PyPy 3.11 | CPython 3.13 | tests + lint + type checks on primary lane |
| Rust | stable | nightly (optional) | n/a | `fmt --check`, `clippy -D warnings`, `test` |
| Go | latest supported | prior minor | n/a | `go test ./...`, `go vet ./...` |
| Zig | pinned stable | preview | n/a | `zig test` |
| Mojo | pinned version | n/a | Python/Rust parity lane | parity + integration checks |

## Conversion Decision Matrix

| Situation | Action |
|---|---|
| SLOs meet target + good velocity | Keep stack |
| Hot-path performance issue | Refactor/optimize in place |
| Repeated SLO misses after optimization | Convert critical module |
| Ecosystem/library blockers | Convert to stack with required library support |

## Required Pre-Conversion Checklist

1. Baseline performance and reliability metrics.
2. API/behavior parity tests.
3. Phased cutover plan with rollback.
4. Governance and `CLAUDE.md` updates.

## Frontmatter and Backmatter

1. Frontmatter required in governance/spec docs: `title`, `date`, `status`, `owner`, `tags`.
2. Backmatter required: decisions, validation commands, residual risks, next review date.

## CLAUDE File Normalization

1. Canonical file is `CLAUDE.md`.
2. Merge typo files like `calude.md` into canonical `CLAUDE.md`.
3. If `CLAUDE.md` grows beyond ~20k tokens, split details into `docs/docsets/claude/` and keep canonical file as index.
