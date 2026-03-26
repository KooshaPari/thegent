# Polyrepo dependency graph — methodology

**Task:** Produce a **machine-assisted** map of “who depends on whom” for reuse planning (task 21 in the productization wave).

## Goals

- Find **`phenotype-*`** and shared-kit references across repos.
- Detect **duplicate clusters** (same capability in two packages).
- Inform **migration order** (leaves first, then consumers).

## Recommended commands (run from `Phenotype/repos` or per repo)

### 1. Git URL / path dependencies

```bash
rg -l "phenotype-" --glob "go.mod" --glob "package.json" --glob "Cargo.toml" --glob "pyproject.toml"
```

### 2. Import path / package name

```bash
rg "github\\.com/.*/phenotype-|@phenotype/|phenotype_" --glob "*.{go,ts,tsx,py,rs,toml}"
```

### 3. Output

- Store results in **CSV** or **Markdown table**: `consumer_repo`, `dependency`, `manifest path`.
- Optional: Graphviz `dot` from CSV for visualization.

## Cadence

- **Quarterly** full refresh; **on-demand** after each major extraction.
- Link the generated artifact from `docs/reference/PHENOTYPE_ECOSYSTEM_ARCHITECTURE_INDEX.md` when published.

## Automation (future)

- CI job: `rg`-based diff on PR to flag new undeclared dependencies.
- Not a substitute for language-specific `go mod graph` / `cargo tree` inside each repo.
