# thegent Dotfiles

Central dotfiles manager for development environment across macOS, Linux, and WSL.

This directory consolidates shell configurations, git settings, editor configs, and development tool settings that previously were scattered across the filesystem.

## Structure

```
dotfiles/
├── shell/               # Shell configurations (zsh, bash)
├── git/                 # Git configuration
├── editors/             # Editor configs (editorconfig, etc.)
├── tools/               # Quality gates and linter configs
│   ├── pre-commit-config.yaml   # Pre-commit hooks
│   ├── shellcheckrc             # ShellCheck linter config
│   ├── vale.ini                 # Vale prose linter config
│   ├── jscpd.json               # Code duplication detector
│   └── importlinter             # Python import linter
├── claude/              # Claude development environment
│   ├── AGENTS.md        # Global agent contract & delegation policy
│   └── settings.json    # Claude IDE settings
├── INSTALL.sh           # Installation script
└── README.md            # This file
```

## Quick Install

On a new system:

```bash
cd thegent
./dotfiles/INSTALL.sh
```

This will symlink all configs to your home directory and copy Claude settings.

## What Gets Installed

### Shell (shell/)
- **`.zshrc`** - Primary zsh configuration with plugins, completions, and aliases
- **`.bashrc`** - Fallback bash configuration

### Git (git/)
- **`.gitconfig`** - Git user config, merge tool, credential helpers, LFS setup

### Editors (editors/)
- **`.editorconfig`** - Universal editor settings (indent, line endings, whitespace)

### Tools (tools/)
- **`.shellcheckrc`** - ShellCheck style and ignore rules
- **`.vale.ini`** - Vale prose linter styles and vocabularies
- **`.pre-commit-config.yaml`** - Pre-commit hooks for git operations
- **`.jscpd.json`** - Code duplication detection threshold
- **`.importlinter`** - Python import architecture enforcement

### Claude (claude/)
- **`AGENTS.md`** - Global AI agent contract and delegation policies (shared across projects)
- **`settings.json`** - Claude IDE preferences and model settings (sensitive - mode 600)

## Installation Details

### Symlinked Configs
Most configs are symlinked (except Claude settings) so they stay in sync with this repository:

```bash
ln -sf /path/to/dotfiles/shell/zshrc ~/.zshrc
```

This means updates to dotfiles automatically propagate to your environment.

### Copied Configs
Claude settings are **copied** (not symlinked) because they contain sensitive data:

```bash
cp /path/to/dotfiles/claude/settings.json ~/.claude/settings.json
chmod 600 ~/.claude/settings.json
```

After updating Claude settings locally, merge changes back into `dotfiles/claude/settings.json` manually.

## Usage After Install

### Reload Shell After Installation
```bash
exec $SHELL
```

### Install Pre-commit Hooks in a Project
```bash
cd your-project
pre-commit install
```

This hooks the pre-commit config into `.git/hooks/`.

### Verify Git Configuration
```bash
git config --list | grep user
# user.name = Claude Code
# user.email = claude@anthropic.com
```

## Maintenance

### Adding New Dotfiles
1. Place the config file in the appropriate subdirectory (shell/, git/, tools/, etc.)
2. Update INSTALL.sh to symlink or copy it
3. Update this README with the new structure
4. Commit and push

### Updating Configs Locally
- **Symlinked files** (shell, git, tools): Edit in the dotfiles directory, then commit
- **Copied files** (Claude settings): Edit `~/.claude/settings.json`, then manually merge back into `dotfiles/claude/settings.json`

### Backups
Before running INSTALL.sh, your existing dotfiles are not deleted. The symlinks will replace them, but you can restore the originals from `~/.local/backups/` if needed.

## Cross-Platform Support

These dotfiles are tested on:
- macOS (homebrew)
- Linux (various distros)
- WSL (Windows Subsystem for Linux)

## Governance & Reuse

This repository is part of the Phenotype organization. Dotfiles can be reused across:
- Multiple workstations
- CI/CD environments (via `./dotfiles/INSTALL.sh`)
- Docker containers (mount or copy `dotfiles/`)
- Fresh system setups

See `~/CodeProjects/Phenotype/CLAUDE.md` for org-wide governance policies.

## Related Documentation

- **thegent README**: `/thegent/README.md` - Agent orchestration framework
- **Project CLAUDE.md**: `/CLAUDE.md` - Project-specific instructions
- **Global CLAUDE.md**: `~/.claude/CLAUDE.md` (linked from dotfiles/claude/)
- **Agent Contract**: `dotfiles/claude/AGENTS.md` - Global agent delegation policy
