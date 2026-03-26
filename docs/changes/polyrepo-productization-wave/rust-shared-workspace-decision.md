# Decision record: canonical Rust shared workspace (`phenotype-infrakit` vs `phenotype-shared`)

**Status:** `DECISION_PENDING`  
**Task:** Item 5 — lock **one** canonical home for shared Rust crates.

## Options

| Option | Pros | Cons |
|--------|------|------|
| **A — `phenotype-infrakit` only** | Single name for infra/event/cache crates | Rename/migrate consumers from `phenotype-shared` |
| **B — `phenotype-shared` only** | Broad name | Overlaps with non-Rust “shared” concepts |
| **C — new workspace root** e.g. `libs/rust/phenotype-crates/` | Clean tree | New path + mass import updates |

## Required inputs

- `rg` / `cargo tree` inventory of **git** and **path** deps pointing at each.
- List of **published** crates.io names (if any).

## Exit criteria

- ADR filed under `docs/governance/adrs/`.
- Consumers updated in **one** forward migration (no long dual-home period).

---

**Action:** Owner runs methodology in `polyrepo-dependency-graph-methodology.md`, then resolves **A/B/C** with semver plan.
