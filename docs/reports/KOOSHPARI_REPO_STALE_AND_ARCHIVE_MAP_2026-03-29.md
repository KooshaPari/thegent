# KooshaPari GitHub: staleness and archival map (2026-03-29)

Source export: `docs/reports/data/KOOSHPARI_GITHUB_REPOS_2026-03-29.tsv`  
Derived buckets: `docs/reports/data/KOOSHPARI_REPOS_STALE_BUCKETS.tsv`

## Summary counts (non-archived repos only)

| Bucket | Meaning | Count |
|--------|---------|------:|
| `active_90d` | Pushed within ~90 days of export | 179 |
| `stale_90d_1y` | Between ~90 days and 1 year | 33 |
| `stale_1y_2y` | Between 1 and 2 years | 7 |
| `stale_over_2y` | Older than ~2 years | 2 |

**GitHub-archived** repos in export: **28** (listed under `archived_github` in the buckets TSV).

## Candidates for triage (no automatic archival)

### Stale over 2 years (2)

- `odin-restaurant` (2024-01-09)
- `Project-Spyn` (2023-11-28)

### Stale 1y–2y (7)

- `340-p2`, `340P1`, `delete-o-matic-for-linkedin`, `Byteport-TestZip`, `odin-dash`, `ssToCal-front`, `canvasApp`

### Stale 90d–1y (33) — themes

- Course / homework: `CSE445-A4`, `330p5`, `472-P2-Flame-War`, `P2`, `340-*`
- Agslag / NetWeave generations: `agslag*`, `NetWeave`, `netweave-final*`, `Frostify`, `hoohacks`
- Infra experiments: `localbase*`, `KDesktopVirt`, `KVirtualStage`, `kmobile`, `KodeVibe`
- **Legacy SDK name:** `pheno-sdk` (last push 2025-10-15 on GitHub; remote tree empty — **`phenoSDK` is canonical**)

**Recommendation:** For each `stale_*` repo, choose one: **archive on GitHub**, **delete** (if duplicate), or **revive** with an AgilePlus feature.

## Already archived on GitHub (28)

Includes superseded work: `agentapi`, `CLIProxyAPI`, `zen`, `heliosHarness`, `TripleM`, `localbase3`, many `odin-*` tutorials. See full list in `KOOSHPARI_REPOS_STALE_BUCKETS.tsv`.

## Decision log (execution)

- **Coldest 9 repos (seed):** `docs/reports/data/KOOSHPARI_STALE_TRIAGE_DECISIONS_2026-03-29.tsv`
- **Full stale set (42 rows: 33 + 7 + 2):** `docs/reports/data/KOOSHPARI_STALE_TRIAGE_FULL_2026-03-29.tsv`

## Regenerate data

```bash
gh repo list KooshaPari --limit 1000 --json name,isArchived,pushedAt,isPrivate \
  | jaq -r 'sort_by(.pushedAt) | reverse | .[] | "\(.pushedAt)\t\(.name)\tarchived=\(.isArchived)\tprivate=\(.isPrivate)"' \
  > docs/reports/data/KOOSHPARI_GITHUB_REPOS_YYYY-MM-DD.tsv
```

Re-run the bucket script from `docs/reports/PORTFOLIO_AUDIT_2026-03-29.md` companion logic (Python one-liner in history) or check in `scripts/reports/` when stabilized.
