# GitHub Namespace Guard (`KooshaPari/*`)

## Goal
Block creation of PRs/issues outside `KooshaPari/*` and provide a retroactive audit for existing out-of-namespace lanes.

## Prevent New Violations
Use wrapper instead of direct `gh` for create flows:

```bash
scripts/policy/gh_namespace_guard.sh pr create ...
scripts/policy/gh_namespace_guard.sh issue create ...
```

Behavior:
- Allows create only when target repo owner is `KooshaPari` (configurable).
- If blocked, exits `42` and prints a rerun command under `KooshaPari/<repo>`.

Config:
- `GH_NAMESPACE_ALLOWED_OWNER` (default `KooshaPari`)
- `GH_NAMESPACE_GUARD_REDIRECT=1` to auto-rewrite target owner and continue.

Shell convenience:

```bash
alias ghc="$(pwd)/scripts/policy/gh_namespace_guard.sh"
# then use:
ghc pr create ...
ghc issue create ...
```

## Retroactive Audit
Find open PRs/issues authored by selected logins that are outside `KooshaPari/*`:

```bash
scripts/policy/gh_namespace_retro_audit.py --authors KooshaPari,Dmouse92 --allowed-owner KooshaPari --limit 200
```

Exit codes:
- `0`: clean
- `1`: findings present
- `2`: configuration/auth problem

## Recommended Rollout
1. Add `alias ghc=.../gh_namespace_guard.sh` to your shell profile.
2. Use `ghc` for all `pr create` and `issue create` commands.
3. Run retro audit weekly and close/recreate findings under `KooshaPari/*`.
