# thegent dotfiles

Portable, idempotent dotfiles manager for macOS, Linux, and WSL. Managed by [thegent](https://github.com/KooshaPari/thegent).

## Quick Start (new machine)

```bash
# Clone thegent to ~/.thegent
git clone git@github.com:KooshaPari/thegent.git ~/.thegent

# Run setup (installs deps, symlinks configs)
~/.thegent/dotfiles/setup.sh

# Restart shell
exec $SHELL
```

## What gets installed

| Config | Source | Destination |
|--------|--------|-------------|
| zsh config | `shell/.zshrc` | `~/.zshrc` |
| bash config | `shell/.bashrc` | `~/.bashrc` |
| shell aliases | `shell/aliases.sh` | `~/.aliases.sh` |
| git config | `git/.gitconfig` | `~/.gitconfig` |
| global gitignore | `git/.gitignore_global` | `~/.gitignore_global` |
| Claude instructions | `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` |
| Agent contract | `claude/AGENTS.md` | `~/.claude/AGENTS.md` |
| mise tool versions | `dev/.mise.toml` | `~/.config/mise/config.toml` |
| Global Taskfile | `dev/Taskfile.global.yml` | `~/Taskfile.yml` |
| VS Code settings | `editors/vscode/settings.json` | `~/Library/Application Support/Code/User/settings.json` |
| Cursor settings | `editors/cursor/settings.json` | `~/Library/Application Support/Cursor/User/settings.json` |

## Tools installed

Via Homebrew (macOS):

- **mise** — tool version manager (replaces nvm/rbenv/pyenv/asdf)
- **starship** — fast cross-shell prompt
- **ripgrep**, **fd**, **bat**, **eza**, **delta** — modern CLI replacements
- **fzf**, **zoxide** — fuzzy finder and smart cd
- **gh** — GitHub CLI
- **process-compose** — multi-process orchestrator
- **gitleaks** — secret scanning
- **orbstack** — fast Docker/container runtime for macOS
- **cursor** — AI-first code editor

Via mise (all platforms):

- **node 22** (LTS Active)
- **go latest**
- **rust latest**
- **bun latest**
- **python 3.12**

## Options

```
Usage: setup.sh [--dry-run] [--no-tools] [--profile <name>]

Options:
  --dry-run     Print what would be done without making changes
  --no-tools    Skip tool installation (Homebrew bundle + mise)
  --profile     Use a named profile (minimal, work-macos, home-linux, wsl)
```

## Customization

Add machine-local overrides to these files (never overwritten by setup):

- `~/.zshrc.local` — local zsh customizations
- `~/.bashrc.local` — local bash customizations
- `~/.gitconfig.local` — local git identity (`user.name`, `user.email`)

Example `~/.gitconfig.local`:

```ini
[user]
  name = Your Name
  email = you@example.com
```

## Directory structure

```
dotfiles/
  setup.sh                    # Main entrypoint
  README.md                   # This file
  macos/
    Brewfile                  # Homebrew packages
    defaults.sh               # macOS system defaults
  shell/
    .zshrc                    # zsh configuration
    .bashrc                   # bash configuration
    aliases.sh                # shared aliases
  git/
    .gitconfig                # global git config template
    .gitignore_global         # global gitignore
  claude/
    CLAUDE.md                 # Claude Code global instructions
    AGENTS.md                 # AI agent contract
  dev/
    .mise.toml                # tool version pinning
    Taskfile.global.yml       # global task runner tasks
  editors/
    vscode/
      settings.json           # VS Code settings
      keybindings.json        # VS Code keybindings
    cursor/
      settings.json           # Cursor AI editor settings
```

## Updating

```bash
# Pull latest configs and re-apply
task dotfiles:sync

# Or manually:
git -C ~/.thegent pull --rebase origin main
~/.thegent/dotfiles/setup.sh
```

## Adding a new machine

1. Generate SSH key: `ssh-keygen -t ed25519 -C "machine-name"`
2. Add to GitHub: `cat ~/.ssh/id_ed25519.pub` → GitHub Settings → SSH keys
3. Clone and run: `git clone git@github.com:KooshaPari/thegent.git ~/.thegent && ~/.thegent/dotfiles/setup.sh`
4. Set git identity: `git config --global user.name "Name" && git config --global user.email "email"`
5. Authenticate gh CLI: `gh auth login`
