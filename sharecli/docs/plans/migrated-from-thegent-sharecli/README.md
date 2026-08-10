# Migrated from `thegent-sharecli` (archived 2026-08-08)

This directory preserves project-specific content that lived only in the
archived `thegent-sharecli` repository. The canonical versions of these
documents live in `/docs/plans/` and document the general methodology.

## Provenance

| File | Source blob SHA | Source HEAD | Source path |
|---|---|---|---|
| `AGILEPLUS_SPEC-thegent-sharecli.md` | `98a3d1819042` | `2e1d734067c5` | `thegent-sharecli/docs/plans/AGILEPLUS_SPEC.md` |
| `KILO_GASTOWN_SPEC-thegent-sharecli.md` | `6c4c61bed4f5` | `2e1d734067c5` | `thegent-sharecli/docs/plans/KILO_GASTOWN_SPEC.md` |
| `../.agileplus/migrated-from-thegent-sharecli/worklog.md` | `da86d7966986` | `2e1d734067c5` | `thegent-sharecli/.agileplus/worklog.md` |

## Timeline

- **2026-04-02**: Initial commits in `thegent-sharecli` documenting how
  the rig applied the canonical AgilePlus + Kilo/Gastown methodologies.
- **2026-07-22**: `thegent-sharecli` archived with tag "DEPRECATED duplicate
  of sharecli — absorb into thegent when runtime stabilizes".
- **2026-08-08**: cherry-picked `2e1d734` (coordination_contract.py) into
  `thegent/sharecli/`. Project-specific methodology docs migrated here.

## Why these files were NOT replaced with canonical versions

The thegent repo's `docs/plans/AGILEPLUS_SPEC.md` and
`docs/plans/KILO_GASTOWN_SPEC.md` are general methodology specs. The
thegent-sharecli versions captured *project-specific bindings*: which
roles the thegent-sharecli rig used, which files were mapped to which
gates, etc. They are not interchangeable with the canonical docs.

## Recoverability

If these files are ever needed in their original context, the full git
history of `thegent-sharecli` is preserved in the bundle:

```
/tmp/gh-backup-2026-07-28-thegent-sharecli.bundle
```

This bundle contains every commit, blob, and tag from the
thegent-sharecli repository up to its archival on 2026-08-08.
To restore the entire repo from this bundle:

```bash
git clone /tmp/gh-backup-2026-07-28-thegent-sharecli.bundle thegent-sharecli-restored
cd thegent-sharecli-restored
git checkout main
```

## Cherry-pick record

The unpushed commit `2e1d734` from thegent-sharecli was cherry-picked
into the absorb branch:

```
$ git cherry-pick sharecli-src/main
[absorb/thegent-sharecli-final <new-commit>] test: add coordination lock queue contract runner
```

Followed by this commit to migrate the project-specific methodology docs.
