# Implementation Strategy

## Approach

1. Treat this pass as a repo-forest classification and verification loop.
2. Separate real branch work from generated scaffolding and pointer metadata.
3. Validate the branches that already contain substantive code changes.
4. Record the remaining ambiguous repos in the session worklog instead of forcing a guess.

## Decisions made

- `AgilePlus` keeps the manual `Clone` implementation on `AppState` and removes unnecessary `Clone` derives from adapters that do not need them.
- `phenotype-design` now resolves its VitePress theme through the shared `phenodocs` theme entrypoint and uses a local package rename that matches the branch intent.
- `phenotype-config` is deferred as a scaffolding/classification problem, not a validation failure.

## Remaining follow-up

- Classify `phenotype-config` staged command scaffolding against the intended command contract.
- Decide whether `phenodocs` temp deletions are cleanup or restore candidates.
- Decide whether `trash-cli` and `thegent` have any actual code changes remaining after pointer/worktree noise is separated.

