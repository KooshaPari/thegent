# Architecture boundary & schema gates — per-repo spec (items 6–8)

**Status:** Specification for rolling adoption (not yet wired in every repo).

## Item 6 — Architecture boundary tests (top repos)

**Intent:** Fail CI when **domain** imports **infrastructure** or **adapters** incorrectly (hexagonal rule).

**Patterns:**

- **Python:** `import-linter` / `tach` boundaries.
- **TypeScript:** `eslint-plugin-boundaries` or `dependency-cruiser`.
- **Go:** `depguard` in `golangci-lint`.
- **Rust:** `cargo-modules` or custom `#[path]` checks (project-specific).

**Rollout:** Add to **thegent**, **heliosApp**, **AgilePlus**, **agentapi-plusplus**, **heliosCLI** first (adjust list per active velocity).

## Item 7 — Schema compatibility

**Intent:** OpenAPI / Protobuf / JSON Schema **diff** or breaking-change detection on PR.

**Patterns:** `buf breaking`, `openapi-diff`, Spectral with breaking rules.

## Item 8 — Changelog / version gate

**Intent:** PR touching `src/` or public API **must** bump `CHANGELOG.md` + semver file when release-worthy.

**Patterns:** `changie`, `semantic-release`, or custom script in `Taskfile`.

---

**Note:** Until GitHub Actions billing is healthy, run these **locally** or in pre-commit.
