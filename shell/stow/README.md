# `shell/stow/` — GNU Stow bundle for user-level zsh scripts

This directory is a [GNU Stow](https://www.gnu.org/software/stow/) package that
links 6 user-level zsh scripts into the home directory. The install is driven
by `dotfiles/INSTALL.sh` which calls `stow --restow` against this directory.

## What's in the bundle

| File                              | LoC  | Installed at (when stow'd to `$HOME`) | Purpose                                                              |
| --------------------------------- | ---- | ------------------------------------- | -------------------------------------------------------------------- |
| `zsh-worktree-governance.zsh`     | 140  | `~/.zsh-worktree-governance.zsh`      | Repo worktree governance (main-line policy, airlock auto-register)    |
| `zsh-fork-guardian.zsh`           | 528  | `~/.zsh-fork-guardian.zsh`            | Fork-bomb detection + tiered response (T1–T5)                        |
| `zsh-protected-processes.zsh`     | 174  | `~/.zsh-protected-processes.zsh`      | Protected-process governance (never-kill list, ancestry walk)         |
| `zsh-safeguards.zsh`              | 520  | `~/.zsh-safeguards.zsh`               | Shell safeguards (ulimits, ls wrapper, gh governance, fork guard)    |
| `phenoforge-org-secrets.zsh`      |   7  | `~/.phenoforge-org-secrets.zsh`       | Org-level API keys (OPENROUTER, WORKOS) — ⚠ see Security below        |
| `phenoforge-refresh-zsh-cache.zsh`|  14  | `~/bin/phenoforge-refresh-zsh-cache.zsh` | Refresh zsh startup caches (zoxide/fzf/mcfly → compile)            |
| **Total**                         |1383  |                                       |                                                                      |

> **Note on naming.** Canonical names use hyphens (GNU Stow convention).
> The user's live scripts in `$HOME` use underscores (`.zsh_*.zsh`); stow
> converts underscores → hyphens at install time. Sourcing in `.zshrc`
> should reference the hyphenated names.

## Usage

### Install (thegent-style)

`dotfiles/INSTALL.sh` does this automatically when `stow` is on PATH:

```bash
cd "$REPO/shell/stow" && stow --target="$HOME" --restow .
```

### Install (manual)

```bash
# from repo root
cd shell/stow
stow --target="$HOME" --restow .

# verify symlinks
ls -la ~/.zsh-worktree-governance.zsh \
       ~/.zsh-fork-guardian.zsh \
       ~/.zsh-protected-processes.zsh \
       ~/.zsh-safeguards.zsh \
       ~/.phenoforge-org-secrets.zsh \
       ~/bin/phenoforge-refresh-zsh-cache.zsh
```

### Revert (uninstall the bundle)

```bash
cd shell/stow
stow --target="$HOME" --delete .
```

This removes the symlinks Stow created (it does **not** delete the files in
`shell/stow/`, only the links in `$HOME`).

### Add a new script

1. Drop the file in `shell/stow/` with a hyphenated name.
2. Re-run `stow --restow .` (or re-run `INSTALL.sh`).
3. Source the new file from your `.zshrc` (Stow only creates symlinks; it does
   not edit `.zshrc`).

## Reconciliation history

- **2026-07-17** — Initial bundle. Six scripts copied byte-identical from user
  home directory into this stow package. See
  `shell/README.md` for the per-file reconciliation of the duplicates that
  previously lived at `shell/.zsh_worktree_governance.zsh` and
  `shell/.zsh_safeguards.zsh`. See
  `../../.recovery-actions-2026-07-17.ndjson` for the audit trail.

## Security

`phenoforge-org-secrets.zsh` contains live credentials:

- `OPENROUTER_API_KEY` (sk-or-v1-...)
- `WORKOS_API_KEY` (sk_test_...)
- `WORKOS_CLIENT_ID` (client_01...)
- `AUTHKIT_DOMAIN` (URL)

These are bundled **byte-identical** per the task's hard rule (no edits during
copy). Before the bundle is shipped to a non-private fork, either:

1. Strip secrets from `phenoforge-org-secrets.zsh` and replace with a template
   (`<YOUR_OPENROUTER_KEY>`), **OR**
2. Move this file out of `stow/` and source it from a private, gitignored
   path, **OR**
3. Ensure the target repo is private and these keys are scoped to a safe
   environment.

## Files in this bundle were copied from

| Bundle file                           | Source                                              |
| ------------------------------------- | --------------------------------------------------- |
| `zsh-worktree-governance.zsh`         | `~/.zsh_worktree_governance.zsh`                    |
| `zsh-fork-guardian.zsh`               | `~/.zsh_fork_guardian.zsh`                          |
| `zsh-protected-processes.zsh`         | `~/.zsh_protected_processes.zsh`                    |
| `zsh-safeguards.zsh`                  | `~/.zsh_safeguards.zsh`                             |
| `phenoforge-org-secrets.zsh`          | `~/.config/phenotype/org-secrets.zsh`               |
| `phenoforge-refresh-zsh-cache.zsh`    | `~/bin/refresh_zsh_cache.zsh`                       |

All copies are byte-identical (verified via `diff -q` + `shasum -a 256`).
