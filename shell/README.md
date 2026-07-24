# `shell/` — thegent shell configurations

This directory contains the thegent's shell configuration files, bundled into
three logical groups:

## Layout

```
shell/
├── zshrc                                   # Main .zshrc (sourced via dotfiles/INSTALL.sh)
├── bashrc                                  # Main .bashrc
├── .zsh_slim.zsh                           # thegent's own minimal zsh helpers
├── .zsh_advanced.zsh                       # thegent's own advanced zsh features
├── .zsh_bundle.zsh                         # thegent's own bundle loader
├── .zsh_instant_prompt.zsh                 # thegent's own instant-prompt
├── .zsh_optimization.zsh                   # thegent's own optimization
├── .zshenv                                 # thegent .zshenv
├── .zshrc                                  # thegent .zshrc (legacy alias for zshrc)
├── .zsh_worktree_governance.zsh            # legacy (RECONCILED — see stow/)
├── .zsh_safeguards.zsh                     # legacy (RECONCILED — see stow/)
├── install-zsh-plugin.sh                   # plugin-mode installer
├── envrc.home.template                     # direnv template
├── thegent.zshrc.agent                     # agent-mode snippet
├── thegent.profile.ps1                     # PowerShell profile
├── zshrc.local.template                    # per-user zshrc additions
├── starship/                               # starship prompt preset
├── zsh-thegent-integration/                # zsh plugin for thegent (thegent.plugin.zsh)
└── stow/                                   # ★ NEW: GNU stow bundle for user-level scripts
    ├── README.md
    ├── zsh-worktree-governance.zsh         # canonical (was ~/.zsh_worktree_governance.zsh)
    ├── zsh-fork-guardian.zsh               # canonical (was ~/.zsh_fork_guardian.zsh)
    ├── zsh-protected-processes.zsh         # canonical (was ~/.zsh_protected_processes.zsh)
    ├── zsh-safeguards.zsh                  # canonical (was ~/.zsh_safeguards.zsh)
    ├── phenoforge-org-secrets.zsh          # canonical (was ~/.config/phenotype/org-secrets.zsh) ⚠ contains API keys
    └── phenoforge-refresh-zsh-cache.zsh    # canonical (was ~/bin/refresh_zsh_cache.zsh)
```

## Install flow

The install is driven by `dotfiles/INSTALL.sh`, which:

1. Symlinks `shell/zshrc` → `~/.zshrc`, `shell/bashrc` → `~/.bashrc`
2. Symlinks git config, editorconfig, shellcheckrc, etc.
3. Copies Claude configs into `~/.claude/`
4. **NEW:** Runs `stow --restow` against `shell/stow/` (only if `stow` is on PATH).

## Reconciliation note (2026-07-17)

Two files in this directory were duplicates of newer user-level scripts:

| Repo file                                  | User's home canonical       | Decision                  |
| ------------------------------------------ | --------------------------- | ------------------------- |
| `shell/.zsh_worktree_governance.zsh`       | `~/.zsh_worktree_governance.zsh` (Jul 16) | Bundle is canonical; legacy file superseded |
| `shell/.zsh_safeguards.zsh`                | `~/.zsh_safeguards.zsh` (Jun 15)          | Bundle is canonical; legacy file superseded |

Both legacy files in this directory are **left in place** (not deleted) per the
conservative-only-on-deletion policy. See
`.recovery-actions-2026-07-17.ndjson` for the per-action audit trail.

## Security note

`stow/phenoforge-org-secrets.zsh` contains live API keys (OPENROUTER, WORKOS
test). Before merging any PR that includes this file, **verify the target repo
is private and the keys are scoped appropriately** for a bundled dotfile.
